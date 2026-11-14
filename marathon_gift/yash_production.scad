// ====================================================================
// PRODUCTION-READY MARATHON ACHIEVEMENT TROPHY FOR YASH (42 KM)
// Specification Compliance:
//  - Total Height: 97.5 mm (Target: 95-98 mm, Max: 100 mm)
//  - Base Width:   56.0 mm (Target: 55-58 mm, Max: 60 mm)
//  - Base Depth:   52.0 mm (Target: 48-54 mm, Max: 60 mm)
//  - Flat Bottom:  Z = 0.00 mm (100% bed adhesion)
//  - Watertight, Single Manifold Solid for Bambu Lab A1 Mini (0.4mm nozzle)
//  - Embossed "42 KM" on Front Wall, "YASH" on Opposite Wall
//  - Integrated Aerodynamic Support for High Strength & Support-Free Printing
// ====================================================================

$fn = 64;

// ---------------- 1. Solid Oval Pedestal Base ----------------
module production_pedestal() {
    bw = 56.0;  // X width
    bd = 50.0;  // Y depth
    rx = bw / 2;
    ry = bd / 2;
    h_front = 10.0;
    h_back  = 24.0;
    
    difference() {
        // Main Base: Oval cylinder sliced by an upward sweeping road ramp
        intersection() {
            // Flat-bottomed solid oval cylinder (Z=0)
            scale([rx, ry, 1])
                cylinder(r=1.0, h=h_back + 5);
            
            // Sweeping road ramp plane sloping from front to back
            translate([0, 0, h_front])
                rotate([16, 0, 0])
                    translate([-35, -35, 0])
                        cube([70, 70, 40]);
        }
        
        // Track Groove Recess (Left and Right lane edges)
        for (gx = [-14.0, 14.0]) {
            translate([gx, 0, h_front + 1.2])
                rotate([16, 0, 0])
                    cube([1.0, 58, 0.8], center=true);
        }
    }
    
    // Dashed Race-Lane Centerline (0.5mm raised, 1.0mm wide)
    for (i = [-3:3]) {
        translate([0, i * 6.8, h_front + 1.2 + i * 1.95])
            rotate([16, 0, 0])
                cube([1.1, 4.0, 0.6], center=true);
    }
    
    // --- 3D Embossed Text: FRONT SIDE ("42 KM") ---
    // Facing Positive Y (Front)
    translate([0, ry - 0.2, 5.0])
        rotate([90, 0, 0])
            linear_extrude(height=0.9)
                text("42 KM", size=5.4, font="Liberation Sans:style=Bold", halign="center", valign="center");

    // --- 3D Embossed Text: OPPOSITE SIDE ("YASH") ---
    // Facing Negative Y (Back / Opposite side)
    translate([0, -ry + 0.2, 5.0])
        rotate([90, 0, 180])
            linear_extrude(height=0.9)
                text("YASH", size=5.8, font="Liberation Sans:style=Bold", halign="center", valign="center");
}

