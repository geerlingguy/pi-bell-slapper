module Pegs(height, pin_diameter) {
  $fn = 90;
  pcb_thickness = 1.9;

  for (i = [-1.05, 0.95]) {
    for (j = [-0.8, 1.2]) {
      translate([i * (58 / 2), j * (23 / 2), 0]) {
        linear_extrude(height)
          circle(r = 2.5);
        linear_extrude(height + pcb_thickness)
          circle(d = pin_diameter);
      }
    }
  }
}

// Pi Zero outline in case coordinates, from the peg (mounting hole) positions.
pi_x0 = -1.05 * (58 / 2) - 3.5;
pi_x1 = 0.95 * (58 / 2) + 3.5;
pi_y0 = -0.8 * (23 / 2) - 3.5;
pi_y1 = 1.2 * (23 / 2) + 3.5;

// Port centers along the port edge (+y), measured from the CSI end (pi_x0).
pwr_x = pi_x0 + 65 - 54;
usb_x = pi_x0 + 65 - 41.4;
hdmi_x = pi_x0 + 65 - 12.4;
plug_width = 12;  // Micro USB plug overmold, plus clearance.
hdmi_plug_width = 16;

// Blocks around the Pi's edges, so plugging in pushes the board against the case instead of the pegs.
module PiStops(inner_x, inner_y, radius, peg_height, clearance = 0.25) {
  h = peg_height + 1;  // Overlaps the bottom 1 mm of the Pi's PCB edge.
  port_gaps = [
    [pi_x0, pwr_x - plug_width / 2],
    [usb_x + plug_width / 2, hdmi_x - hdmi_plug_width / 2],
    [hdmi_x + hdmi_plug_width / 2, pi_x1],
  ];

  intersection() {
    union() {
      // GPIO side
      translate([pi_x0, -inner_y / 2, 0])
        cube([pi_x1 - pi_x0, (inner_y / 2) + pi_y0 - clearance, h]);
      // Port side, between the plugs
      for (gap = port_gaps)
        translate([gap[0], pi_y1 + clearance, 0])
          cube([gap[1] - gap[0], (inner_y / 2) - pi_y1 - clearance, h]);
      // Short ends
      translate([-inner_x / 2, pi_y0, 0])
        cube([(inner_x / 2) + pi_x0 - clearance, pi_y1 - pi_y0, h]);
      translate([pi_x1 + clearance, pi_y0, 0])
        cube([(inner_x / 2) - pi_x1 - clearance, pi_y1 - pi_y0, h]);
    }
    linear_extrude(h)
      minkowski() {
        circle(r = radius);
        square(size = [inner_x - (radius * 2), inner_y - (radius * 2)], center = true);
      }
  }
}

// Posts that press the Pi down around its two mounting holes at the camera connector end, which the perfboard doesn't cover.
module PiHoldDowns(length, diameter = 4.5) {
  $fn = 60;
  // The lid is flipped over when installed, so case x is mirrored.
  for (y = [pi_y0 + 3.5, pi_y1 - 3.5]) {
    translate([-(pi_x0 + 3.5), y, 0])
      difference() {
        union() {
          cylinder(d = diameter, h = length);
          cylinder(d1 = diameter + 3, d2 = diameter, h = 2);  // Fillet at the lid
        }
        // Clearance for the locating pin's tip
        translate([0, 0, length - 1])
          cylinder(d = 3, h = 1.1);
      }
  }
}

module PCBLid(top_thickness, wall_thickness, peg_height = 3, pi_pcb_thickness = 1.5) {
  pcb_padding = 2;
  pcb_x = 72 + pcb_padding;
  pcb_y = 50 + pcb_padding;
  radius = 5;
  pcb_thickness = 1.9 + 20; // pcb + components
  lid_height = 3;

  lip_height = 2;
  outer_lid_x = ((pcb_x + (wall_thickness * 2)) - (radius * 2));
  outer_lid_y = ((pcb_y + (wall_thickness * 2)) - (radius * 2));

