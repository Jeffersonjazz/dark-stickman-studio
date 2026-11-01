"""
DARK STICKMAN STUDIO — Gerador de Thumbnails com Pillow
Cria capas de YouTube otimizadas para CTR.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import io
import math
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_OK = True
except ImportError:
    PIL_OK = False
    print("[THUMBNAIL] Pillow não instalado. Execute: pip install Pillow")

# Dimensões padrão YouTube (1280x720)
THUMB_W = 1280
THUMB_H = 720

# Paletas por nicho
PALETAS = {
    "psicologia":   {"bg": "#0F172A", "accent": "#6366F1", "text": "#FFFFFF", "shadow": "#4338CA"},
    "batalhas":     {"bg": "#1a0505", "accent": "#EF4444", "text": "#FFFFFF", "shadow": "#991B1B"},
    "tecnologia":   {"bg": "#060B18", "accent": "#3B82F6", "text": "#FFFFFF", "shadow": "#1D4ED8"},
    "stem":         {"bg": "#052e16", "accent": "#22C55E", "text": "#FFFFFF", "shadow": "#15803D"},
    "filosofia":    {"bg": "#1a1a2e", "accent": "#A855F7", "text": "#FFFFFF", "shadow": "#7E22CE"},
    "historia":     {"bg": "#2D1B0E", "accent": "#F59E0B", "text": "#FFFFFF", "shadow": "#B45309"},
    "misterio":     {"bg": "#0D0D1A", "accent": "#8B5CF6", "text": "#F0F0FF", "shadow": "#6D28D9"},
    "educacao":     {"bg": "#0C1445", "accent": "#60A5FA", "text": "#FFFFFF", "shadow": "#2563EB"},
    "relaxamento":  {"bg": "#0F2B23", "accent": "#34D399", "text": "#FFFFFF", "shadow": "#059669"},
    "natureza":     {"bg": "#0A1A0A", "accent": "#4ADE80", "text": "#FFFFFF", "shadow": "#16A34A"},
    "musical":      {"bg": "#1A0527", "accent": "#E879F9", "text": "#FFFFFF", "shadow": "#A21CAF"},
    "default":      {"bg": "#1a1a2e", "accent": "#3B82F6", "text": "#FFFFFF", "shadow": "#1D4ED8"},
}


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Converte cor hex para tupla RGB."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _carregar_fonte(tamanho: int, bold: bool = True) -> Optional["ImageFont.FreeTypeFont"]:
    """Tenta carregar fonte do sistema; usa default se não encontrar."""
    if not PIL_OK:
        return None
    fontes_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "arial.ttf",
    ]
    fontes_normal = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
        "arial.ttf",
    ]
    lista = fontes_bold if bold else fontes_normal
    for path in lista:
        try:
            return ImageFont.truetype(path, tamanho)
        except (IOError, OSError):
            continue
    # BUG #82 FIX: load_default() sem size retorna fonte bitmap minúscula (~10px).
    # Pillow >= 10.0 aceita size=; versões anteriores ignoram e retornam bitmap.
    try:
        return ImageFont.load_default(size=tamanho)  # Pillow >= 10.0
    except TypeError:
        return ImageFont.load_default()  # Pillow < 10.0 — bitmap; instale fonte do sistema


def _quebrar_texto(texto: str, max_chars: int = 22) -> list:
    """Quebra texto em linhas de no máximo max_chars caracteres."""
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for p in palavras:
        if len(linha_atual) + len(p) + 1 <= max_chars:
            linha_atual = (linha_atual + " " + p).strip()
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = p
    if linha_atual:
        linhas.append(linha_atual)
    return linhas[:3]  # Máximo 3 linhas no thumbnail


def gerar_thumbnail(
    titulo: str,
    canal_config: dict,
    output_path: Path,
    subtitulo: Optional[str] = None,
    stickman_lado: str = "right",
) -> Path:
    """
    Gera thumbnail de YouTube com texto impactante e stickman.

    Args:
        titulo: Texto principal (ex: "POR QUE VOCÊ PROCRASTINA?").
        canal_config: Config do canal com nicho, cor, etc.
        output_path: Caminho do arquivo PNG de saída.
        subtitulo: Texto secundário opcional.
        stickman_lado: 'right' ou 'left' — posição do stickman.

    Returns:
        Path do arquivo PNG gerado.
    """
    if not PIL_OK:
        raise ImportError("Pillow é necessário para gerar thumbnails: pip install Pillow")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    nicho = canal_config.get("nicho", "default")
    paleta = PALETAS.get(nicho, PALETAS["default"])
    cor_accent = canal_config.get("stickman_color", paleta["accent"])

    bg_rgb = _hex_to_rgb(paleta["bg"])
    accent_rgb = _hex_to_rgb(cor_accent)
    text_rgb = _hex_to_rgb(paleta["text"])
    shadow_rgb = _hex_to_rgb(paleta["shadow"])

    # ── Imagem base ──
    img = Image.new("RGB", (THUMB_W, THUMB_H), bg_rgb)
    draw = ImageDraw.Draw(img)

    # ── Gradiente de fundo (simulado com retângulos) ──
    for i in range(THUMB_H):
        factor = i / THUMB_H
        r = int(bg_rgb[0] * (1 - factor * 0.3))
        g = int(bg_rgb[1] * (1 - factor * 0.3))
        b = int(bg_rgb[2] * (1 - factor * 0.1))
        draw.line([(0, i), (THUMB_W, i)], fill=(r, g, b))

    # ── Faixa de accent no lado ──
    faixa_w = 12
    draw.rectangle([(0, 0), (faixa_w, THUMB_H)], fill=accent_rgb)
    draw.rectangle([(THUMB_W - faixa_w, 0), (THUMB_W, THUMB_H)], fill=accent_rgb)

    # ── Stickman simples via Pillow (lado direito) ──
    _desenhar_stickman_pillow(draw, accent_rgb, stickman_lado)

    # ── Texto principal ──
    linhas_titulo = _quebrar_texto(titulo.upper(), max_chars=18)
    fonte_titulo = _carregar_fonte(100, bold=True)
    fonte_sub = _carregar_fonte(44, bold=False)

    texto_x = 80 if stickman_lado == "right" else THUMB_W // 2 + 40
    texto_y = 120

    for linha in linhas_titulo:
        # Sombra
        draw.text((texto_x + 4, texto_y + 4), linha, font=fonte_titulo, fill=shadow_rgb)
        # Texto principal
        draw.text((texto_x, texto_y), linha, font=fonte_titulo, fill=text_rgb)
        texto_y += 115

    # ── Subtítulo ──
    if subtitulo:
        texto_y += 20
        draw.text((texto_x + 2, texto_y + 2), subtitulo, font=fonte_sub, fill=shadow_rgb)
        draw.text((texto_x, texto_y), subtitulo, font=fonte_sub, fill=(*accent_rgb, 220))

    # ── Barra inferior com nome do canal ──
    nome_canal = canal_config.get("nome", "DARK STUDIO")
    fonte_canal = _carregar_fonte(32, bold=True)
    draw.rectangle([(0, THUMB_H - 70), (THUMB_W, THUMB_H)], fill=(*accent_rgb, 200))
    draw.text((40, THUMB_H - 55), f"▶ {nome_canal}", font=fonte_canal, fill=(255, 255, 255))

    # ── Salva ──
    img.save(str(output_path), "PNG", quality=95)
    print(f"[THUMBNAIL] Gerado: {output_path} ({THUMB_W}x{THUMB_H})")
    return output_path


def _desenhar_stickman_pillow(draw: "ImageDraw.Draw", cor: Tuple, lado: str = "right"):
    """Desenha stickman simples com Pillow no lado indicado."""
    if lado == "right":
        cx = THUMB_W - 250
    else:
        cx = 250
    cy = THUMB_H // 2

    r = 70          # raio cabeça
    lw = 12         # largura dos traços

    # Cabeça
    draw.ellipse(
        [(cx - r, cy - 300 - r), (cx + r, cy - 300 + r)],
        outline=cor, width=lw, fill=(255, 255, 255),
    )
    # Pescoço
    draw.line([(cx, cy - 230), (cx, cy - 200)], fill=cor, width=lw)
    # Torso
    draw.line([(cx, cy - 200), (cx, cy - 50)], fill=cor, width=lw)
    # Braço esquerdo (levantado)
    draw.line([(cx, cy - 160), (cx - 100, cy - 280)], fill=cor, width=lw)
    # Braço direito
    draw.line([(cx, cy - 160), (cx + 90, cy - 130)], fill=cor, width=lw)
    # Perna esquerda
    draw.line([(cx, cy - 50), (cx - 70, cy + 110)], fill=cor, width=lw)
    # Perna direita
    draw.line([(cx, cy - 50), (cx + 70, cy + 110)], fill=cor, width=lw)


def gerar_variacao(
    titulo: str,
    canal_config: dict,
    output_dir: Path,
    n_variacoes: int = 3,
) -> list:
    """Gera N variações de thumbnail para teste A/B."""
    output_dir = Path(output_dir)
    paths = []
    lados = ["right", "left", "right"]

    for i in range(min(n_variacoes, 3)):
        path = output_dir / f"thumb_v{i+1}.png"
        config_var = {**canal_config}
        # Varia leve mente a cor de accent entre versões
        try:
            gerar_thumbnail(titulo, config_var, path, stickman_lado=lados[i])
            paths.append(path)
        except Exception as e:
            print(f"[THUMBNAIL] Variação {i+1} falhou: {e}")

    return paths


if __name__ == "__main__":
    import sys
    titulo = sys.argv[1] if len(sys.argv) > 1 else "POR QUE VOCÊ PROCRASTINA?"
    config_teste = {
        "nome": "Stickman Psicologia",
        "nicho": "psicologia",
        "stickman_color": "#6366F1",
    }
    out = Path("test_thumbnail.png")
    try:
        gerar_thumbnail(titulo, config_teste, out)
        print(f"Thumbnail gerado: {out}")
    except ImportError as e:
        print(e)
