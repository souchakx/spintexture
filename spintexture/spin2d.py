# spintexture/spin2d.py

"""
spin2d.py

Plots in-plane spin textures (Sx, Sy) for 2D materials from VASP PROCAR (non-collinear).
Optionally overlays a colormap showing Sz, energy, or none.

Usage (CLI):
------------
    $ spintexture   # choose 2D materials -> spin2d

Configuration (edit these values at the top):
--------------------------------------------
# Arrow options
ARROW_SCALE        = 50        # scale factor for arrow lengths
ARROW_COLOR        = "lightgray"
ARROW_EDGE_COLOR   = "k"
ARROW_LINEWIDTH    = 0.35
ARROW_HEADLENGTH   = 4
ARROW_HEADAXISLEN  = 3.5
ARROW_WIDTH        = 0.006

# Colormap options
COLORMAP_DEFAULT   = "sz"      # options: 'sz', 'energy', 'none'
COLORMAP_NAME      = "RdBu_r"

# Grid options
KAX_LIM            = 0.2       # plotting range in Å^-1
INTERP_N           = 400       # interpolation grid size

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
from scipy.interpolate import griddata
from .utils import read_poscar, frac_to_cart

# ------------------- User-configurable parameters ---------------------- #
ARROW_SCALE        = 50
ARROW_COLOR        = "lightgray"
ARROW_EDGE_COLOR   = "k"
ARROW_LINEWIDTH    = 0.35
ARROW_HEADLENGTH   = 4
ARROW_HEADAXISLEN  = 3.5
ARROW_WIDTH        = 0.006

COLORMAP_DEFAULT   = "sz"
COLORMAP_NAME      = "RdBu_r"

KAX_LIM            = 0.2
INTERP_N           = 400

POSCAR = "POSCAR"
PROCAR = "PROCAR"

# --------------------- PROCAR parser ----------------------------------- #
def parse_procar_soc(filename=PROCAR, band_no=18):
    kpts_frac, spins, stots, energies = [], [], [], []
    with open(filename, "r") as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("k-point"):
            nums = re.findall(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?', lines[i])
            if len(nums) >= 3:
                kpt_frac = [float(nums[0]), float(nums[1]), float(nums[2])]
            else: i+=1; continue
            i+=1
            while i < len(lines):
                if lines[i].strip().startswith("band"):
                    parts = lines[i].split()
                    try: band = int(parts[1]); energy = float(parts[4])
                    except: band, energy = None, None
                    i+=1
                    if band==band_no:
                        tot_lines=[]
                        while i<len(lines) and len(tot_lines)<4:
                            if lines[i].strip().startswith("tot"): tot_lines.append(lines[i].strip())
                            i+=1
                        if len(tot_lines)==4:
                            stot = float(tot_lines[0].split()[-1])
                            sx   = float(tot_lines[1].split()[-1])
                            sy   = float(tot_lines[2].split()[-1])
                            sz   = float(tot_lines[3].split()[-1])
                            kpts_frac.append(kpt_frac)
                            spins.append([sx,sy,sz])
                            stots.append(stot)
                            energies.append(energy)
                        break
                else: i+=1
        else: i+=1
    return np.array(kpts_frac), np.array(spins), np.array(stots), np.array(energies)

# --------------------- Plot and save ----------------------------------- #
def plot_and_save(POSCAR, PROCAR, BAND_NO):
    B = read_poscar(POSCAR)
    k_frac, spins, stots, energies = parse_procar_soc(PROCAR, BAND_NO)
    k_cart = frac_to_cart(k_frac, B)
    x_c, y_c = k_cart[:,0], k_cart[:,1]
    sx, sy, sz = spins[:,0], spins[:,1], spins[:,2]

    # Save data files
    fname_cart = f"band{BAND_NO}_data_cartesian.dat"
    with open(fname_cart,"w") as f:
        f.write("# E(eV) kx ky kz Sx Sy Sz Stot\n")
        for e,(kx,ky,kz),(sxi,syi,szi),st in zip(energies,k_cart,spins,stots):
            f.write(f"{e:12.6f} {kx:12.6f} {ky:12.6f} {kz:12.6f} "
                    f"{sxi:12.6f} {syi:12.6f} {szi:12.6f} {st:12.6f}\n")
    print(f"Saved Cartesian k-data to {fname_cart}")

    fname_frac = f"band{BAND_NO}_data_fractional.dat"
    with open(fname_frac,"w") as f:
        f.write("# E(eV) kx ky kz Sx Sy Sz Stot\n")
        for e,(kx,ky,kz),(sxi,syi,szi),st in zip(energies,k_frac,spins,stots):
            f.write(f"{e:12.6f} {kx:12.6f} {ky:12.6f} {kz:12.6f} "
                    f"{sxi:12.6f} {syi:12.6f} {szi:12.6f} {st:12.6f}\n")
    print(f"Saved fractional k-data to {fname_frac}")

    # Colormap
    cmap_choice = input(f"Colormap type - 'sz','energy','none' [default: {COLORMAP_DEFAULT}]: ").strip().lower()
    if cmap_choice not in ("sz","energy","none",""): cmap_choice=COLORMAP_DEFAULT

    xi = np.linspace(-KAX_LIM,KAX_LIM,INTERP_N)
    yi = np.linspace(-KAX_LIM,KAX_LIM,INTERP_N)
    fig, ax = plt.subplots(figsize=(6,5))

    zi = None; label=None; vmax=None
    if cmap_choice in ("","sz"):
        zi = griddata((x_c,y_c), sz, (xi[None,:], yi[:,None]), method="cubic")
        vmax=np.nanmax(np.abs(sz)); label=r"$S_z$"
    elif cmap_choice=="energy":
        zi = griddata((x_c,y_c), energies, (xi[None,:], yi[:,None]), method="cubic")
        vmax=np.nanmax(np.abs(energies)); label="Energy (eV)"

    if zi is not None:
        pcm = ax.imshow(zi,extent=[-KAX_LIM,KAX_LIM,-KAX_LIM,KAX_LIM],
                        origin="lower", cmap=COLORMAP_NAME,
                        vmin=-vmax,vmax=vmax,aspect="equal")
        cbar = plt.colorbar(pcm,ax=ax); cbar.set_label(label)

    ax.quiver(x_c,y_c,sx,sy,
              color=ARROW_COLOR, ec=ARROW_EDGE_COLOR,
              linewidths=ARROW_LINEWIDTH,
              angles="xy", scale_units="xy", scale=ARROW_SCALE,
              headlength=ARROW_HEADLENGTH, headaxislength=ARROW_HEADAXISLEN,
              width=ARROW_WIDTH)

    ax.set_xlim(-KAX_LIM,KAX_LIM); ax.set_ylim(-KAX_LIM,KAX_LIM)
    ax.set_xlabel(r"$k_x$ (Å$^{-1}$)"); ax.set_ylabel(r"$k_y$ (Å$^{-1}$)")
    ax.set_title(f"band {BAND_NO}", loc="left", fontsize=10)
    plt.tight_layout()

    outname = f"band{BAND_NO}_spintexture.png"
    plt.savefig(outname,dpi=600); plt.show()
    print(f"Saved plot to {outname}")

# --------------------- CLI runner ------------------------------------- #
def run():
    band = int(input("Enter band number: "))
    plot_and_save(POSCAR, PROCAR, band)

if __name__=="__main__":
    run()
