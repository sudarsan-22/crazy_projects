// ====================================================================
// ESP32 Music Controller - Ultra Spacious Bottom Base (125x90mm)
// Features:
//  - ESP32 Micro-USB port positioned flush with the rear back wall
//  - Raised ESP32 rails with under-board wire clearance for Dupont plugs
//  - 4x anti-skid rubber feet pockets
// ====================================================================

$fn = 64;

box_w      = 125.0;
box_d      = 90.0;
corner_r   = 5.0;
wall       = 2.4;
base_thick = 2.5;
lip_h      = 3.5;

// ESP32 NodeMCU 30-Pin Dimensions & Positioning
esp_w = 51.5;
esp_d = 28.5;
esp_x = box_w / 2;
esp_y = box_d - wall - (esp_d / 2) - 1.5; // Positions Micro-USB connector flush against back cutout

usb_w = 14.5;
usb_h = 9.5;

module rounded_box(w, d, h, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h);
        translate([w-r, r, 0]) cylinder(r=r, h=h);
        translate([r, d-r, 0]) cylinder(r=r, h=h);
        translate([w-r, d-r, 0]) cylinder(r=r, h=h);
    }
}

module ultra_bottom_base() {
    difference() {
        union() {
            // Main Base Plate
            rounded_box(box_w, box_d, base_thick, corner_r);
            
            // Alignment Lip
            translate([wall + 0.25, wall + 0.25, base_thick])
                difference() {
                    rounded_box(box_w - 2*wall - 0.5, box_d - 2*wall - 0.5, lip_h, corner_r - 1.2);
                    translate([1.2, 1.2, -0.5])
                        rounded_box(box_w - 2*wall - 2.9, box_d - 2*wall - 2.9, lip_h + 1, corner_r - 2);
                }
                
            // Raised ESP32 Mounting Rails (6mm tall for Dupont wire clearance underneath)
            translate([esp_x - esp_w/2, esp_y - esp_d/2, base_thick])
                difference() {
                    cube([esp_w, esp_d, 6.0]);
                    // Hollow center channel for wire routing under the ESP32
                    translate([4.0, -1.0, -1.0])
                        cube([esp_w - 8.0, esp_d + 2.0, 8.0]);
                }
        }
        
        // 4 Corner Countersunk M3 Screw Holes
        for (cx = [corner_r + 2.5, box_w - corner_r - 2.5]) {
            for (cy = [corner_r + 2.5, box_d - corner_r - 2.5]) {
                translate([cx, cy, -1]) {
                    cylinder(d=3.4, h=base_thick + lip_h + 2);
                    cylinder(d=6.6, h=1.8);
                }
            }
        }
        
        // 4 Rubber Feet Recesses (8.5mm dia on underside)
        for (fx = [12.0, box_w - 12.0]) {
            for (fy = [12.0, box_d - 12.0]) {
                translate([fx, fy, -0.1])
                    cylinder(d=8.5, h=1.2);
            }
        }
        
        // Rear Micro-USB (Type-B) Port Cutout
        translate([esp_x - usb_w/2, box_d - wall - 2, base_thick + 1.5])
            cube([usb_w, 6, usb_h]);
    }
    
    // ESP32 PCB Corner Screw Standoffs (48.0 x 24.5mm hole pitch)
    for (dx = [-24.0, 24.0]) {
        for (dy = [-12.25, 12.25]) {
            translate([esp_x + dx, esp_y + dy, base_thick])
                difference() {
                    cylinder(d=5.0, h=6.0);
                    cylinder(d=2.0, h=7.0); // M2 mounting screw
                }
        }
    }
}

ultra_bottom_base();
