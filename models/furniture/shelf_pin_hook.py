"""Wall hook that plugs into a pair of 5 mm shelf-pin holes in a furniture panel.

Improves on the user's reference model (WallHook2.stl):
  * The upper rod is a split snap rod. It passes all the way through the 36 mm panel,
    and its two barbs spring open behind the panel so the hook cannot tilt out under
    load. To remove it, squeeze the barbs together from behind and pull.
  * The lower rod is a short plain locating pin. It takes the vertical load.
  * The hook is a 12 mm wide J-shape (the reference is 5.8 mm). It is thickest where
    the bending is highest and blends into the back plate. The back plate reaches
    below the hook, so the panel pushes back lower down and the snap rod carries
    less pull.

Frame: X along the wall (part width), Y up, Z out of the wall. Lower rod axis at
Y = 0, back face of the plate (against the panel) on Z = 0, rods point into -Z.

Print orientation: lying on its side, the X = 0 face on the bed (the exported STL is
already in that orientation). Then the hook outline lies in the layer plane (strong
for hook bending), the rods lie flat with layers running along them, and the snap
prongs flex within the layers. No supports needed. The rods have flats top and bottom
so they sit on the bed; this is why they are off-centre in the hook's width.

Exports: exports/shelf_pin_hook.{stl,step,png}
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib.preview import render  # noqa: E402

# --- Furniture (all to be confirmed by the user's caliper) ---------------------
HOLE_D = 5.0        # source: user ("5 millimeter holes")
PANEL_T = 36.0      # source: user ("furniture wall that is 3.6 centimeters deep"),
                    # holes assumed to go all the way through the panel
PITCH = 32.5        # source: rod centre spacing in the user's reference WallHook2.stl

# --- Rods -----------------------------------------------------------------------
ROD_D = 4.7         # reference rods measure 4.66; 0.15 mm clearance per side
ROD_FLAT = 2.0      # flats at +-2.0 mm (print bed / top); 0.5 mm clearance in the hole
ROD_X = ROD_FLAT    # rod axis height above the bed face (rods sit on the bed)
PIN_L = 15.0        # lower plain pin, length into the hole
PIN_CHAMFER = 0.8

# Snap rod: split by a slot along Y so the two prongs flex up/down (in the layer plane)
SNAP_PLAY = 0.4     # shoulder sits this far past the panel's back face
SLOT_W = 1.8        # closing the slot completely lets each prong move SLOT_W / 2
FLEX_L = 16.0       # slot root -> barb shoulder (spring length of each prong)
BARB_R = 2.4        # barb section = circle of this radius, shifted out by SLOT_W / 2,
                    # so with the slot closed it fits a 4.8 mm circle
BARB_CATCH_L = 1.5  # straight part of the barb behind the shoulder
BARB_LEAD_L = 5.0   # lead-in ramp to the tip
BARB_TIP_Y = 1.9    # ramp height at the very tip (from the rod axis)

# --- Body -----------------------------------------------------------------------
W = 12.0            # part width along X (print height)
PLATE_T_TOP = 5.0   # back plate thickness at the top
PLATE_T_BOT = 7.0   # ... and where the hook starts (plate front is tapered)
PLATE_TOP = PITCH + 6.5
TOP_R = 2.5         # top corner radius of the plate (in profile)
HOOK_Y = 3.0        # height of the hook's inner-arc centre (seat bottom = HOOK_Y - HOOK_RI)
HOOK_RI = 10.0      # inner radius of the hook seat; gap plate-to-tip = 2 * HOOK_RI = 20 mm
TIP_T = 5.5         # tip leg thickness
BOT_T = 9.0         # hook thickness at the bottom
TIP_H = 8.0         # tip top (round end centre) above HOOK_Y
OUTER_SHIFT = 2.0   # outer arc centre shifted towards the wall -> thicker near the plate
PIVOT_R = 2.0       # round-over where the hook's underside meets the back face
EDGE_CHAMFER = 0.8  # on the two flat faces' outline (bed side and top side)

# --- Derived ----------------------------------------------------------------------
SHOULDER_Z = -(PANEL_T + SNAP_PLAY)
ROD_END_Z = SHOULDER_Z - BARB_CATCH_L - BARB_LEAD_L
SLOT_ROOT_Z = SHOULDER_Z + FLEX_L
INNER_C = (PLATE_T_BOT + HOOK_RI, HOOK_Y)         # (Z, Y) in the profile
TIP_Z0 = PLATE_T_BOT + 2 * HOOK_RI                # tip leg inner face
TIP_Z1 = TIP_Z0 + TIP_T                           # tip leg outer face
# outer arc: centre (OUTER_Z, HOOK_Y - e), radius R; passes through (TIP_Z1, HOOK_Y)
# and its lowest point is BOT_T below the seat:  R = HOOK_RI + BOT_T - e,
# (TIP_Z1 - OUTER_Z)^2 + e^2 = R^2  ->  solve for e
OUTER_Z = INNER_C[0] - OUTER_SHIFT
_a = HOOK_RI + BOT_T
OUTER_E = (_a ** 2 - (TIP_Z1 - OUTER_Z) ** 2) / (2 * _a)
OUTER_R = _a - OUTER_E
OUTER_C = (OUTER_Z, HOOK_Y - OUTER_E)
PIVOT_Y = OUTER_C[1] - (OUTER_R ** 2 - OUTER_Z ** 2) ** 0.5   # lowest point of the back face


def yz(face: Face | Sketch, x0: float, x1: float) -> Part:
    """Extrude a profile drawn in local (u, v) = (Z, Y) between X = x0 and X = x1."""
    plane = Plane(origin=(x1, 0, 0), x_dir=(0, 0, 1), z_dir=(-1, 0, 0))
    return extrude(plane * face, x1 - x0)


def body_profile() -> Sketch:
    plate = Polygon((0, HOOK_Y), (PLATE_T_BOT, HOOK_Y), (PLATE_T_TOP, PLATE_TOP),
                    (0, PLATE_TOP), align=None)
    plate = fillet(plate.vertices().filter_by(lambda v: v.Y > PLATE_TOP - 1e-6), TOP_R)
    big = 200
    lower_half = Pos(big / 2, HOOK_Y - big / 2) * Rectangle(big, big)
    outer = Pos(*OUTER_C) * Circle(OUTER_R) & lower_half
    leg = Pos((TIP_Z0 + TIP_Z1) / 2, HOOK_Y + TIP_H / 2) * Rectangle(TIP_T, TIP_H)
    leg += Pos((TIP_Z0 + TIP_Z1) / 2, HOOK_Y + TIP_H) * Circle(TIP_T / 2)
    prof = plate + outer + leg - Pos(*INNER_C) * Circle(HOOK_RI)
    # round the corner where the hook's underside meets the back face (the pivot)
    pivot = prof.vertices().filter_by(lambda v: abs(v.X) < 1e-6).sort_by(Axis.Y)[0]
    return fillet(pivot, PIVOT_R)


def flats(z0: float, z1: float) -> Part:
    """Slab that trims the rods to their two flats (X = 0 .. 2 * ROD_FLAT)."""
    return Pos(ROD_X, PITCH / 2, (z0 + z1) / 2) * Box(2 * ROD_FLAT, PITCH + 20, z1 - z0)


def rod_cyl(y: float, z_end: float, r: float = ROD_D / 2, y_off: float = 0.0) -> Part:
    """Cylinder along Z from Z = +1 (inside the plate) down to z_end."""
    length = 1 - z_end
    return Pos(ROD_X, y + y_off, 1 - length / 2) * Cylinder(r, length)


def build_lower_pin() -> Part:
    pin = rod_cyl(0, -PIN_L)
    pin = chamfer(pin.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[0], PIN_CHAMFER)
    return pin & flats(-PIN_L - 1, 2)


def build_snap_rod() -> Part:
    rod = rod_cyl(PITCH, SHOULDER_Z)
    yc = PITCH + SLOT_W / 2
    barb = Pos(ROD_X, yc, (SHOULDER_Z + ROD_END_Z) / 2) * Cylinder(BARB_R, SHOULDER_Z - ROD_END_Z)
    # lead-in ramp, drawn in (Z, Y): full height behind the shoulder, sloping to the tip
    y_full = SLOT_W / 2 + BARB_R
    ramp = Polygon(
        (SHOULDER_Z + 0.01, PITCH), (SHOULDER_Z + 0.01, PITCH + y_full),
        (SHOULDER_Z - BARB_CATCH_L, PITCH + y_full),
        (ROD_END_Z, PITCH + BARB_TIP_Y), (ROD_END_Z, PITCH), align=None)
    barb &= yz(ramp, -1, 2 * ROD_FLAT + 1)
    rod += barb + mirror(barb, about=Plane.XZ.offset(-PITCH))  # second barb below the slot
    rod &= flats(ROD_END_Z - 1, 2)
    # slot between the prongs, rounded root
    slot_len = SLOT_ROOT_Z - ROD_END_Z + 1
    rod -= Pos(ROD_X, PITCH, SLOT_ROOT_Z - slot_len / 2) * Box(2 * ROD_FLAT + 2, SLOT_W, slot_len)
    rod -= Pos(ROD_X, PITCH, SLOT_ROOT_Z) * Rot(0, 90, 0) * Cylinder(SLOT_W / 2, 2 * ROD_FLAT + 2)
    return rod


def build_hook() -> Part:
    body = yz(body_profile(), 0, W)
    side_edges = body.faces().sort_by(Axis.X)[0].edges() + body.faces().sort_by(Axis.X)[-1].edges()
    body = chamfer(side_edges, EDGE_CHAMFER)
    return body + build_lower_pin() + build_snap_rod()


def print_orientation(part: Part) -> Part:
    """X = 0 face down on the bed."""
    p = Rot(0, -90, 0) * part
    bb = p.bounding_box()
    return Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * p


def report(name: str, part: Part) -> None:
    bb = part.bounding_box()
    print(f"{name}: solids={len(part.solids())} valid={part.is_valid} "
          f"bbox={bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm "
          f"volume={part.volume / 1000:.2f} cm^3 (~{part.volume * 1.24e-3:.1f} g PLA solid)")


def panel() -> Part:
    """Ghost of the furniture panel with its two through holes (preview only)."""
    p = Pos(ROD_X, PITCH / 2, -PANEL_T / 2) * Box(70, 110, PANEL_T)
    for y in (0, PITCH):
        p -= Pos(ROD_X, y, -PANEL_T / 2) * Cylinder(HOLE_D / 2, PANEL_T + 2)
    return p


if __name__ == "__main__":
    hook = build_hook()
    report("shelf_pin_hook (model frame)", hook)
    print(f"  snap shoulder at Z = {SHOULDER_Z:.2f}, rod end Z = {ROD_END_Z:.2f}, "
          f"slot root Z = {SLOT_ROOT_Z:.2f}")
    print(f"  barb reach = {SLOT_W / 2 + BARB_R:.2f} from axis (hole radius {HOLE_D / 2})")
    print(f"  outer arc centre {OUTER_C[0]:.2f}, {OUTER_C[1]:.2f}  R = {OUTER_R:.2f}; "
          f"back face reaches down to Y = {PIVOT_Y:.2f}")
    printed = print_orientation(hook)
    report("shelf_pin_hook (print orientation)", printed)

    out = ROOT / "exports"
    export_stl(printed, str(out / "shelf_pin_hook.stl"))
    export_step(printed, str(out / "shelf_pin_hook.step"))

    blue, light = (0.35, 0.55, 0.85), (0.8, 0.72, 0.6)
    parts = [(hook, blue, 1)]
    render(str(out / "shelf_pin_hook.png"), [
        ("Fig. 2a  Side profile (wall on the left)", 0, 90, parts),
        ("Fig. 2b  Front 3/4", 25, 35, parts),
        ("Fig. 2c  Snap tip close-up (barbs, slot)", 0, 90,
         [(hook & Pos(ROD_X, PITCH, ROD_END_Z + 6) * Box(10, 10, 14), blue, 1)]),
        ("Fig. 2d  Mounted, panel ghosted", 15, 60, parts + [(panel(), light, 0.25)]),
    ], figsize=(20, 7))
    render(str(out / "shelf_pin_hook_print.png"), [
        ("Fig. 3  Print orientation (bed = XY plane)", 35, -30, [(printed, blue, 1)]),
    ], figsize=(8, 6))
    print("wrote", out)
