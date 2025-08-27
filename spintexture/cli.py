#!/usr/bin/env python3
"""
Menu-driven CLI for spintexture package v0.1.0

Main menu:
    1. 2D Materials
    0. Exit

2D Materials menu:
    1. Generate 2D k-mesh
    2. Plot 2D spin texture
    3. Plot 3D spin texture (kx, ky, E)
    0. Back
"""

import sys
from spintexture import kmesh, spin2d, spin3d

def main():
    banner = r"""
   ==========================================
    SPINTEXTURE PACKAGE - CLI INTERFACE
    Tools for K-mesh generation & Spin plots
   ==========================================
    """
    print(banner)
    print("1. 2D Materials")
    print("0. Exit")

    while True:
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            materials_2d_menu()
            break
        elif choice == "0":
            print("Exiting spintexture CLI. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.\n")

def materials_2d_menu():
    banner = r"""
--- 2D Materials ---
    """
    print(banner)
    print("1. Generate 2D k-mesh")
    print("2. Plot 2D spin texture")
    print("3. Plot 3D spin texture (kx, ky, E)")
    print("0. Back")

    while True:
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            print("\n--- Running 2D k-mesh generator ---\n")
            kmesh.run()
            break
        elif choice == "2":
            print("\n--- Running 2D spin texture plot ---\n")
            spin2d.run()
            break
        elif choice == "3":
            print("\n--- Running 3D spin texture plot (kx, ky, E) ---\n")
            spin3d.run()
            break
        elif choice == "0":
            main()
            break
        else:
            print("Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
