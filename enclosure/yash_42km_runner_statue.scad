// ====================================================================
// YASH 42 KM Marathon Runner Statue (Exact Blueprint Match)
// Dimensions: <= 100mm Height, 60mm Base Diameter
// Features:
//  - Round pedestal with sweeping curved road ramp & dashed track line
//  - Curved rim inscriptions: "42 KM" (left side) & "YASH" (right side)
//  - Athletic runner in running tee & shorts in full sprint stride
// ====================================================================

$fn = 64;

// ---------------- 1. Sweeping Road Ramp Pedestal Base ----------------
module road_pedestal() {
    base_d = 58.0;
    base_h_front = 8.0;
    base_h_back  = 22.0;
    
    difference() {
        // Main Cylindrical Base sliced by an upward angled road plane
        intersection() {
            cylinder(d=base_d, h=base_h_back + 4);
            
            // Curved sloping ramp surface
            translate([0, 0, base_h_front])
                rotate([-18, 0, 0])
                    translate([-base_d, -base_d, 0])
                        cube([base_d*2, base_d*2, 35]);
        }
        
        // Engraved Inscription: "42 KM" (Front-Left Rim)
        rotate([0, 0, -28])
            translate([0, 0, 4.0])
                rotate([90, 0, -90])
                    linear_extrude(height=base_d/2 + 0.8)
                        text("42 KM", size=5.2, font="Liberation Sans:style=Bold", halign="center", valign="center");

        // Engraved Inscription: "YASH" (Front-Right Rim)
        rotate([0, 0, 32])
            translate([0, 0, 4.0])
                rotate([90, 0, -90])
                    linear_extrude(height=base_d/2 + 0.8)
                        text("YASH", size=5.6, font="Liberation Sans:style=Bold", halign="center", valign="center");
    }
    
    // Dashed Road / Finish Line Stripe
    for (i = [-2:3]) {
        translate([0, i * 7.5, base_h_front + 1.2 - i * 2.2])
            rotate([-18, 0, 0])
                cube([1.4, 4.5, 0.6], center=true);
    }
}

// ---------------- 2. Detailed Athletic Runner Figurine ----------------
module runner_man() {
    // Runner scale and forward athletic lean angle
    rotate([-14, 0, 0]) {
        
        // --- Head & Face ---
        translate([0, 6, 70]) {
            // Head
            scale([0.85, 1.05, 1.15]) sphere(r=4.6);
            // Jaw & Chin
            translate([0, 1.5, -2]) scale([0.7, 0.9, 0.8]) sphere(r=3.2);
            // Neck
            translate([0, -1, -4.5]) cylinder(r1=2.6, r2=2.4, h=4.8);
        }
        
        // --- Torso & Running T-Shirt ---
        // Upper Chest & Shoulders
        hull() {
            translate([0, 3, 62])
                scale([1.6, 1.1, 1.0]) sphere(r=5.5);
            translate([0, 0, 50])
                scale([1.3, 1.0, 1.0]) sphere(r=4.5);
        }
        // T-Shirt Short Sleeves
        translate([-6.5, 3, 62]) rotate([0, 25, 0]) cylinder(r1=2.6, r2=2.2, h=4.5);
        translate([6.5, 3, 62]) rotate([0, -25, 0]) cylinder(r1=2.6, r2=2.2, h=4.5);
        
        // --- Running Shorts & Pelvis ---
        hull() {
            translate([0, 0, 50])
                scale([1.3, 1.0, 1.0]) sphere(r=4.5);
            translate([0, -2, 42])
                scale([1.4, 1.1, 1.0]) sphere(r=4.8);
        }
        // Shorts leg openings
        translate([-3.2, 0, 40]) rotate([-10, 0, 0]) cylinder(r=3.0, h=3.0);
        translate([3.2, -3, 38]) rotate([25, 0, 0]) cylinder(r=3.0, h=3.0);

        // --- Left Arm (Bent at 90°, Driving Forward & Up) ---
        // Upper arm
        hull() {
            translate([7.5, 2, 61]) sphere(r=2.2);
            translate([10.5, 11, 52]) sphere(r=1.9);
        }
        // Forearm & Clenched Fist
        hull() {
            translate([10.5, 11, 52]) sphere(r=1.9);
            translate([4.5, 15, 60]) sphere(r=1.7);
            translate([4.0, 16, 62]) sphere(r=1.8);
        }

        // --- Right Arm (Driving Backwards) ---
        // Upper arm
        hull() {
            translate([-7.5, 2, 61]) sphere(r=2.2);
            translate([-10.0, -8, 52]) sphere(r=1.9);
        }
        // Forearm & Hand
        hull() {
            translate([-10.0, -8, 52]) sphere(r=1.9);
            translate([-7.5, -15, 46]) sphere(r=1.7);
        }

        // --- Forward Leading Leg (Left Leg - Knee High in Flight) ---
        // Thigh
        hull() {
            translate([3.2, -1, 40]) sphere(r=3.0);
            translate([3.6, 12, 33]) sphere(r=2.6);
        }
        // Calf & Shin
        hull() {
            translate([3.6, 12, 33]) sphere(r=2.6);
            translate([3.2, 8, 17])  sphere(r=2.1);
        }
        // Running Shoe (In flight)
        translate([3.2, 8, 17]) {
            hull() {
                sphere(r=2.0);
                translate([0, 5, -2]) scale([1, 1.6, 0.8]) sphere(r=2.0);
            }
        }

        // --- Rear Trailing Leg (Right Leg - Taking Off from Ramp) ---
        // Thigh
        hull() {
            translate([-3.2, -1, 40]) sphere(r=3.0);
            translate([-3.5, -12, 30]) sphere(r=2.6);
        }
        // Calf extending back down to ramp
        hull() {
            translate([-3.5, -12, 30]) sphere(r=2.6);
            translate([-3.5, -21, 16]) sphere(r=2.3);
            translate([-3.5, -23, 8])  sphere(r=2.2);
        }
        // Rear Running Shoe grounded on ramp
        translate([-3.5, -23, 8]) {
            rotate([28, 0, 0])
                hull() {
                    sphere(r=2.2);
                    translate([0, -5, -2]) scale([1, 1.7, 0.9]) sphere(r=2.0);
                }
        }
    }
}

// ---------------- 3. Complete Statue Assembly ----------------
module yash_marathon_statue() {
    road_pedestal();
    runner_man();
}

yash_marathon_statue();
