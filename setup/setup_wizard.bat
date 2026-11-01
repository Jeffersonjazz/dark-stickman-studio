@echo off
:: ═══════════════════════════════════════════════════════════════
:: DARK STUDIO AAA — Setup Wizard para Windows
:: DARK CREATIVE LAB — Instalador Automatico
::
:: Instala dependencias, configura ambiente, cria atalho
:: e valida a instalacao completa.
::
:: ai_generated: True
:: ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
:: ═══════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion
title DARK STUDIO AAA — Instalador v1.3

echo.
echo  ================================
echo   DARK STUDIO AAA — Instalador
echo   Plataforma de Criacao com IA
echo  ================================
echo.
echo  ai_disclosure: Produzido com DARK STUDIO AAA
echo.

:: ── Admin Check ──────────────────────────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Execute como Administrador!
    echo Clique com botao direito e selecione "Executar como Administrador"
    pause
    exit /b 1
)

set "INSTALL_DIR=%USERPROFILE%\DarkStudioAAA"
set "REPO_URL=https://github.com/Jeffersonjazz/dark-stickman-studio.git"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "DESKTOP=%USERPROFILE%\Desktop"

echo [1/9] Verificando pre-requisitos...

:: Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.10+ em: https://www.python.org/downloads/
    echo IMPORTANTE: Marque "Add Python to PATH" na instalacao.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER%

:: Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Git nao encontrado!
    echo Instale Git em: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo  [OK] Git instalado

:: FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] FFmpeg nao encontrado. Tentando instalar via winget...
    winget install --id Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    echo  [AVISO] Se winget falhou, instale FFmpeg manualmente: https://www.gyan.dev/ffmpeg/builds/
) else (
    echo  [OK] FFmpeg disponivel
)

echo.
echo [2/9] Criando diretorio de instalacao...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
echo  [OK] %INSTALL_DIR%

echo.
echo [3/9] Clonando repositorio DARK STUDIO AAA...
if exist "%INSTALL_DIR%\.git" (
    echo  Repositorio ja existe. Atualizando...
    cd /d "%INSTALL_DIR%"
    git pull origin main
    echo  [OK] Atualizado
) else (
    git clone "%REPO_URL%" "%INSTALL_DIR%"
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao clonar! Verifique a internet.
        pause
        exit /b 1
    )
    echo  [OK] Repositorio clonado
)

echo.
echo [4/9] Criando ambiente virtual Python...
cd /d "%INSTALL_DIR%"
python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao criar venv!
    pause
    exit /b 1
)
echo  [OK] Ambiente virtual criado

echo.
echo [5/9] Instalando dependencias Python...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo  [AVISO] Algumas deps opcionais falharam. Instalando essenciais...
    pip install pillow moviepy requests tqdm psutil fastapi uvicorn -q
)
echo  [OK] Dependencias instaladas

echo.
echo [6/9] Configurando Piper TTS...
set "PIPER_DIR=%INSTALL_DIR%\tools\piper"
set "MODEL_DIR=%INSTALL_DIR%\models\piper"
if not exist "%PIPER_DIR%" mkdir "%PIPER_DIR%"
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

if not exist "%PIPER_DIR%\piper.exe" (
    echo  Baixando Piper TTS para Windows...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_windows_amd64.zip' -OutFile '%PIPER_DIR%\piper.zip' -UseBasicParsing" 2>nul
    if exist "%PIPER_DIR%\piper.zip" (
        powershell -Command "Expand-Archive -Path '%PIPER_DIR%\piper.zip' -DestinationPath '%PIPER_DIR%' -Force" 2>nul
        del "%PIPER_DIR%\piper.zip" 2>nul
        echo  [OK] Piper TTS instalado
    ) else (
        echo  [AVISO] Piper nao baixado. TTS usara gTTS como fallback.
    )
) else (
    echo  [OK] Piper TTS ja instalado
)

if not exist "%MODEL_DIR%\pt_BR-faber-medium.onnx" (
    echo  Baixando modelo de voz pt-BR...
    powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx' -OutFile '%MODEL_DIR%\pt_BR-faber-medium.onnx' -UseBasicParsing" 2>nul
    powershell -Command "Invoke-WebRequest -Uri 'https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json' -OutFile '%MODEL_DIR%\pt_BR-faber-medium.onnx.json' -UseBasicParsing" 2>nul
    if exist "%MODEL_DIR%\pt_BR-faber-medium.onnx" (
        echo  [OK] Modelo pt-BR instalado
    ) else (
        echo  [AVISO] Modelo nao baixado. Configure manualmente.
    )
) else (
    echo  [OK] Modelo pt-BR ja presente
)

