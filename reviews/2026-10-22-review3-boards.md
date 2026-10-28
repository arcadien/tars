# TARS4 — relecture n° 3 : les quatre plaques câblées à la main (2026-10-22)

Relecture en lecture seule des plaques décrites dans `tools/boards.py` (support de la S3, P1, P2, plaquette du
partage de charge) contre la netlist KiCad, `tools/kicad_sch_gen.py`, le README, `liste_achats.md`, les deux pages HTML
et `tars4.scad`. Aucun fichier du projet n'a été modifié. Ce qui a été lancé :
- une copie de `boards.py` dans le scratchpad : les 4 plaques passent leurs propres contrôles (s3 : 31 réseaux et
  27 fils, p1 : 6 et 23, p2 : 9 et 16, alim : 11 et 15), et les SVG régénérés sont **identiques octet pour octet** à
  ceux de `renders/` ;
- `kicad-cli sch export netlist` sur `kicad/tars4.kicad_sch` : la netlist exportée est identique aux dictionnaires
  `nets` de `kicad_sch_gen.py`.

## Résumé

L'équivalence avec la netlist est bonne : chaque pièce des quatre plaques (référence, valeur, réseau de chaque
broche, numéro de GPIO, résistances série, rappels et découplages) correspond au schéma, la carte des broches de la
S3 correspond au dessin et à la photo LOLIN, et toutes les destinations des fils sont cohérentes d'une plaque à
l'autre et avec le tableau des connecteurs X1–X15 et le décompte par tube (13 / 19 / 6). Aucun **bloquant**.

Les points importants portent sur l'implantation et la mécanique, et surtout sur la **plaquette du partage de
charge** : la règle anti-pâté de soudure de `boards.py` ne compare pas deux réseaux de puissance entre eux, et OUT+
est posé juste au-dessus de VSYS. Q5 est collé contre le B+ nu, et les brins nus de Q1 se croisent forcément une fois
le boîtier retourné. Côté **support de la S3**, les fils soudés sur les colonnes A et J ne peuvent pas respecter la
consigne « x 5–25 » du README et passent sous les pattes du couvercle.

| Gravité | Nombre |
|---|---|
| Bloquant | 0 |
| Majeur | 4 |
| Mineur | 10 |
| Remarque | 7 |

## Majeur

