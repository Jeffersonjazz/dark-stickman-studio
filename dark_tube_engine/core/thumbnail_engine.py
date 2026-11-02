"""
DARK TUBE ENGINE — Thumbnail Engine (clone vidiq_generate_thumbnail)
Agente: IMAGE ENGINE + DARK THUMBNAIL PRO
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Paletas por nicho — engenharia reversa dos padrões visuais YouTube
PALETAS = {
    "motivacional": {
        "bg": (10, 10, 30),
        "accent": (255, 165, 0),
        "texto": (255, 255, 255),
        "sombra": (255, 100, 0, 180)
    },
    "terror": {
        "bg": (5, 5, 5),
        "accent": (180, 0, 0),
        "texto": (220, 220, 220),
        "sombra": (100, 0, 0, 200)
    },
    "tech_ia": {
        "bg": (5, 15, 35),
        "accent": (0, 200, 255),
        "texto": (255, 255, 255),
        "sombra": (0, 100, 200, 180)
    },
    "conspiracao": {
        "bg": (8, 8, 20),
        "accent": (150, 0, 200),
        "texto": (200, 200, 200),
        "sombra": (80, 0, 120, 200)
    },
    "relaxamento": {
        "bg": (5, 20, 40),
        "accent": (0, 180, 200),
        "texto": (220, 240, 255),
        "sombra": (0, 80, 120, 180)
    },
    "documentario": {
        "bg": (15, 10, 5),
        "accent": (200, 150, 50),
        "texto": (240, 230, 210),
        "sombra": (100, 70, 20, 180)
    }
}

CANAL_PARA_NICHO = {
    "Mente de Aço": "motivacional",
    "Esquina do Medo": "terror",
    "Intelligentia Nova": "tech_ia",
    "Projeto Secreto": "conspiracao",
    "AquaZen Relax": "relaxamento",
    "Dark Nature": "documentario",
    "Historia Sombria": "documentario"
}

# Dimensões padrão YouTube
TAMANHOS = {
    "thumbnail_horizontal": (1280, 720),
    "thumbnail_shorts": (1080, 1920),
    "banner": (2560, 1440),
    "avatar": (800, 800)
}


def gerar_thumbnail_pillow(
    titulo: str,
    canal: str,
    nicho: str = None,
    subtitulo: str = "",
    output_dir: str = "outputs/thumbnails",
    tamanho: str = "thumbnail_horizontal",
    emoji: str = ""
) -> dict:
    """
    Gera thumbnail YouTube com Pillow — clone da funcionalidade vidiq_generate_thumbnail
    Interface e algoritmo próprios, sem copiar assets do vidIQ
    """
    if not PIL_AVAILABLE:
        return {"status": "failed", "error": "Pillow não instalado. Execute: pip install Pillow"}

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    nicho_det = nicho or CANAL_PARA_NICHO.get(canal, "documentario")
    paleta = PALETAS.get(nicho_det, PALETAS["documentario"])
    w, h = TAMANHOS.get(tamanho, (1280, 720))

    # --- Canvas base ---
    img = Image.new("RGB", (w, h), paleta["bg"])
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Gradiente diagonal (efeito visual dark) ---
    for i in range(h):
        alpha = int(40 * (1 - i / h))
        r, g, b = paleta["accent"]
        draw.line([(0, i), (w, i)], fill=(r, g, b, alpha))

    # --- Borda neon lateral ---
    borda = 8
    r, g, b = paleta["accent"]
    draw.rectangle([0, 0, borda, h], fill=(r, g, b, 200))
    draw.rectangle([w - borda, 0, w, h], fill=(r, g, b, 80))

    # --- Linha horizontal accent ---
    linha_y = int(h * 0.65)
    draw.rectangle([40, linha_y, w - 40, linha_y + 4], fill=paleta["accent"])

    # --- Círculo decorativo background ---
    cx, cy = int(w * 0.75), int(h * 0.4)
    raio = int(h * 0.45)
    r, g, b = paleta["accent"]
    draw.ellipse([cx - raio, cy - raio, cx + raio, cy + raio],
                 fill=(r, g, b, 15), outline=(r, g, b, 60), width=2)

    # --- Texto principal ---
    # Usa fonte padrão do sistema (sem dependência externa)
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                          size=int(h * 0.11))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                                       size=int(h * 0.055))
        font_canal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                         size=int(h * 0.04))
    except Exception:
        font_titulo = ImageFont.load_default()
        font_sub = font_titulo
        font_canal = font_titulo

    # Quebra o título em linhas
    palavras = titulo.split()
    linhas = []
    linha_atual = ""
    max_chars = 22 if tamanho == "thumbnail_horizontal" else 18
    for palavra in palavras:
        if len(linha_atual + " " + palavra) <= max_chars:
            linha_atual = (linha_atual + " " + palavra).strip()
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    linhas = linhas[:3]  # máx 3 linhas

    # Renderiza título com sombra
    y_start = int(h * 0.15)
    line_h = int(h * 0.13)
    for i, linha in enumerate(linhas):
        y = y_start + i * line_h
        # Sombra
        draw.text((52, y + 4), linha, font=font_titulo, fill=(0, 0, 0, 180))
        # Texto principal
        draw.text((48, y), linha, font=font_titulo, fill=paleta["texto"])

    # Subtítulo
    if subtitulo:
        draw.text((50, linha_y + 20), subtitulo[:50], font=font_sub,
                  fill=paleta["accent"])

    # Nome do canal (canto inferior)
    canal_text = f"● {canal.upper()}"
    draw.text((50, h - int(h * 0.1)), canal_text, font=font_canal,
              fill=paleta["accent"])

    # Emoji grande se fornecido
    if emoji:
        try:
            font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                                             size=int(h * 0.3))
            draw.text((int(w * 0.6), int(h * 0.2)), emoji, font=font_emoji,
                      embedded_color=True)
        except Exception:
            pass  # emoji é opcional

    # --- Efeito vinheta ---
    vinheta = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vinheta)
    for raio_v in range(min(w, h) // 2, 0, -5):
        alpha_v = int(80 * (1 - raio_v / (min(w, h) / 2)))
        vd.ellipse([w//2 - raio_v, h//2 - raio_v, w//2 + raio_v, h//2 + raio_v],
                   fill=(0, 0, 0, alpha_v))
    img = Image.alpha_composite(img.convert("RGBA"), vinheta).convert("RGB")

    # Salva
    thumb_id = str(uuid.uuid4())[:8]
    slug = titulo.lower().replace(" ", "_")[:30]
    filename = f"thumb_{thumb_id}_{slug}.jpg"
    path = os.path.join(output_dir, filename)
    img.save(path, "JPEG", quality=95, optimize=True)

    return {
        "thumbnail_id": thumb_id,
        "status": "completed",
        "path": path,
        "filename": filename,
        "tamanho": f"{w}x{h}",
        "nicho": nicho_det,
        "canal": canal,
        "titulo": titulo,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }


def gerar_pack_thumbnails(titulo: str, canal: str, nicho: str = None,
                           output_dir: str = "outputs/thumbnails") -> list:
    """Gera 3 variações de thumbnail — horizontal + shorts + alternativa"""
    resultados = []
    for tamanho in ["thumbnail_horizontal", "thumbnail_shorts"]:
        r = gerar_thumbnail_pillow(titulo, canal, nicho, "", output_dir, tamanho)
        resultados.append(r)
    return resultados
