# TARS4 — shopping list (2026-10-24, translated 2026-10-28)

What is left to buy after the 2026-10-20 order, the review fixes and the "everything demountable" plan.
Links marked **(search)** open a search with the right keywords: pick an offer matching the given criteria. Direct
links were found on 2026-10-21, price and stock not guaranteed.

## 1. Demountable wiring (new)

| Item | Qty | Criteria | Links |
|---|---|---|---|
| Ratchet crimper **SN-28B** + 2.54 Dupont kit | 1 kit | housings 1 to 8 pins (incl. 1 × 3, 1 × 4 and 1 × 6), **~100 female contacts** (~55 used), **male** contacts (≥ 20, also to plug the keying cavities), 3 male housings for the inline pairs (X3, X7, X15) | [Glarks 486 pcs (~19 €)](https://www.amazon.fr/Glarks-connecteur-cliquet-Connecteur-AWG28-18/dp/B07VQ6YNSC) · [JZK (~22 €)](https://www.amazon.fr/JZK-Cliquet-Connecteurs-Assortis-Sertissage/dp/B07PCQ5VMV) · [Taiss 600 pcs (~24 €)](https://www.amazon.fr/Taiss-connecteurs-SN-28B-pression-Connecteur/dp/B0BYMT2BRP) |
| Crimp **JST-XH 2.5** housings, male + female, with their contacts: **2, 3 and 4 pins** (in stock: check both sides of each pair are there) | 2 × 2 p., 1 × 3 p., 2 × 4 p. | X12 and X16 (one per cell, joined on the TP4056 B+ / B− pads); X14 (VBAT/2, USB_DET, SD_EN); X10 (charge port + switch, 4 p.) and X13 (power block outputs). No JST-PH any more: X11 is merged into X10. Crimped with the SN-28B; 30 AWG wires folded back as in the Dupont contacts | in stock |
| **Female 2 × 8** headers, 2.54 pitch, **8.5 mm** high | 2 (lot) | S3 carrier; measure the real height → `s3_sock_h` | [Amazon (search)](https://www.amazon.fr/s?k=barrette+femelle+2x8+2.54) · [AliExpress (search)](https://fr.aliexpress.com/w/wholesale-female-header-2x8-2.54.html) |
| **Single-sided pad perfboard** (one pad per hole, no strips, copper on one side only), 2.54, preferably **FR4 epoxy** (green or pale yellow) rather than FR2 bakelite (brown: pads lift with heat) | 1 (lot) | S3 carrier cut to 25.6 × 34.4 (10 × 13 holes) and power-path board to 26.6 × 20 (10 × 8 holes): plans renders/tars4_board_*.svg | [Amazon (search)](https://www.amazon.fr/s?k=plaque+pastilles+simple+face+2.54+FR4) |
| Insulated **30 AWG** wire-wrap wire (Kynar), small reel | 1 | Q1 / Q5 legs on the power-path board (instead of bare strands), insulated jumpers | [Amazon (search)](https://www.amazon.fr/s?k=fil+wrapping+30+AWG+kynar) |
| Bare tinned copper wire 0.5–0.6 mm | ~0.5 m | GND bus (carrier column E, power-path board row 1); resistor lead offcuts are enough | [Amazon (search)](https://www.amazon.fr/s?k=fil+cuivre+etame+0.6mm) |
| Cyanoacrylate or 5 min epoxy glue | — | female headers glued on the single-sided S3 carrier | probably already in stock |
| Male header 1 × 40 (breakable), straight + **right-angle** | 1 + 1 | X6 (amplifier speaker output); 1 × 8 right-angle headers on the back of both screens (X1, X4); pins for modules shipped without | [Amazon (search)](https://www.amazon.fr/s?k=barrette+male+secable+2.54+droite+coudee) |
| Heat-shrink 1.5 / 2 / 3 mm, **colour assortment** (at least black, white, yellow, orange, purple) | 1 assortment | under the contacts' insulation wings (30 AWG too thin), solder joints, tube exits; black rings of the signal buses (1 / 2 / 3); **coloured bands of the power rails** on red / black, Ø2–3 mm (white OUT+, yellow VPATH, orange VSYS, purple VUSB: ~40 bands of 10 mm) | [Amazon (search)](https://www.amazon.fr/s?k=gaine+thermoretractable+assortiment+1.5mm) |

## 2. Wire

| Item | Qty | Criteria | Links |
|---|---|---|---|
| **30 AWG** silicone wire, **tinned** copper (not CCA), multicolour | ~20.3 m in total (cut lengths from the wiring guide), ≤ 3.6 m per colour | **10-colour kit** (× 7.6 m): **purple** is needed (selects CS / LRC / WS / CMD) and **blue** (GND of screens and sensors); black and grey unused in 30 AWG | [BNTECHGO 10 colours × 25 ft (maker)](https://bntechgo.com/bntechgo-30-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-25-feet-high-temp-200-c-600v-30-awg-silicone-wire-11-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/) · [Amazon (search)](https://www.amazon.fr/s?k=fil+silicone+30+AWG+kit+couleurs+cuivre+etame) |
| 26 AWG silicone wire | ~7.7 m (red 3.3 m, black 2.5 m, blue 0.8 m, white 0.8 m, grey 0.3 m) | already in stock (10-colour kit): **check there are 3.3 m of red and 2.5 m of black** (pair rule: red / black for battery, VUSB, VSYS) | — |

## 3. Parts added by the review

| Item | Qty | Role | Links |
|---|---|---|---|
| **2.4 kΩ** resistor, through-hole 1/4 W or 1/8 W (or SMD 0805 / 1206) | 1 (+ spare) | TP4056 R_PROG (0.5 A charge): original SMD removed, through-hole one lying on the board, legs soldered to its two pads; often already in a 1/4 W resistor assortment (else 2.2 k + 220 Ω in series) | [Amazon (search, 1/4 W assortment)](https://www.amazon.fr/s?k=assortiment+resistances+1%2F4W+1%25) |
| **22 µF 16 V** electrolytic | 1 | C9, TP4056 input: **in stock** (Ø5.15, lying; `charger_h` raised to 6) | — |
| Through-hole 1/4 W resistors: **1 kΩ** ×2, **10 kΩ** ×1, **47 Ω** ×2, **33 Ω** ×1, **100 Ω** ×1, **100 kΩ** ×1; **1 MΩ 1/8 W** ×1 | — | R17, R18; R12 / R19 (split SCK); R20 (MOSI); R21 (AM312 filter); R22 (Q5 gate); R2 (lying under the groove lip; a 1/4 W fits too); not needed if the assortment is already there |
| **AO3401A** P-MOSFET (SOT-23) | 1 more | Q5, cuts the microSD 3V3 in sleep (already ordered for Q1: check one is left) |
| **C12** capacitor: **10 µF 16 V** tantalum (+ at F6) instead of the 47 µF | 1 | AM312 filter on P2: **in stock** (the 47 µF in stock is 12 mm, too tall; the tantalum still cuts the 20 kHz backlight PWM by ~40 dB) | — |
| Small **NPN** (BC547 / BC548 / 2N3904 / 2N2222 / S8050 / S9013) + **1 MΩ** ×2 | 1 + 2 | VSYS sense into GPIO37 (PLAT-POWER-VSENSE-001, draft): **from the drawer, no purchase** | — |

## 4. Capacitors

| Item | Qty | Role | Links |
|---|---|---|---|
| **220 µF SMD 7343** (7.3 × 4.3), tantalum ≥ 6.3 V | 1 | C1, lying under the S3: **in stock** (Panasonic POSCAP 10TPE220ML, 10 V polymer, ESR 25 mΩ) | — |
| **470 µF 10 V** electrolytic, **Ø ≤ 8 × 12** | 1 | C7, amplifier VIN (lying behind the board): **in stock** (Ø8 × 11.5) | — |
| **10 µF** ceramic X5R/X7R ("106") or **16 V tantalum** (+ to 3V3), 2.54 pitch, h ≤ 10 | 4 | C2 on P1, C4 at the microSD reader, C10 and C12 on P2: **16 V tantalums in stock** (6, 2 spare) | — |
| **100 nF** ceramic ("104") through-hole, 2.54 pitch, body ≤ ~4 mm, **no tantalum** for C6 | 5 | C3, C5, C6, C8, C11: **in stock** (small through-hole ceramics) | [Amazon (search)](https://www.amazon.fr/s?k=assortiment+condensateur+ceramique+104) |

## 4 bis. Depending on the measurements

| Item | Qty | For | Links |
|---|---|---|---|
| 2.2 kΩ resistor | 1 | R18 if the amplifier has a 100 k pull-up on SD (E-M1) | in the assortment |
| 4.7 kΩ resistor | 1 | R1 if D1 leaks too much when warm (E-M3) | in the assortment |
| USB charger **5 V ≥ 2 A** + micro-USB cable | 1 | running on mains while charging (if you don't have one already) | [Amazon (search)](https://www.amazon.fr/s?k=chargeur+usb+5V+2A) |

## 5. Protection (to check: already ordered on 2026-10-20?)

| Item | Qty | Criteria | Links |
|---|---|---|---|
| Radial PTC resettable fuse **1.6 A** (trips ~3.2 A), ≥ 16 V | 2 | F1, F2. The Bourns **MF-R160** is rated **30 V** (body Ø10.2 × 3, 5.1 pitch): fine at 4.2 V | [MF-R160 at Mouser (search)](https://www.mouser.fr/c/?q=MF-R160) · [Digi-Key sheet](https://www.digikey.fi/en/products/detail/bourns-inc/MF-R160/259972) |
| **SMAJ5.0A** TVS diode (unidirectional) | 1 (lot) | D3, TP4056 input | [Amazon (search)](https://www.amazon.fr/s?k=SMAJ5.0A) · [AliExpress (search)](https://fr.aliexpress.com/w/wholesale-smaj5.0a.html) |

## 6. Printing (no filament yet)

| Item | Qty | For | Links |
|---|---|---|---|
| **Matte grey** PLA 1.75 mm | 1 kg | columns, lids, splints | [Amazon (search)](https://www.amazon.fr/s?k=PLA+gris+mat+1.75) |
| **Matte black** PLA 1.75 mm | 250–500 g | panel plugs, speaker grille | [Amazon (search)](https://www.amazon.fr/s?k=PLA+noir+mat+1.75) |
| PETG (any colour) | leftover is enough | 3 tube collars | — |

## Reminder: already in stock or ordered (don't buy again)

LOLIN S3 Mini, 2 × 1.3" screens, 2 × 18650, protected TP4056, micro-USB breakout, switch, DS3231, ADXL345, INMP441,
BME280, AM312, MAX98357A, 39 × 22 × 10 speaker, TPS63020, AO3401A, 1N5822, microSD reader, contact plates, 8/7 brass
tubes, M2.5 screws, feet, 26 AWG wire. To check in the 2026-10-20 order: fuses, TVS, resistors.

## Sources

- SN-28B Dupont kits on Amazon.fr: [Glarks](https://www.amazon.fr/Glarks-connecteur-cliquet-Connecteur-AWG28-18/dp/B07VQ6YNSC), [JZK](https://www.amazon.fr/JZK-Cliquet-Connecteurs-Assortis-Sertissage/dp/B07PCQ5VMV), [Taiss](https://www.amazon.fr/Taiss-connecteurs-SN-28B-pression-Connecteur/dp/B0BYMT2BRP), [XH2.54 + SN-28B](https://www.amazon.fr/XH2-54-connecteurs-Dupont-barrettes-broches/dp/B092VPWSK4)
- 30 AWG wire: [BNTECHGO](https://bntechgo.com/bntechgo-30-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-25-feet-high-temp-200-c-600v-30-awg-silicone-wire-11-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/)
- Fuse: [Digi-Key MF-R160](https://www.digikey.fi/en/products/detail/bourns-inc/MF-R160/259972), [Octopart](https://octopart.com/part/bourns/MF-R160)
- JST XH (real pitch 2.5 mm, fits 2.54 on short rows): [Pololu](https://www.pololu.com/product/2717)
