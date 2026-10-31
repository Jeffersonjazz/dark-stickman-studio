"""
DARK STICKMAN STUDIO — FFMPEG SCENE ENGINE
Renderizador de cenas usando apenas FFmpeg + Pillow (sem Manim).
Fallback confiável para ambientes sem GPU ou sem Manim instalado.
"""
import os
import subprocess
import json
from pathlib import Path
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont

from core.stickman_svg import render_pose, POSES
from core.ffmpeg_utils import FFMPEG, FFPROBE, image_to_video, svg_to_png

# Configurações padrão
DEFAULT_W = 1920
DEFAULT_H = 1080
FPS = 30

# Paleta base dark
BG_COLOR = (15, 15, 30)
TEXT_COLOR = (240, 240, 255)
ACCENT_MAP = {
    "psicologia":  "#6366F1",
    "batalhas":    "#EF4444",
    "tecnologia":  "#3B82F6",
    "stem":        "#22C55E",
    "filosofia":   "#A855F7",
    "historia":    "#F59E0B",
    "misterio":    "#8B5CF6",
    "educacao":    "#60A5FA",
    "natureza":    "#4ADE80",
    "ciencia":     "#34D399",
    "financas":    "#FCD34D",
    "saude":       "#F472B6",
}


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _carregar_fonte(size: int):
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _quebrar_texto(texto: str, max_chars: int = 40) -> List[str]:
    """Quebra texto em linhas para caber na tela."""
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= max_chars:
            linha_atual = (linha_atual + " " + palavra).strip()
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas


