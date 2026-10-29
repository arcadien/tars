// TARS (Interstellar), 4-column variant: four independent hollow columns joined by hollow pivots.
// Each middle column holds a screen; the left one also holds the controller (LOLIN S3 Mini, D1 mini footprint), a
// spare breakout slot, the accelerometer and the microphone, the right one the speaker, the amplifier and the AM312 motion
// sensor; each has its distribution board below the screen. The legs hold the two cells; the power leg also the charge
// port, the switch, the microSD reader (card through a slot in its lid), the buck-boost, the charger and the power-path
// board, the other leg the RTC and the BME280 weather sensor.
// Proportions from the wiki: depth:width:height = 1:4:8 (overall, gaps included).
//
// Axes: x = width (left->right seen from the front), y = depth (0 = front face), z = height.
// Columns are numbered 0..3 from the left: 0 = left leg, 1 = left middle, 2 = right middle, 3 = right leg.
// Render one part: openscad -D 'part="col1"' -o col1.stl tars4.scad
// Display only: the JST-XH pairs use XH() from connectors.scad (next to this file); prints do not need it.
use <connectors.scad>

part = "assembly"; // assembly | open | open_ghost | col0..col3 | col<i>_bottom | col<i>_top | lid_<leg|mid>_<bottom|top> | splint | inserts | collar | test_screen | pir_test | tube_test | tube_test2 | tube_test3 | print_<part>

/* [Proportions] */
D = 31;                       // depth (mm). Minimum ~28.5 for a D1 mini alone (wall grooves), 30 for the 0.96" OLED, 31 for the 1.3" LCD
H = 8 * D;                    // height
gap = 0.8;                    // visible gap between columns
col_w = D - 3 * gap / 4;      // column width: 4 columns + 3 gaps = exactly 4D
col_x = [for (i = [0:3]) i * (col_w + gap)];
col_mid = [false, true, true, false];

/* [Shell] */
wall = 1.6;
clr = 0.2;                    // lid clearance

/* [Decor, from a film still (heights measured from the BOTTOM)] */
line_w = 0.8;                 // fine lines (plate joints)
line_d = 0.4;
panel_w = 0.9 * col_w;        // black panels: ~90 % of a column width
screen_panel_z = [H * 0.761, H * 0.877];
bottom_panel_z = [H * 0.132, H * 0.267];
// Black panels are cut THROUGH the front wall (a recess on the bed-side face would need a large bridge when the
// column prints front face down). The inserts are flush plugs, wall thick: the screen glass backs the screen plug,
// a 1 mm ledge inside (+ the splint) backs the lower one.
insert_clr = 0.15;
ledge = [1, 0.8];             // lower panel ledge: width on the wall around the hole, thickness
ledge_lip = 0.3;              // ledge overlap into the hole at the wall face, growing at 45 deg through the thickness
                              // (no support when printed front face down; the plug, 0.15 smaller, still rests on it)
mid_lines = [bottom_panel_z[0], H * 0.51];                    // horizontal lines on the middle columns (+ top of the screen panel)
leg_lines = [0.12, 0.20, 0.28, 0.64, 0.73, 0.82, 0.90] * H;   // plate joints on the legs
tars_text = true;             // vertical "TARS" + braille on column 1
text_font = "DejaVu Sans:style=Book";
text_len = 0.174 * H;
text_h = 0.3 * col_w;
text_z0 = H * 0.557;
braille = true;
braille_pitch = 0.0122 * H;
braille_cell = 0.0434 * H;
braille_dot = 1.8;
engrave_d = 0.6;

/* [Screens] */
// Catalogue: [id, [[key, value], ...]]. To add a screen, copy an entry and fill in its datasheet values.
//   desc         free text
//   module       [w, h] module outline, portrait orientation (mm)
//   thickness    total thickness incl. glass = depth of the holding frame (MEASURE yours)
//   active       [w, h] visible area
//   active_r     corner radius of the visible area
//   active_dx    horizontal offset of the visible area centre vs the module centre (+ = right)
//   active_dz    vertical offset of the visible area centre vs the module centre (+ = up)
//   glass_panel  true  = the black glass itself is the panel: through opening, no insert
//                false = a black insert with a window covers the panel
//   standoffs    undef (held by the frame only) or [hole spacing x, hole spacing y, hole d, height]
SCREENS = [
    ["lcd130cs", [
        ["desc", "1.3in IPS 240x240 ST7789 SPI WITH CS (8 pins), board 27.35 x 42.12 measured: two screens share one SPI bus -> one controller can drive both. Active 23.4 x 23.4; glass 27.35 x 29.9, 7.2 from the pad edge (top), 5 from the bottom: active area assumed centred in the glass (check lit). Holes 2.5, 1.7 from the long edges, 4.7 / 1.5 from the top / bottom edges (frame only, no standoffs)"],
        ["module", [27.35, 42.12]],
        ["thickness", 3.3],
        ["active", [23.4, 23.4]],
        ["active_r", 0],
        ["active_dz", -1.1],        // glass centre 1.1 below the board centre (7.2 / 5 from the edges)
        ["active_dx", 0],
        ["glass_panel", false],
        ["standoffs", undef]]],
    ["oled096", [
        ["desc", "0.96in SSD1306 OLED 128x64, I2C (4 wires), 27 x 27 board, 4-pin header on top; cheap and common"],
        ["module", [27, 27]],
        ["thickness", 4.1],
        ["active", [23, 12]],
        ["active_r", 0],
        ["active_dz", 1.7],
        ["active_dx", 0],
        ["glass_panel", false],
        ["standoffs", [23, 23.3, 1.6, 2.5]]]],
    ["lcd085", [
        ["desc", "Waveshare 0.85in IPS LCD 128x128, GC9107, SPI, MX1.25 8-pin. Board 22.5 x 19 (landscape), active 15.21 x 15.21. Glass position not on the drawing: MEASURE"],
        ["module", [22.5, 19]],
        ["thickness", 4],
        ["active", [15.21, 15.21]],
        ["active_r", 0],
        ["active_dz", 0],
        ["active_dx", 0],
        ["glass_panel", false],
        ["standoffs", undef]]],
    ["lcd130", [
        ["desc", "Generic 1.3in IPS 240x240 ST7789 (ZJY-IPS130-V2.0, e.g. Amazon B07QGPKWJ2), SPI without CS (one screen per D1 mini), 7 pins GND VCC SCL SDA RES DC BLK on top. Board 28 x 39, active 23.4 x 23.4. Offsets/holes measured on product photos: CHECK with the test piece"],
        ["module", [28, 39]],
        ["thickness", 4],
        ["active", [23.4, 23.4]],
        ["active_r", 0],
        ["active_dz", 1.7],
        ["active_dx", 0],
        ["glass_panel", false],
        ["standoffs", [23.2, 34.1, 1.6, 2.5]]]],
    ["lcd169", [
        ["desc", "Waveshare 1.69in IPS LCD 240x280, ST7789V2, SPI (needs D >= 36.5)"],
        ["module", [31.5, 39]],
        ["thickness", 4.6],
        ["active", [27.97, 32.63]],
        ["active_r", 4],
        ["active_dz", (1.916 - 4.45) / 2],
        ["active_dx", 0],
        ["glass_panel", true],
        ["standoffs", undef]]],
];
screen = "lcd130cs";
scr_win_bevel = 0.8;
scr_frame_w = 1.6;             // 4 lines at 0.4
scr_clr = 0.2;
scr_rib = 2.6;                // continuous lid rib along each side wall behind the screen (x reach): holds it against the
                              // frame without pinching the wires that come down between the ribs (x 5-25)

/* [Controller: LOLIN S3 Mini (ESP32-S3), D1 mini footprint (middle columns)] */
// The `d1` names are kept from the Wemos D1 mini it replaced (same 34.3 x 25.4 outline). Components facing the front,
// USB-C at the bottom through a floor opening. The board stands on the bottom lid screw posts; strips on the side walls
// centre it (above the side buttons), short ribs in front (just above the buttons and at the top) and tabs on the lid
// behind both ends hold it in depth, a lug on
// the lid stops it from rising. Socketed (s3_socket): every wire is soldered once on a carrier (perfboard, same
// outline) standing behind the S3, with two 2 x 8 female headers on its front; the S3 plugs into them with its male
// headers. The ribs hold the S3's front, the lid tabs press on the carrier's back: open the lid, slide the pair out
// on its wire loop and pull the S3 off (bench, flashing, swap) without touching a solder joint. Below D ~ 30 it slides in grooves cut into the side walls instead (they run twice the
// board length so it can be dropped in through the open back above its place and slid down).
d1 = [25.6, 34.6];            // board width (x), length (z): LOLIN S3 Mini, 25.4 x 34.5 measured (wemos.cc: 25.4 x 34.3) + margin
// From the LOLIN drawing (references/s3_mini_dimensions.png): pin pads 1.27 from the edge (rings reach ~0.4 from it),
// from 7.9 to 27.5 above the USB end (pin centres 8.8 to 26.6: the carrier is cut 1.2 mm below its first row); buttons 0 / RST 1-3.9 above it (0 sticks out of the edge); rounded top corners.
d1_btn = 4.5;                 // no strip or rib below this (buttons)
d1_boot_out = 1.3;            // BOOT (0) button sticks out of the high-x (right) edge by 1.3 (measured): it would
                              // press into the wall, so a window goes through the wall there (gap between the middle
                              // columns, hardly visible; BOOT reachable with a paper clip)
d1_btn_y = 3;                 // button body depth in front of the PCB (the window reaches this far forward)
d1_notch = [2, 7];            // edge stepped in on the RST side (low x seen from the front) at the USB end: depth, height
d1_pcb_t = 1.0;               // measured (groove is d1_pcb_t + 0.3 wide)
d1_groove_clr = 0.15;         // side clearance in the grooves
d1_end = 2.5;                 // height of the ribs / lid tabs, in the two pad-free bands (d1_btn.. and 6.5 below the top)
d1_rib = 0.8;                 // how far the ribs and tabs reach over the board faces (pad edges ~1.4 from the board edge)
d1_standoff = 6;              // gap between lid and board back (carrier back when socketed): wires soldered on it
s3_socket = true;             // S3 on female headers on a carrier board (false: wires soldered on the S3 itself)
s3_carrier_t = 1.5;           // carrier perfboard thickness (measured) (pads only, no strips: the S3's pins sit in two double rows); layout renders/tars4_board_s3.svg
s3_sock_h = 8.4;              // female header body height (2 x 8, measured)
s3_pin_base = 2.4;            // plastic spacer of the male headers soldered on the S3 (measured; pins 3.1 / 5.6)
s3_sock = [5.08, 20.32];      // each 2 x 8 female header: width (x, from the board edge), length (z): two rows on each side
d1_usb_cut = [11.6, 9];       // floor opening for the USB-C plug overmold (x, y); wider would cut into the foot recesses
d1_usb_h = 3.2;               // USB-C receptacle height in front of the PCB (centres the opening on the plug)
// Optional text engraved in the floor next to the controller's USB-C. Was "SW OFF" while its VBUS was wired straight to
// VSYS; the VBUS pin now only sees its own USB-C (3V3 comes from the TPS63020), so flashing works with the switch on or off.
usb_mark = "";
usb_mark_h = 3.5;             // letter height
usb_mark_y = 12.5;            // centre of the text (y), between the front foot recesses and the USB-C opening
// Spare breakout slot on the inner front wall just above the splint (like the amplifier in the other middle column).
// Free (the 3.3 V buck-boost ended up flat in the power leg, see `buck`). Kept empty for later.
bb = [13.4, 18, 1.6];         // slot size: width (x), length (z), PCB thickness
bb_col = 1;

/* [Split for printing] */
// Each column and lid is printed in two halves (Ender 3: Orca bed 220 x 220). The seam sits on an existing line:
// middle columns on the top edge of the lower black panel (hidden by the insert), legs on the 0.64 H plate line.
// A printed U "splint" glued inside joins the halves.
seam_z = [H * 0.64, bottom_panel_z[1], bottom_panel_z[1], H * 0.64];
splint_h = 20;
splint_t = 1.6;                // 4 lines at 0.4 (was 1.2: too flimsy)
splint_clr = 0.15;

/* [Battery bay (legs)] */
// One Li-ion cell standing in each leg, held by two cradles and the lid. The two cells are wired in parallel
// (1S2P) behind ONE protected TP4056 in the power leg. Only the charge port (a micro-USB breakout standing on the
// outer side wall, plug from behind through the heel of the lid) and the slide switch stay in the foot; the TP4056 lies flat higher up, above
// the buck-boost. The pack wires (B+, B-) of the other cell cross all three pivot tubes.
battery = true;
power_col = 0;                // leg carrying the charger, the charge port and the switch (0 = left leg)
bat = [18.6, 65];             // cell diameter, length: 18650 = [18.6, 65] (default), 18500 = [18.5, 50]
bat_clr = 0.6;
charger = [26.3, 17.15, 0.9]; // TP4056 (protected) lying flat: width (x), depth (y), PCB thickness. 28.7 as bought: its unused
                              // micro-USB desoldered and the two panel-break nubs filed off (26.3). Grooves only if wider
                              // than the leg interior (charger_groove)
charger_h = 6;                // above its PCB: C9 (Ø5.15) and D3 lying flat on the IN end (its micro-USB is desoldered)
charger_lip = 0.5;            // lower ledges under the board's side edges (no upper lip): end pads centred 1.43 from the edge
// Charge port at the heel (PLAT-MECH-CHARGEPORT-001): the breakout stands against the outer side wall (x = 0), solder
// side towards it, receptacle at its back end facing the lid; its back edge rests against the lid (pull-out stop), a
// front stop in two tabs takes the plug's push; the receptacle goes through a notch at the bottom of the lid.
usbb = [14.3, 16, 1.5];       // micro-USB breakout: width (z), length (y), PCB (measured)
usbb_rec = [7.85, 2.47];      // receptacle shell: width (z, centred on the PCB width), height above the PCB (x) (measured)
usbb_out = 1.1;               // receptacle mouth past the PCB's back edge (measured ~1.1; mouth <= 1 mm inside the back face)
usbb_z0 = wall + 1.5;         // bottom edge, above the rear foot pad (1.2)
foot_room = 22;               // under the bottom contact shelf: switch (lever tip to pins 18.9) + its wires, breakout
// Bare cells: spring contact plates at both ends (never solder on the cell). Each plate lies on / under a shelf,
// slid in from the back, solder tab first (towards the front, over the wire slot: wire soldered on the tab beforehand
// and fed through the slot), held by a dab of glue; the spring pushes them onto the shelves.
contact = [13, 18, 1.2];      // contact plate width (x), length (y), thickness
contact_bump = 0.6;           // + plate: bump towards the cell (1.8 overall)
spring_work = 4;              // - plate spring length with the cell in (free length 10.7, solid 2.85 measured)
cradle_groove = [3, 6];       // vertical wire groove in each cell cradle, from the cell towards the front wall (width, depth)
shelf_t = 2.5;                // contact shelves span the whole interior: front wall, both side walls and the lid screw posts
// wire passage through each shelf against the front wall: wire_slot, derived below (as large as the screw posts and
// the contact plates allow)
shelf_z = foot_room + shelf_t;                      // top of the bottom shelf, above the switch and the charge port
bat_z0 = shelf_z + contact[2] + spring_work;         // bottom of the cell
bat_top_shelf_z = bat_z0 + bat[1] + contact_bump + contact[2]; // underside of the top shelf
// Polyfuses F1 / F2 (radial PPTC, XF160): each stands flat against the inner front wall in front of its cell, between
// the two cradles, as high as the top cradle allows (short B+ loop from the + tab), leads up; two side ribs and a bottom
// stop, a dab of glue. Too wide (15) for the top shelf between the lid screw posts.
fuse = [15, 16, 2.5];         // body width (x), height (z), thickness (y), measured (XF160: 1.6 A hold)

/* [Sensors (left middle column, I2C + I2S)] */
// ADXL345 accelerometer on the inner front wall of the controller's column, I2C chained S3 -> ADXL345 -> middle tube
// -> right middle board -> right tube -> DS3231 RTC + BME280 in the right leg (the empty one). Headers removed, wires
// soldered on the pads. Each board sits on a bottom stop just above a lid screw row.
// INMP441 I2S microphone above the accelerometer (narrow enough to pass between the screw posts). Top-port MEMS (sound hole in the middle of its metal can): chip side against the wall, the can facing a
// 1 mm hole drilled in the vertical decor groove (invisible). On its own I2S1 (SCK, WS, SD: three local wires).
sensors = true;
sensor_col = 1;
rtc_col = 3;                  // DS3231 in the right leg, above the top cell shelf (SQW not wired: the S3 timer wakes it)
rtc = [22.18, 38.33, 12.6];   // DS3231 ZS-042 board, measured: width, length (header pins cut or bent towards the lid), overall thickness incl. CR2032
acc = [15.35, 20.34, 1.6];    // ADXL345 GY-291 board: width, length (measured), PCB thickness (solder side to the wall)
mic = [10, 10, 2.6];          // INMP441 board: width, length (measured 10 x 10), PCB + MEMS can thickness
mic_port_dz = 0;              // sound hole height from the board centre (centred on the can, can centred on the board)
mic_hole_d = 1;               // hole through the front wall

