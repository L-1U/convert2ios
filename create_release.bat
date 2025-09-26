@echo off
echo 🚀 Video Converter Release Creator
echo ================================

REM Check if version argument is provided
if "%1"=="" (
    echo Usage: create_release.bat [version]
    echo Example: create_release.bat v1.0.0
    echo.
    echo Current tags:
    git tag --sort=-version:refname
    echo.
    set /p VERSION="Enter version (e.g., v1.0.0): "
) else (
    set VERSION=%1
)

echo.
echo Creating release for version: %VERSION%
echo.

REM Check if we're on a clean working directory
git status --porcelain > nul
if errorlevel 1 (
    echo ❌ Git repository not found
    pause
    exit /b 1
)

for /f %%i in ('git status --porcelain') do (
    echo ⚠️ Warning: You have uncommitted changes
    echo Please commit or stash your changes first
    git status --short
    pause
    exit /b 1
)

REM Create and push tag
echo 📝 Creating tag %VERSION%...
git tag -a %VERSION% -m "Release %VERSION%"

if errorlevel 1 (
    echo ❌ Failed to create tag
    pause
    exit /b 1
)

echo 📤 Pushing tag to GitHub...
git push origin %VERSION%

if errorlevel 1 (
    echo ❌ Failed to push tag
    echo You may need to delete the local tag: git tag -d %VERSION%
    pause
    exit /b 1
)

echo.
echo ✅ Success! 
echo 🎉 GitHub Action will now build and create the release automatically
echo 📋 Check the Actions tab on GitHub to monitor progress
echo 🔗 Release will be available at: https://github.com/[your-username]/[your-repo]/releases
echo.
pause
