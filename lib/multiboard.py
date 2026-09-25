"""MultiBoard mounting interface geometry.

Every constant cites its source (official docs or a user measurement), per CLAUDE.md.
All lengths in mm.
"""
from build123d import (Align, Box, Cylinder, GeomType, Helix, Part, Plane, Polygon, Pos, Rot,
                       chamfer, sweep)

# --- Grid -------------------------------------------------------------------
# Source: https://docs.multibuild.io/beginner-section/core-parts-documentation
#   "MultiBoard Tiles are multi-use boards that are based on a 25 mm grid (MU)."
GRID_PITCH = 25.0

# Small holes sit diagonally between the large holes, half a pitch away on each axis.
# Source: user (grid is periodic every 25 mm; small hole is top-left of a large hole).
SMALL_HOLE_OFFSET = (-GRID_PITCH / 2, GRID_PITCH / 2)  # (x, y) from a large hole, up = +y

# --- Tile -------------------------------------------------------------------
# Source: user caliper measurement of their tile.
TILE_THICKNESS = 6.5
# Source: user, free space between the back of their tile and the wall.
TILE_WALL_GAP = 10.0

# Small hole inner diameter. Source: user caliper measurement ("about 5 mm", imprecise).
SMALL_HOLE_D = 5.0

# --- Large Thread bolt (screws into a large hole) ---------------------------
# Source: measured by slicing the user-supplied official "Big_Thread.stl".
LARGE_THREAD_MAJOR_D = 22.25   # thread crest diameter
LARGE_THREAD_MINOR_D = 20.74   # thread root diameter
LARGE_THREAD_PITCH = 2.5
# Tooth profile, from an axial section of the same file: trapezoidal, 45 deg flanks
# (0.75 mm deep over 0.75 mm axially), 0.5 mm crest flat, 0.5 mm root flat;
# right-handed.
LARGE_THREAD_CREST_W = 0.5
LARGE_THREAD_ROOT_W = 0.5
LARGE_THREAD_SHANK_L = 20.0    # threaded length below the head
LARGE_BOLT_HEAD_AF = 24.0      # octagonal head, across flats
LARGE_BOLT_HEAD_AC = 25.98     # across corners (24 / cos 22.5 deg)
LARGE_BOLT_HEAD_H = 10.0


def large_bolt_clearance_d(clearance: float = 0.5) -> float:
    """Through-hole diameter for a Large Thread bolt passing through a part."""
    return LARGE_THREAD_MAJOR_D + 2 * clearance


