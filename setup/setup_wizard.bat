@echo off
:: ============================================================
:: DARK STICKMAN STUDIO — SETUP WIZARD v1.0
:: DARK CREATIVE LAB — Instalador Automatico para Windows
:: ai_generated: True
:: ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
:: Custo: R$0,00/mes — 100% open source
:: ============================================================
title DARK STICKMAN STUDIO — Instalador
color 0A

echo.
echo  ####################################################
echo  ##  DARK STICKMAN STUDIO - DARK CREATIVE LAB      ##
echo  ##  Instalador Automatico v1.0                    ##
echo  ##  Custo: R$0,00/mes                             ##
echo  ####################################################
echo.

:: 1. Verificar Python 3.10+
echo [1/8] Verificando Python 3.10+...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    echo Marque "Add Python to PATH" durante a instalacao.
    pause & exit /b 1
)
python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Python 3.10+ recomendado.
    choice /c SN /m "Continuar mesmo assim?"
    if errorlevel 2 exit /b 1
)
echo [OK] Python encontrado.

:: 2. Criar ambiente virtual
echo.
echo [2/8] Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [OK] Ambiente virtual pronto.

:: 3. Atualizar pip
echo.
echo [3/8] Atualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip atualizado.

:: 4. Instalar dependencias Python
echo.
echo [4/8] Instalando dependencias Python (aguarde)...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [AVISO] Instalando pacotes essenciais individualmente...
    pip install fastapi uvicorn pydantic typer rich Pillow requests edge-tts openai-whisper --quiet
)
echo [OK] Dependencias instaladas.

:: 5. Verificar/instalar FFmpeg
echo.
echo [5/8] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo FFmpeg nao encontrado. Instalando via winget...
    winget install --id Gyan.FFmpeg -e --silent >nul 2>&1
    ffmpeg -version >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] FFmpeg nao instalado. Instale manualmente:
        echo   winget install Gyan.FFmpeg
        echo   OU baixe em: https://ffmpeg.org/download.html
        echo   (Adicione FFmpeg ao PATH do sistema)
    ) else (
        echo [OK] FFmpeg instalado.
    )
) else (
    echo [OK] FFmpeg disponivel.
)

:: 6. Criar estrutura de pastas
echo.
echo [6/8] Criando estrutura de pastas...
set BASE=%USERPROFILE%\DarkStudioAAA
for %%d in (projetos assets\imagens assets\videos assets\audio assets\fontes exports logs modelos temp) do (
    mkdir "%BASE%\%%d" >nul 2>&1
)
echo [OK] Pastas em: %BASE%

:: Salvar configuracao local
(
echo {
echo   "base_dir": "%BASE:\=\\%",
echo   "version": "1.0.0",
echo   "custo_brl": 0.0,
echo   "ai_generated": true,
echo   "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
echo }
) > "%BASE%\config_local.json"

:: 7. Modelo Piper TTS pt-BR (opcional)
echo.
echo [7/8] Modelo TTS local (opcional)...
choice /c SN /m "Baixar Piper TTS pt-BR offline (~67MB)?"
if not errorlevel 2 (
    mkdir "%BASE%\modelos\piper" >nul 2>&1
    set PIPER_BASE=https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium
    curl -L -o "%BASE%\modelos\piper\pt_BR-faber-medium.onnx" "%PIPER_BASE%/pt_BR-faber-medium.onnx"
    curl -L -o "%BASE%\modelos\piper\pt_BR-faber-medium.onnx.json" "%PIPER_BASE%/pt_BR-faber-medium.onnx.json"
    if exist "%BASE%\modelos\piper\pt_BR-faber-medium.onnx" (
        echo [OK] Piper TTS pt-BR baixado.
    ) else (
        echo [AVISO] Baixe manualmente em: https://huggingface.co/rhasspy/piper-voices
    )
) else (
    echo [INFO] Usando edge-tts online (requer internet durante uso).
)

:: 8. Criar launcher e atalho
echo.
echo [8/8] Criando launcher...
(
echo @echo off
echo title DARK STICKMAN STUDIO
echo cd /d "%%~dp0"
echo call venv\Scripts\activate.bat
echo echo Iniciando DARK STICKMAN STUDIO...
echo echo Acesse: http://localhost:8000/panel
echo start "" "http://localhost:8000/panel"
echo python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
echo pause
) > launcher.bat

:: Atalho na area de trabalho
set VBS=%TEMP%\shortcut_dark.vbs
(
echo Set ws = WScript.CreateObject("WScript.Shell"^)
echo Set sc = ws.CreateShortcut(ws.SpecialFolders("Desktop"^) ^& "\DARK STUDIO AAA.lnk"^)
echo sc.TargetPath = "%~dp0launcher.bat"
echo sc.WorkingDirectory = "%~dp0"
echo sc.Description = "DARK STICKMAN STUDIO — DARK CREATIVE LAB"
echo sc.Save
) > "%VBS%"
cscript //nologo "%VBS%" >nul 2>&1
del "%VBS%" >nul 2>&1
echo [OK] Atalho "DARK STUDIO AAA" criado na area de trabalho.

:: Conclusao
echo.
echo  ####################################################
echo  ##   INSTALACAO CONCLUIDA!                        ##
echo  ##                                                ##
echo  ##   Para iniciar: execute launcher.bat           ##
echo  ##   Ou clique no atalho: DARK STUDIO AAA         ##
echo  ##   URL: http://localhost:8000/panel             ##
echo  ##                                                ##
echo  ##   Custo mensal: R$0,00                         ##
echo  ####################################################
echo.
pause
