#!/usr/bin/env bash
# Rebuild the 4-column variant from tars4.scad: STLs, two Ender 3 plates (3MF) and renders.
# usage: tools/build4.sh [stl|3mf|renders|all|cr10|cr10stl|tests]   (default: all = Ender 3 halves; cr10 = one-piece
# parts, one plate; tests = trial prints). STL exports run in parallel and the script fails when OpenSCAD prints a
# WARNING or an ERROR (model checks such as "WARNING: connector ..." included).
set -euo pipefail
cd "$(dirname "$0")/.."
WHAT=${1:-all}
TMP=$(mktemp -d)
ROOT=$PWD
command -v cygpath >/dev/null && TMP=$(cygpath -m "$TMP") && ROOT=$(cygpath -m "$PWD")   # Windows OpenSCAD cannot read Git Bash /c/... paths
trap 'rm -rf "$TMP"' EXIT
CR10_PARTS="col0 col1 col2 col3 lid_leg lid_leg_sd lid_mid lid_mid_left"
TEST_PARTS="tube_test3"
PARTS="col0_bottom col0_top col1_bottom col1_top col2_bottom col2_top col3_bottom col3_top lid_leg_bottom lid_leg_sd_bottom lid_leg_top lid_mid_bottom lid_mid_top lid_mid_left_bottom lid_mid_left_top splint inserts inserts_speaker collar"

# export_stl <file prefix> <parts...>: print_<part> -> mechanical/stl/tars4_<prefix><part>.stl, in parallel; fails on WARNING / ERROR
export_stl() {
    local pre=$1; shift
    printf '%s\n' "$@" | xargs -P "$(nproc)" -I{} sh -c \
        'rm -f "mechanical/stl/tars4_'"$pre"'{}.stl"; openscad -D "part=\"print_{}\"" -o "mechanical/stl/tars4_'"$pre"'{}.stl" mechanical/scad/tars4.scad > "'"$TMP"'/'"$pre"'{}.log" 2>&1; echo "== mechanical/stl/tars4_'"$pre"'{}.stl"'
    local bad=0
    for p in "$@"; do
        if grep -E "WARNING|ERROR" "$TMP/$pre$p.log" | sed "s|^|   tars4_$pre$p: |" | grep .; then bad=1; fi
        [ -s "mechanical/stl/tars4_$pre$p.stl" ] || { echo "   tars4_$pre$p: no STL written"; bad=1; }
    done
    return $bad
}

build_stl() {
    export_stl "" $PARTS
}

build_3mf() {
    # Ender 3, Orca bed 220 x 220: every part is printed in halves (longest 182 mm), 3 plates, ~20 mm margins.
    # PLATE_DIR=dir writes the raw plates there instead of the repo root (make check: fit test without touching them)
    local D=${PLATE_DIR:-mechanical/3mf}
    mkdir -p "$D"
    P="python3 -I tools/stl2_3mf.py --long-x"
    echo "== tars4_plate1_columns.3mf"
    $P "$D/tars4_plate1_columns.3mf" 220 220 \
        mid_left_top=mechanical/stl/tars4_col1_top.stl mid_right_top=mechanical/stl/tars4_col2_top.stl \
        leg_left_top=mechanical/stl/tars4_col0_top.stl+leg_right_top=mechanical/stl/tars4_col3_top.stl \
        mid_left_bottom=mechanical/stl/tars4_col1_bottom.stl+mid_right_bottom=mechanical/stl/tars4_col2_bottom.stl
    echo "== tars4_plate2_legs.3mf"
    $P "$D/tars4_plate2_legs.3mf" 220 220 \
        leg_left_bottom=mechanical/stl/tars4_col0_bottom.stl leg_right_bottom=mechanical/stl/tars4_col3_bottom.stl \
        lid_leg_left_bottom=mechanical/stl/tars4_lid_leg_sd_bottom.stl lid_leg_right_bottom=mechanical/stl/tars4_lid_leg_bottom.stl \
        lid_leg_left_top=mechanical/stl/tars4_lid_leg_top.stl+lid_leg_right_top=mechanical/stl/tars4_lid_leg_top.stl \
        tube_collars=mechanical/stl/tars4_collar.stl
    echo "== tars4_plate3_lids.3mf"
    $P "$D/tars4_plate3_lids.3mf" 220 220 \
        lid_mid_left_top=mechanical/stl/tars4_lid_mid_left_top.stl lid_mid_right_top=mechanical/stl/tars4_lid_mid_top.stl \
        lid_mid_left_bottom=mechanical/stl/tars4_lid_mid_left_bottom.stl lid_mid_right_bottom=mechanical/stl/tars4_lid_mid_bottom.stl \
        splints=mechanical/stl/tars4_splint.stl
    echo "   black plugs: mechanical/stl/tars4_inserts.stl (left middle) + mechanical/stl/tars4_inserts_speaker.stl (right middle, grille), black filament"
}

