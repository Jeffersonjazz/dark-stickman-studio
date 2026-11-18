"""
DARK HIGGSFIELD BRIDGE — Integração Higgsfield ↔ DARK IMAGE STUDIO
====================================================================
Bridge para geração de imagens premium via Higgsfield AI (MCP).

Backends Higgsfield disponíveis:
  gpt_image_2_6         — modelo padrão — fotorrealista, tipografia, edição
  gpt_image_2_6_flare   — variante com GIF/SVG nativo
  marketing_studio_image — produto/comercial/ads
  soul_cast             — personagens/avatares (texto apenas)
  soul_2                — retratos/editorial/fashion/UGC

Funcionalidades MCP disponíveis:
  mcp__Higgsfield__generate_image      → texto → imagem
  mcp__Higgsfield__generate_image_batch → batch independente
  mcp__Higgsfield__upscale_image       → 2K / 4K upscale
  mcp__Higgsfield__remove_background   → remoção de fundo
  mcp__Higgsfield__outpaint_image      → extensão de imagem
  mcp__Higgsfield__estimate_image_cost → estimativa de custo

CONTRATO JSON — DARK MANAGER:
{
  "agent": "IMAGE_ENGINE",
  "backend": "higgsfield",
  "input": {
    "prompt": "string",
    "nicho": "natureza|historia|tecnologia|misterio|motivacao",
    "resolucao": "youtube_thumbnail|shorts|wallpaper_hd|square",
    "modelo": "gpt_image_2_6",
    "operacao": "gerar|upscale|remove_bg|outpaint"
  },
  "output": {
    "image_path": "/path/to/image.png",
    "job_id": "uuid",
    "resolucao": "1280x720",
    "custo_creditos": 10,
    "backend": "higgsfield",
    "ai_generated": true
  }
}

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
#  MODELOS E CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════════════════

MODELOS_HIGGSFIELD = {
    "padrao":     {"id": "gpt_image_2_6",          "qualidade": 9, "custo": "médio"},
    "flare":      {"id": "gpt_image_2_6_flare",     "qualidade": 9, "custo": "médio", "suporta_gif": True},
    "marketing":  {"id": "marketing_studio_image",  "qualidade": 9, "custo": "alto",  "nicho": "comercial"},
    "personagem": {"id": "soul_cast",               "qualidade": 9, "custo": "médio", "nicho": "avatar"},
    "retrato":    {"id": "soul_2",                  "qualidade": 9, "custo": "médio", "nicho": "fashion"},
}

# Resoluções mapeadas para aspect ratio Higgsfield
RESOLUCOES_HIGGSFIELD = {
    "youtube_thumbnail": {"w": 1280, "h": 720,  "aspect": "16:9"},
    "youtube_banner":    {"w": 2560, "h": 1440, "aspect": "16:9"},
    "shorts":            {"w": 1080, "h": 1920, "aspect": "9:16"},
    "wallpaper_hd":      {"w": 1920, "h": 1080, "aspect": "16:9"},
    "square":            {"w": 1024, "h": 1024, "aspect": "1:1"},
    "portrait":          {"w": 768,  "h": 1344, "aspect": "9:16"},
    "landscape":         {"w": 1344, "h": 768,  "aspect": "16:9"},
    "instagram_post":    {"w": 1080, "h": 1080, "aspect": "1:1"},
    "instagram_story":   {"w": 1080, "h": 1920, "aspect": "9:16"},
    "wallpaper_4k":      {"w": 3840, "h": 2160, "aspect": "16:9"},
}

# Score mínimo aprovação CREATIVE QA para imagens Higgsfield
QA_SCORE_MINIMO_IMAGEM = 80


# ═══════════════════════════════════════════════════════════════════
#  DATACLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ProducaoImagem:
    """Resultado de geração de imagem via Higgsfield."""
    prompt: str
    nicho: str
    resolucao: str = "youtube_thumbnail"
    modelo: str = "gpt_image_2_6"
    operacao: str = "gerar"

    # Resultado
    job_id: str = ""
    image_path: str = ""
    image_url: str = ""
    largura: int = 0
    altura: int = 0

    # Metadados
    qa_score: int = 0
    custo_creditos: int = 0
    duracao_s: float = 0.0
    backend_usado: str = "higgsfield"
    fallback_usado: bool = False
    etapas: list = field(default_factory=list)

    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

    def to_dict(self) -> dict:
        res_info = RESOLUCOES_HIGGSFIELD.get(self.resolucao, {})
        return {
            "prompt": self.prompt,
            "nicho": self.nicho,
            "resolucao": self.resolucao,
            "modelo": self.modelo,
            "operacao": self.operacao,
            "assets": {
                "job_id": self.job_id,
                "image_path": self.image_path,
                "image_url": self.image_url,
                "largura": self.largura or res_info.get("w", 1280),
                "altura": self.altura or res_info.get("h", 720),
            },
            "metricas": {
                "qa_score": self.qa_score,
                "custo_creditos": self.custo_creditos,
                "duracao_s": round(self.duracao_s, 1),
                "backend_usado": self.backend_usado,
                "fallback_usado": self.fallback_usado,
            },
            "etapas": self.etapas,
            "ai_generated": self.ai_generated,
            "ai_disclosure": self.ai_disclosure,
        }


# ═══════════════════════════════════════════════════════════════════
#  CINEMATIC DIRECTOR — PROMPTS POR NICHO
# ═══════════════════════════════════════════════════════════════════

ESTILOS_CINEMATICOS = {
    "natureza": {
        "prefixo": (
            "Cinematic nature photography, ultra-realistic, 8K, "
            "golden hour natural light, Sony A7R IV, f/1.8 bokeh, "
            "National Geographic quality, vivid colors, "
        ),
        "sufixo": ", pristine, majestic, breathtaking composition",
        "neg": "cartoon, anime, painting, blur, watermark, text, artificial",
    },
    "historia": {
        "prefixo": (
            "Historical documentary photography, cinematic, "
            "dramatic chiaroscuro lighting, period-accurate details, "
            "film grain, desaturated amber tones, "
        ),
        "sufixo": ", vintage aesthetic, archival quality, profound atmosphere",
        "neg": "modern elements, cartoon, anime, watermark, text, colorful",
    },
    "tecnologia": {
        "prefixo": (
            "Futuristic technology concept art, photorealistic CGI, "
            "blue and cyan neon lighting, clean minimalist aesthetic, "
            "8K, server room or laboratory environment, "
        ),
        "sufixo": ", innovative, precise, cutting-edge visualization",
        "neg": "cartoon, anime, watermark, text, old technology, retro",
    },
    "misterio": {
        "prefixo": (
            "Dark mysterious cinematic scene, noir atmosphere, "
            "dramatic shadows and highlights, fog machine effect, "
            "thriller movie still, single-source dramatic lighting, "
        ),
        "sufixo": ", suspenseful, psychological tension, 8K, ultra-detailed",
        "neg": "bright, cheerful, cartoon, anime, watermark, colorful",
    },
    "motivacao": {
        "prefixo": (
            "Inspirational cinematic landscape, epic wide angle, "
            "golden hour light rays, powerful composition, "
            "motivational atmosphere, dramatic sky, "
        ),
        "sufixo": ", uplifting, grand scale, cinematic color grade",
        "neg": "sad, dark, cartoon, anime, watermark, text",
    },
    "psicologia": {
        "prefixo": (
            "Conceptual surrealist psychology scene, dreamlike atmosphere, "
            "symbolic imagery, dramatic lighting, "
        ),
        "sufixo": ", thought-provoking, cinematic, mind-bending composition",
        "neg": "cartoon, anime, watermark, text, literal",
    },
    "documentario": {
        "prefixo": (
            "Professional documentary photography, natural journalism lighting, "
            "wide establishing shot, authentic atmosphere, "
        ),
        "sufixo": ", reportage style, honest, compelling visual story",
        "neg": "cartoon, anime, watermark, text, staged",
    },
    "dark_channel": {
        "prefixo": (
            "Dark cinematic YouTube channel aesthetic, noir style, "
            "high contrast black and deep shadows, mysterious atmosphere, "
        ),
        "sufixo": ", dramatic, premium production quality, channel branding",
        "neg": "bright, cheerful, cartoon, anime, watermark",
    },
    "geral": {
        "prefixo": "Cinematic photography, ultra-realistic, professional, dramatic lighting, 8K, ",
        "sufixo": ", premium quality, compelling composition",
        "neg": "cartoon, anime, watermark, text, blur, low quality",
    },
}

ESTILOS_THUMBNAIL = {
    "youtube_padrao": (
        "YouTube thumbnail, eye-catching, high contrast, "
        "bold composition, text space reserved top/bottom, "
        "dramatic lighting, 1280x720, "
    ),
    "shorts_padrao": (
        "YouTube Shorts thumbnail, vertical 9:16 composition, "
        "face or striking visual center frame, "
        "dark gradient edges, bold visual hook, "
    ),
    "dark_history": (
        "YouTube thumbnail dark channel, noir style, "
        "mysterious figure or dramatic scene, "
        "classified/secreto aesthetic, red and black color scheme, "
        "vintage degraded look, 'CONFIDENTIAL' stamp aesthetic, "
    ),
    "dark_mystery": (
        "YouTube thumbnail mystery channel, shadowy silhouette, "
        "question mark visual, conspiracy aesthetic, "
        "dark blue gradient, face partially hidden, "
    ),
}


def enriquecer_prompt_imagem(
    prompt: str,
    nicho: str = "geral",
    operacao: str = "gerar",
    resolucao: str = "youtube_thumbnail",
) -> dict:
    """
    CINEMATIC DIRECTOR — Enriquece prompt com estilo cinematográfico.
    Retorna dict com prompt_positivo e prompt_negativo otimizados.
    """
    estilo = ESTILOS_CINEMATICOS.get(nicho, ESTILOS_CINEMATICOS["geral"])
    res_info = RESOLUCOES_HIGGSFIELD.get(resolucao, RESOLUCOES_HIGGSFIELD["youtube_thumbnail"])

    aspect_nota = f", {res_info['aspect']} aspect ratio"
    prompt_completo = f"{estilo['prefixo']}{prompt}{estilo['sufixo']}{aspect_nota}"

    return {
        "prompt": prompt_completo,
        "negative_prompt": estilo["neg"],
        "aspect_ratio": res_info["aspect"],
        "largura": res_info["w"],
        "altura": res_info["h"],
    }


def gerar_prompt_thumbnail_higgsfield(
    titulo: str,
    nicho: str = "dark_channel",
    canal: str = "DARK STUDIO AAA",
) -> str:
    """
    IMAGE ENGINE — Gera prompt otimizado para thumbnail de alto CTR via Higgsfield.
    Baseado em análise de thumbnails de alto desempenho por nicho.
    """
    base = ESTILOS_THUMBNAIL.get(f"dark_{nicho}", ESTILOS_THUMBNAIL["youtube_padrao"])
    return (
        f"{base}"
        f"channel: {canal}, "
        f"subject context: {titulo[:60]}, "
        f"photorealistic, ultra-detailed, 8K quality, "
        f"professional YouTube creator style"
    )


def gerar_prompt_banner_canal(
    nome_canal: str,
    nicho: str = "dark_channel",
    slogan: str = "",
) -> str:
    """IMAGE ENGINE — Prompt para banner de canal YouTube 2560x1440."""
    return (
        f"YouTube channel banner, ultra-wide 16:9, professional design, "
        f"dark cinematic aesthetic, channel name '{nome_canal}' space reserved center, "
        f"{'slogan: ' + slogan + ', ' if slogan else ''}"
        f"dramatic backdrop, premium production quality, "
        f"{ESTILOS_CINEMATICOS.get(nicho, ESTILOS_CINEMATICOS['geral'])['prefixo']}"
        f"2560x1440 resolution, horizontal banner format"
    )


def gerar_prompt_thumbnail_serie(
    titulo: str,
    numero_episodio: int,
    serie: str,
    nicho: str = "historia",
) -> str:
    """
    IMAGE ENGINE — Prompt de thumbnail para série (consistência visual entre episódios).
    Mantém identidade visual da série com variação de cena por episódio.
    """
    estilo = ESTILOS_CINEMATICOS.get(nicho, ESTILOS_CINEMATICOS["geral"])
    return (
        f"{estilo['prefixo']}"
        f"YouTube thumbnail for episode {numero_episodio} of series '{serie}', "
        f"series visual identity: dark cinematic noir, "
        f"episode content: {titulo[:50]}, "
        f"dramatic scene composition, "
        f"bold typography space reserved, 1280x720"
    )


# ═══════════════════════════════════════════════════════════════════
#  QA — CREATIVE QA AGENT PARA IMAGENS
# ═══════════════════════════════════════════════════════════════════

def calcular_qa_imagem(producao: ProducaoImagem) -> int:
    """
    CREATIVE QA — Avalia qualidade de imagem gerada (0–100).
    Baseado em: backend usado, resolução, prompt quality, fallback.
    """
    score = 0
    detalhes = []

    # Backend quality score
    if producao.backend_usado == "higgsfield":
        score += 30
        detalhes.append("✅ Backend Higgsfield premium (+30)")
    elif producao.backend_usado in ("FLUX.1-schnell", "SDXL", "SD 1.5"):
        score += 20
        detalhes.append(f"✅ Backend HF {producao.backend_usado} (+20)")
    elif producao.backend_usado == "placeholder_pillow":
        score += 5
        detalhes.append("⚠️ Backend Pillow fallback (+5)")

    # Image file exists
    if producao.image_path:
        score += 20
        detalhes.append("✅ Arquivo gerado (+20)")

    # Job ID (Higgsfield confirmed)
    if producao.job_id:
        score += 15
        detalhes.append("✅ Job ID confirmado (+15)")

    # Prompt quality (length heuristic)
    if len(producao.prompt) >= 100:
        score += 15
        detalhes.append("✅ Prompt detalhado (+15)")
    elif len(producao.prompt) >= 50:
        score += 10
        detalhes.append("⚠️ Prompt médio (+10)")
    else:
        score += 5
        detalhes.append("⚠️ Prompt curto (+5)")

    # No fallback used
    if not producao.fallback_usado:
        score += 10
        detalhes.append("✅ Sem fallback necessário (+10)")

    # AI disclosure
    if producao.ai_generated:
        score += 10
        detalhes.append("✅ AI disclosure incluído (+10)")

    score = min(100, score)
    producao.etapas.append({
        "agente": "CREATIVE_QA",
        "score": score,
        "detalhes": detalhes,
        "aprovado": score >= QA_SCORE_MINIMO_IMAGEM,
    })

    return score


# ═══════════════════════════════════════════════════════════════════
#  ESTIMATIVA DE CUSTO
# ═══════════════════════════════════════════════════════════════════

CUSTO_ESTIMADO_HIGGSFIELD = {
    "gerar_imagem":       {"creditos": 10,  "descricao": "Geração de imagem (gpt_image_2_6)"},
    "gerar_thumbnail":    {"creditos": 10,  "descricao": "Thumbnail YouTube"},
    "gerar_shorts_thumb": {"creditos": 10,  "descricao": "Thumbnail Shorts 9:16"},
    "upscale_2k":         {"creditos": 15,  "descricao": "Upscale 2K"},
    "upscale_4k":         {"creditos": 25,  "descricao": "Upscale 4K"},
    "remove_bg":          {"creditos": 5,   "descricao": "Remoção de fundo"},
    "outpaint":           {"creditos": 15,  "descricao": "Extensão de imagem"},
    "batch_4":            {"creditos": 40,  "descricao": "Batch 4 imagens"},
}


def estimar_custo_imagem(operacoes: list[str]) -> dict:
    """ASSET MANAGER — Estima custo em créditos antes de produzir imagens."""
    total = 0
    detalhes = []
    for op in operacoes:
        info = CUSTO_ESTIMADO_HIGGSFIELD.get(op, {"creditos": 10, "descricao": op})
        total += info["creditos"]
        detalhes.append(f"{op}: {info['creditos']} créditos — {info['descricao']}")
    return {
        "operacoes": operacoes,
        "total_creditos": total,
        "detalhes": detalhes,
        "alternativa_gratuita": "HuggingFace FLUX.1-schnell (qualidade 8/10)",
        "fallback_offline": "Pillow gradient (qualidade 3/10)",
    }


# ═══════════════════════════════════════════════════════════════════
#  PLAN DE PRODUÇÃO IMAGENS — DARK IMAGE STUDIO
# ═══════════════════════════════════════════════════════════════════

def planejar_producao_imagens(
    cenas: list[dict],
    nicho: str = "geral",
    resolucao: str = "wallpaper_hd",
    usar_higgsfield: bool = True,
) -> dict:
    """
    CINEMATIC DIRECTOR — Plano completo de geração de imagens para pipeline F02.
    Retorna prompts enriquecidos + estimativa de custo + plano de execução.
    """
    prompts_cenas = []
    for i, cena in enumerate(cenas):
        prompt_base = cena.get("prompt_visual") or cena.get("descricao_visual", "")
        if not prompt_base:
            narracao = cena.get("narracao", cena.get("texto", ""))
            prompt_base = f"cinematic scene for: {narracao[:80]}"

        enriquecido = enriquecer_prompt_imagem(
            prompt=prompt_base,
            nicho=nicho,
            resolucao=resolucao,
        )
        prompts_cenas.append({
            "cena_id": cena.get("id", f"cena_{i+1:02d}"),
            "cena_index": i,
            "prompt_base": prompt_base,
            "prompt_higgsfield": enriquecido["prompt"],
            "negative_prompt": enriquecido["negative_prompt"],
            "aspect_ratio": enriquecido["aspect_ratio"],
            "largura": enriquecido["largura"],
            "altura": enriquecido["altura"],
            "modelo_recomendado": "gpt_image_2_6",
        })

    n_cenas = len(prompts_cenas)
    operacoes = ["gerar_imagem"] * n_cenas

    return {
        "n_cenas": n_cenas,
        "nicho": nicho,
        "resolucao": resolucao,
        "backend_preferido": "higgsfield" if usar_higgsfield else "hf_api",
        "backend_fallback": "hf_api",
        "backend_offline": "pillow",
        "cenas": prompts_cenas,
        "custo_estimado": estimar_custo_imagem(operacoes),
        "modelo": "gpt_image_2_6",
    }


# ═══════════════════════════════════════════════════════════════════
#  EXPORTAR LOG DE PRODUÇÃO
# ═══════════════════════════════════════════════════════════════════

def exportar_log_imagem(producao: ProducaoImagem, path: str) -> None:
    """Salva log completo em JSON para o ASSET MANAGER."""
    from pathlib import Path
    import datetime
    log = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "producao": producao.to_dict(),
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════
#  CONTRATO JSON — DARK MANAGER
# ═══════════════════════════════════════════════════════════════════

CONTRATO_HIGGSFIELD_IMAGE = {
    "task_type": "GERAR_IMAGEM",
    "backend": "higgsfield",
    "agent_chain": [
        "CINEMATIC_DIRECTOR",   # enriquecer prompt
        "IMAGE_ENGINE",         # gerar via Higgsfield MCP
        "CREATIVE_QA",          # avaliar qualidade
        "ASSET_MANAGER",        # salvar e catalogar
    ],
    "input_schema": {
        "prompt": "string — Descrição visual base",
        "nicho": "natureza|historia|tecnologia|misterio|motivacao|psicologia|documentario|dark_channel|geral",
        "resolucao": "youtube_thumbnail|shorts|wallpaper_hd|square|portrait|landscape",
        "modelo": "gpt_image_2_6|marketing_studio_image|soul_cast|soul_2",
        "operacao": "gerar|upscale|remove_bg|outpaint|batch",
    },
    "output_schema": {
        "image_path": "string — caminho local do arquivo gerado",
        "job_id": "uuid — ID do job Higgsfield",
        "resolucao": "1280x720",
        "custo_creditos": "int",
        "backend": "higgsfield",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    },
    "custo_estimado": estimar_custo_imagem(["gerar_imagem"]),
    "qa_minimo": QA_SCORE_MINIMO_IMAGEM,
    "fallback_cascade": [
        "1. Higgsfield gpt_image_2_6 (qualidade: 9/10, custo: ~10 créditos)",
        "2. HuggingFace FLUX.1-schnell (qualidade: 8/10, custo: R$0,00)",
        "3. HuggingFace SDXL (qualidade: 8/10, custo: R$0,00)",
        "4. Pillow gradient (qualidade: 3/10, custo: R$0,00, offline)",
    ],
}


if __name__ == "__main__":
    print("🎨 DARK HIGGSFIELD BRIDGE — Módulo de integração Higgsfield ↔ DARK IMAGE STUDIO")
    print(f"\n📊 Custo estimado (1 imagem): {estimar_custo_imagem(['gerar_imagem'])['total_creditos']} créditos")
    print(f"\n🎬 Modelos disponíveis:")
    for nome, info in MODELOS_HIGGSFIELD.items():
        print(f"   {nome}: {info['id']} — qualidade {info['qualidade']}/10")
    print(f"\n📐 Resoluções suportadas:")
    for nome, res in RESOLUCOES_HIGGSFIELD.items():
        print(f"   {nome}: {res['w']}x{res['h']} ({res['aspect']})")
    print(f"\n📋 Contrato DARK MANAGER:")
    print(json.dumps(CONTRATO_HIGGSFIELD_IMAGE, indent=2, ensure_ascii=False))
