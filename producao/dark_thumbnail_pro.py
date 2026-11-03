#!/usr/bin/env python3
"""
DARK STUDIO AAA — DARK THUMBNAIL PRO
Gera thumbnails 1280x720 cinematográficos por nicho com Pillow.
Agentes: 🖼️ IMAGE ENGINE | 🎨 MOTION GRAPHICS | ✅ CREATIVE QA
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, os
from pathlib import Path

PROJETO = Path("/home/claude/dark-stickman-studio")
OUT_DIR = PROJETO / "outputs" / "thumbnails"
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720

# Paletas por nicho
TEMAS = {
    "psicologia": {
        "bg":      (13, 13, 26),
        "accent":  (106, 90, 255),
        "mid":     (50, 40, 120),
        "txt":     (232, 224, 255),
        "icon":    "🧠",
        "tag":     "PSICOLOGIA",
    },
    "historia": {
        "bg":      (26, 13, 10),
        "accent":  (204, 123, 31),
        "mid":     (100, 55, 10),
        "txt":     (255, 240, 220),
        "icon":    "📜",
        "tag":     "HISTÓRIA",
    },
    "tecnologia": {
        "bg":      (5, 15, 13),
        "accent":  (0, 255, 204),
        "mid":     (0, 100, 80),
        "txt":     (208, 255, 245),
        "icon":    "🤖",
        "tag":     "TECNOLOGIA",
    },
    "misterio": {
        "bg":      (8, 0, 15),
        "accent":  (170, 0, 255),
        "mid":     (70, 0, 110),
        "txt":     (240, 208, 255),
        "icon":    "🔍",
        "tag":     "MISTÉRIO",
    },
    "natureza": {
        "bg":      (3, 13, 7),
        "accent":  (0, 204, 102),
        "mid":     (0, 80, 40),
        "txt":     (208, 255, 232),
        "icon":    "🌊",
        "tag":     "NATUREZA",
    },
}

VIDEOS = [
    {"id": "v001", "titulo": "Por Que Você\nSe Sente Vazio", "tema": "psicologia",  "subtitulo": "A resposta que a ciência esconde"},
    {"id": "v002", "titulo": "Os Bastidores\ndo Tempo",       "tema": "historia",   "subtitulo": "Decisões que mudaram o mundo"},
    {"id": "v003", "titulo": "Intelligentia\nNova",           "tema": "tecnologia", "subtitulo": "A IA que está mudando tudo"},
    {"id": "v004", "titulo": "Projeto\nSecreto",              "tema": "misterio",   "subtitulo": "Arquivos que não deveriam existir"},
    {"id": "v005", "titulo": "AquaZen\nO Poder da Água",      "tema": "natureza",   "subtitulo": "O que a ciência descobriu"},
]


def carregar_fonte(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Tenta carregar fonte do sistema, fallback para default."""
    candidatos_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    candidatos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]
    lista = candidatos_bold if bold else candidatos
    for caminho in lista:
        if Path(caminho).exists():
            return ImageFont.truetype(caminho, size)
    return ImageFont.load_default()


