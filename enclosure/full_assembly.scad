// ====================================================================
// ESP32 Music Controller - Ultra Spacious Assembly Preview (125x90mm)
// ====================================================================

use <top_cover.scad>
use <bottom_base.scad>
use <knob_and_buttons.scad>

tilt_ang = atan((52 - 28) / 90); // ~15 deg

// Bottom Base Plate
color([0.22, 0.23, 0.26])
    ultra_bottom_base();

// Top Wedge Console Housing
color([0.15, 0.16, 0.18], 0.95)
    translate([0, 0, 10])
        ultra_top_cover();

// Studio Volume Knob & Media Buttons
color([0.95, 0.55, 0.12]) {
    translate([0, 0, 10 + 28])
    rotate([tilt_ang, 0, 0]) {
        translate([94, 54, 10])
            knurled_knob();
        translate([38, 22, 5])
            button_cap();
        translate([94, 22, 5])
            button_cap();
    }
}
