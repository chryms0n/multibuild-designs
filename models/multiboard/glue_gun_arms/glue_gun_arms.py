"""Two arms that hold a hot-glue gun on the MultiBoard, one each side of the trigger.

The gun hangs with its side against the wall, in the attitude of the user's side
photo: nozzle down-left, handle down-right, trigger hanging free between the arms.
Each arm is a plate bolted into a large hole, with a cradle in front: a U channel
that runs along the gun's underside and rises LIP_H up both of the gun's sides
(the plate behind it, a lip in front), so the gun cannot tip off the wall.
  - left arm: under the barrel and the flat bottom of the nose, around the corner
    between them
  - right arm: under the front of the handle and into the corner at the knob on
    the handle's end
With both corners caught the gun cannot slide off either; it lifts straight up.

How the cradles follow the gun
  - Side outline: traced from the side photo (the gun is the dark, unsaturated
    pixels; iso-contour of the smoothed mask) rather than picked by hand, then
    corrected for perspective. The photo was taken from ~26 cm, so parts of the
    silhouette that sit above the table look up to 5 % too large (see
    perspective_correct).
  - The four faces the cradles touch are straight in side view (line fits leave
    at most 0.2-0.5 mm residual), so each cradle runs along two fitted lines,
    mitred where they meet.
  - Cross-section: the front photo shows the barrel's underside is a half-round
    across the gun's thickness, and the handle's front is flat with small edge
    rounds. Each cradle's inside is exactly that section plus clearance, swept
    along the lines: a half-pipe under the barrel, a rounded U under the handle.

The two bolt holes sit on the same 25 mm grid (printed at run time); mount the arms
in exactly those holes relative to each other. Each arm needs one flush bolt and
one peg (the same parts as the caliper holder).

Print: each arm stands on edge, so every layer is a slice across the U channel and
its walls can be tall without overhangs; holes in the plate get teardrop roofs.
The arm STL/STEP files are exported in that orientation (bed at z = 0). Use a brim.

Frame (modelling): X along the wall, Y up, Z out of the wall; back of the plates
on Z = 0.

Exports (to exports/glue_gun_arms/): glue_gun_arms_{left,right,bolt,peg}.{stl,step},
glue_gun_arms.png, glue_gun_arms_section.png
"""
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib import multiboard as mb  # noqa: E402
from lib.preview import render, report  # noqa: E402

