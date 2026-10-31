"""
DARK VIDEO STUDIO — Geração de Vídeos Realistas PT-BR
Backends: local (CogVideoX / Wan 2.1) → API (Replicate / Runway / Kling) → FFmpeg fallback

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import os
import json
import shutil
import subprocess
import time
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────

MODELS_DIR = Path(__file__).parent.parent / "assets" / "models" / "video"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "_video_studio"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

# Backends disponíveis (verificados em check_backends())
BACKEND_PRIORITY = [
    "cogvideox_local",   # CogVideoX 5B local (requer GPU 24GB+)
    "wan_local",         # Wan 2.1 local (requer GPU 16GB+)
    "replicate_api",     # Replicate.com (pago, ~$0.02/seg)
    "runway_api",        # Runway Gen-4 (pago, ~$0.05/seg)
    "kling_api",         # Kling AI (pago, ~$0.03/seg)
    "ffmpeg_fallback",   # Slideshow animado via FFmpeg (gratuito, sempre disponível)
]

# Presets cinematográficos
PRESETS = {
    "documentario": {
        "fps": 24,
        "motion": "slow_pan",
        "color_grade": "warm_documentary",
        "duration": 4.0,
        "aspect": "16:9",
    },
    "natureza": {
        "fps": 24,
        "motion": "slow_zoom_in",
        "color_grade": "natural_vivid",
        "duration": 4.0,
        "aspect": "16:9",
    },
    "historia": {
        "fps": 24,
        "motion": "ken_burns",
        "color_grade": "vintage_sepia",
        "duration": 5.0,
        "aspect": "16:9",
    },
    "tecnologia": {
        "fps": 30,
        "motion": "zoom_out",
        "color_grade": "cool_blue",
        "duration": 3.0,
        "aspect": "16:9",
    },
    "misterio": {
        "fps": 24,
        "motion": "slow_push",
        "color_grade": "dark_moody",
        "duration": 5.0,
        "aspect": "16:9",
    },
    "shorts": {
        "fps": 30,
        "motion": "dynamic",
        "color_grade": "vibrant",
        "duration": 3.0,
        "aspect": "9:16",
    },
}


# ─────────────────────────────────────────────
# DIAGNÓSTICO DE BACKENDS
# ─────────────────────────────────────────────

def check_backends() -> Dict[str, Any]:
    """Verifica quais backends de geração de vídeo estão disponíveis."""
    status = {}

    # 1. CogVideoX local
    try:
        import torch
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0
        status["cogvideox_local"] = {
            "available": vram_gb >= 20,
            "vram_gb": round(vram_gb, 1),
            "note": "Requer 24GB VRAM" if vram_gb < 20 else "✅ GPU compatível",
        }
    except Exception:
        status["cogvideox_local"] = {"available": False, "note": "torch não instalado"}

    # 2. Wan 2.1 local
    wan_model = MODELS_DIR / "wan2.1"
    status["wan_local"] = {
        "available": wan_model.exists(),
        "note": "✅ Modelo presente" if wan_model.exists() else f"Modelo ausente em {wan_model}",
    }

    # 3. Replicate API
    replicate_key = os.environ.get("REPLICATE_API_TOKEN", "")
    status["replicate_api"] = {
        "available": bool(replicate_key),
        "note": "✅ Token configurado" if replicate_key else "Defina REPLICATE_API_TOKEN",
        "cost_per_sec": 0.02,
    }

    # 4. Runway API
    runway_key = os.environ.get("RUNWAYML_API_SECRET", "")
    status["runway_api"] = {
        "available": bool(runway_key),
        "note": "✅ Token configurado" if runway_key else "Defina RUNWAYML_API_SECRET",
        "cost_per_sec": 0.05,
    }

    # 5. Kling API
    kling_key = os.environ.get("KLING_API_KEY", "")
    status["kling_api"] = {
        "available": bool(kling_key),
        "note": "✅ Token configurado" if kling_key else "Defina KLING_API_KEY",
        "cost_per_sec": 0.03,
    }

    # 6. FFmpeg fallback (sempre disponível)
    status["ffmpeg_fallback"] = {
        "available": bool(shutil.which("ffmpeg")),
        "note": "✅ Slideshow animado (Ken Burns effect)",
        "cost_per_sec": 0.0,
    }

    return status


def best_backend(status: Dict) -> str:
    """Retorna o melhor backend disponível."""
    for backend in BACKEND_PRIORITY:
        if status.get(backend, {}).get("available"):
            return backend
    return "ffmpeg_fallback"


# ─────────────────────────────────────────────
# ENGINE 1: COGVIDEOX LOCAL
# ─────────────────────────────────────────────

def _generate_cogvideox(
    prompt: str,
    output_path: Path,
    duration: float = 4.0,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
) -> bool:
    """Gera vídeo com CogVideoX 5B local."""
    try:
        import torch
        from diffusers import CogVideoXPipeline

        model_id = "THUDM/CogVideoX-5b"
        pipe = CogVideoXPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
        pipe.enable_model_cpu_offload()

        n_frames = int(duration * fps)
        video = pipe(
            prompt=prompt,
            num_videos_per_prompt=1,
            num_inference_steps=50,
            num_frames=n_frames,
            guidance_scale=6,
            generator=torch.Generator(device="cuda").manual_seed(42),
        ).frames[0]

        from diffusers.utils import export_to_video
        export_to_video(video, str(output_path), fps=fps)
        return output_path.exists()

    except Exception as e:
        print(f"[VIDEO] CogVideoX falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 2: WAN 2.1 LOCAL
# ─────────────────────────────────────────────

def _generate_wan(
    prompt: str,
    output_path: Path,
    image_path: Optional[Path] = None,
    duration: float = 4.0,
    fps: int = 24,
) -> bool:
    """Gera vídeo com Wan 2.1 local."""
    try:
        wan_model = MODELS_DIR / "wan2.1"
        if not wan_model.exists():
            return False

        # Wan 2.1 via wan-video CLI (quando instalado)
        cmd = [
            "wan-video",
            "--model", str(wan_model),
            "--prompt", prompt,
            "--output", str(output_path),
            "--duration", str(duration),
            "--fps", str(fps),
        ]
        if image_path and image_path.exists():
            cmd += ["--image", str(image_path)]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=300)
        return result.returncode == 0 and output_path.exists()

    except Exception as e:
        print(f"[VIDEO] Wan 2.1 falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 3: REPLICATE API
# ─────────────────────────────────────────────

def _generate_replicate(
    prompt: str,
    output_path: Path,
    model: str = "minimax/video-01",
    duration: float = 4.0,
    aspect: str = "16:9",
) -> bool:
    """Gera vídeo via Replicate API."""
    try:
        import replicate

        output = replicate.run(
            model,
            input={
                "prompt": prompt,
                "duration": int(duration),
                "aspect_ratio": aspect,
            },
        )

        # Salva o vídeo retornado
        if hasattr(output, "read"):
            output_path.write_bytes(output.read())
        elif isinstance(output, str) and output.startswith("http"):
            import urllib.request
            urllib.request.urlretrieve(output, str(output_path))
        else:
            return False

        return output_path.exists() and output_path.stat().st_size > 1000

    except Exception as e:
        print(f"[VIDEO] Replicate falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 4: RUNWAY API
# ─────────────────────────────────────────────

def _generate_runway(
    prompt: str,
    output_path: Path,
    image_path: Optional[Path] = None,
    duration: int = 5,
    ratio: str = "1280:720",
) -> bool:
    """Gera vídeo via RunwayML Gen-4 API."""
    try:
        import runwayml

        client = runwayml.RunwayML()

        kwargs = {
            "model": "gen4_turbo",
            "prompt_text": prompt,
            "ratio": ratio,
            "duration": duration,
        }

        if image_path and image_path.exists():
            import base64
            img_data = base64.b64encode(image_path.read_bytes()).decode()
            ext = image_path.suffix.lstrip(".")
            kwargs["prompt_image"] = f"data:image/{ext};base64,{img_data}"

        task = client.image_to_video.create(**kwargs)
        task_id = task.id

        # Aguarda conclusão (polling)
        for _ in range(60):
            time.sleep(5)
            task = client.tasks.retrieve(task_id)
            if task.status in ("SUCCEEDED", "FAILED"):
                break

        if task.status != "SUCCEEDED":
            return False

        import urllib.request
        urllib.request.urlretrieve(task.output[0], str(output_path))
        return output_path.exists()

    except Exception as e:
        print(f"[VIDEO] Runway falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 5: KLING API
# ─────────────────────────────────────────────

def _generate_kling(
    prompt: str,
    output_path: Path,
    image_path: Optional[Path] = None,
    duration: float = 5.0,
    aspect: str = "16:9",
    mode: str = "std",
) -> bool:
    """Gera vídeo via Kling AI API."""
    try:
        import jwt
        import requests

        api_key = os.environ.get("KLING_API_KEY", "")
        api_secret = os.environ.get("KLING_API_SECRET", "")
        if not api_key or not api_secret:
            return False

        # JWT auth
        payload = {"iss": api_key, "exp": int(time.time()) + 1800, "nbf": int(time.time()) - 5}
        token = jwt.encode(payload, api_secret, algorithm="HS256")

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        base_url = "https://api.klingai.com/v1"

        data: Dict[str, Any] = {
            "prompt": prompt,
            "mode": mode,
            "aspect_ratio": aspect,
            "duration": str(int(duration)),
        }

        if image_path and image_path.exists():
            import base64
            img_b64 = base64.b64encode(image_path.read_bytes()).decode()
            data["image"] = img_b64
            endpoint = f"{base_url}/videos/image2video"
        else:
            endpoint = f"{base_url}/videos/text2video"

        resp = requests.post(endpoint, json=data, headers=headers, timeout=30)
        if resp.status_code != 200:
            return False

        task_id = resp.json().get("data", {}).get("task_id")
        if not task_id:
            return False

        # Polling
        for _ in range(60):
            time.sleep(5)
            r = requests.get(f"{base_url}/videos/text2video/{task_id}", headers=headers, timeout=10)
            status = r.json().get("data", {}).get("task_status", "")
            if status == "succeed":
                video_url = r.json()["data"]["task_result"]["videos"][0]["url"]
                import urllib.request
                urllib.request.urlretrieve(video_url, str(output_path))
                return output_path.exists()
            if status == "failed":
                return False

        return False

    except Exception as e:
        print(f"[VIDEO] Kling falhou: {e}")
        return False


# ─────────────────────────────────────────────
# ENGINE 6: FFMPEG FALLBACK (Ken Burns / Slideshow)
# ─────────────────────────────────────────────

def _generate_ffmpeg_fallback(
    prompt: str,
    output_path: Path,
    image_path: Optional[Path] = None,
    duration: float = 4.0,
    fps: int = 24,
    motion: str = "slow_zoom_in",
    width: int = 1280,
    height: int = 720,
    color_grade: str = "documentario",
) -> bool:
    """
    Gera vídeo animado via FFmpeg com efeito Ken Burns ou movimento de câmera.
    Sempre disponível — não requer GPU ou API externa.
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if image_path and image_path.exists():
            src = str(image_path)
        else:
            # Gera frame placeholder com texto do prompt
            src = _create_placeholder_frame(prompt, width, height)

        n_frames = int(duration * fps)

        # Monta filtro de movimento
        motion_filter = _build_motion_filter(motion, width, height, n_frames)

        # Color grade
        grade_filter = _build_color_grade(color_grade)

        full_filter = f"{motion_filter},{grade_filter}" if grade_filter else motion_filter

        cmd = [
            FFMPEG, "-y",
            "-loop", "1",
            "-i", src,
            "-vf", full_filter,
            "-t", str(duration),
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(output_path),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
        return result.returncode == 0 and output_path.exists()

    except Exception as e:
        print(f"[VIDEO] FFmpeg fallback falhou: {e}")
        return False


def _create_placeholder_frame(text: str, width: int = 1280, height: int = 720) -> str:
    """Cria frame PNG com texto do prompt usando Pillow."""
    tmp = tempfile.mktemp(suffix=".png")
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (width, height), color=(10, 10, 20))
        draw = ImageDraw.Draw(img)

        # Gradiente simples
        for y in range(height):
            alpha = y / height
            r = int(10 + 20 * alpha)
            g = int(10 + 15 * alpha)
            b = int(20 + 40 * alpha)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Texto
        words = text.split()
        lines, line = [], []
        for word in words:
            if len(" ".join(line + [word])) < 60:
                line.append(word)
            else:
                lines.append(" ".join(line))
                line = [word]
        if line:
            lines.append(" ".join(line))

        y0 = height // 2 - len(lines) * 20
        for i, ln in enumerate(lines[:6]):
            draw.text((width // 2, y0 + i * 40), ln, fill=(200, 200, 220), anchor="mm")

        img.save(tmp)
    except Exception:
        # Fallback: frame preto via FFmpeg
        subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", f"color=black:s={width}x{height}",
                        "-frames:v", "1", tmp], capture_output=True)
    return tmp


def _build_motion_filter(motion: str, w: int, h: int, n_frames: int) -> str:
    """Constrói filtro FFmpeg para movimento de câmera."""
    # Zoom inicial 10% extra para espaço de crop
    zw, zh = int(w * 1.1), int(h * 1.1)
    base = f"scale={zw}:{zh},zoompan=z='zoom':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={w}x{h}:fps=24"

    motions = {
        "slow_zoom_in": f"scale={zw}:{zh},zoompan=z='min(zoom+0.001,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={w}x{h}:fps=24",
        "zoom_out":     f"scale={zw}:{zh},zoompan=z='max(zoom-0.001,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={w}x{h}:fps=24",
        "slow_pan":     f"scale={zw}:{zh},zoompan=z='1.05':x='on/{n_frames}*({zw}-{w})':y='ih/2-(ih/zoom/2)':d={n_frames}:s={w}x{h}:fps=24",
        "ken_burns":    f"scale={zw}:{zh},zoompan=z='min(zoom+0.0008,1.4)':x='on/{n_frames}*({zw}-{w})':y='on/{n_frames}*({zh}-{h})':d={n_frames}:s={w}x{h}:fps=24",
        "slow_push":    f"scale={zw}:{zh},zoompan=z='min(zoom+0.0015,1.6)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n_frames}:s={w}x{h}:fps=24",
        "dynamic":      f"scale={zw}:{zh},zoompan=z='min(zoom+0.002,1.3)':x='iw/2-(iw/zoom/2)':y='on/{n_frames}*({zh}-{h})':d={n_frames}:s={w}x{h}:fps=24",
        "static":       f"scale={w}:{h}",
    }
    return motions.get(motion, base)


