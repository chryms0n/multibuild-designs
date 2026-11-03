"""Small version of the shelf-pin wall hook: the J-hook is about half the size.

Same rods (snap rod through the 36 mm panel + lower pin), same 16 mm width and back
plate as shelf_pin_hook.py; only the hook shrinks:
  * gap plate-to-tip 25 -> 12.5 mm, lip above the seat 22 -> 11 mm
  * tip 6 -> 5 mm and bottom 10 -> 7 mm thick, so it stays in proportion
The back face still runs straight down to the bottom of the hook.

Frame, print orientation and all geometry code: see shelf_pin_hook.py.
Exports: exports/shelf_pin_hook_small.{stl,step,png}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shelf_pin_hook import LARGE, export_variant  # noqa: E402
from dataclasses import replace  # noqa: E402

SMALL = replace(LARGE, hook_ri=LARGE.hook_ri / 2, lip_h=LARGE.lip_h / 2,
                tip_t=5.0, bot_t=7.0)

if __name__ == "__main__":
    export_variant("shelf_pin_hook_small", SMALL, fig=6)
