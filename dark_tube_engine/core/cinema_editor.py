"""
DARK TUBE ENGINE — DARK CINEMA EDITOR (core)
Color grading, transições xfade, silence removal, pipeline cinema completo
Clone funcional: DaVinci Resolve Color + Premiere Pro transitions + Descript silence removal
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Fase 5 — DARK CINEMA EDITOR
"""
import os
import re
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


# ---------------------------------------------------------------------------
# COLOR GRADE FILTERS — per cinematic preset
# Ref: FFmpeg eq + colorbalance — gratuito, sem LUT externos necessários
# Clone funcional: DaVinci Resolve Color grading
# ---------------------------------------------------------------------------
COLOR_GRADE_FILTERS: Dict[str, Dict[str, Any]] = {
    "documentario_cinematografico": {
        "descricao": "Alto contraste, dessaturado, sombras quentes — estilo BBC Documentary",
        "eq": "eq=contrast=1.3:brightness=-0.03:saturation=0.75:gamma=1.0",
        "colorbalance": "colorbalance=rs=0.05:gs=0.02:bs=-0.05:rm=0.03:gm=0.0:bm=-0.02:rh=-0.02:gh=-0.02:bh=-0.03",
        "extra": None,
        "crf": 20,
        "preset_ffmpeg": "fast",
    },
    "natureza_selvagem": {
        "descricao": "Verdes vibrantes, quente, alta saturação — estilo Planet Earth",
        "eq": "eq=contrast=1.1:brightness=0.02:saturation=1.4:gamma=1.05",
        "colorbalance": "colorbalance=rs=-0.03:gs=0.08:bs=-0.05:rm=-0.02:gm=0.05:bm=-0.03:rh=0.02:gh=0.04:bh=-0.04",
        "extra": None,
        "crf": 20,
        "preset_ffmpeg": "fast",
    },
    "historia_acontecimentos": {
        "descricao": "Tom sépia, dessaturado, baixo contraste — estilo documental histórico",
        "eq": "eq=contrast=1.05:brightness=-0.02:saturation=0.6:gamma=1.1",
        "colorbalance": "colorbalance=rs=0.08:gs=0.02:bs=-0.10:rm=0.05:gm=0.01:bm=-0.07:rh=0.04:gh=0.01:bh=-0.06",
        "extra": "hue=s=0.65",
        "crf": 22,
        "preset_ffmpeg": "fast",
    },
    "tecnologia_ia": {
        "descricao": "Azuis frios, acentos cyan, alto contraste — estilo sci-fi/tech",
        "eq": "eq=contrast=1.35:brightness=-0.04:saturation=1.1:gamma=0.95",
        "colorbalance": "colorbalance=rs=-0.08:gs=-0.02:bs=0.12:rm=-0.05:gm=0.0:bm=0.08:rh=-0.06:gh=0.02:bh=0.10",
        "extra": None,
        "crf": 20,
        "preset_ffmpeg": "fast",
    },
    "misterio_suspense": {
        "descricao": "Low key, roxo/azul, dessaturado dramático — estilo thriller",
        "eq": "eq=contrast=1.5:brightness=-0.08:saturation=0.7:gamma=0.9",
        "colorbalance": "colorbalance=rs=-0.05:gs=-0.05:bs=0.08:rm=-0.03:gm=-0.03:bm=0.05:rh=-0.04:gh=-0.04:bh=0.07",
        "extra": "hue=h=15:s=0.75",
        "crf": 20,
        "preset_ffmpeg": "fast",
    },
    "educacao": {
        "descricao": "Neutro limpo, levemente quente — estilo YouTube educacional",
        "eq": "eq=contrast=1.1:brightness=0.01:saturation=1.05:gamma=1.0",
        "colorbalance": "colorbalance=rs=0.02:gs=0.01:bs=-0.01:rm=0.01:gm=0.01:bm=0.0:rh=0.01:gh=0.01:bh=-0.01",
        "extra": None,
        "crf": 22,
        "preset_ffmpeg": "fast",
    },
    "relaxamento": {
        "descricao": "Pastéis suaves, quente, baixo contraste — estilo lofi/meditação",
        "eq": "eq=contrast=0.9:brightness=0.04:saturation=0.85:gamma=1.1",
        "colorbalance": "colorbalance=rs=0.06:gs=0.03:bs=-0.04:rm=0.04:gm=0.02:bm=-0.02:rh=0.03:gh=0.02:bh=-0.03",
        "extra": None,
        "crf": 23,
        "preset_ffmpeg": "fast",
    },
    "storytelling_dark": {
        "descricao": "Dramático, alto contraste, sombras frias — estilo Dark Channel",
        "eq": "eq=contrast=1.45:brightness=-0.06:saturation=0.8:gamma=0.92",
        "colorbalance": "colorbalance=rs=-0.03:gs=-0.04:bs=0.06:rm=-0.02:gm=-0.02:bm=0.04:rh=-0.04:gh=-0.04:bh=0.08",
        "extra": None,
        "crf": 20,
        "preset_ffmpeg": "fast",
    },
}


