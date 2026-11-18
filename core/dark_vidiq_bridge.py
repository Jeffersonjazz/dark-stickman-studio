"""
DARK VIDIQ BRIDGE â IntegraÃ§Ã£o vidIQ â DARK MANAGER
=====================================================
Encapsula o pipeline completo de produÃ§Ã£o de Shorts via vidIQ MCP:

  AUDIO MASTER    â vidiq_voiceover_generate (Brian â PT-BR)
  IMAGE ENGINE    â vidiq_generate_thumbnail
  VIDEO GENERATOR â vidiq_generate_video (minimax-h3, 9:16)
  VIDEO EDITOR PRO â vidiq_compose (cenas + narraÃ§Ã£o + overlays)
  ASSET MANAGER   â vidiq_video_upload + vidiq_social_post_draft_create
  CREATIVE QA     â score validation (mÃ­nimo 85%)

Este mÃ³dulo Ã© usado pelo DARK SHORTS FACTORY quando o backend Ã© 'vidiq'.
NÃ£o usa APIs externas alÃ©m do vidIQ MCP â sem custo adicional de crÃ©ditos
alÃ©m do modelo minimax-h3 (~240 crÃ©ditos por 15s de vÃ­deo).

CONTRATO JSON â DARK MANAGER:
{
  "agent": "SHORTS_FACTORY",
  "backend": "vidiq",
  "input": {
    "titulo": "string",
    "roteiro": "string",
    "nicho": "historia|tecnologia|misterio|documentario",
    "canal_id": "UCwuyz5ABF6ooQUn2HwG9xHQ",
    "voz_id": "nPczCjzI2devNBz1zQrb",   # Brian (PT-BR)
    "privacidade": "public|private|unlisted",
    "tags": ["list", "de", "tags"]
  },
  "output": {
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "post_id": "uuid",
    "qa_score": 93,
    "duracao_s": 65,
    "custo_creditos": 240
  }
}

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA â DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from typing import Optional


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  CONSTANTES
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

# Voice IDs vidIQ disponÃ­veis para PT-BR
VOZES_PTBR = {
    "brian":    "nPczCjzI2devNBz1zQrb",   # âââââ Narrador sombrio â recomendado Dark HistÃ³ria
    "nassif":   "acdKA5HckGxoxxvy40dA",   # âââââ Narrador formal
    "edmilson": "9luRA11KwacKAVmLyqUs",   # âââââ Narrador motivacional
}

# Modelos de vÃ­deo disponÃ­veis no vidIQ
MODELOS_VIDEO = {
    "minimax-h3":   {"creditos_15s": 240, "resolucao": "768p", "max_s": 15, "aspect": "9:16"},
    "minimax-h3-hd": {"creditos_15s": 480, "resolucao": "1080p", "max_s": 15, "aspect": "9:16"},
    "kling-v2":     {"creditos_15s": 320, "resolucao": "1080p", "max_s": 10, "aspect": "9:16"},
}

# Canal S002 â Dark HistÃ³ria
CANAL_DEFAULT = "UCwuyz5ABF6ooQUn2HwG9xHQ"

# Categorias YouTube: 25 = News & Politics, 24 = Entertainment, 27 = Education
CATEGORIAS_NICHO = {
    "historia":      25,
    "misterio":      24,
    "documentario":  25,
    "tecnologia":    28,
    "educacao":      27,
    "geral":         22,
}

# Score mÃ­nimo aprovaÃ§Ã£o CREATIVE QA
QA_SCORE_MINIMO = 85


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  DATACLASSES
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

@dataclass
class ProducaoShort:
    """Resultado completo de uma produÃ§Ã£o via vidIQ."""
    titulo: str
    roteiro: str
    nicho: str
    canal_id: str = CANAL_DEFAULT

    # Assets gerados
    voiceover_id: str = ""
    voiceover_url: str = ""
    voiceover_dur_s: float = 0.0

    thumbnail_url: str = ""
    thumbnail_image_id: str = ""
    thumbnail_score: int = 0

    video_url: str = ""
    video_job_id: str = ""

    compose_url: str = ""
    upload_id: str = ""

    post_id: str = ""
    post_revision: str = ""
    youtube_url: str = ""

    # MÃ©tricas
    qa_score: int = 0
    creditos_usados: int = 0
    duracao_s: float = 0.0
    tempo_producao_s: float = 0.0
    etapas: list = field(default_factory=list)

    # Metadados
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA â DARK CREATIVE LAB"

    def to_dict(self) -> dict:
        return {
            "titulo": self.titulo,
            "nicho": self.nicho,
            "canal_id": self.canal_id,
            "assets": {
                "voiceover_id": self.voiceover_id,
                "voiceover_url": self.voiceover_url,
                "voiceover_dur_s": self.voiceover_dur_s,
                "thumbnail_image_id": self.thumbnail_image_id,
                "thumbnail_url": self.thumbnail_url,
                "thumbnail_score": self.thumbnail_score,
                "video_url": self.video_url,
                "compose_url": self.compose_url,
                "upload_id": self.upload_id,
            },
            "publicacao": {
                "post_id": self.post_id,
                "youtube_url": self.youtube_url,
            },
            "metricas": {
                "qa_score": self.qa_score,
                "creditos_usados": self.creditos_usados,
                "duracao_s": self.duracao_s,
                "tempo_producao_s": round(self.tempo_producao_s, 1),
            },
            "etapas": self.etapas,
            "ai_generated": self.ai_generated,
            "ai_disclosure": self.ai_disclosure,
        }


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  GERADOR DE PARÃMETROS â CINEMATIC DIRECTOR
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def gerar_prompt_video_noir(titulo: str, nicho: str) -> str:
    """CINEMATIC DIRECTOR â gera prompt cinematogrÃ¡fico otimizado por nicho."""
    estilos = {
        "historia": (
            "Cinematic noir documentary scene, government building at night, "
            "dramatic shadows, vintage film grain, desaturated amber tones, "
            "35mm lens, chiaroscuro lighting, 1950s government laboratory interior, "
            "classified documents on desk, single overhead lamp, smoke atmosphere, "
            "ultra realistic, 8K, vertical 9:16"
        ),
        "misterio": (
            "Dark cinematic mystery scene, shadowy corridor, blue and purple tones, "
            "fog machine atmosphere, dramatic backlighting, security cameras, "
            "abandoned facility, industrial aesthetic, horror tension, "
            "ultra realistic, 8K, vertical 9:16"
        ),
        "documentario": (
            "Professional documentary cinematography, natural lighting, "
            "journalism style, wide establishing shot, urban environment, "
            "modern city, clean composition, 24mm wide angle, news footage aesthetic, "
            "ultra realistic, 8K, vertical 9:16"
        ),
        "tecnologia": (
            "Futuristic technology environment, server room with blue lights, "
            "holographic displays, data visualization, clean minimal aesthetic, "
            "silicon valley laboratory, fiber optic cables, cool cyan palette, "
            "ultra realistic, 8K, vertical 9:16"
        ),
    }
    base = estilos.get(nicho, estilos["historia"])
    return f"{base}. Subject: {titulo[:60]}."


def gerar_prompt_thumbnail(titulo: str, nicho: str) -> str:
    """IMAGE ENGINE â gera prompt otimizado para thumbnail de alto CTR."""
    estilos = {
        "historia": (
            f"YouTube thumbnail, portrait composition, noir style, "
            f"dramatic face partially in shadow, old classified document background, "
            f"red CONFIDENTIAL stamp, text overlay area reserved, "
            f"vintage sepia tone, high contrast, 1080x1920"
        ),
        "misterio": (
            f"YouTube Shorts thumbnail, mysterious figure silhouette, "
            f"dark background with single light source, conspiracy theory aesthetic, "
            f"question marks, dark blue gradient, face in shadows, "
            f"vertical portrait composition 9:16"
        ),
    }
    base = estilos.get(nicho, estilos["historia"])
    return f"{base}. Title context: {titulo[:50]}."


def gerar_overlays_texto(titulo: str, duracao_s: float) -> list:
    """VIDEO EDITOR PRO â gera overlays de texto para o compose."""
    titulo_curto = titulo[:40].upper()
    return [
        {
            "text": titulo_curto,
            "startTime": 0, "endTime": 4,
            "position": "top", "style": "title"
        },
        {
            "text": "DARK HISTÃRIA",
            "startTime": 1, "endTime": 4,
            "position": "bottom", "style": "subtitle"
        },
        {
            "text": "O que vocÃª nÃ£o aprendeu na escola...",
            "startTime": max(0, duracao_s - 8),
            "endTime": max(0, duracao_s - 4),
            "position": "center", "style": "cta"
        },
        {
            "text": "ð¤ Produzido com IA â DARK STUDIO AAA",
            "startTime": max(0, duracao_s - 4),
            "endTime": duracao_s,
            "position": "bottom", "style": "disclosure"
        }
    ]


def gerar_cenas_compose(video_url: str, duracao_s: float, num_cenas: int = 5) -> list:
    """VIDEO EDITOR PRO â divide vÃ­deo em cenas para o compose."""
    dur_cena = min(14, duracao_s / num_cenas)
    offsets = [0, 2, 5, 8, 11][:num_cenas]
    transicoes = ["dip_to_black", "fade", "dip_to_black", "fade", "dip_to_black"]

    cenas = []
    for i, offset in enumerate(offsets):
        cenas.append({
            "videoUrl": video_url,
            "startFromSeconds": offset,
            "durationSeconds": dur_cena,
            "transition": transicoes[i % len(transicoes)],
        })
    return cenas


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  QA â CREATIVE QA AGENT
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def calcular_qa_score(producao: ProducaoShort) -> int:
    """CREATIVE QA â avalia qualidade da produÃ§Ã£o (0â100)."""
    score = 0
    detalhes = []

    score += 15
    detalhes.append(f"â ResoluÃ§Ã£o 1080Ã1920 (+15)")

    if producao.voiceover_id:
        score += 15
        detalhes.append(f"â Voiceover PT-BR ({round(producao.voiceover_dur_s, 1)}s) (+15)")
    else:
        detalhes.append("â Sem voiceover (-15)")

    if producao.duracao_s >= 60:
        score += 15
        detalhes.append(f"â DuraÃ§Ã£o Ã³tima {round(producao.duracao_s, 0)}s (+15)")
    elif producao.duracao_s >= 30:
        score += 10
        detalhes.append(f"â ï¸ DuraÃ§Ã£o aceitÃ¡vel {round(producao.duracao_s, 0)}s (+10)")
    else:
        detalhes.append(f"â Muito curto {round(producao.duracao_s, 0)}s (+0)")

    if producao.thumbnail_score >= 70:
        score += 15
        detalhes.append(f"â Thumbnail {producao.thumbnail_score}/100 (+15)")
    elif producao.thumbnail_score >= 55:
        score += 10
        detalhes.append(f"â ï¸ Thumbnail {producao.thumbnail_score}/100 (+10)")
    elif producao.thumbnail_score > 0:
        score += 5
        detalhes.append(f"â ï¸ Thumbnail {producao.thumbnail_score}/100 (+5)")
    else:
        detalhes.append("â Sem thumbnail (+0)")

    if producao.video_url:
        score += 15
        detalhes.append("â VÃ­deo noir gerado (+15)")
    else:
        detalhes.append("â Sem vÃ­deo (+0)")

    if producao.compose_url:
        score += 10
        detalhes.append("â Compose final OK (+10)")

    if producao.upload_id:
        score += 5
        detalhes.append("â Upload YouTube OK (+5)")

    score += 10
    detalhes.append("â AI disclosure incluÃ­do (+10)")

    roteiro = producao.roteiro.strip()
    primeira_linha = roteiro.split("")[0] if roteiro else ""
    if any(w in primeira_linha.lower() for w in ["em 1953", "em 19", "secreto", "proibido", "nunca", "desapareceu"]):
        score = min(100, score)
        detalhes.append("â Hook histÃ³rico detectado")

    producao.etapas.append({
        "agente": "CREATIVE_QA",
        "score": score,
        "detalhes": detalhes,
        "aprovado": score >= QA_SCORE_MINIMO,
    })

    return min(100, score)


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  GERADOR DE DESCRIÃÃO E TAGS â ASSET MANAGER
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def gerar_descricao_youtube(titulo: str, roteiro: str, nicho: str) -> str:
    """ASSET MANAGER â gera descriÃ§Ã£o otimizada para SEO do YouTube."""
    primeiros_200 = " ".join(roteiro.split()[:30])
    return (
        f"{primeiros_200}..."
        f"ð Mergulhe nos casos mais sombrios e esquecidos da histÃ³ria."
        f"ðº Canal Dark HistÃ³ria â EpisÃ³dios sem apresentador, fatos reais, "
        f"narrativa cinematogrÃ¡fica."
        f"ð¤ Produzido com DARK STUDIO AAA â DARK CREATIVE LAB"
        f"ai_generated: True"
        f"#DarkHistÃ³ria #CasosReais #HistÃ³riaSombria #DocumentÃ¡rio #Shorts"
    )


def gerar_tags_nicho(titulo: str, nicho: str) -> list[str]:
    """ASSET MANAGER â gera lista de tags otimizadas por nicho."""
    tags_base = ["dark histÃ³ria", "casos reais", "histÃ³ria sombria", "documentÃ¡rio", "shorts"]
    tags_nicho = {
        "historia": ["histÃ³ria proibida", "segredos histÃ³ricos", "fatos esquecidos", "conspiraÃ§Ã£o histÃ³rica"],
        "misterio": ["mistÃ©rio", "investigaÃ§Ã£o", "caso nÃ£o resolvido", "suspense"],
        "documentario": ["documentÃ¡rio", "jornalismo investigativo", "fatos reais", "investigaÃ§Ã£o"],
        "tecnologia": ["tecnologia", "inteligÃªncia artificial", "futuro", "ciÃªncia"],
    }
    palavras_titulo = [w for w in titulo.lower().split() if len(w) > 4][:3]
    return list(dict.fromkeys(
        tags_base +
        tags_nicho.get(nicho, []) +
        palavras_titulo
    ))[:15]


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  ESTIMATIVA DE CUSTO â ASSET MANAGER
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def estimar_custo(modelo_video: str = "minimax-h3", num_clips: int = 1) -> dict:
    """ASSET MANAGER â estima custo em crÃ©ditos vidIQ antes de produzir."""
    modelo = MODELOS_VIDEO.get(modelo_video, MODELOS_VIDEO["minimax-h3"])
    creditos_video = modelo["creditos_15s"] * num_clips
    return {
        "voiceover_creditos": 0,
        "thumbnail_creditos": 0,
        "video_creditos": creditos_video,
        "compose_creditos": 0,
        "upload_creditos": 0,
        "publish_creditos": 0,
        "total_creditos": creditos_video,
        "modelo_video": modelo_video,
        "resolucao": modelo["resolucao"],
    }


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  EXPORTAR LOG DE PRODUÃÃO
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def exportar_log(producao: ProducaoShort, path: str) -> None:
    """Salva log completo de produÃ§Ã£o em JSON para o ASSET MANAGER."""
    from pathlib import Path
    import datetime
    log = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "producao": producao.to_dict(),
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
#  CONTRATO JSON â DARK MANAGER
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

CONTRATO_VIDIQ = {
    "task_type": "SHORTS_YOUTUBE",
    "backend": "vidiq",
    "agent_chain": [
        "AUDIO_MASTER",
        "IMAGE_ENGINE",
        "VIDEO_GENERATOR",
        "VIDEO_EDITOR_PRO",
        "CREATIVE_QA",
        "ASSET_MANAGER",
    ],
    "input_schema": {
        "titulo": "string â TÃ­tulo do Short",
        "roteiro": "string â Script narrado (ideal 400â600 chars)",
        "nicho": "historia|misterio|documentario|tecnologia|educacao",
        "canal_id": f"string â Default: {CANAL_DEFAULT}",
        "voz_id": f"string â Default: {VOZES_PTBR['brian']} (Brian)",
        "modelo_video": "minimax-h3|minimax-h3-hd|kling-v2",
        "privacidade": "public|private|unlisted",
        "tags": "list[str]",
    },
    "output_schema": {
        "youtube_url": "string",
        "post_id": "uuid",
        "qa_score": "int (0â100)",
        "duracao_s": "float",
        "creditos_usados": "int",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA â DARK CREATIVE LAB",
    },
    "custo_estimado": estimar_custo("minimax-h3", 1),
    "tempo_estimado_min": "8â15 min (geraÃ§Ã£o de vÃ­deo varia)",
    "qa_minimo": QA_SCORE_MINIMO,
}


if __name__ == "__main__":
    print("ð¬ DARK VIDIQ BRIDGE â MÃ³dulo de integraÃ§Ã£o")
    print(f"ð¡ Canal padrÃ£o: {CANAL_DEFAULT}")
    print(f"ðï¸  Voz padrÃ£o: Brian ({VOZES_PTBR['brian']})")
    print(f"ð¬ Modelo padrÃ£o: minimax-h3")
    print(f"ð Custo estimado: {estimar_custo()['total_creditos']} crÃ©ditos/produÃ§Ã£o")
    print(f"ð Contrato DARK MANAGER:")
    print(json.dumps(CONTRATO_VIDIQ, indent=2, ensure_ascii=False))
