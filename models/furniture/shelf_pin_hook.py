"""Wall hook that plugs into a pair of 5 mm shelf-pin holes in a furniture panel.

Improves on the user's reference model (WallHook2.stl):
  * The upper rod is a split snap rod. It passes all the way through the 36 mm panel,
    and its two barbs spring open behind the panel so the hook cannot tilt out under
    load. To remove it, squeeze the barbs together from behind and pull.
  * The lower rod is a short plain locating pin. It takes the vertical load.
  * The hook is a 16 mm wide J-shape (the reference is 5.8 mm), sized for a loaded
    backpack (~10 kg): 25 mm gap for a padded strap, 22 mm lip. It is thickest where
    the bending is highest. The flat back face runs straight down to the bottom of
    the hook, so the panel pushes back as low as possible and the snap rod carries
    less pull.

Frame: X along the wall (part width), Y up, Z out of the wall. Lower rod axis at
Y = 0, back face of the plate (against the panel) on Z = 0, rods point into -Z.

Both rods are centred in the hook's width, so a load on the hook does not twist the
part about the vertical.

Print orientation: lying on its side, the X = 0 face on the bed (the exported STL is
already in that orientation). Then the hook outline lies in the layer plane (strong
for hook bending), the rods lie along the layers, and the snap prongs flex within
the layers. The rods (and barbs) float half the width above the bed and need
support underneath (tree supports, default 0.2 mm top gap); nothing else overhangs
more than 45 deg. The rods have flats on top and bottom: the bottom flat gives the
support a flat contact strip, and the flats face the direction with 0.5 mm clearance
in the hole, so support marks there do not affect the fit.

Exports: exports/shelf_pin_hook.{stl,step,png}
"""
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib.preview import render  # noqa: E402

# --- Furniture ------------------------------------------------------------------
HOLE_D = 5.0        # source: user ("5 millimeter holes")
PANEL_T = 36.0      # source: user, confirmed: 36 mm panel, holes go all the way through
PITCH = 32.5        # source: rod centre spacing in the user's reference WallHook2.stl;
                    # user confirmed that spacing fits their holes

# --- Rods -----------------------------------------------------------------------
ROD_D = 4.7         # reference rods measure 4.66; 0.15 mm clearance per side
ROD_FLAT = 2.0      # flats at +-2.0 mm (support side / top); 0.5 mm clearance in the hole
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
PLATE_TOP = PITCH + 6.5
TOP_R = 2.5         # top corner radius of the plate (in profile)
BED_CHAMFER = 1.2   # outline edges on the bed side (45 deg, prints without support)
# The rod builders below work around X = 0; build_hook moves them to X = w / 2.
TOP_FILLET = 2.0    # outline edges on the top side (strap-friendly)


@dataclass(frozen=True)
class HookShape:
    """Size of the J-hook and back plate; the rods are the same for every variant."""
    w: float = 16.0            # part width along X (print height)
    plate_t_top: float = 5.0   # back plate thickness at the top
    plate_t_bot: float = 9.0   # ... and where the hook starts (plate front is tapered)
    hook_y: float = 3.5        # height of the hook's inner-arc centre
    hook_ri: float = 12.5      # inner radius of the seat; gap plate-to-tip = 2 * hook_ri
    tip_t: float = 6.0         # tip leg thickness
    bot_t: float = 10.0        # hook thickness at the bottom
    lip_h: float = 22.0        # tip top above the seat bottom
    outer_shift: float = 2.0   # outer arc centre shifted towards the wall
    heel_r: float = 4.0        # round-over of the bottom corner at the back face

    # derived, all as (Z, Y) in the side profile
    @property
    def tip_h(self):           # tip round-end centre above hook_y
        return self.lip_h - self.hook_ri - self.tip_t / 2

    @property
    def inner_c(self):
        return (self.plate_t_bot + self.hook_ri, self.hook_y)

    @property
    def tip_z0(self):          # tip leg inner face
        return self.plate_t_bot + 2 * self.hook_ri

    @property
    def tip_z1(self):          # tip leg outer face
        return self.tip_z0 + self.tip_t

    @property
    def outer(self):
        """Outer arc (centre, radius): centre (oz, hook_y - e), radius R. It passes
        through (tip_z1, hook_y) and its lowest point is bot_t below the seat:
        R = hook_ri + bot_t - e and (tip_z1 - oz)^2 + e^2 = R^2 -> solve for e."""
        oz = self.inner_c[0] - self.outer_shift
        a = self.hook_ri + self.bot_t
        e = (a ** 2 - (self.tip_z1 - oz) ** 2) / (2 * a)
        return (oz, self.hook_y - e), a - e

    @property
    def bottom_y(self):        # lowest point of the hook = bottom of the back face
        (_, cy), r = self.outer
        return cy - r


