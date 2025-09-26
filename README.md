# Video Converter GUI

A GPU-accelerated video converter with a user-friendly GUI interface, built with Python and tkinter.

## Features

- 🖥️ **Easy-to-use GUI** - Simple file selection and conversion
- 🚀 **GPU Acceleration** - Uses NVIDIA NVENC when available, falls back to CPU
- 🎬 **Multiple Codecs** - Supports H.264 and H.265 encoding (H.265 default)
- 📊 **Real-time Progress** - Shows conversion progress and status
- 📁 **Smart File Handling** - Auto-suggests output filenames
- 🌐 **UTF-8 Support** - Handles international filenames (Thai, Chinese, etc.)
- 🛑 **Process Control** - Stop conversion anytime, proper cleanup
- 🔓 **File Lock Management** - Release locked files, kill zombie processes
- 🔧 **Standalone Executable** - No Python installation required for end users
- 📦 **Pipenv Integration** - Modern dependency management

## Prerequisites

### For Running the Source Code:
- Python 3.10 or higher
- Pipenv (install with `pip install pipenv`)
- FFmpeg installed and available in PATH
- NVIDIA GPU with NVENC support (optional, for GPU acceleration)

### For Building the Executable:
- All of the above
- Dependencies managed automatically via Pipenv

## Download & Installation

### 🚀 Quick Start (Recommended)
**Download the pre-built executable:**
- 📥 **[VideoConverter.exe](dist/VideoConverter.exe)** (9.1 MB)
- ✅ No Python installation required
- ✅ No dependencies to install
- ✅ Just download and run!

**Requirements for the executable:**
- Windows 10/11
- FFmpeg installed and in PATH ([Download FFmpeg](https://ffmpeg.org/download.html))
- NVIDIA GPU with NVENC (optional, for GPU acceleration)

**How to use:**
1. Download `VideoConverter.exe` from the link above
2. Double-click to run the application
3. Select your input video file
4. Choose output location and codec (H.265 recommended)
5. Click "Convert Video" and watch the progress!

### 🛠️ Advanced: Run from Source

### Option 1: Run from Source with Pipenv
```bash
# Install pipenv if not already installed
pip install pipenv

# Install dependencies in virtual environment
pipenv install

# Run the GUI
pipenv run python convert_gui.py
```
### Option 2: Build Standalone Executable
```bash
# Method 1: Use the batch file (Windows)
build.bat

# Method 2: Manual build with pipenv
pipenv install
pipenv run python build_complete.py

# Method 3: Direct PyInstaller with pipenv
pipenv run pyinstaller --onefile --windowed --name=VideoConverter convert_gui.py
```
The executable will be created in the `dist` folder as `VideoConverter.exe`.

## How to Use
1. **Select Input File**: Click "Browse" next to "Input File" and choose your video file
2. **Choose Output Location**: Click "Browse" next to "Output File" to set where to save the converted video
3. **Select Codec**: Choose between H.264 (faster, larger files) or H.265 (slower, smaller files)
4. **GPU Acceleration**: Keep checked for faster conversion (if you have NVIDIA GPU)
5. **Click Convert**: Start the conversion process

## Supported Input Formats

- MP4, AVI, MKV, MOV, WMV, FLV, WebM, TS, M4V
- And many more formats supported by FFmpeg

## Output Format

- Primary output: MP4 with AAC audio
- Video bitrate: 5 Mbps
- Audio bitrate: 192 kbps

## GPU Requirements

For GPU acceleration, you need:
- NVIDIA GPU with NVENC support (GTX 600 series or newer)
- Updated NVIDIA drivers
- FFmpeg compiled with NVENC support

If GPU acceleration is not available, the tool will automatically fall back to CPU encoding.

## Troubleshooting

### "ไม่พบ ffmpeg ในระบบ" Error
- Download FFmpeg from https://ffmpeg.org/download.html
- Extract and add the `bin` folder to your system PATH
- Restart the application

### GPU Acceleration Not Working
- Ensure you have an NVIDIA GPU with NVENC support
- Update your NVIDIA drivers
- Check if your FFmpeg build includes NVENC support

### Conversion Fails
- Check the status log in the GUI for detailed error messages
- Ensure input file is not corrupted
- Make sure output directory is writable
- Try a different codec (H.264 vs H.265)

### File Locked / Cannot Rename Files
If you get "File In Use" errors when trying to rename video files:

**Method 1: Use GUI**
- Click "Release Locks" button in the GUI
- Click "Clear" button next to input file

**Method 2: Kill FFmpeg Processes**
- Double-click `kill_ffmpeg.bat`
- Or run `pipenv run python kill_ffmpeg.py`

**Method 3: Manual Command**
```cmd
taskkill /f /im ffmpeg.exe
```

### UTF-8 Filename Issues
- The GUI now supports international characters (Thai, Chinese, Japanese, etc.)
- Files with Unicode names are handled automatically
- Output directories are created automatically if they don't exist

## File Structure

```
FormatFactory/
├── Pipfile                 # Pipenv dependencies
├── Pipfile.lock           # Locked versions (auto-generated)
├── convert.py             # Original command-line version
├── convert_gui.py         # GUI version with UTF-8 support
├── build_complete.py      # Complete build script (pipenv-enabled)
├── build_exe.py           # Alternative build script
├── build.bat             # Windows batch file for easy building
├── run_gui.bat           # Run GUI with pipenv
├── test_gui.py           # GUI component test script
├── test_pipenv.bat       # Test with pipenv
├── kill_ffmpeg.py        # FFmpeg process killer script
├── kill_ffmpeg.bat       # Kill FFmpeg processes (batch)
├── requirements.txt       # Legacy Python dependencies
├── README.md             # This documentation
└── dist/                 # Built executable (after building)
    └── VideoConverter.exe
```

## Technical Details

- **GUI Framework**: tkinter (Python standard library)
- **Video Processing**: FFmpeg with UTF-8 encoding support
- **GPU Acceleration**: NVIDIA NVENC (H.264/H.265)
- **Dependency Management**: Pipenv for virtual environments
- **Process Management**: psutil for advanced process control
- **Executable Builder**: PyInstaller with hidden imports
- **Threading**: Separate thread for conversion to keep GUI responsive
- **File Handling**: Proper UTF-8 path normalization and lock management
- **Default Codec**: H.265 (HEVC) for better compression

## License

This project is open source. Feel free to modify and distribute.
