"""
Build script for creating a standalone executable of the Video Converter GUI
"""
import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Define paths
    script_path = current_dir / "convert_gui.py"
    icon_path = None  # You can add an icon file here if you have one
    
    # PyInstaller arguments
    args = [
        str(script_path),
        '--onefile',                    # Create a single executable file
        '--windowed',                   # Hide console window (GUI mode)
        '--name=VideoConverter',        # Name of the executable
        '--clean',                      # Clean PyInstaller cache
        '--noconfirm',                  # Replace output directory without confirmation
        f'--distpath={current_dir / "dist"}',  # Output directory
        f'--workpath={current_dir / "build"}', # Work directory
        f'--specpath={current_dir}',    # Spec file location
    ]
    
    # Add icon if available
    if icon_path and icon_path.exists():
        args.append(f'--icon={icon_path}')
    
    # Add hidden imports that might be needed
    args.extend([
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=tkinter.messagebox',
    ])
    
    print("Building executable with PyInstaller...")
    print("Arguments:", ' '.join(args))
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n" + "="*50)
    print("Build completed!")
    print(f"Executable location: {current_dir / 'dist' / 'VideoConverter.exe'}")
    print("="*50)

if __name__ == "__main__":
    build_executable()
