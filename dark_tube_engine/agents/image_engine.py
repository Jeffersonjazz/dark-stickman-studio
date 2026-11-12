"""
DARK TUBE ENGINE — AGENTE IMAGE ENGINE v2.0
Fase 2: DARK IMAGE STUDIO — FLUX.1-schnell + BiRefNet + upscaling + Pillow fallback
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Hierarquia de backends (ordem de preferência):
1. FLUX.1-schnell via HuggingFace Space (gratuito, alta qualidade)
2. Pillow local (gratuito, funcionalidade básica, sem GPU)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.thumbnail_engine import gerar_thumbnail_pillow, gerar_pack_thumbnails
from typing import Optional


# Importação condicional do cliente HF
try:
    from core.hf_image_client import (
        gerar_imagem_flux,
        remover_fundo,
        upscale_imagem,
        gerar_thumbnail_ia,
        comprimir_thumbnail_youtube,
        status_hf_image_client,
    )
    HF_CLIENT_AVAILABLE = True
except ImportError:
    HF_CLIENT_AVAILABLE = False


class ImageEngineAgent:
    """
    AGENTE IMAGE ENGINE v2.0 — DARK IMAGE STUDIO
    Capacidades Fase 2:
    - Geração por texto (FLUX.1-schnell / Pillow fallback)
    - Thumbnails YouTube com compressão <2MB automática
    - Remoção de fundo (BiRefNet)
    - Upscaling (Kontext-Unblur-Upscale LoRA)
    - Pack de variações de thumbnail

    Stack: FLUX.1-schnell HF Space (gratuito) + Pillow (gratuito, local)
    """

    AGENT_ID = "image_engine"
    VERSION = "2.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        roteamento = {
            "thumbnail":          self.gerar_thumbnail,
            "thumbnail_ia":       self.gerar_thumbnail_ia,
            "thumbnail_comprimir": self.comprimir_thumbnail,
            "pack":               self.gerar_pack,
            "texto_para_imagem":  self.texto_para_imagem,
            "remover_fundo":      self.remover_fundo,
            "upscale":            self.upscale,
            "status":             lambda p: self.status(),
        }

        for chave, func in roteamento.items():
            if chave in tarefa:
                return func(payload)

        return {"status": "erro", "mensagem": f"Tarefa não reconhecida: {tarefa}"}

    # ------------------------------------------------------------------
    # Thumbnail Pillow (local, sem IA externa)
    # ------------------------------------------------------------------

    def gerar_thumbnail(self, payload: dict) -> dict:
        """Thumbnail local via Pillow — rápido, sem dependências externas."""
        resultado = gerar_thumbnail_pillow(
            titulo=payload.get("titulo", "Sem título"),
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            subtitulo=payload.get("subtitulo", ""),
            tamanho=payload.get("tamanho", "thumbnail_horizontal"),
            emoji=payload.get("emoji", ""),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["backend"] = "pillow_local"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    # ------------------------------------------------------------------
    # Thumbnail IA (FLUX + upscale + compressão <2MB)
    # ------------------------------------------------------------------

    def gerar_thumbnail_ia(self, payload: dict) -> dict:
        """
        Thumbnail YouTube via FLUX.1-schnell + upscaling + compressão JPEG <2MB.
        Requer gradio_client e conexão com HuggingFace.
        Fallback para Pillow se HF não disponível.
        """
        if not HF_CLIENT_AVAILABLE:
            fallback = self.gerar_thumbnail(payload)
            fallback["aviso"] = "HF client indisponível — gerado com Pillow local"
            return fallback

        prompt = payload.get("prompt")
        if not prompt:
            # Constrói prompt automático a partir do título/canal
            titulo = payload.get("titulo", "")
            canal = payload.get("canal", "")
            nicho = payload.get("nicho", "documentary")
            prompt = (
                f"YouTube thumbnail, {titulo}, {canal} channel, "
                f"{nicho} style, dramatic lighting, dark background, "
                "cinematic, 4K, vibrant colors, eye-catching"
            )

        resultado = gerar_thumbnail_ia(
            prompt=prompt,
            output_dir=payload.get("output_dir", "outputs/thumbnails"),
            aplicar_upscale=payload.get("aplicar_upscale", True),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["backend"] = "flux_hf"
        resultado["prompt_usado"] = prompt
        return resultado

    # ------------------------------------------------------------------
    # Compressor standalone (PNG → JPEG <2MB para YouTube)
    # ------------------------------------------------------------------

    def comprimir_thumbnail(self, payload: dict) -> dict:
        """Comprime thumbnail existente para <2MB (limite YouTube)."""
        if not HF_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "hf_image_client não disponível"}

        caminho = payload.get("caminho") or payload.get("path")
        if not caminho:
            return {"status": "erro", "mensagem": "payload.caminho é obrigatório"}

        resultado = comprimir_thumbnail_youtube(
            caminho_entrada=caminho,
            output_dir=payload.get("output_dir"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Pack de thumbnails (horizontal + shorts)
    # ------------------------------------------------------------------

    def gerar_pack(self, payload: dict) -> dict:
        """Gera pack horizontal + shorts via Pillow local."""
        pack = gerar_pack_thumbnails(
            payload.get("titulo", "Sem título"),
            payload.get("canal", ""),
            payload.get("nicho"),
        )
        return {
            "agente": self.AGENT_ID,
            "pack": pack,
            "total": len(pack),
            "backend": "pillow_local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ------------------------------------------------------------------
    # Texto para imagem genérica (FLUX)
    # ------------------------------------------------------------------

    def texto_para_imagem(self, payload: dict) -> dict:
        """
        Gera imagem a partir de texto via FLUX.1-schnell.
        Fallback: retorna erro instruindo instalar gradio_client.
        """
        if not HF_CLIENT_AVAILABLE:
            return {
                "status": "erro",
                "mensagem": "gradio_client não instalado. Execute: pip install gradio_client",
                "alternativa": "Use gerar_thumbnail para geração local com Pillow",
            }

        resultado = gerar_imagem_flux(
            prompt=payload.get("prompt", "cinematic landscape, dark, dramatic"),
            largura=payload.get("largura", 1280),
            altura=payload.get("altura", 720),
            passos=payload.get("passos", 4),
            seed=payload.get("seed"),
            output_dir=payload.get("output_dir", "outputs/images"),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Remoção de fundo
    # ------------------------------------------------------------------

    def remover_fundo(self, payload: dict) -> dict:
        """Remove fundo de imagem via BiRefNet."""
        if not HF_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "gradio_client não instalado."}

        caminho = payload.get("imagem") or payload.get("caminho") or payload.get("path")
        if not caminho:
            return {"status": "erro", "mensagem": "payload.imagem é obrigatório"}

        resultado = remover_fundo(
            imagem=caminho,
            output_dir=payload.get("output_dir", "outputs/images"),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Upscaling
    # ------------------------------------------------------------------

    def upscale(self, payload: dict) -> dict:
        """Upscaling via Photo-Mate-i2i + Kontext-Unblur-Upscale LoRA."""
        if not HF_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "gradio_client não instalado."}

        caminho = payload.get("imagem") or payload.get("caminho") or payload.get("path")
        if not caminho:
            return {"status": "erro", "mensagem": "payload.imagem é obrigatório"}

        resultado = upscale_imagem(
            imagem=caminho,
            prompt=payload.get("prompt", "sharp, high resolution, detailed, photorealistic"),
            passos=payload.get("passos", 28),
            guidance_scale=payload.get("guidance_scale", 2.5),
            seed=payload.get("seed", 42),
            output_dir=payload.get("output_dir", "outputs/images"),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        hf_status = status_hf_image_client() if HF_CLIENT_AVAILABLE else {
            "gradio_client": False,
            "pillow": False,
        }

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
            "fase": "2 — DARK IMAGE STUDIO",
            "hf_client_disponivel": HF_CLIENT_AVAILABLE,
            "pillow": pillow_ok,
            "pillow_version": pillow_version,
            "backends": {
                "flux_schnell": HF_CLIENT_AVAILABLE and hf_status.get("gradio_client", False),
                "birefnet_bg_removal": HF_CLIENT_AVAILABLE and hf_status.get("gradio_client", False),
                "kontext_upscale": HF_CLIENT_AVAILABLE and hf_status.get("gradio_client", False),
                "pillow_local": pillow_ok,
            },
            "capacidades": [
                "thumbnail_local (Pillow)",
                "thumbnail_ia (FLUX + upscale + <2MB)",
                "thumbnail_comprimir (PNG→JPEG <2MB)",
                "texto_para_imagem (FLUX.1-schnell)",
                "remover_fundo (BiRefNet)",
                "upscale (Kontext-Unblur-Upscale)",
                "pack_thumbnails (horizontal + shorts)",
            ],
            "custo": "GRATUITO — HuggingFace Spaces + Pillow local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }
