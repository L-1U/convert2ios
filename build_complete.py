"""
Complete build script for Video Converter GUI
This script handles the entire build process including dependency installation
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔄 {description}")
    print(f"Command: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False

def main():
    print("🚀 Video Converter GUI - Complete Build Process (with Pipenv)")
    print("This script will:")
    print("1. Install pipenv virtual environment and dependencies")
    print("2. Build the standalone executable")
    print("3. Test the build")
    
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Step 1: Install pipenv and dependencies
    if not run_command("pipenv install", 
                      "Installing pipenv virtual environment and dependencies"):
        print("⚠️ Failed to install dependencies. Please ensure pipenv is installed:")
        print("pip install pipenv")
        print("Then run: pipenv install")
        return False
    
    # Step 2: Build executable using pipenv
    build_command = '''pipenv run pyinstaller --onefile --windowed --name=VideoConverter --clean --noconfirm --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox convert_gui.py'''
    
    if not run_command(build_command, "Building standalone executable with pipenv"):
        print("❌ Build failed!")
        return False
    
    # Step 3: Check if executable was created
    exe_path = current_dir / "dist" / "VideoConverter.exe"
    if exe_path.exists():
        print(f"\n🎉 SUCCESS! Executable created at:")
        print(f"📁 {exe_path}")
        print(f"📊 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Create a simple test
        print("\n📋 Build Summary:")
        print("✅ GUI application created")
        print("✅ Standalone executable built")
        print("✅ No Python installation required for end users")
        print("\n🔧 To use:")
        print("1. Double-click VideoConverter.exe")
        print("2. Select input video file")
        print("3. Choose output location")
        print("4. Select codec (H.264 or H.265)")
        print("5. Click 'Convert Video'")
        
        print("\n⚠️ Requirements for end users:")
        print("- FFmpeg must be installed and in PATH")
        print("- NVIDIA GPU with NVENC for GPU acceleration (optional)")
        
        return True
    else:
        print("❌ Executable not found after build!")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎊 All done! Your video converter is ready to use!")
    else:
        print("\n💥 Build process failed. Please check the errors above.")
    
    input("\nPress Enter to exit...")
