"""
DARK STUDIO AAA — Gerador de Thumbnails Semana 02
Gera thumbnails via Pillow para os 5 canais da semana 02.
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json, hashlib, textwrap
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False
    print("⚠ Pillow não instalado. Instale: pip install Pillow --break-system-packages")

THUMB_DIR = Path("outputs/thumbnails")
THUMB_DIR.mkdir(parents=True, exist_ok=True)

CONFIGS = [
    {
        "id": "s02_short1",
        "titulo": "O Fenômeno de Dyatlov",
        "subtitulo": "9 Mortes Sem Explicação",
        "canal": "ESQUINA DO MEDO",
        "bg1": (10, 5, 20),
        "bg2": (40, 0, 0),
        "accent": (200, 0, 0),
        "text_color": (255, 200, 200),
    },
    {
        "id": "s02_short2",
        "titulo": "O Objeto Mais\nBrilhante do Universo",
        "subtitulo": "Descoberta em 2024",
        "canal": "HORIZONTE CÓSMICO",
        "bg1": (0, 0, 20),
        "bg2": (10, 0, 50),
        "accent": (100, 50, 255),
        "text_color": (200, 180, 255),
    },
    {
        "id": "s02_short3",
        "titulo": "Kryptos",
        "subtitulo": "O Código Impossível da CIA",
        "canal": "MESTRE DO OCULTO",
        "bg1": (5, 10, 5),
        "bg2": (0, 30, 10),
        "accent": (0, 200, 100),
        "text_color": (180, 255, 200),
    },
    {
        "id": "s02_short4",
        "titulo": "O Maior Ser\nVivo da Terra",
        "subtitulo": "80.000 Anos de Idade",
        "canal": "RAÍZES DA TERRA",
        "bg1": (10, 20, 5),
        "bg2": (20, 40, 0),
        "accent": (100, 180, 0),
        "text_color": (220, 255, 180),
    },
    {
        "id": "s02_short5",
        "titulo": "O Chip Que Vai\nSubstituir o Smartphone",
        "subtitulo": "O Futuro Chegou",
        "canal": "PULSO DIGITAL",
        "bg1": (0, 10, 20),
        "bg2": (0, 20, 40),
        "accent": (0, 150, 255),
        "text_color": (180, 220, 255),
    },
]


def gerar_thumbnail(cfg: dict) -> str:
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # Gradiente vertical
    bg1, bg2 = cfg["bg1"], cfg["bg2"]
    for y in range(H):
        t = y / H
        r = int(bg1[0] * (1-t) + bg2[0] * t)
        g = int(bg1[1] * (1-t) + bg2[1] * t)
        b = int(bg1[2] * (1-t) + bg2[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    acc = cfg["accent"]
    txt = cfg["text_color"]

    # Barra lateral colorida
    draw.rectangle([0, 0, 8, H], fill=acc)

    # Canal (topo)
    draw.rectangle([20, 20, W-20, 75], fill=(0, 0, 0, 180))
    try:
        font_canal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:
        font_canal = ImageFont.load_default()
    draw.text((W//2, 47), cfg["canal"], fill=acc, font=font_canal, anchor="mm")

    # Título principal
    titulo = cfg["titulo"]
    try:
        font_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 62)
    except Exception:
        font_titulo = ImageFont.load_default()

    linhas = titulo.split("\n")
    y_start = H // 2 - (len(linhas) * 75 // 2)
    for linha in linhas:
        draw.text((W//2, y_start), linha, fill=txt, font=font_titulo, anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 0))
        y_start += 75

    # Linha separadora
    draw.rectangle([80, y_start + 10, W-80, y_start + 14], fill=acc)

    # Subtítulo
    try:
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except Exception:
        font_sub = ImageFont.load_default()
    draw.text((W//2, y_start + 50), cfg["subtitulo"], fill=txt, font=font_sub, anchor="mm")

    # Rodapé AI
    try:
        font_foot = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except Exception:
        font_foot = ImageFont.load_default()
    draw.text((W//2, H - 25), "Produzido com IA — DARK STUDIO AAA", fill=(150, 150, 150),
              font=font_foot, anchor="mm")

    # Salvar
    hash_id = hashlib.md5(cfg["id"].encode()).hexdigest()[:8]
    nome_safe = cfg["titulo"].lower().replace("\n", "_").replace(" ", "_")[:30]
    thumb_path = THUMB_DIR / f"s02_thumb_{hash_id}_{nome_safe}.jpg"
    img.save(str(thumb_path), "JPEG", quality=92)
    return str(thumb_path)


if __name__ == "__main__":
    if not PIL_OK:
        exit(1)

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   THUMBNAIL AGENT — Semana 02 Nov 2026               ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    resultados = []
    for cfg in CONFIGS:
        path = gerar_thumbnail(cfg)
        kb = Path(path).stat().st_size / 1024
        print(f"  ✅ {cfg['id']} — {Path(path).name} ({kb:.0f} KB)")
        resultados.append({"id": cfg["id"], "canal": cfg["canal"], "thumb": path})

    # Salvar mapa
    mapa_path = Path("producao/semana_02_nov_2026/mapa_thumbnails_s02.json")
    mapa_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mapa_path, "w", encoding="utf-8") as f:
        json.dump({
            "gerado_em": datetime.now().isoformat(),
            "semana": "02", "total": len(resultados),
            "thumbnails": resultados,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }, f, ensure_ascii=False, indent=2)

    print(f"\n  {len(resultados)} thumbnails geradas em {THUMB_DIR}/")
    print(f"  Mapa: {mapa_path}")
