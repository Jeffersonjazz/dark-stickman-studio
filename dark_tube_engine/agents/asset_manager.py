"""
DARK TUBE ENGINE — AGENTE ASSET MANAGER
Administra imagens, vídeos, músicas, fontes, licenças e arquivos de produção
Clone funcional: vidiq_keyword_research + catalogação de assets
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import json
import os
import uuid
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.keyword_engine import (
    calcular_score_titulo, pesquisar_palavras_chave_youtube,
    analisar_tendencias_nicho
)


class AssetManagerAgent:
    """
    AGENTE ASSET MANAGER — Catalogação e gestão de assets
    + Pesquisa de keywords e tendências (clone vidiq_keyword_research)
    """

    AGENT_ID = "asset_manager"
    VERSION = "1.0.0"

    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.catalog_path = self.base_dir / "catalog.json"
        self.catalog = self._carregar_catalogo()

    def _carregar_catalogo(self) -> dict:
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"assets": [], "total": 0, "ultima_atualizacao": None}

    def _salvar_catalogo(self):
        self.catalog["ultima_atualizacao"] = datetime.now().isoformat()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump(self.catalog, f, ensure_ascii=False, indent=2)

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "organizar" in tarefa or "catalogar" in tarefa:
            return self.catalogar_asset(payload)
        elif "keyword" in tarefa or "pesquisar" in tarefa:
            return self.pesquisar_keywords(payload)
        elif "tendencias" in tarefa:
            return self.tendencias_nicho(payload)
        elif "score" in tarefa or "titulo" in tarefa:
            return self.score_titulo(payload)
        elif "listar" in tarefa:
            return self.listar_assets(payload)
        else:
            return self.listar_assets(payload)

    def catalogar_asset(self, payload: dict) -> dict:
        asset_id = f"ast_{uuid.uuid4().hex[:8]}"
        asset = {
            "id": asset_id,
            "tipo": payload.get("tipo", "desconhecido"),
            "path": payload.get("path", ""),
            "titulo": payload.get("titulo", ""),
            "canal": payload.get("canal", ""),
            "nicho": payload.get("nicho", ""),
            "tags": payload.get("tags", []),
            "licenca": payload.get("licenca", "ai_generated"),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "criado_em": datetime.now().isoformat()
        }
        self.catalog["assets"].append(asset)
        self.catalog["total"] = len(self.catalog["assets"])
        self._salvar_catalogo()

        return {
            "agente": self.AGENT_ID,
            "asset_id": asset_id,
            "asset": asset,
            "total_catalog": self.catalog["total"],
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def pesquisar_keywords(self, payload: dict) -> dict:
        resultado = pesquisar_palavras_chave_youtube(
            termo=payload.get("termo", ""),
            api_key=payload.get("api_key"),
            max_results=payload.get("max_results", 10)
        )
        resultado["agente"] = self.AGENT_ID
        resultado["clone_de"] = "vidiq_keyword_research"
        return resultado

    def tendencias_nicho(self, payload: dict) -> dict:
        nicho = payload.get("nicho", "tech_ia")
        resultado = analisar_tendencias_nicho(nicho)
        resultado["agente"] = self.AGENT_ID
        return resultado

    def score_titulo(self, payload: dict) -> dict:
        resultado = calcular_score_titulo(payload.get("titulo", ""))
        resultado["agente"] = self.AGENT_ID
        resultado["clone_de"] = "vidiq_score_title"
        return resultado

    def listar_assets(self, payload: dict) -> dict:
        filtro_tipo = payload.get("tipo")
        filtro_canal = payload.get("canal")

        assets = self.catalog["assets"]
        if filtro_tipo:
            assets = [a for a in assets if a.get("tipo") == filtro_tipo]
        if filtro_canal:
            assets = [a for a in assets if a.get("canal") == filtro_canal]

        return {
            "agente": self.AGENT_ID,
            "total": len(assets),
            "assets": assets[-20:],  # últimos 20
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "total_assets": self.catalog["total"],
            "capacidades": ["catalogar", "keyword_research", "score_titulo", "tendencias"],
            "custo": "GRATUITO — YouTube API v3 + análise local",
            "clone_de": "vidiq_keyword_research + vidiq_score_title",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
