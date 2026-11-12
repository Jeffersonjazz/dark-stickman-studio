"""
DARK TUBE ENGINE — HuggingFace Image Client
Fase 2: DARK IMAGE STUDIO — Geração, upscaling e remoção de fundo via HF Spaces
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Modelos integrados:
- FLUX.1-schnell (evalstate/flux1_schnell) — Apache 2.0 — text-to-image
- Background Removal (not-lain/background-removal) — remoção de fundo BiRefNet
- Photo-Mate-i2i (prithivMLmods/Photo-Mate-i2i) — upscaling via Kontext-Unblur-Upscale LoRA
"""
import os
import uuid
import time
import requests
from pathlib import Path
from typing import Optional, Union


# ---------------------------------------------------------------------------
# Verificação de dependências
# ---------------------------------------------------------------------------
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
HF_SPACES = {
    "text_to_image": "evalstate/flux1_schnell",
    "bg_removal":    "not-lain/background-removal",
    "upscale":       "prithivMLmods/Photo-Mate-i2i",
}

DEFAULT_OUTPUT_DIR = "outputs/images"

AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"


# ---------------------------------------------------------------------------
# Utilitários internos
# ---------------------------------------------------------------------------

def _salvar_imagem_url(url: str, output_dir: str, prefixo: str = "img") -> str:
    """Baixa imagem de URL e salva no diretório de saída. Retorna caminho local."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    img_id = str(uuid.uuid4())[:8]
    # Detecta extensão pela URL ou default png
    ext = "png"
    for candidate in [".jpg", ".jpeg", ".png", ".webp"]:
        if candidate in url.lower():
            ext = candidate.lstrip(".")
            break
    filename = f"{prefixo}_{img_id}.{ext}"
    path = os.path.join(output_dir, filename)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    with open(path, "wb") as f:
        f.write(response.content)
    return path


def _imagem_para_url_ou_path(imagem: str) -> str:
    """
    Recebe caminho local ou URL.
    Se local, retorna handle_file(...) para o gradio_client.
    Se URL, retorna a string da URL diretamente.
    """
    if imagem.startswith("http://") or imagem.startswith("https://"):
        return imagem
    return handle_file(imagem) if GRADIO_AVAILABLE else imagem


# ---------------------------------------------------------------------------
# 1. FLUX.1-schnell — Texto para Imagem
# ---------------------------------------------------------------------------

def gerar_imagem_flux(
    prompt: str,
    largura: int = 1280,
    altura: int = 720,
    passos: int = 4,
    seed: Optional[int] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    hf_token: Optional[str] = None,
) -> dict:
    """
    Gera imagem via FLUX.1-schnell (evalstate/flux1_schnell).

    Args:
        prompt: Descrição em inglês (máx ~70 palavras para melhores resultados)
        largura: Largura em pixels (padrão 1280 para thumbnail YouTube)
        altura: Altura em pixels (padrão 720)
        passos: Passos de inferência (4 = rápido, 8 = mais qualidade)
        seed: Semente para reprodutibilidade (None = aleatório)
        output_dir: Diretório para salvar
        hf_token: Token HuggingFace (opcional, usa HF_TOKEN env se não passado)

    Returns:
        dict com status, path, url, metadata
    """
    if not GRADIO_AVAILABLE:
        return {"status": "failed", "error": "gradio_client não instalado. Execute: pip install gradio_client"}

    token = hf_token or os.environ.get("HF_TOKEN")
    kwargs = {}
    if token:
        kwargs["hf_token"] = token

    try:
        client = Client(HF_SPACES["text_to_image"], **kwargs)

        randomize_seed = seed is None
        if seed is None:
            seed = 0  # será randomizado pelo Space

        result = client.predict(
            prompt=prompt,
            width=largura,
            height=altura,
            num_inference_steps=passos,
            randomize_seed=randomize_seed,
            seed=seed,
            api_name="/flux1_schnell_infer"
        )

        # result = (image_path_or_url, seed_used)
        if isinstance(result, (list, tuple)):
            img_data, seed_usado = result[0], result[1] if len(result) > 1 else seed
        else:
            img_data, seed_usado = result, seed

        # Pode ser caminho local temporário ou URL
        path_local = None
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        img_id = str(uuid.uuid4())[:8]

        if isinstance(img_data, str) and (img_data.startswith("http") or img_data.startswith("/")):
            if img_data.startswith("http"):
                path_local = _salvar_imagem_url(img_data, output_dir, f"flux_{img_id}")
            else:
                # Caminho local temporário do gradio — copiar
                import shutil
                ext = Path(img_data).suffix or ".png"
                path_local = os.path.join(output_dir, f"flux_{img_id}{ext}")
                shutil.copy2(img_data, path_local)
        elif hasattr(img_data, "get"):
            # dict com url ou path
            url_ou_path = img_data.get("url") or img_data.get("path") or str(img_data)
            if url_ou_path.startswith("http"):
                path_local = _salvar_imagem_url(url_ou_path, output_dir, f"flux_{img_id}")
            else:
                import shutil
                ext = Path(url_ou_path).suffix or ".png"
                path_local = os.path.join(output_dir, f"flux_{img_id}{ext}")
                shutil.copy2(url_ou_path, path_local)
        else:
            path_local = os.path.join(output_dir, f"flux_{img_id}.png")
            with open(path_local, "wb") as f:
                f.write(bytes(img_data) if not isinstance(img_data, bytes) else img_data)

        return {
            "status": "completed",
            "path": path_local,
            "modelo": "FLUX.1-schnell",
            "space": HF_SPACES["text_to_image"],
            "prompt": prompt,
            "largura": largura,
            "altura": altura,
            "passos": passos,
            "seed": seed_usado,
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    except Exception as e:
        return {"status": "failed", "error": str(e), "modelo": "FLUX.1-schnell"}


# ---------------------------------------------------------------------------
# 2. Remoção de Fundo — BiRefNet (not-lain/background-removal)
# ---------------------------------------------------------------------------

def remover_fundo(
    imagem: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    hf_token: Optional[str] = None,
) -> dict:
    """
    Remove o fundo de uma imagem via BiRefNet (not-lain/background-removal).

    Args:
        imagem: Caminho local ou URL da imagem de entrada
        output_dir: Diretório para salvar resultado
        hf_token: Token HuggingFace (opcional)

    Returns:
        dict com status, path, metadata
    """
    if not GRADIO_AVAILABLE:
        return {"status": "failed", "error": "gradio_client não instalado."}

    token = hf_token or os.environ.get("HF_TOKEN")
    kwargs = {}
    if token:
        kwargs["hf_token"] = token

    try:
        client = Client(HF_SPACES["bg_removal"], **kwargs)

        img_input = _imagem_para_url_ou_path(imagem)

        result = client.predict(
            image=img_input,
            api_name="/background_removal_fn"
        )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        img_id = str(uuid.uuid4())[:8]
        path_local = None

        if isinstance(result, str):
            if result.startswith("http"):
                path_local = _salvar_imagem_url(result, output_dir, f"nobg_{img_id}")
            else:
                import shutil
                ext = Path(result).suffix or ".png"
                path_local = os.path.join(output_dir, f"nobg_{img_id}{ext}")
                shutil.copy2(result, path_local)
        elif hasattr(result, "get"):
            url_ou_path = result.get("url") or result.get("path") or str(result)
            if url_ou_path.startswith("http"):
                path_local = _salvar_imagem_url(url_ou_path, output_dir, f"nobg_{img_id}")
            else:
                import shutil
                ext = Path(url_ou_path).suffix or ".png"
                path_local = os.path.join(output_dir, f"nobg_{img_id}{ext}")
                shutil.copy2(url_ou_path, path_local)

        return {
            "status": "completed",
            "path": path_local,
            "imagem_original": imagem,
            "modelo": "BiRefNet",
            "space": HF_SPACES["bg_removal"],
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    except Exception as e:
        return {"status": "failed", "error": str(e), "modelo": "BiRefNet"}


# ---------------------------------------------------------------------------
# 3. Upscaling — Photo-Mate-i2i (Kontext-Unblur-Upscale LoRA)
# ---------------------------------------------------------------------------

def upscale_imagem(
    imagem: str,
    prompt: str = "sharp, high resolution, detailed, photorealistic",
    passos: int = 28,
    guidance_scale: float = 2.5,
    seed: int = 42,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    hf_token: Optional[str] = None,
) -> dict:
    """
    Realiza upscaling via Photo-Mate-i2i com LoRA Kontext-Unblur-Upscale.

    Args:
        imagem: Caminho local ou URL da imagem de entrada
        prompt: Prompt para guiar o upscaling (melhora nitidez e detalhes)
        passos: Passos de difusão (28 padrão)
        guidance_scale: Escala de orientação (2.5 padrão)
        seed: Semente para reprodutibilidade
        output_dir: Diretório para salvar resultado
        hf_token: Token HuggingFace (opcional)

    Returns:
        dict com status, path, metadata
    """
    if not GRADIO_AVAILABLE:
        return {"status": "failed", "error": "gradio_client não instalado."}

    token = hf_token or os.environ.get("HF_TOKEN")
    kwargs = {}
    if token:
        kwargs["hf_token"] = token

    try:
        client = Client(HF_SPACES["upscale"], **kwargs)

        img_input = _imagem_para_url_ou_path(imagem)

        result = client.predict(
            input_image=img_input,
            lora_adapter="Kontext-Unblur-Upscale",
            prompt=prompt,
            steps=passos,
            guidance_scale=guidance_scale,
            seed=seed,
            api_name="/Photo_Mate_i2i_infer"
        )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        img_id = str(uuid.uuid4())[:8]
        path_local = None

        if isinstance(result, str):
            if result.startswith("http"):
                path_local = _salvar_imagem_url(result, output_dir, f"upscale_{img_id}")
            else:
                import shutil
                ext = Path(result).suffix or ".png"
                path_local = os.path.join(output_dir, f"upscale_{img_id}{ext}")
                shutil.copy2(result, path_local)
        elif isinstance(result, (list, tuple)) and len(result) > 0:
            first = result[0]
            if isinstance(first, str) and first.startswith("http"):
                path_local = _salvar_imagem_url(first, output_dir, f"upscale_{img_id}")
            elif isinstance(first, str):
                import shutil
                ext = Path(first).suffix or ".png"
                path_local = os.path.join(output_dir, f"upscale_{img_id}{ext}")
                shutil.copy2(first, path_local)
        elif hasattr(result, "get"):
            url_ou_path = result.get("url") or result.get("path") or str(result)
            if url_ou_path.startswith("http"):
                path_local = _salvar_imagem_url(url_ou_path, output_dir, f"upscale_{img_id}")
            else:
                import shutil
                ext = Path(url_ou_path).suffix or ".png"
                path_local = os.path.join(output_dir, f"upscale_{img_id}{ext}")
                shutil.copy2(url_ou_path, path_local)

        return {
            "status": "completed",
            "path": path_local,
            "imagem_original": imagem,
            "modelo": "Kontext-Unblur-Upscale",
            "space": HF_SPACES["upscale"],
            "prompt": prompt,
            "passos": passos,
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    except Exception as e:
        return {"status": "failed", "error": str(e), "modelo": "Kontext-Unblur-Upscale"}


# ---------------------------------------------------------------------------
# 4. Pipeline de thumbnail YouTube — FLUX + upscale + compressão <2MB
# ---------------------------------------------------------------------------

def gerar_thumbnail_ia(
    prompt: str,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    aplicar_upscale: bool = True,
    hf_token: Optional[str] = None,
) -> dict:
    """
    Pipeline completo: FLUX text-to-image (1280x720) → upscale → comprime JPEG <2MB.
    Dimensões YouTube thumbnail: 1280x720.

    Args:
        prompt: Descrição da thumbnail em inglês
        output_dir: Diretório de saída
        aplicar_upscale: Aplica Photo-Mate-i2i upscaling (mais lento, melhor qualidade)
        hf_token: Token HuggingFace

    Returns:
        dict com status, path final, tamanho em bytes, metadata completa
    """
    resultado = {}

    # Passo 1: Gerar imagem base 1280x720
    r_flux = gerar_imagem_flux(
        prompt=prompt,
        largura=1280,
        altura=720,
        passos=4,
        output_dir=output_dir,
        hf_token=hf_token,
    )
    resultado["flux"] = r_flux

    if r_flux["status"] != "completed" or not r_flux.get("path"):
        return {
            "status": "failed",
            "etapa_falha": "flux",
            "erro": r_flux.get("error"),
            "ai_disclosure": AI_DISCLOSURE,
        }

    caminho_atual = r_flux["path"]

    # Passo 2: Upscale (opcional)
    if aplicar_upscale:
        r_upscale = upscale_imagem(
            imagem=caminho_atual,
            prompt="sharp YouTube thumbnail, high resolution, vibrant colors, cinematic",
            output_dir=output_dir,
            hf_token=hf_token,
        )
        resultado["upscale"] = r_upscale
        if r_upscale["status"] == "completed" and r_upscale.get("path"):
            caminho_atual = r_upscale["path"]

    # Passo 3: Comprimir para JPEG < 2MB (limite YouTube)
    if PIL_AVAILABLE:
        img_id = str(uuid.uuid4())[:8]
        jpeg_path = os.path.join(output_dir, f"thumb_final_{img_id}.jpg")
        try:
            img = Image.open(caminho_atual).convert("RGB")
            # Redimensiona para 1280x720 se necessário
            if img.size != (1280, 720):
                img = img.resize((1280, 720), Image.LANCZOS)
            # Comprime iterativamente até ficar < 2MB
            qualidade = 92
            while qualidade >= 60:
                img.save(jpeg_path, "JPEG", quality=qualidade, optimize=True)
                tamanho = os.path.getsize(jpeg_path)
                if tamanho <= 1_900_000:  # margem de segurança: 1.9MB
                    break
                qualidade -= 5
            tamanho_final = os.path.getsize(jpeg_path)
            resultado["compressao"] = {
                "qualidade_jpeg": qualidade,
                "tamanho_bytes": tamanho_final,
                "tamanho_mb": round(tamanho_final / 1_048_576, 2),
                "dentro_limite_youtube": tamanho_final <= 2_097_152,
            }
            caminho_atual = jpeg_path
        except Exception as e:
            resultado["compressao"] = {"status": "skipped", "erro": str(e)}

    tamanho_bytes = os.path.getsize(caminho_atual) if os.path.exists(caminho_atual) else 0

    return {
        "status": "completed",
        "path": caminho_atual,
        "tamanho_bytes": tamanho_bytes,
        "tamanho_mb": round(tamanho_bytes / 1_048_576, 2),
        "dentro_limite_youtube": tamanho_bytes <= 2_097_152,
        "prompt": prompt,
        "pipeline": resultado,
        "ai_generated": True,
        "ai_disclosure": AI_DISCLOSURE,
    }


# ---------------------------------------------------------------------------
# 5. Compressor de thumbnail standalone (fix PNG > 2MB)
# ---------------------------------------------------------------------------

def comprimir_thumbnail_youtube(
    caminho_entrada: str,
    output_dir: Optional[str] = None,
    qualidade_inicial: int = 92,
) -> dict:
    """
    Comprime thumbnail PNG/JPG para JPEG <2MB (limite YouTube custom thumbnail).
    Utilitário standalone — pode ser chamado separadamente.

    Args:
        caminho_entrada: Caminho do arquivo de entrada (PNG, JPG, WEBP)
        output_dir: Diretório de saída (None = mesmo dir da entrada)
        qualidade_inicial: Qualidade JPEG inicial (92 padrão)

    Returns:
        dict com status, path, tamanho final, dentro_limite_youtube
    """
    if not PIL_AVAILABLE:
        return {"status": "failed", "error": "Pillow não instalado. Execute: pip install Pillow"}

    if not os.path.exists(caminho_entrada):
        return {"status": "failed", "error": f"Arquivo não encontrado: {caminho_entrada}"}

    out_dir = output_dir or os.path.dirname(caminho_entrada) or "."
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    stem = Path(caminho_entrada).stem
    jpeg_path = os.path.join(out_dir, f"{stem}_youtube.jpg")

    try:
        img = Image.open(caminho_entrada).convert("RGB")

        # Garante dimensões 1280x720
        if img.size != (1280, 720):
            img = img.resize((1280, 720), Image.LANCZOS)

        qualidade = qualidade_inicial
        while qualidade >= 50:
            img.save(jpeg_path, "JPEG", quality=qualidade, optimize=True, progressive=True)
            tamanho = os.path.getsize(jpeg_path)
            if tamanho <= 1_900_000:
                break
            qualidade -= 5

        tamanho_final = os.path.getsize(jpeg_path)
        return {
            "status": "completed",
            "path": jpeg_path,
            "tamanho_original_bytes": os.path.getsize(caminho_entrada),
            "tamanho_final_bytes": tamanho_final,
            "tamanho_mb": round(tamanho_final / 1_048_576, 2),
            "qualidade_jpeg": qualidade,
            "dentro_limite_youtube": tamanho_final <= 2_097_152,
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# ---------------------------------------------------------------------------
# 6. Status e diagnóstico
# ---------------------------------------------------------------------------

def status_hf_image_client() -> dict:
    """Retorna status das dependências e spaces disponíveis."""
    return {
        "gradio_client": GRADIO_AVAILABLE,
        "pillow": PIL_AVAILABLE,
        "spaces": HF_SPACES,
        "hf_token_presente": bool(os.environ.get("HF_TOKEN")),
        "capacidades": [
            "text_to_image (FLUX.1-schnell)",
            "background_removal (BiRefNet)",
            "upscaling (Kontext-Unblur-Upscale)",
            "thumbnail_pipeline (FLUX + upscale + compressão <2MB)",
            "thumbnail_compressor (standalone PNG→JPEG <2MB)",
        ],
        "ai_disclosure": AI_DISCLOSURE,
    }
