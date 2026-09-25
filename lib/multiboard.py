"""MultiBoard mounting interface geometry.

Every constant cites its source (official docs or a user measurement), per CLAUDE.md.
All lengths in mm.
"""
from build123d import Align, Cylinder, Helix, Part, Plane, Polygon, Pos, chamfer, sweep

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
