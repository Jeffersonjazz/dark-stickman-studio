"""
DARK TUBE ENGINE — Wan 2.2 Image-to-Video Client
Fase 3: DARK VIDEO STUDIO — Animação de imagens e geração de vídeo realista
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Modelos integrados:
- Wan 2.2 I2V (image-to-video) via HuggingFace Space — gratuito, alta qualidade
- FFmpeg zoompan — fallback local sem GPU, sem custos

Capacidades:
- Imagem → Vídeo com movimento de câmera (pan, zoom, travelling)
- Texto → Vídeo (Wan T2V quando disponível)
- Presets cinematográficos por nicho DARK STUDIO
- B-roll automático a partir de thumbnails FLUX
"""
import os
import uuid
import time
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Literal

try:
    from gradio_client import Client, handle_file
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Space oficial Wan 2.2 I2V — gratuito, sem login obrigatório
WAN_I2V_SPACE = "Wan-AI/Wan2.2-I2V-A14B-720P"
WAN_T2V_SPACE = "Wan-AI/Wan2.2-T2V-A14B-720P"

DEFAULT_OUTPUT_DIR = "outputs/video"
AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

# Presets de movimento por nicho DARK STUDIO
MOTION_PRESETS = {
    "motivacional": {
        "prompt_motion": "slow zoom in, dramatic camera movement, cinematic lighting",
        "zoompan": "zoom_in",
        "duracao": 6,
    },
    "terror": {
        "prompt_motion": "slow pan left, dark atmosphere, unsettling camera movement, creeping",
        "zoompan": "pan_left",
        "duracao": 7,
    },
    "tech_ia": {
        "prompt_motion": "smooth dolly forward, futuristic atmosphere, blue neon glow",
        "zoompan": "zoom_in",
        "duracao": 6,
    },
    "conspiracao": {
        "prompt_motion": "slow pan right, mystery atmosphere, dramatic shadows",
        "zoompan": "pan_right",
        "duracao": 8,
    },
    "relaxamento": {
        "prompt_motion": "slow zoom out, peaceful movement, soft light",
        "zoompan": "zoom_out",
        "duracao": 10,
    },
    "documentario": {
        "prompt_motion": "steady slow pan, documentary style, natural lighting",
        "zoompan": "pan_right",
        "duracao": 7,
    },
}

CANAL_PARA_NICHO = {
    "Mente de Aço":       "motivacional",
    "Esquina do Medo":    "terror",
    "Intelligentia Nova": "tech_ia",
    "Projeto Secreto":    "conspiracao",
    "AquaZen Relax":      "relaxamento",
    "Dark Nature":        "documentario",
    "Historia Sombria":   "documentario",
}


# ---------------------------------------------------------------------------
# 1. Wan 2.2 — Image to Video via HF Space
# ---------------------------------------------------------------------------

