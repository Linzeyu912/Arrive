@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\pythonw.exe" (
  echo Arrive Python environment is missing. See README.md.
  pause
  exit /b 1
)
start "" "backend\.venv\Scripts\pythonw.exe" "%~dp0scripts\launch_arrive.py"
