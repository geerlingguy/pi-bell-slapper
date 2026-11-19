# Bell Enclosure

This case was designed with [OpenSCAD](http://openscad.org), and STL files are also included here so you can print the enclosure parts directly.

The enclosure design is based on [@tenderlove's Analog Terminal Bell](https://github.com/tenderlove/analog-terminal-bell/tree/master/case).

## Printing

Print `case.stl` (bell base, solenoid stand, and Pi case as one part) and `lid.stl`. The lid prints top-down, with the "Clarence 2.0" text on the bed.

## Generating STLs

Install OpenSCAD (`brew install openscad` on macOS, `sudo apt install openscad` on Debian/Ubuntu), then from this folder:

```
openscad --export-format binstl -o case.stl case.scad
openscad --export-format binstl -o lid.stl lid.scad
```

Each takes a few seconds. `--export-format binstl` writes binary STLs, which are about a quarter the size of the default ASCII ones. Use `-D 'name=value'` to override a top-level variable without editing a file.

## Files

| File | What it is |
| --- | --- |
| `case.scad` | Top-level file for `case.stl` |
| `lid.scad` | Top-level file for `lid.stl` |
| `bell-base-and-stand.scad` | Positions the bell base, solenoid, and Pi case relative to each other |
| `bell-base.scad` | Round base the bell sits in, with a filleted ridge to hold it |
| `solenoid-stand.scad`, `solenoid-mount.scad` | Angled post and cradle that hold the solenoid against the bell |
| `pcb.scad` | Pi Zero case (pegs, edge stops, wall openings) and its lid |

## Design decisions

  - **One printed part**: The bell base, solenoid stand, and Pi case are printed together, so the solenoid always lines up with the bell, and nothing can shift in transit.
  - **Solenoid height**: The solenoid is centered on the height of the ridge on the bell's rim (`to_bell_z` and `bell_ridge_z` in `bell-base-and-stand.scad`), so it strikes the bell where it rings best.
  - **Pi Zero edge stops**: Printed pegs alone sheared off when USB cables were plugged in. Now the pegs only locate the Pi, and blocks on the floor (`PiStops()` in `pcb.scad`) hug all four edges of its circuit board, taking the force of plugging and unplugging. They only come up 1 mm onto the board's edge, so they clear the SD card and camera connector. If the Pi is too tight or loose in the stops on your printer, adjust `clearance` (default 0.25 mm).
  - **No screws**: The perfboard stacked on the Pi covers its mounting holes, so screws couldn't be reached.
  - **Wall openings**: Openings for the power and USB plugs (together) and mini HDMI plug are placed from the Pi Zero's published port positions, sized for plug overmolds, with rounded corners. A slot at the top of the wall lets the solenoid wires through under the lid.
  - **Lid**: A friction fit, with a lip that sits inside the case walls, and small notches on two sides to pry it off.