/* [Motion sensor (right middle column)] */
// AM312 mini PIR (2.7-12 V, ~15 uA, push-pull output, ~2 s hold) at the top of the right middle column, in the 14 mm
// band between the screen frame and the top lid screw (the left middle column with the controller is crowded). At
// that height the middle tube ends on the left (collar + tube end, then its wires turn down along the left wall) and
// the right tube's glued boss sits on the right: the sensor is centred between the two (pir_x), slightly right of the
// column axis. The bare detector (TO-5 can) is soldered on the edge of a small breakout standing perpendicular to the
// front wall, flush with one end of that edge (so the dome is off the board's centre). The white Fresnel cap goes in
// from the inside, dome first, until the dome meets the edge of the wall hole (pir_hole, over the vertical decor
// groove): its top then sits flush with the front face (trial plate pir_test, 2026-10-24). A ring on the inner wall
// centres the rim (glue it there); the can then slides into the skirt from the inside until its flange meets the
// skirt. 3V3 / GND from P2, OUT -> R17 1 k (on P2) -> PIR through the middle tube ->
// GPIO3 (EXT1 ANY_HIGH wake with the ADXL345 INT1 and USB_DET).
pir = true;
pir_col = 2;
pir_z = undef;                // sensor axis: undef = top (centred between the screen frame and the top lid screw, ~233);
                              // or a height, e.g. 117 (between the two middle lid screw rows, centred)
pir_cap_d = 10.50;            // Fresnel cap skirt diameter
pir_cap_skirt = 3.50;         // skirt length, from the cap base to the rim
pir_cap_rim_d = 12;           // rim = dome base diameter (centred by the ring on the inner wall)
pir_cap_rim_t = 0.5;          // rim thickness
pir_dome_h = 5.20;            // dome height above the rim
pir_dome_top_d = 7.15;        // the dome narrows to a flattened top of that diameter
pir_can_d = 8.15;             // detector can diameter
pir_can_h = 4.27;             // detector height, flange included
pir_can_fl = 0.6;             // flange at the can base (the cap base rests on it)
pir_pcb = [10.25, 8.10, 1.15]; // breakout: edge along the detector base, depth behind it, thickness
pir_pcb_a = 90;               // front view: direction the breakout's edge runs from its flush end (0 = right, 90 = up,
                              // 180 = left, 270 = down)
pir_pcb_dn = 1.85;            // board mid-plane off the detector axis, to the left of that direction (straight pins
                              // on the top face, ~1.3 from the axis: estimated from a photo, MEASURE)
pir_hole = 11.5;              // front wall hole, cap glued from the inside: the dome stops on its edge, top flush with
                              // the face (as drawn; printed 10.8 on the trial plate, dome flush)
pir_test_holes = [10.5, 11, 11.5]; // part pir_test: wall holes for the cap glued from the inside (dome stopped by the hole edge);
                              // printed 10.3 (outside hole, 10.8 drawn) / 10.0 / 10.5 / 10.8: holes come out ~0.6 smaller

/* [Buck-boost 3.3 V (power leg)] */
// TPS63020 buck-boost module feeding the S3 Mini's 3V3 pin directly (its own LDO only runs on USB): 3.3 V whatever the
// cell voltage, ~90 % efficient. Lying flat in the power leg between the microSD reader and the splint, long side
// across (it just fits between the side walls), components up, wires along the front wall in front of it. EN tied to
// VIN, PS/SYNC to GND (power save). Same groove mount as the microSD reader.
buck = true;
bk = [26.7, 17.7, 1.6];       // board width (x), depth (y), PCB thickness (measured)
bk_h = 4;                     // components above the PCB (inductor): MEASURE
bk_lip = 0.9;                 // lower ledges under the board's side edges (no upper lip over its pads): corner pad pairs at
                              // 1.3 / 4 from the edge, only the inner ones wired (the outer ones stay bare over the ledge)
bk_clr = 0.4;                 // side play in its slot (cut into the walls: 26.7 in a 27.2 interior)
bk_gap = 3;                   // clearance between the microSD socket top and the bottom of the buck-boost grooves

/* [Weather sensor (right leg)] */
// BME280 (purple GY-BME280, 3.3 V, no regulator: check) on the I2C bus (0x76 / 0x77, beside 0x53 / 0x57 / 0x68) in the
// right leg, the coolest place (far from the S3, the TPS63020 and the charger), in the band above the third lid screw
// row: board in a slot on the inner front wall, sensor side against the wall, its can facing a vent hole. SDA / SCL /
// 3V3 / GND come down the right tube from P2, next to the RTC's. bme = false leaves the vent out.
bme = true;
bme_b = [12, 15.6, 2.6];      // board width (x), length (z), PCB + sensor can, measured (header removed, wires on the pads)
bme_port_dz = 0;              // sensor can centre above the board centre: MEASURE
bme_hole_d = 1.5;             // vent hole through the front wall

/* [Power-path perfboard (power leg)] */
// Q1 (AO3401A), D1 (1N5822), R1, the dividers R2 / R3 and R15 / R16 and the star ground on a piece of perfboard lying
// flat in the power leg just above the splint (same groove mount as the microSD reader), parts up, against the lid
// side: the wires run up and down in front of it. Short runs to the TP4056 / buck-boost below and the left tube above.
pp = true;
pp_b = [26.6, 20, 1.5];       // board width (x), depth (y), thickness (1.5 measured): 10 x 8 holes (renders/tars4_board_power.svg)
pp_parts = 6;                 // tallest part above the board (1N5822 lying flat, ~5.3): MEASURE
pp_lip = 0.6;                 // grooves reach over the board's side edges (pads start ~1 mm in; R2 lies along column J)

/* [Distribution boards (middle columns)] */
// A piece of stripboard (2.54 mm pitch, strips horizontal) standing below each screen, parallel to the front face:
// every net that splits gets one strip (P1: GND ×2, 3V3, BL_EN, DC, RST, MOSI, with R4, C2/C3; no battery voltage
// on it), the single-destination signals go direct. P2 (right middle): 3V3, GND,
// SDA, SCL (on to the right leg), AMP_SD (R10 1 k in series, R18 10 k to GND), PIR (R17 1 k in series); BL_EN goes
// straight to screen 2. Same slot in both columns, so the middle lid (common to both)
// holds both. Slid in from the back with the wires soldered: front stops on the side walls (45 deg slopes, no
// support), centring strips, two tabs on the lid behind it.
hub = true;
hub_b = [24, 32, 1.6];        // board width (x), height (z), thickness: 9 x 12 holes, strips across (renders/tars4_board_p1.svg, _p2.svg), MEASURE (keep ~1.5 mm free of holes at the side edges)
hub_y = 12;                   // front face of the board (depth from the front face): wires in front, solder side and connectors towards the lid
hub_lip = 1.5;                // front stops / lid tabs reach over the board's side edges
hub_tab = 3;                  // lid tab height (z)

/* [microSD reader (power leg)] */
// 3.3 V-only microSD breakout (no regulator, no level shifter) lying flat in the power leg, above the top cell shelf,
// socket mouth facing the lid: the card goes in through a slot in the leg lid (push-push, fingernail or pen tip), no
// need to open TARS. The board slides in from the back into two side grooves; their front ends stop it (the socket
// pushes it forward on insertion), the lid stops it backwards. SDMMC 1-bit (CLK, CMD, D0) + 3V3 + GND through the left tube.
sd_reader = true;
sd_col = power_col;
sd = [18.2, 18.2, 1.5];       // board width (x), length (y, socket edge towards the lid), PCB thickness
sd_sock = [14, 11.5, 2];      // socket width (x), length (y), height above the PCB
sd_sock_dx = 0;               // socket centre from the board centre (x)
sd_sock_over = 2.8;           // socket mouth beyond the board's back edge (y): 21 overall - 18.2
sd_card_out = 6.9;            // latched card beyond the socket mouth (y)
sd_fwd = 2;                   // board moved forward from the lid (sinks the card; costs wire room in front of the board)
sd_lip = 1.0;                 // grooves reach over the board's side edges (keep clear of its components and GND pad)
sd_slot = [12.5, 2.2];        // card slot through the lid (x, z): microSD is 11 x 1
sd_dz = 10;                   // underside of the board above the lid screw posts over the top cell shelf

/* [Sound] */
// Speaker facing the front right behind the lower black panel of one middle column, just under the splint: TARS talks
// through slots in that panel's black plug. Its membrane is flush with its face and its long edges have no rim: it bears
// on two pads under its short-end tabs, sits between side rails on a stop notched for its middle nub, and is glued
// (hot glue, PLAT-MECH-SPEAKER-001). MAX98357A I2S amplifier in a slot on the inner front wall above the splint.
sound = true;
speaker_col = 2;              // right middle column (column 1 carries "TARS")
spk = [13.8, 7.15, 25.27];    // 4 ohm 2 W speaker: width (x), thickness (y), height (z), measured 2026-10-29
spk_pad = 1.5;                // pads under the short-end tabs (z): the membrane starts beyond them (2 mm rim)
spk_nub = [3.3, 2];           // notch for the nub in the middle of the short edges (2.9 wide): width (x), depth (z)
spk_front_y = wall + splint_t + splint_clr;                       // speaker face: ~1 mm behind the plug's ledge
spk_z0 = seam_z[1] - splint_h / 2 - 1 - spk[2];                   // just under the splint (it hides the panel's top)
grille_slot = [1.2, 3];       // slot height, pitch (in the black plug)
amp = [19.4, 18, 1.6];        // MAX98357A breakout: width (x), length (z), PCB thickness
amp_z0 = seam_z[1] + splint_h / 2 + 0.5;                           // just above the splint, below the lid screw row

/* [Switch and feet] */
// Slide switch in the power leg floor (next to the charge port), lever pointing down into a floor slot and recessed:
// nothing sticks out under TARS, it is flipped with a pen tip. Body glued in a low frame on a raised pad.
switch_on = true;
sw_body = [12.95, 6.9];       // mini slide switch body (x, y), measured
sw_lever_h = 5.15;            // lever height out of the body, measured
sw_h = 18.39;                 // lever tip to pin tips, measured
sw_lever = [4, 4];            // lever cross-section (x, y): 3.88 measured, 4 to slide freely (tried in print)
sw_travel = 6;                // lever travel along x, measured
sw_recess = 0.5;              // lever tip above the underside of the floor
sw_window = [sw_lever[0] + sw_travel + 0.6, sw_lever[1] + 0.6]; // slot: lever + travel (room for the pen tip beside it)
sw_pad_h = sw_recess + sw_lever_h - wall;                       // pad under the body (lever face above the floor)
sw_y = D - wall - 8;          // switch centre (y), near the back of the floor
// Recesses under every column for stick-on rubber feet (e.g. 3M Bumpon 8 mm).
feet = true;
foot_d = 8.4;
foot_h = 0.8;
foot_inset = 5;               // foot centre from the column edges
// Stability estimate (echoed): PLA density, cell mass
pla_density = 1.24e-3;        // g / mm3
cell_mass = 46;               // g per 18650

/* [Pivots] */
// Film movement diagrams: two-legged walk = "shoulder" axis near the top (crutch walk / wheel use a centre axis,
// but a joint cannot have both, so only the top one is kept). One brass tube per joint, hollow: the wires run
// through it (single brain + 1S2P pack + microSD: 13 / 19 / 6 wires from left to right, silicone wire, power in 26 AWG, signals and screen / sensor supplies in 30 AWG: ~37 / 38 / 14 % fill of the 7 mm bore, see tools/tube_section.py).
tube_od = 7.93;               // brass tube 8 / 7 mm (0.5 wall), 7.93 measured
tube_glue_clr = 0.07;         // fixed side (tube glued into the left-hand column of the joint): 8.00 teardrop holds (tube_test3)
tube_run_clr = 0.12;          // turning side: 8.05 teardrop turns with micro play (tube_test3)
pivot_boss_d = 14;
pivot_z = [H - wall - pivot_boss_d / 2 - 1]; // top pivot, as high as the bosses allow (clears the screen)
pivot_boss_l = 5;             // boss depth inside the column (bearing / glue length)
pivot_ring_d = 16;            // bearing ring on the turning side, thickness = gap
collar = [13, 2];             // retaining collar glued on the tube inside the turning column (OD, thickness; 2 leaves room for the motion sensor)
tube_over = 0.5;              // tube end past the collar
detent_r = 6.5;
detent_n = 24;
detent_bump_d = 1.6;
detent_bump_h = 0.5;
leg_angle = [0, 0];           // assembly preview: swing of the left / right leg around the top pivot (degrees)

/* [Hardware] */
rib = 1.6;                    // board slot rails and stops (charge port, amplifier, sensors, spare): 4 lines at 0.4
pcb_gap = 1.2;                // boards whose solder side faces the wall stand off it on two edge strips (cut pins, pads)
wire_room = 5;                // free depth wanted behind a board for the wires soldered on it
stack_gap = 4;                // between two flat boards: components / wires of the lower one, solder tails of the upper

/* [Connectors (demountable wiring)] */
// Every module plugs into the harness, so each one is tested on the bench first and fitted later without
// re-soldering. The harness itself (P1, P2, the S3's carrier, the power-path board, the cell plates, the tube
// bundles) is soldered once. 2.54 Dupont crimp housings go straight onto the modules' own header pins; a short
// pigtail + an inline Dupont pair where a header has no room (flat boards, the microphone, the AM312); JST-XH (3 A)
// inline pairs, crimped here, on the power block's wires (X10 J1 + SW1 in one 4-way, X12 / X16 left / right cell,
// X13, X14; no X11).
// Boxes below are the mated housings + the wire bend behind them
// (drawn in the side sections, checked against the walls, posts, boards and each other). Sizes are typical: MEASURE.
// Keying (Dupont housings are not polarised): a module pin left unused is pulled and its housing cavity plugged; inline
// pairs get one empty position (female side, on the powered harness, plugged; no pin there on the male side); the
// screens (all 8 pins used) get a right-angle header and a 1 mm rib glued on the housing's lid-side face, so that
// reversed it cannot slide along the screen's back. The power block's connectors are parked in the free cavity
// above the TP4056, visible from the back.
plugs = true;
dp_t = 2.6;                   // Dupont housing thickness
dp_on = 16.5;                 // header plastic + mated female housing, from the board face
dp_inline = 26;               // mated inline Dupont pair (female + male housings)
xh_inline = [5.8, 20];        // JST-XH 2.5 inline pair: thickness, mated length (width 2.5 n + 2.4)
bend = 4;                     // wire bend room behind a housing (and at both ends of an inline pair)
key_rib = 1;                  // rib on the screen housings (keying)
scr_hdr_dz = 1.4;             // screen header pin row below the board's top edge (measured)
scr_hdr_back = 6.9;           // right-angle header + mated female housings, from the screen PCB's back (dry fit)
// screen headers: right-angle, on the board's back, pins pointing down; the housing lies flat on the back
scr_hdr_ra = true;
rtc_hdr_y = 4;                // DS3231 (ZS-042) right-angle header: pin row depth in front of the board's back face (measured)
// flat boards without an upper lip (TP4056, TPS63020): a lid tab presses on the middle of their back edge
hold_tab = [14, 1, 2];        // width (x), reach over the board (y), height (z)
c7 = [8, 12];                 // C7 470 µF lying across behind the amplifier, leads on its VIN / GND pins (Ø, length): MEASURE

/* [Wire ties and vents] */
// Tie anchors: printed bridges on the side walls, a cable tie through each, >= 25 mm from the tube ends (the bundles
// must twist freely there), never at a screw post or a splint. [column, side (0 left / 1 right), z]; y = tie_y.
ties = true;
tie = [2.8, 6, 5];            // anchor reach from the wall (x), depth (y), height (z); tunnel 1.4 x 2.8 for a 2.5 tie
tie_y = 17;                   // anchor front (y): behind the boards on the front wall, in front of the lid tabs
TIES = [[0, 1, 112], [0, 1, 179], [0, 1, 218], [1, 0, 50], [1, 1, 50], [1, 0, 80], [1, 1, 80], [1, 0, 128], [1, 1, 128],
        [2, 0, 106], [2, 1, 106], [2, 0, 178], [2, 1, 178], [3, 0, 111], [3, 0, 179]];
