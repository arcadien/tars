include <../tars4.scad>
J = 0;
// side sections for tools/column_sections.py: one object per run, I = column, K = part; col / lid / ins are cut
// in the mid plane, the modules are drawn as side silhouettes. Seen from the left of TARS: (y, z) -> 2D (x, y).
module obj(i, k) {
    if (k == "col") column(i);
    if (k == "lid") lid(col_mid[i], sd_reader && i == sd_col, i != sensor_col);
    if (k == "ins" && col_mid[i]) inserts(sound && i == speaker_col);
    if (k == "tube") for (z = pivot_z) translate([0, D / 2, z]) rotate([0, 90, 0]) cylinder(d = tube_od, h = col_w);
    if (k == "env") envelopes(i);
    if (k == "conn" && plugs && CONN[J][0] == i) conn_box(J);
    if (k == "fuse" && !col_mid[i] && battery) translate([col_w / 2 - fuse[0] / 2, wall + wire_slot[1] + 0.5, fuse_z0]) cube(fuse);
    if (col_mid[i]) {
        if (k == "screen") translate([scr_x - scr_pcb[0] / 2, wall, scr_z - scr_pcb[1] / 2]) cube([scr_pcb[0], scr_t, scr_pcb[1]]);
        if (k == "s3" && i == 1) { translate([d1_x - d1[0] / 2, d1_back_y - d1_pcb_t, d1_z0]) cube([d1[0], d1_pcb_t, d1[1]]);
            translate([d1_x - 4.5, d1_back_y - d1_pcb_t - d1_usb_h, d1_z0]) cube([9, d1_usb_h, 7.5]); }
        if (k == "sock" && i == 1 && s3_socket) for (m = [0, 1]) translate([m ? d1_x + d1[0] / 2 - s3_sock[0] : d1_x - d1[0] / 2, d1_back_y, d1_z0 + 7.9 - 1.27])
            cube([s3_sock[0], s3_pin_base + s3_sock_h, s3_sock[1]]);
        if (k == "carrier" && i == 1 && s3_socket) translate([d1_x - d1[0] / 2, carrier_back_y - s3_carrier_t, d1_z0]) cube([d1[0], s3_carrier_t, d1[1]]);
        if (k == "spk" && sound && i == speaker_col) translate([col_w / 2 - spk[0] / 2, spk_front_y, spk_z0]) cube(spk);
        if (k == "amp" && sound && i == speaker_col) translate([col_w / 2 - amp[0] / 2, wall + pcb_gap, amp_z0]) cube([amp[0], amp[2], amp[1]]);
        if (k == "acc" && sensors && i == sensor_col) translate([col_w / 2 - acc[0] / 2, wall + pcb_gap, acc_z0]) cube([acc[0], acc[2], acc[1]]);
        if (k == "mic" && sensors && i == sensor_col) translate([col_w / 2 - mic[0] / 2, wall, mic_z0]) cube([mic[0], mic[2], mic[1]]);
        if (k == "pir" && pir && i == pir_col) pir_dummy();
        if (k == "hub" && hub) translate([col_w / 2 - hub_b[0] / 2, hub_y, hub_z0]) cube([hub_b[0], hub_b[2], hub_b[1]]);
    } else {
        if (k == "cell" && battery) translate([col_w / 2, bat_y, bat_z0]) cylinder(d = bat[0], h = bat[1]);
        if (k == "contact" && battery) for (z = [shelf_z, bat_top_shelf_z - contact[2]]) translate([col_w / 2 - contact[0] / 2, bat_y - contact[1] / 2, z]) cube(contact);
        if (k == "tp" && battery && i == power_col) translate([col_w / 2 - charger[0] / 2, lid_y - 0.3 - charger[1], charger_z0]) cube([charger[0], charger[1], charger[2] + charger_h]);
        if (k == "usb" && battery && i == power_col) translate([col_w / 2 - usbb[0] / 2, wall + pcb_gap, usbb_z0]) cube([usbb[0], usbb[2], usbb[1]]);
        if (k == "sd" && sd_reader && i == sd_col) { translate([col_w / 2 - sd[0] / 2, sd_y0, sd_z0]) cube([sd[0], sd[1], sd[2]]);
            translate([col_w / 2 + sd_sock_dx - sd_sock[0] / 2, sd_y1 + sd_sock_over - sd_sock[1], sd_z0 + sd[2]]) cube(sd_sock); }
        if (k == "buck" && buck && i == power_col) translate([col_w / 2 - bk[0] / 2, bk_y1 - bk[1], bk_z0]) cube([bk[0], bk[1], bk[2] + bk_h]);
        if (k == "pp" && pp && i == power_col) translate([col_w / 2 - pp_b[0] / 2, lid_y - 0.3 - pp_b[1], pp_z0]) cube([pp_b[0], pp_b[1], pp_b[2] + pp_parts]);
        if (k == "sw" && switch_on && i == power_col) translate([col_w / 2, sw_y, sw_recess]) translate([-sw_body[0] / 2, -sw_body[1] / 2, 0]) cube([sw_body[0], sw_body[1], sw_h]);
        if (k == "rtc" && sensors && i == rtc_col) translate([col_w / 2 - rtc[0] / 2, wall, rtc_z0]) cube([rtc[0], rtc[2], rtc[1]]);
        if (k == "bme" && bme && i == bme_col) translate([col_w / 2 - bme_b[0] / 2, wall, bme_z0]) cube([bme_b[0], bme_b[2], bme_b[1]]);
    }
}
// room kept free for the wires: behind every board standing on the front wall (wire_room), on both sides of the
// distribution boards, above the flat boards' components (up to stack_gap)
module envelopes(i) {
    module behind(b, y, z0) translate([col_w / 2 - b[0] / 2, y, z0]) cube([b[0], wire_room, b[1]]);
    if (col_mid[i]) {
        if (sound && i == speaker_col) behind(amp, wall + pcb_gap + amp[2], amp_z0);
        if (sensors && i == sensor_col) { behind(acc, wall + pcb_gap + acc[2], acc_z0); behind(mic, wall + mic[2], mic_z0); }
        if (hub) translate([col_w / 2 - hub_b[0] / 2, 0, hub_z0]) {
            translate([0, hub_y - 6, 0]) cube([hub_b[0], 6, hub_b[1]]);
            translate([0, hub_y + hub_b[2], 0]) cube([hub_b[0], 2 * wire_room, hub_b[1]]);
        }
    } else {
        if (sensors && i == rtc_col) behind(rtc, wall + rtc[2], rtc_z0);
        if (bme && i == bme_col) behind(bme_b, wall + bme_b[2], bme_z0);
        if (battery && i == power_col) {
            behind(usbb, wall + pcb_gap + usbb[2], usbb_z0);
            for (p = [[bk, bk_z0 + bk[2] + bk_h, bk_y1 - bk[1]], [charger, charger_z0 + charger[2] + charger_h, lid_y - 0.3 - charger[1]],
                      [pp_b, pp_z0 + pp_b[2] + pp_parts, lid_y - 0.3 - pp_b[1]]])
                translate([col_w / 2 - p[0][0] / 2, p[2], p[1]]) cube([p[0][0], p[0][1], stack_gap - 1]);
        }
    }
}
M = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, -col_w / 2], [0, 0, 0, 1]];   // (y, z, x - mid) : seen from the left
module flat(i, k, cut) {
    if (cut) projection(cut = true) multmatrix(M) obj(i, k);
    else projection() multmatrix(M) obj(i, k);
}
flat(I, K, CUT);
