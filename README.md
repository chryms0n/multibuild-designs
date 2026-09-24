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
pip install build123d
python models/multiboard/<part>.py
```

Each model script writes its files to `exports/`.
