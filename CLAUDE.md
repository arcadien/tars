# CLAUDE.md

TARS robot, `tars4` variant. `README.md` is the project documentation; `mechanical/scad/tars4.scad` is the model.

## Repository
- Layout: `mechanical/` (scad, stl, 3mf), `hardware/` (kicad, schematic / wiring / harness pages, power budget,
  measurements, shopping list), `software/`, `requirements/` (RBD), `renders/`, `tools/`, `scripts/`,
  `open_questions.md`. `CONTRIBUTING.md` is the manual workflow (no network, no assistant): keep it in step with the tools.
- `make check` (incremental, also the pre-commit hook) must pass; commit the files it rewrites. STLs are re-exported
  byte-different even when the geometry is unchanged.
- Commit prefixes (RBD pre-push hook): req, test, feat, tech, perf, ui, conf, arch, plan, chore, fix, docs, style,
  refactor; `feat(ID):`-style ones need a validated requirement. Granular commits, push after each.
- Branch `bench-tests`: bench firmware for the D1 mini and the S3 Mini, not merged.
- Requirements: draft a whole domain for review; keep a requirement `draft` while a bench measurement is pending;
  a PLAT requirement is validated only after its FUNC / TECH parent.

## Language
- Requirements (`requirements/*.md`) and all documentation are written in **English**: README, markdown notes,
  generated guides and diagrams, code comments, commit messages.
- Conversation with me stays in French.
- In requirements, every reference to another requirement or document is a markdown link, as in `derives_from:`:
  `[TECH-POWER-CHARGE-001](technical.md#tech-power-charge-001)`, `[power_budget.md](../hardware/power_budget.md)`. Headings stay plain.

## Hardware Conventions

### Electronics & Hardware Docs
- Power wires go in pairs: red / black for battery and 5V (B+/B−, VBAT, VSYS, VUSB), white / blue for regulated or stepped voltages (3V3, buck/boost outputs). Blue is for power only, never a signal. Do not use yellow for 3V3.
- Every wiring diagram must label each wire end as solder, Dupont or JST-XH, and give the wire length. Write guides so a beginner knows the first step.
- The TP4056 module's own micro-USB is desoldered: charging goes through the micro-USB breakout J1 in the left foot, wired to its IN pads. Resistors go on the board or harness side, not at the LEDs, unless I say otherwise.
- Parts budget is spent: solutions use parts already in stock (`hardware/shopping_list.md`, *already in stock*).
- Renders must include connector detail on every leg and in open/exploded views.
- Check that the PDF/HTML output has no blank pages and that diagrams are readable at print size.
- Strip EXIF/GPS from every image: `python3 ~/.claude/skills/hardware-change/scripts/strip_exif.py <paths>`.

### Colour code (README, *Colour code*)
The harness follows the pair rule since 2026-10-27 (sources: `tools/boards.py` wire lists, `tools/harness.py` EXTRA).
26 AWG power: red / black pairs for the battery / 5 V rails, white 3V3 / blue logic GND (TPS63020 → P1 → S3), grey speaker.
Power rails sharing the red / black pair carry one coloured heat-shrink band at both ends, on the + wire and on its GND
(the `rings` field holds the colour name): none = B+ / B− of the cells, white = OUT+ / OUT− of the TP4056, yellow =
VPATH, orange = VSYS (star, TPS63020 input, amp pair), purple = VUSB. A new rail on red / black gets its own band colour.
30 AWG signals, by role; 1 / 2 / 3 black heat-shrink rings tell the buses apart (none = SPI/local, 1 = I2S/PIR, 2 = I2C, 3 = microSD):

| Colour | Role |
|---|---|
| white | 3V3 |
| blue | GND (pair of the white 3V3) |
| yellow | clocks (SCK, BCLK, SCL, SD_CLK) |
| green | data (MOSI, DIN, MIC_SD, SDA, SD_D0) |
| purple | select / frame (CS, LRC, WS, SD_CMD) |
| red | status (DC, INT1, PIR) |
| orange | RST, USB_DET |
| brown | enables / analog (BL_EN, VBAT/2, AMP_SD, SD_EN) |

## Modeling

### OpenSCAD / Printing
- Define all parameters at the top of the file, before any formula that uses them. Expose dimensions as named parameters.
- After editing, render with `openscad -o` and check for errors before saying it's done.
- Don't claim parts fit an Ender 3 (220x220) or CR-10 plate unless you've checked the bounding boxes. Flag any overhang over 45° that a design change introduces.
- Regenerating 3MF files wipes the Orca plate layout, so warn me before doing it. `mechanical/3mf/tars4.3mf` is my Orca project: update it with `tools/update_orca_project.py`.