  $fn = 90;
  difference() {
    union() {
      // inner lip
      linear_extrude(lid_height + top_thickness + lip_height)
        minkowski() {
          circle(r = radius);
          square(size = [pcb_x - (radius * 2), pcb_y - (radius * 2)], center = true);
        }

      // Outer
      color("green")
      linear_extrude(lid_height + top_thickness)
        minkowski() {
          circle(r = radius);
          square(size = [outer_lid_x, outer_lid_y], center = true);
        }
    }

    translate([0, 0, top_thickness])
    linear_extrude(pcb_thickness + 3) // Add 1 so it looks nice in preview
      minkowski() {
        circle(r = radius - 1);
        square(size = [pcb_x - (radius * 2), pcb_y - (radius * 2)], center = true);
      }

    for (i = [-1, 1]) {
      color("red")
        translate([0, i * ((outer_lid_y + (radius * 2)) / 2) - (i * (1 / 2)), (lid_height + top_thickness) - 1])
        linear_extrude(1)
        square(size = [5, 2], center = true);
    }

    mirror([1,0,0])
        translate([0,0,-.001])
            linear_extrude(1)
                text("Clarence 2.0", halign = "center", valign = "center", size = 8);
  }

  // Lid's outer rim sits on the case walls; posts reach down to the top of the Pi's PCB.
  translate([0, 0, top_thickness])
    PiHoldDowns(lid_height + pcb_thickness - peg_height - pi_pcb_thickness);
}

// Rounded rectangular hole through a wall centered at y, from height z up.
module WallCutout(x, y, thickness, z, width, height, radius) {
  translate([x, y, z])
    rotate([90, 0, 0])
    color("blue")
    // Add 1 so it looks nice in preview
    linear_extrude(thickness + 1, center = true)
    translate([-width / 2, 0])
    offset(r = radius) offset(delta = -radius)
    square([width, height]);
}

module PCBCase(bottom_thickness, wall_thickness, peg_height = 3, pin_diameter = 2.3) {
  pcb_padding = 2;
  pcb_x = 72 + pcb_padding;
  pcb_y = 50 + pcb_padding;

  usb_height = 8;
  usb_width  = 14;

  radius = 5;
  pcb_thickness = 1.9 + 20; // pcb + components

  translate([0, 0, bottom_thickness]) {
    difference() {
      $fn = 90;
      //translate([0, 0, -bottom_thickness])
      translate([0, 0, -bottom_thickness])
        linear_extrude(bottom_thickness + pcb_thickness)
        minkowski() {
          circle(r = radius);
          square(size = [((pcb_x + (wall_thickness * 2)) - (radius * 2)), ((pcb_y + (wall_thickness * 2)) - (radius * 2))], center = true);
        }

        linear_extrude(pcb_thickness + 1) // Add 1 so it looks nice in preview
        minkowski() {
          circle(r = radius);
          square(size = [pcb_x - (radius * 2), pcb_y - (radius * 2)], center = true);
        }

      // Wire hole (a slot open at the top)
      wall_y = (pcb_y + wall_thickness) / 2;
      wire_z = peg_height + 12;
      WallCutout(((pcb_x - pcb_padding) / 2) - 35, wall_y, wall_thickness, wire_z, 6, pcb_thickness - wire_z + 2, 1);

      // Openings for the power and USB plugs, and the mini HDMI plug
      WallCutout((pwr_x + usb_x) / 2, wall_y, wall_thickness, peg_height - 1.5, usb_x - pwr_x + plug_width, usb_height + 1, 1.5);
      WallCutout(hdmi_x, wall_y, wall_thickness, peg_height - 1.5, hdmi_plug_width, usb_height + 1, 1.5);
    }

    Pegs(peg_height, pin_diameter);
    PiStops(pcb_x, pcb_y, radius, peg_height);
  }
}

PCBCase(1.5, 1.5);
//PCBLid(1.5, 1.5);