build_renders() {
    echo "== renders"
    openscad -o renders/tars4_three_quarter.png --imgsize=900,1300 --camera=-160,-260,290,57,14,114 --viewall --colorscheme=Tomorrow mechanical/scad/tars4.scad 2>/dev/null
    openscad -D 'part="col1"' -o "$TMP/col1.stl" mechanical/scad/tars4.scad 2>/dev/null
    openscad -D 'part="lid_mid"' -o "$TMP/lid.stl" mechanical/scad/tars4.scad 2>/dev/null
    # 4 columns swung around the top pivot (two-legged walk), clean render from meshes
    for p in col0 col1 col2 col3 lid_leg lid_mid inserts inserts_speaker; do openscad -D "part=\"$p\"" -o "$TMP/$p.stl" mechanical/scad/tars4.scad 2>/dev/null; done
    # motion sensor: right middle column with its hole + the sensor's dome (pose renders with -D pir=true)
    openscad -D pir=true -D 'part="col2"' -o "$TMP/col2_pir.stl" mechanical/scad/tars4.scad 2>/dev/null
    openscad -D pir=true -D 'part="pir_dummy"' -o "$TMP/pir_dummy.stl" mechanical/scad/tars4.scad 2>/dev/null
    cat > "$TMP/pose.scad" <<EOF
D = 31; gap = 0.8; H = 8 * D; col_w = D - 3 * gap / 4; wall = 1.6;   // must match tars4.scad
pir = true;                                                            // motion sensor fitted
pz = H - wall - 14 / 2 - 1;                                            // top pivot
angles = [14, -6, 5, -12];
grey = [[0.55, 0.55, 0.53], [0.78, 0.78, 0.76], [0.78, 0.78, 0.76], [0.55, 0.55, 0.53]];
for (i = [0:3]) translate([i * (col_w + gap), 0, 0])
    translate([0, D / 2, pz]) rotate([angles[i], 0, 0]) translate([0, -D / 2, -pz]) {
        color(grey[i]) import(i == 2 && pir ? "$TMP/col2_pir.stl" : str("$TMP/col", i, ".stl"));
        if (i == 2 && pir) color([0.96, 0.96, 0.93]) import("$TMP/pir_dummy.stl");
        color([0.45, 0.45, 0.43]) import(i == 1 || i == 2 ? "$TMP/lid_mid.stl" : "$TMP/lid_leg.stl");
        if (i == 1 || i == 2) {
            color([0.05, 0.05, 0.06]) import(i == 2 ? "$TMP/inserts_speaker.stl" : "$TMP/inserts.stl");
            // speaker behind the grille (right middle column)
            if (i == 2) color([0.25, 0.25, 0.27]) translate([col_w / 2 - 11, 3, 30]) cube([22, 10, 39]);
            color([0.03, 0.04, 0.06]) translate([col_w / 2 - 13, wall + 0.1, (0.761 + 0.877) / 2 * H - 13]) cube([26, 1, 26]);
        }
        if (i < 3) color([0.8, 0.65, 0.3]) translate([col_w - 1, D / 2, pz]) rotate([0, 90, 0]) cylinder(d = 8, h = gap + 2, \$fn = 32);
    }
EOF
    openscad -o renders/tars4_pose_three_quarter.png --imgsize=1200,1500 --camera=-200,-300,300,62,15,115 --viewall --colorscheme=Tomorrow "$TMP/pose.scad" 2>/dev/null
    # same pose, camera turned 90 deg to the right around TARS (front right, same height and distance): the two right
    # columns in front, with the motion sensor at the top of the right middle column
    openscad -D pir=true -o renders/tars4_pose_right.png --imgsize=1200,1500 --camera=377,-247,300,62,15,115 --viewall --colorscheme=Tomorrow "$TMP/pose.scad" 2>/dev/null
    # same pose from the front right: the speaker grille in the right middle column's lower panel
    openscad -o renders/tars4_sound_three_quarter.png --imgsize=1200,1500 --camera=170,-430,170,62,15,105 --viewall --colorscheme=Tomorrow "$TMP/pose.scad" 2>/dev/null
    # lying face down, lids off, parts shown: three-quarter and straight from the back (pivots at the top, batteries at the bottom)
    openscad -D 'part="open"' -o renders/tars4_open_3q.png --imgsize=1600,1200 --camera=62,-124,15,50,0,210,520 --colorscheme=Tomorrow mechanical/scad/tars4.scad 2>/dev/null
    openscad -D 'part="open"' -o renders/tars4_open_back.png --imgsize=900,1500 --camera=62,-124,15,0,0,180,760 --colorscheme=Tomorrow mechanical/scad/tars4.scad 2>/dev/null
    # motion sensor at the top of the right middle column: straight front view (shows its offset from the column axis), and inside (lid off)
    printf 'include <%s/mechanical/scad/tars4.scad>\nintersection() { union() { color([0.82, 0.82, 0.82]) column(2); color("black") inserts(false); dummies(2); } translate([-1, -1, 125]) cube([40, 40, 130]); }\n' "$ROOT" > "$TMP/pir.scad"
    openscad -D pir=true -D 'part="none"' -o renders/tars4_pir_front.png --imgsize=800,1100 --camera=15.2,0,205,90,0,0,170 --projection=o --colorscheme=Tomorrow "$TMP/pir.scad" 2>/dev/null
    openscad -D pir=true -D 'part="none"' -o renders/tars4_pir_inside.png --imgsize=800,1100 --camera=15,15,190,55,0,205,250 --colorscheme=Tomorrow "$TMP/pir.scad" 2>/dev/null
    # each leg seen from the back, lid off, connector boxes (orange) named; close-ups: left leg cut just above the parked
    # power block connectors (two rows: X12 / X13 at the back, X10 / X14 in front), right leg DS3231 / BME280 area
    for i in 0 3; do
        printf 'include <%s/mechanical/scad/tars4.scad>\ncolor([0.6, 0.6, 0.6]) column(%s); dummies(%s); conn_dummies(%s);\nfor (c = CONN) if (c[0] == %s) color("black") translate([c[4][0] - 0.6, c[4][1] + 0.05, (c[3][2] + c[4][2]) / 2 - 1.5]) rotate([90, 0, 180]) linear_extrude(0.2) text(c[1], size = 3, font = "Liberation Sans:style=Bold");\n' "$ROOT" $i $i $i $i > "$TMP/leg$i.scad"
    done
    openscad -D 'part="none"' -o renders/tars4_leg_left.png --imgsize=700,1700 --camera=15,15,124,80,0,195,640 --colorscheme=Tomorrow "$TMP/leg0.scad" 2>/dev/null
    openscad -D 'part="none"' -o renders/tars4_leg_left_xh.png --imgsize=1400,1400 --camera=15,15,152,75,0,200,110 --colorscheme=Tomorrow "$TMP/leg0.scad" 2>/dev/null
    openscad -D 'part="none"' -o renders/tars4_leg_right.png --imgsize=700,1700 --camera=15,15,124,80,0,165,640 --colorscheme=Tomorrow "$TMP/leg3.scad" 2>/dev/null
    openscad -D 'part="none"' -o renders/tars4_leg_right_sensors.png --imgsize=1400,1400 --camera=15,15,165,62,0,160,200 --colorscheme=Tomorrow "$TMP/leg3.scad" 2>/dev/null
    printf 'include <%s/mechanical/scad/tars4.scad>\nzc = park_z0 + xh_inline[1] + 2.6;\nintersection() { union() { color([0.6, 0.6, 0.6]) column(0); dummies(0); conn_dummies(0); } translate([-5, -5, 95]) cube([45, 45, zc - 95]); }\nfor (c = CONN) if (c[0] == 0 && c[4][2] > 140 && c[3][2] < 170) color("black") translate([(c[3][0] + c[4][0]) / 2, (c[3][1] + c[4][1]) / 2, c[4][2] + 0.05]) rotate([0, 0, 180]) linear_extrude(0.2) text(c[1], size = 2.6, halign = "center", valign = "center", font = "Liberation Sans:style=Bold");\n' "$ROOT" > "$TMP/cut0.scad"
    openscad -D 'part="none"' -o renders/tars4_leg_left_power.png --imgsize=1400,1400 --camera=15,15,150,35,0,180,120 --colorscheme=Tomorrow "$TMP/cut0.scad" 2>/dev/null
    # left leg cut through its middle (seen from the right, lid off): microSD reader, then buck-boost + charger above it
    printf 'include <%s/mechanical/scad/tars4.scad>\nintersection() { union() { color([0.6, 0.6, 0.6]) column(0); dummies(0); } translate([-5, -5, 100]) cube([col_w / 2 + 5, 45, 50]); }\n' "$ROOT" > "$TMP/sd.scad"
    openscad -D 'part="none"' -o renders/tars4_sd_reader.png --imgsize=900,900 --camera=12,15,118,60,0,120,75 --colorscheme=Tomorrow "$TMP/sd.scad" 2>/dev/null
    openscad -D 'part="none"' -o renders/tars4_buck_sd.png --imgsize=900,900 --camera=12,15,128,55,0,120,95 --colorscheme=Tomorrow "$TMP/sd.scad" 2>/dev/null
    # heel of the left leg (charge port + switch): from behind with the lid on, then lid off seen from the back right,
    # cut under the bottom shelf
    printf 'include <%s/mechanical/scad/tars4.scad>\nintersection() { union() { color([0.6, 0.6, 0.6]) column(0); color([0.45, 0.45, 0.45]) lid(false, true); } translate([-5, -5, -1]) cube([45, 45, 27]); }\n' "$ROOT" > "$TMP/heel.scad"
    printf 'include <%s/mechanical/scad/tars4.scad>\nintersection() { union() { color([0.6, 0.6, 0.6]) column(0); dummies(0); } translate([-5, -5, -1]) cube([45, 45, shelf_z - shelf_t - 0.5]); }\n' "$ROOT" > "$TMP/heel_open.scad"
    openscad -D 'part="none"' -o renders/tars4_heel_back.png --imgsize=1200,900 --camera=-35,85,30,10,26,9 --colorscheme=Tomorrow "$TMP/heel.scad" 2>/dev/null
    openscad -D 'part="none"' -o renders/tars4_heel_open.png --imgsize=1200,1000 --camera=45,85,45,8,18,7 --colorscheme=Tomorrow "$TMP/heel_open.scad" 2>/dev/null
    # inside of a middle column, lid removed
    echo "color([0.78,0.78,0.76]) import(\"$TMP/col1.stl\");" > "$TMP/inside.scad"
    openscad -o renders/tars4_mid_column_inside.png --imgsize=800,1400 --camera=14,200,114,14,14,114 --viewall --colorscheme=Tomorrow "$TMP/inside.scad" 2>/dev/null
}

