#!/usr/bin/env bash
# TARS validation harness: rebuild the generated files whose sources changed and fail on any problem.
# usage: scripts/check.sh [stl] [erc] [renders] [docs] [overhang] [orca]   (no argument: the first four; overhang and
#        orca only when asked, e.g. `make check-orca`: overhangs and the Orca projects are checked by hand in Orca)
#   stl       every printable part to STL (Ender 3 halves, CR-10 one-piece parts, trial prints) + the raw 3MF plates
#             (written to build/plates, the repo's tars4_plate*.3mf are left alone); fails on any OpenSCAD WARNING /
#             ERROR (connector clashes, fit checks, ...) or a raw layout off its 220 x 220 bed
#   overhang  scripts/overhang.py (uv, trimesh): faces > 50 deg from vertical over 2 cm2, unless a narrow bridge or
#             listed in scripts/overhang_allow.json with the reason it prints without support
#   orca      scripts/orca_check.py: refreshes the meshes of the saved Orca projects (tars4.3mf on the Ender 3,
#             tars4_cr10.3mf on the CR-10, layout kept) and slices every plate with the OrcaSlicer CLI: a part that
#             grew off its plate or into a neighbour fails
#   erc       KiCad ERC through kicad-cli (no GUI): errors fail, warnings are listed
#   renders   standard PNG views (tools/build4.sh renders); each PNG must be rewritten by this run and not blank
#   docs      board drawings (boards.py, with its own net checks), wiring SVG, harness guide + PDF (no blank page)
# Incremental: a stage runs only when its input files changed since its last pass (sha256 of their contents in
# build/check/<stage>.sum, written after the stage passes). FORCE=1 runs everything. Geometry changes (tars4.scad)
# trigger stl → renders → docs (wire lengths); a wire colour change only docs; the schematic only erc.
# Logs go to build/check/<stage>.log. ORCA=/path/to/OrcaSlicer.AppImage and KICAD=/path/to/kicad.AppImage override
# the tool lookup.
set -uo pipefail
cd "$(dirname "$0")/.."
LOG=build/check
mkdir -p "$LOG"
STAGES=${*:-stl erc renders docs}
KICAD=${KICAD:-$(ls ~/bin/kicad-*.AppImage 2>/dev/null | sort | tail -1)}
LIBS=~/.local/share/OpenSCAD/libraries
ORCA_PRESETS=~/.config/OrcaSlicer/user/default
FAILED=()
T0=$(date +%s)

