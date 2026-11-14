// ==============================================================================
//  MINIMO GIRLY EDITION - Part 5: Rear Shell (Electronics Backbone)
//  Components Housed:
//   - DFRobot Beetle ESP32-C3 on raised rails (with bottom wiring clearance)
//   - Rear USB-C Charging Port (with 45° cable relief)
//   - Rear Power Slide Switch pocket (standard SS12D00 / SS12F44)
//   - 1S LiPo Battery Cradle (400-600mAh, 27x38x7.5mm)
//   - 4x Countersunk M2 screw holes (fastens securely from back into front shell)
//   - Peripheral female alignment groove
// ==============================================================================

include <minimo_girly_params.scad>

module rear_ears() {
    for (side = [-1, 1]) {
        color("pink")
        translate([side * 19.5, 0, head_z + 20.0])
        rotate([side * -14, 18, 0]) {
            difference() {
                scale([1.05, 0.65, 1.05])
                sphere(r = 10.5);

                // Trim front half before Y=0
                translate([0, -18, 0])
                cube([36, 36, 36], center = true);
            }
        }
    }
}

module esp32_beetle_rails() {
    // Sits in lower torso behind USB-C port
    translate([0, 12.0, 7.5]) {
        difference() {
            // Raised rail block
            cube([beetle_w + 2*wall_t, beetle_l + 2.0, beetle_rail_h + 3.0], center = true);

            // Beetle PCB pocket
            translate([0, 0, 1.5])
            cube([beetle_w + fit_tol, beetle_l + fit_tol + 2.0, beetle_rail_h + 2.0], center = true);

            // Central wiring clearance channel under PCB
            cube([beetle_w - 6.0, beetle_l + 10.0, 10.0], center = true);
        }

        // Side retention clips
        for (sx = [-1, 1]) {
            translate([sx * (beetle_w/2 + 0.5), 0, beetle_rail_h/2 + 1.2])
            cube([1.0, 6.0, 1.2], center = true);
        }
    }
}

module lipo_battery_cradle() {
    // Mid-torso battery pocket
    translate([0, 12.0, 29.0]) {
        difference() {
            // Pocket walls
            cube([bat_w + 2*1.8, 10.0, bat_l * 0.75], center = true);

            // Battery slot (27 x 7.5 x 38mm)
            cube([bat_w + loose_tol, bat_h + loose_tol, bat_l], center = true);

            // Wire routing cutout at bottom of pocket
            translate([0, 0, -12])
            cube([12.0, 15.0, 8.0], center = true);
        }
    }
}

module rear_power_switch_mount() {
    // Mount positioned above the USB-C port on the rear wall
    translate([0, body_r * 0.88 - 2.0, 18.0]) {
        difference() {
            // Internal support housing
            cube([switch_w + 2*wall_t, 8.0, switch_h + 2*wall_t], center = true);

            // Switch body retention pocket
            translate([0, -1.0, 0])
            cube([switch_w + fit_tol, switch_d + 2.0, switch_h + fit_tol], center = true);

            // Actuator slider slot through rear wall
            translate([0, 4.0, 0])
            cube([switch_travel + switch_knob_w, 10.0, switch_knob_h + fit_tol], center = true);
        }

        // Snap retaining tabs for switch body
        for (sx = [-1, 1]) {
            translate([sx * (switch_w/2 + 0.5), -2.0, 0])
            cube([0.8, 2.0, switch_h - 1.0], center = true);
        }
    }
}

module rear_countersunk_screw_holes() {
    // 4 countersunk screw holes aligned with front shell bosses
    // Lower body
    for (side = [-1, 1]) {
        translate([side * 20.0, 0, 14.0]) {
            rotate([90, 0, 0]) {
                cylinder(d = 2.4, h = 45.0, center = true); // M2 clearance
                translate([0, 0, 14.0])
                cylinder(d1 = 2.4, d2 = screw_head_d + 0.4, h = 3.0, center = true); // countersink
                translate([0, 0, 18.0])
                cylinder(d = screw_head_d + 0.4, h = 8.0, center = true);
            }
        }
        // Upper head
        translate([side * 18.0, 0, head_z + 10.0]) {
            rotate([90, 0, 0]) {
                cylinder(d = 2.4, h = 45.0, center = true); // M2 clearance
                translate([0, 0, 17.0])
                cylinder(d1 = 2.4, d2 = screw_head_d + 0.4, h = 3.0, center = true);
                translate([0, 0, 21.0])
                cylinder(d = screw_head_d + 0.4, h = 8.0, center = true);
            }
        }
    }
}

module rear_shell() {
    color([0.96, 0.82, 0.85]) // Soft Strawberry Milk Pink (Rear)
    union() {
        difference() {
            union() {
                // Main outer body + head (rear half)
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

                        // Flat sitting base collar
                        translate([0, 6.0, 2.0])
                        cylinder(r = 22.0, h = 4.0, center = true);
                    }

                    // Cut away front half before split plane Y = 0
                    translate([0, -40, 35])
                    cube([120, 80, 120], center = true);

                    // Flatten base completely at Z <= 0
                    translate([0, 0, -30])
                    cube([120, 120, 60], center = true);
                }
            }

            // --- Internal Shell Hollow ---
            translate([0, 0, body_z])
            scale([1.12, 1.0, 0.96])
            sphere(r = (body_r * 0.88) - wall_t);

            translate([0, 0, head_z])
            scale([1.08, 1.02, 1.0])
            sphere(r = head_r - wall_t);

            // --- Female Alignment Groove (receives front shell tongue) ---
            difference() {
                union() {
                    translate([0, 0, body_z])
                    scale([1.12, 1.0, 0.96])
                    sphere(r = (body_r * 0.88) - fit_tol);

                    translate([0, 0, head_z])
                    scale([1.08, 1.02, 1.0])
                    sphere(r = head_r - fit_tol);
                }
                union() {
                    translate([0, 0, body_z])
                    scale([1.12, 1.0, 0.96])
                    sphere(r = (body_r * 0.88) - wall_t - fit_tol);

                    translate([0, 0, head_z])
                    scale([1.08, 1.02, 1.0])
                    sphere(r = head_r - wall_t - fit_tol);
                }
                // Groove depth restriction
                translate([0, 22 + lip_h + fit_tol, 35]) cube([120, 44, 120], center = true);
                translate([0, -22, 35]) cube([120, 44, 120], center = true);
            }

            // --- Rear USB-C Port Cutout ---
            translate([0, body_r * 0.88 - 1.0, 8.0]) {
                cube([usbc_w, 24.0, usbc_h], center = true);
                // 45 deg outer chamfer for bulky cable relief
                translate([0, 4.0, 0])
                rotate([0, 45, 0])
                cube([usbc_w + 3.2, 10.0, usbc_w + 3.2], center = true);
            }

            // --- Rear Power Switch Slot Cutout ---
            translate([0, body_r * 0.88 - 1.0, 18.0]) {
                cube([switch_travel + switch_knob_w, 24.0, switch_knob_h + loose_tol], center = true);
            }

            // --- Countersunk Screw Holes ---
            rear_countersunk_screw_holes();

            // --- Top Socket Half for Snap Bow ---
            translate([0, 0, head_z + head_r])
            cylinder(d = 10.8, h = 8.0, center = true);
        }

        // Add Ears
        rear_ears();

        // Add Internal Electronics Mounts
        esp32_beetle_rails();
        lipo_battery_cradle();
        rear_power_switch_mount();
    }
}

// Standalone render for printing
rear_shell();
