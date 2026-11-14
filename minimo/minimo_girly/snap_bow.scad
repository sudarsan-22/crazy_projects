// ==============================================================================
//  MINIMO GIRLY EDITION - Part 1: Snap-Fit Bow & Touch Sensor Carrier
//  Features:
//   - Cute aesthetic ribbon bow printable in pastel pink/coral
//   - Underside pocket for TTP223 capacitive touch board (0.8mm sensing wall)
//   - Dual snap peg / key with central 4mm wire pass-through hole
// ==============================================================================

include <minimo_girly_params.scad>

module snap_bow(touch_pocket = true) {
    difference() {
        union() {
            // --- Bow Center Knot ---
            color("hotpink")
            rotate([90, 0, 0])
            scale([1.0, 1.25, 1.0])
            cylinder(r = 5.5, h = 10, center = true);

            // --- Left Ribbon Loop ---
            color("lightpink")
            translate([-10, 0, 1])
            rotate([5, 22, -10])
            scale([1.8, 0.9, 1.2])
            sphere(r = 6.2);

            // Left inner loop hollow/dent for ribbon look
            // (done in difference)

            // --- Right Ribbon Loop ---
            color("lightpink")
            translate([10, 0, 1])
            rotate([-5, -22, 10])
            scale([1.8, 0.9, 1.2])
            sphere(r = 6.2);

            // --- Ribbon Tails ---
            color("pink")
            translate([-5.5, -4, -8])
            rotate([25, 18, -12])
            scale([1.1, 0.45, 2.0])
            cylinder(r1=3.5, r2=1.8, h=7, center=true);

            color("pink")
            translate([5.5, -4, -8])
            rotate([25, -18, 12])
            scale([1.1, 0.45, 2.0])
            cylinder(r1=3.5, r2=1.8, h=7, center=true);

            // --- Snap-Fit Base Plug ---
            // Plugs into head shell socket
            color("deeppink")
            translate([0, 0, -6]) {
                cylinder(r = 5.2 - fit_tol, h = 6.0, center = false);
                // Snap retention barb
                translate([0, 0, 1.5])
                cylinder(r1 = 5.7 - fit_tol, r2 = 5.0 - fit_tol, h = 2.0, center = false);
            }
        }

        // Left ribbon hollow dent
        translate([-11, -1.5, 1])
        rotate([5, 22, -10])
        scale([1.2, 0.5, 0.8])
        sphere(r = 5.0);

        // Right ribbon hollow dent
        translate([11, -1.5, 1])
        rotate([-5, -22, 10])
        scale([1.2, 0.5, 0.8])
        sphere(r = 5.0);

        if (touch_pocket) {
            // TTP223 Sensor Pocket (recessed from base, leaves 0.8mm plastic roof)
            translate([0, 0, -3.0])
            cube([ttp_w + fit_tol, ttp_h + fit_tol, ttp_t + 2.0], center = true);

            // 3-Pin Touch Sensor Wire Routing Bore (leads straight down into head)
            translate([0, 0, -7])
            cylinder(d = ttp_wire_d, h = 10, center = true);
        }
    }
}

// Standalone render for printing
snap_bow();