### M1 — Alim : OUT+ (C4–D4) juste au-dessus de VSYS (C3–D3), et la règle de sécurité ne le voit pas
- **Où** : plaquette du partage de charge, ponts C4–D4 (OUT+, fil C4 vers le OUT+ du TP4056 + brin D de Q1) et C3–D3
  (VSYS : retour de l'inter. en D3, départs TPS63020 et ampli en C3). Les deux ponts sont parallèles, à 2,54 mm.
- **Preuve** : `tools/boards.py:209-210` (ponts), `:218-221` (fils) ; la règle de sécurité `:325-331` ne signale une
  paire que si l'un des réseaux est un réseau de puissance **et** l'autre GND, une GPIO ou 3V3 / SD_3V3. Une paire
  puissance–puissance (OUT+ ↔ VSYS) n'est jamais testée. Le README `:498-499` la décrit comme une garantie générale.
- **Risque** : un pâté entre les deux ponts court-circuite Q1 **et** SW1. Sur batterie, TARS ne s'éteint plus. Sur
  secteur avec SW1 fermé, VUSB → D1 → VPATH → SW1 → VSYS → OUT+ recharge les cellules à travers le DW01 **sans la
  régulation CC/CV du TP4056** : seuls la coupure de surcharge du DW01 (~4,3 V) et les polyfusibles limitent le
  courant.
- **Correction** : poser OUT+ en **B4** (fil OUT+ côté soudures + brin D de Q1, qui part vers l'avant-gauche depuis
  C5), puis supprimer C4 et le pont C4–D4. Les quatre voisins de B4 (A4, C4, B3, B5) sont alors vides, et ses deux
  voisins en diagonale A5 / C3 sont à 3,6 mm. Étendre la règle de `check()` aux paires de réseaux de puissance
  différents (au moins OUT+ ↔ VSYS / VPATH / VUSB, B+ ↔ tout le reste), puis relancer.

### M2 — Alim : Q5 collé en I7, à côté de la patte nue B+ de R2 (J7)
- **Où** : Q5 (`_at` I7), avec ses pattes S = 3V3, D = SD_3V3 et G, et ses brins nus de 28 AWG. J7 porte la patte
  de R2 côté composants et le pont J7–J8 vers le fil B+ (B+ direct des cellules, protégé seulement par
  2 × 1,6 A).
- **Preuve** : `tools/boards.py:202` (R2 J7→J4), `:204` (Q5 en I7), `:215` (pont J7–J8). Le contrôle ignore les
  trous `_at` (`:276`) et ne sait rien des brins. Une fois Q5 retourné avec D vers l'avant (I6), la patte S (3V3)
  tombe du côté est, donc vers J7, à ~1 mm de la patte de R2.
- **Risque** : un brin ou une patte qui touche J7 met 4,2 V sur tout le 3V3 (S3, écrans, capteurs ; 3,6 V maximum
  absolu) : c'est destructif. Le lien d'achat « plaque à pastilles … double face » (`liste_achats.md:15`) donne en plus
  des pastilles côté composants, donc du cuivre nu sous et autour des SOT-23 collés.
- **Correction** : coucher R2 de **J8 à J5** (corps sur J7–J6 : c'est couché, donc compatible avec la zone de
  l'attache de toron) et relier J5 à J4 (pont), J4–J3 et I4–J4 restant inchangés. J7 devient vide, B+ ne reste qu'en
  J8, et ce trou n'a aucun voisin occupé. Préciser une plaque **simple face** dans `liste_achats.md` (ou isoler les
  pastilles du dessus sous Q1 / Q5 avec du Kapton).

### M3 — Alim : brochage de Q1 retourné, les brins G et S se croisent
- **Où** : Q1 (`_at` C5) : S → A5 (à l'ouest), G → E5 (à l'est), D → D4 (vers l'avant). La note dit « G et S vers
  l'arrière, D vers l'avant ».
- **Preuve** : `tools/boards.py:197`. Un SOT-23 AO3401A (1 = G, 2 = S, 3 = D) vu de dessus a 1 à gauche et 2 à droite.
  Retourné pattes en l'air puis tourné pour que D regarde l'avant, il présente **G à l'ouest et S à l'est**. Les brins
  nus vers A5 (S) et E5 (G) doivent donc se croiser au-dessus du boîtier. C'est la même ambiguïté pour Q5 : le dessin
  ne dit jamais quelle patte est où une fois le boîtier retourné.
- **Risque** : un court-circuit G–S met VUSB sur VPATH. Sur batterie, Q1 reste bloqué (TARS tourne sur la diode
  interne, 0,6–0,7 V de chute), et R1 10 k vide les cellules en permanence (~0,4 mA, même inter. coupé).
- **Correction** : remplacer les brins nus par du **fil à wrapper isolé 30 AWG (Kynar)** pour Q1 et Q5 (l'ajouter au
  BOM et à la liste d'achats), et ajouter au dessin un petit croquis « vu de dessus, retourné » qui donne G / S / D. Une
  autre solution est de tourner Q1 avec D vers l'arrière (G à l'est, S à l'ouest) : seulement si OUT+ peut atterrir
  derrière, ce qui n'est pas le cas aujourd'hui (C6 / D6 sont sous le corps de D1).

### M4 — Support S3 : les fils des colonnes A et J sortent de la zone x 5–25 et passent sous les pattes du couvercle
- **Où** : support de la S3. Les fils sont soudés sur les queues des broches A4–A10 (dont le 3V3 en 26 AWG en A4),
  J5, J6, J8 et J9, plus le cavalier qui part de J7. La note demande de les replier « vers le bas ».
- **Preuve** : `tools/boards.py:90-106` et `:110`. Le README `:177` impose « soldered inward of x 5–25 (clear of the lid
  tabs) ». Or, dans la colonne (col_w 30,4, support centré), A est à x = 3,8 et J à x = 26,6. Les pattes du couvercle
  (`tars4.scad:889-894`, `kos` `:1172`) couvrent x ≤ 4,4 côté RST (d1_rib 0,8 + d1_notch 1,2) et x ≥ 26,0 de l'autre
  côté, sur les bandes z 4,5–7 et 27,9–30,4. Un fil de A ou de J replié le long du bord traverse forcément l'une de ces
  bandes.
- **Risque** : fils pincés entre la patte et le support (isolant 30 AWG entaillé, 3V3 en 26 AWG écrasé), couvercle qui
  ferme mal.
- **Correction** : dans `boards.py` (notes du support) et dans le README, écrire « chaque fil des colonnes A / B / I / J
  part d'abord à plat vers l'intérieur (colonnes C–H, côté soudures) avant de monter ou descendre ; rien à x < 5 ni à
  x > 25 dans les bandes 4,5–7 et 27,9–30,4 ». Mieux encore, dessiner la direction de sortie de chaque fil.

## Mineur

### m1 — Support S3 : la grille centrée ne tombe pas sous les broches de la S3
- **Où** : support, rangées 4–11. `boards.py` centre la grille (marge de 1,96 mm aux deux bouts : rangée 4 à 9,58 mm du
  bord USB).
- **Preuve** : dessin LOLIN `references/s3_mini_dimensions.png` : 1re rangée de broches à **8,8 mm** du bord USB et
  7,7 mm du haut, donc décentrée. `tars4.scad:1051` dessine les barrettes avec la 1re broche à 7,9 mm (c'est le bord de
  la pastille, voir le commentaire `:135`). Trois valeurs différentes.
- **Risque** : découpé comme sur le dessin, le support dépasse de 0,8 mm sous la S3 et se pose le premier sur les
  plots de vis. La S3 monte alors de 0,8 mm, et ses pastilles du haut (rangée EN / IO43, jusqu'à 28,3 mm) passent sous
  la nervure avant de la bande 27,9–30,4.
- **Correction** : découper le support avec **~1,2 mm sous la rangée 1 et ~2,7 mm au-dessus de la rangée 13** (bord bas
  aligné sur le bord USB de la S3), ou le recouper une fois les barrettes soudées et la S3 enfichée. Mettre à jour `my`
  dans `boards.py` et le 7,9 de `s3_dummy` (→ 8,8). À confirmer sur la S3 en main (D-M2).

### m2 — Alim : R2 couchée en colonne J sous la lèvre haute de la rainure
- **Où** : R2 J7→J4 (son corps Ø2,3–2,5 est centré à 1,87 mm du bord droit).
- **Preuve** : `tars4.scad:650` + `flat_slot` `:791-796` (`top = true`) : la lèvre haute recouvre 1,0 mm du bord
  (`pp_lip`), 0,3 mm au-dessus de la plaque. Le corps de R2 occupe 0,7–3,1 mm du bord, soit ~0,3 mm de recouvrement. Le
  modèle ne contrôle que la boîte `pp_parts`, centrée.
- **Correction** : `pp_lip` 1 → 0,6 (les pastilles commencent à ~0,97 mm du bord), ou R2 en 1/8 W (Ø1,8). Avec la
  correction de M2 (R2 en J8→J5), le problème reste le même : à traiter ensemble.

### m3 — Alim : les valeurs de contrôle de la note sont fausses
- **Où** : note « Contrôle : VUSB, VPATH, VSYS, OUT+ et B+ chacun > 1 MΩ vers GND sans les modules ; USB_DET = 100 k et
  VBAT/2 = 1 M ».
- **Preuve** : `tools/boards.py:233`. Sans les modules, VUSB voit R1 ∥ (R15 + R16) = 10 k ∥ 168 k ≈ **9,4 kΩ**, et
  USB_DET voit R16 ∥ (R15 + R1) = 100 k ∥ 78 k ≈ **44 kΩ**. Le 1 M de VBAT/2 est juste.
- **Correction** : « VUSB ≈ 9,4 kΩ, USB_DET ≈ 44 kΩ, VBAT/2 ≈ 1 MΩ, VPATH / VSYS / OUT+ > 1 MΩ, B+ ≈ 2 MΩ vers GND ».

### m4 — Support S3 : la broche V (VBUS de l'USB-C) n'est pas modélisée
- **Où** : J4 (V, sans réseau dans `S3_NET`), entre J5 (GND : joint du fil de 26 AWG + pont I5–J5) et I4 (MIC_SD, avec
  son fil).
- **Preuve** : `tools/boards.py:51-54` (aucune entrée pour `V`), `:86` (pont I5–J5), `:101` (I4). La règle de sécurité ne
  concerne que les plaques à pastilles et les réseaux de `POWER`, et V n'y figure pas.
- **Risque** : S3 sur le PC, un pâté J4–J5 court-circuite le 5 V du port USB, un pâté J4–I4 met 5 V sur GPIO15.
- **Correction** : retirer le contact V de la barrette femelle (ou couper sa queue à ras) pour que VBUS n'arrive
  jamais sur le support ; à défaut, ajouter `'V': 'VBUS'` et `VBUS` dans `POWER` pour que la règle le surveille.

### m5 — Noms AMP_SD / PIR inversés entre le support, P2 et le schéma
- **Où** : le fil A9 du support s'appelle `AMP_SD`, destination « P2 AMP_SD », et le fil B10 `PIR`, destination
  « P2 PIR ». Sur P2, `AMP_SD` (F11) et `PIR` (F4) désignent le côté **module** (ampli / AM312) ; le fil de la S3 y
  arrive en A11 `AMP_SD_S3` et A4 `PIR_S3`. Dans le schéma, `PIR` est le côté S3 et `PIR_OUT` le côté AM312.
- **Preuve** : `tools/boards.py:92`, `:95`, `:159`, `:166`, `:170`, `:178` ; `tools/kicad_sch_gen.py:351`, `:420`.
- **Risque** : en suivant la feuille du support, on soude le fil de la S3 sur la mauvaise moitié de bande. R10 / R17
  sont alors court-circuitées et A11 / A4 restent en l'air. Les deux fils ont en plus la même couleur et le même
  nombre de bagues que leur homologue côté module (marron 1 bague, rouge 1 bague).
- **Correction** : reprendre les noms du schéma partout (`AMP_SD_S3` / `AMP_SD`, `PIR` / `PIR_OUT`) et écrire sur le
  support « → P2 A11 (avant R10) » et « → P2 A4 (avant R17) ».

### m6 — P1 / P2 : les colonnes A et I sont sous les butées avant
- **Où** : P1 A5–A10 (dont les deux 26 AWG A9 / A10) ; P2 A4, A7–A11 et le lien isolé I10 → I5 côté composants.
- **Preuve** : `tars4.scad:276` (« keep ~1.5 mm free of holes at the side edges ») et `standing_mount` `:909-915` : les
  butées avant recouvrent 1,5 mm de la face composants sur toute la hauteur. Les trous A / I sont à 1,84 mm du bord : un
  26 AWG (Ø1,5) qui y entre déborde de ~0,4 mm sous la butée, et le lien isolé de P2 (`boards.py:167`) longe la colonne I
  sur 5 rangées.
- **Correction** : passer le lien I10–I5 de P2 **côté cuivre** (fil isolé : les pattes du couvercle ne touchent que les
  rangées 1 et 12), et noter « fils des colonnes A / I repliés vers l'intérieur dès la sortie du trou ». Sur P1, on peut
  aussi faire entrer les deux 26 AWG en B9 / B10 et les fils de la S3 en A9 / A10.

### m7 — P2 : hauteur de C12 devant la plaque
- **Où** : C12 47 µF 10 V, électrolytique Ø5 debout (F6 / F5), côté composants, vers la façade.
- **Preuve** : `tools/boards.py:164` ; `tars4.scad:277` (`hub_y` 12) : il reste 12 − 1,6 = **10,4 mm** jusqu'à la
  paroi avant. Un 47 µF 10 V Ø5 courant fait 11 mm de haut, plus la garde des pattes. Le modèle ne réserve que 1,6 mm
  devant P1 / P2 (boîte `P1 / P2`, `:1169`).
- **Correction** : spécifier un C12 de 7 mm de haut au plus (Ø5 × 7 ou Ø6,3 × 5,4), ou le coucher. Écrire aussi
  « hauteur ≤ 9 mm devant P1 / P2 » dans les notes (les résistances debout R10 / R17 / R18 font ~9 mm).

### m8 — Deux fils dans un même contact Dupont (X2, chaîne micro → ADXL345) : non documenté
- **Où** : X2 SDA / SCL reçoit le fil du support (B9 / B8) **et** celui qui part vers P2 (P2 A8 / A7) ; le 3V3 / GND de
  l'ADXL345 est « chaîné P1 → micro → ADXL345 » (P1 D9 / D11, « X3 micro … (→ ADXL345) »).
- **Preuve** : `tools/boards.py:96`, `:133`, `:132`, `:175-176` ; README `:546` (X2, « 5 wires »), `:573` (sertissage :
  brins repliés en deux) ; README `:406` (chaîne).
- **Correction** : écrire où se fait chaque dédoublement (côté femelle de X2 : deux 30 AWG sertis ensemble **sans**
  repli ; pour l'alimentation de l'ADXL345, depuis le côté faisceau de X3 et non depuis la queue du micro, sinon
  débrancher le micro coupe l'ADXL345), et compter ces contacts doubles dans le kit.

### m9 — Fournitures des plaques absentes du BOM et de la liste d'achats
- **Où** : brins de 28 AWG nu (Q1 / Q5), fil nu étamé pour les bus GND (colonne E du support, rangée 1 de l'alim), fil
  isolé fin pour les cavaliers.
- **Preuve** : `tools/boards.py:197`, `:230`, `:85`, `:213` ; absents de README `:602-660` et de `liste_achats.md`.
- **Correction** : ajouter « fil à wrapper 30 AWG (Kynar), 1 bobine » (voir M3) et « fil cuivre étamé 0,5–0,6 mm (ou
  chutes de pattes) ».

### m10 — Incohérences de documentation sur les plaques
- `boards.py:147` « Bandes 1–3 et 12 libres » sur P1 : ce sont **1–4** et 12 (MOSI est en rangée 5). `:184` « Bandes 1–2
  et 12 » sur P2 : ce sont **1–3** et 12 (PIR est en rangée 4).
- `tars4_schematic.html:128` et `:434` « P1 … 6 bandes (+6 libres) » : 7 bandes utilisées (2 GND) et 5 libres.
- `tars4.scad:269` : la liste des bandes de P1 contient encore « SCK », alors que SCK est séparé sur le support.
- README `:749` « C1 / C2 polarity » : C2 est une céramique (`boards.py:123`), sans polarité.
- `questions_en_suspens.md:18` D8 « C1 polymère couché » : C1 est maintenant debout sous la S3 (`boards.py:74`, README
  `:309`).
- `kicad_sch_gen.py:496` dessine C10 avec le symbole `C_Polarized`, alors que le BOM (README `:639`) et `boards.py:161`
  en font une céramique.
- `tars4_wiring.html:103` « VBAT/2 · USB_DET (orange) » sur une pastille marron : VBAT/2 est marron, USB_DET orange.
- README `:468` « Every combination is unique inside each tube » : dans le tube gauche, il y a **deux 26 AWG bleus**
  (GND logique vers P1 et GND de l'ampli). Les différencier (1 bague sur le GND de l'ampli, ou noter que c'est la
  torsade qui le désigne).

## Remarques

- **R1 — D1 1N5822** (`boards.py:196`) : percer à 1,5 mm des pastilles de ~1,8–2 mm n'y laisse presque plus d'anneau, et
  avec 12,7 mm entre trous pour un corps de 9,5 mm, les pattes de 1,3 mm se plient à 1,6 mm du corps. Percer à 1,3 mm,
  plier à la pince plate en tenant la patte côté corps, et compter sur les ponts A7–A8 / F7–G7 pour la tenue.
- **R2 — B+ de mesure en 30 AWG** (J8 → B+ du TP4056) : ce fil n'est protégé que par les deux polyfusibles (3,2 A au
  déclenchement chacun). Pour qu'un défaut d'isolant sur ce fil ne voie que des µA, on peut souder R2 directement sur
  la pastille B+ du TP4056.
- **R3 — Support S3, risques de pâté entre signaux** : le pont GND de la rangée 5 (E5–J5) passe entre BCLK (H4) et LRC
  (H6) côté S3, avant les 33 Ω, et B11 (VBAT/2) est voisin de A11 (EN). Contrôler ces paires à l'ohmmètre (à ajouter à
  la note `boards.py:112`).
- **R4 — Pièces conditionnelles sans emplacement** : R5–R9 (rappels de la microSD) et Q2 / Q3 (si BLK alimente les
  LED) ne sont sur aucune plaque. Les bandes libres 1–4 de P1 conviennent pour Q2 / Q3. R5–R9 vont sur le lecteur (X15
  ne transporte ni D1–D3 ni leur 3V3).
- **R5 — `boards.py` ne compare pas les plaques à la netlist** : la comparaison faite ici à la main (références,
  valeurs, réseau de chaque broche) passe. Un contrôle automatique (importer les `NETS` de `kicad_sch_gen.py` et faire
  correspondre les noms) éviterait les dérives comme m5.
- **R6 — D1 « bague côté VSYS »** (README `:626`, `tars4_schematic.html:109`) : la bague est côté **VPATH** (avant
  l'inter.), comme sur le dessin (A7). Sans effet, mais autant être exact.
- **R7 — Jeu entre les pièces debout et les barrettes, sous la S3** : R12 en C8, R13 / R14 / R11 en colonne H, C6 et
  C8 se retrouvent à ~0,1 mm du plastique des barrettes 2 × 8 (5,08 + 2 × 1,27 de large). Souder les barrettes
  d'abord, comme le dit la note, et redresser les pièces vers le centre.

## Vérifié et conforme

- **Netlist** : la netlist exportée par kicad-cli 10.0.7 est identique aux dictionnaires `nets`. Chaque pièce des
  plaques a la bonne valeur et chaque broche le bon réseau : support (R11–R14, R12 / R19 47 Ω, C1, C6, C8), P1 (R4, C2,
  C3), P2 (R10, R17, R18, R21, C10–C12), alim (D1, Q1, Q5, R1–R3, R15, R16, R22). Les pièces hors plaques (D3, C9, F1 /
  F2, C7, C4 / C5, R_PROG) ont toutes un emplacement sur un module ou dans le modèle.
- **Carte des broches de la S3** (`S3_PINS`, colonnes A / B / I / J, rangées 4–11) : conforme au dessin et à la photo
  LOLIN, vue côté composants, USB en bas, sans effet miroir entre la S3 et son support. Les numéros de GPIO cités sur P1
  / P2 / alim (IO1, 3, 4, 7, 8, 11, 13, 21, 36) correspondent aux trous du support. Les broches de démarrage (0, 45, 46)
  et USB (19, 20) ne sont pas utilisées ; GPIO3 est documenté, GPIO 33–38 sont libres sur la S3FH4R2 ; GPIO 2, 3 et 21
  sont des GPIO RTC (EXT1).
- **Continuité des bandes** : les coupes C11 et C4 de P2 isolent exactement A–B de D–I. Aucun groupe ne porte deux
  réseaux et aucun réseau n'est coupé en deux, sur les 4 plaques. P1 n'a pas besoin de coupe.
- **Orientations** : bague de D1 sur VPATH (A7) ; Q1 avec S = VPATH, D = OUT+, G = VUSB (diode interne bloquée sur
  secteur) ; Q5 avec S = 3V3, D = SD_3V3 (R22 vers 3V3, éteint quand la broche flotte) ; + de C1 sur 3V3 et + de C12 sur
  PIR_VDD.
- **Masse en étoile** : OUT−, GND du TPS63020, GND de l'ampli, R1, R3 et R16 sur le bus de la rangée 1. VSYS est à deux
  rangées du bus, et aucune GPIO (USB_DET, VBAT/2, SD_EN) ne touche un réseau de puissance.
- **Courant** : 26 AWG pour OUT+, VSYS, VUSB, les paires TPS / ampli et le 3V3 vers P1 puis la S3 (~0,1 V au plus) ;
  D1 3 A ; l'alimentation de P2 et de la jambe droite en 30 AWG (< 80 mA) suffit.
- **Faisceau** : les 27 + 23 + 16 + 15 fils ont des destinations cohérentes d'une plaque à l'autre et avec X1–X15
  (X13 = VSYS / GND de l'ampli + 3V3 / GND logique, X14 = VBAT/2, USB_DET, SD_EN, X15 = CLK, CMD, D0, SD_3V3, GND
  depuis P1). Le décompte par tube, refait à partir de `boards.py`, donne bien 13 / 19 / 6. Les couleurs et les bagues
  suivent le tableau du README.
- **Dimensions** : 25,6 × 34,4 (10 × 13), 24 × 32 (9 × 12) et 26,6 × 20 (10 × 8), identiques dans `boards.py`, le README
  et `tars4.scad` (`d1`, `hub_b`, `pp_b`).
- **Zones interdites** : rangées 12–13 du support vides (antenne), coins A3 / J3 / A12 / J12 vides. Sur l'alim, en
  colonne J rangées 3–6, seule R2 est posée, couchée (2,4 mm sous les 4,1 mm libres sous l'attache à z 179). Rangées 1
  et 12 de P1 / P2 libres sous les pattes du couvercle.
- **Hauteurs sous la S3** : pièces debout ≤ 10 mm pour 11 mm libres (8,5 + 2,5) ; C1 Ø6,3 en D2 / E2 sans toucher
  les barrettes.
