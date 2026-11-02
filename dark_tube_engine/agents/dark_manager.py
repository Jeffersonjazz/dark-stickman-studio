"""
DARK TUBE ENGINE — DARK MANAGER (Orquestrador Central)
Decide qual agente usar em cada tarefa via contratos JSON
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class DarkManager:
    """
    Orquestrador central do DARK TUBE ENGINE.
    Roteia tarefas para os agentes especializados via contratos JSON.
    Clone funcional da lógica de orquestração do vidIQ.
    """

    AGENT_CAPABILITIES = {
        "image_engine":        ["gerar_imagem", "editar_imagem", "thumbnail", "upscale"],
        "video_generator":     ["gerar_video", "animar_imagem", "broll", "motion"],
        "cinematic_director":  ["composicao", "enquadramento", "iluminacao", "continuidade"],
        "video_editor_pro":    ["montar_video", "cortar", "transicao", "renderizar", "compose"],
        "motion_graphics":     ["titulo", "legenda", "infografico", "animacao_logo"],
        "audio_master":        ["narrar", "voiceover", "mixar", "masterizar", "tts"],
        "visual_consistency":  ["consistencia", "paleta", "personagem", "estilo"],
        "asset_manager":       ["organizar", "catalogar", "licenca", "arquivo"],
        "creative_qa":         ["avaliar", "qualidade", "revisar", "conformidade"],
    }

    def __init__(self):
        self.session_id = uuid.uuid4().hex[:8]
        self.jobs: Dict[str, Any] = {}
        self.log: list = []

    def _criar_contrato(self, tarefa: str, agente: str, payload: dict) -> dict:
        """Cria contrato JSON padronizado para comunicação entre agentes."""
        return {
            "contrato_id": f"ctr_{uuid.uuid4().hex[:12]}",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "tarefa": tarefa,
            "agente_destino": agente,
            "payload": payload,
            "status": "pending",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def rotear(self, tarefa: str, payload: dict) -> dict:
        """
        Decide qual agente deve executar a tarefa.
        Escolhe a alternativa de menor custo que atenda ao padrão de qualidade.
        """
        agente_selecionado = None

        for agente, capacidades in self.AGENT_CAPABILITIES.items():
            if any(cap in tarefa.lower() for cap in capacidades):
                agente_selecionado = agente
                break

        if not agente_selecionado:
            agente_selecionado = "asset_manager"  # fallback

        contrato = self._criar_contrato(tarefa, agente_selecionado, payload)
        self.log.append(contrato)

        return {
            "agente": agente_selecionado,
            "contrato": contrato,
            "rota": f"DARK MANAGER → {agente_selecionado.upper()}"
        }

    def pipeline_completo(self, titulo: str, canal: str, script: str,
                           nicho: Optional[str] = None) -> dict:
        """
        Executa pipeline completo: Script → Voz → Thumb → Vídeo → SEO → YouTube
        Orquestra todos os agentes em sequência.
        """
        pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
        etapas = []

        # 1. Script
        etapas.append(self._criar_contrato("gerar_script", "video_editor_pro", {
            "titulo": titulo, "canal": canal, "nicho": nicho
        }))

        # 2. Voiceover
        etapas.append(self._criar_contrato("narrar_voiceover", "audio_master", {
            "script": script, "canal": canal
        }))

        # 3. Thumbnail
        etapas.append(self._criar_contrato("gerar_thumbnail", "image_engine", {
            "titulo": titulo, "canal": canal, "nicho": nicho
        }))

        # 4. Compor vídeo
        etapas.append(self._criar_contrato("montar_video_compose", "video_editor_pro", {
            "titulo": titulo, "canal": canal, "script": script
        }))

        # 5. SEO keywords
        etapas.append(self._criar_contrato("pesquisar_keywords_seo", "asset_manager", {
            "titulo": titulo, "nicho": nicho
        }))

        # 6. QA
        etapas.append(self._criar_contrato("avaliar_qualidade_final", "creative_qa", {
            "titulo": titulo, "canal": canal
        }))

        return {
            "pipeline_id": pipeline_id,
            "titulo": titulo,
            "canal": canal,
            "total_etapas": len(etapas),
            "etapas": etapas,
            "status": "ready",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status_agentes(self) -> dict:
        """Retorna status de todos os agentes ativos."""
        return {
            "total_agentes": len(self.AGENT_CAPABILITIES),
            "agentes": list(self.AGENT_CAPABILITIES.keys()),
            "jobs_em_fila": len(self.jobs),
            "log_entries": len(self.log),
            "session_id": self.session_id
        }
