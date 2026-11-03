#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║     DARK VISUAL CONSISTENCY — AGENTE VISUAL CONSISTENCY     ║
║     DARK STUDIO AAA v1.4.0 — FASE 8                        ║
║                                                              ║
║  Agentes Especialistas Integrados:                          ║
║  • VISUAL CONSISTENCY — paleta, personagens, estilo         ║
║  • ASSET MANAGER      — banco de referências por projeto    ║
║  • IMAGE ENGINE       — análise e extração de frames        ║
║  • CREATIVE QA        — validação de consistência           ║
╚══════════════════════════════════════════════════════════════╝

Responsabilidades:
  - Banco de referências visuais por projeto/canal
  - Registro de personagens: aparência, vestuário, traços
  - Registro de cenários: ambiente, iluminação, horário
  - Registro de paleta de cores aprovada por nicho
  - Extração de frame representativo de cada vídeo
  - Geração de prompt de consistência para IA generativa
  - Score de consistência entre cenas (comparação de histogramas)
  - Relatório de desvios visuais detectados
  - Exportação de Style Guide por canal

Uso:
  python3 producao/dark_visual_consistency.py --registrar-canal v001
  python3 producao/dark_visual_consistency.py --analisar-todos
  python3 producao/dark_visual_consistency.py --style-guide psicologia
  python3 producao/dark_visual_consistency.py --score-consistencia v001 v002

