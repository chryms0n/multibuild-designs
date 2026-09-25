"""Caliper holder for a MultiBoard large hole.

Holds a 150 mm vernier caliper (Connex COXT710520) hanging vertically, jaws up.
The beam drops into a short fork; the wider slider rests on top of the fork.
The left side of the fork is notched: the fine-adjust wheel below the slider rests
on the notch floor while the slider rests on the right arm. A groove in the back
wall lets the depth-rod guide tab at the beam's end slide through.
The bolt sits above the fork, so the caliper hangs below its fixing point and the
plate below the bolt bears flat against the tile. The bolt is our own flat-headed
Large Thread bolt: its flange sinks into a counterbore in the plate, flush with
the front, so the slider can pass in front of it. Tighten it with a coin in the
slot. A separate press-in peg sits in the small hole top-left of the bolt and
stops rotation.

Frame: X along the wall, Y up, Z out of the wall. Bolt axis at X = Y = 0,
back of the plate on Z = 0. Print the holder in this orientation (back face on
the bed), the bolt on its slotted face (exported that way) and the peg standing
on one end; no supports needed.

Exports (to exports/caliper_holder/): caliper_holder.{stl,step},
caliper_holder_peg.{stl,step}, caliper_holder_bolt.{stl,step}, previews
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib import multiboard as mb  # noqa: E402
from lib.preview import render, report  # noqa: E402

# --- Caliper (estimated from the user's photos via the caliper's own cm scale) --
BEAM_W = 16.0
BEAM_T = 3.5
FIT = 1.0                    # clearance per side around the beam
# Fine-adjust wheel: axis perpendicular to the scale face, left of the beam, just
# below the slider; it also sticks out behind the beam.
WHEEL_D = 10.5
WHEEL_DROP = 11.0            # lowest point of the wheel below the slider's bottom edge
WHEEL_X = -BEAM_W / 2 - 1.2  # wheel centre, ~1 mm outside the beam's left edge
WHEEL_T = 10.0               # thickness along Z (guess; the notch is cut through all Z)
WHEEL_CLR = 1.0
# Depth-rod guide tab on the back of the beam's bottom end, roughly centred.
TAB_W = 9.0
TAB_H = 2.0                  # protrusion behind the beam (guess; hollow behind is ~9 mm)

# --- Print / design choices ---------------------------------------------------
WALL = 2.4                   # 6 lines of 0.4 mm
PLATE_W = 38.0
PLATE_ABOVE = 19.0           # plate edge above the bolt axis (covers counterbore and peg)
BEAM_STANDOFF = 11.5         # plate front to beam back: room for the slider and wheel
FORK_H = 25.0                # right arm; the left arm is notched for the wheel
CORNER_R = 6.0               # plate corner radius
TAB_GROOVE_W = TAB_W + 2 * 1.0
LIP = 3.0                    # front lips reach this far over the slot (45 deg underside)
PEG_X, PEG_Y = mb.SMALL_HOLE_OFFSET

# --- Derived ------------------------------------------------------------------
PLATE_T = mb.MOUNT_PLATE_T
SLOT_W = BEAM_W + 2 * FIT
OUT_W = SLOT_W + 2 * WALL
BACK_Z = PLATE_T + BEAM_STANDOFF                       # beam rests against this face
LIP_Z = BACK_Z + BEAM_T + 2.5                          # inner face of the lips
FRONT_Z = LIP_Z + WALL
FORK_TOP = -(mb.CB_D / 2 + 1.5)                           # fork stays below the flange
FORK_BOT = FORK_TOP - FORK_H
PLATE_BOT = FORK_BOT
PLATE_TOP = PLATE_ABOVE


def fork_profile() -> Face:
    """Fork cross-section in the XZ plane (x -> X, y -> Z)."""
    outer = Polygon(
        (-OUT_W / 2, PLATE_T), (OUT_W / 2, PLATE_T),
        (OUT_W / 2, FRONT_Z), (-OUT_W / 2, FRONT_Z),
        align=None,
    )
    win = SLOT_W / 2 - LIP
    slot = Polygon(
        (-SLOT_W / 2, BACK_Z), (SLOT_W / 2, BACK_Z),
        (SLOT_W / 2, LIP_Z - LIP), (win, LIP_Z), (win, FRONT_Z + 1),
        (-win, FRONT_Z + 1), (-win, LIP_Z), (-SLOT_W / 2, LIP_Z - LIP),
        align=None,
    )
    # hollow behind the back wall saves filament and takes the guide tab; it is only
    # as wide as the tab groove so the back wall strips beside it are fully supported
    hollow = Rectangle(TAB_GROOVE_W, BACK_Z - WALL - PLATE_T - 0.01, align=(Align.CENTER, Align.MIN))
    hollow = Pos(0, PLATE_T - 0.005) * hollow
    return outer - slot - hollow


def build_holder() -> Part:
    plate = Pos(0, (PLATE_TOP + PLATE_BOT) / 2, PLATE_T / 2) * Box(
        PLATE_W, PLATE_TOP - PLATE_BOT, PLATE_T)
    # Plane.XZ has its normal along -Y; place it at the fork top and extrude down
    fork = extrude(Plane.XZ.offset(-FORK_TOP) * fork_profile(), FORK_H)
    holder = plate + fork
    # wheel notch: arm, lip and back wall; the wheel rests on its floor
    nx0 = -OUT_W / 2 - 1
    nx1 = WHEEL_X + WHEEL_D / 2 + WHEEL_CLR
    ny0 = FORK_TOP - WHEEL_DROP
    holder -= Pos((nx0 + nx1) / 2, (ny0 + FORK_TOP + 1) / 2, (PLATE_T + FRONT_Z + 1) / 2 + 0.01) * Box(
        nx1 - nx0, FORK_TOP + 1 - ny0, FRONT_Z + 1 - PLATE_T)
    # groove through the back wall for the depth-rod guide tab
    wz = BACK_Z - WALL / 2
    holder -= Pos(0, FORK_TOP - FORK_H / 2, wz) * Box(TAB_GROOVE_W, FORK_H + 2, WALL + 0.02)
    holder = mb.cut_mount(holder, 0, 0, (PEG_X, PEG_Y))
    # soften the outer plate edges parallel to Z
    edges = holder.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(abs(e.center().X) - PLATE_W / 2) < 1e-6)
    return fillet(edges, CORNER_R)


def wheel() -> Part:
    """Approximate fine-adjust wheel, resting on the notch floor (for checks/preview)."""
    return Pos(WHEEL_X, FORK_TOP - WHEEL_DROP + WHEEL_D / 2, BACK_Z + BEAM_T / 2) * Cylinder(
        WHEEL_D / 2, WHEEL_T)


def tab_path() -> Part:
    """Volume swept by the guide tab when the caliper is lifted through the fork."""
    return Pos(0, FORK_TOP - FORK_H / 2, BACK_Z - TAB_H / 2) * Box(TAB_W, FORK_H + 4, TAB_H)


if __name__ == "__main__":
    holder = build_holder()
    peg = Pos(PEG_X, PEG_Y, 0) * mb.peg()
    bolt = mb.flush_bolt()
    report("holder", holder)
    report("peg", peg)
    report("bolt", bolt)

    out = ROOT / "exports" / "caliper_holder"
    out.mkdir(parents=True, exist_ok=True)
    for name, part in [("caliper_holder", holder), ("caliper_holder_peg", peg),
                       ("caliper_holder_bolt", bolt)]:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))

    # preview: holder, peg, bolt (installed) and ghosted caliper for context
    bolt_in = mb.installed_bolt(bolt)
    beam_z = BACK_Z + BEAM_T / 2
    caliper = (Pos(0, FORK_TOP - 60, beam_z) * Box(BEAM_W, 150, BEAM_T)
               + Pos(0, FORK_TOP + 20, beam_z) * Box(27, 40, 10)
               + wheel()
               + Pos(0, FORK_TOP + 48, beam_z) * Box(75, 14, BEAM_T))
    blue, orange, grey, light = (0.35, 0.55, 0.85), (0.95, 0.55, 0.2), (0.4, 0.4, 0.4), (0.8, 0.8, 0.78)
    parts = [(holder, blue, 1), (peg, orange, 1), (bolt_in, grey, 1)]
    ctx = parts + [(caliper, light, 0.4)]
    render(str(out / "caliper_holder.png"), [
        ("Fig. 3a  Front 3/4, bolt grey", 25, -35, parts),
        ("Fig. 3b  Back (wall side), peg orange", 20, 150, parts),
        ("Fig. 3c  Side: wall left, caliper", 0, 90, ctx),
        ("Fig. 3d  In use (caliper ghosted)", 20, -35, ctx),
    ])
    upright = Rot(-90, 0, 0) * bolt   # renderer has Y up
    render(str(out / "caliper_holder_bolt.png"), [
        ("Bolt as printed, slot on the bed", 20, -30, [(upright, grey, 1)]),
        ("Coin slot (underside)", -65, -30, [(upright, grey, 1)]),
    ], figsize=(10, 5))
    print("wrote", out)
