# multibuild-designs

Custom 3D-printable parts for the [MultiBuild](https://multibuild.io/) organization system:
tool holders that mount on the **MultiBoard** grid, and bins for **MultiBin**.

Models are written as Python code with [build123d](https://github.com/gumyr/build123d)
and exported as STL/STEP for slicing.

Printed on a Bambu Lab A1 in PLA.

## Layout

| Path | Contents |
| --- | --- |
| `lib/` | Shared geometry: MultiBoard mounting interface, MultiBin dimensions |
| `models/multiboard/` | One source file per board-mounted part |
| `models/multibin/` | One source file per bin |
| `models/furniture/` | Parts that mount on furniture directly (e.g. 5 mm shelf-pin holes) |
| `exports/` | Generated STL/STEP files, ready for the slicer |

## Usage

```bash
pip install -r requirements.txt
python models/multiboard/<part>.py
```

Each model script writes its STL/STEP files and a preview image (`<part>.png`) to `exports/`.

## Parts

| Part | Script | Print files |
| --- | --- | --- |
| Caliper holder (150 mm vernier caliper, one MultiBoard large hole + anti-rotation peg) | `models/multiboard/caliper_holder.py` | `exports/caliper_holder.stl`, `exports/caliper_holder_peg.stl` |
| Shelf-pin wall hook (two 5 mm holes through a 36 mm panel, snap rod + pin, 16 mm wide J-hook with 25 mm gap for a ~10 kg backpack) | `models/furniture/shelf_pin_hook.py` | `exports/shelf_pin_hook.stl` (already in print orientation; support under the rods) |
| Shelf-pin wall hook, small (same rods and plate, J-hook about half size: 12.5 mm gap, 11 mm lip) | `models/furniture/shelf_pin_hook_small.py` | `exports/shelf_pin_hook_small.stl` (already in print orientation; support under the rods) |
| Shelf-pin wall hook, small raised (small hook moved 11.5 mm up, plate continues below it) | `models/furniture/shelf_pin_hook_small_raised.py` | `exports/shelf_pin_hook_small_raised.stl` (already in print orientation; support under the rods) |
