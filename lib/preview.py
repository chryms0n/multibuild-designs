"""Quick shaded preview renders of build123d shapes (matplotlib, no GUI needed)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection


def _triangles(shape, tol=0.05):
    verts, tris = shape.tessellate(tol)
    v = np.array([(p.X, p.Y, p.Z) for p in verts])
    return v[np.array(tris)]


def _rotation(elev, azim):
    a, e = np.radians(azim), np.radians(elev)
    ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return rx @ ry


def _draw(ax, items, rot, title):
    light = np.array([0.3, 0.6, 1.0])
    light /= np.linalg.norm(light)
    polys, cols, depth = [], [], []
    for tri, color, alpha in items:
        w = tri @ rot.T
        n = np.cross(w[:, 1] - w[:, 0], w[:, 2] - w[:, 0])
        nn = np.linalg.norm(n, axis=1)
        keep = nn > 1e-9
        w, n = w[keep], n[keep] / nn[keep, None]
        if alpha == 1:  # back-face cull opaque parts
            w, n = w[n[:, 2] > 0], n[n[:, 2] > 0]
        shade = 0.35 + 0.65 * np.abs(n @ light)
        polys += list(w[:, :, :2])
        depth += list(w[:, :, 2].mean(axis=1))
        cols += [(color[0] * s, color[1] * s, color[2] * s, alpha) for s in shade]
    order = np.argsort(depth)
    ax.add_collection(PolyCollection([polys[i] for i in order],
                                     facecolors=[cols[i] for i in order], edgecolors="none"))
    pts = np.concatenate(polys)
    ax.set_xlim(pts[:, 0].min() - 3, pts[:, 0].max() + 3)
    ax.set_ylim(pts[:, 1].min() - 3, pts[:, 1].max() + 3)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=10)
    ax.axis("off")


def render(path, views, figsize=(16, 7), suptitle=None):
    """Render views side by side.

    views: list of (title, elev, azim, [(shape, rgb, alpha), ...]).
    The model frame is X right, Y up, Z towards the viewer at elev = azim = 0.
    """
    fig, axes = plt.subplots(1, len(views), figsize=figsize)
    for ax, (title, elev, azim, items) in zip(np.atleast_1d(axes), views):
        tris = [(_triangles(s), c, a) for s, c, a in items]
        _draw(ax, tris, _rotation(elev, azim), title)
    if suptitle:
        fig.suptitle(suptitle)
    fig.tight_layout()
    fig.savefig(path, dpi=90)
    plt.close(fig)


def report(name, part):
    """Hand-over check: single valid solid, bounding box, volume."""
    bb = part.bounding_box()
    print(f"{name}: solids={len(part.solids())} valid={part.is_valid} "
          f"bbox={bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm "
          f"volume={part.volume / 1000:.2f} cm^3 (~{part.volume * 1.24e-3:.1f} g PLA solid)")