LARGE = HookShape()   # 25 mm gap, 22 mm lip: loaded backpack (~10 kg)

# --- Derived (rods) ----------------------------------------------------------------
SHOULDER_Z = -(PANEL_T + SNAP_PLAY)
ROD_END_Z = SHOULDER_Z - BARB_CATCH_L - BARB_LEAD_L
SLOT_ROOT_Z = SHOULDER_Z + FLEX_L

def yz(face: Face | Sketch, x0: float, x1: float) -> Part:
    """Extrude a profile drawn in local (u, v) = (Z, Y) between X = x0 and X = x1."""
    plane = Plane(origin=(x1, 0, 0), x_dir=(0, 0, 1), z_dir=(-1, 0, 0))
    return extrude(plane * face, x1 - x0)


def body_profile(h: HookShape) -> Sketch:
    plate = Polygon((0, h.hook_y), (h.plate_t_bot, h.hook_y), (h.plate_t_top, PLATE_TOP),
                    (0, PLATE_TOP), align=None)
    plate = fillet(plate.vertices().filter_by(lambda v: v.Y > PLATE_TOP - 1e-6), TOP_R)
    big = 200
    lower_half = Pos(big / 2, h.hook_y - big / 2) * Rectangle(big, big)
    (oz, oy), r = h.outer
    outer = Pos(oz, oy) * Circle(r) & lower_half
    leg_z = (h.tip_z0 + h.tip_z1) / 2
    leg = Pos(leg_z, h.hook_y + h.tip_h / 2) * Rectangle(h.tip_t, h.tip_h)
    leg += Pos(leg_z, h.hook_y + h.tip_h) * Circle(h.tip_t / 2)
    # heel: the back face runs straight down to the hook's lowest point, where a flat
    # underside meets the outer arc tangentially
    heel = Pos(oz / 2, (h.bottom_y + h.hook_y) / 2) * Rectangle(oz, h.hook_y - h.bottom_y)
    prof = plate + outer + heel + leg - Pos(*h.inner_c) * Circle(h.hook_ri)
    corner = prof.vertices().filter_by(lambda v: abs(v.X) < 1e-6).sort_by(Axis.Y)[0]
    return fillet(corner, h.heel_r)


def flats(z0: float, z1: float) -> Part:
    """Slab that trims the rods to their two flats (X = -ROD_FLAT .. ROD_FLAT)."""
    return Pos(0, PITCH / 2, (z0 + z1) / 2) * Box(2 * ROD_FLAT, PITCH + 20, z1 - z0)


def rod_cyl(y: float, z_end: float, r: float = ROD_D / 2, y_off: float = 0.0) -> Part:
    """Cylinder along Z from Z = +1 (inside the plate) down to z_end."""
    length = 1 - z_end
    return Pos(0, y + y_off, 1 - length / 2) * Cylinder(r, length)


def build_lower_pin() -> Part:
    pin = rod_cyl(0, -PIN_L)
    pin = chamfer(pin.edges().filter_by(GeomType.CIRCLE).sort_by(Axis.Z)[0], PIN_CHAMFER)
    return pin & flats(-PIN_L - 1, 2)


