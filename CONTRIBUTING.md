# Contributing

How to change TARS by hand, without network access and without an AI assistant. Every step below runs offline once
the tools are installed.

## Tools

| Tool | Used for | Notes |
|---|---|---|
| OpenSCAD 2021.01 (`openscad`) | the model, STL export, renders | GUI for previewing, CLI for the scripts |
| Python 3 | `tools/*.py`, `scripts/*.py` | standard library only, except the two `uv` scripts below |
| `uv` | `scripts/check_renders.py` (Pillow), `scripts/overhang.py` (trimesh) | downloads packages on the first run: run `make check` once **while online** to fill the cache, then work offline with `UV_OFFLINE=1` |
| Node.js (`node`) | `tools/wiring_svg.js` | static SVG of the wiring sketch |
| Firefox + Ghostscript (`gs`) + `pdfunite` | printable wiring guide `hardware/tars4_harness.pdf` | without Firefox the HTML guide is still written, not the PDF |
| KiCad 10 AppImage in `~/bin` | schematic ERC (`make check`) | only needed when `hardware/kicad/` changes; `KICAD=/path/to/kicad.AppImage` overrides |
| OrcaSlicer | slicing `mechanical/3mf/tars4.3mf` | by hand, at the end |

## Mechanical

Everything that gets printed lives in `mechanical/`:

| Path | What | Who writes it |
|---|---|---|
| `mechanical/scad/tars4.scad` | the model: every dimension is a named parameter at the top of the file | **you** |
| `mechanical/scad/column_sections.scad` | helper for the column section drawing | rarely edited |
| `mechanical/stl/` | one STL per part, in print orientation | `tools/build4.sh stl` |
| `mechanical/3mf/tars4.3mf` | **the Orca project** (plates arranged by hand, Ender 3) | Orca, then `tools/update_orca_project.py` |
| `mechanical/3mf/tars4_cr10.3mf` | the CR-10 Orca project (one-piece parts) | Orca, then `tools/update_orca_project.py` |
| `mechanical/3mf/tars4_plate*.3mf` | raw plates, starting point of a new Orca layout | `tools/build4.sh 3mf` |

### 1. Change the model

1. Open `mechanical/scad/tars4.scad` in OpenSCAD. Change values in the parameter block at the top of the file, never
   numbers buried in a module. Values still marked `MEASURE` wait for a measurement (`hardware/measurements.md`).
2. Preview: set `part` (top of the file) to the part you are working on (`"col1"`, `"lid_mid"`, `"open"`…), F5. Set it
   back to its default before committing.
3. Render (F6) the parts you touched: an OpenSCAD `WARNING` (for instance `WARNING: connector …`) is a failed check,
   not a cosmetic message. The scripts below stop on any WARNING.

### 2. Regenerate what depends on it

The shortest path is the incremental check, which redoes only what changed:

```sh
cd ~/git/Tars
UV_OFFLINE=1 make check        # stl → renders → docs (and the ERC if hardware/kicad/ changed)
```

It takes 5–10 min after a model change (STL export ~5 min, renders ~4 min). Logs: `build/check/<stage>.log`. To run
one step by hand instead:

| Command | Writes |
|---|---|
| `tools/build4.sh stl` | `mechanical/stl/tars4_*.stl` (Ender 3 halves) |
| `tools/build4.sh cr10stl` | `mechanical/stl/tars4_cr10_*.stl` (one-piece parts) |
| `tools/build4.sh tests` | trial prints (`pir_test`, `tube_test*`) |
| `openscad -D 'part="print_<part>"' -o <part>.stl mechanical/scad/tars4.scad` | any other part, one-off (e.g. `test_level`, `test_screen`: kept in the model, no longer exported) |
| `tools/build4.sh renders` | `renders/*.png` (README pictures, connector details) |
| `python3 -I tools/column_sections.py` | `renders/tars4_column_sections.svg` |
| `python3 -I tools/tube_section.py` | `renders/tars4_tube_sections.svg` |
| `python3 -I tools/harness.py` | `hardware/tars4_harness.html` + `.pdf` (wire lengths are read from the model) |
| `tools/build4.sh 3mf` | raw plates in `mechanical/3mf/tars4_plate*.3mf` (**not** the Orca projects) |

### 3. Update the Orca projects

The plates in `mechanical/3mf/tars4.3mf` were arranged by hand: **never regenerate that file**, only swap its meshes.

1. Close the project in OrcaSlicer (if it stays open, saving from Orca later puts the old meshes back).
2. `python3 -I tools/update_orca_project.py mechanical/3mf/tars4.3mf` — each object gets the STL of the same name,
   positions, rotations, plates and settings are kept; a copy of the old file goes to `backups/`. Add `--check` to
   only list what would change.
3. Same for the CR-10: `python3 -I tools/update_orca_project.py mechanical/3mf/tars4_cr10.3mf`.
4. Reopen the project in Orca, check the plates (a part that grew may now overlap or leave the bed), slice.

A **new** part has no object in the Orca project yet: import its STL in Orca by hand, place it, save.

### 4. Commit

```sh
git add -A
git commit -m "feat: …"        # the pre-commit hook runs `make check`
```

- The hook refuses the commit if the check fails, or if it rewrote tracked files (STL, renders, guide): `git add`
  them and commit again.
- STL files are re-exported byte-different even when the geometry is the same: committing them is expected.
- Allowed commit prefixes (checked when pushing): `req`, `test`, `feat`, `tech`, `perf`, `ui`, `conf`, `arch`, `plan`,
  `chore`, `fix`, `docs`, `style`, `refactor`; `feat(ID):`-style prefixes need an existing requirement ID in
  `requirements/`.
- Offline, commits stay local: `git push` once the network is back.

### Pitfalls

- OpenSCAD 2021 writes one object per STL; the multi-object 3MF files come from `tools/stl2_3mf.py`.
- Tangent faces (two solids just touching) make non-manifold STLs: overlap them by 0.01 mm.
- Don't print the columns before the tube bore test (`open_questions.md`, T1) has set `tube_od`.
- `make check` never runs the Orca or overhang checks: check overhangs in Orca's preview before printing.
