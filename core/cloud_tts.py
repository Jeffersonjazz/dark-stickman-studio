"""
DARK STUDIO — CLOUD TTS ENGINE
Síntese de voz PT-BR via serviços gratuitos de nuvem.

Cascata de backends GRATUITOS:
  1. Kokoro TTS local (82M params, sem GPU, rápido)
  2. HF Inference API — facebook/mms-tts-por (gratuito com token HF)
  3. HF Inference API — microsoft/speecht5_tts (gratuito)
  4. HF Spaces — gradio_client (Kokoro Space público)
  5. Delegação para piper_tts (silêncio como último fallback)

Uso no seu PC/Colab:
  pip install kokoro soundfile gradio_client

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import io
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────

# Token Hugging Face (gratuito em hf.co/settings/tokens)
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Voz PT-BR padrão para Kokoro
KOKORO_VOICE_PTBR = "bf_emma"   # feminino suave (disponível no Kokoro)
KOKORO_VOICE_MALE = "bm_lewis"  # masculino

# HF Inference API — modelos gratuitos PT-BR
HF_TTS_MODELS = [
    "facebook/mms-tts-por",      # MMS multilingual — suporte nativo PT
    "microsoft/speecht5_tts",    # SpeechT5 — qualidade boa, precisa embeddings
]

# Kokoro HF Space público (sem token)
KOKORO_SPACE = "hexgrad/Kokoro-TTS"


# ─────────────────────────────────────────────────────────
# ENGINE 1: KOKORO LOCAL
# ─────────────────────────────────────────────────────────

def _tts_kokoro_local(
    text: str,
    output_path: Path,
    voice: str = KOKORO_VOICE_PTBR,
    speed: float = 1.0,
) -> bool:
    """Kokoro TTS local — 82M params, sem GPU, ~150ms/frase."""
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np

        # pt-BR: lang_code 'p' (Portuguese)
        pipeline = KPipeline(lang_code="p")

        samples = []
        generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
        for _, _, audio in generator:
            samples.append(audio)

        if not samples:
            return False

        audio_np = np.concatenate(samples) if len(samples) > 1 else samples[0]
        sf.write(str(output_path), audio_np, 24000)
        return output_path.exists() and output_path.stat().st_size > 100

    except ImportError:
        return False
    except Exception as e:
        print(f"[CLOUD TTS] Kokoro local falhou: {e}")
        return False


# ─────────────────────────────────────────────────────────
# ENGINE 2: HF INFERENCE API — MMS-TTS-POR
# ─────────────────────────────────────────────────────────

def _tts_hf_mms(text: str, output_path: Path) -> bool:
    """
    HF Inference API — facebook/mms-tts-por
    Gratuito com token HF (até ~30k requests/mês no free tier).
    Cria conta grátis em huggingface.co e gera token em hf.co/settings/tokens
    """
    try:
        import requests

        token = HF_TOKEN
        if not token:
            return False

        url = "https://api-inference.huggingface.co/models/facebook/mms-tts-por"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": text}

        resp = requests.post(url, headers=headers, json=payload, timeout=30)

        if resp.status_code == 200:
            output_path.write_bytes(resp.content)
            return output_path.stat().st_size > 100
        elif resp.status_code == 503:
            # Modelo carregando — aguarda e tenta novamente
            time.sleep(20)
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                output_path.write_bytes(resp.content)
                return output_path.stat().st_size > 100

        print(f"[CLOUD TTS] HF MMS falhou: {resp.status_code} {resp.text[:100]}")
        return False

    except Exception as e:
        print(f"[CLOUD TTS] HF MMS erro: {e}")
        return False


# ─────────────────────────────────────────────────────────
# ENGINE 3: HF INFERENCE API — SPEECHT5
# ─────────────────────────────────────────────────────────

def _tts_hf_speecht5(text: str, output_path: Path) -> bool:
    """
    HF Inference API — microsoft/speecht5_tts
    Qualidade boa, inglês nativo mas aceita PT-BR.
    """
    try:
        import requests

        token = HF_TOKEN
        if not token:
            return False

        url = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": text}

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            output_path.write_bytes(resp.content)
            return output_path.stat().st_size > 100

        return False

    except Exception as e:
        print(f"[CLOUD TTS] SpeechT5 erro: {e}")
        return False


# ─────────────────────────────────────────────────────────
# ENGINE 4: KOKORO HF SPACE (via Gradio Client)
# ─────────────────────────────────────────────────────────

def _tts_kokoro_space(
    text: str,
    output_path: Path,
    voice: str = "af_heart",
    speed: float = 1.0,
) -> bool:
    """
    Kokoro TTS via HF Space público — gratuito, sem token.
    Requer: pip install gradio_client
    Latência: ~3-8s por requisição.
    """
    try:
        from gradio_client import Client

        client = Client(KOKORO_SPACE)
        result = client.predict(
            text=text,
            voice=voice,
            speed=speed,
            api_name="/generate_speech",
        )

        # result é o caminho do arquivo gerado no Space
        if result and Path(result).exists():
            import shutil
            shutil.copy2(result, output_path)
            return output_path.exists() and output_path.stat().st_size > 100

        return False

    except ImportError:
        return False
    except Exception as e:
        print(f"[CLOUD TTS] Kokoro Space falhou: {e}")
        return False


# ─────────────────────────────────────────────────────────
# ENGINE 5: ELEVENLABS FREE TIER (API KEY obrigatória)
# ─────────────────────────────────────────────────────────

def _tts_elevenlabs(
    text: str,
    output_path: Path,
    voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel (free)
) -> bool:
    """
    ElevenLabs Free Tier — 10.000 chars/mês gratuitos.
    Cria conta em elevenlabs.io e defina ELEVENLABS_API_KEY.
    Qualidade: ⭐⭐⭐⭐⭐ (melhor voz do mercado)
    """
    try:
        import requests

        api_key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not api_key:
            return False

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.6,
                "similarity_boost": 0.8,
                "style": 0.2,
                "use_speaker_boost": True,
            },
        }

        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if resp.status_code == 200:
            output_path.write_bytes(resp.content)
            return output_path.stat().st_size > 100

        print(f"[CLOUD TTS] ElevenLabs falhou: {resp.status_code} {resp.text[:100]}")
        return False

    except Exception as e:
        print(f"[CLOUD TTS] ElevenLabs erro: {e}")
        return False


# ─────────────────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────────────────

BACKEND_PRIORITY = [
    ("kokoro_local",    _tts_kokoro_local,   "🆓 Local, sem GPU, 82M params"),
    ("hf_mms_por",      _tts_hf_mms,         "🆓 HF Inference API (token gratuito)"),
    ("elevenlabs",      _tts_elevenlabs,     "🆓 10k chars/mês gratuitos"),
    ("kokoro_space",    _tts_kokoro_space,   "🆓 HF Space público (sem token)"),
    ("hf_speecht5",     _tts_hf_speecht5,    "🆓 HF Inference API (token gratuito)"),
]


def synthesize_cloud(
    text: str,
    output_path: Path,
    backend: Optional[str] = None,
    verbose: bool = True,
) -> dict:
    """
    Sintetiza voz PT-BR via serviços gratuitos de nuvem.

    Args:
        text:        Texto em português a narrar.
        output_path: Caminho do arquivo de saída (.wav ou .mp3).
        backend:     Forçar backend específico (None = cascata automática).
        verbose:     Exibe progresso.

    Returns:
        dict com status, backend_used, output_path, cost_usd.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not text.strip():
        # Texto vazio — gera silêncio curto
        _gerar_silencio(output_path, 0.5)
        return {"status": "ok", "backend_used": "silence", "output_path": str(output_path), "cost_usd": 0.0}

    backends_tentar = (
        [(b, fn, d) for b, fn, d in BACKEND_PRIORITY if b == backend]
        if backend
        else BACKEND_PRIORITY
    )

    for name, fn, desc in backends_tentar:
        if verbose:
            print(f"[CLOUD TTS] Tentando {name} ({desc})...")
        try:
            ok = fn(text, output_path)
            if ok:
                if verbose:
                    print(f"[CLOUD TTS] ✅ {name} → {output_path.name}")
                return {
                    "status": "ok",
                    "backend_used": name,
                    "output_path": str(output_path),
                    "cost_usd": 0.0,
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
                }
        except Exception as e:
            if verbose:
                print(f"[CLOUD TTS] {name} erro: {e}")

    # Último fallback: silêncio
    _gerar_silencio(output_path, _estimar_duracao(text))
    return {
        "status": "fallback_silence",
        "backend_used": "silence",
        "output_path": str(output_path),
        "cost_usd": 0.0,
        "note": "Nenhum engine TTS disponível. Defina HF_TOKEN ou instale kokoro.",
    }


