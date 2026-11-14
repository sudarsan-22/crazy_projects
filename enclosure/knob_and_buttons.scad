// ====================================================================
// ESP32 Music Controller - Studio Knurled Knob & Media Button Caps
// ====================================================================

$fn = 64;

// Premium Studio Knurled Knob
module knurled_knob() {
    knob_dia = 24.0;
    knob_h   = 15.0;
    shaft_dia = 6.1; // 6.0mm D-shaft with tolerance
    
    difference() {
        union() {
            // Main knob body
            cylinder(d=knob_dia, h=knob_h);
            // Lower skirt to hide mounting collar
            cylinder(d=knob_dia - 2.0, h=2.5);
        }
        
        // Chamfered top edge
        translate([0, 0, knob_h - 1.0])
            difference() {
                cylinder(d=knob_dia + 2, h=2);
                cylinder(d1=knob_dia, d2=knob_dia - 2.0, h=2);
            }
        
        // Grip knurling ridges around circumference
        for (i = [0:29]) {
            rotate([0, 0, i * (360/30)])
                translate([knob_dia/2, 0, -1])
                    cylinder(r=0.8, h=knob_h + 2);
        }
        
        // Precise D-Shaft Cavity
        translate([0, 0, -1])
            intersection() {
                cylinder(d=shaft_dia, h=11.5);
                translate([-shaft_dia/2, -shaft_dia/2, 0])
                    cube([shaft_dia, shaft_dia - 0.75, 11.5]);
            }
            
        // Top Indicator Notch / Line
        translate([0, knob_dia/2 - 4.5, knob_h - 1.2])
            cube([1.4, 4.0, 2.0], center=true);
    }
}

// Media Push Button Caps
module button_cap(is_prev=true) {
    cap_d = 7.8;
    cap_h = 7.5;
    flange_d = 10.0;
    
    difference() {
        union() {
            // Button stem
            cylinder(d=cap_d, h=cap_h);
            // Retaining flange
            cylinder(d=flange_d, h=1.5);
        }
        // Tactile switch plunger cavity
        translate([-2.2, -2.2, -0.5])
            cube([4.4, 4.4, 3.8]);
            
        // Top tactile concave dip for comfortable finger press
        translate([0, 0, cap_h + 8.5])
            sphere(r=9.0);
    }
}

// Layout for printing on Bambu A1 Mini
translate([0, 0, 0]) knurled_knob();
translate([24, 0, 0]) button_cap(true);
translate([38, 0, 0]) button_cap(false);