# --- Glue gun, from the user's photos -------------------------------------------
# Side photo (1269 x 952 px): the gun lies on its side next to the caliper, whose cm
# scale gives 3.48 px/mm at the scale's face. Outlines traced from the photo and
# simplified to 1 px; image pixels, y down.
PX_PER_MM = 3.48
OUTLINE_PX = [
    (236.6, 611.0), (240.5, 605.0), (246.1, 601.0), (249.1, 593.0), (245.6, 591.0), (243.8, 587.0),
    (248.5, 570.0), (247.8, 559.0), (253.0, 552.5), (256.0, 551.2), (262.0, 557.5), (265.0, 557.9),
    (266.2, 553.0), (258.2, 548.0), (264.0, 541.6), (266.0, 541.6), (275.0, 551.1), (276.5, 547.0),
    (281.8, 543.0), (281.2, 540.0), (277.0, 535.9), (272.0, 537.4), (267.0, 534.5), (265.9, 532.0),
    (268.0, 529.6), (274.0, 532.4), (278.0, 531.6), (285.0, 537.1), (291.0, 534.1), (294.1, 530.0),
    (291.3, 524.0), (291.2, 513.0), (293.0, 510.9), (296.0, 510.8), (296.2, 507.0), (294.0, 503.0),
    (288.3, 499.0), (281.0, 496.5), (279.6, 494.0), (280.5, 492.0), (391.0, 366.3), (490.5, 250.0),
    (495.0, 247.3), (497.0, 242.7), (525.5, 209.0), (536.0, 199.3), (538.0, 195.5), (545.0, 191.3),
    (547.6, 184.0), (552.0, 182.3), (552.6, 178.0), (586.5, 138.0), (591.0, 135.2), (591.8, 132.0),
    (597.5, 125.0), (601.0, 121.6), (604.0, 120.9), (605.5, 116.0), (610.0, 111.6), (614.0, 110.5),
    (618.0, 104.2), (633.0, 106.8), (640.0, 102.8), (653.0, 103.8), (656.0, 105.6), (670.5, 120.0),
    (673.0, 126.3), (686.0, 136.7), (695.0, 156.5), (727.3, 179.0), (740.2, 192.0), (742.4, 199.0),
    (741.2, 205.0), (728.8, 236.0), (722.5, 256.0), (722.5, 268.0), (724.8, 277.0), (730.8, 288.0),
    (737.0, 294.5), (745.0, 300.2), (777.0, 316.3), (987.0, 418.7), (995.0, 425.7), (1000.5, 438.0),
    (1000.5, 526.0), (992.2, 586.0), (990.5, 590.0), (988.0, 591.5), (953.0, 593.5), (949.0, 595.5),
    (938.0, 594.5), (932.0, 591.5), (921.0, 592.1), (918.2, 589.0), (917.4, 569.0), (913.6, 564.0),
    (916.2, 555.0), (911.6, 550.0), (911.8, 546.0), (909.0, 541.7), (898.3, 532.0), (800.0, 484.8),
    (785.0, 480.2), (781.8, 477.0), (780.3, 472.0), (770.0, 465.8), (626.0, 396.8), (613.0, 393.5),
    (605.0, 393.5), (593.0, 396.8), (586.0, 400.8), (579.8, 407.0), (580.4, 416.0), (578.5, 420.0),
    (569.3, 428.0), (559.7, 433.0), (553.0, 439.5), (455.5, 554.0), (442.0, 567.2), (416.0, 567.5),
    (396.0, 565.5), (347.0, 565.5), (341.0, 566.8), (326.0, 580.5), (321.0, 582.5), (302.0, 602.2),
    (287.0, 608.2), (274.0, 610.8), (257.0, 621.2), (242.0, 621.8), (239.8, 620.0),
]
TRIGGER_PX = [
    (606.0, 395.8), (618.0, 396.5), (628.0, 399.8), (635.0, 404.2), (645.0, 407.8), (736.0, 450.8),
    (779.3, 473.0), (780.2, 475.0), (775.2, 483.0), (760.0, 501.5), (741.0, 520.1), (730.0, 525.8),
    (725.0, 529.7), (709.0, 536.2), (704.0, 536.8), (698.0, 540.2), (682.0, 544.8), (676.0, 548.2),
    (657.0, 552.8), (654.0, 555.2), (647.0, 557.2), (643.0, 556.2), (640.5, 554.0), (635.5, 545.0),
    (630.8, 542.0), (630.2, 537.0), (628.5, 534.0), (627.5, 490.0), (623.5, 464.0), (624.5, 451.0),
    (622.2, 444.0), (619.0, 437.7), (612.0, 430.5), (603.0, 425.8), (592.0, 423.2), (586.5, 419.0),
    (581.5, 411.0), (582.0, 406.7), (588.0, 401.8), (596.0, 397.8),
]
BARREL_MAX_X_PX = 590        # outline left of the trigger belongs to the barrel
# Straight runs of the outline the cradles touch, as pixel boxes (x range, y range)
FACES_PX = {
    "nose": ((350, 437), (560, 572)),      # flat bottom of the nose
    "barrel": ((450, 552), (438, 562)),    # barrel underside, nose to trigger
    "handle": ((790, 898), (478, 534)),    # handle front, trigger to knob
    "knob": ((911, 920), (556, 586)),      # face of the knob, towards the trigger
}
# Camera: the user's photos come from a Pixel 8 main camera (EXIF: f = 6.9 mm,
# 2.4 um pixels at 4080 px wide), i.e. 894 px at this image size; principal point
# at the image centre. Its height follows from the caliper scale.
FOCAL_PX = 894.0
CENTRE_PX = (634.5, 475.5)
SCALE_H = 3.5                # height of the caliper's scale above the table
CAMERA_H = FOCAL_PX / PX_PER_MM + SCALE_H
# Front photo (looking into the nozzle): the barrel's underside is a half-round
# across the thickness, the handle's front flat with small edge rounds (shading).
# The thicknesses are upper bounds: perspective can only have made them look
# larger, and a loose channel still holds the gun where a tight one would not fit.
T_BARREL = 34.0
T_HANDLE = 33.0
HANDLE_R = 4.0
# The knob's section is not visible in either photo. If it is round rather than flat
# like the handle, its face sits up to ~2.5 mm further out than traced.
KNOB_EXTRA = 2.0

