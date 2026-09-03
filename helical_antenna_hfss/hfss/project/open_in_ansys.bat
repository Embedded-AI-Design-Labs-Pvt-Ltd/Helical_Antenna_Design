@echo off
set SCRIPT=%~dp0build_helix_hfss.py
where ansysedt >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Opening Ansys Electronics Desktop with helical antenna script...
  start "" ansysedt -RunScript "%SCRIPT%"
  goto :eof
)
echo ansysedt.exe not on PATH. Open Electronics Desktop, then:
echo   Tools ^> Run Script ^> %SCRIPT%
pause
