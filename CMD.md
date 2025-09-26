# CMD
```bash
pipenv --python 3.11
pipenv install ffmpeg-python
pipenv run python convert.py "C:\Users\U17LI\Downloads\Video\The Legend of the Condor Heroes The Gallants.ts" "C:\Users\U17LI\Videos\MP4\The Legend of the Condor Heroes The Gallants.mp4" h265
```
## Install
```bash
# Install pipenv if not already installed
pip install pipenv

# Install all dependencies in virtual environment
pipenv install
```
## Run GUI
```bash
# Option 1: Command line
pipenv run python convert_gui.py

# Option 2: Use batch file
run_gui.bat
```
## Build
```bash
# Option 1: Use batch file
build.bat

# Option 2: Manual
pipenv run python build_complete.py
```

## Kill FFMPEG
```bash
# Option 1: Use batch file
kill_ffmpeg.bat

# Option 2: Manual
pipenv run python kill_ffmpeg.py
```
