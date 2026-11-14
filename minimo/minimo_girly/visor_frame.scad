// ==============================================================================
//  MINIMO GIRLY EDITION - Part 3: 1.3" OLED Visor Frame & Display Holder
//  Features:
//   - Sleek curved glossy face visor sized for standard 1.3" I2C OLED (SH1106/SSD1306)
//   - Dedicated internal carrier pocket for 35.6mm x 33.8mm PCB
//   - 4x M2 mounting corner boss standoffs (30.5mm x 28.5mm pitch) + snap tabs
//   - Viewing aperture (30.0 x 16.0mm) exposing glowing active pixels cleanly
//   - Peripheral stepped mounting flange locks flush into Front Shell
//   - I2C 4-pin header wire channel
// ==============================================================================

include <minimo_girly_params.scad>

module visor_frame() {
    color([0.08, 0.08, 0.10]) // Glossy Piano Black
    difference() {
        union() {
            // --- Outer Curved Visor Dome ---
            difference() {
                // Curved frontal dome
                scale([1.22, 0.62, 1.05])
                sphere(r = head_r * 0.76);

                // Trim rear half
                translate([0, 25, 0])
                cube([80, 50, 80], center = true);

                // Flat back reference face
                translate([0, 1.5, 0])
                cube([80, 10, 80], center = true);
            }

            // --- Peripheral Alignment Mounting Flange ---
            // Seats into the front shell window cutout
            translate([0, -0.6, 0])
            difference() {
                cube([oled_pcb_w + 2*wall_t - 0.8, 4.0, oled_pcb_h + 2*wall_t - 0.8], center = true);
                translate([0, -1, 0])
                cube([oled_pcb_w + fit_tol, 8.0, oled_pcb_h + fit_tol], center = true);
            }
        }

        // --- 1.3" OLED Glass Viewing Aperture ---
        // Exposes active glowing pixels only
        translate([0, -10, oled_glass_z_off])
        cube([oled_glass_w, 35, oled_glass_h], center = true);

        // --- 1.3" OLED PCB Retention Pocket ---
        // Sized 35.6 x 33.8mm snugly
        translate([0, 1.4, 0])
        cube([oled_pcb_w + fit_tol, 5.0, oled_pcb_h + fit_tol], center = true);

        // --- I2C 4-Pin Header Clearance (Top/Bottom) ---
        translate([0, 1.4, (oled_pcb_h/2) + 1.2])
        cube([16.0, 8.0, 5.0], center = true);

        // --- 4x Corner M2 Screw / Pin Clearance Holes (30.5 x 28.5mm pitch) ---
        for (sx = [-1, 1]) {
            for (sz = [-1, 1]) {
                translate([sx * (oled_mount_x / 2), 0, sz * (oled_mount_y / 2)])
                rotate([90, 0, 0])
                cylinder(d = 2.2, h = 12.0, center = true);
            }
        }
    }

    // --- 4 Corner Snap Clips for Toolless Installation ---
    color([0.14, 0.14, 0.16]) {
        for (sx = [-1, 1]) {
            for (sz = [-1, 1]) {
                translate([sx * (oled_pcb_w/2 - 1.2), 2.4, sz * (oled_pcb_h/2 - 1.2)])
                rotate([0, 0, sx * 45])
                cube([2.2, 0.9, 2.2], center = true);
            }
        }
    }
}

// Standalone render for printing
visor_frame();
