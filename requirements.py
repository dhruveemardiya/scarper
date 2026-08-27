#!/usr/bin/env python3
"""
requirements.py - Dependency checker, installer, and generator for DataScraper Desktop.

Usage:
    python requirements.py          # Check and auto-install missing packages
    python requirements.py --check  # Only check missing packages without installing
    python requirements.py --install# Force install / upgrade all dependencies
"""

import sys
import subprocess
import importlib.util
from typing import List, Tuple

# Core dependency definitions: (pip_package_name, import_module_name, minimum_version)
DEPENDENCIES = [
    ("selenium>=4.20.0", "selenium", "4.20.0"),
    ("beautifulsoup4>=4.12.0", "bs4", "4.12.0"),
    ("pandas>=2.2.0", "pandas", "2.2.0"),
    ("requests>=2.31.0", "requests", "2.31.0"),
    ("webdriver-manager>=4.0.0", "webdriver_manager", "4.0.0"),
    ("lxml>=5.0.0", "lxml", "5.0.0"),
    ("aiohttp>=3.9.0", "aiohttp", "3.9.0"),
    ("websockets>=12.0", "websockets", "12.0"),
]

def check_dependencies() -> Tuple[List[str], List[str]]:
    """Check which dependencies are installed vs missing."""
    installed = []
    missing = []
    
    for pkg_spec, mod_name, min_ver in DEPENDENCIES:
        spec = importlib.util.find_spec(mod_name)
        if spec is not None:
            try:
                mod = importlib.import_module(mod_name)
                ver = getattr(mod, "__version__", "unknown")
                installed.append(f"✓ {pkg_spec:<25} (installed: {ver})")
            except Exception as e:
                missing.append(pkg_spec)
        else:
            missing.append(pkg_spec)
            
    return installed, missing

def install_packages(packages: List[str]) -> bool:
    """Install packages using pip."""
    if not packages:
        print("All dependencies are already satisfied!")
        return True

    print(f"\nInstalling missing packages: {', '.join(packages)}...\n")
    cmd = [sys.executable, "-m", "pip", "install"] + packages
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    print("=" * 60)
    print(" DataScraper Python Requirements & Dependency Manager")
    print("=" * 60)

    installed, missing = check_dependencies()

    print("\nInstalled Dependencies:")
    for item in installed:
        print(f"  {item}")

    if missing:
        print("\nMissing Dependencies:")
        for item in missing:
            print(f"  ✗ {item}")

    if "--check" in sys.argv:
        if missing:
            print(f"\n{len(missing)} package(s) missing. Run 'python requirements.py' to install.")
            sys.exit(1)
        else:
            print("\nAll dependencies are verified and up to date.")
            sys.exit(0)

    if "--install" in sys.argv:
        all_pkgs = [pkg for pkg, _, _ in DEPENDENCIES]
        success = install_packages(all_pkgs)
        sys.exit(0 if success else 1)

    if missing:
        print(f"\nFound {len(missing)} missing package(s). Installing now...")
        success = install_packages(missing)
        if success:
            print("\n✓ All requirements installed successfully!")
        else:
            print("\n✗ Failed to install some dependencies. Please run 'pip install -r requirements.txt' manually.")
            sys.exit(1)
    else:
        print("\n✓ All requirements are already installed and ready!")

if __name__ == "__main__":
    main()