ai_generated: True
ai_disclosure: "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
"""

import os
import sys
import json
import subprocess
import argparse
import shutil
import math
from pathlib import Path
from datetime import datetime

# ── Dependências opcionais ─────────────────────────────────────────────────
try:
    from PIL import Image, ImageStat, ImageFilter, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Caminhos base ─────────────────────────────────────────────────────────
BASE        = Path(__file__).parent.parent
VIDEOS_FINAIS = BASE / "outputs" / "videos_finais"
CONSISTENCY_DIR = BASE / "outputs" / "visual_consistency"
FRAMES_DIR  = CONSISTENCY_DIR / "frames_referencia"
GUIDES_DIR  = CONSISTENCY_DIR / "style_guides"
DB_PATH     = CONSISTENCY_DIR / "visual_db.json"

for d in [CONSISTENCY_DIR, FRAMES_DIR, GUIDES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Banco de referências visuais por canal ────────────────────────────────
CANAIS_DB = {
    "v001": {
        "canal":   "Mente de Aço",
        "nicho":   "psicologia",
        "preset":  "psicologia",
        "paleta": {
            "primaria":    "#9B59B6",
            "secundaria":  "#E8DAEF",
            "fundo":       "#1A0533",
            "texto":       "#FFFFFF",
            "acento":      "#D4ACFB",
            "aviso":       "#E74C3C",
        },
        "tipografia": {
            "titulo":  "Arial Black / Bold",
            "corpo":   "Arial / Regular",
            "tamanho_titulo": 80,
            "tamanho_legenda": 52,
        },
        "cinematografia": {
            "aspect_ratio": "16:9",
            "letterbox":    False,
            "vinheta":      0.6,
            "grain":        0.03,
            "temperatura":  "fria-neutra (5500K)",
            "contraste":    "alto",
            "saturacao":    "levemente reduzida",
        },
        "personagens": [],
        "cenarios": [
            {
                "id": "cen001",
                "nome": "Interior introspectivo",
                "descricao": "Ambiente escuro com iluminação lateral suave, tons roxos e azulados, profundidade de campo rasa",
                "elementos": ["névoa suave", "luz direcional única", "fundo desfocado"],
                "aprovado": True,
            }
        ],
        "estilo_prompt": (
            "cinematic dark psychology channel, moody purple tones, #9B59B6 accent, "
            "deep shadows, introspective atmosphere, professional photography style, "
            "8K resolution, film grain, vignette, no presenter, faceless channel"
        ),
        "proibido": [
            "logos de marcas reais",
            "rostos identificáveis sem autorização",
            "imagens documentais apresentadas como reais",
        ],
    },
    "v002": {
        "canal":   "Bastidores do Tempo",
        "nicho":   "historia",
        "preset":  "historia",
        "paleta": {
            "primaria":    "#D4A017",
            "secundaria":  "#FAF0E6",
            "fundo":       "#1C0A00",
            "texto":       "#FAF0E6",
            "acento":      "#F0C040",
            "aviso":       "#8B0000",
        },
        "tipografia": {
            "titulo":  "Cinzel / Bold",
            "corpo":   "Lora / Regular",
            "tamanho_titulo": 72,
            "tamanho_legenda": 48,
        },
        "cinematografia": {
            "aspect_ratio": "2.39:1",
            "letterbox":    True,
            "vinheta":      0.7,
            "grain":        0.05,
            "temperatura":  "quente-sépia (3200K)",
            "contraste":    "muito alto",
            "saturacao":    "reduzida, tons âmbar",
        },
        "personagens": [],
        "cenarios": [
            {
                "id": "cen001",
                "nome": "Arquivo histórico",
                "descricao": "Documentos antigos, mapas, luz de vela ou lamparina, tons sépia e âmbar",
                "elementos": ["papel envelhecido", "tinta antiga", "luz quente direcionada"],
                "aprovado": True,
            }
        ],
        "estilo_prompt": (
            "cinematic historical documentary channel, warm sepia tones, #D4A017 gold accent, "
            "aged parchment texture, dramatic chiaroscuro lighting, letterbox 2.39:1, "
            "film grain, vintage photography style, no presenter, faceless channel"
        ),
        "proibido": [
            "anacronismos visuais",
            "elementos modernos em cenas históricas",
            "imagens históricas reais não licenciadas",
        ],
    },
    "v003": {
        "canal":   "Intelligentia Nova",
        "nicho":   "tecnologia",
        "preset":  "tecnologia",
        "paleta": {
            "primaria":    "#00D4FF",
            "secundaria":  "#E0F7FF",
            "fundo":       "#000D1A",
            "texto":       "#E0F7FF",
            "acento":      "#00FF88",
            "aviso":       "#FF4400",
        },
        "tipografia": {
            "titulo":  "Rajdhani / Bold",
            "corpo":   "Source Code Pro / Regular",
            "tamanho_titulo": 76,
            "tamanho_legenda": 48,
        },
        "cinematografia": {
            "aspect_ratio": "16:9",
            "letterbox":    False,
            "vinheta":      0.4,
            "grain":        0.01,
            "temperatura":  "fria-azulada (7000K)",
            "contraste":    "alto",
            "saturacao":    "alta nos cianos e azuis",
        },
        "personagens": [],
        "cenarios": [
            {
                "id": "cen001",
                "nome": "Interface tech futurista",
                "descricao": "Fundo escuro quase preto, elementos holográficos ciano, código flutuante, circuitos",
                "elementos": ["HUD elements", "data streams", "circuit patterns", "glow effects"],
                "aprovado": True,
            }
        ],
        "estilo_prompt": (
            "futuristic tech channel, deep navy background #000D1A, cyan #00D4FF holographic elements, "
            "digital HUD overlay, circuit board patterns, no presenter, faceless AI channel, "
            "high contrast, 8K, professional CGI style"
        ),
        "proibido": [
            "logos de empresas de tecnologia reais",
            "código-fonte proprietário visível",
            "interfaces reais de produtos sem licença",
        ],
    },
    "v004": {
        "canal":   "Projeto Secreto",
        "nicho":   "misterio",
        "preset":  "misterio",
        "paleta": {
            "primaria":    "#8B0000",
            "secundaria":  "#CCCCCC",
            "fundo":       "#0A0A0A",
            "texto":       "#CCCCCC",
            "acento":      "#CC0000",
            "aviso":       "#FF0000",
        },
        "tipografia": {
            "titulo":  "Crimson Text / Bold",
            "corpo":   "Merriweather / Regular",
            "tamanho_titulo": 72,
            "tamanho_legenda": 48,
        },
        "cinematografia": {
            "aspect_ratio": "2.39:1",
            "letterbox":    True,
            "vinheta":      0.8,
            "grain":        0.06,
            "temperatura":  "neutra-fria (5000K) com realce vermelho",
            "contraste":    "extremo",
            "saturacao":    "quase monocromático com acento vermelho",
        },
        "personagens": [],
        "cenarios": [
            {
                "id": "cen001",
                "nome": "Arquivo classificado",
                "descricao": "Sala escura, documentos com CLASSIFIED/REDACTED, luz vermelha de alerta, sombras profundas",
                "elementos": ["carimbo vermelho", "pasta de documentos", "luz vermelha de emergência"],
                "aprovado": True,
            }
        ],
        "estilo_prompt": (
            "mystery conspiracy channel, near-black background #0A0A0A, dark red #8B0000 accents, "
            "extreme vignette, classified document aesthetic, dramatic shadows, letterbox 2.39:1, "
            "heavy grain, no presenter, faceless dark channel"
        ),
        "proibido": [
            "teorias conspiratórias apresentadas como fatos",
            "documentos governamentais reais classificados",
            "nomes de pessoas reais em contextos prejudiciais",
        ],
    },
    "v005": {
        "canal":   "AquaZen Relax",
        "nicho":   "natureza",
        "preset":  "natureza",
        "paleta": {
            "primaria":    "#2ECC71",
            "secundaria":  "#D5F5E3",
            "fundo":       "#001A0A",
            "texto":       "#D5F5E3",
            "acento":      "#1ABC9C",
            "aviso":       "#F39C12",
        },
        "tipografia": {
            "titulo":  "Raleway / Light",
            "corpo":   "Nunito / Regular",
            "tamanho_titulo": 72,
            "tamanho_legenda": 48,
        },
        "cinematografia": {
            "aspect_ratio": "16:9",
            "letterbox":    False,
            "vinheta":      0.5,
            "grain":        0.02,
            "temperatura":  "neutra-verde (5800K)",
            "contraste":    "suave",
            "saturacao":    "levemente aumentada nos verdes e turquesas",
        },
        "personagens": [],
        "cenarios": [
            {
                "id": "cen001",
                "nome": "Ambiente aquático natural",
                "descricao": "Água cristalina, reflexos de luz, folhagem verde, tons turquesa e verde-esmeralda",
                "elementos": ["água em movimento", "luz filtrada", "natureza intocada", "silêncio visual"],
                "aprovado": True,
            }
        ],
        "estilo_prompt": (
            "relaxation nature channel, deep green background #001A0A, emerald #2ECC71 and turquoise accents, "
            "crystal clear water, soft natural lighting, peaceful atmosphere, no presenter, "
            "faceless zen channel, high detail nature photography, 8K"
        ),
        "proibido": [
            "elementos urbanos ou industriais",
            "poluição ou degradação ambiental",
            "animais em situação de sofrimento",
        ],
    },
}

# ═════════════════════════════════════════════════════════════════════════════
# FUNÇÕES CORE
# ═════════════════════════════════════════════════════════════════════════════

def extrair_frame_referencia(vid_id: str, timestamp: float = 30.0) -> Path | None:
    """Extrai frame representativo do vídeo para uso como referência visual."""
    video_path = VIDEOS_FINAIS / f"{vid_id}_final.mp4"
    if not video_path.exists():
        print(f"  [CONSISTENCY] ⚠️  Vídeo não encontrado: {video_path}")
        return None

    frame_path = FRAMES_DIR / f"{vid_id}_ref_frame.jpg"

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        "-vf", "scale=1280:720",
        str(frame_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0 and frame_path.exists():
        sz = frame_path.stat().st_size / 1024
        print(f"  [CONSISTENCY] 🖼️  Frame extraído: {frame_path.name} ({sz:.0f}KB)")
        return frame_path
    else:
        print(f"  [CONSISTENCY] ⚠️  Falha ao extrair frame de {vid_id}")
        return None


def analisar_histograma(frame_path: Path) -> dict:
    """Analisa distribuição de cores do frame (histograma RGB)."""
    if not PIL_OK or not frame_path or not frame_path.exists():
        return {}

    img = Image.open(frame_path).convert("RGB")
    img_small = img.resize((320, 180))  # reduzir para performance

    r_vals = list(img_small.getdata(0))
    g_vals = list(img_small.getdata(1))
    b_vals = list(img_small.getdata(2))

    def stats(vals):
        n = len(vals)
        media = sum(vals) / n
        variancia = sum((v - media) ** 2 for v in vals) / n
        return {"media": round(media, 1), "desvio": round(math.sqrt(variancia), 1)}

    return {
        "r": stats(r_vals),
        "g": stats(g_vals),
        "b": stats(b_vals),
        "brilho_medio": round((sum(r_vals) + sum(g_vals) + sum(b_vals)) / (3 * len(r_vals)), 1),
    }


def score_consistencia(hist_a: dict, hist_b: dict) -> float:
    """Calcula score de similaridade entre dois histogramas (0-100)."""
    if not hist_a or not hist_b:
        return 0.0

    diferencas = []
    for canal in ("r", "g", "b"):
        if canal in hist_a and canal in hist_b:
            diff_media  = abs(hist_a[canal]["media"]  - hist_b[canal]["media"])
            diff_desvio = abs(hist_a[canal]["desvio"] - hist_b[canal]["desvio"])
            diferencas.append(diff_media + diff_desvio * 0.5)

    if not diferencas:
        return 0.0

    diff_total = sum(diferencas) / len(diferencas)
    score = max(0.0, 100.0 - diff_total)
    return round(score, 1)


def gerar_style_guide(nicho: str, vid_ids: list) -> Path:
    """Gera HTML do Style Guide visual para o nicho/canal."""
    print(f"  [CONSISTENCY] 📋 Gerando Style Guide: {nicho}...")

    # Coletar todos os dados dos canais deste nicho
    canais_nicho = {k: v for k, v in CANAIS_DB.items() if v["nicho"] == nicho and k in vid_ids}

    if not canais_nicho:
        canais_nicho = {k: v for k, v in CANAIS_DB.items() if k in vid_ids}

    # Pegar primeiro canal como referência
    ref_key = list(canais_nicho.keys())[0]
    ref = canais_nicho[ref_key]
    paleta = ref["paleta"]
    cine = ref["cinematografia"]

    # Gerar swatches HTML
    swatches_html = ""
    for nome, cor in paleta.items():
        # calcular luminância para decidir cor do texto no swatch
        h = cor.lstrip("#")
        r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        lum = 0.299*r + 0.587*g + 0.114*b
        txt_cor = "#000" if lum > 128 else "#FFF"
        swatches_html += f"""
        <div class="swatch">
          <div class="swatch-color" style="background:{cor};color:{txt_cor}">
            {cor}
          </div>
          <div class="swatch-name">{nome}</div>
        </div>"""

    # Gerar cenários
    cenarios_html = ""
    for cen in ref.get("cenarios", []):
        elementos = "".join(f"<li>{e}</li>" for e in cen.get("elementos", []))
        cenarios_html += f"""
        <div class="cenario-card">
          <h4>{cen['nome']}</h4>
          <p>{cen['descricao']}</p>
          <ul>{elementos}</ul>
        </div>"""

    # Gerar prompt box
    prompt_txt = ref.get("estilo_prompt", "")

    # Proibições
    proibido_html = "".join(f"<li>🚫 {p}</li>" for p in ref.get("proibido", []))

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Style Guide — {ref['canal']}</title>
<style>
  :root {{
    --bg: #111;
    --card: #1a1a1a;
    --border: #333;
    --text: #eee;
    --accent: {paleta['primaria']};
    --fundo-canal: {paleta['fundo']};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0 }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; padding: 2rem }}
  h1 {{ color: var(--accent); font-size: 2rem; margin-bottom: 0.3rem }}
  h2 {{ color: var(--accent); font-size: 1.2rem; margin: 2rem 0 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem }}
  h3 {{ color: #aaa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem }}
  .subtitle {{ color: #888; font-size: 0.9rem; margin-bottom: 2rem }}
  .section {{ margin-bottom: 2rem }}
  .swatches {{ display: flex; flex-wrap: wrap; gap: 1rem }}
  .swatch {{ width: 120px }}
  .swatch-color {{ height: 80px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-family: monospace; font-weight: bold }}
  .swatch-name {{ text-align: center; margin-top: 0.4rem; font-size: 0.8rem; color: #aaa; text-transform: capitalize }}
  .specs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem }}
  .spec-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1rem }}
  .spec-label {{ font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px }}
  .spec-value {{ font-size: 1rem; color: var(--text); margin-top: 0.25rem; font-weight: 600 }}
  .prompt-box {{ background: var(--fundo-canal); border: 1px solid var(--accent); border-radius: 8px; padding: 1.2rem; font-family: monospace; font-size: 0.85rem; color: {paleta['secundaria']}; line-height: 1.6 }}
  .cenario-card {{ background: var(--card); border-left: 3px solid var(--accent); border-radius: 0 8px 8px 0; padding: 1rem; margin-bottom: 1rem }}
  .cenario-card h4 {{ color: var(--accent); margin-bottom: 0.4rem }}
  .cenario-card p {{ color: #aaa; font-size: 0.9rem; margin-bottom: 0.5rem }}
  .cenario-card ul {{ color: #888; font-size: 0.85rem; padding-left: 1.2rem }}
  .proibido-list {{ list-style: none; padding: 0 }}
  .proibido-list li {{ padding: 0.4rem 0; border-bottom: 1px solid var(--border); font-size: 0.9rem }}
  .badge {{ display: inline-block; background: var(--accent); color: var(--fundo-canal); border-radius: 4px; padding: 0.15rem 0.5rem; font-size: 0.75rem; font-weight: bold; margin-left: 0.5rem }}
  .footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); color: #555; font-size: 0.8rem }}
</style>
</head>
<body>
<h1>🎨 {ref['canal']}</h1>
<p class="subtitle">Style Guide Visual — DARK STUDIO AAA | Nicho: {nicho.upper()} <span class="badge">v1.0</span></p>

<div class="section">
  <h2>🎨 Paleta de Cores</h2>
  <div class="swatches">{swatches_html}</div>
</div>

<div class="section">
  <h2>📐 Especificações Cinematográficas</h2>
  <div class="specs-grid">
    <div class="spec-card"><div class="spec-label">Aspect Ratio</div><div class="spec-value">{cine['aspect_ratio']}</div></div>
    <div class="spec-card"><div class="spec-label">Letterbox</div><div class="spec-value">{'Sim (2.39:1)' if cine['letterbox'] else 'Não'}</div></div>
    <div class="spec-card"><div class="spec-label">Vinheta</div><div class="spec-value">{int(cine['vinheta']*100)}%</div></div>
    <div class="spec-card"><div class="spec-label">Grain Cinematográfico</div><div class="spec-value">{int(cine['grain']*100)}%</div></div>
    <div class="spec-card"><div class="spec-label">Temperatura de Cor</div><div class="spec-value">{cine['temperatura']}</div></div>
    <div class="spec-card"><div class="spec-label">Contraste</div><div class="spec-value">{cine['contraste'].title()}</div></div>
    <div class="spec-card"><div class="spec-label">Saturação</div><div class="spec-value">{cine['saturacao'].title()}</div></div>
  </div>
</div>

<div class="section">
  <h2>✍️ Tipografia</h2>
  <div class="specs-grid">
    <div class="spec-card"><div class="spec-label">Título</div><div class="spec-value">{ref['tipografia']['titulo']}</div></div>
    <div class="spec-card"><div class="spec-label">Corpo / Legenda</div><div class="spec-value">{ref['tipografia']['corpo']}</div></div>
    <div class="spec-card"><div class="spec-label">Tamanho Título</div><div class="spec-value">{ref['tipografia']['tamanho_titulo']}px</div></div>
    <div class="spec-card"><div class="spec-label">Tamanho Legenda</div><div class="spec-value">{ref['tipografia']['tamanho_legenda']}px</div></div>
  </div>
</div>

<div class="section">
  <h2>🎬 Cenários Aprovados</h2>
  {cenarios_html}
</div>

<div class="section">
  <h2>🤖 Prompt de Consistência (IA Generativa)</h2>
  <div class="prompt-box">{prompt_txt}</div>
</div>

<div class="section">
  <h2>🚫 Elementos Proibidos</h2>
  <ul class="proibido-list">{proibido_html}</ul>
</div>

<div class="footer">
  Gerado por DARK VISUAL CONSISTENCY — DARK STUDIO AAA v1.4.0<br>
  ai_generated: true | ai_disclosure: "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"<br>
  {datetime.now().strftime('%Y-%m-%d %H:%M')}
</div>
</body>
</html>"""

    guide_path = GUIDES_DIR / f"style_guide_{nicho}.html"
    guide_path.write_text(html, encoding="utf-8")
    print(f"  [CONSISTENCY] ✅ Style Guide salvo: {guide_path.name}")
    return guide_path


