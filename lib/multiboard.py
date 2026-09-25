"""MultiBoard mounting interface geometry.

Every constant cites its source (official docs or a user measurement), per CLAUDE.md.
All lengths in mm.
"""

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
LARGE_THREAD_SHANK_L = 20.0    # threaded length below the head
LARGE_BOLT_HEAD_AF = 24.0      # octagonal head, across flats
LARGE_BOLT_HEAD_AC = 25.98     # across corners (24 / cos 22.5 deg)
LARGE_BOLT_HEAD_H = 10.0


def large_bolt_clearance_d(clearance: float = 0.5) -> float:
    """Through-hole diameter for a Large Thread bolt passing through a part."""
    return LARGE_THREAD_MAJOR_D + 2 * clearance
