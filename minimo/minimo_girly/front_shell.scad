// ==============================================================================
//  MINIMO GIRLY EDITION - Part 4: Front Shell (1.3" OLED Edition)
//  Features:
//   - Clean aesthetic front casing with bear ears and smooth organic curves
//   - Angled visor aperture (12° back tilt) sized for 1.3" OLED Visor Frame
//   - Cute floral / circular speaker grille on the belly
//   - Dual keyed sockets on lower belly for snap-in Chubby Feet
//   - Top socket for Snap Bow with wire routing tunnel
//   - Internal M2 screw bosses (invisible fasteners from the back)
//   - Peripheral tongue-and-groove alignment lip (fit_tol = 0.25mm)
// ==============================================================================

include <minimo_girly_params.scad>

module front_ears() {
    for (side = [-1, 1]) {
        color("pink")
        translate([side * 19.5, -1.0, head_z + 20.0])
        rotate([side * -14, 18, 0]) {
            difference() {
                // Outer ear lobe
                scale([1.05, 0.65, 1.05])
                sphere(r = 10.5);

                // Inner ear soft hollow
                translate([0, -3.5, 0])
                scale([0.85, 0.55, 0.85])
                sphere(r = 8.5);

                // Trim back half beyond Y=0 parting line
                translate([0, 18, 0])
                cube([36, 36, 36], center = true);
            }
        }
    }
}

module speaker_belly_grille() {
    // Cute circular array on lower belly
    for (x = [-7 : 3.5 : 7]) {
        for (z = [-7 : 3.5 : 7]) {
            if (x*x + z*z <= 56) {
                translate([x, -body_r + 2.5, 16 + z])
                rotate([90, 0, 0])
                cylinder(r = 1.0, h = 10, center = true);
            }
        }
    }
}

module front_screw_bosses() {
    // 4 internal mounting bosses receiving M2 self-tapping screws from rear
    // Lower body bosses
    for (side = [-1, 1]) {
        translate([side * 20.0, 0, 14.0]) {
            difference() {
                cylinder(r = screw_boss_od / 2, h = 18.0, center = true);
                cylinder(d = screw_hole_d, h = 20.0, center = true);
            }
        }
        // Upper head bosses
        translate([side * 18.0, 0, head_z + 10.0]) {
            difference() {
                cylinder(r = screw_boss_od / 2, h = 16.0, center = true);
                cylinder(d = screw_hole_d, h = 18.0, center = true);
            }
        }
    }
}

module front_shell() {
    color([0.98, 0.85, 0.88]) // Soft Strawberry Milk Pink
    union() {
        difference() {
            union() {
                // Main outer body + head (front half)
                difference() {
                    union() {
                        // Chubby lower body
                        translate([0, 0, body_z])
                        scale([1.12, 1.0, 0.96])
                        sphere(r = body_r * 0.88);

                        // Cute head
                        translate([0, 0, head_z])
                        scale([1.08, 1.02, 1.0])
                        sphere(r = head_r);

                        // Base collar
                        translate([0, 0, 4.0])
                        cylinder(r1 = 20.0, r2 = 24.0, h = 8.0, center = true);
                    }

                    // Cut away rear half beyond split plane Y = 0
                    translate([0, 40, 35])
                    cube([120, 80, 120], center = true);
                }

                // Peripheral Male Alignment Tongue (inserts into rear shell groove)
                translate([0, 0.6, 0])
                difference() {
                    // Outer outline slightly inset by fit_tol
                    union() {
                        translate([0, 0, body_z])
                        scale([1.12, 1.0, 0.96])
                        sphere(r = (body_r * 0.88) - fit_tol);

                        translate([0, 0, head_z])
                        scale([1.08, 1.02, 1.0])
                        sphere(r = head_r - fit_tol);
                    }
                    // Inner hollow
                    union() {
                        translate([0, 0, body_z])
                        scale([1.12, 1.0, 0.96])
                        sphere(r = (body_r * 0.88) - wall_t - fit_tol);

                        translate([0, 0, head_z])
                        scale([1.08, 1.02, 1.0])
                        sphere(r = head_r - wall_t - fit_tol);
                    }
                    // Restrict tongue to parting plane zone
                    translate([0, -25, 35]) cube([120, 50, 120], center = true);
                    translate([0, 25 + lip_h, 35]) cube([120, 50, 120], center = true);
                }
            }

            // --- Internal Shell Hollow ---
            translate([0, 0, body_z])
            scale([1.12, 1.0, 0.96])
            sphere(r = (body_r * 0.88) - wall_t);

            translate([0, 0, head_z])
            scale([1.08, 1.02, 1.0])
            sphere(r = head_r - wall_t);

            // --- 1.3" Visor Aperture Cutout ---
            translate([0, -head_r + 4.5, head_z])
            rotate([-shell_tilt, 0, 0])
            cube([oled_pcb_w + 2*wall_t, 30.0, oled_pcb_h + 2*wall_t], center = true);

            // --- Speaker Grille Holes ---
            speaker_belly_grille();

            // --- Sockets for Snap-in Chubby Feet ---
            for (side = [-1, 1]) {
                translate([side * 17.0, -12.0, 5.0])
                cube([8.0 + fit_tol, 18.0, 8.0 + fit_tol], center = true);
            }

            // --- Top Socket for Snap Bow ---
            translate([0, 0, head_z + head_r])
            cylinder(d = 10.8, h = 8.0, center = true);

            // Wire routing hole for touch sensor
            translate([0, 0, head_z + head_r - 5.0])
            cylinder(d = ttp_wire_d + 1.0, h = 10.0, center = true);
        }

        // Add Ears
        front_ears();

        // Add Internal Screw Bosses
        front_screw_bosses();
    }
}

// Standalone render for printing
front_shell();