def imagem_para_video_wan(
    imagem_path: str,
    prompt: str = "cinematic camera movement, smooth motion, high quality video",
    duracao_frames: int = 81,          # 81 frames @ ~16fps ≈ 5s
    resolucao: str = "720p",
    seed: int = -1,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    hf_token: Optional[str] = None,
    timeout: int = 300,
) -> dict:
    """
    Converte imagem estática em vídeo com movimento via Wan 2.2 I2V.

    Args:
        imagem_path: Caminho local da imagem de entrada (FLUX thumbnail, foto etc.)
        prompt:  Descrição do movimento desejado em inglês
        duracao_frames: Número de frames (81 ≈ 5s, 121 ≈ 7.5s)
        resolucao: "480p" ou "720p"
        seed: -1 = aleatório
        output_dir: Diretório de saída
        hf_token: Token HuggingFace (opcional)
        timeout: Timeout em segundos (geração pode demorar 60-300s)

    Returns:
        dict com status, path do vídeo, metadata
    """
    if not GRADIO_AVAILABLE:
        return {"status": "failed", "error": "gradio_client não instalado. Execute: pip install gradio_client"}

    if not os.path.exists(imagem_path):
        return {"status": "failed", "error": f"Imagem não encontrada: {imagem_path}"}

    token = hf_token or os.environ.get("HF_TOKEN")
    kwargs = {}
    if token:
        kwargs["hf_token"] = token

    try:
        client = Client(WAN_I2V_SPACE, **kwargs)

        img_input = handle_file(imagem_path)

        result = client.predict(
            image=img_input,
            prompt=prompt,
            num_frames=duracao_frames,
            resolution=resolucao,
            seed=seed if seed >= 0 else None,
            api_name="/generate_video",
        )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        vid_id = str(uuid.uuid4())[:8]
        path_local = None

        if isinstance(result, str):
            if result.startswith("http"):
                import requests
                resp = requests.get(result, timeout=120)
                resp.raise_for_status()
                path_local = os.path.join(output_dir, f"wan_i2v_{vid_id}.mp4")
                with open(path_local, "wb") as f:
                    f.write(resp.content)
            else:
                ext = Path(result).suffix or ".mp4"
                path_local = os.path.join(output_dir, f"wan_i2v_{vid_id}{ext}")
                shutil.copy2(result, path_local)
        elif isinstance(result, (list, tuple)) and result:
            first = result[0]
            if isinstance(first, str):
                ext = Path(first).suffix or ".mp4"
                path_local = os.path.join(output_dir, f"wan_i2v_{vid_id}{ext}")
                if first.startswith("http"):
                    import requests
                    resp = requests.get(first, timeout=120)
                    resp.raise_for_status()
                    with open(path_local, "wb") as f:
                        f.write(resp.content)
                else:
                    shutil.copy2(first, path_local)
        elif hasattr(result, "get"):
            url_ou_path = result.get("video") or result.get("url") or result.get("path") or str(result)
            ext = ".mp4"
            path_local = os.path.join(output_dir, f"wan_i2v_{vid_id}{ext}")
            if url_ou_path.startswith("http"):
                import requests
                resp = requests.get(url_ou_path, timeout=120)
                with open(path_local, "wb") as f:
                    f.write(resp.content)
            else:
                shutil.copy2(url_ou_path, path_local)

        return {
            "status": "completed",
            "path": path_local,
            "imagem_entrada": imagem_path,
            "prompt": prompt,
            "modelo": "Wan2.2-I2V",
            "space": WAN_I2V_SPACE,
            "frames": duracao_frames,
            "resolucao": resolucao,
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "modelo": "Wan2.2-I2V",
            "fallback": "Use gerar_zoompan_ffmpeg() para animação local sem GPU",
        }


# ---------------------------------------------------------------------------
# 2. FFmpeg zoompan — Motion local sem GPU (fallback gratuito)
# ---------------------------------------------------------------------------

ZOOMPAN_EFFECTS = {
    "zoom_in": {
        "z": "min(zoom+0.0007,1.5)",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)",
        "desc": "Zoom suave para dentro — dramático, motivacional"
    },
    "zoom_out": {
        "z": "if(eq(on,1),1.5,max(zoom-0.0007,1))",
        "x": "iw/2-(iw/zoom/2)",
        "y": "ih/2-(ih/zoom/2)",
        "desc": "Zoom saindo — relaxante, revelação"
    },
    "pan_left": {
        "z": "1.2",
        "x": "if(gte(on,1),x+1,0)",
        "y": "ih/2-(ih/zoom/2)",
        "desc": "Panorâmica para esquerda — narrativa, documentário"
    },
    "pan_right": {
        "z": "1.2",
        "x": "if(gte(on,1),max(x-1,0),iw*(zoom-1)/zoom)",
        "y": "ih/2-(ih/zoom/2)",
        "desc": "Panorâmica para direita — suspense, conspiração"
    },
    "pan_up": {
        "z": "1.2",
        "x": "iw/2-(iw/zoom/2)",
        "y": "if(gte(on,1),y+0.8,ih*(zoom-1)/zoom)",
        "desc": "Pan para cima — revelação épica"
    },
    "pan_down": {
        "z": "1.2",
        "x": "iw/2-(iw/zoom/2)",
        "y": "if(gte(on,1),max(y-0.8,0),0)",
        "desc": "Pan para baixo — descida, terror"
    },
    "travelling": {
        "z": "min(zoom+0.0004,1.3)",
        "x": "iw/2-(iw/zoom/2)+sin(on/30)*5",
        "y": "ih/2-(ih/zoom/2)",
        "desc": "Travelling com leve oscilação — cinematográfico"
    },
    "kenburns": {
        "z": "if(lte(on,50),1+on*0.003,if(lte(on,100),1.15-on*0.001,1.05))",
        "x": "iw/2-(iw/zoom/2)+sin(on/80)*8",
        "y": "ih/2-(ih/zoom/2)+cos(on/120)*5",
        "desc": "Ken Burns clássico — documentário cinematográfico"
    },
}


