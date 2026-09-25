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
| Caliper holder (150 mm vernier caliper, hangs below one MultiBoard large hole; flush coin-slot bolt + anti-rotation peg) | `models/multiboard/caliper_holder.py` | `exports/caliper_holder.stl`, `exports/caliper_holder_bolt.stl`, `exports/caliper_holder_peg.stl` |
| Glue gun arms (two separate arms left/right of the trigger, each a U channel shaped to the gun's cross-section; bolts 5 grid units apart in one row; flush coin-slot bolt + peg each; arms print standing on edge, exported in that pose) | `models/multiboard/glue_gun_arms.py` | `exports/glue_gun_arms_left.stl`, `exports/glue_gun_arms_right.stl`, 2 × `exports/glue_gun_arms_bolt.stl`, 2 × `exports/glue_gun_arms_peg.stl` |
