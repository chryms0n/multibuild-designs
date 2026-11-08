"""Small shelf-pin hook, raised: the small hook moved up the back plate.

Same hook as shelf_pin_hook_small.py (12.5 mm gap, 11 mm lip), moved 11.5 mm up,
like the large hook. The back plate still reaches down to where the small hook's
bottom used to be (9.75 mm below the lower rod), so the panel pushes back just as
low as before and the pull on the snap rod is unchanged.

Frame, print orientation and all geometry code: see shelf_pin_hook.py.
Exports: exports/shelf_pin_hook_small_raised.{stl,step,png}
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shelf_pin_hook import export_variant  # noqa: E402
from shelf_pin_hook_small import SMALL  # noqa: E402

RAISE = 11.5   # same raise as the large hook

SMALL_RAISED = replace(SMALL, hook_y=SMALL.hook_y + RAISE, plate_bottom=SMALL.bottom_y)

if __name__ == "__main__":
    export_variant("shelf_pin_hook_small_raised", SMALL_RAISED, fig=10)
