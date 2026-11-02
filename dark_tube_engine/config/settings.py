"""
DARK TUBE ENGINE — Configurações e API Keys
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env se existir
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".env")

# ── Diretórios ──────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
SCRIPTS_DIR = OUTPUTS_DIR / "scripts"
AUDIO_DIR = OUTPUTS_DIR / "audio"
VIDEO_DIR = OUTPUTS_DIR / "video"
THUMBNAILS_DIR = OUTPUTS_DIR / "thumbnails"
JOBS_DIR = BASE_DIR / "jobs"
CONFIG_DIR = BASE_DIR / "config"

# Cria diretórios
for d in [SCRIPTS_DIR, AUDIO_DIR, VIDEO_DIR, THUMBNAILS_DIR, JOBS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── YouTube API ──────────────────────────────────────────
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # Para pesquisa (não upload)
YOUTUBE_CLIENT_SECRETS = str(CONFIG_DIR / "client_secrets.json")
YOUTUBE_TOKEN = str(CONFIG_DIR / "token.pickle")

# ── TTS ──────────────────────────────────────────────────
TTS_BACKEND = os.getenv("TTS_BACKEND", "edge-tts")  # "edge-tts" | "gtts"
DEFAULT_VOICE_PT = os.getenv("DEFAULT_VOICE_PT", "pt-BR-AntonioNeural")

# ── Servidor ──────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "7860"))
API_DEBUG = os.getenv("API_DEBUG", "false").lower() == "true"

# ── Metadados padrão ──────────────────────────────────────
AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
AI_GENERATED = True

# ── Canais configurados ────────────────────────────────────
CANAIS = {
    "Mente de Aço":       {"nicho": "motivacional", "categoria_yt": "22"},
    "Esquina do Medo":    {"nicho": "terror",        "categoria_yt": "24"},
    "Intelligentia Nova": {"nicho": "tech_ia",       "categoria_yt": "28"},
    "Projeto Secreto":    {"nicho": "conspiracao",   "categoria_yt": "25"},
    "AquaZen Relax":      {"nicho": "relaxamento",   "categoria_yt": "19"},
    "Dark Nature":        {"nicho": "documentario",  "categoria_yt": "19"},
    "Historia Sombria":   {"nicho": "documentario",  "categoria_yt": "25"},
}

# ── Resoluções suportadas ─────────────────────────────────
RESOLUCOES = {
    "shorts":     "1080x1920",
    "horizontal": "1920x1080",
    "square":     "1080x1080",
}

print(f"[DARK TUBE ENGINE] Config carregada — TTS: {TTS_BACKEND} | Port: {API_PORT}")