build_cr10() {
    # CR-10 (300 x 300): columns and lids in one piece, everything on one plate
    export_stl cr10_ $CR10_PARTS
    echo "== tars4_cr10_plate.3mf"
    python3 -I tools/stl2_3mf.py mechanical/3mf/tars4_cr10_plate.3mf 300 300 \
        leg_left=mechanical/stl/tars4_cr10_col0.stl mid_left=mechanical/stl/tars4_cr10_col1.stl mid_right=mechanical/stl/tars4_cr10_col2.stl leg_right=mechanical/stl/tars4_cr10_col3.stl \
        lid_leg_left=mechanical/stl/tars4_cr10_lid_leg_sd.stl lid_mid_left=mechanical/stl/tars4_cr10_lid_mid_left.stl \
        lid_mid_right=mechanical/stl/tars4_cr10_lid_mid.stl lid_leg_right=mechanical/stl/tars4_cr10_lid_leg.stl
    echo "   saved Orca layout: mechanical/3mf/tars4_cr10.3mf (scripts/orca_check.py creates it once, then only refreshes its meshes)"
    echo "   + mechanical/stl/tars4_inserts.stl (x2, black), mechanical/stl/tars4_collar.stl"
}

case $WHAT in
    stl) build_stl ;;
    3mf) build_3mf ;;
    renders) build_renders ;;
    all) build_stl; build_3mf; build_renders ;;
    cr10) build_cr10 ;;
    cr10stl) export_stl cr10_ $CR10_PARTS ;;
    tests) export_stl "" $TEST_PARTS ;;
    *) echo "usage: $0 [stl|3mf|renders|all|cr10|cr10stl|tests]"; exit 1 ;;
esac
