// ==============================================================================
//  MINIMO GIRLY EDITION - Bambu Lab A1 Mini Single Plate Layout
//  Build Volume: 180mm x 180mm x 180mm
//  Pre-oriented for maximum bed adhesion and clean surface finishes:
//   - Front Shell:   Lying flat on its Y=0 parting plane (zero support needed inside)
//   - Rear Shell:    Lying flat on its Y=0 parting plane (zero support needed inside)
//   - Visor Frame:   Lying flat on its rear reference mounting flange
//   - Chubby Feet:   Lying flat on bottom soles
//   - Snap Bow:      Lying flat on underside base plug
// ==============================================================================

use <front_shell.scad>
use <rear_shell.scad>
use <visor_frame.scad>
use <snap_bow.scad>
use <feet_and_paws.scad>
include <minimo_girly_params.scad>

// Optional 180x180mm A1 Mini Bed Visualizer (disabled during 3MF export)
show_bed = false;

module a1_mini_bed_outline() {
    color([0.3, 0.3, 0.35], 0.25)
    translate([0, 0, -1])
    cube([180, 180, 2], center = true);
    
    // 180x180 coordinate boundary line
    color([0.8, 0.8, 0.2])
    difference() {
        cube([180.5, 180.5, 0.5], center = true);
        cube([179.5, 179.5, 1.0], center = true);
    }
}

module bambu_a1_mini_plate() {
    if (show_bed) {
        a1_mini_bed_outline();
    }

    // --- 1. Front Shell ---
    // Positioned in top-left quadrant (-40, 32)
    // Rotated so Y=0 parting line sits flat on build plate (Z=0)
    translate([-38.0, 32.0, 0])
    rotate([-90, 0, 0])
    front_shell();

    // --- 2. Rear Shell ---
    // Positioned in top-right quadrant (38, 32)
    // Rotated so Y=0 parting line sits flat on build plate (Z=0)
    translate([38.0, 32.0, 0])
    rotate([90, 0, 0])
    rear_shell();

    // --- 3. 1.3" Visor Frame ---
    // Positioned in bottom-left quadrant (-45, -45)
    // Seated flat on its rear perimeter mounting flange
    translate([-46.0, -45.0, 2.0])
    rotate([180, 0, 0])
    visor_frame();

    // --- 4. Chubby Feet & Paws Pair ---
    // Positioned in bottom-center (4, -45)
    // Seated flat on their bottom cut soles
    translate([4.0, -25.0, 0])
    feet_and_paws_pair();

    // --- 5. Snap-Fit Bow ---
    // Positioned in bottom-right quadrant (50, -45)
    // Sits flat on base plug
    translate([52.0, -45.0, 6.0])
    rotate([0, 0, 0])
    snap_bow();
}

bambu_a1_mini_plate();
