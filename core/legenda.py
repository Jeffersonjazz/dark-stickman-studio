"""
DARK STICKMAN STUDIO — Geração de Legendas SRT via WhisperX
Transcrição com timestamps → arquivo SRT → burn-in no vídeo.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


# ─────────────────────────────────────────────────────────────────
#  TRANSCRIÇÃO COM WHISPERX
# ─────────────────────────────────────────────────────────────────

def transcrever_audio(
    audio_path: Path,
    output_dir: Optional[Path] = None,
    model: str = "small",
    language: str = "pt",
    device: str = "cpu",
) -> dict:
    """
    Transcreve áudio usando WhisperX com timestamps por palavra.

    Args:
        audio_path: Arquivo WAV/MP3 de entrada.
        output_dir: Diretório para salvar o JSON de resultado.
        model: Modelo Whisper ('tiny', 'small', 'medium', 'large-v2').
        language: Código de idioma ('pt' para PT-BR).
        device: 'cpu' ou 'cuda'.

    Returns:
        Dict com segmentos e timestamps.
    """
    audio_path = Path(audio_path)
    if output_dir is None:
        output_dir = audio_path.parent

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Tenta WhisperX
    try:
        return _transcrever_whisperx(audio_path, output_dir, model, language, device)
    except (ImportError, FileNotFoundError, Exception) as e:
        print(f"[LEGENDA] WhisperX indisponível: {e}")

    # Fallback: Whisper padrão
    try:
        return _transcrever_whisper(audio_path, output_dir, model, language)
    except Exception as e2:
        print(f"[LEGENDA] Whisper falhou: {e2}")

    # Fallback final: SRT vazio estruturado
    return {"segments": [], "language": language, "error": str(e2)}


def _transcrever_whisperx(
    audio_path: Path, output_dir: Path, model: str, language: str, device: str
) -> dict:
    """Transcrição com WhisperX (timestamps por palavra)."""
    import whisperx

    modelo = whisperx.load_model(model, device=device, language=language)
    audio = whisperx.load_audio(str(audio_path))
    result = modelo.transcribe(audio, language=language, batch_size=16)

    # Alinhamento de palavras
    model_a, metadata = whisperx.load_align_model(language_code=language, device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device)

    # Salva JSON
    out_json = output_dir / (audio_path.stem + "_transcricao.json")
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return result


def _transcrever_whisper(
    audio_path: Path, output_dir: Path, model: str, language: str
) -> dict:
    """Transcrição com Whisper padrão (fallback sem timestamps por palavra)."""
    import whisper

    modelo = whisper.load_model(model)
    result = modelo.transcribe(str(audio_path), language=language, word_timestamps=True)

    out_json = output_dir / (audio_path.stem + "_transcricao.json")
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    return result


# ─────────────────────────────────────────────────────────────────
#  GERAÇÃO DE SRT
# ─────────────────────────────────────────────────────────────────

def _format_timestamp(seconds: float) -> str:
    """Formata segundos em HH:MM:SS,mmm (formato SRT)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segmentos_para_srt(
    segments: List[dict],
    max_chars_por_linha: int = 42,
    max_dur_por_segmento: float = 4.0,
) -> str:
    """
    Converte lista de segmentos Whisper/WhisperX para texto SRT.

    Args:
        segments: Lista de dicts com 'start', 'end', 'text'.
        max_chars_por_linha: Limite de caracteres por segmento.
        max_dur_por_segmento: Duração máxima de um segmento SRT (segundos).

    Returns:
        String SRT completa.
    """
    linhas = []
    idx = 1

    for seg in segments:
        texto = seg.get("text", "").strip()
        inicio = seg.get("start", 0.0)
        fim = seg.get("end", inicio + 2.0)

        if not texto:
            continue

        # Quebra segmentos longos
        palavras = texto.split()
        chunks = []
        chunk_atual = []
        chars = 0

        for palavra in palavras:
            if chars + len(palavra) + 1 > max_chars_por_linha and chunk_atual:
                chunks.append(" ".join(chunk_atual))
                chunk_atual = [palavra]
                chars = len(palavra)
            else:
                chunk_atual.append(palavra)
                chars += len(palavra) + 1

        if chunk_atual:
            chunks.append(" ".join(chunk_atual))

        # Distribui timestamps entre os chunks
        dur_total = fim - inicio
        dur_por_chunk = min(dur_total / max(len(chunks), 1), max_dur_por_segmento)

        for i, chunk in enumerate(chunks):
            t_ini = inicio + i * dur_por_chunk
            t_fim = min(t_ini + dur_por_chunk, fim)
            linhas.append(str(idx))
            linhas.append(f"{_format_timestamp(t_ini)} --> {_format_timestamp(t_fim)}")
            linhas.append(chunk)
            linhas.append("")
            idx += 1

    return "\n".join(linhas)


