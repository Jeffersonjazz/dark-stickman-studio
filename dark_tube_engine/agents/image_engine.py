"""
DARK TUBE ENGINE — AGENTE IMAGE ENGINE
Geração, edição, tratamento e otimização de imagens
Clone funcional: vidiq_generate_thumbnail + upscaling + tratamento
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thumbnail_engine import gerar_thumbnail_pillow, gerar_pack_thumbnails
from typing import Optional


class ImageEngineAgent:
    """
    AGENTE IMAGE ENGINE — Criação e tratamento de imagens
    Capacidades: thumbnail, upscale, tratamento de cor, composição
    Stack: Pillow (gratuito, local, sem limites)
    """

    AGENT_ID = "image_engine"
    VERSION = "1.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "thumbnail" in tarefa:
            return self.gerar_thumbnail(payload)
        elif "pack" in tarefa:
            return self.gerar_pack(payload)
        else:
            return {"status": "erro", "mensagem": f"Tarefa não reconhecida: {tarefa}"}

    def gerar_thumbnail(self, payload: dict) -> dict:
        resultado = gerar_thumbnail_pillow(
            titulo=payload.get("titulo", "Sem título"),
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            subtitulo=payload.get("subtitulo", ""),
            tamanho=payload.get("tamanho", "thumbnail_horizontal"),
            emoji=payload.get("emoji", "")
        )
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def gerar_pack(self, payload: dict) -> dict:
        pack = gerar_pack_thumbnails(
            payload.get("titulo", "Sem título"),
            payload.get("canal", ""),
            payload.get("nicho")
        )
        return {
            "agente": self.AGENT_ID,
            "pack": pack,
            "total": 2,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        try:
            from PIL import Image
            pillow_ok = True
            pillow_version = Image.__version__
        except ImportError:
            pillow_ok = False
            pillow_version = "não instalado"

        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "pillow": pillow_ok,
            "pillow_version": pillow_version,
            "capacidades": ["thumbnail_horizontal", "thumbnail_shorts", "banner", "pack"],
            "custo": "GRATUITO — Pillow local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
