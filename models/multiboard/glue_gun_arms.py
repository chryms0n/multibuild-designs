"""Two arms that hold a hot-glue gun on the MultiBoard, one each side of the trigger.

The gun hangs with its side against the wall, in the attitude of the user's side
photo: nozzle down-left, handle down-right, trigger hanging free between the arms.
Each arm is a flat stem, bolted at its top into a large hole, with a cradle in front
that wraps the gun's underside across its thickness:
  - left arm: under the barrel, hooked around the barrel's lower front corner
  - right arm: under the front of the handle, hooked into the corner at the knob
    on the handle's end
With both corners caught the gun cannot slide or roll off; it lifts straight up.
The outer edge of each cradle rises at 45 deg into a lip, so the gun cannot fall
forward and the arm prints without supports.

The two bolt holes sit on the same 25 mm grid (see LEFT_BOLT / RIGHT_BOLT); mount
the arms in exactly those holes relative to each other.

Frame: X along the wall, Y up, Z out of the wall; back of the stems on Z = 0.
Print the arms back face down, as modelled. Each arm needs one flush bolt and one
peg (the same parts as the caliper holder).

Exports: exports/glue_gun_arms_{left,right,bolt,peg}.{stl,step}, glue_gun_arms.png
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build123d import *  # noqa: E402

from lib import multiboard as mb  # noqa: E402
from lib.preview import render, report  # noqa: E402

# --- Glue gun, approximated from the user's photos -----------------------------
# Side photo: gun lying on its side next to the caliper; its cm scale gives
# 3.48 px/mm. Outline points are image pixels (y down) in that photo.
PX_PER_MM = 3.48
OUTLINE_PX = [
    (236, 604), (250, 622), (300, 600), (345, 569),   # nozzle and nose
    (445, 569),                                       # U0: lower front corner of the barrel
    (578, 402),                                       # U1: barrel underside meets the trigger
    (610, 392), (700, 438),                           # crotch above the trigger
    (780, 477),                                       # H0: trigger's back meets the handle
    (912, 553),                                       # H1: handle front meets the end knob
    (918, 592), (995, 592), (1000, 440),              # knob on the handle's end
    (985, 420), (725, 268), (728, 165),               # handle top, back of the grip
    (700, 120), (650, 100), (605, 105),               # rear of the barrel
    (285, 490), (262, 545),                           # barrel top
]
TRIGGER_PX = [(582, 402), (600, 392), (640, 395), (740, 440), (780, 477),   # root, back edge
              (647, 556), (644, 470), (628, 428), (600, 410)]              # tip, front edge
U0, U1, H0, H1 = 4, 5, 8, 9                           # indices into OUTLINE_PX
# Front photo (gun standing on its end, handle on the floor, 15.8 px/mm): the handle
# is ~32 mm wide with ~6 mm edge rounds; the user says the barrel section is
# constant; its end was nearer the camera, so its width is a guess.
T_BARREL = 34.0
T_HANDLE = 32.0
EDGE_R = 6.0

# --- Design choices -----------------------------------------------------------
CLR = 1.0                    # clearance around the gun, in the wall plane and per side in Z
FLOOR = 4.0                  # cradle wall under the gun (10 lines of 0.4 mm)
LIP_H = 8.0                  # how far the 45 deg lip reaches up the gun's outer face
# 45 deg chamfer that contains a round of EDGE_R: the lip starts this far below the face
LIP_C = EDGE_R * (2 - math.sqrt(2))
FOOT_L = 11.5                # left cradle: length under the flat bottom of the nose
SLOPE_L = 42.0               # left cradle: length along the barrel underside from U0
START_GAP = 8.0              # right cradle starts this far past the trigger
KNOB_L = 9.0                 # right cradle: length down the knob face from H1
WIN = 12.0                   # half-width of the band window across the outline
PLATE_T = mb.MOUNT_PLATE_T
PLATE_MARGIN = 4.6           # plate material around the counterbore
PLATE_ROUND = 4.0
BOLT_ABOVE = 3.0             # gap between a cradle's footprint and its counterbore
STEP = 0.4                   # lip step height = layer height


def to_mm(p):
    return Vector(p[0] / PX_PER_MM, -p[1] / PX_PER_MM)


def unit(v: Vector) -> Vector:
    return v / v.length


def polygon(points) -> Face:
    return Polygon(*[(p.X, p.Y) for p in points], align=None)


GUN = [to_mm(p) for p in OUTLINE_PX]
TRIGGER = [to_mm(p) for p in TRIGGER_PX]
Z_MID = PLATE_T + CLR + T_BARREL / 2          # gun's mid-plane; the barrel side touches the stems


def left_window() -> Face:
    """Region around the outline that the left cradle covers: nose bottom + barrel underside."""
    u0, u1 = GUN[U0], GUN[U1]
    d = unit(u1 - u0)
    n_out = Vector(d.Y, -d.X)                 # outward (away from the gun) for the underside
    f0 = u0 - Vector(FOOT_L, 0)
    e = u0 + d * SLOPE_L
    corner_out = u0 + unit(n_out + Vector(0, -1)) * WIN * 1.4
    corner_in = u0 - unit(n_out + Vector(0, -1)) * WIN * 1.4
    return polygon([f0 + Vector(0, WIN), f0 - Vector(0, WIN), corner_out,
                    e + n_out * WIN, e - n_out * WIN, corner_in])


def right_window() -> Face:
    """Region the right cradle covers: handle front + into the corner at the knob."""
    h0, h1 = GUN[H0], GUN[H1]
    d = unit(h1 - h0)
    n_out = Vector(d.Y, -d.X)
    s0 = h0 + d * START_GAP
    k_dir = unit(GUN[H1 + 1] - h1)            # down the knob face
    k1 = h1 + k_dir * KNOB_L
    k_out = Vector(k_dir.Y, -k_dir.X)
    corner = unit(n_out + k_out)
    return polygon([s0 - n_out * WIN, h1 - corner * WIN * 1.4, k1 - k_out * WIN,
                    k1 + k_out * WIN, h1 + corner * WIN * 1.4, s0 + n_out * WIN])


def band(window: Face) -> Face:
    """Cradle footprint: FLOOR outside the (clearance) outline, LIP_H inside it."""
    gun = polygon(GUN)
    outer = offset(gun, CLR + FLOOR, kind=Kind.ARC)
    inner = offset(gun, CLR - LIP_H, kind=Kind.ARC)
    return (outer - inner) & window


def gun_cut(window: Face, t: float) -> Part:
    """Space the cradle must leave free: the gun (+ clearance) up to where its outer
    edge round starts, then a 45 deg taper that contains the round and forms the lip."""
    z0 = Z_MID - t / 2 - CLR
    z_top = Z_MID + t / 2 + CLR
    local = offset(polygon(GUN), CLR, kind=Kind.ARC) & offset(window, LIP_H + 4, kind=Kind.ARC)
    local = local.faces()[0]
    body = Pos(0, 0, z0) * extrude(local, z_top - LIP_C - z0)
    # 45 deg in 0.4 mm steps (one layer each): a true tapered extrusion of this
    # outline comes out invalid in OCC, and the printer steps it anyway
    roof = None
    for i in range(int((LIP_H + 1) / STEP)):
        f = local if i == 0 else offset(local, -i * STEP, kind=Kind.ARC).faces()[0]
        slab = Pos(0, 0, z_top - LIP_C + i * STEP) * extrude(f, STEP + 0.01)
        roof = slab if roof is None else roof + slab
    return body + roof, z_top - LIP_C + LIP_H


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


def sample(face: Face, step: float = 1.0):
    pts = []
    for e in face.edges():
        n = max(2, int(e.length / step))
        pts += [e.position_at(i / n) for i in range(n + 1)]
    return pts


def circle_pts(c: Vector, r: float, n: int = 48):
    return [c + Vector(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def bolt_target(footprint: Face) -> Vector:
    """Directly above the cradle, with the counterbore clear of the cradle footprint."""
    bb = footprint.bounding_box()
    c = footprint.center()
    x = c.X
    y = bb.max.Y + mb.CB_D / 2 + BOLT_ABOVE
    return Vector(x, y)


def clear_of(footprint: Face, c: Vector) -> bool:
    disc = Pos(c.X, c.Y) * Circle(mb.CB_D / 2 + BOLT_ABOVE)
    return (disc & footprint).area < 1e-6


def plate_outline(footprint: Face, bolt: Vector, peg: Vector) -> Face:
    pts = sample(footprint) + circle_pts(bolt, mb.CB_D / 2 + PLATE_MARGIN) \
        + circle_pts(peg, mb.PEG_SOCKET_D / 2 + 2.4, 24)
    hull = polygon(hull2d(pts))
    return offset(offset(hull, -PLATE_ROUND, kind=Kind.ARC), PLATE_ROUND, kind=Kind.ARC).faces()[0]


def pick_peg(footprint: Face, bolt: Vector) -> Vector:
    """Small hole (diagonal neighbour of the large hole) that keeps the plate smallest."""
    base = sample(footprint) + circle_pts(bolt, mb.CB_D / 2 + PLATE_MARGIN)
    best = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = bolt + Vector(sx * mb.GRID_PITCH / 2, sy * mb.GRID_PITCH / 2)
            area = polygon(hull2d(base + circle_pts(p, mb.PEG_SOCKET_D / 2 + 2.4, 24))).area
            if best is None or area < best[0]:
                best = (area, p)
    return best[1]


def build_arm(window: Face, t: float, bolt: Vector):
    foot = band(window).faces()[0]
    cut, z_end = gun_cut(window, t)
    cradle = Pos(0, 0, PLATE_T - 0.01) * extrude(foot, z_end - PLATE_T + 0.01) - cut
    peg_at = pick_peg(foot, bolt)
    plate = extrude(plate_outline(foot, bolt, peg_at), PLATE_T)
    arm = mb.cut_mount(plate + cradle, bolt.X, bolt.Y, (peg_at.X, peg_at.Y))
    return arm, peg_at


def place_bolts(foot_l: Face, foot_r: Face):
    """Left bolt above the left cradle; right bolt on the same grid, nearest above the right cradle."""
    left = bolt_target(foot_l)
    target = bolt_target(foot_r)
    best = None
    for i in range(-10, 11):
        for j in range(-10, 11):
            c = left + Vector(i, j) * mb.GRID_PITCH
            if not clear_of(foot_r, c) or c.Y < target.Y - 1e-6:
                continue
            d = (c - target).length
            if best is None or d < best[0]:
                best = (d, c)
    return left, best[1]


def gun_solid(outline, t: float, edge: float = LIP_C) -> Part:
    """Stand-in for the real gun: its outline at thickness t, the outer edge chamfered
    by LIP_C (which contains a round of EDGE_R), for checks and preview."""
    f = polygon(outline)
    z0 = Z_MID - t / 2
    body = Pos(0, 0, z0) * extrude(f, t - edge)
    try:
        return body + Pos(0, 0, z0 + t - edge) * extrude(f, edge, taper=45)
    except Exception:
        return body


def overlap(a: Part, b: Part) -> float:
    return (a & b).volume


if __name__ == "__main__":
    win_l, win_r = left_window(), right_window()
    foot_l, foot_r = band(win_l).faces()[0], band(win_r).faces()[0]
    LEFT_BOLT, RIGHT_BOLT = place_bolts(foot_l, foot_r)
    left, peg_l = build_arm(win_l, T_BARREL, LEFT_BOLT)
    right, peg_r = build_arm(win_r, T_HANDLE, RIGHT_BOLT)

    # everything relative to the left bolt
    shift = Pos(-LEFT_BOLT.X, -LEFT_BOLT.Y)
    left, right = shift * left, shift * right
    rel = RIGHT_BOLT - LEFT_BOLT
    print(f"right bolt relative to left: {rel.X:+.1f} x {rel.Y:+.1f} mm "
          f"= {rel.X / mb.GRID_PITCH:+.0f} x {rel.Y / mb.GRID_PITCH:+.0f} grid units")
    side = {(-1, 1): "top-left", (1, 1): "top-right", (-1, -1): "bottom-left", (1, -1): "bottom-right"}
    for name, b, pg in [("left", LEFT_BOLT, peg_l), ("right", RIGHT_BOLT, peg_r)]:
        k = (round((pg.X - b.X) / (mb.GRID_PITCH / 2)), round((pg.Y - b.Y) / (mb.GRID_PITCH / 2)))
        print(f"{name} arm peg: small hole {side[k]} of its bolt")

    # checks: gun and trigger stand clear; the gun lifts straight off
    gun_b = shift * gun_solid(GUN, T_BARREL)
    gun_h = shift * gun_solid(GUN, T_HANDLE)
    trig = shift * Pos(0, 0, Z_MID - T_BARREL / 2) * extrude(polygon(TRIGGER), T_BARREL)
    print(f"overlap gun/left {overlap(gun_b, left):.3f}  gun/right {overlap(gun_h, right):.3f}  "
          f"trigger/arms {overlap(trig, left) + overlap(trig, right):.3f}  arms {overlap(left, right):.3f}")
    worst = max(overlap(Pos(0, dy) * gun_b, left) + overlap(Pos(0, dy) * gun_h, right)
                for dy in (0.5, 1, 2, 4, 8, 15, 30))
    print(f"overlap while lifting 0.5-30 mm: {worst:.3f}")
    ctrl = overlap(Pos(0, -3) * gun_b, left) + overlap(Pos(0, -3) * gun_h, right)
    print(f"control, gun pushed 3 mm down: overlap {ctrl:.0f} mm^3 (must be > 0)")

    bolt, peg = mb.flush_bolt(), mb.peg()
    for name, part in [("left arm", left), ("right arm", right), ("bolt", bolt), ("peg", peg)]:
        report(name, part)

    out = ROOT / "exports"
    for name, part in [("glue_gun_arms_left", left), ("glue_gun_arms_right", right),
                       ("glue_gun_arms_bolt", bolt), ("glue_gun_arms_peg", peg)]:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
    print("wrote", out)

    # preview: arms, bolts, pegs and the gun ghosted in place
    peg_l, peg_r = shift * Pos(peg_l.X, peg_l.Y) * peg, shift * Pos(peg_r.X, peg_r.Y) * peg
    bolts = [mb.installed_bolt(bolt, 0, 0), mb.installed_bolt(bolt, rel.X, rel.Y)]
    blue, orange, grey, light = (0.35, 0.55, 0.85), (0.95, 0.55, 0.2), (0.4, 0.4, 0.4), (0.8, 0.8, 0.78)
    arms = [(left, blue, 1), (right, blue, 1), (peg_l, orange, 1), (peg_r, orange, 1)] \
        + [(b, grey, 1) for b in bolts]
    ghost = [(gun_b, light, 0.35), (trig, (0.95, 0.85, 0.3), 0.5)]
    render(str(out / "glue_gun_arms.png"), [
        ("Fig. 4a  On the wall (gun ghosted, trigger yellow)", 0, 0, arms + ghost),
        ("Fig. 4b  3/4 view", 25, -35, arms + ghost),
        ("Fig. 4c  Left arm", 35, -40, [(left, blue, 1), (peg_l, orange, 1)]),
        ("Fig. 4d  Right arm", 35, 40, [(right, blue, 1), (peg_r, orange, 1)]),
    ], figsize=(20, 6))
