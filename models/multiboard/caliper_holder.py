"""Caliper holder for a MultiBoard large hole.

Holds a 150 mm vernier caliper (Connex COXT710520) hanging vertically, jaws up.
The beam drops into a short fork; the wider slider rests on top of the fork.
The left side of the fork is notched so the fine-adjust wheel below the slider fits.
Mounted with one official Large Thread bolt through the plate, plus a separate
press-in peg that sits in the small hole top-left of the bolt and stops rotation.

Frame: X along the wall, Y up, Z out of the wall. Bolt axis at X = Y = 0,
back of the plate on Z = 0. Print the holder in this orientation (back face on
the bed) and the peg standing on one end; no supports needed.

Exports: exports/caliper_holder.{stl,step}, exports/caliper_holder_peg.{stl,step}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib import multiboard as mb  # noqa: E402
from lib.preview import render  # noqa: E402

# --- Caliper (estimated from the user's photo; user accepted the estimates) --
BEAM_W = 16.0
BEAM_T = 3.5
FIT = 1.0                    # clearance per side around the beam
WHEEL_D = 14.0               # fine-adjust wheel just below the slider, left of the beam

# --- Print / design choices ---------------------------------------------------
WALL = 2.4                   # 6 lines of 0.4 mm
PLATE_T = 5.0                # mb.LARGE_THREAD_SHANK_L - TILE_THICKNESS - TILE_WALL_GAP + 1 = 4.5 minimum
PLATE_W = 36.0
HEAD_CLR = 1.5               # air between bolt head and the caliper beam
FORK_H = 25.0                # right arm; the left arm is notched for the wheel
LIP = 3.0                    # front lips reach this far over the slot (45 deg underside)
BOLT_HOLE_D = mb.large_bolt_clearance_d(0.5)

# --- Peg ----------------------------------------------------------------------
PEG_D = mb.SMALL_HOLE_D - 2 * 0.3
PEG_OUT = 4.0                # length sticking into the tile's small hole
PEG_IN = 3.0                 # length pressed into the plate
PEG_SOCKET_D = PEG_D + 0.2
PEG_CHAMFER = 0.6
PEG_X, PEG_Y = mb.SMALL_HOLE_OFFSET

# --- Derived ------------------------------------------------------------------
SLOT_W = BEAM_W + 2 * FIT
OUT_W = SLOT_W + 2 * WALL
BACK_Z = PLATE_T + mb.LARGE_BOLT_HEAD_H + HEAD_CLR     # beam rests against this face
LIP_Z = BACK_Z + BEAM_T + 2.5                          # inner face of the lips
FRONT_Z = LIP_Z + WALL
FORK_BOT = mb.LARGE_BOLT_HEAD_AC / 2 + 1.0             # fork stays clear of the bolt head
FORK_TOP = FORK_BOT + FORK_H
PLATE_BOT = -(mb.LARGE_BOLT_HEAD_AC / 2 + 2.0)
PLATE_TOP = FORK_TOP


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
    # hollow behind the back wall saves filament; the back wall bridges it
    hollow = Rectangle(SLOT_W, BACK_Z - WALL - PLATE_T - 0.01, align=(Align.CENTER, Align.MIN))
    hollow = Pos(0, PLATE_T - 0.005) * hollow
    return outer - slot - hollow


def build_holder() -> Part:
    plate = Pos(0, (PLATE_TOP + PLATE_BOT) / 2, PLATE_T / 2) * Box(
        PLATE_W, PLATE_TOP - PLATE_BOT, PLATE_T)
    # Plane.XZ has its normal along -Y; place it at the fork top and extrude down
    fork = extrude(Plane.XZ.offset(-FORK_TOP) * fork_profile(), FORK_H)
    holder = plate + fork
    # notch for the fine-adjust wheel: left arm, left lip and the edge of the back wall
    notch_h = WHEEL_D + 1.0
    arm_x0, arm_x1 = -OUT_W / 2 - 1, -BEAM_W / 2
    holder -= Pos((arm_x0 + arm_x1) / 2, FORK_TOP - notch_h / 2 + 0.5,
                  (PLATE_T + FRONT_Z + 1) / 2 + 0.01) * Box(
        arm_x1 - arm_x0, notch_h + 1, FRONT_Z + 1 - PLATE_T)
    lip_x0, lip_x1 = -BEAM_W / 2, -(SLOT_W / 2 - LIP)
    lip_z0 = BACK_Z + BEAM_T
    holder -= Pos((lip_x0 + lip_x1) / 2, FORK_TOP - notch_h / 2 + 0.5,
                  (lip_z0 + FRONT_Z + 1) / 2) * Box(
        lip_x1 - lip_x0 + 0.01, notch_h + 1, FRONT_Z + 1 - lip_z0)
    holder -= Pos(0, 0, PLATE_T / 2) * Cylinder(BOLT_HOLE_D / 2, PLATE_T + 1)
    holder -= Pos(PEG_X, PEG_Y, PEG_IN / 2 - 0.01) * Cylinder(PEG_SOCKET_D / 2, PEG_IN + 0.02)
    # soften the outer plate edges parallel to Z
    edges = holder.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(abs(e.center().X) - PLATE_W / 2) < 1e-6)
    return fillet(edges, 2.0)


def build_peg() -> Part:
    """Printed standing on end; shown here in its installed position."""
    peg = Cylinder(PEG_D / 2, PEG_OUT + PEG_IN)
    peg = chamfer(peg.edges().filter_by(GeomType.CIRCLE), PEG_CHAMFER)
    return Pos(PEG_X, PEG_Y, (PEG_IN - PEG_OUT) / 2) * peg


def report(name: str, part: Part) -> None:
    bb = part.bounding_box()
    print(f"{name}: solids={len(part.solids())} valid={part.is_valid} "
          f"bbox={bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm "
          f"volume={part.volume / 1000:.2f} cm^3 (~{part.volume * 1.24e-3:.1f} g PLA solid)")


if __name__ == "__main__":
    holder = build_holder()
    peg = build_peg()
    report("holder", holder)
    report("peg", peg)

    out = ROOT / "exports"
    for name, part in [("caliper_holder", holder), ("caliper_holder_peg", peg)]:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))

    # preview: holder, peg, and ghosted bolt head + caliper for context
    bolt_head = Pos(0, 0, PLATE_T + mb.LARGE_BOLT_HEAD_H / 2) * Cylinder(
        mb.LARGE_BOLT_HEAD_AC / 2, mb.LARGE_BOLT_HEAD_H)
    beam_z = BACK_Z + BEAM_T / 2
    caliper = (Pos(0, FORK_TOP - 60, beam_z) * Box(BEAM_W, 150, BEAM_T)
               + Pos(0, FORK_TOP + 20, beam_z) * Box(27, 40, 10)
               + Pos(-BEAM_W / 2 - WHEEL_D / 2, FORK_TOP - WHEEL_D / 2, beam_z) * Cylinder(WHEEL_D / 2, 4)
               + Pos(0, FORK_TOP + 48, beam_z) * Box(75, 14, BEAM_T))
    blue, orange, grey, light = (0.35, 0.55, 0.85), (0.95, 0.55, 0.2), (0.4, 0.4, 0.4), (0.8, 0.8, 0.78)
    parts = [(holder, blue, 1), (peg, orange, 1)]
    ctx = parts + [(bolt_head, grey, 1), (caliper, light, 0.4)]
    render(str(out / "caliper_holder.png"), [
        ("Fig. 3a  Front 3/4", 25, -35, parts),
        ("Fig. 3b  Back (wall side), peg orange", 20, 150, parts),
        ("Fig. 3c  Side: wall left, bolt head, caliper", 0, 90, ctx),
        ("Fig. 3d  In use (caliper ghosted)", 20, -35, ctx),
    ])
    print("wrote", out)
