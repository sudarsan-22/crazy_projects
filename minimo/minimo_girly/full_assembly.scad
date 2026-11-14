// ==============================================================================
//  MINIMO GIRLY EDITION - Full Assembly & Exploded View (1.3" OLED Edition)
//  Components:
//   1. Front Shell (Pastel Pink)
//   2. Rear Shell (Pastel Pink with USB-C + Power Switch)
//   3. Visor Frame (Piano Black 1.3" OLED Carrier)
//   4. Snap-Fit Bow (Vibrant Pink with TTP223 touch pocket)
//   5. Chubby Feet Pair (Pastel Peach forward-sitting paws)
// ==============================================================================

use <front_shell.scad>
use <rear_shell.scad>
use <visor_frame.scad>
use <snap_bow.scad>
use <feet_and_paws.scad>
include <minimo_girly_params.scad>

// Set to true to view exploded assembly diagram
exploded = false;
explosion_gap = exploded ? 28.0 : 0.0;

module minimo_girly_full_assembly() {
    // 1. Rear Shell (Spine, Beetle ESP32-C3 rails, LiPo cradle, USB-C, Switch)
    translate([0, explosion_gap, 0])
        rear_shell();

    // 2. Front Shell (Face & Belly)
    translate([0, -explosion_gap, 0])
        front_shell();

    // 3. 1.3" Visor Frame & OLED Holder (Black bezel)
    translate([0, -head_r + 4.5 - (explosion_gap * 2.0), head_z])
    rotate([-shell_tilt, 0, 0])
        visor_frame();

    // 4. Snap-Fit Bow (Headpiece & Touch Sensor)
    translate([0, 0, head_z + head_r + 2.0 + (explosion_gap * 1.6)])
    rotate([15, 0, 0])
        snap_bow();

    // 5. Chubby Feet & Paws (Forward sitting stance)
    translate([0, -(explosion_gap * 1.5), -(explosion_gap * 0.4)])
        feet_and_paws_pair();
}

minimo_girly_full_assembly();
