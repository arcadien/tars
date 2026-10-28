# TARS4 — liste d'achats (2026-10-24)

Ce qui reste à acheter après la commande du 2026-10-20, les corrections de la revue et le plan « tout démontable ».
Les liens marqués **(recherche)** ouvrent une recherche avec les bons mots-clés : prendre une offre qui correspond aux
critères donnés. Les liens directs ont été trouvés le 2026-10-21, prix et stock non garantis.

## 1. Câblage démontable (nouveau)

| Article | Qté | Critères | Liens |
|---|---|---|---|
| Pince à sertir **SN-28B** à cliquet + kit Dupont 2,54 | 1 kit | boîtiers 1 à 8 broches (dont 1 × 3, 1 × 4 et 1 × 6), **~100 contacts femelles** (~55 utilisés), contacts **mâles** (≥ 20, aussi pour boucher les cases de détrompage), 3 boîtiers mâles pour les paires en ligne (X3, X7, X15) | [Glarks 486 pcs (~19 €)](https://www.amazon.fr/Glarks-connecteur-cliquet-Connecteur-AWG28-18/dp/B07VQ6YNSC) · [JZK (~22 €)](https://www.amazon.fr/JZK-Cliquet-Connecteurs-Assortis-Sertissage/dp/B07PCQ5VMV) · [Taiss 600 pcs (~24 €)](https://www.amazon.fr/Taiss-connecteurs-SN-28B-pression-Connecteur/dp/B0BYMT2BRP) |
| Boîtiers **JST-XH 2,5** à sertir, mâles + femelles, avec leurs contacts : **2, 3 et 4 broches** (en stock : vérifier qu'il y a bien les deux côtés de chaque paire) | 2 × 2 br., 1 × 3 br., 2 × 4 br. | X12 et X16 (une par cellule, jonction sur les pastilles B+ / B− du TP4056) ; X14 (VBAT/2, USB_DET, SD_EN) ; X10 (port de charge + inter., 4 br.) et X13 (sorties du bloc alim). Plus de JST-PH : X11 est fusionné dans X10. Sertis à la SN-28B ; fils 30 AWG repliés comme dans les contacts Dupont | en stock |
| Barrettes **femelles 2 × 8**, pas 2,54, hauteur **8,5 mm** | 2 (lot) | support de la S3 ; mesurer la hauteur réelle → `s3_sock_h` | [Amazon (recherche)](https://www.amazon.fr/s?k=barrette+femelle+2x8+2.54) · [AliExpress (recherche)](https://fr.aliexpress.com/w/wholesale-female-header-2x8-2.54.html) |
| **Plaque à pastilles simple face** (une pastille par trou, pas de bandes, cuivre sur une seule face), 2,54, de préférence en **époxy FR4** (verte ou jaune pâle) plutôt qu'en bakélite FR2 (marron : pastilles qui se décollent à la chaleur) | 1 (lot) | support de la S3 découpé à 25,6 × 34,4 (10 × 13 trous) et plaquette du partage de charge à 26,6 × 20 (10 × 8 trous) : plans renders/tars4_board_*.svg | [Amazon (recherche)](https://www.amazon.fr/s?k=plaque+pastilles+simple+face+2.54+FR4) |
| Fil à wrapper **30 AWG** isolé (Kynar), petite bobine | 1 | pattes de Q1 / Q5 sur la plaquette du partage de charge (remplace les brins nus), cavaliers isolés | [Amazon (recherche)](https://www.amazon.fr/s?k=fil+wrapping+30+AWG+kynar) |
| Fil de cuivre étamé nu 0,5–0,6 mm | ~0,5 m | bus GND (colonne E du support, rangée 1 de la plaquette du partage de charge) ; des chutes de pattes de résistances suffisent | [Amazon (recherche)](https://www.amazon.fr/s?k=fil+cuivre+etame+0.6mm) |
| Colle cyanoacrylate ou époxy 5 min | — | barrettes femelles collées sur le support simple face de la S3 | probablement déjà en stock |
| Barrette mâle 1 × 40 (sécable), droite + **coudée** | 1 + 1 | X6 (sortie HP de l'ampli) ; barrettes coudées 1 × 8 au dos des deux écrans (X1, X4) ; broches des modules livrés sans | [Amazon (recherche)](https://www.amazon.fr/s?k=barrette+male+secable+2.54+droite+coudee) |
| Gaine thermo 1,5 / 2 / 3 mm, **assortiment de couleurs** (au moins noir, blanc, jaune, orange, violet) | 1 assortiment | sous les ailettes d'isolant des contacts (fil 30 AWG trop fin), soudures, sorties de tube ; bagues noires des bus de signaux (1 / 2 / 3) ; **bagues de couleur des rails d'alimentation** rouge / noir en Ø2–3 mm (blanche OUT+, jaune VPATH, orange VSYS, violette VUSB : ~40 bagues de 10 mm) | [Amazon (recherche)](https://www.amazon.fr/s?k=gaine+thermoretractable+assortiment+1.5mm) |

## 2. Fil

| Article | Qté | Critères | Liens |
|---|---|---|---|
| Fil silicone **30 AWG**, cuivre **étamé** (pas CCA), multicolore | ~20,3 m au total (longueurs à couper du guide de câblage), ≤ 3,6 m par couleur | **kit 10 couleurs** (×7,6 m) : il faut le **violet** (sélections CS / LRC / WS / CMD) et le **bleu** (GND des écrans et capteurs) ; noir et gris inutilisés en 30 AWG | [BNTECHGO 10 couleurs × 25 ft (fabricant)](https://bntechgo.com/bntechgo-30-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-25-feet-high-temp-200-c-600v-30-awg-silicone-wire-11-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/) · [Amazon (recherche)](https://www.amazon.fr/s?k=fil+silicone+30+AWG+kit+couleurs+cuivre+etame) |
| Fil silicone 26 AWG | ~7,7 m (rouge 3,3 m, noir 2,5 m, bleu 0,8 m, blanc 0,8 m, gris 0,3 m) | déjà en stock (kit 10 couleurs) : **vérifier qu'il y a 3,3 m de rouge et 2,5 m de noir** (règle des paires : rouge / noir pour batterie, VUSB, VSYS) | — |

## 3. Composants ajoutés par la revue

| Article | Qté | Rôle | Liens |
|---|---|---|---|
| Résistance **2,4 kΩ**, traversante 1/4 W ou 1/8 W (ou CMS 0805 / 1206) | 1 (+ réserve) | R_PROG du TP4056 (charge 0,5 A) : la CMS d'origine retirée, la traversante couchée sur la carte, pattes soudées sur ses deux pastilles ; souvent déjà dans un assortiment de résistances 1/4 W (sinon 2,2 k + 220 Ω en série) | [Amazon (recherche, assortiment 1/4 W)](https://www.amazon.fr/s?k=assortiment+resistances+1%2F4W+1%25) |
| Condensateur électrolytique **22 µF 16 V** | 1 | C9, entrée du TP4056 : **en stock** (Ø5,15, couché ; `charger_h` porté à 6) | — |
| Résistances traversantes 1/4 W : **1 kΩ** ×2, **10 kΩ** ×1, **47 Ω** ×2, **33 Ω** ×1, **100 Ω** ×1, **100 kΩ** ×1 ; **1 MΩ 1/8 W** ×1 | — | R17, R18 ; R12 / R19 (SCK séparé) ; R20 (MOSI) ; R21 (filtre AM312) ; R22 (grille de Q5) ; R2 (couchée sous la lèvre de la rainure ; une 1/4 W passe aussi) ; inutile si l'assortiment est déjà là |
| P-MOSFET **AO3401A** (SOT-23) | 1 de plus | Q5, coupe le 3V3 de la microSD en veille (déjà commandé pour Q1 : vérifier qu'il en reste un) |
| Condensateur **C12** : tantale **10 µF 16 V** (+ en F6) à la place du 47 µF | 1 | filtre de l'AM312 sur P2 : **en stock** (le 47 µF en stock fait 12 mm, trop haut ; le tantale coupe encore le PWM 20 kHz du rétroéclairage de ~40 dB) | — |

## 4. Condensateurs

| Article | Qté | Rôle | Liens |
|---|---|---|---|
| **220 µF CMS 7343** (7,3 × 4,3), tantale ≥ 6,3 V | 1 | C1, couché sous la S3 : **en stock** (Panasonic POSCAP 10TPE220ML, polymère 10 V, ESR 25 mΩ) | — |
| Électrolytique **470 µF 10 V**, **Ø ≤ 8 × 12** | 1 | C7, VIN de l'ampli (couché derrière la carte) : **en stock** (Ø8 × 11,5) | — |
| **10 µF** céramique X5R/X7R (« 106 ») ou **tantale 16 V** (+ au 3V3), pas 2,54, h ≤ 10 | 4 | C2 sur P1, C4 au lecteur microSD, C10 et C12 sur P2 : **tantales 16 V en stock** (6, 2 de réserve) | — |
| **100 nF** céramique (« 104 ») traversant, pas 2,54, corps ≤ ~4 mm, **ni tantale** pour C6 | 5 | C3, C5, C6, C8, C11 : **en stock** (petites céramiques traversantes) | [Amazon (recherche)](https://www.amazon.fr/s?k=assortiment+condensateur+ceramique+104) |

## 4 bis. Selon les mesures

| Article | Qté | Pour | Liens |
|---|---|---|---|
| Résistance 2,2 kΩ | 1 | R18 si l'ampli a un pull-up de 100 k sur SD (E-M1) | dans l'assortiment |
| Résistance 4,7 kΩ | 1 | R1 si D1 fuit trop à chaud (E-M3) | dans l'assortiment |
| Chargeur USB **5 V ≥ 2 A** + câble micro-USB | 1 | marche sur secteur pendant la charge (si tu n'en as pas déjà un) | [Amazon (recherche)](https://www.amazon.fr/s?k=chargeur+usb+5V+2A) |

## 5. Protection (à vérifier : déjà commandés le 2026-10-20 ?)

| Article | Qté | Critères | Liens |
|---|---|---|---|
| Fusible réarmable PTC radial **1,6 A** (déclenche ~3,2 A), ≥ 16 V | 2 | F1, F2. Le Bourns **MF-R160** est donné pour **30 V** (corps Ø10,2 × 3, pas 5,1) : suffisant à 4,2 V | [MF-R160 sur Mouser (recherche)](https://www.mouser.fr/c/?q=MF-R160) · [fiche Digi-Key](https://www.digikey.fi/en/products/detail/bourns-inc/MF-R160/259972) |
| Diode TVS **SMAJ5.0A** (unidirectionnelle) | 1 (lot) | D3, entrée du TP4056 | [Amazon (recherche)](https://www.amazon.fr/s?k=SMAJ5.0A) · [AliExpress (recherche)](https://fr.aliexpress.com/w/wholesale-smaj5.0a.html) |

## 6. Impression (pas encore de filament)

| Article | Qté | Pour | Liens |
|---|---|---|---|
| PLA **gris mat** 1,75 mm | 1 kg | colonnes, couvercles, éclisses | [Amazon (recherche)](https://www.amazon.fr/s?k=PLA+gris+mat+1.75) |
| PLA **noir mat** 1,75 mm | 250–500 g | caches des panneaux, grille du HP | [Amazon (recherche)](https://www.amazon.fr/s?k=PLA+noir+mat+1.75) |
| PETG (toute couleur) | un reste suffit | 3 bagues des tubes | — |

## Rappel : déjà en stock ou commandé (ne pas racheter)

LOLIN S3 Mini, 2 écrans 1,3", 2 × 18650, TP4056 protégé, breakout micro-USB, interrupteur, DS3231, ADXL345, INMP441,
BME280, AM312, MAX98357A, HP 39 × 22 × 10, TPS63020, AO3401A, 1N5822, lecteur microSD, plaques de contact, tubes
laiton 8/7, vis M2,5, pieds, fil 26 AWG. À vérifier dans la commande du 2026-10-20 : fusibles, TVS, résistances.

## Sources

- Kits Dupont SN-28B sur Amazon.fr : [Glarks](https://www.amazon.fr/Glarks-connecteur-cliquet-Connecteur-AWG28-18/dp/B07VQ6YNSC), [JZK](https://www.amazon.fr/JZK-Cliquet-Connecteurs-Assortis-Sertissage/dp/B07PCQ5VMV), [Taiss](https://www.amazon.fr/Taiss-connecteurs-SN-28B-pression-Connecteur/dp/B0BYMT2BRP), [XH2.54 + SN-28B](https://www.amazon.fr/XH2-54-connecteurs-Dupont-barrettes-broches/dp/B092VPWSK4)
- Fil 30 AWG : [BNTECHGO](https://bntechgo.com/bntechgo-30-gauge-silicone-wire-kit-ultra-flexible-10-colors-each-25-feet-high-temp-200-c-600v-30-awg-silicone-wire-11-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/)
- Fusible : [Digi-Key MF-R160](https://www.digikey.fi/en/products/detail/bourns-inc/MF-R160/259972), [Octopart](https://octopart.com/part/bourns/MF-R160)
- JST XH (pas réel 2,5 mm, compatible 2,54 sur de courtes rangées) : [Pololu](https://www.pololu.com/product/2717)