def gerar_zoompan_ffmpeg(
    imagem_path: str,
    efeito: str = "zoom_in",
    duracao_s: float = 7.0,
    fps: int = 25,
    resolucao: str = "1080x1920",
    output_dir: str = DEFAULT_OUTPUT_DIR,
    audio_path: Optional[str] = None,
) -> dict:
    """
    Anima imagem estática com efeito de câmera via FFmpeg zoompan.
    Fallback gratuito e local — sem GPU, sem API.

    Args:
        imagem_path: Caminho da imagem de entrada
        efeito: Um dos keys de ZOOMPAN_EFFECTS ("zoom_in", "pan_left" etc.)
        duracao_s: Duração do vídeo em segundos
        fps: Frames por segundo
        resolucao: Resolução de saída (ex: "1080x1920" para Shorts)
        output_dir: Diretório de saída
        audio_path: Áudio opcional para sincronizar

    Returns:
        dict com status, path, metadata
    """
    if not os.path.exists(imagem_path):
        return {"status": "failed", "error": f"Imagem não encontrada: {imagem_path}"}

    effect = ZOOMPAN_EFFECTS.get(efeito, ZOOMPAN_EFFECTS["zoom_in"])
    w, h = resolucao.split("x")
    total_frames = int(duracao_s * fps)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    vid_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(output_dir, f"zoompan_{efeito}_{vid_id}.mp4")

    # Filtro zoompan + escala para resolução alvo
    zoompan_filter = (
        f"zoompan=z='{effect['z']}':"
        f"x='{effect['x']}':"
        f"y='{effect['y']}':"
        f"d={total_frames}:s={w}x{h}:fps={fps}"
    )
    scale_filter = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    vf = f"{scale_filter},{zoompan_filter}"

    # Monta comando
    if audio_path and os.path.exists(audio_path):
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", imagem_path,
            "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", imagem_path,
            "-vf", vf,
            "-t", str(duracao_s),
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-pix_fmt", "yuv420p",
            output_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        return {
            "status": "failed",
            "error": result.stderr[-600:],
            "cmd": " ".join(cmd[:8]) + " ...",
        }

    return {
        "status": "completed",
        "path": output_path,
        "efeito": efeito,
        "descricao": effect["desc"],
        "duracao_s": duracao_s,
        "fps": fps,
        "resolucao": resolucao,
        "com_audio": bool(audio_path),
        "modelo": "FFmpeg zoompan",
        "custo": "GRATUITO — local sem GPU",
        "ai_generated": True,
        "ai_disclosure": AI_DISCLOSURE,
    }


# ---------------------------------------------------------------------------
# 3. Pipeline B-roll: thumbnail FLUX → vídeo animado
# ---------------------------------------------------------------------------