echo.
echo [7/9] Criando configuracao...
if not exist "%INSTALL_DIR%\.env" (
    (
        echo # DARK STUDIO AAA — Configuracoes
        echo # ai_generated: True
        echo # ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
        echo.
        echo DARK_PROJETOS_DIR=%INSTALL_DIR%\projetos
        echo PIPER_BIN=%PIPER_DIR%\piper.exe
        echo PIPER_MODEL=%MODEL_DIR%\pt_BR-faber-medium.onnx
        echo.
        echo # APIs opcionais (deixe vazio para usar apenas backends gratuitos)
        echo OPENAI_API_KEY=
        echo ELEVENLABS_API_KEY=
        echo REPLICATE_API_TOKEN=
        echo.
        echo DARK_DEFAULT_RESOLUCAO=1920x1080
        echo DARK_DEFAULT_PRESET=documentario
    ) > "%INSTALL_DIR%\.env"
    echo  [OK] .env criado
) else (
    echo  [OK] .env ja existe
)

if not exist "%INSTALL_DIR%\projetos" mkdir "%INSTALL_DIR%\projetos"
echo  [OK] Diretorio de projetos pronto

echo.
echo [8/9] Criando launcher e atalho...
(
    echo @echo off
    echo title DARK STUDIO AAA
    echo cd /d "%INSTALL_DIR%"
    echo call "%VENV_DIR%\Scripts\activate.bat"
    echo echo Iniciando DARK STUDIO AAA...
    echo echo Acesse: http://localhost:8765
    echo python -m uvicorn api.main:app --host 0.0.0.0 --port 8765 --reload
    echo pause
) > "%INSTALL_DIR%\dark_studio_aaa.bat"
echo  [OK] dark_studio_aaa.bat criado

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\DARK STUDIO AAA.lnk'); $s.TargetPath = '%INSTALL_DIR%\dark_studio_aaa.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'DARK STUDIO AAA - Plataforma de Criacao Audiovisual com IA'; $s.Save()" 2>nul
if exist "%DESKTOP%\DARK STUDIO AAA.lnk" (
    echo  [OK] Atalho criado na Area de Trabalho
) else (
    echo  [AVISO] Atalho nao criado. Use dark_studio_aaa.bat diretamente.
)

echo.
echo [9/9] Validando instalacao...
cd /d "%INSTALL_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"
python -c "
import sys
sys.path.insert(0, '.')
erros = []
avisos = []

try:
    import PIL
    print('  [OK] Pillow (imagens)')
except Exception as e:
    erros.append('Pillow')

try:
    import fastapi
    print('  [OK] FastAPI (servidor API)')
except:
    erros.append('fastapi')

try:
    import requests
    print('  [OK] Requests (HTTP)')
except:
    avisos.append('requests')

try:
    from core import dark_manager
    r = dark_manager.check_all_agents()
    n = sum(1 for v in r.values() if v)
    print(f'  [OK] DARK MANAGER: {n}/{len(r)} agentes OK')
except Exception as e:
    erros.append(f'dark_manager: {e}')

if erros:
    print(f'  [FALHA] Erros criticos: {erros}')
    sys.exit(1)
elif avisos:
    print(f'  [OK] Instalacao OK com avisos: {avisos}')
else:
    print('  [OK] Instalacao completa e validada!')
    print('  ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB')
"

echo.
echo ════════════════════════════════════════════════════
echo.
echo  INSTALACAO CONCLUIDA COM SUCESSO!
echo.
echo  Como iniciar o DARK STUDIO AAA:
echo.
echo   1. Atalho "DARK STUDIO AAA" na Area de Trabalho
echo   2. Execute: %INSTALL_DIR%\dark_studio_aaa.bat
echo.
echo  Acesse: http://localhost:8765
echo.
echo  Para APIs opcionais, edite:
echo  %INSTALL_DIR%\.env
echo.
echo  ai_disclosure: Produzido com DARK STUDIO AAA
echo ════════════════════════════════════════════════════
echo.
pause
