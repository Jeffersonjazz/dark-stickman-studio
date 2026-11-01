@echo off
:: DARK STICKMAN STUDIO — Launcher
:: ai_generated: True
:: ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
title DARK STICKMAN STUDIO
color 0A

cd /d "%~dp0"

:: Ativar ambiente virtual
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [AVISO] Ambiente virtual nao encontrado.
    echo Execute setup\setup_wizard.bat primeiro.
    pause & exit /b 1
)

echo.
echo  ##################################################
echo  ##  DARK STICKMAN STUDIO — DARK CREATIVE LAB   ##
echo  ##  Custo: R$0,00/mes                          ##
echo  ##################################################
echo.
echo  Iniciando servidor...
echo  Painel:  http://localhost:8000/panel
echo  API:     http://localhost:8000
echo  Docs:    http://localhost:8000/docs
echo.
echo  (Pressione Ctrl+C para encerrar)
echo.

:: Abrir painel no navegador apos 2 segundos
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000/panel"

:: Iniciar servidor FastAPI
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
