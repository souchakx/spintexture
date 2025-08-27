# spintexture/kmesh.py

"""
kmesh.py

This module generates a shifted square k-point mesh around a user-specified
centre point. The grid can be defined in either reciprocal fractional coordinates
(R-units) or Cartesian coordinates (Å^-1). It outputs VASP-compatible KPOINTS
files and provides an optional visualization in the kx–ky plane.

Usage (CLI):
------------
    $ spintexture   # then choose option for k-mesh generation

Functions
---------
generate_square_cartesian(nx, ny, kmax, centre_cart) -> np.ndarray
    Generate a square k-point grid in Cartesian space.

write_kpoints(kpts, filename, coord_tag="Reciprocal")
    Write k-points to a VASP-compatible KPOINTS file.

plot_kpoints(k_cart)
    Plot k-points in the kx–ky plane.

run()
    Interactive runner function (used by CLI menu).

Notes
-----
- Requires a valid "POSCAR" file in the current directory.
- The reciprocal lattice vectors are read from POSCAR.
- Only 2D grids are supported (nz must be 1).
- Both fractional (reciprocal) and Cartesian k-points are saved.
"""

import numpy as np
import matplotlib.pyplot as plt
from .utils import read_poscar, frac_to_cart, cart_to_frac


def generate_square_cartesian(nx, ny, kmax, centre_cart):
    """
    Generate a square k-point grid in Cartesian coordinates.

    Parameters
    ----------
    nx, ny : int
        Number of k-points along x and y directions.
    kmax : float
        Half-width of the grid in Å^-1.
    centre_cart : array_like
        Cartesian coordinates (kx, ky, kz) of the grid centre.

    Returns
    -------
    np.ndarray
        Array of shape (nx*ny, 3) containing k-points in Cartesian coords.
    """
    kx_vals = np.linspace(-kmax, kmax, nx) + centre_cart[0]
    ky_vals = np.linspace(-kmax, kmax, ny) + centre_cart[1]
    kz_val  = centre_cart[2]
    return np.array([[kx, ky, kz_val] for kx in kx_vals for ky in ky_vals])


def write_kpoints(kpts, filename, coord_tag="Reciprocal"):
    """
    Write k-points to a VASP-compatible KPOINTS file.

    Parameters
    ----------
    kpts : np.ndarray
        K-points array of shape (N, 3).
    filename : str
        Output file name.
    coord_tag : str
        "Reciprocal" or "Cartesian".
    """
    n = len(kpts)
    with open(filename, "w") as f:
        f.write("Generated square grid\n")
        f.write(f"{n}\n")
        f.write(f"{coord_tag}\n")
        for kx, ky, kz in kpts:
            f.write(f"{kx:.7f}\t{ky:.7f}\t{kz:.7f}\t1.0000000\n")

    print(f"✅ Wrote {n} k-points to {filename} ({coord_tag})")


def plot_kpoints(k_cart):
    """
    Plot k-points in the kx–ky plane.

    Parameters
    ----------
    k_cart : np.ndarray
        K-points in Cartesian coordinates (N x 3).
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(k_cart[:, 0], k_cart[:, 1], s=10, c="blue",
               alpha=0.7, edgecolors="k", linewidths=0.3)
    ax.set_xlabel(r"$k_x$ (Å$^{-1}$)")
    ax.set_ylabel(r"$k_y$ (Å$^{-1}$)")
    ax.set_aspect("equal")
    ax.set_title("Generated k-points (Cartesian)")
    plt.tight_layout()
    plt.show()


def run():
    """
    Interactive runner for generating and plotting a k-point grid.
    Only supports 2D grids (nz must be 1).
    """
    # Defaults
    default_nx, default_ny, default_nz = 21, 21, 1
    default_kmax = 0.2
    default_mode = "R"
    default_centre_frac = [0.0, 0.0, 0.0]
    default_centre_cart = None

    # Read reciprocal lattice
    B = read_poscar("POSCAR")

    # Grid density
    density_str = input(
        f"Enter grid density nx ny nz [default: {default_nx} {default_ny} {default_nz}]: "
    ).strip()
    nx, ny, nz = map(int, density_str.split()) if density_str else (default_nx, default_ny, default_nz)

    # --- 2D grid check ---
    if nz != 1:
        raise ValueError("Only 2D k-mesh generation is supported in this module. Set nz = 1.")

    # Half-width
    kmax_str = input(f"Enter half-width in Å^-1 [default: {default_kmax}]: ").strip()
    kmax = float(kmax_str) if kmax_str else default_kmax

    # Centre mode
    mode_str = input(f"Centre in Reciprocal (R) or Cartesian (C) [default: {default_mode}]: ").strip().upper()
    mode = mode_str if mode_str else default_mode

    if mode == "R":
        centre_str = input(
            f"Enter centre in fractional R-units [default: {default_centre_frac[0]} {default_centre_frac[1]} {default_centre_frac[2]}]: "
        ).strip()
        centre_frac = np.array(list(map(float, centre_str.split()))) if centre_str else np.array(default_centre_frac)
        centre_cart = frac_to_cart(centre_frac, B)
    elif mode == "C":
        if default_centre_cart is None:
            default_centre_cart = frac_to_cart(np.array(default_centre_frac), B)
        centre_str = input(
            f"Enter centre in Cartesian Å^-1 [default: {default_centre_cart[0]:.6f} {default_centre_cart[1]:.6f} {default_centre_cart[2]:.6f}]: "
        ).strip()
        centre_cart = np.array(list(map(float, centre_str.split()))) if centre_str else np.array(default_centre_cart)
        centre_frac = cart_to_frac(centre_cart, B)
    else:
        raise ValueError("Invalid mode. Enter 'R' or 'C'.")

    # Generate grid
    k_cart = generate_square_cartesian(nx, ny, kmax, centre_cart)
    k_frac = cart_to_frac(k_cart, B)

    # Save outputs
    write_kpoints(k_frac, "KPOINTS_rec.dat", "Reciprocal")
    write_kpoints(k_cart, "KPOINTS_cart.dat", "Cartesian")

    print("\n✅ Finished generating k-point grid.")
    print("   -> KPOINTS_rec.dat (Reciprocal coords, VASP format)")
    print("   -> KPOINTS_cart.dat (Cartesian coords, check/plot)\n")

    # Optional plot
    plot_choice = input("Plot k-points in Cartesian coordinates? (y/n) [default: y]: ").strip().lower()
    if plot_choice in ("", "y", "yes"):
        plot_kpoints(k_cart)


if __name__ == "__main__":
    run()

