// ==============================================================================
//  MINIMO GIRLY EDITION - Shared Parameters & Tolerances (1.3" OLED Edition)
// ==============================================================================

$fn = 60;

// --- 3D Printing Fit Tolerances ---
fit_tol         = 0.25;  // Standard FDM slip fit clearance (tight snap)
loose_tol       = 0.40;  // Loose fit clearance (wire channels, USB, battery)
wall_t          = 2.40;  // Nominal shell wall thickness
lip_h           = 3.20;  // Shell split perimeter alignment lip height
lip_w           = 1.10;  // Alignment lip thickness

// --- Body & Head Proportions (Enlarged to fit 1.3" OLED & full battery) ---
body_r          = 31.0;  // Pear body base radius
body_z          = 20.0;  // Body center Z
head_r          = 29.0;  // Head sphere radius (comfortably fits 35.5mm 1.3" OLED)
head_z          = 44.0;  // Head center Z
shell_tilt      = 12.0;  // Visor desk viewing angle (degrees backwards)

// --- OLED Display (Standard 1.3" I2C SH1106 / SSD1306 Module) ---
oled_pcb_w      = 35.6;  // PCB width
oled_pcb_h      = 33.8;  // PCB height
oled_pcb_t      = 1.60;  // PCB thickness
oled_total_d    = 4.20;  // Total depth including glass & header pins
oled_glass_w    = 30.0;  // Active glass display viewing width
oled_glass_h    = 16.0;  // Active glass display viewing height
oled_glass_z_off= 2.50;  // Center offset of active area from PCB center
oled_mount_x    = 30.5;  // M2 mounting hole X pitch
oled_mount_y    = 28.5;  // M2 mounting hole Y pitch

// --- Touch Sensor (TTP223 Red Module in Top Bow) ---
ttp_w           = 15.5;  // TTP223 PCB width
ttp_h           = 11.5;  // TTP223 PCB height
ttp_t           = 2.20;  // Board + SMD components thickness
ttp_wire_d      = 4.50;  // 3-pin wire harness routing hole

// --- Microcontroller (DFRobot Beetle ESP32-C3 with Onboard Charger) ---
beetle_w        = 20.8;  // Beetle width
beetle_l        = 25.2;  // Beetle length
beetle_t        = 1.60;  // PCB thickness
beetle_rail_h   = 5.00;  // Rail standoff height for Dupont/soldering clearance

// --- Battery Compartment (1S 3.7V 400mAh–600mAh LiPo e.g. 602535 / 702535) ---
bat_w           = 27.0;  // Max battery width
bat_l           = 38.0;  // Max battery length
bat_h           = 7.50;  // Max battery thickness

// --- Rear Power Slide Switch (SS12D00 / SS12F44 Standard Mini Switch) ---
switch_w        = 8.8;   // Switch body width
switch_h        = 4.4;   // Switch body height
switch_d        = 4.8;   // Switch body depth
switch_travel   = 3.5;   // Slider travel slot length
switch_knob_w   = 3.2;   // Slider knob width
switch_knob_h   = 3.2;   // Slider knob height

// --- USB-C Port Cutout ---
usbc_w          = 9.6;   // USB-C socket width + clearance
usbc_h          = 3.8;   // USB-C socket height + clearance
usbc_lead_in    = 1.2;   // Outer chamfer for cable head relief

// --- Screw & Snap Hardware ---
screw_hole_d    = 2.1;   // For M2 self-tapping screws or M2 heat-set inserts
screw_head_d    = 4.0;   // Screw head counterbore
screw_boss_od   = 5.5;   // Screw boss outer diameter
