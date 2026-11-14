// ==============================================================================
//  MINIMO GIRLY EDITION - Part 2: Chubby Sitting Feet & Paws (Updated Scale)
//  Features:
//   - Cute forward-facing chubby feet with 3 toe lobes (matching reference desk toy)
//   - Dual keyed alignment pegs (8.0 x 8.0mm) for wobble-free snap/glue into front shell
//   - Flat desktop contact surface with stable 3-point posture
//   - Prints flat with zero supports required
// ==============================================================================

include <minimo_girly_params.scad>

module single_foot(side = 1) {
    mirror([side == -1 ? 1 : 0, 0, 0]) {
        union() {
            // Main chubby foot sole
            difference() {
                union() {
                    // Center foot pad
                    translate([17, -20, 5.5])
                    scale([1.1, 1.4, 0.75])
                    sphere(r = 10.0);

                    // Left toe bump
                    translate([11, -29, 6.5])
                    scale([0.9, 1.1, 0.7])
                    sphere(r = 5.8);

                    // Center toe bump (largest)
                    translate([17, -31, 7.0])
                    scale([0.95, 1.15, 0.75])
                    sphere(r = 6.4);

                    // Right toe bump
                    translate([23, -29, 6.5])
                    scale([0.9, 1.1, 0.7])
                    sphere(r = 5.8);
                }

                // Flat bottom cut (for rock-solid desktop adhesion & zero support needed)
                translate([17, -22, -5])
                cube([45, 45, 10], center = true);
            }

            // Keyed Alignment Mounting Peg (inserts into front shell socket)
            translate([17, -11, 5.0])
            rotate([0, 0, 0]) {
                // Peg shaft
                translate([0, 3.0, 0])
                cube([8.0 - fit_tol, 7.0, 8.0 - fit_tol], center = true);

                // Lead-in chamfer for easy push-fit
                translate([0, 6.5, 0])
                scale([1, 0.6, 1])
                rotate([0, 45, 0])
                cube([6.0 - fit_tol, 3.5, 6.0 - fit_tol], center = true);
            }
        }
    }
}

module feet_and_paws_pair() {
    color("peachpuff") {
        single_foot(1);   // Right foot
        single_foot(-1);  // Left foot
    }
}

// Standalone render for printing plate
feet_and_paws_pair();
