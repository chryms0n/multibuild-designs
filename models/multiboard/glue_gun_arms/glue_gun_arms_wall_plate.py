"""Wall plate for the glue gun arms: taped flat to the wall, it carries the user's
2x6 MultiBoard Octagon Plate, which the two arms bolt into.

Stack, from the wall out: this wall plate (double-sided tape on its flat back), the
2x6 plate lying horizontally on it, then the arms.

  - A thin base the size of the 2x6 plate carries four Flush Snaps (our own
    geometry, see lib.multiboard.flush_snap) that the 2x6 plate clicks onto: both
    rows of the two columns next to the outer ones (the user's plate has its outer
    columns glued up). Stacked in columns, they leave the tape wider solid strips.
  - The arms bolt into the two outer holes of the top row, 5 grid units apart, with
    their pegs in the small holes below-left of the bolts. The 2x6 plate is turned
    so its edge with the interlocking tabs (and its extra row of small holes) is at
    the top. The base is open under the other large holes; the arms' bolts end in
    those windows, short of the wall.
  - The arms reach well below the 2x6 plate. The gun's weight presses their lower
    ends towards the wall, so a thin leg runs down behind each arm to a pad as tall
    as the 2x6 plate, on which the arm's lower end rests.

Frame: X along the wall, Y up, Z out of the wall; the left arm's bolt at X = Y = 0,
the back of the wall plate on Z = 0. Print it as modelled, back on the bed (a smooth
build plate gives the tape a better surface); no supports.

Exports (to exports/glue_gun_arms/): glue_gun_arms_wall_plate.{stl,step}, preview
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import *  # noqa: E402

import glue_gun_arms as arms  # noqa: E402
from lib import multiboard as mb  # noqa: E402
from lib.preview import render, report  # noqa: E402

BASE_T = 3.0                 # base and legs; the arms' bolts end 0.8 mm into it (in windows)
BASE_ROUND = 4.0             # base corner radius
WINDOW_D = 23.0              # opening in the base under a large hole (bolt thread 22.25)
PAD_H = 16.0                 # pad height up each arm from its lowest point
PAD_INSET = 1.5              # pad kept this far inside the arm's outline
LEG_W = 20.0                 # where a leg meets the base
# Large holes of the 2x6 plate as (column 0-5 from the left, row 0 = top, 1 = bottom);
# the arms' bolts use (0, 0) and (5, 0)
SNAP_HOLES = [(1, 0), (1, 1), (4, 0), (4, 1)]
PITCH = mb.GRID_PITCH
TOP_T = BASE_T + mb.OCT_PLATE_T          # front of the 2x6 plate = the arms' back
# The 2x6 plate on the wall: its top-left hole is the left bolt; its own +X (tab
# edge) points up, so it is turned by +90 deg. Its back rests on the base.
PLATE_AT = Pos(2.5 * PITCH, -0.5 * PITCH) * Rot(0, 0, 90)
BASE_Y0 = -0.5 * PITCH - mb.OCT_PLATE_SIZE[0] / 2            # bottom edge of the base


def hole_xy(col: int, row: int) -> Vector:
    return Vector(col * PITCH, -row * PITCH)


def flat(shape):
    """A planar section moved down onto z = 0."""
    return Pos(0, 0, -shape.bounding_box().min.Z) * shape


def arm_back(arm: Part) -> Face:
    """Outline of an arm's back face (the side that rests on the 2x6 plate)."""
    return flat(Sketch() + [Face(f.outer_wire()) for f in section(arm, Plane.XY.offset(0.1)).faces()])


def pad_outline(arm: Part) -> Face:
    """The lowest PAD_H of the arm's back outline, kept inside it."""
    back = offset(arm_back(arm), -PAD_INSET, kind=Kind.ARC)
    bb = back.bounding_box()
    band = Pos(bb.center().X, bb.min.Y + PAD_H / 2) * Rectangle(bb.size.X + 2, PAD_H)
    return (back & band).faces()[0]


def leg_outline(pad: Face) -> Face:
    """From the base's bottom edge down to the pad, LEG_W wide at the base."""
    x = min(max(pad.bounding_box().center().X, LEG_W / 2), 5 * PITCH - LEG_W / 2)   # under the base
    pts = [Vector(x - LEG_W / 2, BASE_Y0 + 2), Vector(x + LEG_W / 2, BASE_Y0 + 2)]
    pts += [e.position_at(i / 8) for e in pad.edges() for i in range(9)]
    return arms.polygon(arms.hull2d(pts))


