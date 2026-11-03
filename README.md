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
| Shelf-pin wall hook (two 5 mm holes through a 36 mm panel, snap rod + pin, 20 mm J-hook) | `models/furniture/shelf_pin_hook.py` | `exports/shelf_pin_hook.stl` (already in print orientation) |