// Vent slots through the leg lids (both: the top half is one part): behind the TP4056 / the parked connectors, and at
// the top (warm air out)
vents = true;
vent = [16, 1.5, 3];          // slot width (x), height (z), pitch
vent_rows = [[141, 3], [217, 5]]; // [lowest slot z, count]

// Lid screws: M2.5 thin-head machine screws (6 or 8 long) threaded straight into the printed bosses (no inserts).
pilot_d = 2.1;                // pilot hole: the screw cuts its own thread in PLA (3.5 = later upgrade to M2.5 heat-set inserts)
pilot_depth = 9;              // from the lid face: covers M2.5 x 8 (6.4 mm engaged) with room at the bottom
screw_clear = 2.9;            // lid clearance hole for M2.5
lid_boss_d = 7;

$fn = 48;
eps = 0.01;

// ---------- screen selection ----------
function kv(pairs, key) = [for (p = pairs) if (p[0] == key) p[1]][0];
SCR = [for (s = SCREENS) if (s[0] == screen) s[1]][0];
assert(SCR != undef, str("unknown screen: ", screen));
scr_pcb = kv(SCR, "module");
scr_t = kv(SCR, "thickness");
scr_win = kv(SCR, "active");
scr_win_r = kv(SCR, "active_r");
scr_win_dz = kv(SCR, "active_dz");
scr_win_dx = kv(SCR, "active_dx");
scr_open = kv(SCR, "glass_panel");
scr_standoffs = kv(SCR, "standoffs");
scr_z = (screen_panel_z[0] + screen_panel_z[1]) / 2 - scr_win_dz;
scr_x = col_w / 2 - scr_win_dx; // visible area centred on the column
// screen panel hole: its top edge stays clear of the screen's top standoffs (they need the wall behind them)
scr_top = scr_standoffs == undef ? screen_panel_z[1] : min(screen_panel_z[1], scr_z + scr_standoffs[1] / 2 - 1.8 - 0.4);
panel_holes = [[screen_panel_z[0], scr_top], bottom_panel_z];

// ---------- derived positions (column-local) ----------
inner = [wall, col_w - wall];                         // interior x range
lid_y = D - wall;                                     // inner face of the lid
usbb_x0 = wall + pcb_gap;                             // solder side of the PCB (cut pins / solder tails between it and the side wall)
usbb_y1 = lid_y - 0.2;                                // back edge of the PCB, against the lid
usbb_y0 = usbb_y1 - usbb[1];                          // front edge (pads: the wires leave forwards)
usbb_zc = usbb_z0 + usbb[0] / 2;                      // receptacle centre height
usbb_xc = usbb_x0 + usbb[2] + usbb_rec[1] / 2;        // receptacle centre (x)
bx = [wall + lid_boss_d / 2 - 0.5, col_w - wall - lid_boss_d / 2 + 0.5]; // bosses overlap the walls by 0.5 (no tangent contact)
// top screw centred (the top pivot bosses sit in the corners), the others in corner pairs, placed so that each
// half-lid has at least 3 screws and nothing collides (D1 mini, charger, battery, pivots, splint)
bat_y = lid_y - (bat[0] + bat_clr) / 2 - 0.3;          // cell axis, close to the lid
// wire passage through each contact shelf, centred against the front wall (x, y): 0.6 mm clear of the screw posts that
// fill the corners at these heights, 1 mm of shelf left in front of the contact plates
wire_slot = [col_w - 2 * (bx[0] + lid_boss_d / 2 + 0.6), bat_y - contact[1] / 2 - 1 - wall];
leg_rows = [shelf_z + 1.2, bat_top_shelf_z + 4 + lid_boss_d / 2 - 1, H * 0.75, H * 0.85]; // top shelf 4 thick into row 1
mid_rows = [wall + lid_boss_d / 2 - 0.5, H * 0.4, H * 0.548];  // none behind the lower panel hole; row 2 low enough for the RTC
// leg / middle lid splits, both away from the column seams so the bottom lid half is screwed on both sides of the
// seam and bridges it at the back (leg: rows 34 / 112 / 186 below the split, 211 + top above; middle: 4.6 / 99 | 136 + top)
lid_seam_z = [(H * 0.75 + H * 0.85) / 2, H * 0.46];
function lid_bosses(mid) = concat([[col_w / 2, H - wall - lid_boss_d / 2 + 0.5]], [for (x = bx, z = mid ? mid_rows : leg_rows) [x, z]]);
d1_x = col_w / 2;
d1_z0 = mid_rows[0] + lid_boss_d / 2;                 // bottom edge of the controller board, standing on the bottom posts
d1_holds = [d1_z0 + d1_btn, d1_z0 + d1[1] - 6.5];     // front ribs / lid tabs: just above the buttons, below the top corners
acc_z0 = mid_rows[1] + lid_boss_d / 2 + 0.5;          // sensor boards just above a screw row
up_z0 = mid_rows[2] + lid_boss_d / 2 + 0.5;          // band above the upper middle screw row, below the screen frame
mic_z0 = up_z0 - rib - 0.3 - 0.3 - mic[1];            // between the upper screw posts, under the distribution board
hub_z0 = up_z0;                                        // distribution boards P1 / P2: below the screens
rtc_z0 = leg_rows[1] + lid_boss_d / 2 + 0.5;          // DS3231 (right leg): above the top cell shelf, under the splint
pir_cap_y = pir_cap_rim_t + pir_dome_h;               // cap base (rim back face) behind the front face: dome top flush
pir_sleeve_d = pir_cap_rim_d + 0.4 + 2 * 1.2;         // centring ring outer diameter (3 lines at 0.4)
pir_sleeve = pir_cap_y + 1 - wall;                     // ring on the inner front wall, 1 mm past the rim
pir_pcb_y0 = pir_cap_y + pir_cap_skirt + pir_can_fl;   // breakout front edge (just behind the flange)
// breakout front-view footprint around the detector axis [x0, z0, x1, z1]: edge from -can_d / 2 (flush end) to
// pcb[0] - can_d / 2 along pir_pcb_a, thickness across (shifted by pir_pcb_dn)
pir_pcb_fp = let(u = [cos(pir_pcb_a), sin(pir_pcb_a)], n = [-u[1], u[0]],
                 c = [for (s = [-pir_can_d / 2, pir_pcb[0] - pir_can_d / 2], t = [-pir_pcb[2] / 2, pir_pcb[2] / 2]) s * u + (t + pir_pcb_dn) * n])
    [min([for (p = c) p[0]]), min([for (p = c) p[1]]), max([for (p = c) p[0]]), max([for (p = c) p[1]])];
// dome = half ellipse (rim_d / 2, pir_dome_b) cut at pir_dome_h, where it is pir_dome_top_d wide
pir_dome_b = pir_dome_h / sqrt(1 - pow(pir_dome_top_d / pir_cap_rim_d, 2));
function pir_dome_z(d) = d <= pir_dome_top_d ? pir_dome_h : pir_dome_b * sqrt(1 - pow(min(d, pir_cap_rim_d) / pir_cap_rim_d, 2));
scr_frame_top = scr_z + scr_pcb[1] / 2 + scr_clr + scr_frame_w;
top_boss_z0 = H - wall - lid_boss_d + 0.5;           // underside of the top (centred) lid screw post
pir_top = pir_z == undef;
pir_zc = pir_top ? (scr_frame_top + top_boss_z0) / 2 - (min(-pir_cap_d / 2, pir_pcb_fp[1]) + max(pir_cap_d / 2, pir_pcb_fp[3])) / 2 : pir_z; // cap + breakout centred in the band
tube_end_x = wall + pivot_boss_l + collar[1] + tube_over;   // turning column: end of the tube coming from the left
pir_x = pir_top ? (tube_end_x + col_w - wall - pivot_boss_l) / 2 : col_w / 2; // top: between that tube end and the right boss
bme_col = 3;
bme_z0 = leg_rows[2] + lid_boss_d / 2 - 0.3;          // BME280 (right leg): on the third leg screw row (the 12 wide board clears the posts in x; its stops merge into them)
carrier_back_y = lid_y - d1_standoff;                 // back face of the S3's carrier (wires soldered there)
d1_back_y = s3_socket ? carrier_back_y - s3_carrier_t - s3_sock_h - s3_pin_base : carrier_back_y; // back face of the S3
d1_hold_y = s3_socket ? carrier_back_y : d1_back_y;   // what the lid tabs press on
d1_lug_y = (s3_socket ? carrier_back_y - s3_carrier_t : d1_back_y - d1_pcb_t) - 0.5; // lug front (clear of the speaker next door)
sd_z0 = leg_rows[1] + lid_boss_d / 2 + sd_dz;        // underside of the microSD board
sd_y1 = lid_y - 0.3 - sd_sock_over - sd_fwd;          // back edge of the microSD board (socket mouth 0.3 + sd_fwd from the lid)
sd_y0 = sd_y1 - sd[1];                                // front edge (header / wire pads)
sd_card_z = sd_z0 + sd[2] + sd_sock[2] / 2;
bk_z0 = sd_z0 + sd[2] + sd_sock[2] + bk_gap + rib;    // underside of the buck-boost board, above the microSD socket
bk_y1 = lid_y - 0.3;                                  // back edge of the buck-boost board
charger_z0 = bk_z0 + bk[2] + bk_h + stack_gap + rib;  // TP4056 underside: flat above the buck-boost's components
charger_groove = max(0, (charger[0] + 0.3 - (col_w - 2 * wall)) / 2); // depth cut into each side wall for its edges
pp_z0 = seam_z[power_col] + splint_h / 2 + 0.5 + rib; // power-path perfboard underside: just above the splint
top_shelf_top = leg_rows[1] - lid_boss_d / 2 + 1;    // top face of the top contact shelf
fuse_z0 = bat_z0 + bat[1] - 9 - 0.5 - fuse[1];       // polyfuse bottom: just under the top cradle

// ---------- helpers ----------
module front_engrave(depth) { // 2D (x = local x, y = z) -> recess in the front face
    translate([0, depth, 0]) rotate([90, 0, 0]) linear_extrude(depth + eps) children();
}

module xcyl(x, z, d, h, dir = 1) { // cylinder along +x (dir = 1) or -x (dir = -1) from x, at y = D/2
    translate([x, D / 2, z]) rotate([0, dir * 90, 0]) cylinder(d = d, h = h);
}
// same, teardrop section with its point towards +y (up when printed front face down): no sagging bore ceiling
module xtear(x, z, d, h, dir = 1) {
    translate([x, D / 2, z]) rotate([0, dir * 90, 0]) linear_extrude(h) union() {
        circle(d = d);
        rotate(45) square(d / 2);
    }
}

// ---------- screen ----------
module win_profile(grow) {
    r = scr_win_r + grow;
    if (r > 0) offset(r = r) square([scr_win[0] - 2 * scr_win_r, scr_win[1] - 2 * scr_win_r], center = true);
    else square(scr_win, center = true);
}

module scr_window(bevel = 0, extra = 0) { // window through the front wall, optionally flared towards the front
    translate([scr_x + scr_win_dx, 0, scr_z + scr_win_dz]) hull() {
        translate([0, wall + eps, 0]) rotate([90, 0, 0]) linear_extrude(eps) win_profile(extra);
        rotate([90, 0, 0]) linear_extrude(eps) win_profile(extra + bevel);
    }
}

module scr_opening() { // glass_panel screens: opening the size of the panel, R3 corners
    ow = min(panel_w, scr_pcb[0] - 0.6);
    oh = screen_panel_z[1] - screen_panel_z[0];
    translate([scr_x, wall + eps, (screen_panel_z[0] + screen_panel_z[1]) / 2]) rotate([90, 0, 0])
        linear_extrude(wall + 2 * eps) offset(r = 3) square([ow - 6, oh - 6], center = true);
}

module scr_frame() { // the side walls act as frame where the module is as wide as the interior
    fh = scr_t + 0.6;
    translate([scr_x, wall - eps, scr_z]) {
        difference() {
            translate([-scr_pcb[0] / 2 - scr_clr - scr_frame_w, 0, -scr_pcb[1] / 2 - scr_clr - scr_frame_w])
                cube([scr_pcb[0] + 2 * (scr_clr + scr_frame_w), fh, scr_pcb[1] + 2 * (scr_clr + scr_frame_w)]);
            translate([-scr_pcb[0] / 2 - scr_clr, -eps, -scr_pcb[1] / 2 - scr_clr])
                cube([scr_pcb[0] + 2 * scr_clr, fh + 2 * eps, scr_pcb[1] + 2 * scr_clr]);
        }
        if (scr_standoffs != undef) let(st = scr_standoffs) for (i = [-1, 1], j = [-1, 1])
            translate([i * st[0] / 2, 0, j * st[1] / 2]) rotate([-90, 0, 0]) difference() {
                cylinder(d = 3.6, h = st[3] + eps);
                translate([0, 0, -eps]) cylinder(d = st[2], h = st[3] + 3 * eps);
            }
    }
}

// module wider than the interior: pocket cut into the side walls over the module height only
module scr_wall_pockets() {
    fh = scr_t + 0.6;
    for (e = [[scr_x - scr_pcb[0] / 2 - scr_clr, wall], [col_w - wall, scr_x + scr_pcb[0] / 2 + scr_clr]])
        if (e[1] > e[0]) translate([e[0], wall - eps, scr_z - scr_pcb[1] / 2 - scr_clr]) cube([e[1] - e[0] + eps, fh, scr_pcb[1] + 2 * scr_clr]);
}

// ---------- decor ----------
module mid_panels(depth = wall, c = 0) { // panel holes through the front wall (or the plugs, with clearance c)
    for (zz = scr_open ? [bottom_panel_z] : panel_holes)
        translate([col_w / 2 - panel_w / 2 + c, -eps, zz[0] + c]) cube([panel_w - 2 * c, depth + eps, zz[1] - zz[0] - 2 * c]);
}

// ledge behind the lower panel plug: bottom and sides, stopping below the splint; its inner edge is a 45 deg slope
module low_panel_ledge() {
    z0 = bottom_panel_z[0];
    z1 = min(bottom_panel_z[1], seam_z[1] - splint_h / 2 - 1);
    translate([0, wall - eps, 0]) difference() {
        translate([col_w / 2 - panel_w / 2 - ledge[0], 0, z0 - ledge[0]]) cube([panel_w + 2 * ledge[0], ledge[1], z1 - z0 + ledge[0]]);
        hull() for (k = [0, 1]) let(o = ledge_lip + k * (ledge[1] + eps))
            translate([col_w / 2 - panel_w / 2 + o, -eps + k * (ledge[1] + eps), z0 + o]) cube([panel_w - 2 * o, eps, z1]);
    }
}

braille_tars = [[2, 3, 4, 5], [1], [1, 2, 3, 5], [2, 3, 4]]; // T A R S
module tars_marking() {
    if (tars_text) front_engrave(engrave_d)
        translate([col_w / 4 + text_h / 2, text_z0]) rotate(90)
            resize([text_len, text_h]) text("TARS", font = text_font, valign = "baseline");
    if (braille) front_engrave(engrave_d)
        translate([3 * col_w / 4 - braille_pitch, text_z0 + braille_dot]) rotate(90)
            for (c = [0:3], n = braille_tars[c]) let(col = n > 3 ? 1 : 0, row = (n - 1) % 3)
                translate([c * braille_cell + col * braille_pitch, -row * braille_pitch]) circle(d = braille_dot);
}

module mid_lines_cut() {
    for (z = mid_lines) translate([-eps, -eps, z - line_w / 2]) cube([col_w + 2 * eps, line_d + eps, line_w]);
    // vertical line in the middle of the column, interrupted by the panels
    translate([-eps, -eps, scr_top - line_w / 2]) cube([col_w + 2 * eps, line_d + eps, line_w]);
    for (seg = [[-eps, bottom_panel_z[0]], [bottom_panel_z[1], screen_panel_z[0]], [scr_top, H + eps]])
        translate([col_w / 2 - line_w / 2, -eps, seg[0]]) cube([line_w, line_d + eps, seg[1] - seg[0]]);
}

