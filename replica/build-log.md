# DARK STICKMAN STUDIO — Build Log
**Versão:** 1.0.0 | **Data:** 2026-10-31 | ai_generated: true

## Construído

### Core
- `core/stickman_svg.py` — SVG stickman 20 poses, seeds por canal ✅
- `core/ffmpeg_utils.py` — edição, watermark, color grade (8 presets) ✅
- `core/piper_tts.py` — narração PT-BR offline ✅
- `core/manim_scene.py` — animação Manim CE ✅
- `core/legenda.py` — WhisperX → Whisper → fallback texto ✅
- `core/thumbnail.py` — 1280x720 Pillow, 12 paletas ✅

### Pipeline / API / CLI
- `pipeline/f01_producao.py` — 15 etapas, SQLite, watermark obrigatório ✅
- `api/main.py` — FastAPI porta 7870, 12 endpoints ✅
- `api/models.py` — Pydantic, ai_generated/ai_disclosure em todos os outputs ✅
- `cli/dark_stickman.py` — Typer + Rich, 6 comandos ✅

### Config / Infra
- 12 configs de canal JSON (seeds 1001–1012) ✅
- 9 presets cinematográficos JSON ✅
- `db/schema.sql`, `requirements.txt`, `setup.py` ✅
- `setup/setup_wizard.bat` (Windows 8 passos) ✅
- `README.md` completo ✅

## Git
- Commit: f1e9994 — 33 arquivos
- **GitHub push PENDENTE** — criar repo em https://github.com/new (dark-stickman-studio)
- ZIP disponível: dark-stickman-studio-v1.0.0.zip

## Desvios do recon
- Coqui TTS → Piper TTS (Coqui descontinuado)
- MoviePy → FFmpeg direto (mais estável)
- PostgreSQL → SQLite (deploy Windows local)
- Geração de vídeo real → Manim CE (APIs pagas fora do escopo gratuito)

## Pulado / Pendente
- Diagnóstico de hardware (FASE 1 do spec 13.8)
- Download do modelo Piper pt_BR-faber-medium
- Integração real com DARK MANAGER /manager/dispatch
- Testes de produção com vídeo real
