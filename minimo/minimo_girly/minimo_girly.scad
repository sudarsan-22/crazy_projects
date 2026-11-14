// ==============================================================================
//  MINIMO GIRLY EDITION - Desktop Companion Enclosure
//  Parametric 3D printable desk pet enclosure with cute bow, visor, & PCB mounts
// ==============================================================================

$fn = 60;

// --- Dimensions & Parameters ---
body_radius     = 28;
body_height     = 48;
head_z_offset   = 36;
head_radius     = 26;

// OLED Display Window (0.96" SSD1306)
oled_w          = 26;
oled_h          = 15;
oled_frame_w    = 28;
oled_frame_h    = 28;
visor_tilt      = 12; // degrees back tilt

// Touch Sensor (TTP223)
ttp223_w        = 15.5;
ttp223_l        = 11.5;
ttp223_d        = 2.0;

// USB-C port
usbc_w          = 9.5;
usbc_h          = 3.6;

// Wall thickness
wall_t          = 2.2;

// --- Modules ---

// Cute Bow Module for Head
module hair_bow(scale_factor = 1.0) {
    scale([scale_factor, scale_factor, scale_factor]) {
        // Center knot
        color("hotpink")
        sphere(r = 4.5);
        
        // Left loop
        color("lightpink")
        translate([-7.5, 0, 0])
        rotate([0, 25, 0])
        scale([1.6, 0.9, 1.2])
        sphere(r = 5);

        // Right loop
        color("lightpink")
        translate([7.5, 0, 0])
        rotate([0, -25, 0])
        scale([1.6, 0.9, 1.2])
        sphere(r = 5);

        // Ribbon tails
        color("pink")
        translate([-4, -2, -6])
        rotate([20, 20, -15])
        scale([0.8, 0.4, 1.6])
        cylinder(r1=3, r2=1.5, h=6, center=true);

        color("pink")
        translate([4, -2, -6])
        rotate([20, -20, 15])
        scale([0.8, 0.4, 1.6])
        cylinder(r1=3, r2=1.5, h=6, center=true);
    }
}

// Bear Ears
module ear(side = 1) {
    color("pink")
    translate([side * 17, 0, head_z_offset + 18])
    rotate([side * -15, 20, 0]) {
        // Outer ear
        difference() {
            scale([1, 0.6, 1])
            sphere(r = 9.5);
            // Inner ear indent
            translate([0, -3.5, 0])
            scale([0.8, 0.5, 0.8])
            sphere(r = 7.5);
        }
    }
}

// Chubby Sitting Paws / Feet
module paw(side = 1) {
    color("lightpink")
    translate([side * 18, -20, 4])
    rotate([15, side * -10, side * 15]) {
        scale([1.1, 1.5, 0.85])
        sphere(r = 9);
        
        // Toe pad accents
        translate([0, -3, 6])
        scale([0.8, 1.0, 0.4])
        color("mistyrose")
        sphere(r = 4);
    }
}

// Visor Face Mask (Front Bezel)
module curved_visor() {
    color("black")
    translate([0, -head_radius + 4.5, head_z_offset])
    rotate([-visor_tilt, 0, 0]) {
        difference() {
            // Screen bubble outer
            scale([1.25, 0.55, 1.0])
            sphere(r = 18);
            
            // Cut flat back
            translate([0, 10, 0])
            cube([50, 20, 50], center=true);
            
            // OLED cutout
            translate([0, -5, 0])
            cube([oled_w, 20, oled_h], center=true);
        }
    }
}

// Speaker Grille on Belly
module speaker_grille() {
    for (x = [-6 : 3 : 6]) {
        for (z = [-6 : 3 : 6]) {
            if (x*x + z*z <= 40) {
                translate([x, -body_radius + 2, 14 + z])
                rotate([90, 0, 0])
                cylinder(r = 0.9, h = 6, center = true);
            }
        }
    }
}

// Main Outer Shell
module outer_shell() {
    color("mistyrose")
    union() {
        // Body (chubby pear shape)
        translate([0, 0, 18])
        scale([1.1, 1.0, 0.95])
        sphere(r = body_radius * 0.85);

        // Head
        translate([0, 0, head_z_offset])
        scale([1.08, 1.0, 0.98])
        sphere(r = head_radius);

        // Base flat transition
        translate([0, 0, 4])
        cylinder(r1 = 18, r2 = 22, h = 8, center = true);
    }
}

// Internal Electronics Cavity
module internal_cavity() {
    // Hollow body
    translate([0, 0, 16])
    scale([1.0, 0.9, 0.9])
    sphere(r = (body_radius * 0.85) - wall_t);

    // Hollow head
    translate([0, 0, head_z_offset])
    scale([0.98, 0.9, 0.92])
    sphere(r = head_radius - wall_t);

    // Bottom opening / access
    translate([0, 0, -1])
    cylinder(r = 16, h = 10, center = true);

    // USB-C port cutout at back
    translate([0, body_radius - 2, 8])
    cube([usbc_w, 10, usbc_h], center = true);

    // TTP223 touch sensor pocket inside top of head
    translate([0, 0, head_z_offset + head_radius - 3.5])
    cube([ttp223_w, ttp223_l, ttp223_d + 1], center = true);

    // Visor opening through shell
    translate([0, -head_radius + 2, head_z_offset])
    rotate([-visor_tilt, 0, 0])
    cube([oled_frame_w + 2, 18, oled_frame_h + 2], center=true);

    // Speaker grille holes
    speaker_grille();
}

// Full Assembly
module minimo_girly_assembly() {
    // Main Body Shell
    difference() {
        outer_shell();
        internal_cavity();
    }

    // Attached cute features
    ear(-1);
    ear(1);
    paw(-1);
    paw(1);

    // Cute Bow atop head (angled delightfully)
    translate([0, -2, head_z_offset + head_radius + 2])
    rotate([15, 0, 0])
    hair_bow(1.15);

    // Front Visor Screen Bezel
    curved_visor();
}

minimo_girly_assembly();