def audio_para_srt(
    audio_path: Path,
    srt_path: Optional[Path] = None,
    model: str = "small",
    language: str = "pt",
    device: str = "cpu",
) -> Path:
    """
    Pipeline completo: áudio → transcrição → arquivo SRT.

    Returns:
        Path do arquivo .srt gerado.
    """
    audio_path = Path(audio_path)
    if srt_path is None:
        srt_path = audio_path.with_suffix(".srt")
    srt_path = Path(srt_path)

    resultado = transcrever_audio(audio_path, srt_path.parent, model, language, device)
    segments = resultado.get("segments", [])
    srt_content = segmentos_para_srt(segments)

    srt_path.write_text(srt_content, encoding="utf-8")
    print(f"[LEGENDA] SRT gerado: {srt_path} ({len(segments)} segmentos)")
    return srt_path


def srt_de_narracao(texto: str, duracao_total: float, srt_path: Path) -> Path:
    """
    Gera SRT simples a partir do texto de narração quando não há áudio ainda.
    Distribui palavras uniformemente ao longo da duração.
    Útil como fallback quando WhisperX não está disponível.
    """
    palavras = texto.split()
    total = len(palavras)
    if total == 0:
        srt_path.write_text("", encoding="utf-8")
        return srt_path

    palavras_por_seg = 8
    segmentos = []
    for i in range(0, total, palavras_por_seg):
        chunk = palavras[i : i + palavras_por_seg]
        frac_ini = i / total
        frac_fim = min((i + palavras_por_seg) / total, 1.0)
        segmentos.append({
            "start": frac_ini * duracao_total,
            "end": frac_fim * duracao_total,
            "text": " ".join(chunk),
        })

    srt_path = Path(srt_path)
    srt_path.write_text(segmentos_para_srt(segmentos), encoding="utf-8")
    return srt_path


# ─────────────────────────────────────────────────────────────────
#  BURN-IN DE LEGENDA NO VÍDEO
# ─────────────────────────────────────────────────────────────────

def burn_in_srt(
    video_path: Path,
    srt_path: Path,
    output_path: Path,
    fonte: str = "Arial",
    tamanho: int = 32,
    cor_texto: str = "white",
    cor_borda: str = "black",
) -> Path:
    """
    Queima legendas SRT no vídeo via FFmpeg drawtext.

    Returns:
        Path do vídeo com legendas.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    srt_escaped = str(srt_path).replace("\\", "/").replace(":", "\\:")

    vf = (
        f"subtitles={srt_escaped}:force_style='"
        f"FontName={fonte},"
        f"FontSize={tamanho},"
        f"PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,"
        f"BorderStyle=1,"
        f"Outline=2,"
        f"Shadow=1,"
        f"Alignment=2,"
        f"MarginV=40'"
    )

    cmd = [
        FFMPEG, "-y",
        "-i", str(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"[LEGENDA] Burn-in falhou: {result.stderr[-300:]}")
        # Retorna o vídeo sem legenda como fallback
        import shutil as sh
        sh.copy2(video_path, output_path)

    return output_path


def pipeline_legenda(
    audio_path: Path,
    video_path: Path,
    output_path: Path,
    narracao_texto: Optional[str] = None,
    model: str = "small",
    device: str = "cpu",
) -> Path:
    """
    Pipeline completo: áudio → SRT → burn-in no vídeo.
    Se WhisperX falhar e narracao_texto for fornecido, usa distribuição simples.
    """
    srt_path = audio_path.with_suffix(".srt")

    try:
        audio_para_srt(audio_path, srt_path, model=model, device=device)
    except Exception as e:
        print(f"[LEGENDA] Whisper falhou ({e}), usando distribuição de texto")
        if narracao_texto:
            from .ffmpeg_utils import get_duration
            dur = get_duration(audio_path)
            srt_de_narracao(narracao_texto, dur, srt_path)
        else:
            srt_path.write_text("", encoding="utf-8")

    return burn_in_srt(video_path, srt_path, output_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        resultado = audio_para_srt(Path(sys.argv[1]), Path(sys.argv[2]))
        print(f"SRT: {resultado}")
    else:
        print("Uso: python legenda.py <audio.wav> <saida.srt>")
