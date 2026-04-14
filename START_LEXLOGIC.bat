@echo off
title LexLogic Desktop - AI Legal Reasoning System
color 0B

echo.
echo  ==========================================================
echo    LexLogic Desktop  v2.0   -   AI Legal Reasoning System
echo    Project 4.1  :  Propositional + FOL  :  Fwd + Bwd Chain
echo  ==========================================================
echo.

python --version >nul 2>^&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    echo  Download: https://www.python.org/downloads/
    echo  Check "Add Python to PATH" during install.
    pause & exit /b 1
)

python -c "import reportlab" >nul 2>^&1
if errorlevel 1 (
    echo  Installing ReportLab (PDF generator)...
    pip install reportlab -q
)

where swipl >nul 2>^&1
if errorlevel 1 (
    echo  Note: SWI-Prolog not found. Using Python FOL engine.
    echo  Optional install: https://www.swi-prolog.org/download
) else (
    echo  SWI-Prolog detected - native Prolog inference active!
)

echo.
echo  Launching LexLogic Desktop...
echo.

cd /d "%~dp0"
python lexlogic.py

pause
