"""
DARK TUBE ENGINE — AGENTE VISUAL CONSISTENCY
Mantém identidade visual, personagens, ambientes, paleta de cores e estilo entre cenas
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


PALETAS_NICHO = {
    "motivacional":  {"primaria": "#FF6B35", "secundaria": "#FFD700", "fundo": "#1a1a2e", "texto": "#FFFFFF"},
    "terror":        {"primaria": "#8B0000", "secundaria": "#4B0082", "fundo": "#0a0a0a", "texto": "#CCCCCC"},
    "tech_ia":       {"primaria": "#00D4FF", "secundaria": "#7C3AED", "fundo": "#07070f", "texto": "#E0E0E0"},
    "conspiracao":   {"primaria": "#4CAF50", "secundaria": "#795548", "fundo": "#1B1B1B", "texto": "#B8B8B8"},
    "relaxamento":   {"primaria": "#4FC3F7", "secundaria": "#81C784", "fundo": "#E8F5E9", "texto": "#333333"},
    "documentario":  {"primaria": "#5C6BC0", "secundaria": "#29B6F6", "fundo": "#121212", "texto": "#EEEEEE"},
}

ESTILOS_FOTOGRAFIA = {
    "motivacional":  "high_key_warm_vibrant",
    "terror":        "low_key_cold_desaturated",
    "tech_ia":       "neon_cyberpunk_blue",
    "conspiracao":   "green_tint_film_grain",
    "relaxamento":   "soft_natural_pastel",
    "documentario":  "neutral_realistic_4K",
}


class VisualConsistencyAgent:
    """
    AGENTE VISUAL CONSISTENCY — Manutenção de identidade visual
    Cria e mantém banco de referências visuais por projeto
    """

    AGENT_ID = "visual_consistency"
    VERSION = "1.0.0"

    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.referencias_dir = self.base_dir / "referencias"
        self.referencias_dir.mkdir(parents=True, exist_ok=True)
        self.projetos: Dict[str, Any] = {}

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "consistencia" in tarefa or "paleta" in tarefa:
            return self.gerar_guia_visual(payload)
        elif "personagem" in tarefa:
            return self.registrar_personagem(payload)
        elif "estilo" in tarefa:
            return self.definir_estilo_projeto(payload)
        else:
            return self.gerar_guia_visual(payload)

    def gerar_guia_visual(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "documentario")
        canal = payload.get("canal", "")
        paleta = PALETAS_NICHO.get(nicho, PALETAS_NICHO["documentario"])
        estilo = ESTILOS_FOTOGRAFIA.get(nicho, ESTILOS_FOTOGRAFIA["documentario"])

        guia = {
            "projeto_id": f"proj_{uuid.uuid4().hex[:8]}",
            "canal": canal,
            "nicho": nicho,
            "paleta_cores": paleta,
            "estilo_fotografia": estilo,
            "regras": [
                f"Usar apenas cores da paleta definida: {paleta}",
                f"Manter estilo fotográfico: {estilo}",
                "Todos os personagens devem manter mesma aparência entre cenas",
                "Iluminação consistente com horário narrativo",
                "Proporções e escala dos elementos mantidos",
                "Não apresentar cenas sintéticas como documentais reais",
                "Identificar conteúdo produzido por IA quando necessário",
            ],
            "disclosure_obrigatorio": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
        return {"agente": self.AGENT_ID, "guia_visual": guia}

    def registrar_personagem(self, payload: dict) -> dict:
        personagem_id = f"char_{uuid.uuid4().hex[:8]}"
        personagem = {
            "id": personagem_id,
            "nome": payload.get("nome", "Personagem"),
            "descricao": payload.get("descricao", ""),
            "aparencia": payload.get("aparencia", {}),
            "vestuario": payload.get("vestuario", {}),
            "prompt_base": payload.get("prompt_base", ""),
            "registrado_em": datetime.now().isoformat(),
            "nota": "Manter consistência visual entre todas as cenas com este personagem"
        }

        ref_path = self.referencias_dir / f"personagem_{personagem_id}.json"
        with open(ref_path, "w", encoding="utf-8") as f:
            json.dump(personagem, f, ensure_ascii=False, indent=2)

        return {
            "agente": self.AGENT_ID,
            "personagem_id": personagem_id,
            "personagem": personagem,
            "arquivo": str(ref_path),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def definir_estilo_projeto(self, payload: dict) -> dict:
        projeto_id = payload.get("projeto_id", f"proj_{uuid.uuid4().hex[:8]}")
        nicho = payload.get("nicho", "documentario")

        estilo = {
            "projeto_id": projeto_id,
            "nicho": nicho,
            "paleta": PALETAS_NICHO.get(nicho, PALETAS_NICHO["documentario"]),
            "fotografia": ESTILOS_FOTOGRAFIA.get(nicho, ESTILOS_FOTOGRAFIA["documentario"]),
            "definido_em": datetime.now().isoformat()
        }

        self.projetos[projeto_id] = estilo
        return {
            "agente": self.AGENT_ID,
            "projeto_id": projeto_id,
            "estilo": estilo,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "nichos_configurados": list(PALETAS_NICHO.keys()),
            "projetos_ativos": len(self.projetos),
            "capacidades": ["paleta_cores", "estilo_fotografia", "registro_personagens", "guia_visual"],
            "custo": "GRATUITO — sistema local de referências",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
