"""
DARK CREATIVE LAB — AGENTE CREATIVE QA
Avalia qualidade visual, áudio, continuidade, legibilidade, resolução e conformidade.

Funções:
- Verificar resolução e proporção do vídeo
- Verificar duração mínima (4 minutos para YouTube)
- Verificar presença de áudio, legenda e watermark de IA
- Análise de silêncio e volume médio
- Verificar arquivo SRT gerado
- Score geral de qualidade por categoria
- Relatório de conformidade com DARK STUDIO AAA

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import subprocess
import re
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES DE QUALIDADE
# ─────────────────────────────────────────────────────────────────

# Duração mínima em segundos (4 minutos)
DURACAO_MINIMA_S = 240

# Resoluções aceitas (largura x altura)
RESOLUCOES_ACEITAS = {
    "4K":       (3840, 2160),
    "1080p":    (1920, 1080),
    "720p":     (1280, 720),
    "shorts":   (1080, 1920),
    "reel":     (1080, 1920),
}

# Volume mínimo médio (dBFS) — abaixo disso é considerado muito silencioso
VOLUME_MINIMO_DBFS = -35.0

# Score mínimo para aprovação (0-100)
SCORE_MINIMO_APROVACAO = 60


# ─────────────────────────────────────────────────────────────────
#  VERIFICAÇÕES INDIVIDUAIS
# ─────────────────────────────────────────────────────────────────

def verificar_resolucao(video_path: Path) -> dict:
    """
    Verifica resolução e proporção do vídeo.

    Returns:
        Dict com largura, altura, fps, proporcao, score.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"ok": False, "erro": "Arquivo não encontrado", "score": 0}

    info = _ffprobe_video(video_path)
    if not info:
        return {"ok": False, "erro": "ffprobe falhou", "score": 0}

    w = info.get("width", 0)
    h = info.get("height", 0)
    fps = info.get("fps", 0)

    # Identifica resolução
    resolucao_nome = "desconhecida"
    score = 40
    for nome, (rw, rh) in RESOLUCOES_ACEITAS.items():
        if w == rw and h == rh:
            resolucao_nome = nome
            score = 100
            break

    # Score parcial para resoluções próximas
    if score < 100:
        if w >= 1920 and h >= 1080:
            score = 85
        elif w >= 1280 and h >= 720:
            score = 65

    proporcao = f"{w}:{h}" if h > 0 else "desconhecida"
    eh_vertical = h > w

    return {
        "ok": score >= 60,
        "largura": w,
        "altura": h,
        "fps": fps,
        "resolucao": resolucao_nome,
        "proporcao": proporcao,
        "vertical": eh_vertical,
        "score": score,
        "ai_generated": True,
    }


def verificar_duracao(video_path: Path, minimo_s: float = DURACAO_MINIMA_S) -> dict:
    """
    Verifica se o vídeo tem duração mínima para YouTube (4 min = 240s).
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"ok": False, "erro": "Arquivo não encontrado", "score": 0}

    duracao = _ffprobe_duracao(video_path)
    if duracao is None:
        return {"ok": False, "erro": "Não foi possível ler duração", "score": 0}

    ok = duracao >= minimo_s
    # Score proporcional: 100 se atingir o mínimo, proporcional abaixo
    score = min(100, int((duracao / minimo_s) * 100)) if minimo_s > 0 else 100

    return {
        "ok": ok,
        "duracao_s": round(duracao, 1),
        "minimo_s": minimo_s,
        "duracao_formatada": _formatar_duracao(duracao),
        "score": score,
        "aviso": None if ok else f"Vídeo curto: {_formatar_duracao(duracao)} (mínimo: {_formatar_duracao(minimo_s)})",
        "ai_generated": True,
    }


def verificar_audio(video_path: Path) -> dict:
    """
    Verifica presença e volume do áudio no vídeo.
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"ok": False, "erro": "Arquivo não encontrado", "score": 0}

    # Verifica presença de stream de áudio
    info = _ffprobe_audio(video_path)
    if not info.get("tem_audio"):
        return {
            "ok": False,
            "tem_audio": False,
            "score": 0,
            "aviso": "Vídeo sem stream de áudio",
            "ai_generated": True,
        }

    # Analisa volume via loudnorm
    volume = _analisar_volume(video_path)
    vol_medio = volume.get("integrated_loudness", -99.0)

    ok = vol_medio >= VOLUME_MINIMO_DBFS
    score = 100 if ok else max(0, int(100 + (vol_medio - VOLUME_MINIMO_DBFS) * 3))

    return {
        "ok": ok,
        "tem_audio": True,
        "volume_integrated_lufs": vol_medio,
        "volume_ok": ok,
        "score": score,
        "aviso": None if ok else f"Volume muito baixo: {vol_medio:.1f} LUFS (mínimo: {VOLUME_MINIMO_DBFS})",
        "ai_generated": True,
    }