# --- Design choices -------------------------------------------------------------
CLR = 1.0                    # clearance all round the gun's section
FLOOR = 4.0                  # cradle wall under the gun (10 lines of 0.4 mm)
LIP_T = 3.2                  # lip in front of the gun (8 lines)
LIP_H = 22.0                 # how far the U rises up the gun's sides from its underside
LEAD = 2.0                   # 45 deg lead-in on the lip's edge
NOSE_L = 12.0                # left cradle: along the nose bottom from the corner
BARREL_L = 42.0              # left cradle: along the barrel underside from the corner
HANDLE_L = 34.0              # right cradle: along the handle front from the corner
KNOB_L = 9.0                 # right cradle: down the knob face from the corner
PLATE_T = mb.MOUNT_PLATE_T
PLATE_MARGIN = 4.6           # plate material around the counterbore
PLATE_ROUND = 4.0
BOLT_CLEAR = 6.0             # counterbore to cradle: room for fingers and a coin
PRINT_MARGIN = 5.0           # keep every cradle face at least this far inside 45 deg
Z_MID = PLATE_T + CLR + T_BARREL / 2          # the gun's mid-plane


# --- Outline: photo pixels -> millimetres ---------------------------------------
def outward_normals(p: np.ndarray) -> np.ndarray:
    x, y = p[:, 0], p[:, 1]
    ccw = np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y) > 0
    t = np.roll(p, -1, 0) - np.roll(p, 1, 0)
    t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.c_[t[:, 1], -t[:, 0]]
    return n if ccw else -n


def to_mm(px: np.ndarray) -> np.ndarray:
    """Pixels -> mm at the caliper scale's height, y up, origin under the camera."""
    return np.c_[(px[:, 0] - CENTRE_PX[0]) / PX_PER_MM, -(px[:, 1] - CENTRE_PX[1]) / PX_PER_MM]


def magnification(h: float) -> float:
    """How much larger than at the caliper scale something at height h looks."""
    return (CAMERA_H - SCALE_H) / (CAMERA_H - h)


def perspective_correct(px: np.ndarray) -> np.ndarray:
    """Outline pixels -> mm (y up, origin under the camera), perspective removed.

    A silhouette point seen at distance x from the camera axis lies at height h on
    the gun and really at x / magnification(h). The barrel's round underside forms
    its silhouette at mid-thickness; the handle's flat front, seen from outside,
    at its lower edge. The scale is blended across the trigger."""
    w = np.clip((px[:, 0] - BARREL_MAX_X_PX) / 40 + 0.5, 0, 1)
    scale = (1 - w) / magnification(T_BARREL / 2) + w / magnification(HANDLE_R)
    return to_mm(px) * scale[:, None]


def resample(px: np.ndarray, step: float = 0.5) -> np.ndarray:
    closed = np.vstack([px, px[:1]])
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(closed, axis=0), axis=1))]
    t = np.arange(0, s[-1], step)
    return np.c_[np.interp(t, s, closed[:, 0]), np.interp(t, s, closed[:, 1])]


def fit_line(pts: np.ndarray):
    mu = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - mu)
    resid = (pts - mu) @ vt[1]
    return mu, vt[0], np.abs(resid).max()


def intersect(a, b) -> np.ndarray:
    (p, d), (q, e) = a, b
    s = np.linalg.solve(np.array([d, -e]).T, q - p)
    return p + s[0] * d


def v2(p) -> Vector:
    return Vector(float(p[0]), float(p[1]), 0)