def gerar_broll_de_thumbnail(
    imagem_path: str,
    canal: str = "",
    nicho: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    usar_wan: bool = True,
    hf_token: Optional[str] = None,
    duracao_s: float = 7.0,
    resolucao_short: str = "1080x1920",
) -> dict:
    """
    Pipeline completo: thumbnail → vídeo animado (B-roll).
    Tenta Wan 2.2 I2V primeiro; fallback para FFmpeg zoompan.

    Args:
        imagem_path: Thumbnail gerada pelo FLUX ou qualquer imagem
        canal: Nome do canal (para preset automático de movimento)
        nicho: Nicho explícito (sobrescreve detecção por canal)
        output_dir: Diretório de saída
        usar_wan: Tenta Wan 2.2 antes do fallback FFmpeg
        hf_token: Token HuggingFace
        duracao_s: Duração alvo em segundos (usado no fallback FFmpeg)
        resolucao_short: Resolução para Shorts (fallback FFmpeg)

    Returns:
        dict com status, path do vídeo, backend usado, metadata
    """
    nicho_det = nicho or CANAL_PARA_NICHO.get(canal, "documentario")
    preset = MOTION_PRESETS.get(nicho_det, MOTION_PRESETS["documentario"])

    # --- Wan 2.2 (preferencial quando GPU disponível no Space) ---
    if usar_wan and GRADIO_AVAILABLE:
        prompt_wan = (
            f"{preset['prompt_motion']}, "
            "smooth motion, high quality, cinematic, no text"
        )
        resultado = imagem_para_video_wan(
            imagem_path=imagem_path,
            prompt=prompt_wan,
            duracao_frames=preset.get("duracao", 7) * 16,  # ~16fps
            output_dir=output_dir,
            hf_token=hf_token,
        )
        if resultado["status"] == "completed":
            resultado["nicho"] = nicho_det
            resultado["preset_usado"] = preset
            resultado["pipeline"] = "thumbnail→wan_i2v"
            return resultado
        # Wan falhou → fallback
        resultado["wan_erro"] = resultado.get("error")

    # --- Fallback: FFmpeg zoompan (sempre disponível) ---
    efeito = preset.get("zoompan", "zoom_in")
    resultado_ffmpeg = gerar_zoompan_ffmpeg(
        imagem_path=imagem_path,
        efeito=efeito,
        duracao_s=duracao_s or preset.get("duracao", 7),
        resolucao=resolucao_short,
        output_dir=output_dir,
    )
    resultado_ffmpeg["nicho"] = nicho_det
    resultado_ffmpeg["preset_usado"] = preset
    resultado_ffmpeg["pipeline"] = "thumbnail→zoompan_ffmpeg"
    return resultado_ffmpeg


# ---------------------------------------------------------------------------
# 4. Geração de pack de B-roll para um Short inteiro
# ---------------------------------------------------------------------------

def gerar_pack_broll(
    imagens: list,
    canal: str = "",
    nicho: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    usar_wan: bool = False,  # False por padrão — Wan lento sem GPU dedicada
    hf_token: Optional[str] = None,
) -> dict:
    """
    Gera múltiplos clipes B-roll a partir de uma lista de imagens.
    Ideal para montar um Short com cenas variadas.

    Args:
        imagens: Lista de caminhos de imagens
        canal: Nome do canal para preset automático
        nicho: Nicho explícito
        output_dir: Diretório de saída
        usar_wan: Usar Wan 2.2 (mais lento mas melhor qualidade)
        hf_token: Token HuggingFace

    Returns:
        dict com lista de clips gerados e status de cada um
    """
    clips = []
    efeitos_ciclo = ["zoom_in", "pan_right", "pan_left", "zoom_out", "kenburns", "travelling"]

    for i, imagem in enumerate(imagens):
        efeito = efeitos_ciclo[i % len(efeitos_ciclo)]
        nicho_det = nicho or CANAL_PARA_NICHO.get(canal, "documentario")

        if usar_wan and GRADIO_AVAILABLE:
            preset = MOTION_PRESETS.get(nicho_det, MOTION_PRESETS["documentario"])
            r = imagem_para_video_wan(
                imagem_path=imagem,
                prompt=f"{preset['prompt_motion']}, cinematic, smooth, 4K",
                output_dir=output_dir,
                hf_token=hf_token,
            )
        else:
            r = gerar_zoompan_ffmpeg(
                imagem_path=imagem,
                efeito=efeito,
                duracao_s=5.0,
                output_dir=output_dir,
            )

        r["clip_index"] = i
        r["imagem_entrada"] = imagem
        clips.append(r)

    concluidos = sum(1 for c in clips if c.get("status") == "completed")

    return {
        "status": "completed" if concluidos > 0 else "failed",
        "clips": clips,
        "total": len(clips),
        "concluidos": concluidos,
        "canal": canal,
        "nicho": nicho or CANAL_PARA_NICHO.get(canal, "documentario"),
        "ai_generated": True,
        "ai_disclosure": AI_DISCLOSURE,
    }


