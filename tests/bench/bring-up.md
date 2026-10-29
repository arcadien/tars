# Bring-up (when the parts arrive)

The order matters: nothing goes on the 3V3 before step 3.6. A line ending in → links the bench test sheet that holds the procedure, the pass criteria and the results; the other lines are checks with no requirement behind them.
What is left to buy: [shopping_list.md](../../hardware/shopping_list.md). Open questions and measurements: [open_questions.md](../../open_questions.md).

**1. Measure and update the `MEASURE` values in `mechanical/scad/tars4.scad`** (then `tools/build4.sh stl`,
`python3 -I tools/update_orca_project.py mechanical/3mf/tars4.3mf`)
- [x] LOLIN S3 Mini: 25.4 × 34.5 × 1.0, notch 2 × 7, BOOT sticks out 1.3 on the right (window through the wall,
      `d1_boot_window`). All measurements of 2026-10-27: `hardware/measurements.md`.
- [x] 1.3" CS screen: 27.35 × 42.12 × 3.3, glass 7.2 / 5 from the short edges (`active_dz` −1.1, assuming the active
      area centred in the glass: check lit with a test pattern; print the screen test piece first, see above).
- [x] TPS63020 module: 26.7 × 17.7 × 1.6, slot cut into the walls (`bk_clr` 0.4); wire only the inner pad of each corner
      pair. - [ ] `bk_h` (inductor height).
- [ ] microSD reader: `sd`, `sd_sock`, `sd_sock_dx`, `sd_sock_over`, `sd_card_out`, `sd_lip`; the card clicks in
      through the lid slot.
- [x] Stripboard 1.61 thick (`hub_b[2]` 1.6); cut P1 / P2 to 24 × 32.
- [x] TP4056 board lying flat: 28.7 as bought → **desolder its micro-USB and file off the two panel-break nubs** →
      26.3 × 17.15 × 0.9, on 0.5 ledges (end pads centred 1.43 from the edge), no side grooves. Cells 65 × 18.3 (fit).
      - [ ] contact plates, switch body.
- [x] Micro-USB breakout 14.3 × 16 × 1.5, plug overmold 7.9 × 5.5 (fits). - [ ] USB-C plug
      overmold ≤ 11.5 wide (S3 floor opening); speaker 39 × 22 × 10 and MAX98357A sizes.
- [x] Power-path perfboard 1.5 thick (26.6 × 20, 10 × 8 holes); D1 lying 5.2 (`pp_parts` 6).
- [ ] Every board soldered on the wall side (ADXL345, MAX98357A, micro-USB, spare): solder tails ≤ 1 mm (`pcb_gap` 1.2).
- [x] Screens' backs: parts 3 high from 8.7 below the pad row, clear of the right-angle header + housings (dry fit,
      6.9 from the PCB back); C7 8 × 11.5.
- [x] Connectors: female header 8.4, male spacer 2.4, screen header row 1.4, ZS-042 header depth ~4, XH (male 8,
      female 7, mated 9.7). - [ ] Dupont housing
      (`dp_t`, `dp_on`, `dp_inline`), XH pairs (`xh_inline`); screen header row → `scr_hdr_dz`,
      ZS-042 header depth → `rtc_hdr_y`. The model must echo no connector WARNING afterwards.
- [x] Polyfuses XF160 15 × 16 × 2.5: too wide for the top shelf → standing on the inner front wall in front of each cell.
- [x] BME280 12 × 15.6 × 2.6, sensor centred. - [ ] no regulator (3.3 V straight to the sensor), no LED.
- [x] Pivot bores: tube 7.93; `tube_test3` (teardrop bores, the round ones sagged ~0.3): G7.95 scrapes, **G8.00 holds**
  with no play, **R8.05 turns** with micro play, wider bores get looser → teardrop pivots 8.00 / 8.05
  (PLAT-MECH-PIVOT-001). A bore that binds: sand or ream with an 8 mm drill.
- [x] AM312: `pir_test` printed, cap glued from the inside, Ø11.5 hole (dome flush). - [ ] measure `pir_pcb_dn`.

**2. Check on the bench, before wiring** (multimeter)
- [ ] Screen BLK ↔ VCC resistance (power off): note any pull-up. BLK current with the screen on (a few mA expected:
      then no Q2 / Q3).
- [ ] MAX98357A breakout: SD pull-up value (Adafruit: 1 M to VIN). With a 100 k pull-up, R18 → **2.2 k**; if SD is
      tied to VIN, cut the trace.