module leg_lines_cut() { // front and both sides (the back is the lid)
    for (z = leg_lines) {
        translate([-eps, -eps, z - line_w / 2]) cube([col_w + 2 * eps, line_d + eps, line_w]);
        for (x = [-eps, col_w - line_d]) translate([x, -eps, z - line_w / 2]) cube([line_d + eps, D + 2 * eps, line_w]);
    }
    translate([col_w / 2 - line_w / 2, -eps, -eps]) cube([line_w, line_d + eps, H + 2 * eps]);
    for (x = [-eps, col_w - line_d]) translate([x, D / 2 - line_w / 2, -eps]) cube([line_d + eps, line_w, H + 2 * eps]);
}

// ---------- bed levelling test (print orientation, Ender 3 bed centred on the origin) ----------
// five single-layer 25 mm squares (corners + centre) and a slice of column 1's front, face down: groove, "TARS",
// braille and the column edges, to judge the first layer on the real facade (squish, elephant foot, engraving)
module test_level(sq = 25, layer = 0.2, reach = 85) {
    for (p = [[-reach, -reach], [reach, -reach], [-reach, reach], [reach, reach], [0, 0]])
        translate([p[0] - sq / 2, p[1] - sq / 2, 0]) cube([sq, sq, layer]);
    z0 = text_z0 - 4;
    z1 = text_z0 + text_len + 4;
    translate([sq / 2 + 8, (z0 + z1) / 2, 0]) rotate([90, 0, 0]) intersection() { // print z = model y
        column(1);
        translate([-eps, -eps, z0]) cube([col_w + 2 * eps, 2.4, z1 - z0]);
    }
}

// ---------- pivots ----------
// Joint k is between column k (fixed side: tube glued in its right wall) and column k+1 (turning side: left wall,
// bearing ring with detent bumps). Column k's right outer face carries the detent dimples.
// Each boss is filled down to the front wall: no overhang under it when the column prints front face down.
module pivot_boss(x0, z) {
    hull() {
        xcyl(x0, z, pivot_boss_d, pivot_boss_l + eps);
        translate([x0, wall - eps, z - pivot_boss_d / 2]) cube([pivot_boss_l + eps, eps, pivot_boss_d]);
    }
}

module pivot_add(i) {
    for (z = pivot_z) {
        if (i > 0) {
            pivot_boss(wall - eps, z);                                                // turning side boss
            xcyl(-gap, z, pivot_ring_d, gap + eps);                                   // bearing ring
            for (a = [0, 180]) translate([-gap, D / 2, z]) rotate([a, 0, 0]) translate([0, 0, detent_r])
                intersection() {
                    sphere(d = detent_bump_d, $fn = 16);
                    translate([-detent_bump_h, -detent_bump_d, -detent_bump_d]) cube([detent_bump_h + eps, 2 * detent_bump_d, 2 * detent_bump_d]);
                }
        }
        if (i < 3) pivot_boss(col_w - wall - pivot_boss_l, z);                        // fixed side boss
    }
}

module pivot_cut(i) {
    for (z = pivot_z) {
        if (i > 0) xtear(-gap - eps, z, tube_od + tube_run_clr, gap + wall + pivot_boss_l + 2 * eps);
        if (i < 3) {
            xtear(col_w + eps, z, tube_od + tube_glue_clr, wall + pivot_boss_l + 2 * eps, -1);
            for (k = [0:detent_n - 1]) translate([col_w, D / 2, z]) rotate([k * 360 / detent_n, 0, 0])
                translate([0, 0, detent_r]) sphere(d = detent_bump_d + 0.2, $fn = 16);
        }
    }
}

// ---------- column ----------
module column(i) {
    mid = col_mid[i];
    difference() {
        union() {
            difference() {
                cube([col_w, D, H]);
                translate([wall, wall, wall]) cube([col_w - 2 * wall, D, H - 2 * wall]);
            }
            for (p = lid_bosses(mid)) translate([p[0], wall - eps, p[1]]) rotate([-90, 0, 0]) cylinder(d = lid_boss_d, h = lid_y - wall + eps);
            pivot_add(i);
            if (mid) {
                intersection() { scr_frame(); cube([col_w, D, H]); } // never past the side faces
                low_panel_ledge();
                if (sound && i == speaker_col) sound_mount();
                if (i == bb_col) board_slot(bb, amp_z0, gap = pcb_gap);
                if (pir && i == pir_col) pir_mount();
                if (i == 1) d1_guides();
                if (hub) hub_mount();
                if (sensors && i == sensor_col) { board_slot(acc, acc_z0, bottom = true, gap = pcb_gap);
                    board_slot(mic, mic_z0, bottom = true, bottom_to = acc_z0 + acc[1] + 0.3 + rib); }
            }
            else {
                if (battery) battery_bay(i == power_col);
                if (switch_on && i == power_col) switch_frame();
                if (sd_reader && i == sd_col) sd_mount();
                if (buck && i == power_col) bk_mount();
                if (pp && i == power_col) flat_slot(pp_b, pp_z0, lid_y - 0.3 - pp_b[1], pp_lip);
                if (battery && i == power_col) { flat_slot(charger, charger_z0, lid_y - 0.3 - charger[1], charger_lip, top = false); usbb_frame(); }
                if (sensors && i == rtc_col) board_slot(rtc, rtc_z0, bottom = true, top_gap = plugs ? dp_w(6) + 1 : 0);
                if (bme && i == bme_col) board_slot(bme_b, bme_z0, bottom = true);
            }
            if (feet) for (p = foot_pos) foot_pad(p); // pad behind the recess
            if (ties) for (t = TIES) if (t[0] == i) tie_anchor(t[1], t[2]);
        }
        for (p = lid_bosses(mid)) translate([p[0], lid_y - pilot_depth, p[1]]) rotate([-90, 0, 0]) cylinder(d = pilot_d, h = pilot_depth + eps, $fn = 16);
        pivot_cut(i);
        if (feet) for (p = foot_pos) translate([p[0], p[1], -eps]) cylinder(d = foot_d, h = foot_h + eps);
        if (mid) {
            mid_lines_cut();
            mid_panels();
            if (scr_open) scr_opening(); else scr_window(extra = 0.3);
            if (i == 1) tars_marking();
            if (sensors && i == sensor_col) translate([col_w / 2, -eps, mic_z0 + mic[1] / 2 + mic_port_dz]) rotate([-90, 0, 0])
                cylinder(d = mic_hole_d, h = wall + 2 * eps, $fn = 16);
            if (pir && i == pir_col) translate([pir_x, -eps, pir_zc]) rotate([-90, 0, 0]) // motion sensor dome
                cylinder(d = pir_hole, h = wall + 2 * eps);
            d1_grooves();
            if (i == 1) d1_boot_window();
            scr_wall_pockets();
            // USB-C plug of the controller through the floor
            translate([d1_x - d1_usb_cut[0] / 2, d1_back_y - d1_pcb_t - d1_usb_h / 2 - d1_usb_cut[1] / 2, -eps])
                cube([d1_usb_cut[0], d1_usb_cut[1], wall + 2 * eps]);
            // optional text engraved under the floor, mirrored so that it reads correctly from below
            if (i == 1 && usb_mark != "") translate([d1_x, usb_mark_y, -eps]) mirror([1, 0, 0]) linear_extrude(engrave_d + eps)
                text(usb_mark, size = usb_mark_h, font = "DejaVu Sans:style=Bold", halign = "center", valign = "center");
        } else {
            leg_lines_cut();
            if (battery) pol_marks();
            if (battery && i == power_col && charger_groove > 0)   // TP4056 edge grooves, open at the back (slid in)
                translate([col_w / 2 - charger[0] / 2 - 0.15, lid_y - 0.3 - charger[1] - 0.2, charger_z0]) cube([charger[0] + 0.3, D, charger[2] + 0.3]);
            if (switch_on && i == power_col) translate([col_w / 2, sw_y, -eps]) sw_slot(wall + 2 * eps);
            if (bme && i == bme_col) translate([col_w / 2, -eps, bme_z0 + bme_b[1] / 2 + bme_port_dz]) rotate([-90, 0, 0])
                cylinder(d = bme_hole_d, h = wall + 2 * eps, $fn = 16);                       // weather sensor vent
        }
    }
}

// ---------- wire tie anchors ----------
// bridge on a side wall with a vertical tunnel (along y) for a cable tie; 45 deg slope under it (no overhang when
// the column prints front face down, the tunnel then prints as a vertical hole)
module tie_anchor(side, z) {
    translate([side * col_w, 0, 0]) mirror([side, 0, 0]) difference() {
        translate([0, 0, z - tie[2] / 2]) linear_extrude(tie[2])
            polygon([[wall - eps, tie_y - tie[0]], [wall + tie[0], tie_y], [wall + tie[0], tie_y + tie[1]], [wall - eps, tie_y + tie[1]]]);
        translate([wall - 2 * eps, tie_y - tie[0] - eps, z - 1.4]) cube([1.4 + 2 * eps, tie[1] + tie[0] + 2 * eps, 2.8]);
    }
}
function tie_box(t) = let(x0 = t[1] == 0 ? wall : col_w - wall - tie[0])
    ["attache de toron", [x0, tie_y - tie[0], t[2] - tie[2] / 2], [x0 + tie[0], tie_y + tie[1], t[2] + tie[2] / 2]];

// ---------- switch and feet ----------
foot_pos = [for (x = [foot_inset, col_w - foot_inset], y = [foot_inset, D - foot_inset]) [x, y]];

// pad behind a foot recess, clear of the outer faces; teardrop towards the front where it does not touch the front wall
// (no overhang when the column prints front face down)
module foot_pad(p) {
    r = (foot_d + 1.2) / 2;
    intersection() {
        translate([p[0], p[1], wall - eps]) hull() {
            cylinder(r = r, h = 1.2);
            if (p[1] - r > wall) translate([0, max(wall - p[1], -r * sqrt(2)), 0]) cylinder(d = 0.1, h = 1.2, $fn = 4);
        }
        cube([col_w, lid_y - 0.3, H]); // clear of the lid (rear pads)
    }
}

// raised pad + low frame around the body (glue it in), lever slot through both; the front of pad and frame is one
// 45 deg slope (no overhang when printed front face down)
module switch_frame() {
    fx = sw_body[0] + 2.4;
    fy = sw_body[1] + 2.4;
    translate([col_w / 2, sw_y, wall - eps]) difference() {
        union() {
            hull() {
                translate([-fx / 2, -fy / 2 - sw_pad_h, 0]) cube([fx, fy + sw_pad_h, eps]);
                translate([-fx / 2, -fy / 2, sw_pad_h]) cube([fx, fy, eps]);
            }
            hull() { // under the frame's front wall, up to the top of the frame (1.0 = wall left by the body pocket)
                translate([-fx / 2, -fy / 2 - sw_pad_h - 2, 0]) cube([fx, sw_pad_h + 3, eps]);
                translate([-fx / 2, -fy / 2, sw_pad_h + 2 - eps]) cube([fx, 1, eps]);
            }
            translate([0, 0, sw_pad_h]) difference() { // front and sides only: a back wall would bridge the pocket
                translate([-fx / 2, -fy / 2, 0]) cube([fx, fy, 2]);
                translate([-sw_body[0] / 2 - 0.2, -sw_body[1] / 2 - 0.2, -eps]) cube([sw_body[0] + 0.4, fy, 2 + 2 * eps]);
            }
        }
        translate([0, 0, -eps]) sw_slot(sw_pad_h + 3 * eps);
    }
}