# --- Cross-sections (x = outward from the gun's outer line, y = height above Z_MID)
def gun_section(kind: str, grow: float) -> Face:
    """The gun's section near its underside, grown by `grow` all round."""
    deep = LIP_H + 20
    if kind == "barrel":
        r = T_BARREL / 2
        return Pos(-r, 0) * Circle(r + grow) \
            + Pos(-(deep + r) / 2, 0) * Rectangle(deep - r, 2 * (r + grow))
    r, h = HANDLE_R, T_HANDLE / 2
    body = Pos(-(deep + r) / 2, 0) * Rectangle(deep - r, 2 * (h + grow)) \
        + Pos((grow - deep) / 2, 0) * Rectangle(deep + grow, 2 * (h - r))
    return body + Pos(-r, h - r) * Circle(r + grow) + Pos(-r, r - h) * Circle(r + grow)


def cradle_section(kind: str) -> Face:
    """The U channel's section: floor, lip and the strip on the plate, around the gun."""
    t = T_BARREL if kind == "barrel" else T_HANDLE
    back, lip_in = PLATE_T - 0.01 - Z_MID, t / 2 + CLR
    front = lip_in + LIP_T
    box = Pos((CLR + FLOOR - LIP_H) / 2, (back + front) / 2) * Rectangle(CLR + FLOOR + LIP_H, front - back)
    lead = Polygon((-LIP_H - 1, lip_in - 1), (-LIP_H + LEAD + 1, lip_in - 1),
                   (-LIP_H - 1, lip_in + LEAD + 1), align=None)
    return box - gun_section(kind, CLR) - lead


def swept(section: Face, corner, d: Vector, n: Vector, s0: float, s1: float) -> Part:
    """section swept straight along d, over s0..s1 measured from corner."""
    z_dir = n.cross(Vector(0, 0, 1))          # makes the section's y axis +Z
    start = s0 if z_dir.dot(d) > 0 else s1
    plane = Plane(origin=v2(corner) + d * start + Vector(0, 0, Z_MID), x_dir=n, z_dir=z_dir)
    return extrude(plane * section, s1 - s0)


class Cradle:
    """A cradle along two straight faces of the gun that meet at `corner`.
    faces: [(direction away from the corner, outward normal, length)]; the first
    one is the end that sits on the print bed."""

    def __init__(self, kind, corner, faces):
        self.kind, self.corner, self.faces = kind, corner, faces
        self.up = print_up(faces)

    def solid(self, extra: float = 0.0) -> Part:
        """The cradle, its bed end lengthened by `extra`, mitred at the corner."""
        (da, na, la), (db, nb, lb) = self.faces
        section = cradle_section(self.kind)
        out = None
        for d, n, length, other in ((da, na, la + extra, db), (db, nb, lb, da)):
            piece = swept(section, self.corner, d, n, -30, length)
            mitre = Plane(origin=v2(self.corner), z_dir=(d - other).normalized())
            piece = split(piece, bisect_by=mitre, keep=Keep.TOP)
            out = piece if out is None else out + piece
        return out

    def footprint(self, extra: float = 0.0):
        """Corners of the cradle's outline on the wall (it is convex per face)."""
        pts = []
        (da, na, la), (db, nb, lb) = self.faces
        for d, n, length, other, on in ((da, na, la + extra, db, nb), (db, nb, lb, da, na)):
            for t in (-LIP_H, CLR + FLOOR):
                pts.append(v2(self.corner) + d * length + n * t)
                # where this edge meets the mitre: same offset from both faces
                pts.append(v2(self.corner) + n * t + d * mitre_s(d, n, other, on, t))
        return pts

    def bed_extra(self, h_bed: float) -> float:
        """How much longer the bed end must be to reach below the bed plane."""
        d, n, length = self.faces[0]
        top = max((v2(self.corner) + d * length + n * t).dot(self.up) for t in (-LIP_H, CLR + FLOOR))
        return (top - h_bed) / -d.dot(self.up) + 1.0


def mitre_s(d, n, other_d, other_n, t):
    """Distance along d from the corner to the mitre, at offset t from the face."""
    # point c + n t + d s lies on the bisector: offset t from the other face too
    return (t - t * n.dot(other_n)) / d.dot(other_n) if abs(d.dot(other_n)) > 1e-9 else 0.0