def build_wall_plate(arm_parts) -> Part:
    base = PLATE_AT * RectangleRounded(*mb.OCT_PLATE_SIZE, BASE_ROUND)
    pads = [pad_outline(a) for a in arm_parts]
    body = extrude(base + [leg_outline(p) for p in pads], BASE_T)
    body += [extrude(p, TOP_T) for p in pads]
    snap = mb.flush_snap()
    for col in range(6):
        for row in range(2):
            c = hole_xy(col, row)
            if (col, row) in SNAP_HOLES:
                body += Pos(c.X, c.Y, BASE_T - 0.01) * snap
            else:
                body -= Pos(c.X, c.Y, -1) * Cylinder(WINDOW_D / 2, BASE_T + 2,
                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    return body


def octagon_plate_stand_in() -> Part:
    """The 2x6 plate for previews and checks: outline and plain octagonal holes."""
    body = extrude(mb.oct_plate_outline(), mb.OCT_PLATE_T)
    for x, y in mb.oct_plate_large_holes():
        body -= Pos(x, y, -1) * extrude(RegularPolygon(mb.SNAP_BASE_AF / 2 + 0.05, 8, major_radius=False,
                                                       rotation=22.5), mb.OCT_PLATE_T + 2)
    return Pos(0, 0, BASE_T) * PLATE_AT * body


if __name__ == "__main__":
    d = arms.design(verbose=False)
    shift = Pos(-d.left_bolt.X, -d.left_bolt.Y)
    rel = d.right_bolt - d.left_bolt
    assert (rel - hole_xy(5, 0)).length < 1e-6, "arms no longer bolt 5 grid units apart in one row"
    left, right = shift * d.left, shift * d.right
    pegs = [p - d.left_bolt for p in (d.peg_l, d.peg_r)]
    wall = build_wall_plate([left, right])
    report("wall plate", wall)

    # checks: where the arms rest; bolt tips, pegs and the 2x6 plate clear of the wall plate
    on_top = Pos(0, 0, TOP_T)
    bolt, peg = mb.flush_bolt(arms.BOLT_THREAD_L), mb.peg()
    bolts = [on_top * mb.installed_bolt(bolt, c.X, c.Y) for c in (hole_xy(0, 0), hole_xy(5, 0))]
    peg_parts = [on_top * Pos(p.X, p.Y) * peg for p in pegs]
    stand_in = octagon_plate_stand_in()
    pad_tops = flat(section(wall, Plane.XY.offset(TOP_T - 0.05)))
    for name, a in (("left", left), ("right", right)):
        back = arm_back(a)
        print(f"{name} arm rests on: 2x6 plate {(back & PLATE_AT * mb.oct_plate_outline()).area:.0f} mm^2, "
              f"pad {(back & pad_tops).area:.0f} mm^2")
    print(f"overlap with wall plate: bolts {sum((b & wall).volume for b in bolts):.3f}  "
          f"pegs {sum((p & wall).volume for p in peg_parts):.3f}  "
          f"2x6 plate (outline, octagonal holes) {(stand_in & wall).volume:.3f} mm^3; "
          f"bolt tips end {min(b.bounding_box().min.Z for b in bolts):.1f} mm from the wall")
    print(f"tape area on the back: {section(wall, Plane.XY.offset(0.05)).area / 100:.0f} cm^2")
    bad, bridges = arms.overhangs(wall)
    print(f"faces steeper than 45 deg off the bed {bad:.1f} mm^2, of which flat bridges (snap tabs) {bridges:.1f}; "
          f"unsupported islands when sliced: {arms.islands(wall)}")

    out = ROOT / "exports" / "glue_gun_arms"
    out.mkdir(parents=True, exist_ok=True)
    export_stl(wall, str(out / "glue_gun_arms_wall_plate.stl"))
    export_step(wall, str(out / "glue_gun_arms_wall_plate.step"))
    print("wrote", out)

    teal, grey, blue, orange = (0.3, 0.7, 0.6), (0.62, 0.62, 0.6), (0.35, 0.55, 0.85), (0.95, 0.55, 0.2)
    stack = [(wall, teal, 1), (stand_in, grey, 1)]
    arm_items = [(on_top * a, blue, 0.55) for a in (left, right)] + [(b, grey, 1) for b in bolts] \
        + [(p, orange, 1) for p in peg_parts]
    exploded = [(wall, teal, 1), (Pos(0, 0, 25) * stand_in, grey, 1)] \
        + [(Pos(0, 0, 50) * item, c, a) for item, c, a in arm_items]
    render(str(out / "glue_gun_arms_wall_plate.png"), [
        ("Fig. 6a  Wall plate as printed (snaps on the base)", 35, -30, [(wall, teal, 1)]),
        ("Fig. 6b  With the 2x6 plate clicked on", 0, 0, stack),
        ("Fig. 6c  With the arms (blue, see-through)", 0, 0, stack + arm_items),
        ("Fig. 6d  Exploded: wall plate, 2x6 plate, arms", 25, -60, exploded),
    ], figsize=(22, 6))
