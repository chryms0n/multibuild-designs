# multibuild-designs

Claude designs 3D-printable parts for the MultiBuild system on request; the user prints them.

## Target printer

- Bambu Lab A1, build volume 256 × 256 × 256 mm
- PLA
- 0.4 mm nozzle (assumed; confirm with the user if a design depends on it)

Design for FDM: avoid unsupported overhangs beyond ~45°, pick an orientation that
prints without supports where possible, and keep walls a multiple of the line width.

## MultiBuild

MultiBuild is the overall system (formerly called Multiboard). Subsystems:

- **MultiBoard**: wall-mounted grid that tool holders attach to
- **MultiBin**: scalable bin system

Docs: https://docs.multibuild.io/ and https://multibuild.io/

**Rule:** take every mounting dimension (grid pitch, hole/thread geometry, snap and peg
profiles, bin units) from the official docs or from user measurements, never from memory.
Record the source next to each constant in `lib/`. Write the geometry ourselves; do not
copy MultiBuild's own model files into this repository (it is public).

## Tooling

- CAD: build123d (`pip install build123d`)
- Shared interface geometry lives in `lib/multiboard.py` and `lib/multibin.py`
- One script per part in `models/multiboard/` or `models/multibin/`; each exports STL
  (and STEP) to `exports/` with the same base name as the script
- Before handing a part over, check that it is a single valid solid, report its bounding
  box, and render a preview image
