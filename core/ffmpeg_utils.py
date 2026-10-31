"""
DARK STICKMAN STUDIO — Utilitários FFmpeg
Wrapper Python sobre FFmpeg para montagem, efeitos e encoding.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import subprocess
import shutil
import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def _run(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Executa comando FFmpeg com tratamento de erro."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg erro (código {result.returncode}):\n{result.stderr[-1000:]}"
        )
    return result


def probe(path: Path) -> dict:
    """Retorna metadata do arquivo de mídia via ffprobe."""
    cmd = [
        FFPROBE, "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path),
    ]
    r = _run(cmd)
    return json.loads(r.stdout)


def get_duration(path: Path) -> float:
    """Duração do arquivo em segundos."""
    info = probe(path)
    return float(info["format"].get("duration", 0))


def svg_to_png(svg_path: Path, png_path: Path, width: int = 1920, height: int = 1080) -> Path:
    """Converte SVG para PNG via FFmpeg (requer libsvg ou Inkscape como fallback)."""
    # Tenta via Inkscape primeiro (melhor qualidade para SVG)
    inkscape = shutil.which("inkscape")
    if inkscape:
        _run([inkscape, "--export-type=png", f"--export-filename={png_path}",
              f"--export-width={width}", f"--export-height={height}", str(svg_path)])
        return png_path

    # Fallback: cairosvg via Python
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
            output_height=height,
        )
        return png_path
    except ImportError:
        pass

    # Fallback final: FFmpeg com filtro scale
    cmd = [
        FFMPEG, "-y",
        "-i", str(svg_path),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        str(png_path),
    ]
    _run(cmd)
    return png_path


def image_to_video(
    image_path: Path,
    output_path: Path,
    duration: float = 5.0,
    fps: int = 30,
    zoom: bool = False,
    zoom_speed: float = 0.0003,
) -> Path:
    """
    Converte imagem estática em clipe de vídeo.
    Opcionalmente aplica efeito de zoom suave (Ken Burns).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if zoom:
        vf = (
            f"zoompan=z='min(zoom+{zoom_speed},1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * fps)}:s=1920x1080:fps={fps}"
        )
    else:
        vf = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"

    cmd = [
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def concat_videos(clips: List[Path], output_path: Path, transition: str = "fade", transition_dur: float = 0.5) -> Path:
    """
    Concatena múltiplos clipes com transição.
    transition: 'fade', 'dissolve', 'none'
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clips = [Path(c) for c in clips]

    if transition == "none" or len(clips) == 1:
        # Concatenação simples via arquivo de lista
        list_file = output_path.with_suffix(".txt")
        with open(list_file, "w") as f:
            for c in clips:
                f.write(f"file '{c.absolute()}'\n")
        cmd = [
            FFMPEG, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            str(output_path),
        ]
        _run(cmd)
        list_file.unlink(missing_ok=True)
        return output_path

    # Transição xfade entre clipes
    if len(clips) == 2:
        dur_a = get_duration(clips[0])
        offset = max(0, dur_a - transition_dur)
        cmd = [
            FFMPEG, "-y",
            "-i", str(clips[0]),
            "-i", str(clips[1]),
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=dissolve:duration={transition_dur}:offset={offset:.2f}[v];"
            f"[0:a][1:a]acrossfade=d={transition_dur}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path),
        ]
        _run(cmd)
        return output_path

    # Múltiplos clipes: encadear xfades recursivamente
    current = clips[0]
    for i, next_clip in enumerate(clips[1:]):
        tmp = output_path.parent / f"_xfade_{i}.mp4"
        dur_a = get_duration(current)
        offset = max(0, dur_a - transition_dur)
        cmd = [
            FFMPEG, "-y",
            "-i", str(current),
            "-i", str(next_clip),
            "-filter_complex",
            f"[0:v][1:v]xfade=transition=dissolve:duration={transition_dur}:offset={offset:.2f}[v];"
            f"[0:a][1:a]acrossfade=d={transition_dur}[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(tmp),
        ]
        _run(cmd)
        current = tmp

    shutil.move(str(current), str(output_path))
    return output_path


def add_audio(video_path: Path, audio_path: Path, output_path: Path, vol_video: float = 1.0) -> Path:
    """Adiciona trilha de áudio a um vídeo (substitui ou mistura)."""
    output_path = Path(output_path)
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex", f"[1:a]volume={vol_video}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def mix_audio(narr_path: Path, music_path: Path, output_path: Path,
              vol_narr: float = 1.0, vol_music: float = 0.15) -> Path:
    """Mixa narração + trilha sonora com ducking automático."""
    output_path = Path(output_path)
    cmd = [
        FFMPEG, "-y",
        "-i", str(narr_path),
        "-i", str(music_path),
        "-filter_complex",
        f"[0:a]volume={vol_narr}[narr];"
        f"[1:a]volume={vol_music}[music];"
        "[narr][music]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def normalize_audio(input_path: Path, output_path: Path, target_lufs: float = -14.0) -> Path:
    """Normaliza áudio para target LUFS (padrão YouTube)."""
    output_path = Path(output_path)
    cmd = [
        FFMPEG, "-y",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def burn_subtitles(video_path: Path, srt_path: Path, output_path: Path,
                   font: str = "Arial", font_size: int = 32,
                   color: str = "white", border_color: str = "black") -> Path:
    """Queima legendas SRT no vídeo."""
    output_path = Path(output_path)
    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")
    vf = (
        f"subtitles={srt_escaped}:force_style='"
        f"FontName={font},FontSize={font_size},"
        f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
        f"BorderStyle=1,Outline=2,Shadow=1,Alignment=2'"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def add_watermark_text(video_path: Path, output_path: Path, text: str,
                       x: str = "10", y: str = "10", font_size: int = 16,
                       color: str = "white@0.5") -> Path:
    """Adiciona watermark de texto (identificação de conteúdo IA)."""
    output_path = Path(output_path)
    vf = (
        f"drawtext=text='{text}':x={x}:y={y}:"
        f"fontsize={font_size}:fontcolor={color}:"
        f"box=1:boxcolor=black@0.3:boxborderw=5"
    )
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def apply_color_grade(video_path: Path, output_path: Path, preset: str = "neutral") -> Path:
    """Aplica color grading por preset cinematográfico."""
    GRADES = {
        "neutral":     "eq=brightness=0.0:contrast=1.0:saturation=1.0",
        "documentario": "eq=brightness=-0.02:contrast=1.1:saturation=0.85,curves=r='0/0 0.5/0.45 1/0.9':b='0/0.05 1/0.95'",
        "batalha":     "eq=brightness=-0.05:contrast=1.3:saturation=0.7,vignette=PI/4",
        "educacao":    "eq=brightness=0.02:contrast=1.05:saturation=1.1",
        "suspense":    "eq=brightness=-0.08:contrast=1.2:saturation=0.6,curves=r='0/0 1/0.85':b='0/0.05 1/1.0'",
        "relaxamento": "eq=brightness=0.03:contrast=0.95:saturation=1.15",
        "tecnologia":  "eq=brightness=0:contrast=1.1:saturation=0.9,curves=b='0/0 0.5/0.55 1/1'",
        "natureza":    "eq=brightness=0.02:contrast=1.05:saturation=1.3",
    }
    vf = GRADES.get(preset, GRADES["neutral"])
    output_path = Path(output_path)
    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def export_final(
    video_path: Path,
    output_path: Path,
    resolution: str = "1920x1080",
    format: str = "16:9",
) -> Path:
    """Exporta vídeo final com resolução e formato especificados."""
    output_path = Path(output_path)
    w, h = resolution.split("x")

    if format == "9:16":
        # Vertical: recortar centro para 9:16
        vf = f"crop=ih*9/16:ih,scale={w}:{h}"
    else:
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"

    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    _run(cmd)
    return output_path


def check_ffmpeg() -> bool:
    """Verifica se FFmpeg está instalado e acessível."""
    try:
        r = _run([FFMPEG, "-version"], check=False)
        return r.returncode == 0
    except FileNotFoundError:
        return False
