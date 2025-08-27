#!/usr/bin/env python3
"""
spin3d.py

Plots a band as a 3D surface (kx, ky, energy) with spin vectors (Sx, Sy, Sz)
as 3D arrows just above the energy surface.

Arrow length is fixed; offset above surface depends on energy range.
All arrow parameters are customizable.

Usage (CLI):
------------
    $ spintexture   # choose 2D material -> 3D -> spin3d

Configuration (edit at the top):
--------------------------------
# Arrow options
ARROW_SCALE        = 0.01       # scale factor for arrow vectors
ARROW_COLOR        = "red"
ARROW_LINEWIDTH    = 1.0
ARROW_ALPHA        = 1.0
ARROW_LENGTH_RATIO = 0.3
ARROW_PIVOT        = "tail"

# Colormap options
COLORMAP_NAME      = "viridis"

# Grid options
GRID_POINTS        = 100       # interpolation resolution

Dependencies:
-------------
- numpy
- matplotlib
- scipy
- VASP POSCAR and PROCAR files must exist in the working directory
"""

import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, LinearNDInterpolator
from mpl_toolkits.mplot3d import Axes3D

from spintexture.utils import read_poscar, frac_to_cart

# ------------------- User-configurable parameters ---------------------- #
ARROW_SCALE        = 0.01
ARROW_COLOR        = "red"
ARROW_LINEWIDTH    = 1.0
ARROW_ALPHA        = 1.0
ARROW_LENGTH_RATIO = 0.3
ARROW_PIVOT        = "tail"

COLORMAP_NAME      = "viridis"
GRID_POINTS        = 100

POSCAR = "POSCAR"
PROCAR = "PROCAR"

# --------------------- PROCAR parser ----------------------------------- #
def parse_procar_soc(filename=PROCAR, band_no=18):
    """
    Parse non-collinear PROCAR file for a specific band.

    Returns:
        kpts_frac : np.ndarray
            Fractional k-points (N x 3)
        spins : np.ndarray
            Spin components (N x 3)
        stots : np.ndarray
            Spin magnitude (N)
        energies : np.ndarray
            Band energies (N)
    """
    kpts_frac, spins, stots, energies = [], [], [], []
    with open(filename, "r") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("k-point"):
            nums = re.findall(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?', lines[i])
            if len(nums) >= 3:
                kpt_frac = [float(nums[0]), float(nums[1]), float(nums[2])]
            else:
                i += 1; continue
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith("band"):
                    parts = lines[i].split()
                    try:
                        band = int(parts[1])
                        energy = float(parts[4])
                    except Exception:
                        band, energy = None, None
                    i += 1
                    if band == band_no:
                        tot_lines = []
                        while i < len(lines) and len(tot_lines) < 4:
                            if lines[i].strip().startswith("tot"):
                                tot_lines.append(lines[i].strip())
                            i += 1
                        if len(tot_lines) == 4:
                            stot = float(tot_lines[0].split()[-1])
                            sx   = float(tot_lines[1].split()[-1])
                            sy   = float(tot_lines[2].split()[-1])
                            sz   = float(tot_lines[3].split()[-1])
                            kpts_frac.append(kpt_frac)
                            spins.append([sx, sy, sz])
                            stots.append(stot)
                            energies.append(energy)
                        break
                else:
                    i += 1
        else:
            i += 1
    return np.array(kpts_frac), np.array(spins), np.array(stots), np.array(energies)

# --------------------- 3D plot and save -------------------------------- #
def plot_and_save_3d(poscar=POSCAR, procar=PROCAR, band_no=18):
    """
    Plot 3D spin texture for a specific band and save data and figure.
    """
    B = read_poscar(poscar)
    k_frac, spins, stots, energies = parse_procar_soc(procar, band_no)
    k_cart = frac_to_cart(k_frac, B)
    x_c, y_c = k_cart[:,0], k_cart[:,1]

    # Save data
    fname_cart = f"band{band_no}_data_cartesian.dat"
    with open(fname_cart, "w") as f:
        f.write("# E(eV) kx ky kz Sx Sy Sz Stot\n")
        for e, (kx, ky, kz), (sxi, syi, szi), st in zip(energies, k_cart, spins, stots):
            f.write(f"{e:12.6f} {kx:12.6f} {ky:12.6f} {kz:12.6f} "
                    f"{sxi:12.6f} {syi:12.6f} {szi:12.6f} {st:12.6f}\n")
    print(f"Saved data for band {band_no}")

    # Interpolate surface
    grid_x = np.linspace(min(x_c), max(x_c), GRID_POINTS)
    grid_y = np.linspace(min(y_c), max(y_c), GRID_POINTS)
    grid_X, grid_Y = np.meshgrid(grid_x, grid_y)
    grid_Z = griddata((x_c, y_c), energies, (grid_X, grid_Y), method="cubic")

    # 3D plot
    fig = plt.figure(figsize=(9,7))
    ax = fig.add_subplot(111, projection="3d")

    # Surface
    norm_vals = (grid_Z - np.nanmin(grid_Z)) / (np.nanmax(grid_Z) - np.nanmin(grid_Z))
    surf = ax.plot_surface(grid_X, grid_Y, grid_Z,
                           facecolors=plt.cm.get_cmap(COLORMAP_NAME)(norm_vals),
                           linewidth=0, antialiased=False, alpha=0.85)
    mappable = plt.cm.ScalarMappable(cmap=COLORMAP_NAME)
    mappable.set_array(grid_Z)
    cbar = fig.colorbar(mappable, ax=ax, pad=0.1)
    cbar.set_label("Energy (eV)")

    # Arrow base above surface
    interp_energy = LinearNDInterpolator(list(zip(x_c, y_c)), energies)
    z_base = interp_energy(x_c, y_c)
    energy_range = np.nanmax(energies) - np.nanmin(energies)
    z_offset = 0.02 * energy_range
    z_start = z_base + z_offset

    # Scale spin vectors
    max_spin = np.max(np.linalg.norm(spins, axis=1))
    max_spin = 1.0 if max_spin==0 else max_spin
    vecs = spins * (ARROW_SCALE / max_spin)
    sx_scaled, sy_scaled, sz_scaled = vecs[:,0], vecs[:,1], vecs[:,2]

    # Plot arrows
    ax.quiver(x_c, y_c, z_start,
              sx_scaled, sy_scaled, sz_scaled,
              color=ARROW_COLOR,
              linewidth=ARROW_LINEWIDTH,
              alpha=ARROW_ALPHA,
              length=1.0,
              normalize=False,
              arrow_length_ratio=ARROW_LENGTH_RATIO,
              pivot=ARROW_PIVOT,
              antialiased=True)

    # Labels
    ax.set_xlabel(r"$k_x$ (Å$^{-1}$)")
    ax.set_ylabel(r"$k_y$ (Å$^{-1}$)")
    ax.set_zlabel("Energy (eV)")
    ax.set_title(f"3D Spin Texture for Band {band_no}")

    plt.tight_layout()
    outname = f"band{band_no}_spintexture_3d.png"
    plt.savefig(outname, dpi=600)
    plt.show()
    print(f"Saved 3D spin texture plot to {outname}")

# --------------------- CLI runner ------------------------------------- #
def run():
    band = int(input("Enter band number: "))
    plot_and_save_3d(POSCAR, PROCAR, band)

if __name__ == "__main__":
    run()
