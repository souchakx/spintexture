# spintexture/utils.py
import numpy as np

def read_poscar(filename="POSCAR"):
    """Read POSCAR and return reciprocal lattice matrix (B)."""
    with open(filename, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    scale = float(lines[1])
    a1 = np.fromstring(lines[2], sep=" ")
    a2 = np.fromstring(lines[3], sep=" ")
    a3 = np.fromstring(lines[4], sep=" ")
    A = np.vstack([a1, a2, a3]) * scale
    V = np.dot(A[0], np.cross(A[1], A[2]))
    b1 = 2*np.pi * np.cross(A[1], A[2]) / V
    b2 = 2*np.pi * np.cross(A[2], A[0]) / V
    b3 = 2*np.pi * np.cross(A[0], A[1]) / V
    return np.vstack([b1, b2, b3])

def frac_to_cart(k_frac, B):
    """Fractional → Cartesian k-points."""
    return k_frac @ B

def cart_to_frac(k_cart, B):
    """Cartesian → Fractional k-points."""
    return k_cart @ np.linalg.inv(B)