def registrar_canal(vid_id: str) -> dict:
    """Registra o canal no banco de referências visuais e extrai frame."""
    print(f"\n{'═'*60}")
    print(f"  [CONSISTENCY] 🗄️  Registrando canal: {vid_id}")

    if vid_id not in CANAIS_DB:
        return {"erro": f"{vid_id} não cadastrado"}

    dados = CANAIS_DB[vid_id]

    # Extrair frame de referência
    frame = extrair_frame_referencia(vid_id, timestamp=30.0)

    # Analisar histograma
    histograma = analisar_histograma(frame) if frame else {}

    registro = {
        "vid_id":    vid_id,
        "canal":     dados["canal"],
        "nicho":     dados["nicho"],
        "timestamp": datetime.now().isoformat(),
        "frame_ref": str(frame) if frame else None,
        "histograma": histograma,
        "paleta":    dados["paleta"],
        "cinematografia": dados["cinematografia"],
        "estilo_prompt": dados["estilo_prompt"],
        "proibido":  dados["proibido"],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    if histograma:
        print(f"  [CONSISTENCY] 📊 Brilho médio: {histograma.get('brilho_medio')} | "
              f"R:{histograma['r']['media']:.0f} G:{histograma['g']['media']:.0f} B:{histograma['b']['media']:.0f}")

    return registro


def analisar_consistencia_entre(vid_a: str, vid_b: str) -> dict:
    """Compara consistência visual entre dois vídeos."""
    print(f"  [CONSISTENCY] 🔍 Comparando {vid_a} ↔ {vid_b}...")

    frame_a = extrair_frame_referencia(vid_a, 30.0)
    frame_b = extrair_frame_referencia(vid_b, 30.0)

    hist_a = analisar_histograma(frame_a)
    hist_b = analisar_histograma(frame_b)

    score = score_consistencia(hist_a, hist_b)

    resultado = {
        "vid_a": vid_a, "vid_b": vid_b,
        "score": score,
        "classificacao": (
            "excelente" if score >= 80 else
            "boa"        if score >= 60 else
            "regular"    if score >= 40 else
            "baixa"
        ),
        "hist_a": hist_a,
        "hist_b": hist_b,
    }

    icon = "✅" if score >= 60 else "⚠️ "
    print(f"  [CONSISTENCY] {icon} Score: {score}/100 ({resultado['classificacao']})")
    return resultado


def rodar_analise_completa() -> dict:
    """Registra todos os canais, extrai frames e gera todos os style guides."""
    print(f"\n{'╔'+'═'*58+'╗'}")
    print(f"║  🎨 DARK VISUAL CONSISTENCY — ANÁLISE COMPLETA         ║")
    print(f"{'╚'+'═'*58+'╝'}\n")

    registros = {}
    vid_ids = list(CANAIS_DB.keys())

    # 1. Registrar todos os canais
    for vid_id in vid_ids:
        registros[vid_id] = registrar_canal(vid_id)

    # 2. Gerar Style Guides por nicho
    nichos_vistos = set()
    guides_gerados = []
    for vid_id, dados in CANAIS_DB.items():
        nicho = dados["nicho"]
        if nicho not in nichos_vistos:
            guide = gerar_style_guide(nicho, vid_ids)
            guides_gerados.append(str(guide))
            nichos_vistos.add(nicho)

    # 3. Score de consistência entre vídeos do mesmo nicho
    scores = []
    # (todos são nichos diferentes nesta semana — comparamos sequencialmente)
    for i in range(len(vid_ids) - 1):
        sc = analisar_consistencia_entre(vid_ids[i], vid_ids[i+1])
        scores.append(sc)

    # 4. Salvar DB
    db = {
        "dark_studio_aaa": {
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "timestamp": datetime.now().isoformat(),
            "agentes": ["VISUAL CONSISTENCY", "ASSET MANAGER", "IMAGE ENGINE", "CREATIVE QA"],
        },
        "canais": registros,
        "style_guides": guides_gerados,
        "scores_consistencia": scores,
    }

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    # Resumo
    print(f"\n{'═'*60}")
    print(f"  📊 RESULTADO VISUAL CONSISTENCY:")
    for vid_id, reg in registros.items():
        brilho = reg.get("histograma", {}).get("brilho_medio", "—")
        print(f"  ✅ {vid_id}: {reg['canal']} | brilho={brilho}")
    print(f"  🎨 Style Guides: {len(guides_gerados)} gerados")
    print(f"  📄 DB: {DB_PATH}")
    print(f"{'═'*60}\n")

    return db


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="DARK VISUAL CONSISTENCY — Banco de referências visuais"
    )
    parser.add_argument("--registrar-canal",   metavar="VID_ID", help="Registrar canal no banco")
    parser.add_argument("--analisar-todos",    action="store_true", help="Análise completa de todos os canais")
    parser.add_argument("--style-guide",       metavar="NICHO", help="Gerar style guide de um nicho")
    parser.add_argument("--score-consistencia",nargs=2, metavar=("VID_A","VID_B"), help="Score entre dois vídeos")
    parser.add_argument("--listar",            action="store_true", help="Listar canais cadastrados")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║     DARK VISUAL CONSISTENCY — DARK STUDIO AAA v1.4.0       ║
║     AGENTE VISUAL CONSISTENCY + ASSET MANAGER ATIVADOS     ║
╚══════════════════════════════════════════════════════════════╝
""")

    if args.listar:
        for vid_id, dados in CANAIS_DB.items():
            print(f"  {vid_id}: {dados['canal']} [{dados['nicho']}]")
        return

    if args.registrar_canal:
        r = registrar_canal(args.registrar_canal)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return

    if args.style_guide:
        vid_ids = [k for k, v in CANAIS_DB.items() if v["nicho"] == args.style_guide]
        if not vid_ids:
            vid_ids = list(CANAIS_DB.keys())
        guide = gerar_style_guide(args.style_guide, vid_ids)
        print(f"Style Guide gerado: {guide}")
        return

    if args.score_consistencia:
        sc = analisar_consistencia_entre(*args.score_consistencia)
        print(json.dumps(sc, ensure_ascii=False, indent=2))
        return

    # Default: análise completa
    rodar_analise_completa()


if __name__ == "__main__":
    main()
