# TARS4 — questions en suspens (mis à jour le 2026-10-22)

Regroupe ce qui reste ouvert après les trois séries de relectures (`reviews/2026-10-21-review.md`, `reviews/2026-10-21-review2.md`,
`reviews/2026-10-22-review3-boards.md`).
Les bloquants B1–B2, les décisions D1–D12, les améliorations et les corrections de doc sont **appliqués** (options
recommandées, D11 : inter. gardé) ; le README décrit l'état actuel (plus de journal des décisions : historique dans `backups/README.md.bak-20261022-consolidate` et `reviews/`).

## 1. Bloquants — réglés

| # | Problème | Ce qui a été fait |
|---|---|---|
| B1 | Boîtiers Dupont sans détrompeur | broche inutile retirée + case bouchée (X2 INT2, X8 32K, X5 GAIN avec X5 en 4 + 3) ; une case de plus bouchée côté femelle sur les paires en ligne (X3, X7, X15) ; écrans : barrette coudée + nervure collée sur le boîtier ; X14 en JST-PH 3 ; X6 et X9 sans détrompeur (à l'envers, rien ne casse). Ordre des broches dans le README (*Connectors*) |
| B2 | TP4056 contre la lèvre de sa rainure | plus de lèvre haute (appui dessous seulement) pour le TP4056 et le TPS63020, une patte du couvercle tient le bord arrière ; le micro-USB du TP4056 reste en place ; C9 / D3 couchés sur l'extrémité IN (`charger_h` 5,5) |

## 2. Décisions — prises

D1 barrette coudée · D2 nervure continue · D3 X10–X14 rangés au-dessus du TP4056, cartes une par une · D4 SCK séparé
sur le support (R12 / R19 47 Ω) · D5 15 attaches imprimées · D6 fentes d'aération · D7 R21 + C12 sur l'AM312, C10 +
C11 sur P2, PWM 20 kHz · D8 C1 tantale polymère CMS 7343 (POSCAP 10TPE220ML) couché sous la S3, sur son support (2026-10-24) · D9 couvercle `lid_mid_left` · D10 Q5 sur le 3V3 de la microSD (GPIO36)
· D11 inter. gardé · D12 chargeur 5 V ≥ 2 A.

## 3. Nouvelle question

| # | Question | Options |
|---|---|---|
| D13 | **Chargeur IP2312 (2 A, à découpage) à la place du TP4056** : pas de R_PROG à changer, ~0,47 W à 2 A au lieu de 0,65–1 W à 0,5 A. | voir la réponse du 2026-10-21 : il faut garder une protection DW01 à part, et 2 A de charge + 1 A pour TARS dépassent le micro-USB et les JST-PH ; il ne tient pas à plat dans la jambe (34,4 × 15) |

## 4. Mesures à faire à réception des pièces

**Électriques**

| # | Mesure | Ce qui en dépend |
|---|---|---|
| E-M1 | Pull-up de SD sur la carte ampli (1 M ? 100 k ?) | R18 : 10 k si 1 M, **2,2 k si 100 k** ; couper la piste si SD est relié à VIN |
| E-M2 | Pull-up et courant de BLK sur les écrans | à retirer s'il existe (~0,66 mA en veille pour deux écrans) ; Q2 / Q3 si BLK alimente les LED |
| E-M3 | Fuite de D1 (1N5822) en inverse à 4,2 V, tiède (~50 °C) | > 50 µA → R1 4,7 k ou autre Schottky |
| E-M4 | Niveau haut de la sortie de l'AM312 à 3,3 V | doit dépasser 2,5 V |
| E-M5 | Le module DW01 s'allume-t-il seul à la première connexion des cellules ? | certains attendent un premier branchement du chargeur |
| E-M6 | Calibre de l'inter. SW1 (≥ 1 A voulu) | sinon un inter. 1–2 A |
| E-M7 | Courant de veille réel, carte microSD présente et absente | D10 |
| E-M8 | Température du TP4056 après 15 min de charge à 0,5 A | D6 |

**Cotes (valeurs `MEASURE` du modèle)**

| # | Mesure | Paramètres |
|---|---|---|
| D-M1 | AM312 : cache par l'extérieur (5,7 mm de saillie) ou collé dedans (plaque `pir_test`) ; décalage plaque/axe | `pir_test_holes`, `pir_pcb_dn` (cotes mesurées le 23/10) |
| D-M2 | Barrettes femelles et entretoise des broches de la S3 | `s3_sock_h`, `s3_pin_base` |
| D-M3 | Boîtiers Dupont, paires XH emboîtées, queues de sertissage | `dp_t`, `dp_on`, `dp_inline`, `xh_inline` |
| D-M4 | Position des pastilles du TP4056 et du TPS63020 par rapport au bord | B2, `charger_lip`, `bk_lip` |
| D-M5 | Dos des écrans (nappe, composants), rangée de broches | D1, `scr_hdr_dz` |
| D-M6 | Barrette coudée de la ZS-042 | `rtc_hdr_y` |
| D-M7 | Fusibles couchés (MF-R160 : Ø10,2 × 3, pas 5,1) | `fuse` |
| D-M8 | Et toutes les autres valeurs `MEASURE` (écrans, TP4056, TPS63020, microSD, micro-USB, plaquettes, BME280…) | liste dans le README, « to do when the parts arrive » |

**Autres** : angle de balancement voulu pour les jambes (longueur libre à la torsion des fils) ; état des commandes du 2026-10-20 (D3, fusibles, résistances).

## 5. Points de la première relecture et corrections de doc — appliqués

Rien d'ouvert hors des mesures ci-dessus.

## 6. Relecture n° 3 des plaques (2026-10-22) — appliquée

Toutes les plaques sont **simple face**. Appliqué : M1 OUT+ seul en B4 + règle anti-pâté étendue à toute paire
puissance / autre réseau ; M2 R2 couchée J8 → J5 (J7 vide à côté de Q5) ; M3 pattes de Q1 / Q5 en fil à wrapper isolé
30 AWG, sens de collage dessiné (vu de dessus, retourné) ; M4 fils du support partant vers l'intérieur ; m1 support
découpé à 1,2 mm sous la rangée 1 (`s3_dummy` à 8,8) ; m2 `pp_lip` 0,6 + R2 en 1/8 W (jambe G haute réexportée) ;
m3 valeurs de contrôle ; m4 contact V retiré de la barrette ; m5 noms du schéma partout (AMP_SD_S3 / AMP_SD,
PIR / PIR_OUT, SCK_S3, *_S3 côté S3) + contrôle automatique des plaques contre `kicad_sch_gen.py` ; m6 P1 sans 26 AWG
en colonne A, cavalier de P2 côté cuivre ; m7 C12 ≤ 7 mm → tantale 10 µF 16 V (2026-10-24) ; m8 contacts Dupont doubles documentés ; m9 fil à wrapper,
fil étamé, colle au BOM ; m10 corrections de doc (C10 non polarisé dans KiCad) ; remarques R1, R3, R4, R6, R7. D14 (fil B+ de mesure en 30 AWG, R2 sur la plaquette) : **gardé tel quel** (décision du 2026-10-22).

| # | Reste ouvert | Options |
|---|---|---|
| D-M9 | Position réelle de la 1re rangée de broches de la S3 (8,8 mm du bord USB d'après le dessin LOLIN) | marges de découpe du support (`my0` dans `tools/boards.py`) |

## 7. Relecture du guide de câblage (2026-10-24) — appliquée

Aucun point bloquant. Appliqué : gaine thermo fermée sur chaque bout libre avant toute mise sous tension (étapes 3–6) ;
préparation du lecteur microSD à l'étape 5 (C4 tantale **couché** : ~6,6 mm jusqu'au TPS63020, C5, R5–R9) ; polarités
dans le guide (C9 / D3 sur IN+, C7 + sur VIN) ; C2 / C10 dessinés polarisés (tantale, + en G9 / F9) sur les plans et dans
KiCad, C4 aussi ; X12 / X16 côté bloc coiffés d'un boîtier XH vide tant qu'ils ne sont pas branchés ; épissures avant les
pastilles IN+ / B+ / B− du TP4056 ; essai < 10 µA sur le TP4056 seul ; **R20 33 Ω en série sur MOSI** (support C9–C10,
cavalier J4 depuis A6) ; scan I2C avec 0x57 / 0x77 ; masque EXT1 sans les sources déjà hautes ; contacts doubles de X2,
torsades du tube droit, « sans replier » pour deux fils par contact, longueurs par couleur du README, règle h ≤ 9 sur P1 / P2.
Non appliqué : R2 sur la pastille B+ (D14, décision du 2026-10-22 maintenue).

- D-M1 AM312 tranché (2026-10-24) : cache collé par l'intérieur, trou Ø11,5 (dôme affleurant, essai Pro Micro) ; trous imprimés ~0,6 mm trop petits.
- `sd_fwd` = 2 (2026-10-24) : carte microSD 3 mm hors du couvercle, 4,5 mm devant le lecteur.