# ---------------------------------------------------------------------------
# TRANSITION TYPES — xfade filter
# ---------------------------------------------------------------------------
TRANSITION_TYPES: Dict[str, Dict[str, Any]] = {
    "fade":       {"xfade": "fade",       "tempo": 0.5, "descricao": "Fade clássico"},
    "dissolve":   {"xfade": "dissolve",    "tempo": 0.6, "descricao": "Dissolve suave"},
    "wipeleft":   {"xfade": "wipeleft",    "tempo": 0.4, "descricao": "Wipe para esquerda"},
    "wiperight":  {"xfade": "wiperight",   "tempo": 0.4, "descricao": "Wipe para direita"},
    "slideright": {"xfade": "slideright",  "tempo": 0.5, "descricao": "Slide para direita"},
    "circleopen": {"xfade": "circleopen",  "tempo": 0.6, "descricao": "Abertura circular"},
    "pixelize":   {"xfade": "pixelize",    "tempo": 0.5, "descricao": "Pixelização dramática"},
    "fadegrays":  {"xfade": "fadegrays",   "tempo": 0.6, "descricao": "Fade via preto e branco"},
    "cut":        {"xfade": None,          "tempo": 0.0, "descricao": "Corte direto sem transição"},
}

# Transição padrão por preset (baseado no ritmo/estilo do preset)
PRESET_TRANSICAO_DEFAULT: Dict[str, str] = {
    "documentario_cinematografico": "dissolve",
    "natureza_selvagem":            "fade",
    "historia_acontecimentos":      "fadegrays",
    "tecnologia_ia":                "wipeleft",
    "misterio_suspense":            "circleopen",
    "educacao":                     "fade",
    "relaxamento":                  "dissolve",
    "storytelling_dark":            "dissolve",
}


# ---------------------------------------------------------------------------
# COLOR GRADING
# ---------------------------------------------------------------------------

