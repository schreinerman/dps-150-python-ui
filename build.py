"""
Build script for cross-platform application creation
Uses PyInstaller to create native executables
"""

import os
import sys
import platform
import shutil
from pathlib import Path

def get_platform_spec():
    """Detects the current operating system"""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"

def clean_build():
    """Cleans previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Delete .spec file if present
    spec_file = 'gui_app.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)

def build_app(target_arch=None):
    """Builds the native application
    
    Args:
        target_arch: Target architecture for macOS builds.
                    Options: 'universal2' (Intel+ARM), 'x86_64' (Intel), 'arm64' (Apple Silicon)
                    Default: None (uses system architecture)
    """
    plat = get_platform_spec()
    
    arch_info = f" ({target_arch})" if target_arch else ""
    print(f"Building application for {plat}{arch_info}...")
    
    # PyInstaller arguments (without 'pyinstaller' at the start)
    args = [
        '--name=DPS150-Control',
        '--windowed',  # No console window
        '--onefile',   # Single executable file
        '--clean',
        # Hidden imports for PyQtGraph and Numpy
        '--hidden-import=pyqtgraph',
        '--hidden-import=numpy',
        '--hidden-import=numpy.core._multiarray_umath',
        # PyQtGraph submodules (only necessary ones)
        '--hidden-import=pyqtgraph.graphicsItems',
        '--hidden-import=pyqtgraph.widgets',
        # Excludes to reduce app size
        '--exclude-module=pyqtgraph.examples',
        '--exclude-module=pyqtgraph.opengl',  # Requires PyOpenGL
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        'gui_app.py'
    ]
    
    # Platform-specific adjustments
    if plat == "macos":
        # On macOS no --icon=NONE, that leads to errors
        # Add target architecture if specified
        if target_arch:
            args.append(f'--target-arch={target_arch}')
            print(f"  -> Building for architecture: {target_arch}")
        # Note: By default, PyInstaller builds for the native architecture
    elif plat == "windows":
        # On Windows an icon could be specified here
        # args.extend(['--icon=icon.ico'])
        pass
    
    # Run PyInstaller
    import PyInstaller.__main__
    PyInstaller.__main__.run(args)
    
    print(f"\n[OK] Build completed!")
    print(f"The application is located in the 'dist' folder")
    
    if plat == "macos":
        print(f"  -> dist/DPS150-Control.app")
    elif plat == "windows":
        print(f"  -> dist/DPS150-Control.exe")
    else:
        print(f"  -> dist/DPS150-Control")

def check_venv():
    """Checks if script is running in venv"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("[WARNING] Script is not running in a virtual environment!")
        print("   Recommended: Use build.sh (macOS/Linux) or build.bat (Windows)")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['j', 'ja', 'y', 'yes']:
            print("Build cancelled.")
            sys.exit(0)
        print()
    else:
        print("[OK] Running in virtual environment")
        print()

def main():
    """Main function"""
    print("=== DPS-150 Native App Builder ===\n")
    
    # Check venv
    check_venv()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("[ERROR] PyInstaller is not installed.")
        print("   Install it with: pip install pyinstaller")
        print("   Or use: ./build.sh (macOS/Linux) or build.bat (Windows)")
        sys.exit(1)
    
    # Parse command line arguments
    target_arch = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['--arch', '-a'] and len(sys.argv) > 2:
            target_arch = sys.argv[2]
        elif arg in ['universal2', 'x86_64', 'arm64']:
            target_arch = arg
    
    # Perform build
    clean_build()
    build_app(target_arch)
    
    print("\n=== [SUCCESS] Build successful! ===")

if __name__ == '__main__':
    main()
