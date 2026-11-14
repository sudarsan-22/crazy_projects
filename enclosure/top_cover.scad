// ====================================================================
// ESP32 Music Controller - Ultra Spacious Desktop Console (Top Cover)
// Dimensions: 125mm (W) x 90mm (D) x 28mm (Front) -> 52mm (Back)
// Massive internal volume for Dupont wiring harnesses & module clearance
// ====================================================================

$fn = 64;

box_w    = 125.0;
box_d    = 90.0;
h_front  = 28.0;  // Generous front height for button clearance
h_back   = 52.0;  // 52mm rear height for huge wiring chamber
tilt_ang = atan((h_back - h_front) / box_d); // ~15 deg
wall     = 2.4;
corner_r = 5.0;

// Screen & Controls Layout on Angled Face
oled_w = 30.5;
oled_h = 16.0;
oled_x = 38.0;
oled_y = 54.0;

knob_d = 7.5;
knob_x = 94.0;
knob_y = 54.0;

btn_d = 8.5;
btn1_x = 38.0;
btn2_x = 94.0;
btn_y  = 22.0;

// Rear Micro-USB (Type-B) Power Cutout
usb_w = 14.5;
usb_h = 9.5;
esp_x = box_w / 2;

module desk_wedge(w, d, h1, h2, r) {
    hull() {
        translate([r, r, 0]) cylinder(r=r, h=h1);
        translate([w-r, r, 0]) cylinder(r=r, h=h1);
        translate([r, d-r, 0]) cylinder(r=r, h=h2);
        translate([w-r, d-r, 0]) cylinder(r=r, h=h2);
    }
}

module ultra_top_cover() {
    difference() {
        // Outer Body
        desk_wedge(box_w, box_d, h_front, h_back, corner_r);
        
        // Huge Hollow Interior
        translate([wall, wall, wall - 1])
            desk_wedge(box_w - 2*wall, box_d - 2*wall, h_front - wall, h_back - wall, corner_r - 1.2);
            
        // Angled Face Cutouts
        translate([0, 0, h_front])
        rotate([tilt_ang, 0, 0]) {
            // 1. OLED Screen Frame (with beveled accent)
            translate([oled_x - oled_w/2, oled_y - oled_h/2, -5])
                cube([oled_w, oled_h, 20]);
            translate([oled_x - (oled_w+4)/2, oled_y - (oled_h+4)/2, -1.2])
                cube([oled_w+4, oled_h+4, 3]);
            
            // 2. Rotary Encoder Cutout & Dial Accent Well
            translate([knob_x, knob_y, -5])
                cylinder(d=knob_d, h=20);
            translate([knob_x, knob_y, -1.2])
                difference() {
                    cylinder(d=30.0, h=3);
                    cylinder(d=26.5, h=4);
                }
                
            // 3. Tactile Push Button Cutouts
            translate([btn1_x, btn_y, -5])
                cylinder(d=btn_d, h=20);
            translate([btn2_x, btn_y, -5])
                cylinder(d=btn_d, h=20);
        }
        
        // Rear Centered Micro-USB Power Cutout (Direct access to ESP32 port)
        translate([esp_x - usb_w/2, box_d - wall - 1, wall + 3.0])
            cube([usb_w, wall + 3, usb_h]);
    }
    
    // Internal OLED Screw Mounts (M2, 29x28mm pitch)
    translate([0, 0, h_front])
    rotate([tilt_ang, 0, 0]) {
        for (dx = [-14.5, 14.5]) {
            for (dy = [-14.0, 14.0]) {
                translate([oled_x + dx, oled_y + dy, -6.0])
                    difference() {
                        cylinder(d=5.0, h=6.0);
                        cylinder(d=2.0, h=7.0);
                    }
            }
        }
        
        // 6x6mm Button Sockets
        for (bx = [btn1_x, btn2_x]) {
            translate([bx - 4.5, btn_y - 4.5, -6.0])
                difference() {
                    cube([9.0, 9.0, 6.0]);
                    translate([1.2, 1.2, -0.5])
                        cube([6.6, 6.6, 7.0]);
                }
        }
    }
    
    // 4 Corner Screw Pillars (M3)
    for (cx = [corner_r + 2.5, box_w - corner_r - 2.5]) {
        translate([cx, corner_r + 2.5, wall])
            difference() {
                cylinder(d=7.0, h=h_front - 2);
                cylinder(d=3.0, h=h_front);
            }
        translate([cx, box_d - corner_r - 2.5, wall])
            difference() {
                cylinder(d=7.0, h=h_back - 3);
                cylinder(d=3.0, h=h_back);
            }
    }
}

ultra_top_cover();
