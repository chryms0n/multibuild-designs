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

Exports: exports/caliper_holder.{stl,step}, exports/caliper_holder_peg.{stl,step},
exports/caliper_holder_bolt.{stl,step}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib import multiboard as mb  # noqa: E402
from lib.preview import render  # noqa: E402

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
BOLT_HOLE_D = mb.large_bolt_clearance_d(0.0)  # test print: +0.5/side was too loose

# --- Bolt (flat head, flush in the plate) -------------------------------------
FLANGE_D = 28.0
FLANGE_T = 4.0
UNDER_HEAD = 3.0             # plate material between the flange and the tile
CB_D = FLANGE_D + 2 * 0.4    # counterbore for the flange
CB_DEPTH = FLANGE_T + 0.2    # flange ends slightly below the plate front
THREAD_L = UNDER_HEAD + mb.TILE_THICKNESS + 3.5  # 3.5 past the tile, well short of the wall
THREAD_CLR = 0.2             # radial; first print of our own thread, adjust after testing
COIN_SLOT_W = 2.8            # euro coins are 1.67-2.33 thick
COIN_SLOT_DEPTH = 2.2

# --- Peg ----------------------------------------------------------------------
PEG_D = mb.SMALL_HOLE_D - 2 * 0.3   # part that goes into the tile's small hole
PEG_OUT = 4.0                # length sticking into the tile's small hole
PEG_IN = 3.0                 # length pressed into the plate
PEG_SOCKET_D = 5.6           # test print: 4.6 printed smaller than the tile's small hole
PEG_IN_D = PEG_SOCKET_D - 0.2  # press fit (printed holes come out undersize)
PEG_CHAMFER = 0.6
PEG_X, PEG_Y = mb.SMALL_HOLE_OFFSET

# --- Derived ------------------------------------------------------------------
PLATE_T = UNDER_HEAD + CB_DEPTH
SLOT_W = BEAM_W + 2 * FIT
OUT_W = SLOT_W + 2 * WALL
BACK_Z = PLATE_T + BEAM_STANDOFF                       # beam rests against this face
LIP_Z = BACK_Z + BEAM_T + 2.5                          # inner face of the lips
FRONT_Z = LIP_Z + WALL
FORK_TOP = -(CB_D / 2 + 1.5)                           # fork stays below the flange
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
    holder -= Pos(0, 0, PLATE_T / 2) * Cylinder(BOLT_HOLE_D / 2, PLATE_T + 1)
    holder -= Pos(0, 0, PLATE_T - CB_DEPTH / 2 + 0.01) * Cylinder(CB_D / 2, CB_DEPTH + 0.02)
    holder -= Pos(PEG_X, PEG_Y, PEG_IN / 2 - 0.01) * Cylinder(PEG_SOCKET_D / 2, PEG_IN + 0.02)
    # soften the outer plate edges parallel to Z
    edges = holder.edges().filter_by(Axis.Z).filter_by(
        lambda e: abs(abs(e.center().X) - PLATE_W / 2) < 1e-6)
    return fillet(edges, CORNER_R)


def build_peg() -> Part:
    """Printed standing on end; shown here in its installed position."""
    tip = Pos(0, 0, -PEG_OUT / 2) * Cylinder(PEG_D / 2, PEG_OUT)
    tip = chamfer(tip.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[0], PEG_CHAMFER)
    base = Pos(0, 0, PEG_IN / 2) * Cylinder(PEG_IN_D / 2, PEG_IN)
    base = chamfer(base.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[-1], 0.4)
    return Pos(PEG_X, PEG_Y, 0) * (tip + base)


def build_bolt() -> Part:
    """Print orientation: slotted face on the bed (z = 0), thread pointing up."""
    flange = Cylinder(FLANGE_D / 2, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    flange = chamfer(flange.edges().sort_by(Axis.Z)[-1], 0.6)   # top rim, meets the counterbore floor
    flange -= Pos(0, 0, COIN_SLOT_DEPTH / 2 - 0.01) * Box(FLANGE_D + 2, COIN_SLOT_W, COIN_SLOT_DEPTH + 0.02)
    thread = Pos(0, 0, FLANGE_T - 0.01) * mb.large_thread(THREAD_L + 0.01, THREAD_CLR)
    return flange + thread


def installed(bolt: Part) -> Part:
    """Bolt as fitted: flange in the counterbore, thread towards the wall."""
    return Pos(0, 0, PLATE_T - 0.2) * Rot(180, 0, 0) * bolt


def report(name: str, part: Part) -> None:
    bb = part.bounding_box()
    print(f"{name}: solids={len(part.solids())} valid={part.is_valid} "
          f"bbox={bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm "
          f"volume={part.volume / 1000:.2f} cm^3 (~{part.volume * 1.24e-3:.1f} g PLA solid)")


def wheel() -> Part:
    """Approximate fine-adjust wheel, resting on the notch floor (for checks/preview)."""
    return Pos(WHEEL_X, FORK_TOP - WHEEL_DROP + WHEEL_D / 2, BACK_Z + BEAM_T / 2) * Cylinder(
        WHEEL_D / 2, WHEEL_T)


def tab_path() -> Part:
    """Volume swept by the guide tab when the caliper is lifted through the fork."""
    return Pos(0, FORK_TOP - FORK_H / 2, BACK_Z - TAB_H / 2) * Box(TAB_W, FORK_H + 4, TAB_H)


if __name__ == "__main__":
    holder = build_holder()
    peg = build_peg()
    bolt = build_bolt()
    report("holder", holder)
    report("peg", peg)
    report("bolt", bolt)

    out = ROOT / "exports"
    for name, part in [("caliper_holder", holder), ("caliper_holder_peg", peg),
                       ("caliper_holder_bolt", bolt)]:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))

    # preview: holder, peg, bolt (installed) and ghosted caliper for context
    bolt_in = installed(bolt)
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
