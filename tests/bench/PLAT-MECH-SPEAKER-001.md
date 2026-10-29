# Bench test PLAT-MECH-SPEAKER-001 — speaker fitted under the splint, no rattle

Requirement: [PLAT-MECH-SPEAKER-001](../../requirements/platform.md#plat-mech-speaker-001). The model part (geometry
asserts, no WARNING) is checked by `tests/test_mechanical.py`; this sheet is the print part. Manual test, run at
bring-up step **4** ([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The printed right middle column (bottom half) with its splint glued, and its lid.
- The speaker (4 Ω, 25.3 × 13.8 × 7.2), its wires soldered; glue as planned for it.

## Setup
1. Fit the speaker just under the splint, face against the lower black panel (the lower nub notched), and glue it.
2. Let the glue cure, then screw the lid on.

## Steps
1. Hold the column and shake it firmly by hand in every direction for 10 s.
2. Tap the column walls next to the speaker.
3. Play a sound through it (once the amplifier is wired: [FUNC-AUDIO-SPEAK-001](../../requirements/functional.md#func-audio-speak-001)).

## Pass criteria
- Steps 1–2: no rattle, the speaker does not move.
- Step 3: no buzz from the speaker against the column at full volume.

## Results
| Date | Commit / build | Shaken | Tapped | Sound | Pass | By | Notes |
|---|---|---|---|---|---|---|---|