- [ ] D1 (1N5822) reverse leakage at 4.2 V, at 35 °C (hot room; D1 only blocks on battery, the charger is off then and does not heat the leg): > 50 µA → R1 4.7 k or a lower-leakage Schottky.
- [ ] AM312 output high level at 3.3 V > 2.5 V; DW01: does it switch on by itself when the cells are first connected?
- [ ] TP4056 R_PROG 2.4 k → [PLAT-POWER-CHARGE-002](PLAT-POWER-CHARGE-002.md)
- [ ] TPS63020 output and idle current → [PLAT-POWER-REG-001](PLAT-POWER-REG-001.md)
- [ ] Slide switch current rating (≥ 1 A).
- [ ] ZS-042: CR2032 charging resistor removed.
- [ ] Battery-fed LEDs removed → [PLAT-POWER-SLEEP-001](PLAT-POWER-SLEEP-001.md), [TECH-POWER-SLEEP-001](TECH-POWER-SLEEP-001.md)
- [ ] Cells matched → [TECH-POWER-CELL-002](TECH-POWER-CELL-002.md)

**3. Bring-up, one element at a time** (multimeter at each step; a bench supply at 3.7 V / 300 mA stands in for the
cells until step 3.5; nothing goes on the 3V3 before step 3.6 is green)

