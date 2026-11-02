"""
DARK TUBE ENGINE — AGENTE CINEMATIC DIRECTOR
Direção de fotografia, composição, iluminação, enquadramentos e continuidade visual
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Presets cinematográficos por estilo
PRESETS_CINEMATOGRAFICOS = {
    "documentario": {
        "aspect_ratio": "16:9",
        "color_grade": "neutro realista",
        "iluminacao": "natural difusa",
        "movimentos": ["panorâmica lenta", "travelling suave", "plano estático"],
        "lut": "Rec709",
        "temperatura_cor": "5500K",
    },
    "terror": {
        "aspect_ratio": "16:9",
        "color_grade": "alto contraste frio",
        "iluminacao": "baixa chave lateral",
        "movimentos": ["câmera na mão leve", "zoom lento inquietante", "plano fechado"],
        "lut": "TealOrange_dark",
        "temperatura_cor": "3200K",
    },
    "motivacional": {
        "aspect_ratio": "9:16",
        "color_grade": "vibrante quente",
        "iluminacao": "high key frontal",
        "movimentos": ["zoom in energético", "cortes rápidos", "push in"],
        "lut": "Golden_warm",
        "temperatura_cor": "6500K",
    },
    "tech_ia": {
        "aspect_ratio": "16:9",
        "color_grade": "neon azul frio",
        "iluminacao": "LED azul lateral",
        "movimentos": ["câmera estática", "rack focus", "zoom digital lento"],
        "lut": "CyberpunkBlue",
        "temperatura_cor": "8000K",
    },
    "relaxamento": {
        "aspect_ratio": "16:9",
        "color_grade": "pastel suave",
        "iluminacao": "natural difusa suave",
        "movimentos": ["travelling lento", "plano aberto", "slow motion"],
        "lut": "SoftPastel",
        "temperatura_cor": "5600K",
    },
    "conspiracao": {
        "aspect_ratio": "16:9",
        "color_grade": "dessaturado esverdeado",
        "iluminacao": "baixa chave verde",
        "movimentos": ["câmera na mão agitada", "zoom rápido", "dutch angle"],
        "lut": "GreenGrade_dark",
        "temperatura_cor": "4000K",
    },
}

ENQUADRAMENTOS = {
    "abertura": ["plano geral", "plano estabelecimento"],
    "narrativa": ["plano médio", "plano americano", "plano detalhe"],
    "emoção": ["close up", "plano fechado", "extreme close up"],
    "contexto": ["plano geral", "plano panorâmico"],
    "encerramento": ["plano geral recuando", "fade out suave"],
}


class CinematicDirectorAgent:
    """
    AGENTE CINEMATIC DIRECTOR — Direção cinematográfica
    Gera prompts de câmera, enquadramentos e continuidade visual
    """

    AGENT_ID = "cinematic_director"
    VERSION = "1.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "composicao" in tarefa or "enquadramento" in tarefa:
            return self.gerar_composicao(payload)
        elif "continuidade" in tarefa:
            return self.plano_continuidade(payload)
        elif "prompt" in tarefa:
            return self.gerar_prompts_cena(payload)
        else:
            return self.gerar_composicao(payload)

    def gerar_composicao(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "documentario")
        preset = PRESETS_CINEMATOGRAFICOS.get(nicho, PRESETS_CINEMATOGRAFICOS["documentario"])
        script = payload.get("script", "")

        num_cenas = max(3, len(script.split(".")) // 3) if script else 5
        cenas = []
        tipos = list(ENQUADRAMENTOS.keys())
        for i in range(num_cenas):
            tipo = tipos[i % len(tipos)]
            cenas.append({
                "cena": i + 1,
                "tipo_plano": ENQUADRAMENTOS[tipo][0],
                "movimento": preset["movimentos"][i % len(preset["movimentos"])],
                "duracao_sugerida": "3-5s"
            })

        return {
            "agente": self.AGENT_ID,
            "nicho": nicho,
            "preset_cinematografico": preset,
            "cenas": cenas,
            "total_cenas": len(cenas),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def gerar_prompts_cena(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "documentario")
        titulo = payload.get("titulo", "")
        preset = PRESETS_CINEMATOGRAFICOS.get(nicho, PRESETS_CINEMATOGRAFICOS["documentario"])

        prompt_base = (
            f"Cinematic {nicho} style, {preset['color_grade']} color grade, "
            f"{preset['iluminacao']} lighting, {preset['temperatura_cor']} color temperature, "
            f"ultra realistic, 8K, professional photography, no text, no watermark"
        )

        return {
            "agente": self.AGENT_ID,
            "titulo": titulo,
            "nicho": nicho,
            "prompt_base": prompt_base,
            "prompt_negativo": "blurry, low quality, watermark, text overlay, cartoon, anime",
            "preset": preset,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def plano_continuidade(self, payload: dict) -> dict:
        return {
            "agente": self.AGENT_ID,
            "regras_continuidade": [
                "Manter mesma temperatura de cor entre cenas contínuas",
                "Manter direção de movimento consistente (regra dos 180°)",
                "Usar corte no movimento para fluidez",
                "Match cut para continuidade visual",
                "Manter proporção e posição dos elementos entre cortes",
            ],
            "checklist": [
                "Paleta de cores definida",
                "LUT aplicado uniformemente",
                "Direção de câmera consistente",
                "Iluminação coerente com horário da cena",
                "Personagens com mesmo vestuário por sequência",
            ],
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "presets_disponíveis": list(PRESETS_CINEMATOGRAFICOS.keys()),
            "capacidades": ["composicao", "enquadramento", "prompts_cena", "continuidade"],
            "custo": "GRATUITO — geração local de prompts e planos",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
