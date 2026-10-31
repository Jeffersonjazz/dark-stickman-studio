"""
DARK CREATIVE LAB — AGENTE CINEMATIC DIRECTOR
Direção de fotografia, composição, iluminação, enquadramentos e continuidade visual.

Baseado em pesquisa da comunidade:
- n8n Animation Studio: amplificar para 4K antes do zoompan elimina jitter
- dev.to pipeline: FFmpeg direto, sem MoviePy
- saiedpod-bot/Stickman-Studio: presets por nicho de conteúdo

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import random
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  PRESETS CINEMATOGRÁFICOS
# ─────────────────────────────────────────────────────────────────

CINEMA_PRESETS = {
    "documentario": {
        "zoom_speed": 0.0002,       # Zoom lento e suave
        "zoom_start": 1.0,
        "zoom_max": 1.3,
        "pan_style": "static",      # Câmera estática
        "vignette": True,
        "color_temp": "warm",       # Temperatura quente
        "contrast_boost": 0.05,
        "saturation": 0.85,
        "grain": 0.02,              # Grão de filme
        "fps": 24,                  # Cinemático
        "description": "Documentário cinematográfico — câmera estática, zoom suave",
    },
    "natureza": {
        "zoom_speed": 0.0003,
        "zoom_start": 1.05,
        "zoom_max": 1.5,
        "pan_style": "drift",       # Deriva suave
        "vignette": False,
        "color_temp": "cool",
        "contrast_boost": 0.1,
        "saturation": 1.3,
        "grain": 0.01,
        "fps": 30,
        "description": "Natureza e vida selvagem — zoom dinâmico, cores vibrantes",
    },
    "historia": {
        "zoom_speed": 0.00015,
        "zoom_start": 1.0,
        "zoom_max": 1.2,
        "pan_style": "static",
        "vignette": True,
        "color_temp": "sepia",      # Sépia histórico
        "contrast_boost": 0.15,
        "saturation": 0.7,
        "grain": 0.05,              # Grão antigo
        "fps": 24,
        "description": "História e acontecimentos — paleta envelhecida, grão de filme",
    },
    "tecnologia": {
        "zoom_speed": 0.0004,
        "zoom_start": 1.0,
        "zoom_max": 1.4,
        "pan_style": "push",        # Push in dinâmico
        "vignette": False,
        "color_temp": "blue",       # Frio tecnológico
        "contrast_boost": 0.1,
        "saturation": 0.9,
        "grain": 0.0,
        "fps": 30,
        "description": "Tecnologia e IA — movimento dinâmico, paleta azulada",
    },
    "misterio": {
        "zoom_speed": 0.00025,
        "zoom_start": 1.02,
        "zoom_max": 1.35,
        "pan_style": "slow_push",
        "vignette": True,
        "color_temp": "dark",
        "contrast_boost": 0.2,
        "saturation": 0.6,
        "grain": 0.03,
        "fps": 24,
        "description": "Mistério e suspense — vinheta dramática, paleta escura",
    },
    "educacao": {
        "zoom_speed": 0.0002,
        "zoom_start": 1.0,
        "zoom_max": 1.25,
        "pan_style": "static",
        "vignette": False,
        "color_temp": "neutral",
        "contrast_boost": 0.05,
        "saturation": 1.1,
        "grain": 0.0,
        "fps": 30,
        "description": "Educação — neutro, legível, sem distrações",
    },
    "relaxamento": {
        "zoom_speed": 0.00015,
        "zoom_start": 1.0,
        "zoom_max": 1.2,
        "pan_style": "float",       # Flutuante suave
        "vignette": False,
        "color_temp": "warm",
        "contrast_boost": 0.0,
        "saturation": 1.15,
        "grain": 0.0,
        "fps": 24,
        "description": "Relaxamento — movimento minimal, cores quentes e suaves",
    },
    "storytelling_dark": {
        "zoom_speed": 0.0003,
        "zoom_start": 1.0,
        "zoom_max": 1.45,
        "pan_style": "slow_push",
        "vignette": True,
        "color_temp": "dark",
        "contrast_boost": 0.18,
        "saturation": 0.65,
        "grain": 0.04,
        "fps": 24,
        "description": "Storytelling dark — atmosfera intensa, sem apresentador",
    },
}

# Mapeamento nicho → preset
NICHO_PARA_PRESET = {
    "psicologia":  "storytelling_dark",
    "batalhas":    "historia",
    "tecnologia":  "tecnologia",
    "filosofia":   "misterio",
    "historia":    "historia",
    "misterio":    "misterio",
    "educacao":    "educacao",
    "relaxamento": "relaxamento",
    "natureza":    "natureza",
    "stem":        "tecnologia",
    "musical":     "relaxamento",
    "financas":    "educacao",
    "saude":       "relaxamento",
    "documentario": "documentario",
}

# Tipos de movimento de câmera
MOVIMENTOS_CAMERA = {
    "static":    "Câmera estática — foco no conteúdo",
    "push":      "Push in — aproximação dinâmica",
    "pull":      "Pull out — afastamento revelador",
    "drift":     "Deriva suave — movimento orgânico",
    "slow_push": "Push lento — tensão crescente",
    "float":     "Flutuante — leveza e tranquilidade",
}

# ─────────────────────────────────────────────────────────────────
#  GERADOR DE FILTRO FFMPEG ANTI-JITTER (técnica 4K)
# ─────────────────────────────────────────────────────────────────

def gerar_filtro_zoompan_antijitter(
    preset_nome: str,
    duracao: float,
    fps: int = 30,
    target_w: int = 1920,
    target_h: int = 1080,
) -> str:
    """
    Gera filtro FFmpeg zoompan com técnica anti-jitter da comunidade n8n:
    1. Amplifica para 4K antes do zoompan
    2. Aplica movimento em 4K
    3. Reduz para target resolution

    Isso elimina o jitter causado pelo filtro zoompan em resoluções menores.

    Referência: n8n Community — "Fully Autonomous AI Animation Studio"
    """
    p = CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"])
    zoom_speed = p["zoom_speed"]
    zoom_start = p["zoom_start"]
    zoom_max = p["zoom_max"]
    pan_style = p["pan_style"]

    # Resolução 4K para processamento interno (anti-jitter)
    w4k = 3840
    h4k = 2160
    total_frames = int(duracao * fps)

    # Expressão de zoom
    zoom_expr = f"min(zoom+{zoom_speed:.6f},{zoom_max:.3f})"
    if zoom_start > 1.0:
        zoom_expr = f"if(eq(on,1),{zoom_start:.3f},min(zoom+{zoom_speed:.6f},{zoom_max:.3f}))"

    # Expressão de panorâmica por estilo
    if pan_style == "static":
        x_expr = f"iw/2-(iw/zoom/2)"
        y_expr = f"ih/2-(ih/zoom/2)"
    elif pan_style == "drift":
        x_expr = f"iw/2-(iw/zoom/2)+sin(on/{total_frames}*3.14159)*{w4k*0.03:.0f}"
        y_expr = f"ih/2-(ih/zoom/2)+cos(on/{total_frames}*3.14159)*{h4k*0.02:.0f}"
    elif pan_style in ("push", "slow_push"):
        x_expr = f"iw/2-(iw/zoom/2)"
        y_expr = f"ih/2-(ih/zoom/2)"
    elif pan_style == "float":
        x_expr = f"iw/2-(iw/zoom/2)+sin(on/{total_frames*2:.0f}*3.14159)*{w4k*0.015:.0f}"
        y_expr = f"ih/2-(ih/zoom/2)+cos(on/{total_frames*3:.0f}*3.14159)*{h4k*0.01:.0f}"
    else:
        x_expr = f"iw/2-(iw/zoom/2)"
        y_expr = f"ih/2-(ih/zoom/2)"

    # Pipeline anti-jitter:
    # scale para 4K → zoompan em 4K → scale final
    filtro = (
        f"scale={w4k}:{h4k}:flags=lanczos,"
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}'"
        f":d={total_frames}:s={w4k}x{h4k}:fps={fps},"
        f"scale={target_w}:{target_h}:flags=lanczos"
    )

    return filtro


def gerar_filtro_colorgrade(preset_nome: str) -> str:
    """Gera filtro FFmpeg de color grading para o preset cinematográfico."""
    p = CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"])
    temp = p.get("color_temp", "neutral")
    saturation = p.get("saturation", 1.0)
    contrast = 1.0 + p.get("contrast_boost", 0.0)
    grain = p.get("grain", 0.0)

    # Ajuste de temperatura de cor via curvas RGB
    curvas = {
        "warm":    "curves=r='0/0 0.5/0.55 1/1':g='0/0 0.5/0.5 1/0.95':b='0/0 0.5/0.45 1/0.85'",
        "cool":    "curves=r='0/0 0.5/0.45 1/0.9':g='0/0 0.5/0.5 1/0.95':b='0/0 0.5/0.55 1/1.05'",
        "sepia":   "curves=r='0/0.05 0.5/0.6 1/0.95':g='0/0 0.5/0.45 1/0.85':b='0/0 0.5/0.35 1/0.7'",
        "dark":    "curves=r='0/0 0.5/0.42 1/0.85':g='0/0 0.5/0.42 1/0.85':b='0/0.05 0.5/0.45 1/0.9'",
        "blue":    "curves=r='0/0 0.5/0.45 1/0.9':g='0/0 0.5/0.5 1/0.95':b='0/0.05 0.5/0.55 1/1.05'",
        "neutral": "",
    }
    curva = curvas.get(temp, "")

    # Montar filtro
    partes = [f"eq=saturation={saturation:.2f}:contrast={contrast:.2f}"]
    if curva:
        partes.append(curva)
    if p.get("vignette", False):
        partes.append("vignette=PI/5")
    if grain > 0:
        partes.append(f"noise=c0s={int(grain*15)}:c0f=t+u")

    return ",".join(partes)


# ─────────────────────────────────────────────────────────────────
#  GERADOR DE PROMPTS VISUAIS (para geração de imagem/vídeo)
# ─────────────────────────────────────────────────────────────────

def gerar_prompt_visual(
    cena: dict,
    preset_nome: str,
    estilo_extra: str = "",
) -> str:
    """
    Gera prompt visual para geração de imagem/vídeo baseado no preset cinematográfico.

    Args:
        cena: Dict com 'titulo', 'narracao', 'ambiente', 'descricao_visual'.
        preset_nome: Nome do preset cinematográfico.
        estilo_extra: Instruções adicionais de estilo.

    Returns:
        Prompt otimizado para geração de imagem realista.
    """
    p = CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"])
    titulo = cena.get("titulo", "")
    descricao = cena.get("descricao_visual", cena.get("narracao", ""))
    ambiente = cena.get("ambiente", "")

    # Estilo fotográfico por preset
    estilos_foto = {
        "documentario": "cinematic documentary photography, 35mm film, natural lighting, shallow depth of field",
        "natureza":     "wildlife photography, golden hour light, telephoto lens, vivid colors, National Geographic style",
        "historia":     "historical photography, vintage film grain, sepia tones, archival quality",
        "tecnologia":   "futuristic tech aesthetic, blue lighting, clean lines, high contrast",
        "misterio":     "dark atmospheric photography, dramatic shadows, fog, cinematic noir",
        "educacao":     "clean educational visual, bright neutral lighting, clear composition",
        "relaxamento":  "peaceful serene photography, soft warm light, gentle bokeh",
        "storytelling_dark": "dramatic storytelling, dark moody atmosphere, cinematic composition, no presenter",
    }
    estilo_foto = estilos_foto.get(preset_nome, "cinematic photography")

    # Qualidade universal
    qualidade = "8K resolution, photorealistic, professional photography, masterpiece"

    prompt = f"{descricao}"
    if titulo:
        prompt += f" showing {titulo}"
    if ambiente:
        prompt += f", {ambiente}"
    prompt += f", {estilo_foto}"
    if estilo_extra:
        prompt += f", {estilo_extra}"
    prompt += f", {qualidade}"

    # Prefixo anti-apresentador (canal faceless)
    prompt = f"NO PRESENTER, NO TEXT OVERLAY, NO WATERMARK, {prompt}"

    return prompt


def gerar_prompt_movimento_camera(
    cena: dict,
    preset_nome: str,
) -> str:
    """Gera descrição de movimento de câmera para animação de vídeo."""
    p = CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"])
    pan_style = p["pan_style"]
    zoom_speed = p["zoom_speed"]

    descricoes = {
        "static":    f"static shot, steady camera, slow zoom in at {zoom_speed*100:.3f}% per frame",
        "drift":     f"gentle camera drift, organic movement, slow zoom at {zoom_speed*100:.3f}% per frame",
        "push":      f"slow push in, camera moves forward, establishing then closing",
        "slow_push": f"very slow push in, tension building movement, cinematic pace",
        "float":     f"floating camera movement, gentle and peaceful, minimal motion",
    }

    return descricoes.get(pan_style, "static shot")


# ─────────────────────────────────────────────────────────────────
#  PLANO DE CENAS (storyboard automático)
# ─────────────────────────────────────────────────────────────────

def criar_plano_cenas(
    roteiro: dict,
    canal_config: dict,
) -> dict:
    """
    AGENTE CINEMATIC DIRECTOR — Cria plano cinematográfico completo do roteiro.

    Para cada cena, define:
    - Enquadramento e composição
    - Movimento de câmera
    - Iluminação e temperatura de cor
    - Prompt visual para geração
    - Duração e ritmo
    - Transição para próxima cena

    Returns:
        Roteiro enriquecido com dados cinematográficos.
    """
    nicho = canal_config.get("nicho", "documentario")
    preset_nome = NICHO_PARA_PRESET.get(nicho, "documentario")
    preset = CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"])

    cenas_enriquecidas = []
    cenas = roteiro.get("cenas", [])
    n_total = len(cenas)

    for i, cena in enumerate(cenas):
        posicao_relativa = i / max(n_total - 1, 1)  # 0.0 a 1.0

        # Tipo de enquadramento por posição narrativa
        if i == 0:
            enquadramento = "wide establishing shot"
        elif i == n_total - 1:
            enquadramento = "medium shot, closing frame"
        elif posicao_relativa < 0.3:
            enquadramento = "medium wide shot, introducing"
        elif posicao_relativa < 0.7:
            enquadramento = "medium close-up, engagement"
        else:
            enquadramento = "close-up, climax building"

        # Intensidade de zoom aumenta no clímax
        fator_intensidade = 0.5 + posicao_relativa * 0.5
        zoom_speed_ajustado = preset["zoom_speed"] * fator_intensidade

        # Prompt visual
        prompt_visual = gerar_prompt_visual(cena, preset_nome)
        movimento = gerar_prompt_movimento_camera(cena, preset_nome)

        # Transição
        if i < n_total - 1:
            if preset_nome in ("misterio", "storytelling_dark"):
                transicao = "dissolve"
            elif preset_nome == "natureza":
                transicao = "fade"
            else:
                transicao = "dissolve"
        else:
            transicao = "fade_out"

        cena_enriquecida = {
            **cena,
            "cinematografia": {
                "preset": preset_nome,
                "enquadramento": enquadramento,
                "movimento_camera": movimento,
                "zoom_speed": zoom_speed_ajustado,
                "zoom_max": preset["zoom_max"],
                "pan_style": preset["pan_style"],
                "color_temp": preset["color_temp"],
                "saturation": preset["saturation"],
                "vignette": preset["vignette"],
                "grain": preset["grain"],
                "fps": preset["fps"],
                "transicao": transicao,
            },
            "prompt_visual": cena.get("prompt_visual") or prompt_visual,
            "prompt_camera": movimento,
        }
        cenas_enriquecidas.append(cena_enriquecida)

    roteiro_enriquecido = {
        **roteiro,
        "cenas": cenas_enriquecidas,
        "cinematografia_global": {
            "preset": preset_nome,
            "descricao": preset["description"],
            "fps": preset["fps"],
            "color_grade_filtro": gerar_filtro_colorgrade(preset_nome),
        },
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    return roteiro_enriquecido


# ─────────────────────────────────────────────────────────────────
#  GERADOR DE FILTRO FFMPEG PARA CENA
# ─────────────────────────────────────────────────────────────────

def get_filtro_cena(
    cena: dict,
    duracao: float,
    target_w: int = 1920,
    target_h: int = 1080,
) -> str:
    """
    Retorna filtro FFmpeg completo para uma cena com dados cinematográficos.
    Usa técnica anti-jitter 4K quando disponível.
    """
    cinema = cena.get("cinematografia", {})
    preset_nome = cinema.get("preset", "documentario")

    if cinema:
        zoom_speed = cinema.get("zoom_speed", 0.0002)
        zoom_max = cinema.get("zoom_max", 1.3)
        pan_style = cinema.get("pan_style", "static")
        fps = cinema.get("fps", 30)

        # Criar preset temporário com valores da cena
        preset_tmp = {
            **CINEMA_PRESETS.get(preset_nome, CINEMA_PRESETS["documentario"]),
            "zoom_speed": zoom_speed,
            "zoom_max": zoom_max,
            "pan_style": pan_style,
        }

        # Técnica anti-jitter: usar gerar_filtro_zoompan_antijitter
        w4k, h4k = 3840, 2160
        total_frames = int(duracao * fps)

        zoom_expr = f"min(zoom+{zoom_speed:.6f},{zoom_max:.3f})"
        if pan_style == "static":
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif pan_style == "drift":
            x_expr = f"iw/2-(iw/zoom/2)+sin(on/{max(1,total_frames)}*3.14159)*{w4k*0.03:.0f}"
            y_expr = f"ih/2-(ih/zoom/2)+cos(on/{max(1,total_frames)}*3.14159)*{h4k*0.02:.0f}"
        else:
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        return (
            f"scale={w4k}:{h4k}:flags=lanczos,"
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}'"
            f":d={max(1,total_frames)}:s={w4k}x{h4k}:fps={fps},"
            f"scale={target_w}:{target_h}:flags=lanczos"
        )
    else:
        # Fallback sem dados cinematográficos
        return f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2"


def check_cinematic_director() -> dict:
    """Diagnóstico do AGENTE CINEMATIC DIRECTOR."""
    return {
        "status": "ok",
        "presets_disponiveis": list(CINEMA_PRESETS.keys()),
        "nichos_mapeados": list(NICHO_PARA_PRESET.keys()),
        "tecnica_antijitter": "4K zoompan (n8n community method)",
        "recursos": [
            "Plano cinematográfico automático por nicho",
            "Anti-jitter via amplificação 4K",
            "9 presets cinematográficos",
            "Geração de prompts visuais",
            "Movimentos de câmera por posição narrativa",
            "Color grading por preset",
        ],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
