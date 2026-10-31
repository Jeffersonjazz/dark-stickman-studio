"""
DARK STICKMAN STUDIO — Narração PT-BR Multi-Engine TTS
Prioridade: Piper (local) → edge-tts (Microsoft online) → gTTS (Google online) → silêncio

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import os
import shutil
import subprocess
import json
import asyncio
from pathlib import Path
from typing import Optional

PIPER_BIN = shutil.which("piper") or os.environ.get("PIPER_PATH", "piper")

PT_BR_MODELS = {
    "faber-medium":   "pt_BR-faber-medium.onnx",
    "faber-low":      "pt_BR-faber-low.onnx",
    "edresson-low":   "pt_BR-edresson_low.onnx",
}

DEFAULT_MODEL  = "faber-medium"
MODELS_DIR     = Path(__file__).parent.parent / "assets" / "models" / "piper"

# Voz edge-tts PT-BR mais natural disponível
EDGE_TTS_VOICE = "pt-BR-FranciscaNeural"  # voz feminina natural PT-BR
EDGE_TTS_VOICE_MALE = "pt-BR-AntonioNeural"  # voz masculina


def _model_path(model_name: str) -> Optional[Path]:
    filename = PT_BR_MODELS.get(model_name, model_name)
    candidate = MODELS_DIR / filename
    if candidate.exists():
        return candidate
    direct = Path(model_name)
    if direct.exists():
        return direct
    return None


# ─────────────────────────────────────────────
# ENGINE 1: PIPER (local, offline, alta qualidade)
# ─────────────────────────────────────────────

def _synthesize_piper(text: str, output_path: Path, length_scale: float = 1.0) -> bool:
    """Tenta sintetizar com Piper TTS. Retorna True se ok."""
    model_path = _model_path(DEFAULT_MODEL)
    if model_path is None:
        return False

    config_path = model_path.with_suffix(".onnx.json")
    cmd = [
        PIPER_BIN,
        "--model", str(model_path),
        "--output_file", str(output_path),
        "--length_scale", str(length_scale),
    ]
    if config_path.exists():
        cmd += ["--config", str(config_path)]

    result = subprocess.run(cmd, input=text, capture_output=True, text=True, check=False)
    return result.returncode == 0 and output_path.exists()


# ─────────────────────────────────────────────
# ENGINE 2: EDGE-TTS (Microsoft, online, voz natural)
# ─────────────────────────────────────────────

def _synthesize_edge_tts(text: str, output_path: Path, voice: str = EDGE_TTS_VOICE) -> bool:
    """Sintetiza com edge-tts (Microsoft Neural PT-BR). Retorna True se ok."""
    try:
        import edge_tts

        mp3_tmp = output_path.with_suffix(".mp3")

        async def _run():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(mp3_tmp))

        asyncio.run(_run())

        if not mp3_tmp.exists() or mp3_tmp.stat().st_size < 100:
            return False

        # Converte MP3 → WAV para compatibilidade com pipeline
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        r = subprocess.run(
            [ffmpeg, "-y", "-i", str(mp3_tmp), str(output_path)],
            capture_output=True, check=False
        )
        mp3_tmp.unlink(missing_ok=True)
        return r.returncode == 0 and output_path.exists()

    except Exception as e:
        print(f"[TTS] edge-tts falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 3: gTTS (Google, online, fallback)
# ─────────────────────────────────────────────

def _synthesize_gtts(text: str, output_path: Path) -> bool:
    """Sintetiza com gTTS (Google Text-to-Speech). Retorna True se ok."""
    try:
        from gtts import gTTS

        mp3_tmp = output_path.with_suffix(".mp3")
        tts = gTTS(text=text, lang="pt", tld="com.br", slow=False)
        tts.save(str(mp3_tmp))

        if not mp3_tmp.exists() or mp3_tmp.stat().st_size < 100:
            return False

        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        r = subprocess.run(
            [ffmpeg, "-y", "-i", str(mp3_tmp), str(output_path)],
            capture_output=True, check=False
        )
        mp3_tmp.unlink(missing_ok=True)
        return r.returncode == 0 and output_path.exists()

    except Exception as e:
        print(f"[TTS] gTTS falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 4: SILÊNCIO (fallback final)
# ─────────────────────────────────────────────

def _synthesize_silence(output_path: Path, duration_s: float = 5.0) -> bool:
    """Gera silêncio WAV como fallback final."""
    try:
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        r = subprocess.run(
            [ffmpeg, "-y", "-f", "lavfi", "-i", f"anullsrc=r=22050:cl=mono",
             "-t", str(duration_s), str(output_path)],
            capture_output=True, check=False
        )
        return r.returncode == 0
    except Exception:
        return False


# ─────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────

def synthesize(
    text: str,
    output_path: Path,
    model: str = DEFAULT_MODEL,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
    sentence_silence: float = 0.3,
    voice: str = EDGE_TTS_VOICE,
) -> Path:
    """
    Sintetiza texto em WAV usando a melhor engine disponível.
    Ordem: Piper → edge-tts → gTTS → silêncio

    Args:
        text: Texto a narrar (PT-BR).
        output_path: Caminho do arquivo WAV de saída.
        model: Modelo Piper (ignorado se Piper indisponível).
        voice: Voz edge-tts (padrão: pt-BR-FranciscaNeural).

    Returns:
        Path do arquivo WAV gerado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ENGINE 1 — Piper (local)
    if _synthesize_piper(text, output_path, length_scale):
        print(f"[TTS] Piper ✅ → {output_path.name}")
        return output_path

    # ENGINE 2 — edge-tts (Microsoft Neural PT-BR)
    if _synthesize_edge_tts(text, output_path, voice):
        print(f"[TTS] edge-tts ✅ → {output_path.name}")
        return output_path

    # ENGINE 3 — gTTS (Google)
    if _synthesize_gtts(text, output_path):
        print(f"[TTS] gTTS ✅ → {output_path.name}")
        return output_path

    # ENGINE 4 — silêncio
    words = len(text.split())
    dur = max(3.0, words * 0.4)
    _synthesize_silence(output_path, dur)
    print(f"[TTS] ⚠️ silêncio ({dur:.0f}s) → {output_path.name} — instale Piper para voz real")
    return output_path