def gerar_thumbnail(v: dict) -> Path:
    tema = TEMAS[v["tema"]]
    bg    = tema["bg"]
    acc   = tema["accent"]
    mid   = tema["mid"]
    txt   = tema["txt"]
    tag   = tema["tag"]

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # ── Gradiente lateral (accent → bg) ──────────────────────────────────────
    for x in range(W // 2):
        ratio = x / (W // 2)
        r = int(acc[0] * (1 - ratio) + bg[0] * ratio)
        g = int(acc[1] * (1 - ratio) + bg[1] * ratio)
        b = int(acc[2] * (1 - ratio) + bg[2] * ratio)
        alpha = int(60 * (1 - ratio))
        overlay = Image.new("RGBA", (1, H), (r, g, b, alpha))
        img.paste(Image.new("RGB", (1, H), (r, g, b)), (x, 0))

    # Refazer o fundo correto com gradiente suave
    img2 = Image.new("RGB", (W, H), bg)
    draw2 = ImageDraw.Draw(img2)

    # Fundo sólido
    draw2.rectangle([0, 0, W, H], fill=bg)

    # Faixa accent à esquerda (coluna colorida)
    bar_w = 12
    draw2.rectangle([0, 0, bar_w, H], fill=acc)

    # Linha diagonal decorativa
    for i in range(0, 6):
        x0 = bar_w + i * 2
        draw2.line([(x0, 0), (x0 + H, H)], fill=mid, width=1)

    # Círculo de fundo (decorativo, canto direito)
    cx, cy, r_circ = W - 200, H // 2, 260
    for step in range(8, 0, -1):
        alpha_v = step * 8
        r_step  = r_circ * step // 8
        color = tuple(min(255, c + 20) for c in mid)
        draw2.ellipse(
            [cx - r_step, cy - r_step, cx + r_step, cy + r_step],
            outline=color + (alpha_v,) if False else color,
            width=2
        )

    # ── Tag de nicho (topo) ────────────────────────────────────────────────────
    fonte_tag = carregar_fonte(22, bold=True)
    tag_text  = f"  {tag}  "
    bbox_tag  = draw2.textbbox((0, 0), tag_text, font=fonte_tag)
    tag_w     = bbox_tag[2] - bbox_tag[0]
    tag_h     = bbox_tag[3] - bbox_tag[1]
    tag_x, tag_y = 40, 36
    draw2.rectangle([tag_x - 6, tag_y - 6, tag_x + tag_w + 6, tag_y + tag_h + 6], fill=acc)
    draw2.text((tag_x, tag_y), tag_text, font=fonte_tag, fill=bg)

    # ── Ícone grande (centro-direita) ─────────────────────────────────────────
    try:
        fonte_icon = carregar_fonte(160)
        draw2.text((W - 340, H // 2 - 100), tema["icon"], font=fonte_icon, fill=mid)
    except Exception:
        pass

    # ── Título principal ───────────────────────────────────────────────────────
    fonte_titulo = carregar_fonte(88, bold=True)
    linhas = v["titulo"].split("\n")
    y_titulo = H // 2 - len(linhas) * 50 - 20
    for linha in linhas:
        # Sombra
        draw2.text((bar_w + 42, y_titulo + 3), linha, font=fonte_titulo, fill=(0, 0, 0))
        # Texto
        draw2.text((bar_w + 40, y_titulo), linha, font=fonte_titulo, fill=txt)
        y_titulo += 100

    # ── Subtítulo ──────────────────────────────────────────────────────────────
    fonte_sub = carregar_fonte(32)
    sub_y     = y_titulo + 12
    draw2.text((bar_w + 40, sub_y), v["subtitulo"], font=fonte_sub, fill=acc)

    # ── Linha separadora ───────────────────────────────────────────────────────
    draw2.rectangle([bar_w + 40, sub_y - 14, bar_w + 40 + 340, sub_y - 10], fill=acc)

    # ── Rodapé DARK STUDIO ────────────────────────────────────────────────────
    fonte_rod = carregar_fonte(20)
    rod_text  = "DARK STUDIO AAA"
    draw2.text((bar_w + 40, H - 50), rod_text, font=fonte_rod, fill=mid)

    # ── Vinheta (bordas escuras) ───────────────────────────────────────────────
    vinheta = Image.new("RGB", (W, H), (0, 0, 0))
    vig_draw = ImageDraw.Draw(vinheta)
    for i in range(120):
        alpha = int(180 * (1 - i / 120))
        c = (alpha, alpha, alpha)
        vig_draw.rectangle([i, i, W - i, H - i], outline=c)
    img_final = Image.blend(img2, vinheta, alpha=0.25)

    out_path = OUT_DIR / f"{v['id']}_thumbnail.jpg"
    img_final.save(out_path, "JPEG", quality=95)
    size_kb = out_path.stat().st_size // 1024
    print(f"  ✅ {out_path.name} — {size_kb}KB")
    return out_path


print("=" * 50)
print("🖼️  DARK THUMBNAIL PRO — Gerando capas Semana 01")
print("=" * 50)

resultados = []
for v in VIDEOS:
    print(f"\n  📌 {v['id']}: {v['titulo'].replace(chr(10), ' ')}")
    try:
        p = gerar_thumbnail(v)
        resultados.append({"id": v["id"], "arquivo": str(p), "status": "OK"})
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        resultados.append({"id": v["id"], "status": f"ERRO: {e}"})

print(f"\n✅ {sum(1 for r in resultados if r['status']=='OK')}/{len(resultados)} thumbnails gerados")
print(f"📁 {OUT_DIR}")

with open(OUT_DIR / "thumbnails_manifesto.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
