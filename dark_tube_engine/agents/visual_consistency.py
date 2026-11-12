"""
DARK TUBE ENGINE — AGENTE VISUAL CONSISTENCY v2.0
Mantém identidade visual, personagens, ambientes, paleta de cores e estilo entre cenas
Integrado com BancoReferencias do CinematicDirector

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────────────────────
# PALETAS POR NICHO
# ─────────────────────────────────────────────────────────────
PALETAS_NICHO: Dict[str, Dict] = {
    "motivacional": {
        "primaria":   "#FF6B35",
        "secundaria": "#FFD700",
        "acento":     "#FF4500",
        "fundo":      "#1a1a2e",
        "texto":      "#FFFFFF",
        "descricao":  "laranja quente energético sobre escuro profundo"
    },
    "terror": {
        "primaria":   "#8B0000",
        "secundaria": "#4B0082",
        "acento":     "#2d0000",
        "fundo":      "#0a0a0a",
        "texto":      "#CCCCCC",
        "descricao":  "vermelho sangue e roxo sombrio"
    },
    "tech_ia": {
        "primaria":   "#00D4FF",
        "secundaria": "#7C3AED",
        "acento":     "#00FFCC",
        "fundo":      "#07070f",
        "texto":      "#E0E0E0",
        "descricao":  "ciano neon e violeta digital sobre preto profundo"
    },
    "conspiracao": {
        "primaria":   "#4CAF50",
        "secundaria": "#795548",
        "acento":     "#33691E",
        "fundo":      "#1B1B1B",
        "texto":      "#B8B8B8",
        "descricao":  "verde fosco e marrom desgastado sobre cinza escuro"
    },
    "relaxamento": {
        "primaria":   "#4FC3F7",
        "secundaria": "#81C784",
        "acento":     "#F8BBD9",
        "fundo":      "#E8F5E9",
        "texto":      "#333333",
        "descricao":  "azul suave e verde menta, tons pastel"
    },
    "documentario": {
        "primaria":   "#5C6BC0",
        "secundaria": "#29B6F6",
        "acento":     "#FF7043",
        "fundo":      "#121212",
        "texto":      "#EEEEEE",
        "descricao":  "azul índigo sério, acentos laranja jornalístico"
    },
    "historia": {
        "primaria":   "#8D6E63",
        "secundaria": "#A1887F",
        "acento":     "#D4A25B",
        "fundo":      "#2C1810",
        "texto":      "#F5DEB3",
        "descricao":  "sépia e dourado envelhecido, pergaminho"
    },
    "educacao": {
        "primaria":   "#1565C0",
        "secundaria": "#43A047",
        "acento":     "#F9A825",
        "fundo":      "#FFFFFF",
        "texto":      "#212121",
        "descricao":  "azul educacional, verde positivo, amarelo destaque"
    },
}

# ─────────────────────────────────────────────────────────────
# ESTILOS DE FOTOGRAFIA
# ─────────────────────────────────────────────────────────────
ESTILOS_FOTOGRAFIA: Dict[str, Dict] = {
    "motivacional":  {
        "nome":         "High Key Warm Vibrant",
        "prompt":       "high key lighting, warm golden tones, vibrant saturated colors, energetic",
        "temperatura":  "6500K",
        "contraste":    "médio",
        "saturacao":    "+20",
    },
    "terror": {
        "nome":         "Low Key Cold Desaturated",
        "prompt":       "low key dramatic lighting, cold blue tones, deep shadows, desaturated",
        "temperatura":  "3200K",
        "contraste":    "alto",
        "saturacao":    "-30",
    },
    "tech_ia": {
        "nome":         "Neon Cyberpunk Blue",
        "prompt":       "neon blue rim light, cyberpunk aesthetic, LED glow, dark background, digital particles",
        "temperatura":  "9000K",
        "contraste":    "alto",
        "saturacao":    "+15",
    },
    "conspiracao": {
        "nome":         "Green Tint Film Grain",
        "prompt":       "green tinted desaturated, film grain, conspiracy noir, harsh shadows",
        "temperatura":  "4000K",
        "contraste":    "muito alto",
        "saturacao":    "-20",
    },
    "relaxamento": {
        "nome":         "Soft Natural Pastel",
        "prompt":       "soft natural lighting, pastel colors, gentle bokeh, serene atmosphere",
        "temperatura":  "5800K",
        "contraste":    "baixo",
        "saturacao":    "-10",
    },
    "documentario": {
        "nome":         "Neutral Realistic 4K",
        "prompt":       "natural realistic lighting, neutral color grading, documentary style, 4K sharp",
        "temperatura":  "5500K",
        "contraste":    "médio-baixo",
        "saturacao":    "neutro",
    },
    "historia": {
        "nome":         "Film Grain Sepia",
        "prompt":       "film grain 35mm, sepia warm tones, Rembrandt lighting, historical reconstruction",
        "temperatura":  "4800K",
        "contraste":    "médio-alto",
        "saturacao":    "-25",
    },
    "educacao": {
        "nome":         "Educational Clean Bright",
        "prompt":       "clean bright lighting, modern classroom aesthetic, vibrant accent colors",
        "temperatura":  "6000K",
        "contraste":    "médio-baixo",
        "saturacao":    "+10",
    },
}

# ─────────────────────────────────────────────────────────────
# REGRAS DE CONSISTÊNCIA VISUAL
# ─────────────────────────────────────────────────────────────
REGRAS_CONSISTENCIA = [
    "Usar exclusivamente cores da paleta aprovada para o projeto",
    "Aplicar mesmo LUT/color grade em toda a produção",
    "Manter temperatura de cor consistente (±200K entre cenas da mesma sequência)",
    "Personagens devem ter aparência e vestuário idênticos entre cortes",
    "Iluminação deve ser coerente com horário e local estabelecidos",
    "Proporções e escala dos objetos devem ser mantidas entre cenas",
    "Direção de câmera deve respeitar a regra dos 180°",
    "Cenas sintéticas NÃO devem ser apresentadas como documentais reais",
    "Identificar conteúdo produzido por IA quando exigido pela plataforma",
    "Manter paleta aprovada consistente em thumbnails e materiais de divulgação",
]


# ─────────────────────────────────────────────────────────────
# AGENTE PRINCIPAL
# ─────────────────────────────────────────────────────────────
class VisualConsistencyAgent:
    """
    AGENTE VISUAL CONSISTENCY v2.0 — Manutenção de identidade visual
    - Paletas de cor por nicho com tokens HEX
    - Estilos de fotografia por nicho
    - Registro de personagens com referências visuais
    - Guia visual por projeto
    - Verificação de conformidade de estilo
    """

    AGENT_ID = "visual_consistency"
    VERSION = "2.0.0"

    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.referencias_dir = self.base_dir / "referencias"
        self.referencias_dir.mkdir(parents=True, exist_ok=True)
        self.projetos: Dict[str, Any] = {}

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "").lower()
        payload = contrato.get("payload", {})

        roteamento = {
            "guia_visual":        self.gerar_guia_visual,
            "paleta":             self.obter_paleta,
            "personagem":         self.registrar_personagem,
            "cenario":            self.registrar_cenario,
            "estilo":             self.definir_estilo_projeto,
            "verificar":          self.verificar_conformidade,
            "conformidade":       self.verificar_conformidade,
            "listar_nichos":      self.listar_nichos,
            "status":             lambda p: self.status(),
        }

        for chave, metodo in roteamento.items():
            if chave in tarefa:
                return metodo(payload)

        return self.gerar_guia_visual(payload)

    def gerar_guia_visual(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "documentario")
        canal = payload.get("canal", "")
        projeto_id = payload.get("projeto_id", f"proj_{uuid.uuid4().hex[:8]}")

        paleta = PALETAS_NICHO.get(nicho, PALETAS_NICHO["documentario"])
        estilo = ESTILOS_FOTOGRAFIA.get(nicho, ESTILOS_FOTOGRAFIA["documentario"])

        guia = {
            "projeto_id": projeto_id,
            "canal": canal,
            "nicho": nicho,
            "paleta_cores": paleta,
            "estilo_fotografia": estilo,
            "regras": REGRAS_CONSISTENCIA,
            "tokens_css": self._gerar_tokens_css(paleta, nicho),
            "disclosure_obrigatorio": True,
            "criado_em": datetime.now().isoformat(),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

        # Salvar guia em disco
        guia_path = self.referencias_dir / f"guia_{projeto_id}.json"
        with open(guia_path, "w", encoding="utf-8") as f:
            json.dump(guia, f, ensure_ascii=False, indent=2)

        return {"agente": self.AGENT_ID, "guia_visual": guia, "arquivo": str(guia_path)}

    def _gerar_tokens_css(self, paleta: dict, nicho: str) -> str:
        """Gera variáveis CSS com tokens da paleta."""
        return (
            f":root {{\n"
            f"  --color-primary:   {paleta['primaria']};\n"
            f"  --color-secondary: {paleta['secundaria']};\n"
            f"  --color-accent:    {paleta.get('acento', paleta['secundaria'])};\n"
            f"  --color-bg:        {paleta['fundo']};\n"
            f"  --color-text:      {paleta['texto']};\n"
            f"  /* {nicho}: {paleta.get('descricao', '')} */\n"
            f"}}"
        )

    def obter_paleta(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "documentario")
        paleta = PALETAS_NICHO.get(nicho, PALETAS_NICHO["documentario"])
        estilo = ESTILOS_FOTOGRAFIA.get(nicho, ESTILOS_FOTOGRAFIA["documentario"])
        return {
            "agente": self.AGENT_ID,
            "nicho": nicho,
            "paleta": paleta,
            "tokens_css": self._gerar_tokens_css(paleta, nicho),
            "estilo_fotografia": estilo,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def registrar_personagem(self, payload: dict) -> dict:
        personagem_id = f"char_{uuid.uuid4().hex[:8]}"
        personagem = {
            "id": personagem_id,
            "nome": payload.get("nome", "Personagem"),
            "descricao": payload.get("descricao", ""),
            "aparencia": payload.get("aparencia", {}),
            "vestuario": payload.get("vestuario", ""),
            "prompt_base": payload.get("prompt_base", ""),
            "prompt_consistencia": payload.get("prompt_consistencia", payload.get("prompt_base", "")),
            "nicho": payload.get("nicho", "documentario"),
            "registrado_em": datetime.now().isoformat(),
            "nota": "Incluir prompt_consistencia em todos os prompts com este personagem",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

        ref_path = self.referencias_dir / f"personagem_{personagem_id}.json"
        with open(ref_path, "w", encoding="utf-8") as f:
            json.dump(personagem, f, ensure_ascii=False, indent=2)

        return {
            "agente": self.AGENT_ID,
            "personagem_id": personagem_id,
            "personagem": personagem,
            "arquivo": str(ref_path),
            "instrucao": f"Adicionar '{personagem['prompt_consistencia']}' em todos os prompts com {personagem['nome']}",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def registrar_cenario(self, payload: dict) -> dict:
        cenario_id = f"scene_{uuid.uuid4().hex[:8]}"
        cenario = {
            "id": cenario_id,
            "nome": payload.get("nome", "Cenário"),
            "descricao": payload.get("descricao", ""),
            "prompt_cenario": payload.get("prompt_cenario", ""),
            "horario": payload.get("horario", "dia"),
            "clima": payload.get("clima", "bom"),
            "iluminacao_ref": payload.get("iluminacao", ""),
            "nicho": payload.get("nicho", "documentario"),
            "registrado_em": datetime.now().isoformat(),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

        ref_path = self.referencias_dir / f"cenario_{cenario_id}.json"
        with open(ref_path, "w", encoding="utf-8") as f:
            json.dump(cenario, f, ensure_ascii=False, indent=2)

        return {
            "agente": self.AGENT_ID,
            "cenario_id": cenario_id,
            "cenario": cenario,
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
            "tokens_css": self._gerar_tokens_css(
                PALETAS_NICHO.get(nicho, PALETAS_NICHO["documentario"]), nicho
            ),
            "definido_em": datetime.now().isoformat(),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

        self.projetos[projeto_id] = estilo

        # Persistir
        est_path = self.referencias_dir / f"estilo_{projeto_id}.json"
        with open(est_path, "w", encoding="utf-8") as f:
            json.dump(estilo, f, ensure_ascii=False, indent=2)

        return {
            "agente": self.AGENT_ID,
            "projeto_id": projeto_id,
            "estilo": estilo,
            "arquivo": str(est_path),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def verificar_conformidade(self, payload: dict) -> dict:
        """Verifica se assets/prompts estão em conformidade com o estilo do projeto."""
        nicho = payload.get("nicho", "documentario")
        prompts_verificar = payload.get("prompts", [])
        alertas = []
        aprovados = []

        paleta = PALETAS_NICHO.get(nicho, {})
        estilo = ESTILOS_FOTOGRAFIA.get(nicho, {})

        for i, prompt in enumerate(prompts_verificar):
            prompt_lower = prompt.lower()
            # Verificar se estilo do nicho está presente
            estilo_keywords = estilo.get("prompt", "").lower().split(", ")
            encontrou = any(kw in prompt_lower for kw in estilo_keywords[:3])
            if encontrou:
                aprovados.append(f"Prompt {i+1}: estilo '{nicho}' identificado")
            else:
                alertas.append(f"Prompt {i+1}: estilo '{nicho}' pode não estar presente — adicionar: {estilo.get('prompt', '')}")

        return {
            "agente": self.AGENT_ID,
            "nicho": nicho,
            "total_prompts": len(prompts_verificar),
            "aprovados": aprovados,
            "alertas": alertas,
            "status": "aprovado" if not alertas else "revisao_necessaria",
            "regras_aplicadas": REGRAS_CONSISTENCIA[:5],
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def listar_nichos(self, payload: dict) -> dict:
        return {
            "agente": self.AGENT_ID,
            "nichos_disponíveis": list(PALETAS_NICHO.keys()),
            "paletas": {n: p.get("descricao", "") for n, p in PALETAS_NICHO.items()},
            "estilos": {n: e.get("nome", "") for n, e in ESTILOS_FOTOGRAFIA.items()},
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        personagens = list(self.referencias_dir.glob("personagem_*.json"))
        cenarios = list(self.referencias_dir.glob("cenario_*.json"))
        estilos = list(self.referencias_dir.glob("estilo_*.json"))

        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "nichos_configurados": list(PALETAS_NICHO.keys()),
            "total_nichos": len(PALETAS_NICHO),
            "projetos_ativos": len(self.projetos),
            "personagens_registrados": len(personagens),
            "cenarios_registrados": len(cenarios),
            "estilos_salvos": len(estilos),
            "capacidades": [
                "paleta_cores_por_nicho",
                "tokens_css_automaticos",
                "estilo_fotografia_por_nicho",
                "registro_personagens",
                "registro_cenarios",
                "guia_visual_por_projeto",
                "verificacao_conformidade",
            ],
            "custo": "GRATUITO — sistema local de referências visuais",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
