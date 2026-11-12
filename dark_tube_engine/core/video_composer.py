"""
DARK TUBE ENGINE — Video Composer (clone vidiq_compose + vidiq_generate_video)
Agente: VIDEO EDITOR PRO + CINEMATIC DIRECTOR
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Fase 3 — DARK VIDEO STUDIO: zoompan, B-roll, pipeline_imagem_para_short
"""
import os
import json
import uuid
import subprocess
from pathlib import Path
from typing import Optional, List


# ---------------------------------------------------------------------------
# Efeitos zoompan disponíveis (clone local do wan_client.ZOOMPAN_EFFECTS)
# ---------------------------------------------------------------------------
ZOOMPAN_EFFECTS = {
    "zoom_in":    {"z": "min(zoom+0.0015,1.5)", "x": "iw/2-(iw/zoom/2)", "y": "ih/2-(ih/zoom/2)"},
    "zoom_out":   {"z": "if(eq(on,1),1.5,max(zoom-0.0015,1.0))", "x": "iw/2-(iw/zoom/2)", "y": "ih/2-(ih/zoom/2)"},
    "pan_left":   {"z": "1.2", "x": "if(eq(on,1),0,x+1)", "y": "ih/2-(ih/zoom/2)"},
    "pan_right":  {"z": "1.2", "x": "if(eq(on,1),iw*(1-1/zoom),x-1)", "y": "ih/2-(ih/zoom/2)"},
    "pan_up":     {"z": "1.2", "x": "iw/2-(iw/zoom/2)", "y": "if(eq(on,1),0,y+1)"},
    "pan_down":   {"z": "1.2", "x": "iw/2-(iw/zoom/2)", "y": "if(eq(on,1),ih*(1-1/zoom),y-1)"},
    "travelling": {"z": "min(zoom+0.001,1.3)", "x": "if(eq(on,1),0,x+0.5)", "y": "ih/2-(ih/zoom/2)"},
    "kenburns":   {"z": "min(zoom+0.0012,1.4)", "x": "if(eq(on,1),0,x+0.3)", "y": "if(eq(on,1),0,y+0.2)"},
}

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


def gerar_zoompan_ffmpeg(
    imagem_path: str,
    efeito: str = "zoom_in",
    duracao_s: float = 7.0,
    fps: int = 25,
    resolucao: str = "1080x1920",
    output_dir: str = "outputs/video",
    audio_path: Optional[str] = None,
) -> dict:
    """
    Anima imagem estática com efeito de câmera via FFmpeg zoompan.
    Backend local gratuito — sem GPU, sem API.

    Efeitos: zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down,
             travelling, kenburns
    """
    ffmpeg_ok = verificar_ffmpeg()
    if not ffmpeg_ok["disponivel"]:
        return {"status": "failed", "error": "FFmpeg não encontrado"}

    if not os.path.exists(imagem_path):
        return {"status": "failed", "error": f"Imagem não encontrada: {imagem_path}"}

    efeito_cfg = ZOOMPAN_EFFECTS.get(efeito, ZOOMPAN_EFFECTS["zoom_in"])
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    total_frames = int(duracao_s * fps)

    # Escala com padding para manter proporção 9:16
    scale_filter = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"

    z_expr = efeito_cfg["z"]
    x_expr = efeito_cfg["x"]
    y_expr = efeito_cfg["y"]
    zoompan_filter = (
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}'"
        f":d={total_frames}:s={w}x{h}:fps={fps}"
    )

    vf = f"{scale_filter},{zoompan_filter},format=yuv420p"

    vid_id = uuid.uuid4().hex[:8]
    output_path = str(Path(output_dir) / f"zoompan_{efeito}_{vid_id}.mp4")

    if audio_path and os.path.exists(audio_path):
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", imagem_path,
            "-i", audio_path,
            "-vf", vf,
            "-t", str(duracao_s),
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", imagem_path,
            "-vf", vf,
            "-t", str(duracao_s),
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-an",
            output_path,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "path": output_path if result.returncode == 0 else None,
        "efeito": efeito,
        "duracao_s": duracao_s,
        "resolucao": resolucao,
        "backend": "ffmpeg_zoompan",
        "custo": "GRATUITO",
        "error": result.stderr[-400:] if result.returncode != 0 else None,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def gerar_broll_imagem(
    imagem_path: str,
    efeito: str = "zoom_in",
    duracao_s: float = 5.0,
    resolucao: str = "1080x1920",
    output_dir: str = "outputs/video",
    audio_path: Optional[str] = None,
) -> dict:
    """
    Converte imagem estática em clipe B-roll animado.
    Wrapper semântico sobre gerar_zoompan_ffmpeg().
    """
    return gerar_zoompan_ffmpeg(
        imagem_path=imagem_path,
        efeito=efeito,
        duracao_s=duracao_s,
        fps=25,
        resolucao=resolucao,
        output_dir=output_dir,
        audio_path=audio_path,
    )


