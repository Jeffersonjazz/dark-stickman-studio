"""
DARK IMAGE STUDIO — FASE 2 do DARK CREATIVE LAB
================================================
Módulo unificado de geração e tratamento de imagens.

Implementa o AGENTE IMAGE ENGINE com cadeia de fallback completa:

  TIER 1 — Higgsfield AI (via MCP)
    gpt_image_2_6         → fotorrealismo, edição, tipografia       (~10 créditos)
    gpt_image_2_6_flare   → variante com suporte a GIF/SVG          (~10 créditos)
    soul_2                → retratos, editorial, fashion             (~10 créditos)
    soul_cast             → avatares, personagens                    (~10 créditos)
    marketing_studio_image → produto, comercial, ads                (~15 créditos)

  TIER 2 — HuggingFace Spaces (gratuito)
    FLUX.1-schnell        → texto→imagem rápido, qualidade alta
    Stable Diffusion XL   → texto→imagem alta qualidade
    SD v1.5               → fallback leve

  TIER 3 — Pillow local (zero custo, zero dependência GPU)
    Gradiente cinematográfico com metadados e AI disclosure

Funcionalidades principais:
  - Geração de imagem (gerar)
  - Thumbnail YouTube/Shorts (gerar_thumbnail)
  - Banner de canal (gerar_banner)
  - Lote de imagens por cenas (gerar_lote)
  - Upscale 2K/4K (upscale)
  - Remoção de fundo (remover_fundo)
  - Color grading (color_grade)
  - Planejamento de produção (planejar_cenas)

CONTRATO JSON — DARK MANAGER:
{
  "agent": "IMAGE_ENGINE",
  "backend_tier": "higgsfield|huggingface|pillow",
  "operacao": "gerar|thumbnail|banner|upscale|remove_bg|color_grade|lote",
  "input": {
    "prompt": "string",
    "nicho": "natureza|historia|tecnologia|misterio|motivacao|psicologia|...",
    "resolucao": "youtube_thumbnail|shorts|wallpaper_hd|square|...",
    "modelo": "padrao|flare|marketing|personagem|retrato",
    "enriquecer_prompt": true
  },
  "output": {
    "image_path": "/path/image.png",
    "job_id": "uuid-higgsfield",
    "resolucao": "1280x720",
    "custo_creditos": 10,
    "backend": "higgsfield|huggingface|pillow",
    "qa_score": 85,
    "ai_generated": true
  }
}

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import os
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

# Garante root no sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ═══════════════════════════════════════════════════════════════════
#  IMPORTS — CAMADAS DE BACKEND
# ═══════════════════════════════════════════════════════════════════

# Tier 2: HuggingFace + Pillow (import direto — sempre disponível)
try:
    from core.dark_image_engine import DarkImageEngine as _HFEngine
    _HF_DISPONIVEL = True
except ImportError:
    _HF_DISPONIVEL = False

# Helpers Higgsfield (sem MCP — só dados e funções)
try:
    from core.dark_higgsfield_bridge import (
        MODELOS_HIGGSFIELD,
        RESOLUCOES_HIGGSFIELD,
        ESTILOS_CINEMATICOS,
        ESTILOS_THUMBNAIL,
        ProducaoImagem,
        enriquecer_prompt_imagem,
        gerar_prompt_thumbnail_higgsfield,
        gerar_prompt_banner_canal,
        gerar_prompt_thumbnail_serie,
        calcular_qa_imagem,
        estimar_custo_imagem,
        planejar_producao_imagens,
        CUSTO_ESTIMADO_HIGGSFIELD,
        CONTRATO_HIGGSFIELD_IMAGE,
    )
    _HIGGSFIELD_BRIDGE_DISPONIVEL = True
except ImportError as _e:
    _HIGGSFIELD_BRIDGE_DISPONIVEL = False


# ═══════════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════════

VERSION = "2.0.0"
AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

# Ordem de preferência de backend
BACKEND_TIER = ["higgsfield", "huggingface", "pillow"]

# Mapeamento de nichos para presets HF
NICHO_HF_MAP = {
    "natureza":    "natureza",
    "historia":    "historia",
    "tecnologia":  "tecnologia",
    "psicologia":  "psicologia",
    "misterio":    "misterio",
    "motivacao":   "motivacao",
    "batalhas":    "batalhas",
    "filosofia":   "filosofia",
    "ciencia":     "ciencia",
    "financas":    "financas",
    "saude":       "saude",
    "stem":        "stem",
    "geral":       "geral",
}

# Dimensões padrão por resolução
DIMENSOES = {
    "youtube_thumbnail": (1280, 720),
    "shorts":            (1080, 1920),
    "wallpaper_hd":      (1920, 1080),
    "wallpaper_4k":      (3840, 2160),
    "square":            (1024, 1024),
    "instagram_post":    (1080, 1080),
    "instagram_story":   (1080, 1920),
    "banner_canal":      (2560, 1440),
    "portrait":          (768, 1344),
    "landscape":         (1344, 768),
}


# ═══════════════════════════════════════════════════════════════════
#  RESULTADO UNIFICADO
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ResultadoImagem:
    """Resultado unificado de qualquer operação do DARK IMAGE STUDIO."""
    status: str = "ok"             # ok | erro | pendente
    operacao: str = ""             # gerar | thumbnail | upscale | remove_bg | ...
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    job_id: Optional[str] = None   # UUID Higgsfield para operações MCP
    resolucao: str = "1024x1024"
    largura: int = 1024
    altura: int = 1024
    backend: str = "pillow"        # higgsfield | huggingface | pillow
    tier: int = 3                  # 1=Higgsfield, 2=HF, 3=Pillow
    custo_creditos: int = 0
    qa_score: int = 0
    prompt_usado: str = ""
    nicho: str = "geral"
    modelo: str = ""
    fallback_usado: bool = False
    erro: Optional[str] = None
    metadados: Dict[str, Any] = field(default_factory=dict)
    ai_generated: bool = True
    ai_disclosure: str = AI_DISCLOSURE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "operacao": self.operacao,
            "image_path": self.image_path,
            "image_url": self.image_url,
            "job_id": self.job_id,
            "resolucao": self.resolucao,
            "largura": self.largura,
            "altura": self.altura,
            "backend": self.backend,
            "tier": self.tier,
            "custo_creditos": self.custo_creditos,
            "qa_score": self.qa_score,
            "prompt_usado": self.prompt_usado,
            "nicho": self.nicho,
            "modelo": self.modelo,
            "fallback_usado": self.fallback_usado,
            "erro": self.erro,
            "metadados": self.metadados,
            "ai_generated": self.ai_generated,
            "ai_disclosure": self.ai_disclosure,
        }


# ═══════════════════════════════════════════════════════════════════
#  DARK IMAGE STUDIO — AGENTE IMAGE ENGINE
# ═══════════════════════════════════════════════════════════════════

class DarkImageStudio:
    """
    AGENTE IMAGE ENGINE — Geração, edição, tratamento e otimização de imagens.

    Orquestra a cadeia de fallback:
      Higgsfield (Tier 1, MCP) → HuggingFace (Tier 2) → Pillow (Tier 3)

    Uso típico (dentro de sessão Claude com MCP Higgsfield):
      # 1. Planejar prompts Higgsfield
      studio = DarkImageStudio()
      plano = studio.planejar_cenas(cenas, nicho="historia")

      # 2. Gerar via MCP (chamada externa — ver contrato JSON)
      #    mcp__Higgsfield__generate_image(model=plano["modelo"], prompt=plano["prompt"])

      # 3. Registrar resultado
      resultado = studio.registrar_resultado_higgsfield(job_id, image_path)

    Uso autônomo (sem MCP — HuggingFace + Pillow):
      studio = DarkImageStudio()
      resultado = studio.gerar(prompt="floresta tropical", nicho="natureza")
    """

    def __init__(self, projeto_id: str = "dark_studio", output_dir: str = "outputs/imagens"):
        self.projeto_id = projeto_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Instanciar motor HF (Tier 2+3)
        self._hf: Optional[_HFEngine] = None
        if _HF_DISPONIVEL:
            try:
                self._hf = _HFEngine()
            except Exception:
                pass

        self._log: List[Dict] = []

    # ─────────────────────────────────────────────
    # GERAÇÃO — TIER 2+3 (HuggingFace / Pillow)
    # Usado diretamente em pipelines Python autônomos
    # ─────────────────────────────────────────────

    def gerar(
        self,
        prompt: str,
        nicho: str = "geral",
        resolucao: str = "wallpaper_hd",
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Gera imagem via HuggingFace ou Pillow (sem custo).

        Args:
            prompt: Descrição textual da imagem
            nicho: Nicho do canal (natureza, historia, etc.)
            resolucao: Chave de resolução (youtube_thumbnail, shorts, etc.)
            output_path: Caminho de saída (opcional)

        Returns:
            dict com image_path, backend, qa_score, etc.
        """
        if self._hf is None:
            return self._fallback_pillow(prompt, nicho, resolucao, output_path)

        try:
            # Enriquecer prompt via bridge Higgsfield (apenas enriquecimento textual)
            prompt_final = prompt
            if _HIGGSFIELD_BRIDGE_DISPONIVEL:
                enr = enriquecer_prompt_imagem(prompt, nicho, resolucao)
                prompt_final = enr.get("prompt", prompt)

            result = self._hf.gerar(
                prompt=prompt_final,
                nicho=NICHO_HF_MAP.get(nicho, "geral"),
                output_path=output_path,
                **kwargs,
            )
            result["operacao"] = "gerar"
            self._registrar_log("gerar", result)
            return result

        except Exception as e:
            return self._fallback_pillow(prompt, nicho, resolucao, output_path, str(e))

    def gerar_thumbnail(
        self,
        titulo: str,
        subtitulo: str = "",
        nicho: str = "geral",
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Gera thumbnail YouTube (1280×720) via HF/Pillow.

        Args:
            titulo: Título principal do vídeo
            subtitulo: Subtítulo ou chamada (opcional)
            nicho: Nicho do canal
            output_path: Caminho de saída (opcional)

        Returns:
            dict com image_path, backend, resolucao, etc.
        """
        if self._hf is None:
            return self._fallback_pillow(titulo, nicho, "youtube_thumbnail", output_path)

        try:
            result = self._hf.gerar_thumbnail(
                titulo=titulo,
                subtitulo=subtitulo,
                nicho=NICHO_HF_MAP.get(nicho, "geral"),
                output_path=output_path,
                **kwargs,
            )
            result["operacao"] = "thumbnail"
            self._registrar_log("thumbnail", result)
            return result

        except Exception as e:
            return self._fallback_pillow(titulo, nicho, "youtube_thumbnail", output_path, str(e))

    def gerar_lote(
        self,
        cenas: List[Dict[str, Any]],
        nicho: str = "geral",
        output_dir: Optional[Path] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Gera imagens para múltiplas cenas em lote.

        Args:
            cenas: Lista de dicts com 'prompt', 'titulo', 'cena_id'
            nicho: Nicho do canal
            output_dir: Diretório de saída (opcional)

        Returns:
            Lista de resultados por cena
        """
        if self._hf is None:
            return [
                self._fallback_pillow(c.get("prompt", c.get("titulo", f"cena {i}")), nicho, "wallpaper_hd", None)
                for i, c in enumerate(cenas)
            ]

        try:
            # Enriquecer prompts
            cenas_enriquecidas = []
            for c in cenas:
                p = c.get("prompt", c.get("titulo", "cena"))
                if _HIGGSFIELD_BRIDGE_DISPONIVEL:
                    enr = enriquecer_prompt_imagem(p, nicho, "wallpaper_hd")
                    p = enr.get("prompt", p)
                cenas_enriquecidas.append({**c, "prompt": p})

            results = self._hf.gerar_lote(
                cenas=cenas_enriquecidas,
                nicho=NICHO_HF_MAP.get(nicho, "geral"),
                output_dir=output_dir or self.output_dir,
                **kwargs,
            )
            for r in results:
                r["operacao"] = "lote"
            return results

        except Exception as e:
            return [
                {**self._fallback_pillow(c.get("prompt", f"cena {i}"), nicho, "wallpaper_hd", None, str(e)), "operacao": "lote"}
                for i, c in enumerate(cenas)
            ]

    def upscale(
        self,
        image_path: Path,
        resolucao_alvo: str = "wallpaper_4k",
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Upscale de imagem (HF/Pillow local — sem créditos Higgsfield).

        Para upscale premium via Higgsfield, usar planejar_upscale_higgsfield().

        Args:
            image_path: Caminho da imagem de entrada
            resolucao_alvo: Resolução alvo (wallpaper_4k, wallpaper_hd, etc.)
            output_path: Caminho de saída (opcional)

        Returns:
            dict com image_path, resolucao, backend, etc.
        """
        if self._hf is None:
            return {"status": "erro", "erro": "HF Engine não disponível", "operacao": "upscale",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}
        try:
            w, h = DIMENSOES.get(resolucao_alvo, (1920, 1080))
            result = self._hf.upscale(
                image_path=image_path,
                largura=w,
                altura=h,
                output_path=output_path,
                **kwargs,
            )
            result["operacao"] = "upscale"
            self._registrar_log("upscale", result)
            return result
        except Exception as e:
            return {"status": "erro", "erro": str(e), "operacao": "upscale",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}

    def remover_fundo(
        self,
        image_path: Path,
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Remove fundo da imagem (rembg local ou HF).

        Args:
            image_path: Caminho da imagem de entrada
            output_path: Caminho de saída (opcional, PNG com alpha)

        Returns:
            dict com image_path, backend, etc.
        """
        if self._hf is None:
            return {"status": "erro", "erro": "HF Engine não disponível", "operacao": "remover_fundo",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}
        try:
            result = self._hf.remover_fundo(
                image_path=image_path,
                output_path=output_path,
                **kwargs,
            )
            result["operacao"] = "remover_fundo"
            self._registrar_log("remover_fundo", result)
            return result
        except Exception as e:
            return {"status": "erro", "erro": str(e), "operacao": "remover_fundo",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}

    def color_grade(
        self,
        image_path: Path,
        preset: str = "cinematico",
        output_path: Optional[Path] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Aplica color grading a uma imagem existente.

        Args:
            image_path: Caminho da imagem de entrada
            preset: Preset de cor (cinematico, natureza, escuro, etc.)
            output_path: Caminho de saída (opcional)

        Returns:
            dict com image_path, preset_aplicado, backend, etc.
        """
        if self._hf is None:
            return {"status": "erro", "erro": "HF Engine não disponível", "operacao": "color_grade",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}
        try:
            result = self._hf.color_grade(
                image_path=image_path,
                preset=preset,
                output_path=output_path,
                **kwargs,
            )
            result["operacao"] = "color_grade"
            self._registrar_log("color_grade", result)
            return result
        except Exception as e:
            return {"status": "erro", "erro": str(e), "operacao": "color_grade",
                    "ai_generated": True, "ai_disclosure": AI_DISCLOSURE}

    # ─────────────────────────────────────────────
    # PLANEJAMENTO HIGGSFIELD (Tier 1 — MCP externo)
    # Prepara contratos JSON para chamadas MCP em sessões Claude
    # ─────────────────────────────────────────────

    def planejar_cenas(
        self,
        cenas: List[Dict[str, Any]],
        nicho: str = "geral",
        modelo: str = "padrao",
        resolucao: str = "wallpaper_hd",
    ) -> Dict[str, Any]:
        """Planeja produção de imagens para N cenas via Higgsfield.

        Retorna contrato JSON com todos os prompts enriquecidos,
        estimativa de custo e instruções MCP para a sessão Claude.

        Args:
            cenas: Lista de dicts com 'prompt' ou 'titulo' por cena
            nicho: Nicho do canal
            modelo: Modelo Higgsfield (padrao, flare, retrato, etc.)
            resolucao: Resolução alvo

        Returns:
            dict com plano_completo, custo_total, instrucoes_mcp
        """
        if not _HIGGSFIELD_BRIDGE_DISPONIVEL:
            return {
                "status": "bridge_indisponivel",
                "mensagem": "Higgsfield bridge não carregado. Use gerar() para HF/Pillow.",
                "ai_generated": True,
                "ai_disclosure": AI_DISCLOSURE,
            }

        return planejar_producao_imagens(
            cenas=cenas,
            nicho=nicho,
            resolucao=resolucao,
            usar_higgsfield=(modelo != "pillow"),
        )

    def planejar_thumbnail_higgsfield(
        self,
        titulo: str,
        subtitulo: str = "",
        nicho: str = "geral",
        estilo_thumb: str = "youtube_padrao",
    ) -> Dict[str, Any]:
        """Planeja geração de thumbnail premium via Higgsfield.

        Retorna contrato com prompt enriquecido para chamada MCP.

        Args:
            titulo: Título do vídeo
            subtitulo: Subtítulo ou chamada
            nicho: Nicho do canal
            estilo_thumb: Estilo do thumbnail (youtube_padrao, dark_history, etc.)

        Returns:
            dict com prompt, modelo, resolucao, custo_estimado
        """
        if not _HIGGSFIELD_BRIDGE_DISPONIVEL:
            return {
                "status": "bridge_indisponivel",
                "mensagem": "Use gerar_thumbnail() para HF/Pillow.",
                "ai_generated": True,
                "ai_disclosure": AI_DISCLOSURE,
            }

        prompt_data = gerar_prompt_thumbnail_higgsfield(titulo, subtitulo, nicho, estilo_thumb)
        custo = estimar_custo_imagem("gerar_imagem")

        return {
            "status": "planejado",
            "operacao": "thumbnail",
            "prompt": prompt_data["prompt"],
            "modelo": "gpt_image_2_6",
            "resolucao": "1280x720",
            "largura": 1280,
            "altura": 720,
            "custo_creditos": custo,
            "instrucoes_mcp": (
                "Chamar: mcp__Higgsfield__generate_image("
                f"model='gpt_image_2_6', "
                f"prompt='{prompt_data['prompt'][:60]}...', "
                "width=1280, height=720)"
            ),
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    def registrar_resultado_higgsfield(
        self,
        job_id: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        operacao: str = "gerar",
        custo_creditos: int = 10,
        prompt: str = "",
        nicho: str = "geral",
    ) -> ResultadoImagem:
        """Registra resultado de chamada MCP Higgsfield no log do studio.

        Calcula QA score e retorna ResultadoImagem padronizado.

        Args:
            job_id: UUID do job Higgsfield
            image_path: Caminho local da imagem baixada (opcional)
            image_url: URL da imagem gerada (opcional)
            operacao: Operação realizada
            custo_creditos: Créditos consumidos
            prompt: Prompt usado
            nicho: Nicho do canal

        Returns:
            ResultadoImagem com qa_score calculado
        """
        if _HIGGSFIELD_BRIDGE_DISPONIVEL:
            producao = ProducaoImagem(
                job_id=job_id,
                image_path=image_path,
                image_url=image_url,
                custo_creditos=custo_creditos,
                backend_usado="higgsfield",
                prompt_usado=prompt,
                nicho=nicho,
            )
            qa = calcular_qa_imagem(producao)
        else:
            qa = 50 if job_id else 10

        resultado = ResultadoImagem(
            status="ok",
            operacao=operacao,
            image_path=image_path,
            image_url=image_url,
            job_id=job_id,
            backend="higgsfield",
            tier=1,
            custo_creditos=custo_creditos,
            qa_score=qa,
            prompt_usado=prompt,
            nicho=nicho,
            modelo="gpt_image_2_6",
            resolucao="1024x1024",
        )
        self._registrar_log(operacao, resultado.to_dict())
        return resultado

    # ─────────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────────

    def _fallback_pillow(
        self,
        prompt: str,
        nicho: str,
        resolucao: str,
        output_path: Optional[Path],
        erro_anterior: str = "",
    ) -> Dict[str, Any]:
        """Fallback Pillow — gera gradiente cinematográfico com metadados."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import colorsys

            w, h = DIMENSOES.get(resolucao, (1920, 1080))
            if output_path is None:
                safe = "".join(c if c.isalnum() else "_" for c in prompt[:30])
                output_path = self.output_dir / f"fallback_{safe}.png"

            # Paleta por nicho
            paletas = {
                "natureza":   ((20, 60, 20), (60, 120, 50)),
                "historia":   ((40, 20, 10), (100, 60, 20)),
                "tecnologia": ((10, 20, 60), (20, 60, 120)),
                "misterio":   ((10, 5, 20),  (40, 20, 60)),
                "motivacao":  ((60, 30, 5),  (140, 80, 20)),
                "psicologia": ((20, 10, 30), (60, 30, 80)),
            }
            c1, c2 = paletas.get(nicho, ((15, 15, 25), (40, 40, 70)))

            img = Image.new("RGB", (w, h))
            draw = ImageDraw.Draw(img)

            # Gradiente vertical
            for y in range(h):
                t = y / h
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                draw.line([(0, y), (w, y)], fill=(r, g, b))

            # Letterbox cinematográfico
            bar_h = max(int(h * 0.08), 20)
            draw.rectangle([(0, 0), (w, bar_h)], fill=(0, 0, 0))
            draw.rectangle([(0, h - bar_h), (w, h)], fill=(0, 0, 0))

            # AI disclosure
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            disc_text = "[ IA Gerada — DARK STUDIO AAA ]"
            draw.text((10, h - bar_h + 4), disc_text, fill=(150, 150, 150), font=font)

            # Título truncado
            title_text = prompt[:60] + ("..." if len(prompt) > 60 else "")
            draw.text((10, bar_h + 10), title_text, fill=(220, 220, 220), font=font)

            img.save(str(output_path))

            resultado = {
                "status": "ok",
                "operacao": "gerar",
                "image_path": str(output_path),
                "resolucao": f"{w}x{h}",
                "largura": w,
                "altura": h,
                "backend": "pillow",
                "tier": 3,
                "custo_creditos": 0,
                "qa_score": 15,
                "fallback_usado": True,
                "ai_generated": True,
                "ai_disclosure": AI_DISCLOSURE,
            }
            if erro_anterior:
                resultado["erro_anterior"] = erro_anterior
            self._registrar_log("fallback_pillow", resultado)
            return resultado

        except Exception as e2:
            return {
                "status": "erro",
                "erro": str(e2),
                "erro_anterior": erro_anterior,
                "operacao": "gerar",
                "backend": "pillow",
                "ai_generated": True,
                "ai_disclosure": AI_DISCLOSURE,
            }

    def _registrar_log(self, operacao: str, resultado: Dict[str, Any]) -> None:
        """Registra operação no log interno."""
        from datetime import datetime
        self._log.append({
            "ts": datetime.now().isoformat(),
            "operacao": operacao,
            "backend": resultado.get("backend", "?"),
            "status": resultado.get("status", "?"),
            "qa_score": resultado.get("qa_score", 0),
            "custo": resultado.get("custo_creditos", 0),
        })

    # ─────────────────────────────────────────────
    # RELATÓRIOS
    # ─────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Retorna status completo do DARK IMAGE STUDIO."""
        return {
            "version": VERSION,
            "projeto_id": self.projeto_id,
            "output_dir": str(self.output_dir),
            "backends": {
                "higgsfield": {
                    "tier": 1,
                    "disponivel": _HIGGSFIELD_BRIDGE_DISPONIVEL,
                    "requer_mcp": True,
                    "custo": "~10 créditos/imagem",
                    "qualidade": 9,
                },
                "huggingface": {
                    "tier": 2,
                    "disponivel": _HF_DISPONIVEL,
                    "requer_mcp": False,
                    "custo": "gratuito",
                    "qualidade": 7,
                    "modelos": ["FLUX.1-schnell", "SDXL", "SD-v1.5"],
                },
                "pillow": {
                    "tier": 3,
                    "disponivel": True,
                    "requer_mcp": False,
                    "custo": "zero",
                    "qualidade": 2,
                    "descricao": "fallback offline — gradiente com metadados",
                },
            },
            "operacoes_suportadas": [
                "gerar", "gerar_thumbnail", "gerar_lote", "upscale",
                "remover_fundo", "color_grade",
                "planejar_cenas", "planejar_thumbnail_higgsfield",
                "registrar_resultado_higgsfield",
            ],
            "log_operacoes": len(self._log),
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }

    def exportar_log(self, path: Optional[str] = None) -> str:
        """Exporta log de operações em JSON."""
        from datetime import datetime
        log_data = {
            "projeto_id": self.projeto_id,
            "exportado_em": datetime.now().isoformat(),
            "total_operacoes": len(self._log),
            "operacoes": self._log,
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }
        if path is None:
            path = str(self.output_dir / "dark_image_studio_log.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        return path


# ═══════════════════════════════════════════════════════════════════
#  CONTRATO JSON — DARK MANAGER
# ═══════════════════════════════════════════════════════════════════

CONTRATO_IMAGE_STUDIO = {
    "agent": "IMAGE_ENGINE",
    "module": "core.dark_image_studio",
    "class": "DarkImageStudio",
    "version": VERSION,
    "backend_tiers": {
        "1": {"nome": "Higgsfield AI", "tipo": "mcp_externo", "custo": "creditos"},
        "2": {"nome": "HuggingFace",   "tipo": "api_gratuita", "custo": "zero"},
        "3": {"nome": "Pillow",        "tipo": "local_offline", "custo": "zero"},
    },
    "operacoes": {
        "gerar":                      {"tier_minimo": 2, "descricao": "Texto → imagem"},
        "thumbnail":                  {"tier_minimo": 2, "descricao": "Thumbnail YouTube/Shorts"},
        "gerar_lote":                 {"tier_minimo": 2, "descricao": "Batch de imagens por cenas"},
        "upscale":                    {"tier_minimo": 2, "descricao": "Upscale 2K/4K"},
        "remover_fundo":              {"tier_minimo": 2, "descricao": "Remoção de fundo"},
        "color_grade":                {"tier_minimo": 2, "descricao": "Color grading"},
        "planejar_cenas":             {"tier_minimo": 1, "descricao": "Planejar produção Higgsfield"},
        "planejar_thumbnail_higgsfield": {"tier_minimo": 1, "descricao": "Planejar thumbnail Higgsfield"},
        "registrar_resultado_higgsfield": {"tier_minimo": 1, "descricao": "Registrar resultado MCP"},
    },
    "contrato_entrada": {
        "prompt": "string — descrição da imagem",
        "nicho": "natureza|historia|tecnologia|misterio|motivacao|psicologia|...",
        "resolucao": "youtube_thumbnail|shorts|wallpaper_hd|square|...",
        "modelo": "padrao|flare|marketing|personagem|retrato",
        "operacao": "gerar|thumbnail|gerar_lote|upscale|remover_fundo|color_grade",
    },
    "contrato_saida": {
        "status": "ok|erro|pendente",
        "image_path": "caminho local da imagem",
        "job_id": "UUID Higgsfield (Tier 1 apenas)",
        "resolucao": "LARGURAxALTURA",
        "backend": "higgsfield|huggingface|pillow",
        "tier": "1|2|3",
        "custo_creditos": "inteiro",
        "qa_score": "0-100",
        "ai_generated": True,
        "ai_disclosure": AI_DISCLOSURE,
    },
    "ai_generated": True,
    "ai_disclosure": AI_DISCLOSURE,
}


# ═══════════════════════════════════════════════════════════════════
#  INTERFACE FUNCIONAL (compatibilidade com dark_manager.py)
# ═══════════════════════════════════════════════════════════════════

_studio_singleton: Optional[DarkImageStudio] = None


def _get_studio() -> DarkImageStudio:
    global _studio_singleton
    if _studio_singleton is None:
        _studio_singleton = DarkImageStudio()
    return _studio_singleton


def gerar_imagem(
    prompt: str,
    nicho: str = "geral",
    resolucao: str = "wallpaper_hd",
    output_path: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Interface funcional — geração de imagem."""
    return _get_studio().gerar(
        prompt=prompt,
        nicho=nicho,
        resolucao=resolucao,
        output_path=Path(output_path) if output_path else None,
        **kwargs,
    )


def gerar_thumbnail(
    titulo: str,
    subtitulo: str = "",
    nicho: str = "geral",
    output_path: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Interface funcional — geração de thumbnail."""
    return _get_studio().gerar_thumbnail(
        titulo=titulo,
        subtitulo=subtitulo,
        nicho=nicho,
        output_path=Path(output_path) if output_path else None,
        **kwargs,
    )


def check_image_studio() -> Dict[str, Any]:
    """Verifica status do DARK IMAGE STUDIO."""
    return _get_studio().status()