def check_cloud_tts() -> dict:
    """Diagnóstico dos engines disponíveis."""
    import importlib

    status = {}

    # Kokoro local
    try:
        importlib.import_module("kokoro")
        status["kokoro_local"] = {"available": True, "note": "✅ Instalado", "cost": "Gratuito"}
    except ImportError:
        status["kokoro_local"] = {"available": False, "note": "pip install kokoro soundfile", "cost": "Gratuito"}

    # HF Inference API
    has_hf = bool(HF_TOKEN)
    status["hf_inference_api"] = {
        "available": has_hf,
        "note": "✅ Token presente" if has_hf else "Defina HF_TOKEN (grátis em hf.co/settings/tokens)",
        "cost": "Gratuito (30k req/mês)",
    }

    # ElevenLabs
    has_el = bool(os.environ.get("ELEVENLABS_API_KEY", ""))
    status["elevenlabs"] = {
        "available": has_el,
        "note": "✅ API Key presente" if has_el else "Defina ELEVENLABS_API_KEY (10k chars/mês grátis)",
        "cost": "10k chars/mês gratuitos",
    }

    # Gradio client (Kokoro Space)
    try:
        importlib.import_module("gradio_client")
        status["kokoro_space"] = {"available": True, "note": "✅ gradio_client instalado", "cost": "Gratuito"}
    except ImportError:
        status["kokoro_space"] = {"available": False, "note": "pip install gradio_client", "cost": "Gratuito"}

    return status