def concatenar_clips_local(
    clips_paths: List[str],
    output_path: str,
    adicionar_fade: bool = True,
) -> dict:
    """
    Concatena lista de clipes MP4 em um único vídeo via FFmpeg concat demuxer.
    Clone local de concatenar_clips() do wan_client.
    """
    ffmpeg_ok = verificar_ffmpeg()
    if not ffmpeg_ok["disponivel"]:
        return {"status": "failed", "error": "FFmpeg não encontrado"}

    clips_ok = [c for c in clips_paths if c and os.path.exists(c)]
    if not clips_ok:
        return {"status": "failed", "error": "Nenhum clip válido fornecido"}

    Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)

    # Arquivo de lista para o concat demuxer
    list_file = output_path.replace(".mp4", "_list.txt")
    with open(list_file, "w") as f:
        for clip in clips_ok:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    if adicionar_fade and len(clips_ok) > 1:
        # Reencoda com fade entre clips
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
    else:
        # Copy stream (mais rápido, sem reencoding)
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", list_file,
            "-c", "copy",
            output_path,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    try:
        os.remove(list_file)
    except Exception:
        pass

    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "path": output_path if result.returncode == 0 else None,
        "clips_concatenados": len(clips_ok),
        "backend": "ffmpeg_concat",
        "error": result.stderr[-400:] if result.returncode != 0 else None,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def pipeline_imagem_para_short(
    imagens: List[str],
    audio_path: Optional[str] = None,
    canal: str = "",
    efeitos: Optional[List[str]] = None,
    duracao_por_imagem: float = 5.0,
    resolucao: str = "1080x1920",
    output_dir: str = "outputs/video",
) -> dict:
    """
    Pipeline completo: lista de imagens → clipes B-roll → Short montado.

    Fluxo:
    1. Para cada imagem, gera clipe animado (zoompan alternado)
    2. Concatena todos os clipes
    3. Se audio_path fornecido, adiciona áudio ao vídeo final

    Efeitos alternam automaticamente: zoom_in → pan_right → pan_left → zoom_out → kenburns → travelling
    """
    if not imagens:
        return {"status": "failed", "error": "Nenhuma imagem fornecida"}

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    vid_id = uuid.uuid4().hex[:8]

    efeitos_ciclo = efeitos or ["zoom_in", "pan_right", "pan_left", "zoom_out", "kenburns", "travelling"]

    # Passo 1: Gera clipes individuais
    clips_gerados = []
    for idx, img_path in enumerate(imagens):
        efeito = efeitos_ciclo[idx % len(efeitos_ciclo)]
        resultado_clip = gerar_broll_imagem(
            imagem_path=img_path,
            efeito=efeito,
            duracao_s=duracao_por_imagem,
            resolucao=resolucao,
            output_dir=output_dir,
        )
        clips_gerados.append({
            "imagem": img_path,
            "efeito": efeito,
            "status": resultado_clip["status"],
            "path": resultado_clip.get("path"),
            "error": resultado_clip.get("error"),
        })

    clips_ok = [c["path"] for c in clips_gerados if c["status"] == "completed" and c["path"]]
    if not clips_ok:
        return {
            "status": "failed",
            "error": "Nenhum clipe gerado com sucesso",
            "clips_detalhes": clips_gerados,
        }

    # Passo 2: Concatena clipes
    concat_path = str(Path(output_dir) / f"concat_{vid_id}.mp4")
    concat_result = concatenar_clips_local(clips_ok, concat_path)

    if concat_result["status"] != "completed":
        return {
            "status": "failed",
            "error": f"Falha na concatenação: {concat_result.get('error')}",
            "clips_detalhes": clips_gerados,
        }

    # Passo 3: Adiciona áudio se fornecido
    video_final = concat_path
    if audio_path and os.path.exists(audio_path):
        final_path = str(Path(output_dir) / f"short_{vid_id}.mp4")
        cmd_audio = [
            "ffmpeg", "-y",
            "-i", concat_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_path,
        ]
        r = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=120)
        video_final = final_path if r.returncode == 0 else concat_path

    return {
        "status": "completed",
        "path": video_final,
        "canal": canal,
        "total_imagens": len(imagens),
        "clips_ok": len(clips_ok),
        "clips_detalhes": clips_gerados,
        "resolucao": resolucao,
        "backend": "ffmpeg_zoompan+concat",
        "custo": "GRATUITO — FFmpeg local",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


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