def print_up(faces) -> Vector:
    """Direction in the wall plane that points up on the bed.

    Standing on edge, a cradle face prints without overhang while its normal stays
    within 45 deg of level (less PRINT_MARGIN). Within that, level is turned as
    close as possible to the bed end's normal, so that end lies nearly flat."""
    (da, na, _), (_, nb, _) = faces
    a = math.degrees(math.atan2(na.Y, na.X))
    b = a + (math.degrees(math.atan2(nb.Y, nb.X)) - a + 180) % 360 - 180
    lim = 45 - PRINT_MARGIN
    lo, hi = max(a, b) - lim, min(a, b) + lim
    assert lo <= hi, "cradle faces too far apart to print on edge"
    level = math.radians(min(max(a, lo), hi))
    up = Vector(-math.sin(level), math.cos(level), 0)
    return up if da.dot(up) < 0 else -up


def printable_outline(points, up: Vector, h_bed: float) -> Face:
    """Rounded convex outline around points that prints standing on edge: its lower
    sides run no flatter than 45 deg down to a flat edge on the bed."""
    w = Vector(up.Y, -up.X, 0)
    pts = list(points)
    for side in (1, -1):
        m = (-up + w * side).normalized()     # outward normal of a 45 deg lower side
        sigma = max(p.dot(m) for p in points)
        h = h_bed - PLATE_ROUND
        pts.append(up * h + w * ((sigma - h * up.dot(m)) / w.dot(m)))
    hull = polygon(hull2d(pts))
    return offset(offset(hull, -PLATE_ROUND, kind=Kind.ARC), PLATE_ROUND, kind=Kind.ARC).faces()[0]


def polygon(points) -> Face:
    """Face through points, wound counter-clockwise so it faces +Z and extrudes up."""
    pts = [(p.X, p.Y) for p in points]
    area2 = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return Polygon(*(pts if area2 > 0 else pts[::-1]), align=None)


def hull2d(points):
    pts = sorted(set((round(p.X, 4), round(p.Y, 4)) for p in points))

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
        return out
    lower, upper = half(pts), half(reversed(pts))
    return [Vector(*p) for p in lower[:-1] + upper[:-1]]


