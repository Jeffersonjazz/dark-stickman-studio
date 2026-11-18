"""
DARK HIGGSFIELD VIDEO BRIDGE — Helpers para geração de vídeo via Higgsfield MCP
Padrão: apenas helpers, dataclasses e contratos JSON.
MCP calls acontecem em sessões interativas Claude — NÃO aqui.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# ─────────────────────────────────────────────
# MODELOS HIGGSFIELD VÍDEO
# ─────────────────────────────────────────────

MODELOS_VIDEO = {
    "padrao":   "minimax-h3",        # Melhor custo-benefício, 6s, 720p
    "hd":       "minimax-h3-pro",    # Alta definição, 6s, 1080p
    "luma":     "luma-dream-machine",# Dream Machine — cinematográfico
    "kling":    "kling-v1-5-std",    # Kling 1.5 padrão, 5s
    "kling_pro":"kling-v1-5-pro",    # Kling 1.5 pro, motion control avançado
    "runway":   "runway-gen4-turbo", # Runway Gen-4 Turbo
    "wan":      "wan-2.1-t2v-480p",  # Wan 2.1 local/remoto, 480p
    "wan_hd":   "wan-2.1-t2v-720p",  # Wan 2.1, 720p
}

MODELO_DEFAULT = "minimax-h3"

# ─────────────────────────────────────────────
# ASPECT RATIOS
# ─────────────────────────────────────────────

ASPECT_RATIOS = {
    "shorts":    "9:16",   # YouTube Shorts / Instagram Reels / TikTok
    "horizontal":"16:9",   # YouTube padrão / wide screen
    "quadrado":  "1:1",    # Instagram feed / avatar
    "retrato":   "4:5",    # Instagram retrato
    "cinema":    "21:9",   # Cinemascope
}

# ─────────────────────────────────────────────
# ESTILOS CINEMATOGRÁFICOS (por nicho)
# ─────────────────────────────────────────────

ESTILOS_VIDEO = {
    "documentario": {
        "motion":      "slow camera push",
        "lighting":    "natural golden hour lighting",
        "grade":       "warm documentary color grade",
        "atmosphere":  "realistic, handheld feel, shallow depth of field",
        "fps":         24,
    },
    "natureza": {
        "motion":      "slow zoom wildlife shot",
        "lighting":    "diffused natural sunlight",
        "grade":       "vibrant nature, saturated greens and blues",
        "atmosphere":  "macro photography, ultra realistic, BBC Earth style",
        "fps":         24,
    },
    "historia": {
        "motion":      "Ken Burns effect, slow diagonal pan",
        "lighting":    "sepia tinted, low contrast",
        "grade":       "vintage film grain, desaturated browns",
        "atmosphere":  "1920s archival footage aesthetic",
        "fps":         24,
    },
    "tecnologia": {
        "motion":      "smooth zoom out reveal",
        "lighting":    "cool blue neon, rim lighting",
        "grade":       "cool cinematic, blue-teal palette",
        "atmosphere":  "futuristic, sci-fi, high contrast",
        "fps":         30,
    },
    "misterio": {
        "motion":      "slow push into darkness",
        "lighting":    "single harsh sidelight, deep shadows",
        "grade":       "dark, desaturated, moody noir",
        "atmosphere":  "horror atmospheric, fog, analog noise",
        "fps":         24,
    },
    "motivacional": {
        "motion":      "dynamic, fast cuts, slow-motion impact",
        "lighting":    "dramatic cinematic lighting",
        "grade":       "high contrast, warm orange tones",
        "atmosphere":  "epic, powerful, motivational sports photography",
        "fps":         30,
    },
    "relaxamento": {
        "motion":      "ultra slow drift, floating camera",
        "lighting":    "soft diffused golden sunset",
        "grade":       "warm pastel, low saturation, dreamlike",
        "atmosphere":  "calm, meditative, lofi aesthetic",
        "fps":         24,
    },
    "educacao": {
        "motion":      "clean static shot, slight push",
        "lighting":    "bright clean studio light",
        "grade":       "clean natural, no color cast",
        "atmosphere":  "clear, informative, explainer style",
        "fps":         30,
    },
    "storytelling_dark": {
        "motion":      "slow creeping push, slight shake",
        "lighting":    "underlighting, candlelight flicker",
        "grade":       "crushed blacks, cold green shadows",
        "atmosphere":  "atmospheric noir, dark channels, faceless storytelling",
        "fps":         24,
    },
    "musica": {
        "motion":      "rhythmic cuts, beat-synced zooms",
        "lighting":    "concert lighting, colored gels",
        "grade":       "vibrant, high saturation, music video look",
        "atmosphere":  "dynamic, energetic, visual album aesthetic",
        "fps":         30,
    },
}

# ─────────────────────────────────────────────
# TIPOS DE MOVIMENTO DE CÂMERA
# ─────────────────────────────────────────────

MOVIMENTOS_CAMERA = {
    "push_in":        "slow camera push into subject",
    "pull_out":       "smooth camera pull back revealing scene",
    "pan_left":       "slow pan left across scene",
    "pan_right":      "slow pan right across scene",
    "tilt_up":        "camera tilts up from ground to sky",
    "tilt_down":      "camera tilts down from sky to ground",
    "orbit":          "camera orbits around subject",
    "tracking":       "tracking shot following subject",
    "crane_up":       "crane shot rising upward",
    "crane_down":     "crane shot descending",
    "handheld":       "handheld, slight organic movement",
    "static":         "static locked-off shot",
    "dolly_zoom":     "dolly zoom (vertigo effect)",
    "aerial":         "aerial drone shot looking down",
    "fly_through":    "fly-through shot, moving through environment",
    "ken_burns":      "Ken Burns effect, slow zoom with diagonal pan",
}

# ─────────────────────────────────────────────
# DATACLASS
# ─────────────────────────────────────────────

@dataclass
class ProducaoVideo:
    """Estrutura de dados para uma geração de vídeo via Higgsfield."""
    # Input
    prompt:           str = ""
    prompt_enriquecido: str = ""
    imagem_base:      Optional[str] = None   # URL ou path da imagem base (img2video)
    nicho:            str = "documentario"
    modelo:           str = MODELO_DEFAULT
    aspect_ratio:     str = "16:9"
    duracao_s:        float = 6.0
    fps:              int = 24
    movimento:        str = "push_in"

    # Output
    job_id:           Optional[str] = None
    video_url:        Optional[str] = None
    video_path:       Optional[str] = None
    status:           str = "pending"        # pending, processing, completed, failed

    # QA
    qa_score:         int = 0
    motion_smooth:    bool = True
    visual_quality:   str = "good"

    # Meta
    backend:          str = "higgsfield"
    custo_creditos:   int = 0
    tier:             int = 1
    fallback_usado:   bool = False
    ai_generated:     bool = True
    ai_disclosure:    str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    erro:             Optional[str] = None
    metadados:        Dict[str, Any] = field(default_factory=dict)


# ─────────────────────────────────────────────
# PROMPT ENGINEERING
# ─────────────────────────────────────────────

def enriquecer_prompt_video(
    prompt: str,
    nicho: str = "documentario",
    aspect_ratio: str = "16:9",
    movimento: Optional[str] = None,
    duracao: float = 6.0,
) -> Dict[str, Any]:
    """
    Enriquece um prompt básico com instruções cinematográficas.

    Returns:
        dict com 'prompt_final', 'movimento', 'estilo', 'aspect_ratio'.
    """
    estilo = ESTILOS_VIDEO.get(nicho, ESTILOS_VIDEO["documentario"])

    if not movimento:
        # Escolhe movimento padrão do estilo
        movimento = estilo["motion"].split(",")[0].strip()
        # Mapeia para key do dict de movimentos
        for key, val in MOVIMENTOS_CAMERA.items():
            if key in movimento.replace(" ", "_").lower():
                movimento = key
                break
        else:
            movimento = "push_in"

    movimento_desc = MOVIMENTOS_CAMERA.get(movimento, movimento)

    prompt_final = (
        f"{prompt}. "
        f"{movimento_desc}. "
        f"{estilo['lighting']}. "
        f"{estilo['atmosphere']}. "
        f"{estilo['grade']}. "
        f"Ultra high quality, cinematic, photorealistic. "
        f"{'Vertical 9:16 format.' if '9:16' in aspect_ratio else 'Horizontal 16:9 widescreen.'}"
    )

    return {
        "prompt_final": prompt_final,
        "prompt_original": prompt,
        "movimento": movimento,
        "movimento_descricao": movimento_desc,
        "estilo": estilo,
        "aspect_ratio": aspect_ratio,
        "duracao_s": duracao,
        "nicho": nicho,
    }


def gerar_prompt_cena_video(
    cena: Dict[str, Any],
    nicho: str = "documentario",
    numero_cena: int = 1,
    total_cenas: int = 1,
    personagens: Optional[List[Dict]] = None,
) -> str:
    """
    Gera prompt cinematográfico completo para uma cena de roteiro.

    Args:
        cena:          dict com 'descricao', 'ambiente', 'personagens', etc.
        nicho:         Nicho do canal.
        numero_cena:   Número da cena (para controle de narrativa).
        total_cenas:   Total de cenas (para saber se é abertura/encerramento).
        personagens:   Lista de personagens registrados para consistência.
    """
    estilo = ESTILOS_VIDEO.get(nicho, ESTILOS_VIDEO["documentario"])

    # Descrição principal
    descricao = cena.get("prompt_visual") or cena.get("descricao") or cena.get("texto", "")
    ambiente = cena.get("ambiente", "")
    horario = cena.get("horario", "")
    clima = cena.get("clima", "")

    # Contexto de posição na narrativa
    if numero_cena == 1:
        posicao = "opening shot, establishing scene"
    elif numero_cena == total_cenas:
        posicao = "closing shot, final scene"
    else:
        posicao = f"scene {numero_cena} of {total_cenas}"

    # Personagens com aparência registrada
    char_desc = ""
    if personagens:
        chars_na_cena = cena.get("personagens", [])
        for char in personagens:
            if char.get("nome") in chars_na_cena:
                char_desc += f" {char.get('descricao_visual', '')}."

    prompt = (
        f"{descricao}."
        f"{(' ' + ambiente + '.') if ambiente else ''}"
        f"{(' ' + horario + ' lighting.') if horario else ''}"
        f"{(' ' + clima + ' weather.') if clima else ''}"
        f"{char_desc}"
        f" {estilo['motion']}."
        f" {estilo['lighting']}."
        f" {estilo['atmosphere']}."
        f" {posicao}."
        f" Cinematic, photorealistic, ultra detailed."
    )

    return prompt.strip()


def gerar_prompt_b_roll(
    tema: str,
    nicho: str = "documentario",
    quantidade: int = 3,
) -> List[str]:
    """
    Gera lista de prompts para vídeos B-Roll complementares.

    Args:
        tema:       Tema principal do vídeo.
        nicho:      Nicho cinematográfico.
        quantidade: Número de clipes B-Roll a gerar.
    """
    estilo = ESTILOS_VIDEO.get(nicho, ESTILOS_VIDEO["documentario"])

    movimentos_broll = ["push_in", "pan_left", "pull_out", "tilt_up", "aerial"]
    prompts = []

    for i in range(quantidade):
        mov_key = movimentos_broll[i % len(movimentos_broll)]
        mov_desc = MOVIMENTOS_CAMERA[mov_key]

        prompt = (
            f"B-roll footage: {tema}. "
            f"{mov_desc}. "
            f"{estilo['lighting']}. "
            f"{estilo['atmosphere']}. "
            f"Cinematic insert shot, no people, environmental footage."
        )
        prompts.append(prompt)

    return prompts


def gerar_prompt_intro_canal(
    nome_canal: str,
    descricao: str,
    nicho: str,
    duracao_s: float = 3.0,
) -> str:
    """Gera prompt para vídeo de intro/abertura do canal."""
    estilo = ESTILOS_VIDEO.get(nicho, ESTILOS_VIDEO["documentario"])

    return (
        f"Channel intro animation for '{nome_canal}': {descricao}. "
        f"Dramatic reveal, {estilo['lighting']}. "
        f"Logo animation, {estilo['grade']}. "
        f"Epic opening, {duracao_s:.0f} second intro, cinematic reveal."
    )


# ─────────────────────────────────────────────
# PLANEJAMENTO DE PRODUÇÃO
# ─────────────────────────────────────────────

def planejar_producao_videos(
    cenas: List[Dict],
    nicho: str = "documentario",
    aspect_ratio: str = "16:9",
    modelo: str = MODELO_DEFAULT,
    usar_higgsfield: bool = True,
    incluir_broll: bool = True,
) -> Dict[str, Any]:
    """
    Planeja a produção de vídeos para um roteiro completo.

    Returns:
        dict com plano de produção: cenas, custo estimado, backends, etc.
    """
    aspect = "9:16" if "shorts" in nicho.lower() or aspect_ratio == "9:16" else "16:9"

    plano = {
        "total_cenas": len(cenas),
        "nicho": nicho,
        "modelo": modelo,
        "aspect_ratio": aspect,
        "usar_higgsfield": usar_higgsfield,
        "cenas": [],
        "broll": [],
        "custo_estimado_creditos": 0,
        "custo_estimado_usd": 0.0,
        "duracao_total_s": 0.0,
    }

    for i, cena in enumerate(cenas, 1):
        prompt = gerar_prompt_cena_video(cena, nicho, i, len(cenas))
        enriquecido = enriquecer_prompt_video(prompt, nicho, aspect)

        dur = cena.get("duracao_s", 5.0)
        custo = estimar_custo_video(modelo, dur)

        plano["cenas"].append({
            "numero": i,
            "prompt_original": cena.get("descricao", ""),
            "prompt_enriquecido": enriquecido["prompt_final"],
            "duracao_s": dur,
            "movimento": enriquecido["movimento"],
            "custo_creditos": custo["creditos"],
            "custo_usd": custo["usd"],
            "imagem_base": cena.get("imagem_base"),
        })

        plano["custo_estimado_creditos"] += custo["creditos"]
        plano["custo_estimado_usd"] += custo["usd"]
        plano["duracao_total_s"] += dur

    # B-Roll (opcional)
    if incluir_broll and cenas:
        tema_geral = cenas[0].get("descricao", nicho)
        broll_prompts = gerar_prompt_b_roll(tema_geral, nicho, quantidade=min(3, len(cenas)))
        for j, bp in enumerate(broll_prompts, 1):
            plano["broll"].append({
                "numero": j,
                "prompt": bp,
                "duracao_s": 3.0,
                "tipo": "b_roll",
            })

    return plano


# ─────────────────────────────────────────────
# CUSTO E QA
# ─────────────────────────────────────────────

CUSTO_ESTIMADO = {
    "minimax-h3":       {"creditos": 15, "usd": 0.08},
    "minimax-h3-pro":   {"creditos": 25, "usd": 0.14},
    "luma-dream-machine": {"creditos": 20, "usd": 0.11},
    "kling-v1-5-std":   {"creditos": 18, "usd": 0.10},
    "kling-v1-5-pro":   {"creditos": 30, "usd": 0.17},
    "runway-gen4-turbo":{"creditos": 35, "usd": 0.20},
    "wan-2.1-t2v-480p": {"creditos": 5,  "usd": 0.02},
    "wan-2.1-t2v-720p": {"creditos": 8,  "usd": 0.04},
}


def estimar_custo_video(modelo: str, duracao_s: float = 5.0) -> Dict[str, Any]:
    """
    Estima custo de geração de um vídeo.

    Args:
        modelo:    ID do modelo.
        duracao_s: Duração em segundos.

    Returns:
        dict com 'creditos', 'usd', 'modelo', 'duracao_s'.
    """
    base = CUSTO_ESTIMADO.get(modelo, {"creditos": 15, "usd": 0.08})
    # Custo escala com duração (base = 5s)
    fator = duracao_s / 5.0
    return {
        "creditos": round(base["creditos"] * fator),
        "usd":      round(base["usd"] * fator, 4),
        "modelo":   modelo,
        "duracao_s": duracao_s,
    }


def calcular_qa_video(producao: ProducaoVideo) -> int:
    """
    Calcula score de QA (0–100) para uma produção de vídeo.

    Returns:
        Score de 0 a 100.
    """
    score = 0

    # Status (40 pts)
    if producao.status == "completed":
        score += 40
    elif producao.status == "processing":
        score += 20

    # Prompt (20 pts)
    if len(producao.prompt_enriquecido) > 50:
        score += 10
    if len(producao.prompt_enriquecido) > 150:
        score += 10

    # Qualidade visual (20 pts)
    qualidades = {"excellent": 20, "good": 15, "fair": 10, "poor": 5}
    score += qualidades.get(producao.visual_quality, 10)

    # Motion suave (10 pts)
    if producao.motion_smooth:
        score += 10

    # Sem fallback (10 pts)
    if not producao.fallback_usado:
        score += 10

    return min(score, 100)


# ─────────────────────────────────────────────
# RESULTADO / LOG
# ─────────────────────────────────────────────

def registrar_resultado_higgsfield_video(
    job_id: str,
    video_url: Optional[str],
    video_path: Optional[str],
    prompt: str,
    nicho: str,
    modelo: str,
    duracao_s: float,
    custo_creditos: int,
) -> ProducaoVideo:
    """
    Registra o resultado de uma geração Higgsfield em um objeto ProducaoVideo.
    Chamado APÓS receber resultado do MCP mcp__Higgsfield__jobs_wait.
    """
    prod = ProducaoVideo(
        prompt=prompt,
        nicho=nicho,
        modelo=modelo,
        job_id=job_id,
        video_url=video_url,
        video_path=video_path,
        status="completed" if (video_url or video_path) else "failed",
        custo_creditos=custo_creditos,
        duracao_s=duracao_s,
        tier=1,
        fallback_usado=False,
    )
    prod.qa_score = calcular_qa_video(prod)
    return prod


# ─────────────────────────────────────────────
# CONTRATO JSON (para DARK MANAGER)
# ─────────────────────────────────────────────

CONTRATO_HIGGSFIELD_VIDEO: Dict[str, Any] = {
    "agente": "VIDEO_GENERATOR",
    "bridge": "dark_higgsfield_video_bridge",
    "versao": "1.0.0",
    "descricao": "Geração de vídeos via Higgsfield MCP com cascade automático",

    "inputs": {
        "prompt": "str — descrição em português do vídeo a gerar",
        "nicho": "str — nicho cinematográfico (documentario, natureza, historia, etc.)",
        "aspect_ratio": "str — '9:16' para Shorts ou '16:9' para YouTube padrão",
        "modelo": f"str — modelo Higgsfield (default: {MODELO_DEFAULT})",
        "duracao_s": "float — duração em segundos (3–10)",
        "imagem_base": "str|None — URL/path de imagem base para img2video",
        "movimento": "str|None — tipo de movimento (push_in, pan_left, etc.)",
    },

    "outputs": {
        "status": "ok | error",
        "job_id": "str — ID do job Higgsfield",
        "video_url": "str | None — URL do vídeo gerado",
        "video_path": "str | None — path local do vídeo",
        "qa_score": "int (0–100)",
        "backend": "higgsfield | ffmpeg_fallback",
        "tier": "int (1=Higgsfield, 2=API externa, 3=FFmpeg)",
        "custo_creditos": "int",
        "ai_generated": "bool (sempre True)",
        "ai_disclosure": "str",
    },

    "cascade": [
        {"tier": 1, "backend": "Higgsfield MCP (mcp__Higgsfield__generate_video)",
         "custo": "15–35 créditos", "qualidade": "alta"},
        {"tier": 2, "backend": "vidIQ MCP (mcp__vidIQ__vidiq_generate_video)",
         "custo": "incluso no plano vidIQ", "qualidade": "alta"},
        {"tier": 3, "backend": "FFmpeg Ken Burns (local)",
         "custo": "gratuito", "qualidade": "básica (slideshow animado)"},
    ],

    "presets_disponiveis": list(ESTILOS_VIDEO.keys()),
    "modelos_disponiveis": list(MODELOS_VIDEO.keys()),
    "movimentos_disponiveis": list(MOVIMENTOS_CAMERA.keys()),
}