def build_snap_rod() -> Part:
    rod = rod_cyl(PITCH, SHOULDER_Z)
    yc = PITCH + SLOT_W / 2
    barb = Pos(0, yc, (SHOULDER_Z + ROD_END_Z) / 2) * Cylinder(BARB_R, SHOULDER_Z - ROD_END_Z)
    # lead-in ramp, drawn in (Z, Y): full height behind the shoulder, sloping to the tip
    y_full = SLOT_W / 2 + BARB_R
    ramp = Polygon(
        (SHOULDER_Z + 0.01, PITCH), (SHOULDER_Z + 0.01, PITCH + y_full),
        (SHOULDER_Z - BARB_CATCH_L, PITCH + y_full),
        (ROD_END_Z, PITCH + BARB_TIP_Y), (ROD_END_Z, PITCH), align=None)
    barb &= yz(ramp, -ROD_FLAT - 1, ROD_FLAT + 1)
    rod += barb + mirror(barb, about=Plane.XZ.offset(-PITCH))  # second barb below the slot
    rod &= flats(ROD_END_Z - 1, 2)
    # slot between the prongs, rounded root
    slot_len = SLOT_ROOT_Z - ROD_END_Z + 1
    rod -= Pos(0, PITCH, SLOT_ROOT_Z - slot_len / 2) * Box(2 * ROD_FLAT + 2, SLOT_W, slot_len)
    rod -= Pos(0, PITCH, SLOT_ROOT_Z) * Rot(0, 90, 0) * Cylinder(SLOT_W / 2, 2 * ROD_FLAT + 2)
    return rod


def build_hook(h: HookShape = LARGE) -> Part:
    body = yz(body_profile(h), 0, h.w)
    body = chamfer(body.faces().sort_by(Axis.X)[0].edges(), BED_CHAMFER)
    body = fillet(body.faces().sort_by(Axis.X)[-1].edges(), TOP_FILLET)
    return body + Pos(h.w / 2, 0, 0) * (build_lower_pin() + build_snap_rod())


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


def panel(rod_x: float) -> Part:
    """Ghost of the furniture panel with its two through holes (preview only)."""
    p = Pos(rod_x, PITCH / 2, -PANEL_T / 2) * Box(70, 110, PANEL_T)
    for y in (0, PITCH):
        p -= Pos(rod_x, y, -PANEL_T / 2) * Cylinder(HOLE_D / 2, PANEL_T + 2)
    return p


def export_variant(name: str, h: HookShape, fig: int) -> None:
    """Check, export (print orientation) and render one hook variant.
    The preview images are labelled Fig. <fig> and Fig. <fig + 1>."""
    hook = build_hook(h)
    report(f"{name} (model frame)", hook)
    print(f"  snap shoulder at Z = {SHOULDER_Z:.2f}, rod end Z = {ROD_END_Z:.2f}, "
          f"slot root Z = {SLOT_ROOT_Z:.2f}")
    print(f"  barb reach = {SLOT_W / 2 + BARB_R:.2f} from axis (hole radius {HOLE_D / 2})")
    print(f"  gap = {2 * h.hook_ri:.2f}, lip = {h.lip_h:.2f}, seat bottom Y = "
          f"{h.hook_y - h.hook_ri:.2f}, back face down to Y = {h.bottom_y:.2f}, "
          f"load arm from wall = {h.inner_c[0]:.2f}")
    printed = print_orientation(hook)
    report(f"{name} (print orientation)", printed)

    out = ROOT / "exports"
    export_stl(printed, str(out / f"{name}.stl"))
    export_step(printed, str(out / f"{name}.step"))

    blue, light = (0.35, 0.55, 0.85), (0.8, 0.72, 0.6)
    parts = [(hook, blue, 1)]
    render(str(out / f"{name}.png"), [
        (f"Fig. {fig}a  Side profile (wall on the left)", 0, 90, parts),
        (f"Fig. {fig}b  Front 3/4", 25, 35, parts),
        (f"Fig. {fig}c  Snap tip close-up (barbs, slot)", 0, 90,
         [(hook & Pos(h.w / 2, PITCH, ROD_END_Z + 6) * Box(10, 10, 14), blue, 1)]),
        (f"Fig. {fig}d  Mounted, panel ghosted", 15, 60, parts + [(panel(h.w / 2), light, 0.25)]),
    ], figsize=(20, 7))
    render(str(out / f"{name}_print.png"), [
        (f"Fig. {fig + 1}  Print orientation (bed = XY plane)", 35, -30, [(printed, blue, 1)]),
    ], figsize=(8, 6))
    print("wrote", out)


if __name__ == "__main__":
    export_variant("shelf_pin_hook", LARGE, fig=4)
