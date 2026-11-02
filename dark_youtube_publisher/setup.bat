@echo off
REM DARK YOUTUBE PUBLISHER — Setup Windows
REM DARK STUDIO AAA

echo.
echo ========================================
echo  DARK YOUTUBE PUBLISHER — SETUP
echo  DARK STUDIO AAA v1.0.0
echo ========================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10+ em python.org
    pause
    exit /b 1
)

REM Cria ambiente virtual
echo [1/5] Criando ambiente virtual...
python -m venv venv
if errorlevel 1 goto :error

REM Ativa ambiente
call venv\Scripts\activate.bat

REM Instala dependencias
echo [2/5] Instalando dependencias...
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 goto :error

REM Cria pasta de configuracao
echo [3/5] Criando pastas de configuracao...
if not exist "%USERPROFILE%\.dark_studio\tokens" mkdir "%USERPROFILE%\.dark_studio\tokens"
if not exist "%USERPROFILE%\.dark_studio\publish_results" mkdir "%USERPROFILE%\.dark_studio\publish_results"

REM Instala CLI
echo [4/5] Instalando DARK YOUTUBE CLI...
pip install -e . --quiet

REM Verifica client_secrets.json
echo [5/5] Verificando configuracao OAuth...
if not exist "%USERPROFILE%\.dark_studio\client_secrets.json" (
    echo.
    echo [AVISO] client_secrets.json nao encontrado!
    echo.
    echo Para completar a configuracao:
    echo 1. Acesse console.cloud.google.com
    echo 2. Crie um projeto e habilite YouTube Data API v3
    echo 3. Crie credenciais OAuth 2.0 (Desktop App)
    echo 4. Baixe o JSON e salve em:
    echo    %USERPROFILE%\.dark_studio\client_secrets.json
    echo.
) else (
    echo [OK] client_secrets.json encontrado!
)

echo.
echo ========================================
echo  INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Comandos disponiveis:
echo   dark-youtube list         - Lista canais
echo   dark-youtube auth         - Autoriza canal
echo   dark-youtube publish      - Publica video
echo   dark-youtube batch2       - Publica Batch 2
echo.
echo Iniciar servidor API:
echo   uvicorn dark_youtube_publisher.api.main:app --reload
echo.
pause
exit /b 0

:error
echo [ERRO] Falha na instalacao. Verifique o log acima.
pause
exit /b 1