def large_thread(length: float, clearance: float = 0.2, lead_in: float = 1.0) -> Part:
    """External Large Thread along +Z from z = 0 to z = length (right-handed).

    clearance: radial undersize of the whole tooth, so a printed bolt turns freely
    in the tile. The tip gets a 45 deg lead-in chamfer of `lead_in`.
    """
    r_maj = LARGE_THREAD_MAJOR_D / 2 - clearance
    r_min = LARGE_THREAD_MINOR_D / 2 - clearance
    depth = r_maj - r_min
    base_w = LARGE_THREAD_PITCH - LARGE_THREAD_ROOT_W   # tooth width at the root
    sink = 0.2                                          # tooth reaches into the core
    w0 = base_w + 2 * sink - 0.1                        # keep neighbouring turns apart
    # tooth section in the XZ plane at the helix start point (r, 0, z)
    tooth = Polygon(
        (r_min - sink, -w0 / 2), (r_min, -base_w / 2), (r_maj, -LARGE_THREAD_CREST_W / 2),
        (r_maj, LARGE_THREAD_CREST_W / 2), (r_min, base_w / 2), (r_min - sink, w0 / 2),
        align=None,
    )
    tooth = Plane.XZ * tooth
    turns_h = length + 2 * LARGE_THREAD_PITCH
    helix = Helix(LARGE_THREAD_PITCH, turns_h, r_min - sink)
    ridge = Pos(0, 0, -LARGE_THREAD_PITCH) * sweep(tooth, path=helix, is_frenet=True)
    core = Cylinder(r_min, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    envelope = Cylinder(r_maj, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    envelope = chamfer(envelope.edges().sort_by(lambda e: e.center().Z)[-1], lead_in)
    return (core + ridge) & envelope


# --- Our flush Large Thread bolt ----------------------------------------------
# Design choices (not MultiBuild dimensions): a flat flange that sits flush in a
# counterbore in the part's mounting plate, turned with a coin.
FLANGE_D = 28.0
FLANGE_T = 4.0
UNDER_HEAD = 3.0                 # plate material between the flange and the tile
CB_D = FLANGE_D + 2 * 0.4        # counterbore for the flange
CB_DEPTH = FLANGE_T + 0.2        # flange ends slightly below the plate front
MOUNT_PLATE_T = UNDER_HEAD + CB_DEPTH
FLUSH_THREAD_L = UNDER_HEAD + TILE_THICKNESS + 3.5   # 3.5 past the tile, short of the wall
FLUSH_THREAD_CLR = 0.2           # radial; first print of our own thread
BOLT_HOLE_D = large_bolt_clearance_d(0.0)  # caliper test print: +0.5/side was too loose
COIN_SLOT_W = 2.8                # euro coins are 1.67-2.33 thick
COIN_SLOT_DEPTH = 2.2

# --- Anti-rotation peg (press-fit into the plate, sits in a small hole) --------
PEG_D = SMALL_HOLE_D - 2 * 0.3   # part that goes into the tile's small hole
PEG_OUT = 4.0                    # length sticking into the tile's small hole
PEG_IN = 3.0                     # length pressed into the plate
PEG_SOCKET_D = 5.6               # caliper test print: 4.6 printed smaller than the small hole
PEG_IN_D = PEG_SOCKET_D - 0.2    # press fit (printed holes come out undersize)
PEG_CHAMFER = 0.6


def flush_bolt() -> Part:
    """Print orientation: slotted face on the bed (z = 0), thread pointing up."""
    flange = Cylinder(FLANGE_D / 2, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    flange = chamfer(flange.edges().sort_by(lambda e: e.center().Z)[-1], 0.6)  # meets the counterbore floor
    flange -= Pos(0, 0, COIN_SLOT_DEPTH / 2 - 0.01) * Box(FLANGE_D + 2, COIN_SLOT_W, COIN_SLOT_DEPTH + 0.02)
    thread = Pos(0, 0, FLANGE_T - 0.01) * large_thread(FLUSH_THREAD_L + 0.01, FLUSH_THREAD_CLR)
    return flange + thread


def installed_bolt(bolt: Part, x: float = 0, y: float = 0) -> Part:
    """Bolt as fitted in a mounting plate (back on Z = 0): flange flush, thread into the wall."""
    return Pos(x, y, MOUNT_PLATE_T - 0.2) * Rot(180, 0, 0) * bolt


def peg() -> Part:
    """Printed standing on end; returned in its installed position at the origin."""
    tip = Pos(0, 0, -PEG_OUT / 2) * Cylinder(PEG_D / 2, PEG_OUT)
    tip = chamfer(tip.edges().filter_by(GeomType.CIRCLE).sort_by(lambda e: e.center().Z)[0], PEG_CHAMFER)
    base = Pos(0, 0, PEG_IN / 2) * Cylinder(PEG_IN_D / 2, PEG_IN)
    base = chamfer(base.edges().filter_by(GeomType.CIRCLE).sort_by(lambda e: e.center().Z)[-1], 0.4)
    return tip + base


def cut_mount(part: Part, x: float, y: float, peg_xy: tuple[float, float]) -> Part:
    """Cut the bolt hole, flange counterbore and peg socket into a mounting plate
    of thickness MOUNT_PLATE_T whose back lies on Z = 0. peg_xy is absolute."""
    t = MOUNT_PLATE_T
    part -= Pos(x, y, t / 2) * Cylinder(BOLT_HOLE_D / 2, t + 1)
    part -= Pos(x, y, t - CB_DEPTH / 2 + 0.01) * Cylinder(CB_D / 2, CB_DEPTH + 0.02)
    part -= Pos(*peg_xy, PEG_IN / 2 - 0.01) * Cylinder(PEG_SOCKET_D / 2, PEG_IN + 0.02)
    return part
