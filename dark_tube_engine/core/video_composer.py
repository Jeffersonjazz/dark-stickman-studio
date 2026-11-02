"""
DARK TUBE ENGINE — Video Composer (clone vidiq_compose + vidiq_generate_video)
Agente: VIDEO EDITOR PRO + CINEMATIC DIRECTOR
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
import json
import uuid
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False


def verificar_ffmpeg() -> dict:
    """Verifica se FFmpeg está disponível"""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        versao = result.stdout.split('\n')[0] if result.returncode == 0 else None
        return {"disponivel": result.returncode == 0, "versao": versao}
    except FileNotFoundError:
        return {"disponivel": False, "versao": None}


def gerar_video_fundo_ffmpeg(
    audio_path: str,
    output_path: str,
    cor_bg: str = "0x0A0A1E",
    resolucao: str = "1080x1920",
    fps: int = 30
) -> dict:
    """
    Gera vídeo com fundo sólido + áudio via FFmpeg
    Equivalente ao vidiq_generate_video com fundo animado mínimo
    """
    w, h = resolucao.split("x")
    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-f", "lavfi",
        "-i", f"color=c={cor_bg}:s={w}x{h}:r={fps}",
        "-shortest",
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "output_path": output_path,
        "error": result.stderr if result.returncode != 0 else None
    }


def gerar_video_com_legenda(
    audio_path: str,
    legenda_path: str,
    output_path: str,
    thumbnail_path: Optional[str] = None,
    resolucao: str = "1080x1920",
    cor_bg: str = "0x0A0A1E",
    estilo_legenda: dict = None
) -> dict:
    """
    Compõe Short vertical com áudio + legenda animada (estilo Shorts virais)
    Clone funcional do vidiq_compose
    """
    ffmpeg_ok = verificar_ffmpeg()
    if not ffmpeg_ok["disponivel"]:
        return {"status": "failed", "error": "FFmpeg não encontrado. Instale: sudo apt install ffmpeg"}

    w, h = resolucao.split("x")
    estilo = estilo_legenda or {
        "fontsize": 56,
        "fontcolor": "white",
        "bordercolor": "black",
        "borderw": 3,
        "alignment": 2,  # centro
        "shadow": 1
    }

    # Filtro de legenda
    ass_filter = (
        f"subtitles={legenda_path}:force_style='"
        f"Fontsize={estilo['fontsize']},"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"Outline={estilo['borderw']},"
        f"Shadow={estilo['shadow']},"
        f"Alignment={estilo['alignment']}'"
    )

    # Comando FFmpeg
    vf_filters = [ass_filter]
    filter_str = ",".join(vf_filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-f", "lavfi", "-i", f"color=c={cor_bg}:s={w}x{h}:r=30",
        "-shortest",
        "-vf", filter_str,
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "output_path": output_path if result.returncode == 0 else None,
        "error": result.stderr[-500:] if result.returncode != 0 else None
    }


def gerar_srt_do_script(
    script: str,
    duracao_total_s: float,
    output_path: str
) -> str:
    """
    Gera arquivo SRT de legenda a partir do script
    Clone da funcionalidade de geração de legendas vidIQ
    """
    Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
    frases = [f.strip() for f in script.replace('\n', ' ').split('.') if f.strip()]
    if not frases:
        frases = [script.strip()]

    duracao_por_frase = duracao_total_s / max(len(frases), 1)
    srt_content = ""
    for i, frase in enumerate(frases):
        inicio = i * duracao_por_frase
        fim = (i + 1) * duracao_por_frase
        inicio_ts = _segundos_para_srt(inicio)
        fim_ts = _segundos_para_srt(fim)
        srt_content += f"{i+1}\n{inicio_ts} --> {fim_ts}\n{frase}\n\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return output_path


def _segundos_para_srt(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def pipeline_compose_short(
    titulo: str,
    canal: str,
    script: str,
    audio_path: str,
    output_dir: str = "outputs/video",
    resolucao: str = "1080x1920"
) -> dict:
    """
    Pipeline completo: áudio → legenda → vídeo final
    Equivalente ao fluxo vidiq_compose para Shorts
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    video_id = str(uuid.uuid4())[:8]
    slug = titulo.lower().replace(" ", "_")[:30]

    srt_path = os.path.join(output_dir, f"leg_{video_id}.srt")
    output_path = os.path.join(output_dir, f"short_{video_id}_{slug}.mp4")

    # Estimar duração do áudio
    duracao_est = len(script.split()) / 2.5  # ~2.5 palavras/s PT-BR

    # Gera legenda
    gerar_srt_do_script(script, duracao_est, srt_path)

    # Compõe vídeo
    resultado = gerar_video_fundo_ffmpeg(audio_path, output_path, resolucao=resolucao)

    return {
        "video_id": video_id,
        "titulo": titulo,
        "canal": canal,
        "output_path": resultado.get("output_path") or output_path,
        "srt_path": srt_path,
        "status": resultado["status"],
        "resolucao": resolucao,
        "error": resultado.get("error"),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }
