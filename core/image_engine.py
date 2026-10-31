"""
DARK CREATIVE LAB — AGENTE IMAGE ENGINE
Geração, edição, tratamento e otimização de imagens.

Funcionalidades:
- Texto para imagem (via Stable Diffusion local / HuggingFace API / placeholder)
- Imagem para imagem (variações e edições)
- Upscaling (ESRGAN via OpenCV / PIL)
- Remoção de fundo (rembg / OpenCV)
- Correção de cores e iluminação (Pillow)
- Thumbnails e capas YouTube (Pillow + templates)
- Redimensionamento automático
- Geração de imagens fotorrealistas (presets)

Stack preferencial (open source, sem custo):
1. Stable Diffusion via diffusers (local, GPU)
2. HuggingFace Inference API (gratuito com limite)
3. Placeholder gerado com Pillow (fallback offline)

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import time
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────

RESOLUCOES = {
    "youtube_thumbnail": (1280, 720),
    "youtube_banner":    (2560, 1440),
    "square":            (1024, 1024),
    "portrait":          (768, 1344),
    "landscape":         (1344, 768),
    "shorts":            (1080, 1920),
    "wallpaper_hd":      (1920, 1080),
    "wallpaper_4k":      (3840, 2160),
    "instagram_post":    (1080, 1080),
    "instagram_story":   (1080, 1920),
}

ESTILOS_PROMPT = {
    "cinematografico":  "cinematic photography, dramatic lighting, 8k uhd, film grain, anamorphic lens",
    "fotorrealista":    "photorealistic, hyperrealistic, ultra detailed, professional photography, DSLR",
    "natureza":         "nature photography, wildlife, golden hour, national geographic style, vivid colors",
    "urbano":           "urban photography, street photography, city lights, architectural details",
    "historico":        "historical documentary, vintage photography, sepia tones, archival quality",
    "dark_channel":     "dramatic dark atmosphere, noir style, high contrast, mysterious, cinematic",
    "stickman":         "stickman animation style, clean lines, minimalist, black on white background",
    "thumbnail_yt":     "youtube thumbnail style, bold colors, high contrast, eye-catching, text space",
}

NEGATIVOS_PADRAO = (
    "blurry, low quality, watermark, text, logo, signature, "
    "deformed, ugly, bad anatomy, extra limbs, cloned face"
)

_HF_TOKEN = os.getenv("HF_TOKEN", "")
_SD_MODEL_ID = os.getenv("SD_MODEL_ID", "stabilityai/stable-diffusion-xl-base-1.0")


# ─────────────────────────────────────────────────────────────────
#  GERADOR DE PLACEHOLDER (offline — sem GPU)
# ─────────────────────────────────────────────────────────────────

def _gerar_placeholder(
    prompt: str,
    largura: int = 1280,
    altura: int = 720,
    output_path: Path = None,
) -> Path:
    """Gera imagem placeholder com Pillow quando SD não está disponível."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise RuntimeError("Pillow não instalado: pip install Pillow")

    # Cor baseada no hash do prompt (estética consistente)
    h = hashlib.md5(prompt.encode()).hexdigest()
    r = int(h[0:2], 16) // 2  # tons escuros para estética dark
    g = int(h[2:4], 16) // 2
    b = int(h[4:6], 16) // 2 + 30

    img = Image.new("RGB", (largura, altura), color=(r, g, b))
    draw = ImageDraw.Draw(img)

    # Gradiente simples — barra superior mais clara
    for y in range(altura // 4):
        alpha = 1 - (y / (altura // 4))
        overlay_r = min(255, r + int(60 * alpha))
        overlay_g = min(255, g + int(60 * alpha))
        overlay_b = min(255, b + int(60 * alpha))
        draw.line([(0, y), (largura, y)], fill=(overlay_r, overlay_g, overlay_b))

    # Texto do prompt truncado
    max_chars = 60
    texto = prompt[:max_chars] + ("..." if len(prompt) > max_chars else "")
    label = f"DARK IMAGE ENGINE\n{texto}"

    try:
        font_size = max(16, largura // 40)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Sombra do texto
    x, y = largura // 20, altura // 2 - 40
    draw.text((x + 2, y + 2), label, fill=(0, 0, 0), font=font)
    draw.text((x, y), label, fill=(255, 255, 255), font=font)

    # Marca d'água AI
    marca = "⚡ DARK STUDIO AAA | AI Generated"
    draw.text((largura // 20, altura - 40), marca, fill=(200, 200, 200), font=font)

    if output_path is None:
        output_path = Path("/tmp") / f"dark_img_{h[:8]}.png"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", optimize=True)
    return output_path


# ─────────────────────────────────────────────────────────────────
#  GERADOR VIA HUGGINGFACE INFERENCE API
# ─────────────────────────────────────────────────────────────────

def _gerar_via_hf_api(
    prompt: str,
    modelo: str = "stabilityai/stable-diffusion-xl-base-1.0",
    largura: int = 1024,
    altura: int = 1024,
    output_path: Path = None,
    token: str = "",
) -> Optional[Path]:
    """Usa HuggingFace Inference API (gratuito com HF_TOKEN)."""
    try:
        import requests
    except ImportError:
        return None

    if not token:
        return None

    url = f"https://api-inference.huggingface.co/models/{modelo}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": NEGATIVOS_PADRAO,
            "width": min(largura, 1024),
            "height": min(altura, 1024),
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
            from PIL import Image
            img = Image.open(io.BytesIO(resp.content))

            if output_path is None:
                h = hashlib.md5(prompt.encode()).hexdigest()[:8]
                output_path = Path("/tmp") / f"dark_hf_{h}.png"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(output_path), "PNG")
            return output_path
    except Exception as e:
        print(f"[IMAGE_ENGINE] HF API falhou: {e}")

    return None


# ─────────────────────────────────────────────────────────────────
#  GERADOR VIA DIFFUSERS LOCAL (requer GPU + torch)
# ─────────────────────────────────────────────────────────────────

def _gerar_local_sd(
    prompt: str,
    model_id: str = _SD_MODEL_ID,
    largura: int = 1024,
    altura: int = 1024,
    steps: int = 30,
    output_path: Path = None,
) -> Optional[Path]:
    """Gera imagem com Stable Diffusion local via diffusers."""
    try:
        import torch
        from diffusers import StableDiffusionXLPipeline
    except ImportError:
        return None

    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            print("[IMAGE_ENGINE] AVISO: GPU não disponível. SD local será muito lento.")

        pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
        ).to(device)

        resultado = pipe(
            prompt=prompt,
            negative_prompt=NEGATIVOS_PADRAO,
            width=largura,
            height=altura,
            num_inference_steps=steps,
            guidance_scale=7.5,
        )
        img = resultado.images[0]

        if output_path is None:
            h = hashlib.md5(prompt.encode()).hexdigest()[:8]
            output_path = Path("/tmp") / f"dark_sd_{h}.png"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG")
        return output_path

    except Exception as e:
        print(f"[IMAGE_ENGINE] SD local falhou: {e}")
        return None


# ─────────────────────────────────────────────────────────────────
#  FUNÇÃO PRINCIPAL: TEXTO PARA IMAGEM
# ─────────────────────────────────────────────────────────────────

def gerar_imagem(
    prompt: str,
    estilo: str = "cinematografico",
    resolucao: str = "youtube_thumbnail",
    output_path: Path = None,
    engine: str = "auto",  # auto, local, hf_api, placeholder
    steps: int = 30,
) -> dict:
    """
    Gera imagem a partir de texto.

    Args:
        prompt: Descrição textual da imagem.
        estilo: Preset de estilo (ver ESTILOS_PROMPT).
        resolucao: Preset de resolução (ver RESOLUCOES).
        output_path: Caminho de saída (opcional).
        engine: Motor a usar — auto escolhe o melhor disponível.
        steps: Passos de inferência (para SD).

    Returns:
        Dict com status, caminho da imagem, engine usada.
    """
    t0 = time.time()

    # Resolve resolução
    res = RESOLUCOES.get(resolucao, (1280, 720))
    largura, altura = res

    # Enriquece o prompt com o estilo
    sufixo = ESTILOS_PROMPT.get(estilo, "")
    prompt_completo = f"{prompt}, {sufixo}".strip(", ")

    # Determina engine
    img_path = None

    if engine in ("auto", "local"):
        img_path = _gerar_local_sd(prompt_completo, largura=largura, altura=altura,
                                   steps=steps, output_path=output_path)
        if img_path:
            engine_usada = "stable_diffusion_local"

    if img_path is None and engine in ("auto", "hf_api") and _HF_TOKEN:
        img_path = _gerar_via_hf_api(prompt_completo, largura=largura, altura=altura,
                                     output_path=output_path, token=_HF_TOKEN)
        if img_path:
            engine_usada = "huggingface_api"

    if img_path is None:
        img_path = _gerar_placeholder(prompt_completo, largura=largura, altura=altura,
                                      output_path=output_path)
        engine_usada = "placeholder_pillow"

    duracao = round(time.time() - t0, 2)

    return {
        "status": "ok",
        "caminho": str(img_path),
        "prompt": prompt,
        "prompt_completo": prompt_completo,
        "estilo": estilo,
        "resolucao": resolucao,
        "largura": largura,
        "altura": altura,
        "engine": engine_usada,
        "duracao_s": duracao,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  UPSCALING
# ─────────────────────────────────────────────────────────────────

def upscalar_imagem(
    input_path: Path,
    fator: int = 2,
    output_path: Path = None,
) -> dict:
    """Aumenta resolução da imagem via interpolação Lanczos (sem GPU)."""
    try:
        from PIL import Image
    except ImportError:
        return {"status": "error", "erro": "Pillow não instalado"}

    input_path = Path(input_path)
    if not input_path.exists():
        return {"status": "error", "erro": f"Arquivo não encontrado: {input_path}"}

    img = Image.open(str(input_path))
    nova_largura = img.width * fator
    nova_altura = img.height * fator

    img_upscaled = img.resize((nova_largura, nova_altura), Image.LANCZOS)

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_x{fator}{input_path.suffix}"

    output_path = Path(output_path)
    img_upscaled.save(str(output_path))

    return {
        "status": "ok",
        "caminho": str(output_path),
        "resolucao_original": f"{img.width}x{img.height}",
        "resolucao_final": f"{nova_largura}x{nova_altura}",
        "fator": fator,
        "ai_generated": True,
    }


# ─────────────────────────────────────────────────────────────────
#  REMOÇÃO DE FUNDO
# ─────────────────────────────────────────────────────────────────

def remover_fundo(
    input_path: Path,
    output_path: Path = None,
) -> dict:
    """Remove fundo da imagem. Usa rembg se disponível, senão método simples."""
    input_path = Path(input_path)
    if not input_path.exists():
        return {"status": "error", "erro": f"Arquivo não encontrado: {input_path}"}

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_nobg.png"
    output_path = Path(output_path)

    # Tenta rembg (melhor qualidade)
    try:
        from rembg import remove
        from PIL import Image

        with open(str(input_path), "rb") as f:
            img_bytes = f.read()

        resultado = remove(img_bytes)
        img = Image.open(io.BytesIO(resultado))
        img.save(str(output_path), "PNG")

        return {
            "status": "ok",
            "caminho": str(output_path),
            "metodo": "rembg",
            "ai_generated": True,
        }
    except ImportError:
        pass
    except Exception as e:
        print(f"[IMAGE_ENGINE] rembg falhou: {e}")

    # Fallback: OpenCV GrabCut simples
    try:
        import cv2
        import numpy as np
        from PIL import Image

        img_cv = cv2.imread(str(input_path))
        mascara = np.zeros(img_cv.shape[:2], np.uint8)
        rect = (10, 10, img_cv.shape[1] - 10, img_cv.shape[0] - 10)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(img_cv, mascara, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mascara2 = np.where((mascara == 2) | (mascara == 0), 0, 1).astype("uint8")
        img_result = img_cv * mascara2[:, :, np.newaxis]

        # Converte para RGBA
        img_pil = Image.fromarray(cv2.cvtColor(img_result, cv2.COLOR_BGR2RGBA))
        alpha = Image.fromarray(mascara2 * 255)
        img_pil.putalpha(alpha)
        img_pil.save(str(output_path), "PNG")

        return {
            "status": "ok",
            "caminho": str(output_path),
            "metodo": "opencv_grabcut",
            "nota": "Qualidade limitada — instale rembg para melhor resultado",
            "ai_generated": True,
        }
    except Exception as e:
        return {"status": "error", "erro": f"Remoção de fundo falhou: {e}"}


# ─────────────────────────────────────────────────────────────────
#  CORREÇÃO DE CORES E ILUMINAÇÃO
# ─────────────────────────────────────────────────────────────────

def corrigir_imagem(
    input_path: Path,
    brilho: float = 1.0,
    contraste: float = 1.0,
    saturacao: float = 1.0,
    nitidez: float = 1.0,
    output_path: Path = None,
) -> dict:
    """Aplica correções de cor e iluminação com Pillow."""
    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        return {"status": "error", "erro": "Pillow não instalado"}

    input_path = Path(input_path)
    if not input_path.exists():
        return {"status": "error", "erro": f"Arquivo não encontrado: {input_path}"}

    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_corrigido{input_path.suffix}"
    output_path = Path(output_path)

    img = Image.open(str(input_path))

    if brilho != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brilho)
    if contraste != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contraste)
    if saturacao != 1.0:
        img = ImageEnhance.Color(img).enhance(saturacao)
    if nitidez != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(nitidez)

    img.save(str(output_path))

    return {
        "status": "ok",
        "caminho": str(output_path),
        "ajustes": {
            "brilho": brilho,
            "contraste": contraste,
            "saturacao": saturacao,
            "nitidez": nitidez,
        },
        "ai_generated": True,
    }


# ─────────────────────────────────────────────────────────────────
#  REDIMENSIONAMENTO
# ─────────────────────────────────────────────────────────────────

def redimensionar(
    input_path: Path,
    largura: int = None,
    altura: int = None,
    resolucao_preset: str = None,
    manter_proporcao: bool = True,
    output_path: Path = None,
) -> dict:
    """Redimensiona imagem para qualquer resolução ou preset."""
    try:
        from PIL import Image
    except ImportError:
        return {"status": "error", "erro": "Pillow não instalado"}

    input_path = Path(input_path)
    if not input_path.exists():
        return {"status": "error", "erro": f"Arquivo não encontrado: {input_path}"}

    if resolucao_preset and resolucao_preset in RESOLUCOES:
        largura, altura = RESOLUCOES[resolucao_preset]

    if not largura and not altura:
        return {"status": "error", "erro": "Informe largura, altura ou resolucao_preset"}

    img = Image.open(str(input_path))

    if manter_proporcao:
        img.thumbnail((largura or 99999, altura or 99999), Image.LANCZOS)
    else:
        img = img.resize((largura, altura), Image.LANCZOS)

    if output_path is None:
        sufixo = f"_{largura}x{altura}" if largura and altura else "_resized"
        output_path = input_path.parent / f"{input_path.stem}{sufixo}{input_path.suffix}"
    output_path = Path(output_path)

    img.save(str(output_path))

    return {
        "status": "ok",
        "caminho": str(output_path),
        "resolucao": f"{img.width}x{img.height}",
        "ai_generated": True,
    }


# ─────────────────────────────────────────────────────────────────
#  THUMBNAIL YOUTUBE
# ─────────────────────────────────────────────────────────────────

def gerar_thumbnail(
    titulo: str,
    subtitulo: str = "",
    background_path: Path = None,
    output_path: Path = None,
    estilo: str = "dark_channel",
    canal: str = "DARK STUDIO AAA",
) -> dict:
    """Gera thumbnail profissional para YouTube (1280x720)."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        return {"status": "error", "erro": "Pillow não instalado"}

    largura, altura = 1280, 720

    # Carrega background ou gera um
    if background_path and Path(background_path).exists():
        img = Image.open(str(background_path)).convert("RGB")
        img = img.resize((largura, altura), Image.LANCZOS)
    else:
        # Gera background com gradiente dark
        img = Image.new("RGB", (largura, altura), (10, 10, 20))
        draw_bg = ImageDraw.Draw(img)
        # Gradiente diagonal
        for i in range(largura):
            ratio = i / largura
            r = int(20 + ratio * 40)
            g = int(10 + ratio * 20)
            b = int(30 + ratio * 60)
            draw_bg.line([(i, 0), (i, altura)], fill=(r, g, b))

    # Escurece levemente para contraste do texto
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    overlay = Image.new("RGBA", (largura, altura), (0, 0, 0, 100))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay).convert("RGB")

    draw = ImageDraw.Draw(img)

    # Fontes
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_canal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except Exception:
        font_titulo = ImageFont.load_default()
        font_sub = font_titulo
        font_canal = font_titulo

    # Barra lateral colorida
    draw.rectangle([(0, 0), (12, altura)], fill=(255, 50, 50))

    # Título (com quebra de linha automática)
    max_width = largura - 80
    palavras = titulo.upper().split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        teste = (linha_atual + " " + palavra).strip()
        bbox = draw.textbbox((0, 0), teste, font=font_titulo)
        if bbox[2] - bbox[0] <= max_width:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)

    # Desenha título
    y_titulo = altura // 4
    for linha in linhas[:3]:
        # Sombra
        draw.text((32, y_titulo + 3), linha, fill=(0, 0, 0), font=font_titulo)
        draw.text((30, y_titulo), linha, fill=(255, 255, 255), font=font_titulo)
        y_titulo += 80

    # Subtítulo
    if subtitulo:
        draw.text((32, y_titulo + 10), subtitulo, fill=(200, 200, 200), font=font_sub)

    # Nome do canal
    draw.text((30, altura - 45), canal, fill=(255, 50, 50), font=font_canal)

    # Marca IA (canto inferior direito)
    marca_ia = "⚡ AI"
    draw.text((largura - 60, altura - 35), marca_ia, fill=(255, 200, 50), font=font_canal)

    if output_path is None:
        h = hashlib.md5(titulo.encode()).hexdigest()[:8]
        output_path = Path("/tmp") / f"thumbnail_{h}.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")

    return {
        "status": "ok",
        "caminho": str(output_path),
        "titulo": titulo,
        "subtitulo": subtitulo,
        "resolucao": f"{largura}x{altura}",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_image_engine() -> dict:
    engines = {}

    # Pillow
    try:
        from PIL import Image
        engines["pillow"] = {"disponivel": True, "tipo": "local"}
    except ImportError:
        engines["pillow"] = {"disponivel": False}

    # HuggingFace API
    engines["huggingface_api"] = {
        "disponivel": bool(_HF_TOKEN),
        "tipo": "cloud_gratuito",
        "nota": "Requer HF_TOKEN no ambiente" if not _HF_TOKEN else "Token configurado",
    }

    # Stable Diffusion local
    try:
        import torch
        from diffusers import StableDiffusionXLPipeline  # noqa: F401
        engines["stable_diffusion_local"] = {
            "disponivel": True,
            "tipo": "local_gpu",
            "cuda": torch.cuda.is_available(),
            "modelo": _SD_MODEL_ID,
        }
    except ImportError:
        engines["stable_diffusion_local"] = {
            "disponivel": False,
            "tipo": "local_gpu",
            "nota": "Instale: pip install torch diffusers",
        }

    # rembg
    try:
        import rembg  # noqa: F401
        engines["rembg"] = {"disponivel": True, "tipo": "local"}
    except ImportError:
        engines["rembg"] = {"disponivel": False, "nota": "pip install rembg"}

    # Engine ativa
    engine_ativa = "placeholder_pillow"
    if engines.get("stable_diffusion_local", {}).get("disponivel"):
        engine_ativa = "stable_diffusion_local"
    elif engines.get("huggingface_api", {}).get("disponivel"):
        engine_ativa = "huggingface_api"

    return {
        "status": "ok",
        "engines": engines,
        "engine_ativa": engine_ativa,
        "resolucoes_suportadas": list(RESOLUCOES.keys()),
        "estilos_suportados": list(ESTILOS_PROMPT.keys()),
        "funcionalidades": [
            "texto_para_imagem",
            "upscaling",
            "remocao_fundo",
            "correcao_cores",
            "redimensionamento",
            "thumbnail_youtube",
        ],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
