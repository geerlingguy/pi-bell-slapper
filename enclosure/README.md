# Bell Enclosure

This case was designed with [OpenSCAD](http://openscad.org), and STL files are also included here so you can print the enclosure parts directly.

The enclosure design is based on [@tenderlove's Analog Terminal Bell](https://github.com/tenderlove/analog-terminal-bell/tree/master/case).

The Pi Zero sits in stops that hug its circuit board's edges, so plugging and unplugging USB cables pushes the board against the case instead of the small locating pegs. If the board is too tight (or loose) in the stops on your printer, adjust `clearance` in `PiStops()` in `pcb.scad` and re-export `case.stl`.