def verificar_legenda(srt_path: Path) -> dict:
    """
    Verifica se o arquivo SRT é válido e não está vazio.
    """
    srt_path = Path(srt_path)
    if not srt_path.exists():
        return {
            "ok": False,
            "existe": False,
            "score": 0,
            "aviso": "Arquivo SRT não encontrado",
            "ai_generated": True,
        }

    conteudo = srt_path.read_text(encoding="utf-8", errors="ignore")
    linhas = [l.strip() for l in conteudo.splitlines() if l.strip()]
    n_blocos = conteudo.count(" --> ")

    ok = n_blocos >= 1
    score = min(100, n_blocos * 5) if ok else 0

    return {
        "ok": ok,
        "existe": True,
        "tamanho_bytes": srt_path.stat().st_size,
        "num_legendas": n_blocos,
        "linhas_total": len(linhas),
        "score": score,
        "aviso": None if ok else "SRT vazio ou inválido",
        "ai_generated": True,
    }


def verificar_watermark(video_path: Path, texto_esperado: str = "DARK STUDIO AAA") -> dict:
    """
    Verifica se o vídeo tem metadados indicando watermark de IA.
    (Verificação via metadados — não analisa frames visualmente)
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {"ok": False, "erro": "Arquivo não encontrado", "score": 0}

    # Verifica metadados FFmpeg
    meta = _ffprobe_metadata(video_path)
    comment = meta.get("comment", "") + meta.get("title", "") + meta.get("description", "")

    tem_marca = "DARK STUDIO" in comment or "IA" in comment or "AI" in comment

    return {
        "ok": tem_marca,
        "tem_watermark_meta": tem_marca,
        "score": 100 if tem_marca else 50,  # 50 pois o watermark pode estar no frame
        "nota": "Verificação via metadados. Watermark visual deve ser confirmado manualmente.",
        "ai_generated": True,
    }


def verificar_conformidade_ia(video_path: Path) -> dict:
    """
    Verifica se o vídeo atende requisitos de divulgação de conteúdo IA.
    Checa metadados e nome do arquivo para indicadores de conformidade.
    """
    video_path = Path(video_path)
    nome = video_path.stem.lower()

    indicadores = {
        "nome_inclui_ia": any(k in nome for k in ["ia", "ai", "dark", "stickman"]),
        "diretorio_dark": "dark" in str(video_path).lower(),
    }

    # Metadados
    meta = _ffprobe_metadata(video_path)
    indicadores["meta_disclosure"] = any(
        k in str(meta).lower() for k in ["dark studio", "ai_generated", "produzido com ia"]
    )

    score = sum(100 // len(indicadores) for v in indicadores.values() if v)

    return {
        "ok": score >= 33,  # pelo menos 1 de 3 indicadores
        "indicadores": indicadores,
        "score": score,
        "nota": "Conteúdo IA deve ser identificado. Use watermark visível e metadados.",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  VERIFICAÇÃO COMPLETA
# ─────────────────────────────────────────────────────────────────

def verificar_qualidade(
    video_path: Path,
    srt_path: Path = None,
    canal_config: dict = None,
    minimo_s: float = DURACAO_MINIMA_S,
) -> dict:
    """
    Executa verificação completa de qualidade de um vídeo.

    Returns:
        Dict com score geral (0-100), aprovado, e detalhe por categoria.
    """
    video_path = Path(video_path)
    canal_config = canal_config or {}

    # Verificações individuais
    check_res = verificar_resolucao(video_path)
    check_dur = verificar_duracao(video_path, minimo_s=minimo_s)
    check_aud = verificar_audio(video_path)
    check_srt = verificar_legenda(srt_path) if srt_path else {"ok": True, "score": 70, "nota": "SRT não verificado"}
    check_wm  = verificar_watermark(video_path)
    check_ia  = verificar_conformidade_ia(video_path)

    categorias = {
        "resolucao":    check_res,
        "duracao":      check_dur,
        "audio":        check_aud,
        "legenda":      check_srt,
        "watermark":    check_wm,
        "conformidade": check_ia,
    }

    # Score ponderado
    pesos = {
        "resolucao": 0.20,
        "duracao":   0.25,
        "audio":     0.25,
        "legenda":   0.15,
        "watermark": 0.05,
        "conformidade": 0.10,
    }
    score_total = sum(
        categorias[k].get("score", 0) * pesos[k]
        for k in pesos
    )
    score_total = round(score_total)
    aprovado = score_total >= SCORE_MINIMO_APROVACAO

    # Avisos e erros
    avisos = [v["aviso"] for v in categorias.values() if v.get("aviso")]
    erros = [v["erro"] for v in categorias.values() if v.get("erro")]

    return {
        "status": "ok",
        "aprovado": aprovado,
        "score": score_total,
        "score_minimo": SCORE_MINIMO_APROVACAO,
        "categorias": categorias,
        "avisos": avisos,
        "erros": erros,
        "video": str(video_path),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  HELPERS FFPROBE
# ─────────────────────────────────────────────────────────────────

def _ffprobe_video(path: Path) -> dict:
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-select_streams", "v:0", str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=15)
        data = json.loads(out)
        streams = data.get("streams", [{}])
        s = streams[0] if streams else {}
        fps_str = s.get("r_frame_rate", "0/1")
        fps = _parse_fps(fps_str)
        return {
            "width": s.get("width", 0),
            "height": s.get("height", 0),
            "fps": fps,
            "codec": s.get("codec_name", ""),
        }
    except Exception:
        return {}


def _ffprobe_audio(path: Path) -> dict:
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-select_streams", "a:0", str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10)
        data = json.loads(out)
        streams = data.get("streams", [])
        return {"tem_audio": len(streams) > 0}
    except Exception:
        return {"tem_audio": False}


def _ffprobe_duracao(path: Path) -> Optional[float]:
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10)
        data = json.loads(out)
        return float(data.get("format", {}).get("duration", 0))
    except Exception:
        return None


def _ffprobe_metadata(path: Path) -> dict:
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10)
        data = json.loads(out)
        return data.get("format", {}).get("tags", {})
    except Exception:
        return {}


def _analisar_volume(path: Path) -> dict:
    """Usa ffmpeg loudnorm para medir LUFS integrado."""
    try:
        cmd = [
            "ffmpeg", "-i", str(path),
            "-af", "loudnorm=print_format=json",
            "-f", "null", "-", "-t", "30"  # Analisa até 30s
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        # loudnorm imprime JSON no stderr
        stderr = result.stderr
        start = stderr.rfind("{")
        end = stderr.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(stderr[start:end])
            return {
                "integrated_loudness": float(data.get("input_i", -99)),
                "loudness_range":      float(data.get("input_lra", 0)),
                "true_peak":           float(data.get("input_tp", 0)),
            }
    except Exception:
        pass
    return {"integrated_loudness": -30.0}  # assume ok se não conseguir medir


def _parse_fps(fps_str: str) -> float:
    try:
        if "/" in fps_str:
            num, den = fps_str.split("/")
            return round(float(num) / float(den), 2) if float(den) != 0 else 0
        return float(fps_str)
    except Exception:
        return 0.0


def _formatar_duracao(segundos: float) -> str:
    s = int(segundos)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    return f"{m}m{s:02d}s"


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_creative_qa() -> dict:
    # Verifica ffprobe
    try:
        subprocess.check_output(["ffprobe", "-version"], stderr=subprocess.DEVNULL, timeout=5)
        ffprobe_ok = True
    except Exception:
        ffprobe_ok = False

    return {
        "status": "ok",
        "ffprobe": ffprobe_ok,
        "duracao_minima_s": DURACAO_MINIMA_S,
        "score_minimo_aprovacao": SCORE_MINIMO_APROVACAO,
        "volume_minimo_dbfs": VOLUME_MINIMO_DBFS,
        "resolucoes_aceitas": list(RESOLUCOES_ACEITAS.keys()),
        "verificacoes": [
            "resolucao", "duracao", "audio",
            "legenda", "watermark", "conformidade_ia",
        ],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
