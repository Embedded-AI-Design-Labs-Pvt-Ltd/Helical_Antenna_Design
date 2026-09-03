@echo off
title 3.035 GHz Helical Antenna HFSS — Full Run
cd /d "%~dp0"

echo ========================================
echo  3.035 GHz Helical Antenna
echo  Full HFSS workflow + GUI
echo ========================================
echo.

python -c "import matplotlib,numpy" 2>nul
if errorlevel 1 (
  echo Installing numpy and matplotlib...
  python -m pip install numpy matplotlib
  if errorlevel 1 (
    echo Python packages failed to install.
    pause
    exit /b 1
  )
)

echo.
echo [1/3] Running geometry, HFSS model, reports, QA...
echo       Ansys Electronics Desktop will open if it is installed.
echo.
python "%~dp0scripts\workflow.py"
set WF_ERR=%ERRORLEVEL%
if not "%WF_ERR%"=="0" (
  echo Workflow finished with error code %WF_ERR%.
)

echo.
echo [2/3] Opening HTML dashboard...
if exist "%~dp0docs\index.html" (
  start "" "%~dp0docs\index.html"
)

echo.
echo [3/3] Starting the GUI...
start "Helical Antenna HFSS GUI" python "%~dp0run_gui.py"

echo.
echo ========================================
echo  Finished.
echo  GUI is open. Press RUN in the GUI to rebuild / reopen HFSS.
echo  Results stay NOT SIMULATED until HFSS actually solves.
echo ========================================
echo.
if /I not "%~1"=="nopause" pause
