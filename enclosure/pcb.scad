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

module PCBLid(top_thickness, wall_thickness) {
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
                text("Clarence 2.0", font = f, halign = "center", valign = "center", size = 8);
  }
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

      // Wire hole
      translate([((pcb_x - pcb_padding) / 2) - 35, ((pcb_y + wall_thickness) / 2), peg_height + 14])
        color("blue")
        linear_extrude(6)
        // Add 1 so it looks nice in preview
        square(size = [6, wall_thickness + 1], center = true);

      // USB hole
      translate([((pcb_x - pcb_padding) / 2) - 61, ((pcb_y + wall_thickness) / 2), peg_height + 1])
        color("blue")
        linear_extrude(usb_height)
        // Add 1 so it looks nice in preview
        square(size = [usb_width, wall_thickness + 1], center = true);

    }

    Pegs(peg_height, pin_diameter);
  }
}

PCBCase(1.5, 1.5);
//PCBLid(1.5, 1.5);
