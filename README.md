# spintexture v0.1.0

**SpinTexture** is a Python package for generating k-meshes and visualizing spin textures for **2D materials**.  
It provides an **interactive CLI** for quick k-mesh generation and spin texture visualization from VASP/DFT outputs.

---

## Features (v0.1.0)

- **Interactive CLI** for 2D materials:
  - Generate **2D k-mesh** around a chosen k-point.
  - Plot **2D spin textures** from VASP PROCAR.
  - Plot **3D spin textures** for 2D materials in *(kx, ky, E)* space.
- Utility functions available: `read_poscar`, `cart_to_frac`, `frac_to_cart`.
- Generates VASP-compatible `KPOINTS` files and data files for plotting.

> ⚠️ 3D materials functionalities will be added in future versions.

---

## Installation

Clone the repository and install it:

```bash
# Clone the repository
git clone https://github.com/souchakx/spintexture.git
cd spintexture

# Create a virtual environment (recommended)
python3 -m venv ~/.venvs/spintexture
source ~/.venvs/spintexture/bin/activate

# Install the package
pip install .
```


Dependencies (`numpy`, `matplotlib`, `scipy`) are automatically installed.

> Tested with **Python 3.10**.

---

## Usage

Run the **interactive CLI**:

```bash
spintexture
```

You will see the main menu:

```
   ==========================================
    SPINTEXTURE PACKAGE - CLI INTERFACE
    Tools for K-mesh generation & Spin plots
   ==========================================
1. 2D Materials
0. Exit
```

### 2D Materials Menu

```
--- 2D Materials ---
1. Generate 2D k-mesh
2. Plot 2D spin texture
3. Plot 3D spin texture (kx, ky, E)
0. Back
```

* **Generate 2D k-mesh** → Creates a shifted square k-grid around a user-defined point.

  * Output: `KPOINTS_rec.dat` (reciprocal coordinates, VASP format)
    `KPOINTS_cart.dat` (Cartesian coordinates, for checking/plotting)
* **Plot 2D spin texture** → Quiver plot of in-plane spin components.

  * Data files saved: `band##_data_cartesian.dat`, `band##_data_fractional.dat`
* **Plot 3D spin texture (kx, ky, E)** → 3D visualization of the spin texture for 2D materials.

---

## Example Workflow

1. **Generate 2D k-mesh**:

```bash
spintexture
# Select "2D Materials" → "Generate 2D k-mesh"
# Enter grid density, center, and half-width
# Generates KPOINTS files for VASP
```

2. **Plot 2D spin texture**:

```bash
spintexture
# Select "2D Materials" → "Plot 2D spin texture"
# Enter band number → Quiver plot appears
```

3. **Plot 3D spin texture**:

```bash
spintexture
# Select "2D Materials" → "Plot 3D spin texture (kx, ky, E)"
# Enter band number → 3D spin surface appears
```

---

## Package Structure

```
spintexture/
│── __init__.py
│── cli.py                 # Interactive menu
│── utils.py               # read_poscar, cart_to_frac, frac_to_cart
│── kmesh2d.py             # 2D k-mesh generator
│── spin2d.py              # 2D spin texture plotting
│── spin3d.py              # 3D spin surface plotting for 2D materials
```

---

## Development

* **Python**: ≥3.8
* **Dependencies**: `numpy`, `matplotlib`, `scipy`


* Contributions are welcome via fork & pull request.

---

## Citation

If you use this code in your work, please cite:

*spintexture v0.1.0, Souvick Chakraborty (2025).*

---
