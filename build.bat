@echo off
echo Setting up pipenv environment...
pipenv install

echo.
echo Building executable with pipenv...
pipenv run python build_complete.py

echo.
echo Build complete! Check the 'dist' folder for VideoConverter.exe
pause