def renderizar_cena_pillow(
    cena_num: int,
    pose: str,
    texto_tela: str,
    narracao: str,
    duracao_s: float,
    canal_config: dict,
    output_path: Path,
    show_counter: bool = True,
) -> Optional[Path]:
    """
    Renderiza uma cena usando Pillow + FFmpeg.
    Substitui o Manim quando ele não está disponível.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nicho = canal_config.get("nicho", "tecnologia")
    cor_hex = canal_config.get("stickman_color", ACCENT_MAP.get(nicho, "#3B82F6"))
    seed = canal_config.get("stickman_seed", 1001)

    # Selecionar pose (com fallback)
    pose_clean = pose.lower().replace(" ", "_")
    if pose_clean not in POSES:
        pose_clean = "parado"

    # Criar frame base
    img = Image.new("RGB", (DEFAULT_W, DEFAULT_H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    cor_rgb = _hex_to_rgb(cor_hex)
    cor_dim = tuple(int(c * 0.3) for c in cor_rgb)

    # Fundo gradiente simples (barra lateral colorida)
    draw.rectangle([0, 0, 8, DEFAULT_H], fill=cor_rgb)
    draw.rectangle([DEFAULT_W - 8, 0, DEFAULT_W, DEFAULT_H], fill=cor_rgb)

    # Barra inferior
    draw.rectangle([0, DEFAULT_H - 80, DEFAULT_W, DEFAULT_H], fill=cor_dim)

    # Número da cena
    if show_counter:
        f_cena = _carregar_fonte(36)
        draw.text((32, 32), f"CENA {cena_num:02d}", font=f_cena, fill=cor_rgb)

    # Gerar SVG do stickman e converter para PNG
    svg_content = render_pose(pose_clean, color=cor_hex, accent="#FFFFFF")
    svg_tmp = output_path.parent / f"_stickman_cena{cena_num:02d}.svg"
    png_tmp = output_path.parent / f"_stickman_cena{cena_num:02d}.png"
    svg_tmp.write_text(svg_content)

    stickman_ok = False
    stickman_img = svg_to_png(svg_tmp, png_tmp, width=300, height=450)
    if stickman_img and stickman_img.exists():
        try:
            stick = Image.open(str(stickman_img)).convert("RGBA")
            # Posicionar stickman no lado direito
            x_pos = DEFAULT_W - 380
            y_pos = DEFAULT_H - stick.height - 100
            img.paste(stick, (x_pos, y_pos), stick)
            stickman_ok = True
        except Exception:
            pass

    if not stickman_ok:
        # Desenhar stickman simplificado com Pillow
        _desenhar_stickman_simples(draw, DEFAULT_W - 300, DEFAULT_H // 2 - 100, cor_rgb)

    # Texto principal da cena
    linhas = _quebrar_texto(texto_tela.upper(), max_chars=35)
    f_titulo = _carregar_fonte(72)
    y_start = DEFAULT_H // 2 - (len(linhas) * 90) // 2
    for i, linha in enumerate(linhas):
        draw.text((120, y_start + i * 90), linha, font=f_titulo, fill=TEXT_COLOR)

    # Narração (menor, abaixo)
    linhas_narr = _quebrar_texto(narracao, max_chars=60)
    f_narr = _carregar_fonte(32)
    y_narr = DEFAULT_H - 160
    for i, linha in enumerate(linhas_narr[:2]):
        draw.text((120, y_narr + i * 44), linha, font=f_narr,
                  fill=tuple(int(c * 0.7) for c in TEXT_COLOR))

    # Watermark obrigatório
    f_wm = _carregar_fonte(22)
    draw.text(
        (DEFAULT_W // 2, DEFAULT_H - 30),
        "Produzido com IA — DARK STUDIO AAA",
        font=f_wm,
        fill=tuple(int(c * 0.4) for c in TEXT_COLOR),
        anchor="mm"
    )

    # Salvar frame
    frame_png = output_path.with_suffix(".png")
    img.save(str(frame_png), quality=95)

    # Converter para MP4
    result = image_to_video(frame_png, output_path, duration=duracao_s, fps=FPS)

    # Limpeza de temporários
    for tmp in [svg_tmp, png_tmp, frame_png]:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass

    return result


def _desenhar_stickman_simples(draw: ImageDraw.Draw, cx: int, cy: int, cor: tuple, escala: int = 1):
    """Desenha stickman vetorial com Pillow como fallback extremo."""
    r = 35 * escala
    lw = 6 * escala
    # Cabeça
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=cor, width=lw)
    # Corpo
    draw.line([cx, cy + r, cx, cy + r + 100 * escala], fill=cor, width=lw)
    # Braços
    draw.line([cx - 60 * escala, cy + r + 40 * escala,
               cx + 60 * escala, cy + r + 40 * escala], fill=cor, width=lw)
    # Pernas
    draw.line([cx, cy + r + 100 * escala,
               cx - 50 * escala, cy + r + 180 * escala], fill=cor, width=lw)
    draw.line([cx, cy + r + 100 * escala,
               cx + 50 * escala, cy + r + 180 * escala], fill=cor, width=lw)


def renderizar_intro_hook_ffmpeg(
    titulo: str,
    canal_config: dict,
    output_path: Path,
    duracao_s: float = 5.0,
) -> Optional[Path]:
    """Renderiza intro/hook usando apenas FFmpeg + Pillow."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nicho = canal_config.get("nicho", "tecnologia")
    cor_hex = canal_config.get("stickman_color", "#3B82F6")
    cor_rgb = _hex_to_rgb(cor_hex)
    cor_dim = tuple(int(c * 0.15) for c in cor_rgb)

    img = Image.new("RGB", (DEFAULT_W, DEFAULT_H), cor_dim)
    draw = ImageDraw.Draw(img)

    # Borda superior/inferior
    draw.rectangle([0, 0, DEFAULT_W, 10], fill=cor_rgb)
    draw.rectangle([0, DEFAULT_H - 10, DEFAULT_W, DEFAULT_H], fill=cor_rgb)

    # Título centralizado
    linhas = _quebrar_texto(titulo.upper(), max_chars=30)
    f_big = _carregar_fonte(90)
    f_canal = _carregar_fonte(40)
    y_start = DEFAULT_H // 2 - (len(linhas) * 110) // 2
    for i, linha in enumerate(linhas):
        draw.text((DEFAULT_W // 2, y_start + i * 110), linha,
                  font=f_big, fill=TEXT_COLOR, anchor="mm")

    # Nome do canal
    draw.text((DEFAULT_W // 2, DEFAULT_H - 120),
              canal_config.get("nome", "DARK STICKMAN STUDIO"),
              font=f_canal, fill=cor_rgb, anchor="mm")

    frame_png = output_path.with_suffix(".png")
    img.save(str(frame_png))

    result = image_to_video(frame_png, output_path, duration=duracao_s, fps=FPS)
    if frame_png.exists():
        frame_png.unlink()
    return result


def renderizar_outro_cta_ffmpeg(
    canal_config: dict,
    output_path: Path,
    duracao_s: float = 5.0,
) -> Optional[Path]:
    """Renderiza tela de encerramento CTA."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cor_hex = canal_config.get("stickman_color", "#3B82F6")
    cor_rgb = _hex_to_rgb(cor_hex)
    cor_dim = tuple(int(c * 0.1) for c in cor_rgb)

    img = Image.new("RGB", (DEFAULT_W, DEFAULT_H), cor_dim)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, DEFAULT_W, 10], fill=cor_rgb)
    draw.rectangle([0, DEFAULT_H - 10, DEFAULT_W, DEFAULT_H], fill=cor_rgb)

    f_cta = _carregar_fonte(80)
    f_sub = _carregar_fonte(42)
    f_wm = _carregar_fonte(28)

    draw.text((DEFAULT_W // 2, 300), "INSCREVA-SE!", font=f_cta, fill=cor_rgb, anchor="mm")
    draw.text((DEFAULT_W // 2, 420), "e ative o sininho 🔔", font=f_sub, fill=TEXT_COLOR, anchor="mm")
    draw.text((DEFAULT_W // 2, 580), canal_config.get("nome", "DARK STICKMAN STUDIO"),
              font=f_sub, fill=cor_rgb, anchor="mm")
    draw.text((DEFAULT_W // 2, DEFAULT_H - 50),
              "Produzido com IA — DARK STUDIO AAA",
              font=f_wm, fill=tuple(int(c * 0.4) for c in TEXT_COLOR), anchor="mm")

    frame_png = output_path.with_suffix(".png")
    img.save(str(frame_png))
    result = image_to_video(frame_png, output_path, duration=duracao_s, fps=FPS)
    if frame_png.exists():
        frame_png.unlink()
    return result