def synthesize_ssml(ssml_text: str, output_path: Path, model: str = DEFAULT_MODEL) -> Path:
    return synthesize(ssml_text, output_path, model)


def wav_to_mp3(wav_path: Path, mp3_path: Optional[Path] = None, bitrate: str = "192k") -> Path:
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    if mp3_path is None:
        mp3_path = wav_path.with_suffix(".mp3")
    mp3_path = Path(mp3_path)
    result = subprocess.run(
        [ffmpeg, "-y", "-i", str(wav_path), "-b:a", bitrate, str(mp3_path)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Conversão WAV→MP3 falhou: {result.stderr}")
    return mp3_path


def get_audio_duration(path: Path) -> float:
    ffprobe = shutil.which("ffprobe") or "ffprobe"
    result = subprocess.run(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-show_formats", str(path)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0))
    return 0.0


def check_tts_engines() -> dict:
    """Retorna status de cada engine TTS disponível."""
    status = {"piper": False, "edge_tts": False, "gtts": False, "silence_fallback": True}
    status["piper"] = _model_path(DEFAULT_MODEL) is not None
    try:
        import edge_tts; status["edge_tts"] = True
    except ImportError:
        pass
    try:
        from gtts import gTTS; status["gtts"] = True
    except ImportError:
        pass
    return status


def narrar_roteiro(
    cenas: list,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    length_scale: float = 1.05,
    voice: str = EDGE_TTS_VOICE,
) -> list:
    """
    Narra todas as cenas de um roteiro.

    Returns:
        Lista de Paths dos arquivos WAV gerados (None para cenas sem narração).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audios = []

    for i, cena in enumerate(cenas, 1):
        texto = cena.get("narracao", "")
        if not texto.strip():
            audios.append(None)
            continue

        out_path = output_dir / f"narr_cena_{i:02d}.wav"
        try:
            synthesize(texto, out_path, model=model, length_scale=length_scale, voice=voice)
            audios.append(out_path)
        except Exception as e:
            print(f"[AVISO] Narração cena {i} falhou: {e}")
            audios.append(None)

    return audios


if __name__ == "__main__":
    import sys
    print("=== DARK STICKMAN STUDIO — TTS Engine Check ===")
    engines = check_tts_engines()
    for eng, ok in engines.items():
        print(f"  {'✅' if ok else '❌'} {eng}")

    text = sys.argv[1] if len(sys.argv) > 1 else \
        "Olá! Este é o DARK STICKMAN STUDIO, sua plataforma de criação de conteúdo."
    out = Path("/tmp/test_narr.wav")
    synthesize(text, out)
    dur = get_audio_duration(out)
    print(f"\nÁudio gerado: {out} ({dur:.1f}s)")
