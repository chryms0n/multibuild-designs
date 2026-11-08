"""Locking key for the shelf-pin hooks' snap rod.

After the hook has snapped in, push this key into the slot of the snap rod from
behind the panel. Its blade fills the slot between the two barbed halves, so they
cannot be squeezed together and the barbs cannot slip back through the hole. Pull
it out by its head to remove the hook. It fits all three hooks (same snap rod).

The blade tapers (thicker at the head) so it wedges in even if the printed slot
comes out a little narrower than drawn. It is longer than the barb section, so the
barbs are blocked even if the key does not go all the way in.

Frame: the hook's model frame (see shelf_pin_hook.py), key shown in place on the
large hook's snap rod. Print orientation: flat side profile on the bed (the slot in
the hook is also drawn in the layer plane, so both come out with the same accuracy).
Exports: exports/shelf_pin_hook_lock.{stl,step,png}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[2]

from build123d import *  # noqa: E402

from shelf_pin_hook import (  # noqa: E402
    LARGE, PITCH, ROD_END_Z, SHOULDER_Z, SLOT_ROOT_Z, SLOT_W, build_hook, print_orientation,
    report, yz,
)
from lib.preview import render  # noqa: E402

BLADE_T_HEAD = SLOT_W - 0.1   # blade thickness next to the head (slot is 1.8)
BLADE_T_TIP = SLOT_W - 0.5    # ... at the blade's tip
BLADE_L = 16.0                # into the slot; covers the 6.5 mm barb section and more
BLADE_H = 3.6                 # along X; the rod is 4.0 between its flats
TIP_CHAMFER = 0.4
HEAD_W = 7.0                  # grip tab behind the rod tip (along Y)
HEAD_T = 3.0                  # along the rod axis
HEAD_R = 1.0

assert BLADE_L < SLOT_ROOT_Z - ROD_END_Z, "blade must not reach the slot root"


def build_lock(rod_x: float) -> Part:
    """Key in place in the snap rod whose axis is at X = rod_x, Y = PITCH."""
    z0 = ROD_END_Z                 # rod tip; blade goes towards the wall (+Z)
    zh, ze = z0 - HEAD_T, z0 + BLADE_L
    a, b, hw = BLADE_T_HEAD / 2, BLADE_T_TIP / 2, HEAD_W / 2
    c = TIP_CHAMFER
    # side profile in (Z, Y) around the rod axis, counter-clockwise
    prof = Polygon(
        (zh, -hw), (z0, -hw), (z0, -a), (ze - c, -b), (ze, -b + c),
        (ze, b - c), (ze - c, b), (z0, a), (z0, hw), (zh, hw), align=None)
    prof = fillet(prof.vertices().filter_by(lambda v: v.X < zh + 1e-6), HEAD_R)
    return Pos(0, PITCH, 0) * yz(prof, rod_x - BLADE_H / 2, rod_x + BLADE_H / 2)


if __name__ == "__main__":
    rod_x = LARGE.w / 2
    lock = build_lock(rod_x)
    report("shelf_pin_hook_lock (in place)", lock)
    hook = build_hook(LARGE)
    clash = hook & lock
    print(f"  overlap with the hook's snap rod: {clash.volume if clash else 0:.4f} mm^3")
    print(f"  blade {BLADE_T_HEAD:.2f} -> {BLADE_T_TIP:.2f} mm thick in a {SLOT_W} mm slot, "
          f"reaches {BLADE_L - (SHOULDER_Z - ROD_END_Z):.1f} mm past the barb shoulder")

    printed = print_orientation(lock)     # same rotation as the hook: profile on the bed
    report("shelf_pin_hook_lock (print orientation)", printed)
    out = ROOT / "exports"
    export_stl(printed, str(out / "shelf_pin_hook_lock.stl"))
    export_step(printed, str(out / "shelf_pin_hook_lock.step"))

    blue, orange = (0.35, 0.55, 0.85), (0.95, 0.55, 0.2)
    tip = hook & Pos(rod_x, PITCH, ROD_END_Z + 10) * Box(12, 12, 26)
    render(str(out / "shelf_pin_hook_lock.png"), [
        ("Fig. 12a  Key (orange) in the snap rod, side", 0, 90, [(tip, blue, 1), (lock, orange, 1)]),
        ("Fig. 12b  Same, from behind the panel", 25, 150, [(tip, blue, 1), (lock, orange, 1)]),
        ("Fig. 12c  Key alone", 30, 60, [(lock, orange, 1)]),
        ("Fig. 12d  Print orientation", 35, -30, [(printed, orange, 1)]),
    ], figsize=(20, 6))
    print("wrote", out)