# ---------------------------------------------------------------------------
# 5. Concatenar clips com FFmpeg
# ---------------------------------------------------------------------------

def concatenar_clips(
    clips_paths: list,
    output_path: str,
    adicionar_fade: bool = True,
) -> dict:
    """
    Concatena múltiplos clipes MP4 em um único vídeo via FFmpeg.
    Usa filter_complex concat com fade opcional entre clipes.

    Args:
        clips_paths: Lista de caminhos de vídeos MP4
        output_path: Caminho do vídeo final
        adicionar_fade: Adiciona fade in/out entre clipes

    Returns:
        dict com status e output_path
    """
    if not clips_paths:
        return {"status": "failed", "error": "Lista de clips vazia"}

    Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)

    if len(clips_paths) == 1:
        shutil.copy2(clips_paths[0], output_path)
        return {"status": "completed", "path": output_path, "clips": 1}

    # Cria arquivo de lista para concat demuxer
    list_path = output_path.replace(".mp4", "_list.txt")
    with open(list_path, "w") as f:
        for p in clips_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    # Limpa arquivo temporário
    try:
        os.remove(list_path)
    except Exception:
        pass

    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "path": output_path if result.returncode == 0 else None,
        "clips_concatenados": len(clips_paths),
        "error": result.stderr[-400:] if result.returncode != 0 else None,
    }


# ---------------------------------------------------------------------------
# 6. Status e diagnóstico
# ---------------------------------------------------------------------------

def status_wan_client() -> dict:
    """Retorna status das dependências e capabilities disponíveis."""
    # Verifica FFmpeg
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        ffmpeg_ok = r.returncode == 0
        ffmpeg_ver = r.stdout.split("\n")[0] if ffmpeg_ok else "não encontrado"
    except Exception:
        ffmpeg_ok = False
        ffmpeg_ver = "não encontrado"

    return {
        "gradio_client": GRADIO_AVAILABLE,
        "pillow": PIL_AVAILABLE,
        "ffmpeg": ffmpeg_ok,
        "ffmpeg_version": ffmpeg_ver,
        "spaces": {
            "wan_i2v": WAN_I2V_SPACE,
            "wan_t2v": WAN_T2V_SPACE,
        },
        "efeitos_disponiveis": list(ZOOMPAN_EFFECTS.keys()),
        "motion_presets": list(MOTION_PRESETS.keys()),
        "capacidades": [
            "imagem_para_video (Wan 2.2 I2V — HF Space)",
            "zoompan_ffmpeg (zoom_in, zoom_out, pan, kenburns, travelling)",
            "broll_de_thumbnail (pipeline automático com preset por canal)",
            "pack_broll (múltiplos clips para um Short)",
            "concatenar_clips (montagem final FFmpeg)",
        ],
        "custo": "GRATUITO — HF Space (Wan I2V) + FFmpeg local",
        "hf_token_presente": bool(os.environ.get("HF_TOKEN")),
        "ai_disclosure": AI_DISCLOSURE,
    }