def _gerar_silencio(output_path: Path, duracao: float = 3.0):
    """Gera arquivo WAV de silêncio."""
    import subprocess, shutil
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    subprocess.run([
        ffmpeg, "-y", "-f", "lavfi",
        "-i", f"anullsrc=r=22050:cl=mono",
        "-t", str(duracao),
        "-acodec", "pcm_s16le",
        str(output_path),
    ], capture_output=True)


def _estimar_duracao(text: str) -> float:
    """Estima duração do áudio baseado na velocidade de fala (150 palavras/min)."""
    palavras = len(text.split())
    return max(1.0, palavras / 2.5)


# ─────────────────────────────────────────────────────────
# CLI / SETUP GUIDE
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== DARK STUDIO — CLOUD TTS ENGINE ===\n")
    print("📋 SERVIÇOS GRATUITOS DE VOZ:\n")

    SERVICOS = [
        {
            "nome": "Kokoro TTS Local",
            "qualidade": "⭐⭐⭐⭐",
            "custo": "GRATUITO — sem internet",
            "setup": "pip install kokoro soundfile",
            "velocidade": "~150ms/frase (CPU)",
            "ptbr": "Sim (lang_code='p')",
        },
        {
            "nome": "HF Inference API — facebook/mms-tts-por",
            "qualidade": "⭐⭐⭐",
            "custo": "GRATUITO — 30k req/mês",
            "setup": "1) Conta em huggingface.co\n      2) Token em hf.co/settings/tokens\n      3) export HF_TOKEN=hf_xxx",
            "velocidade": "~2-5s/frase",
            "ptbr": "Sim — modelo treinado em PT",
        },
        {
            "nome": "ElevenLabs Free Tier",
            "qualidade": "⭐⭐⭐⭐⭐",
            "custo": "GRATUITO — 10k chars/mês",
            "setup": "1) Conta em elevenlabs.io\n      2) export ELEVENLABS_API_KEY=sk_xxx",
            "velocidade": "~1-3s/frase",
            "ptbr": "Sim — eleven_multilingual_v2",
        },
        {
            "nome": "Kokoro HF Space",
            "qualidade": "⭐⭐⭐⭐",
            "custo": "GRATUITO — sem token",
            "setup": "pip install gradio_client",
            "velocidade": "~3-8s/frase",
            "ptbr": "Sim (lang_code='p')",
        },
    ]

    for s in SERVICOS:
        print(f"  {'─'*50}")
        print(f"  🎙️  {s['nome']}")
        print(f"  💰 Custo: {s['custo']}")
        print(f"  ⭐ Qualidade: {s['qualidade']}")
        print(f"  ⚡ Velocidade: {s['velocidade']}")
        print(f"  🇧🇷 PT-BR: {s['ptbr']}")
        print(f"  📦 Setup: {s['setup']}")
    print()

    status = check_cloud_tts()
    print("Status atual:")
    for name, info in status.items():
        icon = "✅" if info["available"] else "❌"
        print(f"  {icon} {name}: {info['note']}")

    print("\n💡 RECOMENDAÇÃO PARA DARK STUDIO:")
    print("  1️⃣  Instale kokoro (gratuito, sem internet): pip install kokoro soundfile")
    print("  2️⃣  Crie conta HF e defina HF_TOKEN (30k req/mês grátis)")
    print("  3️⃣  Opcional: ElevenLabs para voz premium (10k chars/mês grátis)")