# input files of each stage (what makes its result change)
inputs() {
    case $1 in
        stl) echo mechanical/scad/tars4.scad tools/build4.sh tools/stl2_3mf.py $LIBS/*.scad ;;
        overhang) echo mechanical/stl/tars4_*.stl scripts/overhang.py scripts/overhang_allow.json ;;
        orca) echo mechanical/stl/tars4_*.stl mechanical/3mf/tars4.3mf mechanical/3mf/tars4_cr10.3mf scripts/orca_check.py scripts/orca_profile.py \
                   tools/update_orca_project.py tools/stl2_3mf.py "$ORCA_PRESETS"/machine/*.json "$ORCA_PRESETS"/process/*.json ;;
        erc) echo hardware/kicad/*.kicad_sch hardware/kicad/*.kicad_sym hardware/kicad/*.kicad_pro hardware/kicad/sym-lib-table ;;
        renders) echo mechanical/scad/tars4.scad tools/build4.sh $LIBS/*.scad scripts/check_renders.py ;;
        docs) echo mechanical/scad/tars4.scad tools/boards.py tools/harness.py tools/html2pdf.py tools/wiring_svg.js hardware/tars4_wiring.html ;;
    esac
}

digest() { # sha256 of the stage's inputs (names + contents); missing files count as changed
    local f
    for f in $(inputs "$1"); do
        if [ -f "$f" ]; then sha256sum "$f"; else echo "missing $f"; fi
    done | sha256sum | cut -d' ' -f1
}

stage_stl() {
    tools/build4.sh stl && tools/build4.sh cr10stl && tools/build4.sh tests || return 1
    # raw Ender 3 plates go to build/plates: checked for fit, the repo copies are only rewritten on request
    PLATE_DIR=build/plates tools/build4.sh 3mf | tee "$LOG/3mf.out"
    ! grep -q "WARNING" "$LOG/3mf.out"
}

stage_overhang() {
    uv run -q scripts/overhang.py mechanical/stl/tars4_*.stl
}

stage_orca() {
    python3 -I scripts/orca_check.py
}

stage_erc() {
    [ -n "$KICAD" ] || { echo "KiCad AppImage not found in ~/bin (set KICAD=...)"; return 1; }
    "$KICAD" kicad-cli sch erc --severity-all --format json -o "$LOG/erc.json" hardware/kicad/tars4.kicad_sch || return 1
    python3 -I - "$LOG/erc.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
v = [x for s in d["sheets"] for x in s["violations"]]
for x in v:
    print(f"ERC {x['severity']}: {x['description']} ({', '.join(i['description'] for i in x.get('items', []))})")
err = sum(x["severity"] == "error" for x in v)
print(f"erc: {err} error(s), {len(v) - err} warning(s)")
sys.exit(1 if err else 0)
EOF
}

stage_renders() {
    local since bad=0
    since=$(date +%s)
    tools/build4.sh renders || bad=1
    grep -o 'renders/[a-z0-9_]*\.png' tools/build4.sh | sort -u | xargs uv run -q scripts/check_renders.py --since "$since" || bad=1
    return $bad
}

stage_docs() {
    local since bad=0
    since=$(date +%s)
    python3 -I tools/boards.py || bad=1
    node tools/wiring_svg.js || bad=1
    python3 -I tools/harness.py || bad=1
    for f in renders/tars4_board_*.svg renders/tars4_wiring.svg hardware/tars4_harness.html hardware/tars4_harness.pdf; do
        if [ ! -s "$f" ] || [ "$(stat -c %Y "$f")" -lt "$since" ]; then echo "RENDER $f: missing or not rewritten"; bad=1; fi
    done
    # harness PDF: no blank page (ghostscript ink coverage, every page must carry some ink)
    if [ -s hardware/tars4_harness.pdf ]; then
        gs -q -o - -sDEVICE=inkcov hardware/tars4_harness.pdf | awk '{ n++; if ($1 + $2 + $3 + $4 < 0.0005) { print "RENDER hardware/tars4_harness.pdf: page " n " is blank"; b = 1 } }
            END { print "harness pdf: " n " pages"; exit b }' || bad=1
    fi
    return $bad
}

for s in $STAGES; do
    if ! declare -F "stage_$s" >/dev/null; then echo "unknown stage: $s"; exit 2; fi
    printf '== %-9s ' "$s"
    sum=$(digest "$s")
    if [ -z "${FORCE:-}" ] && [ "$(cat "$LOG/$s.sum" 2>/dev/null)" = "$sum" ]; then
        echo "unchanged, skipped"
        continue
    fi
    t=$(date +%s)
    rm -f "$LOG/$s.sum"
    if "stage_$s" > "$LOG/$s.log" 2>&1; then
        digest "$s" > "$LOG/$s.sum"   # after the run: a stage may rewrite its own inputs (orca refreshes the 3MF meshes)
        echo "ok ($(( $(date +%s) - t )) s)"
    else
        echo "FAILED ($(( $(date +%s) - t )) s), $LOG/$s.log:"
        grep -E "WARNING|ERROR|OVERHANG|ORCA|RENDER|ERC |FAIL|Error|error" "$LOG/$s.log" | grep -v "^ERC warning" | head -20 | sed 's/^/   /'
        FAILED+=("$s")
    fi
done

echo "== $(( $(date +%s) - T0 )) s"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "check FAILED: ${FAILED[*]}"
    exit 1
fi
echo "check passed: $STAGES"
