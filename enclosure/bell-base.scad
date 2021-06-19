module BellBase(plate_thickness, bell_bottom_diameter, fillet_height) {
  bell_bottom_radius = bell_bottom_diameter / 2;
  bottom_ridge_x = fillet_height + 1;

  translate([0, 0, plate_thickness]) {
    color("Violet")
      translate([0, 0, -plate_thickness])
      linear_extrude(height = plate_thickness)
      circle(d = bell_bottom_diameter + (2 * bottom_ridge_x));

    color("Olive")
      rotate_extrude()
      translate([bell_bottom_radius, 0, 0]) {
        union() {
          square(size = [1, fillet_height]);
          translate([1, 0, 0]) {
            intersection() {
              square(fillet_height * 2);
              difference() {
                square(fillet_height * 2, center=true);
                translate([fillet_height, fillet_height]) circle(fillet_height);
              }
            }
          }
        }
      }
  }
}
