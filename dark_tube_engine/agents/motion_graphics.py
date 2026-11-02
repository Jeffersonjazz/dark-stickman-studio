"""
DARK TUBE ENGINE — AGENTE MOTION GRAPHICS
Animações, infográficos, títulos e efeitos
Clone funcional: After Effects essentials via FFmpeg + Pillow
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import os
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_composer import verificar_ffmpeg


TEMPLATES_TITULOS = {
    "abertura_dark": {
        "fonte": "Impact",
        "cor_texto": "white",
        "cor_sombra": "#7c3aed",
        "animacao": "fade_in_scale",
        "duracao": 3.0,
        "efeito": "glow_purple"
    },
    "titulo_motivacional": {
        "fonte": "Arial Black",
        "cor_texto": "#FFD700",
        "cor_sombra": "#FF4500",
        "animacao": "slide_up",
        "duracao": 2.5,
        "efeito": "neon_orange"
    },
    "legenda_documentario": {
        "fonte": "Arial",
        "cor_texto": "white",
        "cor_sombra": "black",
        "animacao": "typewriter",
        "duracao": "variavel",
        "efeito": "clean_shadow"
    },
    "lower_third": {
        "fonte": "Helvetica",
        "cor_texto": "white",
        "cor_fundo": "#1a1a2e",
        "cor_acento": "#7c3aed",
        "animacao": "slide_left",
        "duracao": 4.0,
        "efeito": "gradient_bar"
    },
}


class MotionGraphicsAgent:
    """
    AGENTE MOTION GRAPHICS — Animações e efeitos visuais
    Stack: FFmpeg drawtext/overlay (gratuito) + Pillow para stills
    Para animações complexas: Manim (Python, gratuito) ou Blender scripting
    """

    AGENT_ID = "motion_graphics"
    VERSION = "1.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "titulo" in tarefa or "abertura" in tarefa:
            return self.gerar_template_titulo(payload)
        elif "legenda" in tarefa or "srt" in tarefa:
            return self.configurar_legendas(payload)
        elif "lower_third" in tarefa:
            return self.gerar_lower_third(payload)
        else:
            return self.listar_templates(payload)

    def gerar_template_titulo(self, payload: dict) -> dict:
        estilo = payload.get("estilo", "abertura_dark")
        template = TEMPLATES_TITULOS.get(estilo, TEMPLATES_TITULOS["abertura_dark"])
        titulo = payload.get("titulo", "Sem título")

        # Gerar filtro FFmpeg para overlay de texto
        # cor_sombra pode não existir em todos os templates (ex: lower_third usa cor_fundo)
        cor_sombra = template.get('cor_sombra', template.get('cor_fundo', 'black'))
        duracao = template.get('duracao', 3.0) if isinstance(template.get('duracao'), (int, float)) else 3.0
        ffmpeg_filter = (
            f"drawtext=text='{titulo}':"
            f"fontcolor={template['cor_texto']}:"
            f"fontsize=72:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"shadowcolor={cor_sombra}:shadowx=3:shadowy=3:"
            f"alpha='if(lt(t,0.5),t*2,if(lt(t,{duracao}-0.5),1,(({duracao}-t)*2)))'"
        )

        return {
            "agente": self.AGENT_ID,
            "titulo": titulo,
            "estilo": estilo,
            "template": template,
            "ffmpeg_filter": ffmpeg_filter,
            "instrucao": f"Adicionar como overlay no início do vídeo por {template['duracao']}s",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def configurar_legendas(self, payload: dict) -> dict:
        srt_path = payload.get("srt_path", "")
        estilo = payload.get("estilo", "legenda_documentario")
        template = TEMPLATES_TITULOS.get(estilo, TEMPLATES_TITULOS["legenda_documentario"])

        ffmpeg_subtitle = (
            f"subtitles={srt_path}:force_style='"
            f"FontName={template['fonte']},"
            f"FontSize=24,"
            f"PrimaryColour=&Hffffff&,"
            f"OutlineColour=&H000000&,"
            f"Outline=2,"
            f"Bold=1,"
            f"Alignment=2'"
        )

        return {
            "agente": self.AGENT_ID,
            "srt_path": srt_path,
            "ffmpeg_subtitle_filter": ffmpeg_subtitle,
            "estilo": estilo,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def gerar_lower_third(self, payload: dict) -> dict:
        canal = payload.get("canal", "DARK TUBE")
        template = TEMPLATES_TITULOS["lower_third"]

        return {
            "agente": self.AGENT_ID,
            "canal": canal,
            "template": template,
            "posicao": "bottom_left",
            "entrada": "t=2.0s",
            "saida": "t=6.0s",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def listar_templates(self, payload: dict) -> dict:
        return {
            "agente": self.AGENT_ID,
            "templates_disponiveis": list(TEMPLATES_TITULOS.keys()),
            "templates": TEMPLATES_TITULOS,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        ffmpeg = verificar_ffmpeg()
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "ffmpeg": ffmpeg,
            "templates": list(TEMPLATES_TITULOS.keys()),
            "capacidades": ["titulos_animados", "legendas_srt", "lower_thirds", "overlays"],
            "custo": "GRATUITO — FFmpeg drawtext + Pillow",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