def circle_pts(c: Vector, r: float, n: int = 48):
    return [c + Vector(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def clear_of(points, c: Vector) -> bool:
    disc = Pos(c.X, c.Y) * Circle(mb.CB_D / 2 + BOLT_CLEAR)
    return (disc & polygon(hull2d(points))).area < 1e-6


def bolt_target(points) -> Vector:
    """Directly above the cradle, with the counterbore clear of it."""
    xs, ys = [p.X for p in points], [p.Y for p in points]
    return Vector((min(xs) + max(xs)) / 2, max(ys) + mb.CB_D / 2 + BOLT_CLEAR)


def place_bolts(left_pts, right_pts):
    """Left bolt above the left cradle; right bolt on the same grid, nearest above the right one."""
    left = bolt_target(left_pts)
    target = bolt_target(right_pts)
    best = None
    for i in range(-10, 11):
        for j in range(-10, 11):
            c = left + Vector(i, j) * mb.GRID_PITCH
            if not clear_of(right_pts, c) or c.Y < target.Y - 1e-6:
                continue
            d = (c - target).length
            if best is None or d < best[0]:
                best = (d, c)
    return left, best[1]


def pick_peg(points, bolt: Vector) -> Vector:
    """Small hole (diagonal neighbour of the large hole) that keeps the plate smallest."""
    base = list(points) + circle_pts(bolt, mb.CB_D / 2 + PLATE_MARGIN)
    best = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = bolt + Vector(sx * mb.GRID_PITCH / 2, sy * mb.GRID_PITCH / 2)
            area = polygon(hull2d(base + circle_pts(p, mb.PEG_SOCKET_D / 2 + 2.4, 24))).area
            if best is None or area < best[0]:
                best = (area, p)
    return best[1]


def build_arm(cradle: Cradle, bolt: Vector):
    """Plate + cradle + mount, cut flat on the bed plane. Returns (arm, peg position)."""
    up = cradle.up
    peg_at = pick_peg(cradle.footprint(), bolt)
    around = circle_pts(bolt, mb.CB_D / 2 + PLATE_MARGIN) + circle_pts(peg_at, mb.PEG_SOCKET_D / 2 + 2.4, 24)
    h_bed = min(p.dot(up) for p in cradle.footprint() + around)
    extra = cradle.bed_extra(h_bed)
    body = cradle.solid(extra)
    assert clear_of(cradle.footprint(extra), bolt)
    plate = extrude(printable_outline(cradle.footprint(extra) + around, up, h_bed), PLATE_T)
    arm = mb.cut_mount(plate + body, bolt.X, bolt.Y, (peg_at.X, peg_at.Y), up=(up.X, up.Y))
    arm = split(arm, bisect_by=Plane(origin=up * h_bed, z_dir=up), keep=Keep.TOP)
    return arm, peg_at


def print_pose(arm: Part, up: Vector) -> Part:
    """The arm as it stands on the bed: `up` -> +Z, bed at z = 0, centred in XY."""
    w = Vector(up.Y, -up.X, 0)
    part = Plane(origin=(0, 0, 0), x_dir=w, z_dir=up).to_local_coords(arm)
    bb = part.bounding_box()
    return Pos(-bb.center().X, -bb.center().Y, -bb.min.Z) * part


def overhangs(part: Part):
    """Area (mm^2) of faces that point down more than 45 deg from vertical, off the
    bed, in print pose; and how much of that is flat bridge (teardrop tops)."""
    verts, tris = part.tessellate(0.02)
    v = np.array([(p.X, p.Y, p.Z) for p in verts])[np.array(tris)]
    n = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * area, 1e-12)
    bad = (nz < -math.sqrt(0.5) - 1e-3) & (v[:, :, 2].min(axis=1) > 0.2)
    flat = bad & (nz < -0.999)
    return area[bad].sum(), area[flat].sum()


def islands(part: Part, layer: float = 0.4) -> int:
    """Number of regions in the sliced print pose that nothing below holds up."""
    count, below, z = 0, None, layer / 2
    while z < part.bounding_box().max.Z - 0.05:
        faces = section(part, Plane.XY.offset(z)).faces()
        if below is not None:
            count += sum((f & below).area < 1e-3 for f in faces)
        below, z = Sketch() + [Pos(0, 0, layer) * f for f in faces], z + layer
    return count


# --- Gun stand-ins for checks and previews --------------------------------------
def section_inset(kind: str, u: float) -> float:
    """How far the section's surface lies inside the outer line, at height u above Z_MID."""
    if kind == "barrel":
        r = T_BARREL / 2
        return r - math.sqrt(max(r * r - u * u, 0))
    r, h = HANDLE_R, T_HANDLE / 2
    k = abs(u) - (h - r)
    return 0.0 if k <= 0 else r - math.sqrt(max(r * r - k * k, 0))


def inset_outline(outline: Face, inset: float) -> Face:
    """outline shrunk by inset. OCC's offset fails at the odd distance where a thin
    spike (the nozzle's traced highlights) closes up exactly; shrinking a little
    more is still inside the gun."""
    if inset < 1e-3:
        return outline
    for extra in (0, 0.05, 0.1, 0.2):
        try:
            return offset(outline, -(inset + extra), kind=Kind.ARC)
        except RuntimeError:
            continue
    raise RuntimeError(f"cannot inset the outline by {inset:.2f} mm")


def gun_solid(outline: Face, kind: str, step: float = 1.0) -> Part:
    """The gun in 1 mm slabs: its outline inset by the section's rounding, each slab
    at its largest inset, so the stand-in never exceeds the real gun."""
    t = T_BARREL if kind == "barrel" else T_HANDLE
    slabs = []
    u = -t / 2
    while u < t / 2 - 1e-6:
        u1 = min(u + step, t / 2)
        inset = max(section_inset(kind, u), section_inset(kind, u1))
        slabs.append(Pos(0, 0, Z_MID + u) * extrude(inset_outline(outline, inset), u1 - u))
        u = u1
    return Part() + slabs


def overlap(a: Part, b: Part) -> float:
    return (a & b).volume


if __name__ == "__main__":
    # outline in mm, corrected for perspective; fit the faces the cradles touch
    px = np.array(OUTLINE_PX)
    gun_mm = perspective_correct(px)
    dense_px = resample(px)
    dense = perspective_correct(dense_px)
    normals = outward_normals(dense)
    faces = {}
    for name, ((x0, x1), (y0, y1)) in FACES_PX.items():
        m = (dense_px[:, 0] >= x0) & (dense_px[:, 0] <= x1) & (dense_px[:, 1] >= y0) & (dense_px[:, 1] <= y1)
        mu, d, worst = fit_line(dense[m])
        n = np.array([d[1], -d[0]])
        n = n if n @ normals[m].mean(axis=0) > 0 else -n
        faces[name] = (mu, d, n)
        print(f"{name:6s} face: {m.sum():3d} points, straight within {worst:.2f} mm")
    mu, d, n = faces["knob"]
    faces["knob"] = (mu + n * KNOB_EXTRA, d, n)
    u0 = intersect(faces["nose"][:2], faces["barrel"][:2])
    h1 = intersect(faces["handle"][:2], faces["knob"][:2])

    def along(name, corner, length):
        mu, d, n = faces[name]
        d = d if (mu - corner) @ d > 0 else -d
        return (v2(d), v2(n), length)

    left_c = Cradle("barrel", u0, [along("nose", u0, NOSE_L), along("barrel", u0, BARREL_L)])
    right_c = Cradle("handle", h1, [along("knob", h1, KNOB_L), along("handle", h1, HANDLE_L)])

    LEFT_BOLT, RIGHT_BOLT = place_bolts(left_c.footprint(), right_c.footprint())
    left, peg_l = build_arm(left_c, LEFT_BOLT)
    right, peg_r = build_arm(right_c, RIGHT_BOLT)

    rel = RIGHT_BOLT - LEFT_BOLT
    print(f"right bolt relative to left: {rel.X:+.1f} x {rel.Y:+.1f} mm "
          f"= {rel.X / mb.GRID_PITCH:+.0f} x {rel.Y / mb.GRID_PITCH:+.0f} grid units")
    side = {(-1, 1): "top-left", (1, 1): "top-right", (-1, -1): "bottom-left", (1, -1): "bottom-right"}
    for name, b, pg in [("left", LEFT_BOLT, peg_l), ("right", RIGHT_BOLT, peg_r)]:
        k = (round((pg.X - b.X) / (mb.GRID_PITCH / 2)), round((pg.Y - b.Y) / (mb.GRID_PITCH / 2)))
        print(f"{name} arm peg: small hole {side[k]} of its bolt")

    # checks, in the wall frame: gun and trigger clear, gun lifts straight off,
    # and cannot drop or come forward
    outline = polygon([v2(p) for p in gun_mm])
    assert outline.is_valid, "corrected outline intersects itself"
    gun_b, gun_h = gun_solid(outline, "barrel"), gun_solid(outline, "handle")
    trig_px = np.array(TRIGGER_PX)
    trig_mm = to_mm(trig_px) / magnification(T_BARREL / 2)     # thin, at mid-thickness
    trig = Pos(0, 0, Z_MID - T_BARREL / 2) * extrude(polygon([v2(p) for p in trig_mm]), T_BARREL)
    print(f"overlap gun/left {overlap(gun_b, left):.3f}  gun/right {overlap(gun_h, right):.3f}  "
          f"trigger/arms {overlap(trig, left) + overlap(trig, right):.3f}  arms {overlap(left, right):.3f} mm^3")
    worst = max(overlap(Pos(0, dy) * gun_b, left) + overlap(Pos(0, dy) * gun_h, right)
                for dy in (0.5, 1, 2, 4, 8, 15, 30))
    print(f"overlap while lifting 0.5-30 mm: {worst:.3f} mm^3")
    down = overlap(Pos(0, -3) * gun_b, left) + overlap(Pos(0, -3) * gun_h, right)
    fwd = overlap(Pos(0, 0, 3) * gun_b, left) + overlap(Pos(0, 0, 3) * gun_h, right)
    print(f"controls (must be > 0): gun 3 mm down {down:.0f} mm^3, 3 mm off the wall {fwd:.0f} mm^3")

    # print poses and exports
    bolt, peg = mb.flush_bolt(), mb.peg()
    left_p, right_p = print_pose(left, left_c.up), print_pose(right, right_c.up)
    for name, part in [("left arm", left_p), ("right arm", right_p), ("bolt", bolt), ("peg", peg)]:
        report(name, part)
    for name, part in [("left arm", left_p), ("right arm", right_p)]:
        bad, flat = overhangs(part)
        print(f"{name}: faces steeper than 45 deg off the bed {bad:.1f} mm^2, of which teardrop bridges "
              f"{flat:.1f}; unsupported islands when sliced: {islands(part)}")

    out = ROOT / "exports" / "glue_gun_arms"
    out.mkdir(parents=True, exist_ok=True)
    for name, part in [("glue_gun_arms_left", left_p), ("glue_gun_arms_right", right_p),
                       ("glue_gun_arms_bolt", bolt), ("glue_gun_arms_peg", peg)]:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
    print("wrote", out)

    # preview: everything relative to the left bolt
    shift = Pos(-LEFT_BOLT.X, -LEFT_BOLT.Y)
    left_w, right_w = shift * left, shift * right
    pegs = [shift * Pos(p.X, p.Y) * peg for p in (peg_l, peg_r)]
    bolts = [mb.installed_bolt(bolt, 0, 0), mb.installed_bolt(bolt, rel.X, rel.Y)]
    blue, orange, grey, light = (0.35, 0.55, 0.85), (0.95, 0.55, 0.2), (0.4, 0.4, 0.4), (0.8, 0.8, 0.78)
    arms = [(left_w, blue, 1), (right_w, blue, 1)] + [(p, orange, 1) for p in pegs] \
        + [(b, grey, 1) for b in bolts]
    ghost = [(shift * gun_b, light, 0.35), (shift * trig, (0.95, 0.85, 0.3), 0.5)]
    render(str(out / "glue_gun_arms.png"), [
        ("Fig. 4a  On the wall (gun ghosted, trigger yellow)", 0, 0, arms + ghost),
        ("Fig. 4b  3/4 view", 25, -35, arms + ghost),
        ("Fig. 4c  Left arm", 30, -50, [(left_w, blue, 1), (pegs[0], orange, 1)]),
        ("Fig. 4d  Right arm", 30, 50, [(right_w, blue, 1), (pegs[1], orange, 1)]),
    ], figsize=(20, 6))

    # Fig. 5: the section across each cradle (the fitted curvature), and the arms
    # standing as they print
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    from lib.preview import view

    def fill(ax, face, color):
        verts, tris = face.tessellate(0.02)
        v = np.array([(p.X, p.Y) for p in verts])
        ax.add_collection(PolyCollection(v[np.array(tris)], facecolors=color, edgecolors=color, linewidths=0.3))

    fig, axes = plt.subplots(1, 4, figsize=(20, 5.5))
    for ax, kind, title in [(axes[0], "barrel", "Fig. 5a  Across the left cradle: half-pipe"),
                            (axes[1], "handle", "Fig. 5b  Across the right cradle: rounded U")]:
        on_wall = Pos(Z_MID, 0) * Rot(0, 0, -90)   # wall on the left, gun's underside at the bottom
        fill(ax, Pos(0, -CLR - FLOOR) * Rectangle(PLATE_T, CLR + FLOOR + LIP_H + 8, align=Align.MIN), blue)
        fill(ax, on_wall * cradle_section(kind), blue)
        fill(ax, on_wall * (gun_section(kind, 0) & Pos(-LIP_H / 2 - 4, 0) * Rectangle(LIP_H + 8, 80)), light)
        ax.set_xlim(-2, Z_MID + T_BARREL / 2 + CLR + LIP_T + 3)
        ax.set_ylim(-CLR - FLOOR - 3, LIP_H + 8)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("mm out of the wall; gun grey, 1 mm clearance", fontsize=9)
    for ax, part, azim, title in [(axes[2], left_p, 150, "Fig. 5c  Left arm as printed"),
                                  (axes[3], right_p, -30, "Fig. 5d  Right arm as printed")]:
        bb = part.bounding_box()
        bed = Pos(0, 0, -0.6) * Box(bb.size.X + 20, bb.size.Y + 20, 1.2)
        upright = Rot(-90, 0, 0)                      # the renderer has Y up
        view(ax, title, 15, azim, [(upright * part, blue, 1), (upright * bed, (0.7, 0.7, 0.68), 1)])
    fig.tight_layout()
    fig.savefig(str(out / "glue_gun_arms_section.png"), dpi=90)
    plt.close(fig)
