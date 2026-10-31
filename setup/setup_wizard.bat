@echo off
:: DARK STICKMAN STUDIO — Setup Wizard para Windows
:: Instala todas as dependências automaticamente.
:: ai_generated: True
:: ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

title DARK STICKMAN STUDIO — Setup Wizard
color 0B
echo.
echo  ██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗████████╗██╗ ██████╗██╗  ██╗███╗   ███╗ █████╗ ███╗   ██╗
echo  ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝╚══██╔══╝██║██╔════╝██║ ██╔╝████╗ ████║██╔══██╗████╗  ██║
echo  ██║  ██║███████║██████╔╝█████╔╝     ███████╗   ██║   ██║██║     █████╔╝ ██╔████╔██║███████║██╔██╗ ██║
echo  ██║  ██║██╔══██║██╔══██╗██╔═██╗     ╚════██║   ██║   ██║██║     ██╔═██╗ ██║╚██╔╝██║██╔══██║██║╚██╗██║
echo  ██████╔╝██║  ██║██║  ██║██║  ██╗    ███████║   ██║   ██║╚██████╗██║  ██╗██║ ╚═╝ ██║██║  ██║██║ ╚████║
echo  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚══════╝   ╚═╝   ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
echo.
echo  Produzido com IA — DARK STUDIO AAA — DARK CREATIVE LAB
echo  ================================================================
echo.

:: ── Verificar Python ──────────────────────────────────────────────────────────
echo [1/8] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERRO] Python nao encontrado. Baixe em https://python.org e instale.
    echo         Marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)
python --version
echo  [OK] Python encontrado.
echo.

:: ── Verificar pip ─────────────────────────────────────────────────────────────
echo [2/8] Atualizando pip...
python -m pip install --upgrade pip --quiet
echo  [OK] pip atualizado.
echo.

:: ── Instalar dependencias Python ──────────────────────────────────────────────
echo [3/8] Instalando dependencias Python...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  [AVISO] Algumas dependencias podem ter falhado. Verifique acima.
) else (
    echo  [OK] Dependencias instaladas.
)
echo.

:: ── Verificar FFmpeg ──────────────────────────────────────────────────────────
echo [4/8] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo  [AVISO] FFmpeg nao encontrado.
    echo         Opcoes de instalacao:
    echo           1. winget install FFmpeg
    echo           2. choco install ffmpeg  (requer Chocolatey)
    echo           3. Download manual: https://ffmpeg.org/download.html
    echo.
    echo  Pressione qualquer tecla para tentar instalar via winget...
    pause
    winget install FFmpeg --accept-source-agreements --accept-package-agreements
    ffmpeg -version >nul 2>&1
    if errorlevel 1 (
        echo  [ERRO] FFmpeg ainda nao encontrado. Instale manualmente e adicione ao PATH.
    ) else (
        echo  [OK] FFmpeg instalado via winget.
    )
) else (
    echo  [OK] FFmpeg encontrado.
)
echo.

:: ── Manim CE ─────────────────────────────────────────────────────────────────
echo [5/8] Instalando Manim CE...
pip install manim --quiet
if errorlevel 1 (
    echo  [AVISO] Manim pode ter falhado. Tente manualmente: pip install manim
    echo         Dependencias extras: pip install manim[jupyterlab,webgl_renderer]
) else (
    echo  [OK] Manim CE instalado.
)
echo.

:: ── Piper TTS ─────────────────────────────────────────────────────────────────
echo [6/8] Instalando Piper TTS...
pip install piper-tts --quiet
if errorlevel 1 (
    echo  [AVISO] piper-tts nao instalado via pip.
    echo         Alternativa: baixe o binario em https://github.com/rhasspy/piper/releases
    echo         e adicione ao PATH ou defina PIPER_PATH no .env
) else (
    echo  [OK] Piper TTS instalado.
)
echo.

:: ── Whisper ───────────────────────────────────────────────────────────────────
echo [7/8] Instalando OpenAI Whisper...
pip install openai-whisper --quiet
if errorlevel 1 (
    echo  [AVISO] Whisper pode ter falhado. Tente: pip install openai-whisper
) else (
    echo  [OK] Whisper instalado.
)
echo.

:: ── Criar diretorios ─────────────────────────────────────────────────────────
echo [8/8] Criando estrutura de diretorios...
if not exist "output" mkdir output
if not exist "output\thumbnails" mkdir output\thumbnails
if not exist "db" mkdir db
if not exist "logs" mkdir logs
echo  [OK] Diretorios criados.
echo.

:: ── Verificacao final ─────────────────────────────────────────────────────────
echo  ================================================================
echo  VERIFICACAO FINAL
echo  ================================================================
echo.
python -c "import fastapi; print('FastAPI: OK')" 2>nul || echo "FastAPI: FALHOU"
python -c "import typer; print('Typer CLI: OK')" 2>nul || echo "Typer: FALHOU"
python -c "from PIL import Image; print('Pillow: OK')" 2>nul || echo "Pillow: FALHOU"
python -c "import whisper; print('Whisper: OK')" 2>nul || echo "Whisper: FALHOU"
python -c "import manim; print('Manim CE: OK')" 2>nul || echo "Manim: FALHOU"
ffmpeg -version >nul 2>&1 && echo "FFmpeg: OK" || echo "FFmpeg: NAO ENCONTRADO"
echo.

:: ── Registrar CLI ─────────────────────────────────────────────────────────────
echo  Registrando comando 'dark-stickman' no PATH...
pip install -e . --quiet 2>nul || echo  [INFO] Instale manualmente: pip install -e .
echo.

:: ── Conclusao ─────────────────────────────────────────────────────────────────
echo  ================================================================
echo  SETUP CONCLUIDO!
echo  ================================================================
echo.
echo  Como usar:
echo    dark-stickman status            -- verifica dependencias
echo    dark-stickman canais            -- lista os 12 canais
echo    dark-stickman produzir --canal psicologia --titulo "SEU TITULO"
echo    dark-stickman api               -- inicia API na porta 7870
echo.
echo  Documentacao: README.md
echo  Issues: https://github.com/Jeffersonjazz/dark-stickman-studio/issues
echo.
echo  Produzido com IA — DARK STUDIO AAA — DARK CREATIVE LAB
echo.
pause
