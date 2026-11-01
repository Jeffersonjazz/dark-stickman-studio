@echo off
:: Atalho CLI para DARK STICKMAN STUDIO
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" call venv\Scripts\activate.bat
python cli\dark_stickman.py %*
