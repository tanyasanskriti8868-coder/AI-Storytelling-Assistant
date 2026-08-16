@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ======================================
echo Arcanova AI - Anaconda Launcher
echo ======================================

a:: Find conda.bat in common install paths
set "CONDA_BAT="
if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "C:\ProgramData\anaconda3\condabin\conda.bat" set "CONDA_BAT=C:\ProgramData\anaconda3\condabin\conda.bat"
if not defined CONDA_BAT if exist "C:\ProgramData\miniconda3\condabin\conda.bat" set "CONDA_BAT=C:\ProgramData\miniconda3\condabin\conda.bat"

if not defined CONDA_BAT (
    echo [ERROR] Conda not found.
    echo Install Anaconda or Miniconda, then run this file again.
    pause
    exit /b 1
)

echo [1/5] Checking environment: arcanova
call "%CONDA_BAT%" run -n arcanova python --version >nul 2>&1
if errorlevel 1 (
    echo Environment not found. Creating it now...
    call "%CONDA_BAT%" create -n arcanova python=3.10 -y
    if errorlevel 1 (
        echo [ERROR] Failed to create conda environment.
        pause
        exit /b 1
    )
)

echo [2/5] Activating environment
call "%CONDA_BAT%" activate arcanova
if errorlevel 1 (
    echo [ERROR] Failed to activate conda environment.
    pause
    exit /b 1
)

echo [3/5] Upgrading pip
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] pip upgrade failed.
    pause
    exit /b 1
)

echo [4/5] Verifying dependencies
python -c "import streamlit, torch, transformers, pyttsx3" >nul 2>&1
if errorlevel 1 (
    echo Missing packages found. Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

echo [5/5] Starting Streamlit app
start "" http://localhost:8501
streamlit run app.py

endlocal
