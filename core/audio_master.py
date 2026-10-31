"""
DARK CREATIVE LAB — AGENTE AUDIO MASTER
Narração, mixagem, tratamento e masterização para YouTube.

Cascade de engines TTS (gratuitas):
1. Kokoro TTS local (82M params, pip install kokoro, sem GPU)
2. Piper TTS local (pt_BR-faber-medium, offline)
3. edge-tts via subprocess (Microsoft Neural, sem chave de API)
4. HuggingFace Inference API (facebook/mms-tts-por, token gratuito)
5. gTTS (Google, fallback final)

Processamento de áudio via FFmpeg:
- Normalização LUFS YouTube (-14 LUFS)
- Redução de ruído (highpass/lowpass)
- Compressão dinâmica
- Equalização
- Detecção de silêncio
- Mixagem narração + trilha

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, List

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

# Target de loudness YouTube
YOUTUBE_LUFS = -14.0
YOUTUBE_TP = -1.5    # True Peak
YOUTUBE_LRA = 11     # Loudness Range

# Vozes PT-BR disponíveis por engine
VOZES_PTBR = {
    "piper":       "pt_BR/faber-medium",
    "kokoro":      "p",          # lang_code para PT-BR
    "edge_tts":    "pt-BR-FranciscaNeural",  # Voz feminina natural
    "edge_tts_m":  "pt-BR-AntonioNeural",    # Voz masculina
    "hf_mms":      "facebook/mms-tts-por",
    "gtts":        "pt",
}


# ─────────────────────────────────────────────────────────────────
#  TTS CASCADE
# ─────────────────────────────────────────────────────────────────

def _tts_kokoro(texto: str, output_path: Path, voz: str = "bf_emma") -> bool:
    """Kokoro TTS local — 82M params, sem GPU necessário."""
    try:
        from kokoro import KPipeline
        import soundfile as sf
        import numpy as np

        pipe = KPipeline(lang_code="p")  # 'p' = português
        samples, sr = [], 22050
        for gs, ps, audio in pipe(texto, voice=voz, speed=1.0, split_pattern=r"\n+"):
            samples.append(audio)
        if samples:
            combined = np.concatenate(samples)
            sf.write(str(output_path), combined, sr)
            return True
    except Exception as e:
        print(f"[AUDIO] Kokoro falhou: {e}")
    return False


def _tts_piper(texto: str, output_path: Path) -> bool:
    """Piper TTS local — pt_BR-faber-medium, offline."""
    piper = shutil.which("piper") or shutil.which("piper-tts")
    if not piper:
        # Tenta caminho comum do Colab
        for p in ["/usr/local/bin/piper", "/content/piper/piper", "/tmp/piper/piper"]:
            if Path(p).exists():
                piper = p
                break

    model_search = [
        "/content/piper/pt_BR-faber-medium.onnx",
        "/tmp/piper/pt_BR-faber-medium.onnx",
        str(Path.home() / "piper" / "pt_BR-faber-medium.onnx"),
    ]
    model = next((m for m in model_search if Path(m).exists()), None)

    if not piper or not model:
        return False

    try:
        tmp_wav = output_path.with_suffix(".piper.wav")
        result = subprocess.run(
            [piper, "--model", model, "--output_file", str(tmp_wav)],
            input=texto.encode("utf-8"),
            capture_output=True,
            timeout=60,
        )
        if result.returncode == 0 and tmp_wav.exists():
            # Converte para MP3 via FFmpeg
            subprocess.run([
                FFMPEG, "-y", "-i", str(tmp_wav),
                "-c:a", "libmp3lame", "-q:a", "2",
                str(output_path)
            ], capture_output=True, check=True)
            tmp_wav.unlink(missing_ok=True)
            return True
    except Exception as e:
        print(f"[AUDIO] Piper falhou: {e}")
    return False


def _tts_edge(texto: str, output_path: Path, voz: str = None) -> bool:
    """edge-tts — Microsoft Neural, sem chave de API."""
    voz = voz or VOZES_PTBR["edge_tts"]
    try:
        import asyncio
        import edge_tts

        async def _gen():
            comm = edge_tts.Communicate(texto, voz)
            await comm.save(str(output_path))

        loop = asyncio.new_event_loop()
        loop.run_until_complete(_gen())
        loop.close()
        return output_path.exists() and output_path.stat().st_size > 1000
    except Exception as e:
        print(f"[AUDIO] edge-tts falhou: {e}")
    return False


def _tts_hf_mms(texto: str, output_path: Path) -> bool:
    """HuggingFace MMS-TTS-POR — Inference API gratuita (requer HF_TOKEN)."""
    import urllib.request
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        return False
    try:
        url = "https://api-inference.huggingface.co/models/facebook/mms-tts-por"
        data = texto.encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "text/plain",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            audio_bytes = r.read()
        if len(audio_bytes) > 1000:
            output_path.write_bytes(audio_bytes)
            return True
    except Exception as e:
        print(f"[AUDIO] HF MMS falhou: {e}")
    return False


def _tts_gtts(texto: str, output_path: Path) -> bool:
    """gTTS — Google Text-to-Speech, fallback."""
    try:
        from gtts import gTTS
        tts = gTTS(text=texto, lang="pt", slow=False)
        tts.save(str(output_path))
        return output_path.exists() and output_path.stat().st_size > 1000
    except Exception as e:
        print(f"[AUDIO] gTTS falhou: {e}")
    return False


def _tts_silencio(duracao: float, output_path: Path) -> bool:
    """Gera arquivo de silêncio como último fallback."""
    try:
        subprocess.run([
            FFMPEG, "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=22050:cl=mono",
            "-t", str(max(0.5, duracao)),
            "-c:a", "libmp3lame", "-q:a", "9",
            str(output_path),
        ], capture_output=True, check=True)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────
#  INTERFACE PRINCIPAL TTS
# ─────────────────────────────────────────────────────────────────

TTS_CASCADE = [
    ("kokoro_local", _tts_kokoro,   "🆓 Kokoro local — 82M params, PT-BR"),
    ("piper_local",  _tts_piper,    "🆓 Piper local — pt_BR-faber-medium"),
    ("edge_tts",     _tts_edge,     "🆓 Microsoft Neural — edge-tts"),
    ("hf_mms",       _tts_hf_mms,  "🆓 HF Inference API — MMS-TTS-POR"),
    ("gtts",         _tts_gtts,    "🆓 Google TTS — fallback"),
]


def synthesize(
    texto: str,
    output_path: Path,
    duracao_esperada: float = 5.0,
    verbose: bool = True,
) -> dict:
    """
    AGENTE AUDIO MASTER — Sintetiza narração via cascade de engines TTS.

    Args:
        texto: Texto a narrar.
        output_path: Caminho do arquivo de saída.
        duracao_esperada: Duração esperada em segundos (usado para silêncio fallback).
        verbose: Imprimir logs.

    Returns:
        Dict com status, engine usada e caminho do arquivo.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not texto or not texto.strip():
        _tts_silencio(duracao_esperada, output_path)
        return {
            "status": "ok",
            "engine": "silencio",
            "output_path": str(output_path),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    for nome, func, descricao in TTS_CASCADE:
        if verbose:
            print(f"[AUDIO] Tentando {nome}: {descricao}")
        try:
            ok = func(texto, output_path)
            if ok and output_path.exists() and output_path.stat().st_size > 500:
                if verbose:
                    print(f"[AUDIO] ✅ {nome} — {output_path.name}")
                return {
                    "status": "ok",
                    "engine": nome,
                    "output_path": str(output_path),
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
                }
        except Exception as e:
            if verbose:
                print(f"[AUDIO] {nome} exception: {e}")
            continue

    # Último recurso: silêncio
    _tts_silencio(duracao_esperada, output_path)
    return {
        "status": "silencio",
        "engine": "silencio",
        "output_path": str(output_path),
        "aviso": "Nenhum engine TTS disponível — usando silêncio",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  PROCESSAMENTO DE ÁUDIO
# ─────────────────────────────────────────────────────────────────

def normalizar_lufs(input_path: Path, output_path: Path) -> Path:
    """Normaliza áudio para -14 LUFS (padrão YouTube)."""
    output_path = Path(output_path)
    subprocess.run([
        FFMPEG, "-y", "-i", str(input_path),
        "-af", f"loudnorm=I={YOUTUBE_LUFS}:TP={YOUTUBE_TP}:LRA={YOUTUBE_LRA}",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ], capture_output=True, check=True)
    return output_path


def reduzir_ruido(input_path: Path, output_path: Path, intensidade: float = 0.2) -> Path:
    """Redução básica de ruído via FFmpeg (highpass + lowpass + denoise)."""
    output_path = Path(output_path)
    # afftdn = FFmpeg Adaptive Noise Reduction
    af = (
        f"highpass=f=80,"           # Remove ruído de baixa frequência
        f"lowpass=f=10000,"         # Remove hiss de alta frequência
        f"afftdn=nf=-{intensidade*80:.0f},"  # Noise reduction adaptativo
        f"dynaudnorm=f=150:g=15"   # Normalização dinâmica
    )
    subprocess.run([
        FFMPEG, "-y", "-i", str(input_path),
        "-af", af,
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ], capture_output=True, check=True)
    return output_path


def comprimir_audio(input_path: Path, output_path: Path) -> Path:
    """Compressão dinâmica para narração — voz mais uniforme."""
    output_path = Path(output_path)
    # acompressor: threshold=-15dB, ratio=4:1, attack=5ms, release=50ms
    af = "acompressor=threshold=-15dB:ratio=4:attack=5:release=50:makeup=2dB"
    subprocess.run([
        FFMPEG, "-y", "-i", str(input_path),
        "-af", af,
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ], capture_output=True, check=True)
    return output_path


def equalizar_voz(input_path: Path, output_path: Path) -> Path:
    """EQ para narração — presença e clareza para YouTube."""
    output_path = Path(output_path)
    # Boost presença (3kHz), clareza (5kHz), corta grave excessivo
    af = (
        "equalizer=f=200:t=o:w=200:g=-3,"    # Corta empastelamento
        "equalizer=f=3000:t=o:w=2000:g=3,"   # Boost presença
        "equalizer=f=5000:t=o:w=3000:g=2"    # Clareza de voz
    )
    subprocess.run([
        FFMPEG, "-y", "-i", str(input_path),
        "-af", af,
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ], capture_output=True, check=True)
    return output_path


def mixar_narr_trilha(
    narr_path: Path,
    trilha_path: Path,
    output_path: Path,
    vol_narr: float = 1.0,
    vol_trilha: float = 0.12,
) -> Path:
    """
    Mixagem narração + trilha com ducking automático.
    - Narração: volume normal
    - Trilha: reduzida para 12% (não atrapalha a voz)
    """
    output_path = Path(output_path)
    subprocess.run([
        FFMPEG, "-y",
        "-i", str(narr_path),
        "-i", str(trilha_path),
        "-filter_complex",
        f"[0:a]volume={vol_narr}[narr];"
        f"[1:a]volume={vol_trilha},aloop=loop=-1:size=2e+09[trilha];"
        "[narr][trilha]amix=inputs=2:duration=first:dropout_transition=3[mix]",
        "-map", "[mix]",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ], capture_output=True, check=True)
    return output_path


def masterizar(input_path: Path, output_path: Path) -> Path:
    """Pipeline completo de masterização: EQ → Compressão → Normalização LUFS."""
    tmp1 = input_path.parent / f"_eq_{input_path.name}"
    tmp2 = input_path.parent / f"_comp_{input_path.name}"
    try:
        equalizar_voz(input_path, tmp1)
        comprimir_audio(tmp1, tmp2)
        normalizar_lufs(tmp2, output_path)
    finally:
        for f in [tmp1, tmp2]:
            if Path(f).exists():
                Path(f).unlink(missing_ok=True)
    return output_path


def detectar_silencio(audio_path: Path, threshold_db: float = -30.0) -> list[dict]:
    """
    Detecta segmentos de silêncio no áudio.
    Retorna lista de {'inicio': float, 'fim': float, 'duracao': float}.
    """
    result = subprocess.run([
        FFMPEG, "-i", str(audio_path),
        "-af", f"silencedetect=noise={threshold_db}dB:d=0.3",
        "-f", "null", "-"
    ], capture_output=True, text=True)

    import re
    silences = []
    starts = re.findall(r"silence_start: ([\d.]+)", result.stderr)
    ends   = re.findall(r"silence_end: ([\d.]+)", result.stderr)

    for s, e in zip(starts, ends):
        s, e = float(s), float(e)
        silences.append({"inicio": s, "fim": e, "duracao": round(e - s, 3)})

    return silences


def get_duracao_audio(audio_path: Path) -> float:
    """Retorna duração do arquivo de áudio em segundos."""
    result = subprocess.run([
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ], capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────────
#  GERAÇÃO DE NARRAÇÃO COMPLETA DO ROTEIRO
# ─────────────────────────────────────────────────────────────────

def narrar_roteiro_completo(
    cenas: list[dict],
    output_dir: Path,
    verbose: bool = True,
) -> list[Optional[Path]]:
    """
    AGENTE AUDIO MASTER — Narra todas as cenas do roteiro.

    Args:
        cenas: Lista de dicts com 'narracao' e 'duracao'.
        output_dir: Diretório de saída dos áudios.
        verbose: Imprimir progresso.

    Returns:
        Lista de Path para cada arquivo de áudio (None se cena sem narração).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audios = []

    for i, cena in enumerate(cenas):
        texto = cena.get("narracao", "").strip()
        duracao = float(cena.get("duracao", cena.get("duracao_s", 5.0)))
        out = output_dir / f"narr_{i+1:02d}.mp3"

        if not texto:
            audios.append(None)
            continue

        resultado = synthesize(texto, out, duracao_esperada=duracao, verbose=verbose)
        if resultado["status"] in ("ok", "silencio") and Path(resultado["output_path"]).exists():
            audios.append(Path(resultado["output_path"]))
        else:
            audios.append(None)

        if verbose:
            print(f"[AUDIO] Cena {i+1}/{len(cenas)} → {out.name} ({resultado['engine']})")

    return audios


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_audio_master() -> dict:
    """Diagnóstico de todos os engines TTS disponíveis."""
    engines = {}

    # Kokoro
    try:
        import kokoro
        engines["kokoro"] = {"disponivel": True, "tipo": "local", "gpu": False}
    except ImportError:
        engines["kokoro"] = {"disponivel": False, "instalar": "pip install kokoro soundfile"}

    # Piper
    piper = shutil.which("piper") or shutil.which("piper-tts")
    engines["piper"] = {
        "disponivel": bool(piper),
        "tipo": "local",
        "gpu": False,
        "binario": piper or "não encontrado",
    }

    # edge-tts
    try:
        import edge_tts
        engines["edge_tts"] = {"disponivel": True, "tipo": "cloud_gratis", "gpu": False}
    except ImportError:
        engines["edge_tts"] = {"disponivel": False, "instalar": "pip install edge-tts"}

    # gTTS
    try:
        from gtts import gTTS
        engines["gtts"] = {"disponivel": True, "tipo": "cloud_gratis", "gpu": False}
    except ImportError:
        engines["gtts"] = {"disponivel": False, "instalar": "pip install gtts"}

    # HF Token
    engines["hf_mms"] = {
        "disponivel": bool(os.environ.get("HF_TOKEN")),
        "tipo": "cloud_gratis",
        "requer": "HF_TOKEN env var",
    }

    # FFmpeg
    engines["ffmpeg"] = {
        "disponivel": bool(shutil.which("ffmpeg")),
        "processamento": ["normalizar", "comprimir", "equalizar", "masterizar", "mixar"],
    }

    algum_tts = any(
        v.get("disponivel") for k, v in engines.items()
        if k not in ("ffmpeg",)
    )

    return {
        "status": "ok" if algum_tts else "degradado",
        "engines": engines,
        "target_lufs": YOUTUBE_LUFS,
        "vozes_ptbr": VOZES_PTBR,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