*3.1 TP4056 module alone*
- [ ] USB in (its own micro-USB), nothing on B+/B−: LED behaviour, VUSB = 4.75–5.25 V at the IN pads.
- [ ] Bench supply on B+/B− (3.7 V): supply current with USB out < 10 µA for the TP4056 alone (the whole block adds D1's leakage, up to tens of µA: note it); protection → [TECH-POWER-PROTECT-001](TECH-POWER-PROTECT-001.md)
- [ ] Charge current, end of charge, chip temperature → [PLAT-POWER-CHARGE-002](PLAT-POWER-CHARGE-002.md), [TECH-POWER-CHARGE-001](TECH-POWER-CHARGE-001.md)
- [ ] D3 and C9 on the IN pads, **D3 band (cathode) and C9 + on IN+**: VUSB unchanged, no heating, IN+ ↔ IN− not shorted; hot-plug peak → [TECH-POWER-HOTPLUG-001](TECH-POWER-HOTPLUG-001.md)

*3.2 Power path (Q1, D1, R1) + SW1, VSYS loaded with 33 Ω (~110 mA)*
- [ ] Power-path drops → [PERF-POWER-PATH-001](PERF-POWER-PATH-001.md); USB out: VUSB < 0.5 V within ~1 s.
- [ ] Switch off → [FUNC-POWER-SWITCH-001](FUNC-POWER-SWITCH-001.md). SW1 on with 1 A load (3.9 Ω 5 W): Q1 and SW1 barely warm.

*3.3 Dividers on the power-path board*
- [ ] VBAT/2 = B+ / 2 ± 2 % with the switch on **and** off, and with the charger plugged in (10 MΩ multimeter loads the 500 k
      node by ~5 %: compare with GPIO1 later).
- [ ] USB_DET ≈ 3.0 V with USB in (never > 3.3 V), < 0.2 V with USB out.

*3.4 Polyfuses, cells, star ground*
- [ ] Polyfuses → [PLAT-POWER-FUSE-001](PLAT-POWER-FUSE-001.md)
- [ ] Cells in: the load does not draw from the cells on the supply, plug / unplug under load → [FUNC-POWER-PATH-001](FUNC-POWER-PATH-001.md), [FUNC-POWER-PATH-002](FUNC-POWER-PATH-002.md)
- [ ] B− / OUT− / TPS GND / amp GND all < 0.1 Ω to the star point.

*3.5 TPS63020 module, nothing on its output*
- [ ] Static regulation → [PERF-POWER-REG-001](PERF-POWER-REG-001.md)

*3.6 3V3 distribution: P1 with C2 / C3, C1 at the S3's 3V pin, P2*
- [ ] Before connecting the TPS: 3V3 ↔ GND on P1 > 1 kΩ, C1 / C12 polarity, strip cuts checked.
- [ ] TPS connected: 3.3 V at P1 and at the S3's 3V pin.

*3.7 S3 Mini alone on the 3V3*
- [ ] Boots from the TPS (no USB-C): idle current on VSYS.
- [ ] VBAT/2 read by GPIO1 = multimeter value ± 3 % (ADC calibration); USB_DET on GPIO21 follows the charger.
- [ ] S3's USB-C in a PC that is **off**, on battery: current from the cells into its VBUS ≈ 0; with the PC on,
      flashing works with SW1 on or off; second 3V3 source → [TECH-POWER-REG-002](TECH-POWER-REG-002.md)

*3.8 Peripherals, one at a time, measuring the 3V3 current added by each*
- [ ] Screen 1, then screen 2 (backlight off at boot unless BLK has a pull-up; PWM dimming works); total BLK current at
      GPIO7 < 10 mA (else Q2 / Q3).
- [ ] MAX98357A: off at boot and with GPIO4 low (SD < 0.1 V), VIN = VSYS, C7 + to VIN; Wi-Fi + loud sound → [PERF-POWER-REG-002](PERF-POWER-REG-002.md)
- [ ] INMP441: I2S1 data present. DS3231: 0x68 through both tubes, CR2032 not charged. ADXL345: 0x53, INT1 toggles.
- [ ] microSD: CMD / D0–D3 read 10 kΩ to SD_3V3, init at 10 MHz 1-bit, 3V3 dip at insertion < 0.1 V; GPIO36 high →
      SD_3V3 < 0.1 V; sleep current with and without the card.
- [ ] BME280: 0x76 (or 0x77) next to 0x53 / 0x57 (DS3231 EEPROM) / 0x68; pull-up total ≥ 1.1 k; temperature vs a reference thermometer cold
      and after 10 min running → offset.
- [ ] AM312 + R17: ~15 µA idle; GPIO3 ≈ 0 V idle, ≈ 3.3 V on motion, held ~2 s; no false trigger during Wi-Fi bursts and
      backlight PWM (else 1 nF on GPIO3); a hand waved in front wakes the S3 from deep sleep.

*3.9 Whole robot*
- [ ] Deep-sleep current from the cells (target above; LEDs removed, DS3231 32 kHz off, pins held); wake by USB_DET,
      ADXL INT1, PIR and the S3 timer.
- [ ] Charge from the heel, switch on / off, time, wall temperature, supply voltage → [FUNC-POWER-CHARGE-001](FUNC-POWER-CHARGE-001.md), [FUNC-POWER-SWITCH-002](FUNC-POWER-SWITCH-002.md), [PERF-POWER-CHARGE-001](PERF-POWER-CHARGE-001.md), [PERF-POWER-THERMAL-001](PERF-POWER-THERMAL-001.md), [PERF-POWER-MAINS-001](PERF-POWER-MAINS-001.md); TP4056, Q1, D1, TPS63020 finger-warm at most.
- [ ] Note every measured value here (it feeds the `MEASURE` values and the firmware thresholds).

**4. Print** (`mechanical/3mf/tars4.3mf`, or the CR-10 plate)
- [ ] bed levelling (`part="print_test_level"`) and screen fit (`part="print_test_screen"`), exported by hand from the scad if needed, then the plates; PETG collars, black PLA plugs.
- [ ] Check the lid slot / microSD, the TPS63020 and P1 / P2 grooves on the printed parts before gluing the splints.
- [ ] Charge port in the left leg, first pivot joint → [PLAT-MECH-CHARGEPORT-001](PLAT-MECH-CHARGEPORT-001.md), [PLAT-MECH-PIVOT-001](PLAT-MECH-PIVOT-001.md)

**5. Firmware**
- [ ] GPIO map from the README *Signals* table and the carrier plan (`renders/tars4_board_s3.svg`); SPI 26.7 MHz first (scope SCK at screen 2 if possible), then 40 MHz;
      backlight PWM ~20 kHz; `RST = -1`; I2S0 amp, I2S1 microphone; SDMMC 1-bit 10 MHz; I2C 100 kHz.
- [ ] Charger detect: USB_DET high = on mains (no cut-off, charging icon); charge done ≈ B+ relaxing to ~4.15 V with
      USB_DET still high.
- [ ] Battery: cut-off 3.3 V on B+ (ignore below 2.5 V), "empty" flag in RTC memory; BL_EN, AMP_SD and I2S0 off until
      B+ is validated; Wi-Fi TX power limited if needed.
- [ ] Deep sleep / wake-up as in *Deep sleep and wake-up*.
- [ ] **Irony cue**: in the film it is a white dot that appears *inside* the screen → drawn on the right screen, no LED.
