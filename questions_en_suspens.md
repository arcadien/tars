# TARS4 — questions en suspens (mis à jour le 2026-10-28)

Regroupe ce qui reste ouvert après les trois séries de relectures (`reviews/2026-10-21-review.md`, `reviews/2026-10-21-review2.md`,
`reviews/2026-10-22-review3-boards.md`).
Les bloquants B1–B2, les décisions D1–D12, les améliorations et les corrections de doc sont **appliqués** (options
recommandées, D11 : inter. gardé) ; le README décrit l'état actuel (plus de journal des décisions : historique dans `reviews/` et dans git).

## 1. Bloquants — réglés

| # | Problème | Ce qui a été fait |
|---|---|---|
| B1 | Boîtiers Dupont sans détrompeur | broche inutile retirée + case bouchée (X2 INT2, X8 32K, X5 GAIN avec X5 en 4 + 3) ; une case de plus bouchée côté femelle sur les paires en ligne (X3, X7, X15) ; écrans : barrette coudée + nervure collée sur le boîtier ; X14 en JST-PH 3 ; X6 et X9 sans détrompeur (à l'envers, rien ne casse). Ordre des broches dans le README (*Connectors*) |
| B2 | TP4056 contre la lèvre de sa rainure | plus de lèvre haute (appui dessous seulement) pour le TP4056 et le TPS63020, une patte du couvercle tient le bord arrière ; depuis le 2026-10-27 le TP4056 (raccourci à 26,3, micro-USB dessoudé) pose sur des appuis de 0,5 sans rainure ; C9 / D3 couchés sur l'extrémité IN (`charger_h` 5,5) |

## 2. Décisions — prises

D1 barrette coudée · D2 nervure continue · D3 X10–X14 rangés au-dessus du TP4056, cartes une par une · D4 SCK séparé
sur le support (R12 / R19 47 Ω) · D5 15 attaches imprimées · D6 fentes d'aération · D7 R21 + C12 sur l'AM312, C10 +
C11 sur P2, PWM 20 kHz · D8 C1 tantale polymère CMS 7343 (POSCAP 10TPE220ML) couché sous la S3, sur son support (2026-10-24) · D9 couvercle `lid_mid_left` · D10 Q5 sur le 3V3 de la microSD (GPIO36)
· D11 inter. gardé · D12 chargeur 5 V ≥ 2 A.

## 3. Ouvert maintenant

| # | Question | État |
|---|---|---|
| T1 | **Tube test3** (alésages en goutte, G7,95 / 8,0 / 8,05, R8,05 / 8,1 / 8,15) | à imprimer et mesurer → `tube_od` 7,93 + jeux + pivots en goutte, puis **une seule** passe STL + `tools/update_orca_project.py` sur `tars4.3mf`. Ne pas imprimer les colonnes avant |
| D13 | **Chargeur à découpage à la place du TP4056** | TP4056 gardé pour l'instant (500 mA, R_PROG 2,4k). Si E-M8 chauffe trop : R_PROG 3,6k (330 mA) ou jambe gauche basse en PETG ; alternative TP5100 1 A + DW01 séparé. IP2312 : ne tient pas à plat (34,4 × 15) |
| E-M8 | **Température du TP4056** (jambes en PLA) | mesurer la paroi à 15 et 30 min de charge : > 45 °C → R_PROG 3,6k. Radiateur cuivre RPi ≤ ~3 mm + pad thermique 0,5–1 mm entre puce et radiateur, jamais entre carte et PLA |

## 4. Mesures restantes

**Cotes** (`measurements.md`) : `bk_h` (hauteur de la self du TPS63020), `pir_pcb_dn`, zone active de l'écran vérifiée
allumé, queues de soudure côté paroi (ADXL345, MAX98357A, micro-USB), écran 0,85" si utilisé, D-M9 (1re rangée de
broches de la S3, marges `my0`).

**Électriques**, au banc (liste du README *to do when the parts arrive*) : E-M1 pull-up SD de l'ampli (R18), E-M2 BLK
des écrans, E-M3 fuite de D1 tiède, E-M4 niveau haut de l'AM312, E-M5 réveil du DW01, E-M6 calibre de SW1, E-M7 courant
de veille avec et sans microSD.

**Autre** : angle de balancement voulu pour les jambes (longueur libre des fils à la torsion).

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
