@echo off
echo Killing all ffmpeg processes to unlock files...
echo.

REM Try with pipenv first
pipenv run python kill_ffmpeg.py

REM If pipenv fails, try direct python
if errorlevel 1 (
    echo Pipenv failed, trying direct python...
    python kill_ffmpeg.py
)

REM If python fails, use direct taskkill
if errorlevel 1 (
    echo Python failed, using direct taskkill...
    echo Looking for ffmpeg processes...
    tasklist /fi "imagename eq ffmpeg.exe"
    echo.
    echo Killing ffmpeg processes...
    taskkill /f /im ffmpeg.exe
    echo Done!
)

echo.
pause