// lever slot (centred on the switch, extruded along z): rectangle with a 45 deg gable towards the back, so that its
// top prints without support when the column prints front face down
module sw_slot(h) {
    w = sw_window[0];
    d = sw_window[1];
    linear_extrude(h) polygon([[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [0, d / 2 + w / 2], [-w / 2, d / 2]]);
}

// ---------- battery bay (legs) ----------
module battery_bay(with_charger = true) {
    bd = bat[0] + bat_clr;
    cw = bd + 3;                                       // cradle width
    contact_shelf(shelf_z - shelf_t, shelf_t);                                          // - side, overlaps the 34.3 posts
    contact_shelf(bat_top_shelf_z, leg_rows[1] - lid_boss_d / 2 + 1 - bat_top_shelf_z); // + side, thickened into the next posts
    // cell: two U cradles open towards the lid (no overhang when printed front face down; the shelves above also
    // print as vertical walls)
    translate([col_w / 2, 0, 0]) {
        for (z = [bat_z0 + 4, bat_z0 + bat[1] - 9]) difference() {
            translate([-cw / 2, wall - eps, z]) cube([cw, bat_y - wall + eps, 5]);
            translate([0, bat_y, z - eps]) cylinder(d = bd, h = 5 + 2 * eps);
            // wire groove cut from the cell side (open towards the lid: no overhang), in line with the shelf slots
            translate([-cradle_groove[0] / 2, bat_y - bd / 2 - cradle_groove[1], z - eps]) cube([cradle_groove[0], bd / 2 + cradle_groove[1], 5 + 2 * eps]);
        }
        // polyfuse on the inner front wall: a side rib with a foot under each corner (the middle stays free for the
        // wires running down behind it)
        for (s = [-1, 1]) {
            translate([s < 0 ? -fuse[0] / 2 - 0.2 - rib : fuse[0] / 2 + 0.2, wall - eps, fuse_z0 - rib]) cube([rib, fuse[2] + 0.3 + eps, fuse[1] + rib]);
            translate([s < 0 ? -fuse[0] / 2 - 0.2 : fuse[0] / 2 - 2.8, wall - eps, fuse_z0 - rib]) cube([3, fuse[2] + 0.3 + eps, rib]);
        }
    }
}

// charge port: micro-USB breakout standing on the outer side wall, receptacle towards the lid. Bottom block (from the
// floor) and top rail, each with a groove for a PCB edge (the wall side of the groove is the solder-side standoff);
// front stop in two tabs (the wires leave forwards between them). Constant section along y: vertical walls when the
// column prints front face down.
module usbb_frame() {
    xg = usbb_x0 + usbb[2] + 0.2;       // groove bottom .. lip face
    xr = xg + 1;                        // rail face (0.8 lip over each PCB edge, clear of the receptacle)
    y0 = usbb_y0 - 0.2;
    y1 = lid_y - 0.3;
    difference() {
        union() {
            translate([wall - eps, y0, wall - eps]) cube([xr - wall + eps, y1 - y0, usbb_z0 + 0.8 - wall + eps]);
            translate([wall - eps, y0, usbb_z0 + usbb[0] - 0.8]) cube([xr - wall + eps, y1 - y0, 0.8 + 0.3 + rib]);
            for (z = [usbb_z0, usbb_z0 + usbb[0] - 3]) translate([wall - eps, y0 - rib, z]) cube([xr - wall + eps, rib + eps, 3]);
        }
        translate([usbb_x0 - 0.1, y0 - eps, usbb_z0 - 0.15]) cube([xg - usbb_x0 + 0.1, y1 - y0 + 2 * eps, usbb[0] + 0.3]);
    }
}

// notch at the bottom of the power leg's lid: receptacle shell + 0.3
module usbb_notch() {
    translate([usbb_xc - usbb_rec[1] / 2 - 0.3, lid_y - eps, usbb_zc - usbb_rec[0] / 2 - 0.3])
        cube([usbb_rec[1] + 0.6, wall + 2 * eps, usbb_rec[0] + 0.6]);
}

// microSD board grooves: one block per side wall, from the front wall to the lid, with a groove open towards the lid;
// the solid part in front of the groove is the front stop. Constant section along y: prints as vertical walls.
module sd_mount() { flat_slot(sd, sd_z0, sd_y0, sd_lip); }
module bk_mount() { flat_slot(bk, bk_z0, bk_y1 - bk[1], bk_lip, top = false, clr = bk_clr); }

// board lying flat (b = width x, depth y, thickness), underside at z0, front edge at y0: one block per side wall from
// the front wall to the lid, with a groove open towards the lid; the solid part in front of the groove is the stop.
// top = false: lower ledge only (connector / pads / parts along the side edges); a lid tab holds the back edge down
module flat_slot(b, z0, y0, lip, top = true, clr = 0.2) {
    ex = col_w / 2 - b[0] / 2;                         // board side edge (x)
    for (m = [0, 1]) translate([m * col_w, 0, 0]) mirror([m, 0, 0]) difference() {
        translate([wall - eps, wall - eps, z0 - rib]) cube([ex + lip - wall + eps, lid_y - 0.5 - wall + eps, b[2] + 0.3 + 2 * rib]);
        translate([min(ex - clr, wall - eps), y0 - 0.2, z0]) cube([b[0], D, top ? b[2] + 0.3 : b[2] + 0.3 + rib + eps]);
    }
}

// lid tab over the middle of a flat board's back edge (power leg lid), for the boards mounted with top = false
module hold_tab(b, z0) {
    translate([col_w / 2 - hold_tab[0] / 2, lid_y - 0.3 - hold_tab[1], z0 + b[2] + 0.3]) cube([hold_tab[0], 0.3 + hold_tab[1] + eps, hold_tab[2]]);
}

// polarity marks engraved in the back faces of the contact shelves, seen from the back with the lid off: "+" on the
// top shelf, "-" on the bottom one (a top face when printed front face down: no overhang)
pol_d = 0.4;                  // engraving depth
module pol_marks() {
    yb = lid_y - 0.5;                                  // back face of the shelves
    tt = leg_rows[1] - lid_boss_d / 2 + 1 - bat_top_shelf_z;
    zt = bat_top_shelf_z + tt / 2;
    zb = shelf_z - shelf_t / 2;
    translate([col_w / 2, yb - pol_d, 0]) {
        translate([-1.5, 0, zt - 0.4]) cube([3, pol_d + 0.1, 0.8]);
        translate([-0.4, 0, zt - 1.5]) cube([0.8, pol_d + 0.1, 3]);
        translate([-1.5, 0, zb - 0.4]) cube([3, pol_d + 0.1, 0.8]);
    }
}

// shelf under / over a contact plate: whole interior width (front, side walls, screw posts), wire slot at the front
// (the plate's solder tab points into it)
module contact_shelf(z, t) {
    difference() {
        translate([wall - eps, wall - eps, z]) cube([col_w - 2 * wall + 2 * eps, lid_y - wall - 0.5, t]);
        translate([col_w / 2 - wire_slot[0] / 2, wall - 2 * eps, z - eps]) cube([wire_slot[0], wire_slot[1], t + 2 * eps]);
    }
}

// ---------- halves and splint ----------
module half(i, top) { // one half of column i (z below / above its seam)
    intersection() {
        column(i);
        translate([-gap - 2, -1, top ? seam_z[i] : -1]) cube([col_w + 2 * gap + 4, D + 2, top ? H - seam_z[i] + 1 : seam_z[i] + 1]);
    }
}

module lid_half(mid, top, sd_slot_on = false) {
    sz = mid ? lid_seam_z[1] : lid_seam_z[0];
    intersection() {
        lid(mid, sd_slot_on);
        translate([-1, -1, top ? sz + 0.1 : -1]) cube([col_w + 2, D + 2, top ? H : sz - 0.1 + 1]);
    }
}

// U glued inside across the seam (front + both sides; the back is the lid). Printed standing, open side up.
module splint() {
    w = col_w - 2 * wall - 2 * splint_clr;
    d = lid_y - wall - splint_clr - 1;
    difference() {
        cube([w, d, splint_h]);
        translate([splint_t, splint_t, -eps]) cube([w - 2 * splint_t, d, splint_h + 2 * eps]);
    }
}

// ---------- lid ----------
// sd_slot_on: power leg lid (microSD card slot, tabs over the flat boards, vents)
module lid(mid = false, sd_slot_on = false) {
    difference() {
        union() {
            translate([wall + clr, lid_y, wall + clr]) cube([col_w - 2 * wall - 2 * clr, wall, H - 2 * wall - 2 * clr]);
            if (mid) { d1_lug(); d1_back_tabs(); scr_ribs(); if (hub) hub_tabs(); }
            if (sd_slot_on) { if (battery) hold_tab(charger, charger_z0); if (buck) hold_tab(bk, bk_z0); }
        }
        for (p = lid_bosses(mid)) translate([p[0], lid_y - eps, p[1]]) rotate([-90, 0, 0]) cylinder(d = screw_clear, h = wall + 2 * eps);
        if (sd_slot_on && battery) usbb_notch();
        if (sd_slot_on) translate([col_w / 2 + sd_sock_dx - sd_slot[0] / 2, lid_y - eps, sd_card_z - sd_slot[1] / 2])
            cube([sd_slot[0], wall + 2 * eps, sd_slot[1]]);
        if (!mid && vents) for (r = vent_rows, k = [0:r[1] - 1])   // both leg lids (the top half is shared); vertical holes when printing
            translate([col_w / 2 - vent[0] / 2, lid_y - eps, r[0] + k * vent[2]]) cube([vent[0], wall + 2 * eps, vent[1]]);
    }
}

// lug on the lid, just above the controller board, so it cannot slide up (plugging the USB-C in from below pushes it
// up into the lug): 4 thick, 45 deg gusset on the side away from the board (none below: wires soldered on its back)
module d1_lug() {
    z0 = d1_z0 + d1[1] + 0.3;
    translate([d1_x - 4, d1_lug_y, z0]) cube([8, lid_y - d1_lug_y + eps, 4]);
    lid_gusset(d1_x - 4, 8, z0 + 4, 1, 5);
}

// 45 deg gusset between the lid's inner face and a tab face at height ze, growing towards dir (+1 up / -1 down);
// it prints as a slope widening towards the bed (lids print outer face down), no support
module lid_gusset(x0, w, ze, dir, h) {
    hull() {
        translate([x0, lid_y - eps, dir > 0 ? ze - eps : ze - h]) cube([w, 2 * eps, h + eps]);
        translate([x0, lid_y - h, dir > 0 ? ze - eps : ze - eps]) cube([w, h, 2 * eps]);
    }
}

// tabs on the lid behind both ends of the controller board (vertical when the lid prints: no overhang)
module d1_back_tabs() {
    for (m = [0, 1], z = d1_holds) translate([m * col_w, 0, 0]) mirror([m, 0, 0])
        translate([wall + clr + 0.1, d1_hold_y + 0.15, z])
            cube([d1_x - d1[0] / 2 + d1_rib + d1_step(m, z) - wall - clr - 0.1, lid_y - d1_hold_y - 0.15 + eps, d1_end]);
}

// side strips centring the controller board between the walls, ribs in front of both ends; 45 deg fronts (no overhang
// when printed front face down)
module d1_guides() {
    s = col_w / 2 - wall - d1[0] / 2 - d1_groove_clr;     // strip fills the side gap minus the clearance
    yf = d1_back_y - d1_pcb_t - 0.15;                     // front of the board slot
    for (m = [0, 1]) translate([m * col_w, 0, 0]) mirror([m, 0, 0]) {
        if (s > 0) guide_prism(s, yf - 1.5, d1_hold_y, d1_z0 + d1_btn, d1[1] - d1_btn);
        for (z = d1_holds) guide_prism(max(s, 0) + d1_groove_clr + d1_rib + d1_step(m, z), yf - 1.5, yf, z, d1_end);
    }
}

// board standing parallel to the front wall (b = width x, height z, thickness; front face at y, bottom at z0): front
// stops over its side edges and centring strips beside it, both off the side walls with a 45 deg slope in front (no
// overhang when printed front face down)
module standing_mount(b, y, z0, lip) {
    s = col_w / 2 - wall - b[0] / 2 - 0.15;              // side gap minus the clearance
    for (m = [0, 1]) translate([m * col_w, 0, 0]) mirror([m, 0, 0]) {
        guide_prism(s + 0.15 + lip, y - 1.6, y, z0, b[1]);
        if (s > 0) guide_prism(s, y - 1.6, y + b[2], z0, b[1]);
    }
}
module hub_mount() { standing_mount(hub_b, hub_y, hub_z0, hub_lip); } // distribution boards P1 / P2

// lid tabs behind the distribution board's corners, with a 45 deg gusset on the side away from the board
module hub_tabs() {
    yb = hub_y + hub_b[2] + 0.15;                        // back face of the board + play
    w = col_w / 2 - hub_b[0] / 2 + hub_lip - wall - clr - 0.1;
    for (m = [0, 1]) translate([m * col_w, 0, 0]) mirror([m, 0, 0]) {
        for (z = [hub_z0 + 1, hub_z0 + hub_b[1] - 1 - hub_tab]) translate([wall + clr + 0.1, yb, z]) cube([w, lid_y - yb + eps, hub_tab]);
        lid_gusset(wall + clr + 0.1, w, hub_z0 + hub_b[1] - 1, 1, 4);
        lid_gusset(wall + clr + 0.1, w, hub_z0 + 1, -1, 4);
    }
}

// one rib on the lid along each side wall behind the screen's side edges (outside its header): keeps the screen from
// tipping back out of its frame; the wires come down between the two ribs, nothing to pinch them against the wall
module scr_ribs() {
    yb = wall + scr_t + 0.2;                             // back of the screen module + play
    z0 = scr_z - scr_pcb[1] / 2;
    for (m = [0, 1]) translate([m * col_w, 0, 0]) mirror([m, 0, 0])
        translate([wall + clr + 0.1, yb, z0 + 1]) cube([scr_rib, lid_y - yb + eps, scr_pcb[1] - 2]);
}

function d1_step(m, z) = m == 0 && z < d1_z0 + d1_notch[1] ? d1_notch[0] : 0; // reach further over the RST-side notch

module guide_prism(w, y0, y1, z, h) { // off the left side wall, w wide, y0..y1 deep, 45 deg slope in front of y0
    translate([0, 0, z]) linear_extrude(h) polygon([[wall - eps, y0 - w], [wall + w, y0], [wall + w, y1], [wall - eps, y1]]);
}

// grooves for the D1 mini board edges in both side walls (closed at the bottom: the board rests on them)
module d1_grooves() {
    depth = d1[0] / 2 + d1_groove_clr - (col_w / 2 - wall);
    if (depth > 0) for (s = [-1, 1]) translate([s < 0 ? wall - depth : col_w - wall - eps, d1_back_y - d1_pcb_t - 0.15, d1_z0])
        cube([depth + eps, d1_pcb_t + 0.3, 2 * d1[1] + 2]);
}

// window through the high-x side wall in front of the S3's BOOT button (it sticks out of the board edge)
module d1_boot_window() {
    if (d1_x + 25.4 / 2 + d1_boot_out + 0.3 > col_w - wall)
        translate([col_w - wall - eps, d1_back_y - d1_pcb_t - d1_btn_y - 0.3, d1_z0 + 0.5])
            cube([wall + 2 * eps, d1_btn_y + 0.6, d1_btn - 0.5]);
}

// ---------- sound ----------
module sound_mount() {
    x0 = col_w / 2 - spk[0] / 2;
    // pads in front of the short-end tabs, and the stop under the speaker, notched for its nub
    for (z = [spk_z0, spk_z0 + spk[2] - spk_pad]) translate([x0, wall - eps, z]) cube([spk[0], spk_front_y - wall + eps, spk_pad]);
    difference() {
        translate([x0, wall - eps, spk_z0 - spk_nub[1] - 1]) cube([spk[0], spk_front_y + 3 - wall + eps, spk_nub[1] + 1]);
        translate([col_w / 2 - spk_nub[0] / 2, spk_front_y, spk_z0 - spk_nub[1]]) cube([spk_nub[0], 4, spk_nub[1] + eps]);
    }
    // side rails (bottom half only, below the splint arms); their front face is a 45 deg slope off the side wall
    // (no overhang when printed front face down)
    spk_rail();
    translate([col_w, 0, 0]) mirror([1, 0, 0]) spk_rail();
    board_slot(amp, amp_z0, gap = pcb_gap);
}

module spk_rail() { // left one
    w = col_w / 2 - spk[0] / 2 - 0.3 - wall;
    y0 = spk_front_y - w;
    y1 = spk_front_y + spk[1] + 0.3;
    h = spk[2];
    translate([0, 0, spk_z0]) intersection() {
        hull() {
            translate([wall - eps, y0, 0]) cube([eps, y1 - y0, h]);
            translate([wall - eps, spk_front_y, 0]) cube([w + eps, y1 - spk_front_y, h]);
        }
        translate([0, wall - eps, -1]) cube([col_w, D, h + 2]); // kept behind the front wall (the panel hole is there)
    }
}

// slot for a small breakout on the inner front wall: two side rails, a top stop, and a bottom stop when nothing below
// holds the board (z0 = bottom edge of the board); the rails run into the stops: one rigid frame, no loose fins.
// top_to / bottom_to: the rails run up / down to this height (the next part there), so that slots stacked close
// together form one frame
// gap: the board stands off the wall on two strips under its side edges (solder tails / pads on the wall side)
module board_slot(b, z0, top = true, bottom = false, top_to = undef, bottom_to = undef, gap = 0, top_gap = 0) {
    r0 = bottom_to != undef ? bottom_to - z0 - eps : bottom ? -0.3 - rib : 0;
    r1 = top ? b[1] + 0.3 + rib : top_to != undef ? top_to - z0 + eps : b[1];
    d = gap + b[2] + 1.5;
    translate([col_w / 2, wall - eps, z0]) {
        for (s = [-1, 1]) translate([s * (b[0] / 2 + 0.2) + (s < 0 ? -rib : 0), 0, r0]) cube([rib, d, r1 - r0]);
        if (gap > 0) for (s = [-1, 1]) translate([s * (b[0] / 2 - 0.4) - 0.4, 0, 0]) cube([0.8, gap + eps, b[1]]);
        if (top) difference() { // top_gap: notch for a header pointing up (DS3231)
            translate([-b[0] / 2 - 0.2 - rib, 0, b[1] + 0.3]) cube([b[0] + 0.4 + 2 * rib, d, rib]);
            if (top_gap > 0) translate([-top_gap / 2, -eps, b[1]]) cube([top_gap, d + 2 * eps, rib + 1]);
        }
        if (bottom) translate([-b[0] / 2 - 0.2 - rib, 0, -0.3 - rib]) cube([b[0] + 0.4 + 2 * rib, d, rib]);
    }
}

// motion sensor ring on the inner front wall, centring the cap rim (a vertical tube when printed front face down)
module pir_mount() {
    translate([pir_x, wall - eps, pir_zc]) rotate([-90, 0, 0]) difference() {
        cylinder(d = pir_sleeve_d, h = pir_sleeve + eps);
        translate([0, 0, -eps]) cylinder(d = pir_cap_rim_d + 0.4, h = pir_sleeve + 3 * eps);
    }
}

// pivot bore trial piece, printed like the columns (front face down, bores horizontal): one side wall + pivot boss per
// bore, glued side (tube_od + tube_glue_clr) then turning side (tube_od + tube_run_clr), each nominal and + tube_test_offs.
// Push the brass tube in: glued = snug without forcing, turning = turns freely without play; keep the offset that fits.
tube_test_offs = [0, 0.2, 0.4];
// second round (2026-10-27, tube 7.93 measured; G8.1 printed 8.00 and it still turned): explicit bores, part tube_test2
tube_test2_glue = [7.9];
tube_test2_run = [8.0];
// third round: teardrop bores (2nd round: round bores sagged ~0.3 vertically), as long as the 1st (same cooling)
tube_test3_glue = [7.95, 8.0, 8.05];
tube_test3_run = [8.05, 8.1, 8.15];
module tube_test(pitch = 18, glue = [for (o = tube_test_offs) tube_od + tube_glue_clr + o],
                 run = [for (o = tube_test_offs) tube_od + tube_run_clr + o], tear = false) {
    bores = concat(glue, run);
    zs = [for (k = [0:len(bores) - 1]) k * pitch];
    difference() {
        union() {
            translate([0, 0, -pitch / 2]) cube([wall + pivot_boss_l, wall, pitch * len(bores)]);          // front wall
            translate([0, 0, -pitch / 2]) cube([wall, D / 2 + pivot_boss_d / 2 + 1, pitch * len(bores)]); // side wall
            for (z = zs) pivot_boss(wall - eps, z);
        }
        for (k = [0:len(bores) - 1]) {
            if (tear) xtear(-eps, zs[k], bores[k], wall + pivot_boss_l + 2 * eps);
            else xcyl(-eps, zs[k], bores[k], wall + pivot_boss_l + 2 * eps);
            translate([0.4, (wall + D / 2 - pivot_boss_d / 2) / 2 + 2, zs[k]])   // label on the outer side face, under the bore
                multmatrix([[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]) linear_extrude(0.4 + eps)
                    text(str(k < len(glue) ? "G" : "R", bores[k]), size = 3, halign = "center", valign = "center");
        }
    }
}

// motion sensor trial plate (front wall thickness, front face at y = 0): the outside-cap hole + sleeve, then one hole per
// pir_test_holes for the cap glued from the inside, each with a ring centring the rim
module pir_test(pitch = 17) {
    ring = function(d) wall + pir_dome_z(d) + pir_cap_rim_t + 1;
    difference() {
        union() {
            translate([-pitch / 2, 0, -pitch / 2]) cube([pitch * (len(pir_test_holes) + 1), wall, pitch]);
            translate([0, wall - eps, 0]) rotate([-90, 0, 0]) cylinder(d = pir_cap_d + 0.3 + 2 * 1.2, h = pir_cap_skirt - wall + eps);
            for (k = [0:len(pir_test_holes) - 1]) translate([(k + 1) * pitch, wall - eps, 0]) rotate([-90, 0, 0])
                cylinder(d = pir_cap_rim_d + 0.4 + 2 * 1.2, h = ring(pir_test_holes[k]) - wall + eps);
        }
        translate([0, -eps, 0]) rotate([-90, 0, 0]) cylinder(d = pir_cap_d + 0.3, h = pir_cap_skirt + 3 * eps);
        for (k = [0:len(pir_test_holes) - 1]) translate([(k + 1) * pitch, -eps, 0]) rotate([-90, 0, 0]) {
            cylinder(d = pir_test_holes[k], h = wall + 3 * eps);
            translate([0, 0, wall]) cylinder(d = pir_cap_rim_d + 0.4, h = ring(pir_test_holes[k]));
        }
    }
}

// ---------- small parts ----------
module inserts(speaker = false) { // black flush plugs for the panel holes of a middle column (column-local placement)
    difference() {
        translate([0, eps, 0]) mid_panels(wall - 2 * eps, insert_clr);
        if (!scr_open) scr_window(bevel = scr_win_bevel);
        // grille: horizontal slots in the lower plug in front of the speaker
        if (speaker) for (z = [spk_z0 + 3:grille_slot[1]:spk_z0 + spk[2] - 3])
            if (z > bottom_panel_z[0] + 2 && z + grille_slot[0] < bottom_panel_z[1] - 2)
                translate([col_w / 2 - (spk[0] - 2) / 2, -1, z]) cube([spk[0] - 2, wall + 2, grille_slot[0]]);
    }
}

module tube_collar() {
    difference() { cylinder(d = collar[0], h = collar[1]); translate([0, 0, -eps]) cylinder(d = tube_od + tube_glue_clr, h = collar[1] + 2 * eps); }
}

module test_screen() { // front wall of a middle column around the screen
    intersection() {
        column(2);
        translate([-1, 0, scr_z - scr_pcb[1] / 2 - scr_clr - scr_frame_w - 2]) cube([col_w + 2, wall + scr_t + 1, scr_pcb[1] + 2 * (scr_clr + scr_frame_w) + 4]);
    }
}

// ---------- preview dummies ----------
module pir_dummy() { // Fresnel cap + detector + breakout (column-local); also part "pir_dummy" for the pose renders
    translate([pir_x, 0, pir_zc]) {
        translate([0, pir_cap_y, 0]) rotate([-90, 0, 0]) {
            cylinder(d = pir_cap_d, h = pir_cap_skirt);
            translate([0, 0, -pir_cap_rim_t]) cylinder(d = pir_cap_rim_d, h = pir_cap_rim_t);
            translate([0, 0, -pir_cap_rim_t]) rotate_extrude() polygon(concat([[0, 0]], [for (k = [0:12]) let(d = pir_cap_rim_d - k * (pir_cap_rim_d - pir_dome_top_d) / 12)
                [d / 2, -pir_dome_z(d)]], [[0, -pir_dome_h]]));
            translate([0, 0, pir_cap_skirt]) cylinder(d = pir_cap_d, h = pir_can_fl);  // flange (as wide as the cap)
        }
        color("darkgreen") translate([0, pir_pcb_y0, 0]) rotate([0, -pir_pcb_a, 0])
            translate([-pir_can_d / 2, 0, -pir_pcb[2] / 2 + pir_pcb_dn]) cube([pir_pcb[0], pir_pcb[1], pir_pcb[2]]);
    }
}

module s3_dummy() { // S3 board + its USB-C, and when socketed the headers and the carrier
    color("teal") translate([d1_x - d1[0] / 2, d1_back_y - d1_pcb_t, d1_z0]) cube([d1[0], d1_pcb_t, d1[1]]);
    color("silver") translate([d1_x - 4.5, d1_back_y - d1_pcb_t - d1_usb_h, d1_z0]) cube([9, d1_usb_h, 7.5]);
    if (s3_socket) {
        color("black") for (m = [0, 1]) translate([m ? d1_x + d1[0] / 2 - s3_sock[0] : d1_x - d1[0] / 2, d1_back_y, d1_z0 + 8.8 - 1.27])
            cube([s3_sock[0], s3_pin_base + s3_sock_h, s3_sock[1]]);
        color("peru") translate([d1_x - d1[0] / 2, carrier_back_y - s3_carrier_t, d1_z0]) cube([d1[0], s3_carrier_t, d1[1]]);
    }
}

module dummies(i) {
    conn_dummies(i);
    if (col_mid[i]) {
        color([0.08, 0.08, 0.1]) translate([scr_x - scr_pcb[0] / 2, wall, scr_z - scr_pcb[1] / 2]) cube([scr_pcb[0], scr_t, scr_pcb[1]]);
        if (i == 1) s3_dummy();        if (sound && i == speaker_col) {
            color("dimgray") translate([col_w / 2 - spk[0] / 2, spk_front_y, spk_z0]) cube(spk);
            color("purple") translate([col_w / 2 - amp[0] / 2, wall + pcb_gap, amp_z0]) cube([amp[0], amp[2], amp[1]]);
            color("navy") translate([col_w / 2 - c7[1] / 2, c7_y, c7_z + c7[0] / 2]) rotate([0, 90, 0]) translate([0, c7[0] / 2, 0]) cylinder(d = c7[0], h = c7[1]);
        }
        if (sensors && i == sensor_col) {
            color("crimson") translate([col_w / 2 - acc[0] / 2, wall + pcb_gap, acc_z0]) cube([acc[0], acc[2], acc[1]]);
            color("olive") translate([col_w / 2 - mic[0] / 2, wall, mic_z0]) cube([mic[0], mic[2], mic[1]]);
        }
        if (pir && i == pir_col) color("white") pir_dummy();
        if (hub) {
            color("peru") translate([col_w / 2 - hub_b[0] / 2, hub_y, hub_z0]) cube([hub_b[0], hub_b[2], hub_b[1]]);
        }
    } else if (battery) {
        color("royalblue") translate([col_w / 2, bat_y, bat_z0]) cylinder(d = bat[0], h = bat[1]);
        color("silver") for (z = [shelf_z, bat_top_shelf_z - contact[2]]) translate([col_w / 2 - contact[0] / 2, bat_y - contact[1] / 2, z]) cube(contact);
        color("silver") translate([col_w / 2, bat_y, shelf_z + contact[2]]) cylinder(d = 5, h = spring_work);
        if (i == power_col) {
            color("darkgreen") translate([col_w / 2 - charger[0] / 2, lid_y - 0.3 - charger[1], charger_z0]) cube([charger[0], charger[1], charger[2] + charger_h]);
            color("dimgray") translate([usbb_x0, usbb_y0, usbb_z0]) cube([usbb[2], usbb[1], usbb[0]]);
            color("silver") translate([usbb_x0 + usbb[2], usbb_y1 + usbb_out - 5, usbb_zc - usbb_rec[0] / 2]) cube([usbb_rec[1], 5, usbb_rec[0]]);
        }
        color("orange") translate([col_w / 2 - fuse[0] / 2, wall, fuse_z0]) cube([fuse[0], fuse[2], fuse[1]]);
        if (sensors && i == rtc_col) color("navy") translate([col_w / 2 - rtc[0] / 2, wall, rtc_z0]) cube([rtc[0], rtc[2], rtc[1]]);
        if (bme && i == bme_col) color("mediumorchid") translate([col_w / 2 - bme_b[0] / 2, wall, bme_z0]) cube([bme_b[0], bme_b[2], bme_b[1]]);
        if (sd_reader && i == sd_col) {
            color("seagreen") translate([col_w / 2 - sd[0] / 2, sd_y0, sd_z0]) cube([sd[0], sd[1], sd[2]]);
            color("silver") translate([col_w / 2 + sd_sock_dx - sd_sock[0] / 2, sd_y1 + sd_sock_over - sd_sock[1], sd_z0 + sd[2]]) cube(sd_sock);
            color("black") translate([col_w / 2 + sd_sock_dx - 5.5, sd_y1 + sd_sock_over + sd_card_out - 15, sd_card_z - 0.5]) cube([11, 15, 1]);
        }
        if (buck && i == power_col) {
            color("mediumpurple") translate([col_w / 2 - bk[0] / 2, bk_y1 - bk[1], bk_z0]) cube(bk);
        }
        if (pp && i == power_col) {
            color("tan") translate([col_w / 2 - pp_b[0] / 2, lid_y - 0.3 - pp_b[1], pp_z0]) cube([pp_b[0], pp_b[1], pp_b[2]]);
            color("dimgray") translate([col_w / 2 - 5, lid_y - 0.3 - pp_b[1] / 2 - 5, pp_z0 + pp_b[2]]) cube([10, 10, pp_parts]);
            color("dimgray") translate([col_w / 2 - 3, bk_y1 - bk[1] / 2 - 3, bk_z0 + bk[2]]) cube([6, 6, bk_h]);
        }
    }
    if (switch_on && i == power_col) color("black") translate([col_w / 2, sw_y, sw_recess]) {
        translate([-sw_lever[0] / 2 - sw_travel / 2, -sw_lever[1] / 2, 0]) cube([sw_lever[0], sw_lever[1], sw_lever_h]);
        translate([-sw_body[0] / 2, -sw_body[1] / 2, sw_lever_h]) cube([sw_body[0], sw_body[1], sw_h - sw_lever_h - 6.7]);
    }
    if (i < 3) for (z = pivot_z) color("gold") translate([col_w - wall - pivot_boss_l, D / 2, z]) rotate([0, 90, 0])
        difference() { cylinder(d = tube_od, h = 2 * (wall + pivot_boss_l) + gap + collar[1] + tube_over); cylinder(d = tube_od - 1, h = 90, center = true); }
}
if (tube_od + tube_run_clr > pivot_boss_d - 2 * 2.5 || detent_r - (detent_bump_d + 0.2) / 2 < (tube_od + tube_run_clr) / 2 + 1) {
    echo("WARNING: pivot tube too large for the bosses / detent ring");
}

// ---------- connectors (demountable wiring) ----------
function dp_w(n) = n * 2.54 + 0.3;                    // Dupont housing width for n pins
scr_hdr_z = scr_z + scr_pcb[1] / 2 - scr_hdr_dz;
acc_hdr_x = col_w / 2 - acc[0] / 2 + 1.27;           // GY-291: 8 pins along its left long edge
// [column, ref, what, min corner, max corner] (column-local), mated housings + bend room
function on_board(i, ref, what, xc, n, y, zc, vertical = false) = vertical
    ? [i, ref, what, [xc - dp_t / 2, y, zc], [xc + dp_t / 2, y + dp_on + bend, zc + dp_w(n)]]
    : [i, ref, what, [xc - dp_w(n) / 2, y, zc - dp_t / 2], [xc + dp_w(n) / 2, y + dp_on + bend, zc + dp_t / 2]];
// inline pair standing along z: w wide (x), t thick (y), mated length l + ends (wire bends at both ends)
function inline(i, ref, what, x0, y0, z0, w, t, l, ends = 2 * bend) = [i, ref, what, [x0, y0, z0], [x0 + w, y0 + t, z0 + l + ends]];
// screens: right-angle header on the back, pins down, housing (+ key rib) lying flat on the back, wires straight down
function scr_conn(i, ref, what) = scr_hdr_ra
    ? [i, ref, what, [scr_x - dp_w(8) / 2, wall + scr_t, scr_hdr_z + 1.25 - dp_on - 2], [scr_x + dp_w(8) / 2, wall + scr_t + scr_hdr_back + key_rib + 0.3, scr_hdr_z + 1.25]]
    : on_board(i, ref, what, scr_x, 8, wall + scr_t, scr_hdr_z);
c7_y = wall + pcb_gap + amp[2] + 0.5;               // C7 lying across behind the amplifier, between X6 and X5
c7_z = amp_z0 + 3.5;
// bundle corridor in the middle columns: from the tube end down behind the screen to P1 / P2 (no connector there)
corridor = [[col_w / 2 - 6, 13.5, hub_z0 + hub_b[1] + 4], [col_w / 2 + 6, 25, pivot_z[0] - collar[0] / 2]]; // behind the screen connectors
park_z0 = charger_z0 + charger[2] + charger_h + 1;    // power block connectors: cavity above the TP4056, below the
park_y = [lid_y - 0.6 - xh_inline[0], lid_y - 1.1 - 2 * xh_inline[0]]; // power-path board, two rows at the back
CONN = [
    scr_conn(1, "X1", "screen 1 · 8 p. right-angle"),
    on_board(1, "X2", "ADXL345 · 8 p. (5 wires, INT2 removed)", acc_hdr_x, 8, wall + pcb_gap + acc[2], acc_z0, true),
    inline(1, "X3", "INMP441 · pigtail + 5 p. (+1)", col_w - wall - 0.5 - dp_w(6), lid_y - 1 - dp_t, mid_rows[1] + lid_boss_d / 2 + 0.3, dp_w(6), dp_t, dp_inline, 2),
    scr_conn(2, "X4", "screen 2 · 8 p. right-angle"),
    on_board(2, "X5", "MAX98357A · 4 + 3 p. (GAIN removed)", col_w / 2, 7, wall + pcb_gap + amp[2], amp_z0 + amp[1] - 1.3),
    on_board(2, "X6", "speaker · 2 p.", col_w / 2, 2, wall + pcb_gap + amp[2], amp_z0 + 1.3),
    inline(2, "X7", "AM312 · pigtail + 3 p. (+1)", wall + 3.5, lid_y - 1 - dp_t, scr_z - 12, dp_w(4), dp_t, dp_inline),
    [3, "X8", "DS3231 · 6 p. right-angle (4 wires, 32K removed)", [col_w / 2 - dp_w(6) / 2, wall + rtc[2] - rtc_hdr_y - dp_t / 2, rtc_z0 + rtc[1]],
        [col_w / 2 + dp_w(6) / 2, wall + rtc[2] - rtc_hdr_y + dp_t / 2, rtc_z0 + rtc[1] + dp_on + bend]],
    on_board(3, "X9", "BME280 · 4 p.", col_w / 2, 4, wall + bme_b[2], bme_z0 + bme_b[1] - 1.3),
    inline(0, "X10", "J1 + SW1 ↔ power block · XH 4", 3.5, park_y[1], park_z0, 12.4, xh_inline[0], xh_inline[1], 2),
    inline(0, "X12", "left cell → power block · XH 2", 16.4, park_y[0], park_z0, 7.4, xh_inline[0], xh_inline[1], 2),
    inline(0, "X13", "power block → tubes · XH 4", 3.5, park_y[0], park_z0, 12.4, xh_inline[0], xh_inline[1], 2),
    inline(0, "X14", "VBAT/2, USB_DET, SD_EN, VSENSE_B · XH 4", col_w / 2 - 6.2, park_y[1] - 0.5 - xh_inline[0], park_z0, 12.4, xh_inline[0], xh_inline[1], 2),
    // right cell: its pair comes down from the tubes, parked above the power-path board between the lid screw posts
    inline(0, "X16", "right cell → power block · XH 2", col_w / 2 - 3.7, park_y[0], pp_z0 + pp_b[2] + pp_parts + 1.5, 7.4, xh_inline[0], xh_inline[1], 2),
    inline(0, "X15", "microSD · pigtail + 5 p. (+1)", col_w / 2 - dp_w(6) / 2, 3.5, leg_rows[1] + lid_boss_d / 2 + 0.5, dp_w(6), dp_t, dp_inline),
];

// keep-out boxes of a column (solid parts and other modules): [what, min, max]
function mirx(k) = [k[0], [col_w - k[2][0], k[1][1], k[1][2]], [col_w - k[1][0], k[2][1], k[2][2]]];
function both(k) = [k, mirx(k)];
function standing(what, b, y1, z0, d, top_gap = 0) = concat( // board on the front wall + its slot (rails, stops)
    [[what, [col_w / 2 - b[0] / 2, wall, z0], [col_w / 2 + b[0] / 2, y1, z0 + b[1]]]],
    both([str(what, " (rail)"), [col_w / 2 - b[0] / 2 - 0.2 - rib, wall, z0 - 0.3 - rib], [col_w / 2 - b[0] / 2 - 0.2, wall + d, z0 + b[1] + 0.3 + rib]]),
    both([str(what, " (top stop)"), [col_w / 2 - b[0] / 2 - 0.2 - rib, wall, z0 + b[1] + 0.3], [col_w / 2 - top_gap / 2, wall + d, z0 + b[1] + 0.3 + rib]]));
function flat(what, b, z0, y0, parts, lip) = concat(
    [[what, [col_w / 2 - b[0] / 2, y0, z0], [col_w / 2 + b[0] / 2, y0 + b[1], z0 + b[2] + parts]]],
    both([str(what, " (groove)"), [wall, wall, z0 - rib], [col_w / 2 - b[0] / 2 + lip, lid_y - 0.5, z0 + b[2] + 0.3 + rib]]));
function kos(i) = let(mid = col_mid[i], zs = seam_z[i] - splint_h / 2, ze = seam_z[i] + splint_h / 2, st = splint_t + splint_clr,
                      sz0 = scr_z - scr_pcb[1] / 2, sz1 = scr_z + scr_pcb[1] / 2, ht = hub_z0 + hub_b[1]) concat(
    [for (p = lid_bosses(mid)) ["lid screw", [p[0] - lid_boss_d / 2, wall, p[1] - lid_boss_d / 2], [p[0] + lid_boss_d / 2, lid_y, p[1] + lid_boss_d / 2]]],
    i < 3 ? [["pivot boss", [col_w - wall - pivot_boss_l, D / 2 - pivot_boss_d / 2, pivot_z[0] - pivot_boss_d / 2], [col_w - wall, D / 2 + pivot_boss_d / 2, pivot_z[0] + pivot_boss_d / 2]]] : [],
    i > 0 ? [["collar / tube end", [wall, D / 2 - collar[0] / 2, pivot_z[0] - collar[0] / 2], [tube_end_x, D / 2 + collar[0] / 2, pivot_z[0] + collar[0] / 2]]] : [],
    [["splint", [wall, wall, zs], [col_w - wall, wall + st, ze]]], both(["splint", [wall, wall, zs], [wall + st, lid_y - 1, ze]]),
    ties ? [for (t = TIES) if (t[0] == i) tie_box(t)] : [],
    mid ? concat(
        [["screen", [scr_x - scr_pcb[0] / 2, wall, sz0], [scr_x + scr_pcb[0] / 2, wall + scr_t, sz1]]],
        both(["screen rib", [wall, wall + scr_t + 0.2, sz0 + 1], [wall + clr + 0.1 + scr_rib, lid_y, sz1 - 1]]),
        hub ? concat([["P1 / P2", [col_w / 2 - hub_b[0] / 2, hub_y - 1.6, hub_z0], [col_w / 2 + hub_b[0] / 2, hub_y + hub_b[2], ht]]],
            both(["P1 / P2 tab", [wall, hub_y + hub_b[2], hub_z0 + 1 - 4], [col_w / 2 - hub_b[0] / 2 + hub_lip, lid_y, hub_z0 + 1 + hub_tab]]),
            both(["P1 / P2 tab", [wall, hub_y + hub_b[2], ht - 1 - hub_tab], [col_w / 2 - hub_b[0] / 2 + hub_lip, lid_y, ht - 1 + 4]])) : [],
        [["lid lug (S3)", [d1_x - 4, d1_lug_y, d1_z0 + d1[1] + 0.3], [d1_x + 4, lid_y, d1_z0 + d1[1] + 9.3]]],
        [for (z = d1_holds) each both(["lid tab (S3)", [wall, d1_hold_y, z], [d1_x - d1[0] / 2 + d1_rib + d1_notch[0], lid_y, z + d1_end]])],
        i == 1 ? concat([["S3 + carrier + wires", [d1_x - d1[0] / 2, d1_back_y - d1_pcb_t - d1_usb_h, d1_z0], [d1_x + d1[0] / 2, lid_y, d1_z0 + d1[1]]]],
            sensors ? concat(standing("ADXL345", acc, wall + pcb_gap + acc[2], acc_z0, pcb_gap + acc[2] + 1.5),
                             [["INMP441", [col_w / 2 - mic[0] / 2, wall, mic_z0], [col_w / 2 + mic[0] / 2, wall + mic[2], mic_z0 + mic[1]]]]) : []) : [],
        [["harness corridor", corridor[0], corridor[1]]],
        i == 2 && sound ? concat([["C7", [col_w / 2 - c7[1] / 2, c7_y, c7_z], [col_w / 2 + c7[1] / 2, c7_y + c7[0], c7_z + c7[0]]]],
            [["speaker", [col_w / 2 - spk[0] / 2, spk_front_y, spk_z0], [col_w / 2 + spk[0] / 2, spk_front_y + spk[1], spk_z0 + spk[2]]]],
            standing("MAX98357A", amp, wall + pcb_gap + amp[2], amp_z0, pcb_gap + amp[2] + 1.5)) : [],
        i == 2 && pir ? [["AM312", [pir_x - pir_sleeve_d / 2, wall, pir_zc - pir_sleeve_d / 2], [pir_x + pir_sleeve_d / 2, pir_pcb_y0, pir_zc + pir_sleeve_d / 2]],
                         ["AM312 breakout", [pir_x + pir_pcb_fp[0], pir_pcb_y0, pir_zc + pir_pcb_fp[1]], [pir_x + pir_pcb_fp[2], pir_pcb_y0 + pir_pcb[1], pir_zc + pir_pcb_fp[3]]]] : [])
    : concat(
        [["bottom shelf", [wall, wall + wire_slot[1], shelf_z - shelf_t], [col_w - wall, lid_y, shelf_z]],
         ["top shelf", [wall, wall + wire_slot[1], bat_top_shelf_z], [col_w - wall, lid_y, top_shelf_top]],
         ["cell", [col_w / 2 - bat[0] / 2, bat_y - bat[0] / 2, bat_z0], [col_w / 2 + bat[0] / 2, bat_y + bat[0] / 2, bat_z0 + bat[1]]],
         ["fuse", [col_w / 2 - fuse[0] / 2, wall, fuse_z0], [col_w / 2 + fuse[0] / 2, wall + fuse[2], fuse_z0 + fuse[1]]]],
        sensors && i == rtc_col ? standing("DS3231", rtc, wall + rtc[2], rtc_z0, rtc[2] + 1.5, plugs ? dp_w(6) + 1 : 0) : [],
        bme && i == bme_col ? standing("BME280", bme_b, wall + bme_b[2], bme_z0, bme_b[2] + 1.5) : [],
        battery && i == power_col ? concat(
            [["micro-USB socket", [wall, usbb_y0 - 0.2 - rib, wall], [usbb_x0 + usbb[2] + usbb_rec[1], lid_y, usbb_z0 + usbb[0] + 0.3 + rib]]],
            flat("microSD reader", sd, sd_z0, sd_y0, sd_sock[2], sd_lip), flat("TPS63020", bk, bk_z0, bk_y1 - bk[1], bk_h, bk_lip),
            flat("TP4056", charger, charger_z0, lid_y - 0.3 - charger[1], charger_h, charger_lip),
            flat("power-path board", pp_b, pp_z0, lid_y - 0.3 - pp_b[1], pp_parts, pp_lip)) : []));
function ov(a0, a1, b0, b1) = a0[0] < b1[0] - 0.05 && b0[0] < a1[0] - 0.05 && a0[1] < b1[1] - 0.05 && b0[1] < a1[1] - 0.05 && a0[2] < b1[2] - 0.05 && b0[2] < a1[2] - 0.05;
module conn_box(j) { c = CONN[j]; translate(c[3]) cube(c[4] - c[3]); }
XH_REFS = ["X10", "X12", "X13", "X14", "X16"];   // inline JST-XH pairs (power block): drawn in detail inside their check box
xh_male_back = 1;             // crimped male housing: body behind the shroud (8 overall, measured)
xh_female = [7, 1.7];         // XHP female housing: length, part left outside the shroud once mated (mated pair 9.7, measured)
// Dupont connectors drawn in detail: [ref, pins, mating axis (0 x, 1 y, 2 z), wires leaving towards + (1) or - (-1),
// inline pair?]; the pins spread along the box's longer remaining side
DP = [["X1", 8, 2, -1, false], ["X2", 8, 1, 1, false], ["X3", 6, 2, 1, true], ["X4", 8, 2, -1, false],
      ["X5", 7, 1, 1, false], ["X6", 2, 1, 1, false], ["X7", 4, 2, 1, true], ["X8", 6, 2, 1, false],
      ["X9", 4, 1, 1, false], ["X15", 6, 2, 1, true]];
module conn_dummies(i) { if (plugs) for (j = [0:len(CONN) - 1]) if (CONN[j][0] == i) {
    dp = [for (d = DP) if (d[0] == CONN[j][1]) d];
    if ([for (r = XH_REFS) if (r == CONN[j][1]) 1] != []) { xh_pair(CONN[j]); color("darkorange", 0.2) conn_box(j); }
    else if (dp != []) { dupont(CONN[j], dp[0][1], dp[0][2], dp[0][3], dp[0][4]); color("darkorange", 0.2) conn_box(j); }
    else color("darkorange", 0.85) conn_box(j);
} }
// Dupont housings in their check box, drawn in local axes (u pins, v thickness, w mating, wires out at +w) mapped onto
// the box: on a module, its header base (2.5) then the female housing (dp_on in all) and the wire stubs; inline, the
// male and the female housings (dp_inline) between two wire stubs
module dupont(c, n, ma, dir, inl) {
    lo = c[3]; hi = c[4];
    o = [for (a = [0:2]) if (a != ma) a];
    pa = hi[o[0]] - lo[o[0]] >= hi[o[1]] - lo[o[1]] ? o[0] : o[1];
    ta = pa == o[0] ? o[1] : o[0];
    U = hi[pa] - lo[pa]; V = hi[ta] - lo[ta]; W = hi[ma] - lo[ma];
    function e(r, a) = r == a ? 1 : 0;
    multmatrix([for (r = [0:2]) [e(r, pa), e(r, ta), e(r, ma), lo[r]], [0, 0, 0, 1]])
    translate([0, 0, dir > 0 ? 0 : W]) mirror([0, 0, dir > 0 ? 0 : 1]) {
        u0 = (U - n * 2.54) / 2 + 1.27; t = min(V, dp_t);
        w0 = inl ? (W - dp_inline) / 2 : 0;                    // housings start (inline: centred between the bends)
        h1 = inl ? dp_inline / 2 : 2.5;                        // male housing / header base
        color(inl ? "darkSlateGrey" : [0.1, 0.1, 0.1]) translate([(U - dp_w(n)) / 2, 0, w0]) cube([dp_w(n), t, h1]);
        color([0.16, 0.17, 0.19]) translate([(U - dp_w(n)) / 2 + 0.1, 0.1, w0 + h1]) cube([dp_w(n) - 0.2, t - 0.2, (inl ? dp_inline : dp_on) - h1]);
        for (k = [0:n - 1]) color(k % 2 ? "darkSlateGrey" : "firebrick") {
            translate([u0 + k * 2.54, t / 2, w0 + (inl ? dp_inline : dp_on) - 0.05]) cylinder(d = 1, h = 2, $fn = 10);
            if (inl) translate([u0 + k * 2.54, t / 2, w0 - 1.95]) cylinder(d = 1, h = 2, $fn = 10);
        }
        if (!inl) color("silver") for (k = [0:n - 1]) translate([u0 + k * 2.54 - 0.32, t / 2 - 0.32, -0.8]) cube([0.64, 0.64, 0.85]);
    }
}
// mated inline XH pair standing in its box, wires vertical: male housing at the bottom (XH() shroud, opening up, on a
// back block holding the crimped pins), XHP female housing plugged in from above, wire stubs at both ends
module xh_pair(c) {
    n = round((c[4][0] - c[3][0] - 2.4) / 2.5);
    A = (n - 1) * 2.5;
    x0 = c[3][0] + 2.45; yc = (c[3][1] + c[4][1]) / 2; z0 = c[3][2] + 1;
    zs = z0 + xh_male_back;                                   // shroud floor
    color("ivory") translate([c[3][0], yc - 5.75 / 2, z0]) cube([A + 4.9, 5.75, xh_male_back]);
    translate([x0, yc, zs]) XH(n);
    color("burlywood") {
        translate([x0 - 1.5, yc - 3.9 / 2, zs + 1.5]) cube([A + 3, 3.9, xh_female[0] - xh_female[1]]);
        translate([c[3][0], yc - 5.75 / 2, zs + 7]) cube([A + 4.9, 5.75, xh_female[1]]);
    }
    for (k = [0:n - 1]) color(k % 2 ? "darkSlateGrey" : "firebrick") {
        translate([x0 + k * 2.5, yc, z0 - 1]) cylinder(d = 1.5, h = 1.05, $fn = 12);
        translate([x0 + k * 2.5, yc, zs + 7 + xh_female[1] - 0.05]) cylinder(d = 1.5, h = 1.05, $fn = 12);
    }
}
if (plugs) {
    for (j = [0:len(CONN) - 1]) let(c = CONN[j], a0 = c[3], a1 = c[4]) {
        if (a0[0] < wall - 0.05 || a1[0] > col_w - wall + 0.05 || a0[1] < wall - 0.05 || a1[1] > lid_y + 0.05 || a0[2] < wall || a1[2] > H - wall)
            echo(str("WARNING: connector ", c[1], " (", c[2], ") leaves the column interior"));
        for (k = kos(c[0])) if (ov(a0, a1, k[1], k[2])) echo(str("WARNING: connector ", c[1], " (", c[2], ") runs into: ", k[0]));
        for (jj = [0:len(CONN) - 1]) if (jj > j && CONN[jj][0] == c[0] && ov(a0, a1, CONN[jj][3], CONN[jj][4]))
            echo(str("WARNING: connectors ", c[1], " and ", CONN[jj][1], " overlap"));
    }
    echo(str(len(CONN), " connectors placed and checked (S3 on its socket: ", d1_back_y - d1_pcb_t - d1_usb_h - wall,
             " mm in front of its USB-C, ", d1_standoff, " mm of wires behind the carrier)"));
}

// ---------- assembly / print layouts ----------
module placed(i, angle = 0) {
    pz = pivot_z[0];
    translate([col_x[i], 0, 0]) translate([0, D / 2, pz]) rotate([angle, 0, 0]) translate([0, -D / 2, -pz]) children();
}

module assembly() {
    for (i = [0:3]) placed(i, i == 0 ? leg_angle[0] : i == 3 ? leg_angle[1] : 0) {
        color(col_mid[i] ? "lightgray" : "gray") column(i);
        color("darkgray") lid(col_mid[i], sd_reader && i == sd_col, i != sensor_col);
        if (col_mid[i]) color("black") inserts(sound && i == speaker_col);
        %dummies(i);
    }
}

// lying face down, lids off, components shown (open: opaque shells, open_ghost: see-through shells)
module open_view(alpha = 1) {
    rotate([90, 0, 0]) for (i = [0:3]) placed(i) {
        color(col_mid[i] ? [0.83, 0.83, 0.83, alpha] : [0.55, 0.55, 0.55, alpha]) column(i);
        if (col_mid[i]) color("black") inserts(sound && i == speaker_col);
        dummies(i);
    }
}

if (part == "assembly") assembly();
else if (part == "open") open_view();
else if (part == "open_ghost") open_view(0.3);
else if (part == "col0") column(0);
else if (part == "col1") column(1);
else if (part == "col2") column(2);
else if (part == "col3") column(3);
else if (part == "lid_leg") lid(false);
else if (part == "lid_mid") lid(true);
else if (part == "lid_mid_left") lid(true);
else if (part == "lid_leg_sd") lid(false, true);
else if (part == "inserts") inserts();
else if (part == "inserts_speaker") inserts(true);
else if (part == "collar") tube_collar();
else if (part == "test_screen") test_screen();
else if (part == "splint") splint();
else if (part == "pir_dummy") pir_dummy();
// print orientations: columns and inserts front face on the bed, lids outer face on the bed
// one-piece columns and lids (CR-10, 300 x 300: no split, no splint)
else if (part == "print_col0") rotate([90, 0, 0]) column(0);
else if (part == "print_col1") rotate([90, 0, 0]) column(1);
else if (part == "print_col2") rotate([90, 0, 0]) column(2);
else if (part == "print_col3") rotate([90, 0, 0]) column(3);
else if (part == "print_lid_leg") translate([0, 0, D]) rotate([-90, 0, 0]) lid(false);
else if (part == "print_lid_mid") translate([0, 0, D]) rotate([-90, 0, 0]) lid(true);
else if (part == "print_lid_mid_left") translate([0, 0, D]) rotate([-90, 0, 0]) lid(true);
else if (part == "print_lid_leg_sd") translate([0, 0, D]) rotate([-90, 0, 0]) lid(false, true);
else if (part == "print_splint") for (k = [0:3]) translate([k * (col_w - 2 * wall + 3), 0, 0]) splint(); // 4 splints
else if (part == "print_inserts") rotate([90, 0, 0]) inserts();
else if (part == "print_inserts_speaker") rotate([90, 0, 0]) inserts(true);
else if (part == "print_collar") for (k = [0:3 * len(pivot_z) - 1]) translate([k * (collar[0] + 3), 0, 0]) tube_collar(); // one per joint
else if (part == "print_test_screen") rotate([90, 0, 0]) test_screen();
else if (part == "print_test_level") test_level();
else if (part == "pir_test") pir_test();
else if (part == "print_pir_test") rotate([90, 0, 0]) pir_test();
else if (part == "tube_test") tube_test();
else if (part == "print_tube_test") rotate([90, 0, 0]) tube_test();
else if (part == "tube_test2") tube_test(glue = tube_test2_glue, run = tube_test2_run);
else if (part == "print_tube_test2") rotate([90, 0, 0]) tube_test(glue = tube_test2_glue, run = tube_test2_run);
else if (part == "tube_test3") tube_test(glue = tube_test3_glue, run = tube_test3_run, tear = true);
else if (part == "print_tube_test3") rotate([90, 0, 0]) tube_test(glue = tube_test3_glue, run = tube_test3_run, tear = true);

// halves: col<i>_bottom / col<i>_top, lid_<leg|mid>_<bottom|top> (assembly position or print orientation)
for (i = [0:3], h = ["bottom", "top"]) {
    if (part == str("col", i, "_", h)) half(i, h == "top");
    if (part == str("print_col", i, "_", h)) rotate([90, 0, 0]) half(i, h == "top");
}
for (k = ["leg", "mid", "leg_sd", "mid_left"], h = ["bottom", "top"]) {
    if (part == str("lid_", k, "_", h)) lid_half(k == "mid" || k == "mid_left", h == "top", k == "leg_sd");
    if (part == str("print_lid_", k, "_", h)) translate([0, 0, D]) rotate([-90, 0, 0]) lid_half(k == "mid" || k == "mid_left", h == "top", k == "leg_sd");
}

// ---------- checks ----------
echo(str("TARS4 ", 4 * D, " x ", D, " x ", H, " mm ; column ", col_w, " ; interior ", col_w - 2 * wall, " ; screen ", screen, ": ", kv(SCR, "desc")));
let(pd = (scr_pcb[0] + 2 * scr_clr - (col_w - 2 * wall)) / 2) if (pd > wall - 0.8)
    echo(str("WARNING: screen module ", scr_pcb[0], " mm needs ", pd, " mm wall pockets in a ", col_w - 2 * wall, " mm interior (raise D)"));
else if (pd > 0) echo(str("note: screen sits in ", pd, " mm pockets cut into the side walls"));
if (d1_z0 + d1[1] + 0.3 + 4 + 5 > mid_rows[1] - lid_boss_d / 2) echo("WARNING: controller lug runs into the lid screw row");
let(gd = d1[0] / 2 + d1_groove_clr - (col_w / 2 - wall)) if (gd > wall - 0.8)
    echo(str("WARNING: D1 mini grooves are ", gd, " mm deep, leaving less than 0.8 mm of wall"));
if (sound) {
    if (spk[0] + 2 * 2.3 > col_w - 2 * wall) echo("WARNING: speaker too wide for the side rails");
    if (spk_front_y + spk[1] + 0.3 > d1_lug_y) echo("WARNING: speaker runs into the controller lug on the middle lid");
    if (spk_z0 + spk[2] > mid_rows[1] - lid_boss_d / 2) echo("WARNING: speaker runs into the lid screw row");
    if (spk_z0 + spk[2] > seam_z[speaker_col] - splint_h / 2 - 0.5) echo("WARNING: speaker runs into the splint");
    if (spk_z0 + spk[2] - spk_pad < bottom_panel_z[0] + 2) echo("WARNING: speaker membrane hidden behind the front wall");
    if (amp_z0 + amp[1] > mid_rows[1] - lid_boss_d / 2 - 0.5) echo("WARNING: amplifier board runs into the lid screw posts");
}
if (amp_z0 + bb[1] > mid_rows[1] - lid_boss_d / 2 - 0.5 || bb[0] + 0.4 + 2 * rib > col_w - 2 * wall) {
    echo("WARNING: spare breakout slot runs into the lid screw posts / side walls");
}
if (battery) {
    if (fuse_z0 - rib < bat_z0 + 4 + 5) echo("WARNING: polyfuse taller than the room between the cradles");
    if (wall + fuse[2] + 0.3 > bat_y - (bat[0] + bat_clr) / 2) echo("WARNING: polyfuse thicker than the room in front of the cell");
    if (fuse[0] + 0.4 + 2 * rib > col_w - 2 * wall) echo("WARNING: polyfuse holder wider than the leg");
    echo(str("polyfuses on the inner front walls in front of the cells: z ", fuse_z0, " - ", fuse_z0 + fuse[1]));
}
if (bme) {
    if (bme_b[0] + 0.4 + 2 * rib > col_w - 2 * wall) echo("WARNING: weather sensor slot wider than the leg");
    if (bme_z0 + bme_b[1] + 0.3 + rib > leg_rows[3] - lid_boss_d / 2 - 0.3) echo("WARNING: weather sensor runs into the fourth leg screw row");
    if (wall + bme_b[2] + wire_room > lid_y) echo("WARNING: no wire room behind the weather sensor");
}
if (pir) {
    if (pir_top) { // cap skirt and breakout in the band; the sleeve may merge into the frame / post
        let(z0 = min(-pir_cap_d / 2, pir_pcb_fp[1]), z1 = max(pir_cap_d / 2, pir_pcb_fp[3]))
        if (pir_zc + z0 < scr_frame_top + 0.3 || pir_zc + z1 > top_boss_z0 - 0.3)
            echo("WARNING: motion sensor taller than the band between the screen frame and the top lid screw");
        let(cl = pir_x + min(-pir_cap_d / 2, pir_pcb_fp[0]) - tube_end_x,
            cr = col_w - wall - pivot_boss_l - pir_x - max(pir_cap_d / 2, pir_pcb_fp[2])) {
            if (min(cl, cr) < 0.5) echo("WARNING: motion sensor body runs into the middle tube's end / collar or the right tube's boss");
            echo(str("motion sensor at the top, x ", pir_x, " (", pir_x - col_w / 2, " right of the axis): ", cl,
                     " mm to the middle tube's end, ", cr, " mm to the right boss"));
        }
    } else {
        if (pir_zc + pir_sleeve_d / 2 > mid_rows[2] - lid_boss_d / 2 - 0.5 && pir_zc - pir_sleeve_d / 2 < mid_rows[2] + lid_boss_d / 2 + 0.5
            || pir_zc - pir_sleeve_d / 2 < mid_rows[1] + lid_boss_d / 2 + 0.5) echo("WARNING: motion sensor sleeve runs into the lid screw posts");
        if (pir_zc + pir_sleeve_d / 2 > scr_z - scr_pcb[1] / 2 - scr_clr - scr_frame_w - 0.5) echo("WARNING: motion sensor runs into the screen frame");
        if (sound && pir_col == speaker_col && pir_zc - pir_sleeve_d / 2 < amp_z0 + amp[1] + rib + 0.5) echo("WARNING: motion sensor runs into the amplifier slot");
    }
    if (pir_sleeve_d > col_w - 2 * wall) echo("WARNING: motion sensor sleeve wider than the column interior");
    if (pir_pcb_y0 + pir_pcb[1] + 4 > lid_y) echo("WARNING: motion sensor too deep: less than 4 mm left for the wires before the lid");
    if (pir_hole >= pir_cap_rim_d) echo("WARNING: motion sensor wall hole as wide as the cap rim: the dome falls through");
    if (pir_can_h - pir_can_fl > pir_cap_skirt + pir_cap_rim_t + pir_dome_h - 1) echo("WARNING: motion sensor can longer than its cap");
    echo(str("motion sensor: cap glued from the inside, dome flush in a ", pir_hole, " hole at z ", pir_zc, ", ring to ", pir_cap_y + 1,
             ", breakout from ", pir_pcb_y0, " to ", pir_pcb_y0 + pir_pcb[1], " mm behind it"));
    echo(str("motion sensor test plate (part pir_test), left to right: cap from the outside, then glued from the inside, ",
             [for (d = pir_test_holes) str("hole ", d, ": ", round(100 * (pir_dome_h - pir_dome_z(d) - wall)) / 100, " mm out")]));
}
if (hub) {
    if (hub_b[0] + 0.4 > col_w - 2 * wall) echo("WARNING: distribution board wider than the middle column interior");
    if (hub_y - 1.6 < wall + 6) echo("WARNING: less than 6 mm in front of the distribution boards for the wires");
    if (lid_y - (hub_y + hub_b[2]) < 2 * wire_room) echo(str("WARNING: less than ", 2 * wire_room, " mm behind the distribution boards (wires / connectors)"));
    if (wall + clr + 0.1 + scr_rib > scr_x - dp_w(8) / 2) echo("WARNING: screen lid ribs run into the screen connectors");
    if (hub_z0 + hub_b[1] + 4 > scr_z - scr_pcb[1] / 2 - scr_clr - scr_frame_w) echo("WARNING: distribution board / lid tab gussets run into the screen frame");
    if (hub_z0 - 4 < lid_seam_z[1]) echo("WARNING: distribution board runs into the middle lid split");
    if (pir && pir_top && hub_z0 + hub_b[1] > pir_zc - pir_sleeve_d / 2) echo("WARNING: distribution board runs into the motion sensor");
}
if (pp) {
    if (pp_b[0] + 0.4 > col_w - 2 * wall) echo("WARNING: power-path perfboard wider than the leg interior");
    if (lid_y - 0.3 - pp_b[1] - 0.2 < wall + 6) echo("WARNING: power-path perfboard too deep: less than 6 mm for the wires in front of it");
    if (pp_z0 + pp_b[2] + pp_parts + 2 > leg_rows[2] - lid_boss_d / 2) echo("WARNING: power-path perfboard parts run into the third leg screw row");
}
if (battery) {
    if (wall - charger_groove < 1) echo("WARNING: TP4056 board too wide: less than 1 mm of side wall left at its grooves");
    if (charger_groove > 0) echo(str("TP4056: edges in ", charger_groove, " mm grooves in the side walls (", wall - charger_groove,
                                     " mm left, ", wall - charger_groove - line_d, " under the vertical side line): keep its end pads / solder joints ",
                                     charger_groove + 0.1, " mm clear of the board ends"));
    if (lid_y - 0.3 - charger[1] - 0.2 < wall + 6) echo("WARNING: TP4056 board too deep: less than 6 mm for the wires in front of it");
    if (charger_z0 + charger[2] + charger_h + 3 > seam_z[power_col] - splint_h / 2) echo("WARNING: TP4056 runs into the leg splint");
    // PLAT-MECH-CHARGEPORT-001
    if (usbb_z0 + usbb[0] + 0.3 + rib > shelf_z - shelf_t) echo("WARNING: charge port breakout runs into the bottom contact shelf");
    if (usbb_y1 + usbb_out < D - 1) echo("WARNING: charge port mouth more than 1 mm inside the back face");
    if (usbb_y1 + usbb_out > D) echo("WARNING: charge port receptacle sticks out of the back face");
    if (usbb_zc < 6) echo("WARNING: charge port centre less than 6 mm above the floor (plug overmold on the table)");
    if (usbb_zc - usbb_rec[0] / 2 - 0.3 < wall + clr) echo("WARNING: charge port notch cuts the bottom edge of the lid");
    if (usbb_y0 - 0.2 - rib < wall + 4) echo("WARNING: charge port front stop leaves less than 4 mm for its wires");
}
if (buck) {
    if (bk[0] + 0.3 > col_w - 2 * wall) echo("WARNING: buck-boost board wider than the leg interior");
    if (bk_y1 - bk[1] - 0.2 < wall + 6) echo("WARNING: buck-boost board too deep: less than 6 mm for the wires in front of it");
    if (bk_z0 + bk[2] + 0.3 + rib + bk_h > seam_z[power_col] - splint_h / 2) echo("WARNING: buck-boost board runs into the leg splint");
    echo(str("power leg stack: buck-boost ", bk_z0, ", TP4056 ", charger_z0, " (", seam_z[power_col] - splint_h / 2 - charger_z0 - charger[2] - charger_h,
             " mm above its parts), power-path board ", pp_z0, ", microSD ", sd_z0));
    if (bk_z0 - rib < leg_rows[1] + lid_boss_d / 2) echo("WARNING: buck-boost grooves run into the lid screw posts");
}
if (sd_reader) {
    if (sd[0] + 0.4 > col_w - 2 * wall) echo("WARNING: microSD board wider than the leg interior");
    if (sd_y0 - 0.2 < wall + 3) echo("WARNING: microSD board too long: no front stop / wire room in front of it");
    if (sd_z0 - rib < leg_rows[1] + lid_boss_d / 2 || sd_card_z + sd_slot[1] / 2 > seam_z[sd_col] - splint_h / 2)
        echo("WARNING: microSD grooves run into the lid screw posts or the splint");
    if (sd_sock[0] / 2 + abs(sd_sock_dx) > sd[0] / 2 - sd_lip - 0.2) echo("WARNING: microSD socket under the groove lips");
    if (sd_card_z + sd_slot[1] / 2 > lid_seam_z[0] - 2) echo("WARNING: microSD lid slot too close to the leg lid split");
    let(out = sd_y1 + sd_sock_over + sd_card_out - (lid_y + wall))
        echo(str("microSD: latched card ends ", abs(out), out > 0 ? " mm out of" : " mm inside", " the lid's outer face; ",
                 sd_y0 - wall, " mm free in front of the board"));
}
// stability: plastic shell + lids (walls only), cells in the legs; tipping angle front/back when standing straight
let(shell = (2 * (col_w + D) * wall * H + 2 * col_w * D * wall) * pla_density,
    lidm = (col_w - 2 * wall) * wall * H * pla_density,
    m_col = shell + lidm, cells = battery ? 2 * cell_mass : 0,
    m = 4 * m_col + cells,
    zc = (4 * m_col * H / 2 + cells * (bat_z0 + bat[1] / 2)) / m)
    echo(str("stability: ~", round(m), " g, centre of gravity ~", round(zc), " mm high -> tips over past ~",
             round(atan((D / 2) / zc)), " deg front/back when standing straight (walking pose is much steadier)"));
for (i = [0:3]) let(L = max(seam_z[i], H - seam_z[i])) if (L > 200)
    echo(str("WARNING: column ", i, " half is ", L, " mm long"));
if (battery && bat_top_shelf_z + 1 > leg_rows[1] - lid_boss_d / 2)
    echo("WARNING: the cell runs into the leg lid screws");
if (switch_on && battery && sw_recess + sw_h + 3 > shelf_z - shelf_t)
    echo("WARNING: switch pins (+3 mm for the wires) run into the bottom contact shelf");
if (switch_on && (col_w / 2 - sw_body[0] / 2 - 1.2 < usbb_x0 + usbb[2] + max(usbb_rec[1], 1.2) + 0.5 || sw_y + sw_body[1] / 2 + 1.2 > lid_y - 0.5))
    echo("WARNING: switch pad runs into the charge port or the lid");
if (sensors) {
    if (rtc[0] + 0.4 + 2 * rib > col_w - 2 * wall) echo("WARNING: RTC slot too wide for the leg");
    if (acc_z0 + acc[1] + 1.5 > mid_rows[2] - lid_boss_d / 2) echo("WARNING: accelerometer runs into the lid screw row");
    if (rtc_z0 + rtc[1] + 0.3 + rib > seam_z[rtc_col] - splint_h / 2) echo("WARNING: RTC runs into the leg splint");
    if (rtc[2] + wire_room > lid_y - wall) echo("WARNING: RTC too thick, no room left for the wires behind it");
    if (mic_z0 + mic[1] + 0.3 + rib > hub_z0 - 0.3) echo("WARNING: microphone top stop runs into the distribution board");
    if (mic_z0 - 0.3 - rib < acc_z0 + acc[1] + 0.3 + rib) echo("WARNING: microphone runs into the accelerometer");
    if (mic[0] / 2 + 0.2 + rib > col_w / 2 - bx[0] - lid_boss_d / 2) echo("WARNING: microphone slot runs into the lid screw posts");
}
if (battery && contact[1] / 2 > lid_y - 0.5 - bat_y)
    echo("WARNING: contact plates stick out past the lid face");