def _build_color_grade(style: str) -> str:
    """Constrói filtro de color grade FFmpeg."""
    grades = {
        "warm_documentary": "eq=contrast=1.1:brightness=0.02:saturation=0.9,colorbalance=rs=0.05:gs=0:bs=-0.05",
        "natural_vivid":    "eq=contrast=1.05:brightness=0.02:saturation=1.3",
        "vintage_sepia":    "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0,eq=saturation=0.3:contrast=1.1",
        "cool_blue":        "eq=contrast=1.1:saturation=0.8,colorbalance=rs=-0.05:gs=0:bs=0.1",
        "dark_moody":       "eq=contrast=1.3:brightness=-0.05:saturation=0.7,vignette=PI/4",
        "vibrant":          "eq=contrast=1.1:saturation=1.4:brightness=0.03",
        "documentario":     "eq=contrast=1.05:brightness=0.01:saturation=0.95",
    }
    return grades.get(style, "")


# ─────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────

def generate_video(
    prompt: str,
    output_path: Path,
    image_path: Optional[Path] = None,
    preset: str = "documentario",
    backend: Optional[str] = None,
    duration: Optional[float] = None,
    width: int = 1280,
    height: int = 720,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Gera vídeo a partir de texto e/ou imagem usando o melhor backend disponível.

    Args:
        prompt:      Descrição do vídeo em PT-BR (traduzida automaticamente se necessário).
        output_path: Caminho do arquivo MP4 de saída.
        image_path:  Imagem base opcional (img2video).
        preset:      Estilo cinematográfico (documentario, natureza, historia, etc.).
        backend:     Forçar backend específico (None = automático).
        duration:    Duração em segundos (None = usa preset).
        verbose:     Exibe progresso.

    Returns:
        dict com status, backend_used, output_path, duration, cost_estimate.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cfg = PRESETS.get(preset, PRESETS["documentario"])
    dur = duration or cfg["duration"]
    motion = cfg.get("motion", "slow_zoom_in")
    color_grade = cfg.get("color_grade", "documentario")
    fps = cfg.get("fps", 24)

    # Ajusta resolução para Shorts (9:16)
    if cfg.get("aspect") == "9:16":
        width, height = 720, 1280

    # Detecta backends disponíveis
    status = check_backends()

    if backend:
        chosen = backend
    else:
        chosen = best_backend(status)

    if verbose:
        print(f"[VIDEO] Backend: {chosen} | preset: {preset} | {dur:.0f}s | {width}x{height}")

    success = False
    t0 = time.time()

    if chosen == "cogvideox_local":
        success = _generate_cogvideox(prompt, output_path, dur, fps, width, height)

    elif chosen == "wan_local":
        success = _generate_wan(prompt, output_path, image_path, dur, fps)

    elif chosen == "replicate_api":
        aspect = "16:9" if width > height else "9:16"
        success = _generate_replicate(prompt, output_path, duration=dur, aspect=aspect)

    elif chosen == "runway_api":
        ratio = f"{width}:{height}"
        success = _generate_runway(prompt, output_path, image_path, int(dur), ratio)

    elif chosen == "kling_api":
        aspect = "16:9" if width > height else "9:16"
        success = _generate_kling(prompt, output_path, image_path, dur, aspect)

    # Fallback para FFmpeg se backend principal falhou
    if not success:
        if verbose and chosen != "ffmpeg_fallback":
            print(f"[VIDEO] {chosen} falhou → usando FFmpeg fallback")
        success = _generate_ffmpeg_fallback(
            prompt, output_path, image_path, dur, fps, motion, width, height, color_grade
        )
        chosen = "ffmpeg_fallback"

    elapsed = time.time() - t0

    # Calcula custo estimado
    cost_info = status.get(chosen, {})
    cost_estimate = cost_info.get("cost_per_sec", 0.0) * dur

    result = {
        "status": "ok" if success else "error",
        "backend_used": chosen,
        "output_path": str(output_path) if success else None,
        "duration_requested": dur,
        "elapsed_s": round(elapsed, 1),
        "cost_estimate_usd": round(cost_estimate, 4),
        "preset": preset,
        "width": width,
        "height": height,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    if verbose:
        icon = "✅" if success else "❌"
        print(f"[VIDEO] {icon} {chosen} → {output_path.name} ({elapsed:.1f}s | ~${cost_estimate:.4f})")

    return result


def generate_scene_videos(
    cenas: list,
    output_dir: Path,
    preset: str = "documentario",
    image_paths: Optional[list] = None,
    verbose: bool = True,
) -> list:
    """
    Gera vídeo para cada cena de um roteiro.

    Args:
        cenas:       Lista de dicts com 'prompt_visual' (ou 'descricao').
        output_dir:  Pasta de saída.
        preset:      Preset cinematográfico.
        image_paths: Lista de imagens opcionais (None para geração text2video).

    Returns:
        Lista de Paths dos vídeos gerados (None para cenas sem prompt).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, cena in enumerate(cenas, 1):
        prompt = cena.get("prompt_visual") or cena.get("descricao") or cena.get("texto", "")
        if not prompt.strip():
            results.append(None)
            continue

        img = None
        if image_paths and i <= len(image_paths) and image_paths[i - 1]:
            img = Path(image_paths[i - 1])

        out_path = output_dir / f"cena_{i:02d}.mp4"
        result = generate_video(prompt, out_path, image_path=img, preset=preset, verbose=verbose)

        results.append(out_path if result["status"] == "ok" else None)

    return results


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=== DARK VIDEO STUDIO — Backend Check ===")
    backends = check_backends()
    for name, info in backends.items():
        icon = "✅" if info.get("available") else "❌"
        note = info.get("note", "")
        cost = f"~${info.get('cost_per_sec', 0):.2f}/s" if info.get("cost_per_sec") else "gratuito"
        print(f"  {icon} {name:25s} {note} [{cost}]")

    print()
    chosen = best_backend(backends)
    print(f"  → Backend ativo: {chosen}")

    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        preset = sys.argv[2] if len(sys.argv) > 2 else "documentario"
        out = Path("/tmp/test_video.mp4")
        print(f"\nGerando vídeo de teste: '{prompt[:50]}...' [{preset}]")
        result = generate_video(prompt, out, preset=preset)
        print(f"\nResultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