def aplicar_color_grade(
    video_path: str,
    preset_nome: str,
    output_path: str,
    crf: Optional[int] = None,
) -> dict:
    """
    Aplica color grading ao vídeo baseado no preset cinematográfico.
    Clone funcional: DaVinci Resolve Color grading sem LUT externos.
    Stack: FFmpeg eq + colorbalance (gratuito, offline).

    Args:
        video_path: Caminho do vídeo de entrada
        preset_nome: Nome do preset cinematográfico (ver COLOR_GRADE_FILTERS)
        output_path: Caminho do vídeo de saída
        crf: CRF opcional (substitui o padrão do preset)

    Returns:
        dict com status, output_path, filtros_aplicados
    """
    if not _verificar_ffmpeg():
        return {"status": "failed", "error": "FFmpeg não encontrado"}

    if not os.path.exists(video_path):
        return {"status": "failed", "error": f"Vídeo não encontrado: {video_path}"}

    grade = COLOR_GRADE_FILTERS.get(preset_nome, COLOR_GRADE_FILTERS["storytelling_dark"])
    Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)

    # Monta cadeia de filtros
    filtros = [grade["eq"], grade["colorbalance"]]
    if grade.get("extra"):
        filtros.append(grade["extra"])
    vf = ",".join(filtros)

    _crf = crf if crf is not None else grade.get("crf", 20)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", vf,
        "-c:v", "libx264", "-crf", str(_crf),
        "-preset", grade.get("preset_ffmpeg", "fast"),
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return {
        "status": "completed" if result.returncode == 0 else "failed",
        "output_path": output_path if result.returncode == 0 else None,
        "preset": preset_nome,
        "filtros_aplicados": filtros,
        "custo": "GRATUITO — FFmpeg eq+colorbalance",
        "error": result.stderr[-500:] if result.returncode != 0 else None,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ---------------------------------------------------------------------------
# TRANSITIONS
# ---------------------------------------------------------------------------

def adicionar_transicao(
    clip1_path: str,
    clip2_path: str,
    output_path: str,
    tipo: str = "dissolve",
    duracao: Optional[float] = None,
) -> dict:
    """
    Adiciona transição entre dois clipes via FFmpeg xfade.
    Clone funcional: Premiere Pro transitions / DaVinci Resolve transitions.

    Args:
        clip1_path: Primeiro clipe
        clip2_path: Segundo clipe
        output_path: Clipe resultante com transição
        tipo: Tipo de transição (ver TRANSITION_TYPES)
        duracao: Duração da transição em segundos (None = padrão do tipo)

    Returns:
        dict com status e output_path
    """
    transicao = TRANSITION_TYPES.get(tipo, TRANSITION_TYPES["dissolve"])
    _duracao = duracao if duracao is not None else transicao["tempo"]

    # Corte direto — sem xfade
    if transicao["xfade"] is None or _duracao == 0.0:
        return _concatenar_dois_clips(clip1_path, clip2_path, output_path)

    # Precisa da duração do clip1 para calcular o offset xfade
    dur1 = _obter_duracao_video(clip1_path)
    if dur1 is None:
        # Fallback para corte direto se não conseguir duração
        return _concatenar_dois_clips(clip1_path, clip2_path, output_path)

    # offset = ponto (s) a partir do início do clip1 onde começa a transição
    offset = max(0.0, dur1 - _duracao)
    xfade_tipo = transicao["xfade"]

    Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)

    fc = (
        f"[0:v][1:v]xfade=transition={xfade_tipo}"
        f":duration={_duracao}:offset={offset:.3f}[v];"
        f"[0:a][1:a]acrossfade=d={_duracao}[a]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", clip1_path,
        "-i", clip2_path,
        "-filter_complex", fc,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # Se xfade falhar (clipes sem áudio, versão antiga de FFmpeg), cai no concat
    if result.returncode != 0:
        return _concatenar_dois_clips(clip1_path, clip2_path, output_path)

    return {
        "status": "completed",
        "output_path": output_path,
        "tipo_transicao": tipo,
        "duracao_transicao": _duracao,
        "custo": "GRATUITO — FFmpeg xfade",
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ---------------------------------------------------------------------------
# SILENCE REMOVAL
# ---------------------------------------------------------------------------

def remover_silencio(
    audio_path: str,
    output_path: str,
    threshold_db: float = -35.0,
    min_silence_duration: float = 0.5,
    padding_ms: int = 200,
) -> dict:
    """
    Detecta e remove silêncios do áudio via FFmpeg silencedetect.
    Clone funcional: Descript silence removal / Audacity truncate silence.

    Args:
        audio_path: Arquivo de áudio de entrada
        output_path: Arquivo de áudio sem silêncios
        threshold_db: dB abaixo do qual é considerado silêncio (padrão -35 dB)
        min_silence_duration: Duração mínima de silêncio a remover (segundos)
        padding_ms: Padding antes/depois de cada fala para não cortar seco (ms)

    Returns:
        dict com status, silencias_removidos, segmentos_fala
    """
    if not _verificar_ffmpeg():
        return {"status": "failed", "error": "FFmpeg não encontrado"}

    if not os.path.exists(audio_path):
        return {"status": "failed", "error": f"Áudio não encontrado: {audio_path}"}

    Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)

    # Passo 1: Detectar silêncios
    detect_cmd = [
        "ffmpeg", "-y",
        "-i", audio_path,
        "-af", f"silencedetect=n={threshold_db}dB:d={min_silence_duration}",
        "-f", "null", "-",
    ]
    result_detect = subprocess.run(detect_cmd, capture_output=True, text=True, timeout=120)
    silences = _parse_silencedetect(result_detect.stderr)

    if not silences:
        shutil.copy2(audio_path, output_path)
        return {
            "status": "completed",
            "output_path": output_path,
            "silencias_removidos": 0,
            "custo": "GRATUITO — FFmpeg silencedetect",
            "mensagem": "Nenhum silêncio longo detectado — áudio copiado",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # Passo 2: Obter duração total do áudio
    duracao_total = _obter_duracao_audio(audio_path)

    # Passo 3: Construir intervalos de fala (não-silêncio)
    padding_s = padding_ms / 1000.0
    intervals = _silences_para_intervals_fala(silences, duracao_total, padding_s)

    if not intervals:
        shutil.copy2(audio_path, output_path)
        return {
            "status": "completed",
            "output_path": output_path,
            "silencias_removidos": 0,
            "custo": "GRATUITO — FFmpeg silencedetect",
            "mensagem": "Intervalos de fala não encontrados — áudio copiado",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # Passo 4: Recortar e concatenar segmentos de fala
    temp_dir = str(Path(output_path).parent / f"tmp_sil_{uuid.uuid4().hex[:6]}")
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    temp_clips: List[str] = []

    for idx, (start, end) in enumerate(intervals):
        if end - start < 0.1:  # Ignora segmentos menores que 100ms
            continue
        clip_path = str(Path(temp_dir) / f"seg_{idx:03d}.wav")
        trim_cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-c", "copy",
            clip_path,
        ]
        r = subprocess.run(trim_cmd, capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            temp_clips.append(clip_path)

    if not temp_clips:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return {"status": "failed", "error": "Falha ao extrair segmentos de fala"}

    # Concatenar segmentos
    list_file = str(Path(temp_dir) / "list.txt")
    with open(list_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy",
        output_path,
    ]
    result_concat = subprocess.run(concat_cmd, capture_output=True, text=True, timeout=120)
    shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "status": "completed" if result_concat.returncode == 0 else "failed",
        "output_path": output_path if result_concat.returncode == 0 else None,
        "silencias_removidos": len(silences),
        "segmentos_fala": len(temp_clips),
        "custo": "GRATUITO — FFmpeg silencedetect",
        "error": result_concat.stderr[-400:] if result_concat.returncode != 0 else None,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ---------------------------------------------------------------------------
# PIPELINE CINEMA EDITOR — FLUXO COMPLETO
# ---------------------------------------------------------------------------

def pipeline_cinema_editor(
    clips: List[str],
    preset_nome: str,
    audio_path: Optional[str] = None,
    output_dir: str = "outputs/video",
    tipo_transicao: Optional[str] = None,
    resolucao: str = "1920x1080",
    remover_silencio_audio: bool = False,
    titulo: str = "",
) -> dict:
    """
    Pipeline cinema completo — clone funcional DaVinci Resolve + Premiere Pro:
    1. Aplica color grading a cada clipe (per preset)
    2. Adiciona transições entre clipes (xfade)
    3. Concatena clipes gradados com transições
    4. Se audio_path fornecido, remove silêncios (opcional) e mescla
    5. Renderiza vídeo final

    Args:
        clips: Lista de caminhos de clipes de entrada
        preset_nome: Preset cinematográfico (ver COLOR_GRADE_FILTERS)
        audio_path: Áudio de narração/trilha (opcional)
        output_dir: Diretório de saída
        tipo_transicao: Tipo de transição (None = padrão do preset)
        resolucao: Resolução de saída (ex: "1920x1080", "1080x1920")
        remover_silencio_audio: Se True, remove silêncios do áudio antes de mesclar
        titulo: Título do vídeo (para nomenclatura do arquivo)

    Returns:
        dict com status, output_path, etapas, custo
    """
    if not clips:
        return {"status": "failed", "error": "Nenhum clipe fornecido"}

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    pipe_id = uuid.uuid4().hex[:8]
    etapas: List[Dict] = []

    # ── Etapa 1: Color grading por clipe ──────────────────────────────────
    clips_gradados: List[str] = []
    for idx, clip in enumerate(clips):
        if not clip or not os.path.exists(clip):
            etapas.append({
                "etapa": f"grade_clip_{idx}",
                "status": "skipped",
                "motivo": "arquivo não encontrado",
            })
            continue
        graded_path = str(Path(output_dir) / f"graded_{pipe_id}_{idx:02d}.mp4")
        r = aplicar_color_grade(clip, preset_nome, graded_path)
        etapas.append({
            "etapa": f"grade_clip_{idx}",
            "status": r["status"],
            "path": r.get("output_path"),
        })
        # Fallback: usa original se grade falhar
        clips_gradados.append(r.get("output_path") or clip)

    if not clips_gradados:
        return {
            "status": "failed",
            "error": "Nenhum clipe disponível após color grading",
            "etapas": etapas,
        }

    # ── Etapa 2 + 3: Transições e concatenação ────────────────────────────
    _transicao = tipo_transicao or PRESET_TRANSICAO_DEFAULT.get(preset_nome, "dissolve")
    video_concatenado: Optional[str] = None

    if len(clips_gradados) == 1:
        video_concatenado = clips_gradados[0]
        etapas.append({"etapa": "transicao", "status": "skipped", "motivo": "apenas 1 clipe"})
    else:
        video_base = clips_gradados[0]
        for idx in range(1, len(clips_gradados)):
            trans_out = str(Path(output_dir) / f"trans_{pipe_id}_{idx:02d}.mp4")
            r_trans = adicionar_transicao(video_base, clips_gradados[idx], trans_out, _transicao)
            etapas.append({
                "etapa": f"transicao_{idx}",
                "status": r_trans["status"],
                "path": r_trans.get("output_path"),
            })
            if r_trans["status"] == "completed" and r_trans.get("output_path"):
                video_base = r_trans["output_path"]
        video_concatenado = video_base

    if not video_concatenado or not os.path.exists(video_concatenado):
        return {
            "status": "failed",
            "error": "Falha na composição dos clipes",
            "etapas": etapas,
        }

    # ── Etapa 4: Áudio ────────────────────────────────────────────────────
    video_final = video_concatenado
    if audio_path and os.path.exists(audio_path):
        audio_processado = audio_path

        if remover_silencio_audio:
            audio_clean = str(Path(output_dir) / f"audio_clean_{pipe_id}.wav")
            r_sil = remover_silencio(audio_path, audio_clean)
            etapas.append({
                "etapa": "remover_silencio",
                "status": r_sil["status"],
                "silencias": r_sil.get("silencias_removidos", 0),
            })
            if r_sil["status"] == "completed" and r_sil.get("output_path"):
                audio_processado = r_sil["output_path"]

        # Mescla áudio com vídeo
        slug = _slug(titulo)
        final_path = str(Path(output_dir) / f"cinema_{pipe_id}_{slug}.mp4")
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", video_concatenado,
            "-i", audio_processado,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            final_path,
        ]
        r_mix = subprocess.run(cmd_mix, capture_output=True, text=True, timeout=300)
        etapas.append({
            "etapa": "audio_merge",
            "status": "completed" if r_mix.returncode == 0 else "failed",
            "error": r_mix.stderr[-300:] if r_mix.returncode != 0 else None,
        })
        if r_mix.returncode == 0:
            video_final = final_path

    return {
        "status": "completed",
        "output_path": video_final,
        "preset": preset_nome,
        "transicao": _transicao,
        "total_clips": len(clips),
        "clips_gradados": len(clips_gradados),
        "etapas": etapas,
        "custo": "GRATUITO — FFmpeg (color grade + xfade + concat)",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def renderizar_em_lote(
    projetos: List[Dict],
    output_dir: str = "outputs/video/batch",
) -> dict:
    """
    Renderização em lote — processa múltiplos projetos sequencialmente.
    Clone funcional: DaVinci Resolve batch render / Adobe Media Encoder queue.

    Args:
        projetos: Lista de dicts com {clips, preset_nome, audio_path, titulo, tipo_transicao}
        output_dir: Diretório de saída para todos os projetos

    Returns:
        dict com status geral e lista de resultados por projeto
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    resultados: List[Dict] = []

    for idx, projeto in enumerate(projetos):
        r = pipeline_cinema_editor(
            clips=projeto.get("clips", []),
            preset_nome=projeto.get("preset_nome", "storytelling_dark"),
            audio_path=projeto.get("audio_path"),
            output_dir=output_dir,
            titulo=projeto.get("titulo", f"projeto_{idx}"),
            tipo_transicao=projeto.get("tipo_transicao"),
            remover_silencio_audio=projeto.get("remover_silencio_audio", False),
        )
        resultados.append({
            "projeto_idx": idx,
            "titulo": projeto.get("titulo", f"projeto_{idx}"),
            **r,
        })

    total_ok = sum(1 for r in resultados if r["status"] == "completed")
    return {
        "status": "completed" if total_ok > 0 else "failed",
        "total_projetos": len(projetos),
        "projetos_ok": total_ok,
        "projetos_falhos": len(projetos) - total_ok,
        "resultados": resultados,
        "custo": "GRATUITO — FFmpeg lote",
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def listar_presets() -> dict:
    """Retorna todos os presets de color grade disponíveis com descrições."""
    return {
        "presets": {nome: cfg["descricao"] for nome, cfg in COLOR_GRADE_FILTERS.items()},
        "transicoes": {nome: cfg["descricao"] for nome, cfg in TRANSITION_TYPES.items()},
        "total_presets": len(COLOR_GRADE_FILTERS),
        "total_transicoes": len(TRANSITION_TYPES),
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ---------------------------------------------------------------------------
# HELPERS INTERNOS
# ---------------------------------------------------------------------------

def _verificar_ffmpeg() -> bool:
    """Verifica se FFmpeg está disponível no PATH."""
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _obter_duracao_video(video_path: str) -> Optional[float]:
    """Retorna duração em segundos usando ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
    except Exception:
        pass
    return None


def _obter_duracao_audio(audio_path: str) -> float:
    """Retorna duração em segundos do arquivo de áudio."""
    dur = _obter_duracao_video(audio_path)  # ffprobe funciona para áudio também
    return dur or 0.0


def _parse_silencedetect(stderr: str) -> List[Dict]:
    """
    Parse da saída do silencedetect do FFmpeg.
    Retorna lista de {start, end, duration}.
    """
    silences: List[Dict] = []
    pending_start: Optional[float] = None

    for line in stderr.split("\n"):
        m_start = re.search(r"silence_start: ([\d.]+)", line)
        m_end = re.search(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", line)

        if m_start:
            pending_start = float(m_start.group(1))
        elif m_end and pending_start is not None:
            silences.append({
                "start": pending_start,
                "end": float(m_end.group(1)),
                "duration": float(m_end.group(2)),
            })
            pending_start = None

    return silences


def _silences_para_intervals_fala(
    silences: List[Dict],
    duracao_total: float,
    padding_s: float = 0.2,
) -> List[Tuple[float, float]]:
    """
    Converte lista de silêncios em intervalos de fala.
    Retorna lista de (start, end) para segmentos de fala com padding.
    """
    if not silences or duracao_total <= 0:
        return [(0.0, duracao_total)]

    intervals: List[Tuple[float, float]] = []
    cursor = 0.0

    for silence in sorted(silences, key=lambda x: x["start"]):
        fala_end = silence["start"] + padding_s
        fala_start = max(0.0, cursor - padding_s) if cursor > 0 else 0.0
        if fala_end - fala_start > 0.1:  # Mínimo 100ms de fala
            intervals.append((fala_start, min(fala_end, duracao_total)))
        cursor = silence["end"] - padding_s

    # Último segmento de fala após o último silêncio
    fala_start = max(0.0, cursor)
    if duracao_total - fala_start > 0.1:
        intervals.append((fala_start, duracao_total))

    return intervals


def _concatenar_dois_clips(clip1: str, clip2: str, output: str) -> dict:
    """Concatena dois clips sem transição (corte direto) via concat demuxer."""
    Path(os.path.dirname(output) or ".").mkdir(parents=True, exist_ok=True)
    list_file = output.replace(".mp4", "_clist.txt")
    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(clip1)}'\n")
        f.write(f"file '{os.path.abspath(clip2)}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c", "copy",
        output,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    try:
        os.remove(list_file)
    except Exception:
        pass
    return {
        "status": "completed" if r.returncode == 0 else "failed",
        "output_path": output if r.returncode == 0 else None,
        "tipo_transicao": "cut",
        "error": r.stderr[-400:] if r.returncode != 0 else None,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def _slug(texto: str, max_len: int = 25) -> str:
    """Converte texto em slug seguro para nomes de arquivo."""
    s = texto.lower().replace(" ", "_")
    s = re.sub(r"[^a-z0-9_]", "", s)
    return s[:max_len] or "video"