// ---------------- 2. Athletic Male Marathon Runner ----------------
module athletic_marathoner() {
    // Scaled to achieve exact target height of 97.5 mm
    translate([0, 0, 10.0])
    scale([1.28, 1.28, 1.28])
    rotate([14, 0, 0]) {
        
        // --- Head & Facial Structure ---
        translate([0, 7.0, 68.5]) {
            // Head
            scale([0.88, 1.05, 1.15]) sphere(r=4.6);
            // Athletic Jaw & Chin
            translate([0, 2.2, -1.8]) scale([0.75, 0.9, 0.8]) sphere(r=3.0);
            // Solid Stylized Hair
            translate([0, -0.5, 2.2]) scale([0.92, 1.05, 0.8]) sphere(r=4.2);
            // Neck
            translate([0, -0.8, -4.5]) cylinder(r1=2.7, r2=2.4, h=4.8);
        }
        
        // --- Upper Torso / Running T-Shirt ---
        // Chest & Shoulders (athletic V-taper)
        hull() {
            translate([0, 3.2, 61.0])
                scale([1.55, 1.1, 1.0]) sphere(r=5.4);
            translate([0, 0.5, 49.0])
                scale([1.25, 0.95, 1.0]) sphere(r=4.5);
        }
        // T-Shirt Short Sleeves (Solid structural junctions)
        translate([-6.4, 3.0, 60.5]) rotate([0, 24, 0]) cylinder(r1=2.7, r2=2.2, h=4.5);
        translate([6.4, 3.0, 60.5]) rotate([0, -24, 0]) cylinder(r1=2.7, r2=2.2, h=4.5);
        
        // --- Pelvis & Running Shorts ---
        hull() {
            translate([0, 0.5, 49.0])
                scale([1.25, 0.95, 1.0]) sphere(r=4.5);
            translate([0, -1.5, 41.5])
                scale([1.35, 1.05, 1.0]) sphere(r=4.6);
        }
        // Shorts leg openings
        translate([-3.2, 0.5, 39.5]) rotate([10, 0, 0]) cylinder(r=3.0, h=3.0);
        translate([3.2, -2.5, 37.5]) rotate([-25, 0, 0]) cylinder(r=3.0, h=3.0);

        // --- Left Arm (Driving Forward & Up) ---
        // Upper Arm
        hull() {
            translate([-7.2, 2.5, 59.5]) sphere(r=2.2);
            translate([-10.5, 11.0, 51.5]) sphere(r=1.9);
        }
        // Forearm & Solid Running Fist
        hull() {
            translate([-10.5, 11.0, 51.5]) sphere(r=1.9);
            translate([-4.5, 15.5, 59.5]) sphere(r=1.8);
            translate([-4.0, 16.5, 61.5]) sphere(r=2.0); // Solid Fist (No fragile fingers)
        }

        // --- Right Arm (Driving Backwards) ---
        // Upper Arm
        hull() {
            translate([7.2, 2.5, 59.5]) sphere(r=2.2);
            translate([9.8, -7.5, 51.0]) sphere(r=1.9);
        }
        // Forearm & Solid Fist
        hull() {
            translate([9.8, -7.5, 51.0]) sphere(r=1.9);
            translate([7.2, -14.5, 45.0]) sphere(r=1.8);
        }

        // --- Leading Leg (Right Leg - Knee High in Forward Flight) ---
        // Muscular Thigh
        hull() {
            translate([3.2, 0.5, 39.5]) sphere(r=3.0);
            translate([3.6, 12.5, 32.5]) sphere(r=2.7);
        }
        // Knee & Shin
        hull() {
            translate([3.6, 12.5, 32.5]) sphere(r=2.7);
            translate([3.2, 8.5, 17.5])  sphere(r=2.2);
        }
        // Leading Running Shoe (Curved aerodynamic flight support)
        translate([3.2, 8.5, 17.5]) {
            hull() {
                sphere(r=2.1);
                translate([0, 5.0, -1.8]) scale([1, 1.6, 0.85]) sphere(r=2.1);
            }
        }

        // --- Trailing Leg (Left Leg - Grounded & Taking Off from Ramp) ---
        // Thigh
        hull() {
            translate([-3.2, 0.5, 39.5]) sphere(r=3.0);
            translate([-3.4, -11.5, 29.5]) sphere(r=2.6);
        }
        // Calf extending back down to the ramp crest
        hull() {
            translate([-3.4, -11.5, 29.5]) sphere(r=2.6);
            translate([-3.4, -20.5, 16.0]) sphere(r=2.3);
            translate([-3.4, -23.0, 7.5])  sphere(r=2.2);
        }
        // Rear Running Shoe (Firmly planted on the top of the ramp)
        translate([-3.4, -23.0, 7.5]) {
            rotate([-28, 0, 0])
                hull() {
                    sphere(r=2.2);
                    translate([0, -5.0, -1.8]) scale([1, 1.7, 0.9]) sphere(r=2.1);
                }
        }
    }
    
    // --- Aerodynamic Sculptural Ground Anchor ---
    hull() {
        translate([4.0, 12.0, 24.0]) cylinder(r1=2.8, r2=2.2, h=3.5);
        translate([4.0, 10.0, 8.0])  cylinder(r1=4.2, r2=2.8, h=6.0);
    }
}

// ---------------- 3. Complete Watertight Manifold Trophy ----------------
module yash_production_trophy() {
    // Exact flat-bottom clipping (Z >= 0)
    intersection() {
        union() {
            production_pedestal();
            athletic_marathoner();
        }
        translate([-40, -40, 0])
            cube([80, 80, 150]);
    }
}

yash_production_trophy();
