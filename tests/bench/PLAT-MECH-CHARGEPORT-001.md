# Bench test PLAT-MECH-CHARGEPORT-001 — charge port holds in the printed left leg

Requirement: [PLAT-MECH-CHARGEPORT-001](../../requirements/platform.md#plat-mech-chargeport-001). The model part (geometry
asserts) is checked by `tests/test_mechanical.py`; this sheet is the print part. Manual test, run at bring-up step **4**
([bring-up.md](bring-up.md)); add a line to *Results* every time it is run.

## Equipment
- The printed left leg (bottom half) and its lid.
- The micro-USB breakout J1, wires soldered.
- A micro-USB cable.

## Setup
1. Slide the breakout into its frame on the outer side wall, solder side to the wall, receptacle towards the heel,
   until its back edge rests against the lid position and the two front tabs hold it.
2. Screw the lid on.

## Steps
1. From behind, plug the cable into the receptacle through the lid notch, then pull it out. Do it 10 times.
2. Open the lid and look at the breakout.

## Pass criteria
- The plug goes in and out 10 times without forcing.
- The breakout has not moved (still against the lid edge and the front tabs, nothing bent or cracked).

## Results
| Date | Commit / build | Plug cycles | Breakout in place | Pass | By | Notes |
|---|---|---|---|---|---|---|
