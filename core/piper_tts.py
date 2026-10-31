"""
DARK STICKMAN STUDIO — Narração PT-BR com Piper TTS
Geração de voz natural offline — modelo pt_BR.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import os
import shutil
import subprocess
import json
import time
from pathlib import Path
from typing import Optional

PIPER_BIN = shutil.which("piper") or os.environ.get("PIPER_PATH", "piper")

# Modelos recomendados para PT-BR (baixar em https://huggingface.co/rhasspy/piper-voices)
PT_BR_MODELS = {
    "faber-medium":   "pt_BR-faber-medium.onnx",
    "faber-low":      "pt_BR-faber-low.onnx",
    "edresson-low":   "pt_BR-edresson_low.onnx",
}

DEFAULT_MODEL = "faber-medium"
MODELS_DIR = Path(__file__).parent.parent / "assets" / "models" / "piper"


def _model_path(model_name: str) -> Optional[Path]:
    """Retorna caminho do modelo .onnx se existir."""
    filename = PT_BR_MODELS.get(model_name, model_name)
    candidate = MODELS_DIR / filename
    if candidate.exists():
        return candidate
    # Tenta path direto se model_name já for um caminho
    direct = Path(model_name)
    if direct.exists():
        return direct
    return None


def synthesize(
    text: str,
    output_path: Path,
    model: str = DEFAULT_MODEL,
    length_scale: float = 1.0,
    noise_scale: float = 0.667,
    noise_w: float = 0.8,
    sentence_silence: float = 0.3,
) -> Path:
    """
    Sintetiza texto em áudio WAV usando Piper TTS.

    Args:
        text: Texto a narrar (PT-BR).
        output_path: Caminho do arquivo WAV de saída.
        model: Nome ou caminho do modelo ONNX.
        length_scale: Velocidade da fala (1.0 = normal; >1 = mais lento).
        noise_scale: Variação de tom (0 = monotônico; 1 = mais variado).
        noise_w: Variação de duração de fonemas.
        sentence_silence: Silêncio entre frases (segundos).

    Returns:
        Path do arquivo WAV gerado.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model_path = _model_path(model)
    if model_path is None:
        # Fallback: tentar piper instalado no sistema sem especificar modelo
        _synthesize_system_piper(text, output_path, length_scale)
        return output_path

    config_path = model_path.with_suffix(".onnx.json")

    cmd = [
        PIPER_BIN,
        "--model", str(model_path),
        "--output_file", str(output_path),
        "--length_scale", str(length_scale),
        "--noise_scale", str(noise_scale),
        "--noise_w", str(noise_w),
        "--sentence_silence", str(sentence_silence),
    ]
    if config_path.exists():
        cmd += ["--config", str(config_path)]

    result = subprocess.run(
        cmd,
        input=text,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Piper TTS falhou (código {result.returncode}):\n{result.stderr}"
        )

    if not output_path.exists():
        raise FileNotFoundError(f"Piper não gerou o arquivo: {output_path}")

    return output_path


def _synthesize_system_piper(text: str, output_path: Path, length_scale: float = 1.0) -> None:
    """Tenta usar piper instalado no sistema sem especificar modelo."""
    cmd = [PIPER_BIN, "--output_file", str(output_path), "--length_scale", str(length_scale)]
    result = subprocess.run(cmd, input=text, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            "Piper TTS não encontrado ou sem modelo configurado.\n"
            "Instale via: pip install piper-tts\n"
            "Baixe o modelo PT-BR em: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR\n"
            f"Erro: {result.stderr}"
        )


def synthesize_ssml(
    ssml_text: str,
    output_path: Path,
    model: str = DEFAULT_MODEL,
) -> Path:
    """
    Sintetiza com marcações SSML para controle fino de entonação.
    SSML básico suportado pelo Piper: <break time="0.5s"/>, <emphasis>.
    """
    # Piper suporta subset de SSML — passamos o texto direto
    return synthesize(ssml_text, output_path, model)


def wav_to_mp3(wav_path: Path, mp3_path: Optional[Path] = None, bitrate: str = "192k") -> Path:
    """Converte WAV para MP3 via FFmpeg."""
    import shutil as sh
    ffmpeg = sh.which("ffmpeg") or "ffmpeg"
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
    """Retorna duração do áudio em segundos."""
    import shutil as sh
    ffprobe = sh.which("ffprobe") or "ffprobe"
    result = subprocess.run(
        [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return float(data.get("format", {}).get("duration", 0))
    return 0.0


def check_piper() -> bool:
    """Verifica se Piper está instalado."""
    result = subprocess.run(
        [PIPER_BIN, "--help"],
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0


def narrar_roteiro(
    cenas: list,
    output_dir: Path,
    model: str = DEFAULT_MODEL,
    length_scale: float = 1.05,
) -> list:
    """
    Narra todas as cenas de um roteiro.

    Args:
        cenas: Lista de dicts com campo 'narracao'.
        output_dir: Diretório para arquivos WAV.
        model: Modelo Piper PT-BR.
        length_scale: Velocidade (>1 = mais lento, mais natural).

    Returns:
        Lista de Paths dos arquivos WAV gerados.
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
            synthesize(texto, out_path, model=model, length_scale=length_scale)
            audios.append(out_path)
        except Exception as e:
            print(f"[AVISO] Narração cena {i} falhou: {e}")
            audios.append(None)

    return audios


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "Olá! Este é o DARK STICKMAN STUDIO, sua plataforma de criação de conteúdo."
    out  = Path("test_narr.wav")
    try:
        synthesize(text, out)
        print(f"Áudio gerado: {out} ({get_audio_duration(out):.1f}s)")
    except Exception as e:
        print(f"Erro: {e}")
        print("Instale Piper: pip install piper-tts")
        print("Baixe modelo PT-BR: https://huggingface.co/rhasspy/piper-voices")
