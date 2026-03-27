@echo off
REM Build Neural Speed Academy as a standalone Windows .exe
REM Run this from the project root: build_exe.bat

echo === Neural Speed Academy - Windows Build ===
echo.

REM Try to find Python
where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON=py
    goto :found
)
where python >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON=python
    goto :found
)
echo ERROR: Python not found. Install from https://www.python.org/downloads/
echo        Make sure to check "Add Python to PATH" during installation.
pause
exit /b 1

:found
echo Using: %PYTHON%
%PYTHON% --version
echo.

REM Install dependencies
echo Installing dependencies...
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install PyQt6>=6.5 pyinstaller>=6.0
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo.

REM Build the exe
echo Building executable...
%PYTHON% -m PyInstaller --onefile --windowed --name "NeuralSpeedAcademy" nsa.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo === Build complete ===
echo Executable: dist\NeuralSpeedAcademy.exe
echo.
pause
