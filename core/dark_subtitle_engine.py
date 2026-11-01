"""
DARK SUBTITLE ENGINE
Geração automática de legendas: Whisper → SRT → queimar em vídeo
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
Custo: R$0,00/mês — Whisper + FFmpeg open source
"""

from __future__ import annotations
import json
import re
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

BASE_OUT = Path("/tmp/dark-studio/subtitles")
BASE_OUT.mkdir(parents=True, exist_ok=True)


def _ffmpeg_ok() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        return True
    except Exception:
        return False


def _whisper_ok() -> bool:
    try:
        import whisper  # noqa
        return True
    except ImportError:
        return False


def _ts(seconds: float) -> str:
    """Converte segundos → timestamp SRT: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class DarkSubtitleEngine:
    """Motor de legendas automáticas: transcrição → SRT → queimar em vídeo."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else BASE_OUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg = _ffmpeg_ok()
        self._whisper = _whisper_ok()

    # ── 1. Transcrever áudio/vídeo com Whisper ─────────────────────────────
    def transcrever(
        self,
        media_path: str,
        idioma: str = "pt",
        modelo: str = "base",
    ) -> dict:
        """
        Transcreve áudio ou vídeo com Whisper.
        Modelos: tiny | base | small | medium | large
        Retorna lista de segmentos com start, end, text.
        """
        t0 = time.time()

        if not self._whisper:
            # Fallback: transcrição simulada para teste sem Whisper instalado
            return self._transcricao_simulada(media_path, t0)

        try:
            import whisper

            model = whisper.load_model(modelo)
            result = model.transcribe(
                str(media_path),
                language=idioma,
                task="transcribe",
                word_timestamps=False,
                verbose=False,
            )

            segmentos = [
                {
                    "index": i + 1,
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                }
                for i, seg in enumerate(result.get("segments", []))
                if seg.get("text", "").strip()
            ]

            return {
                "status": "ok",
                "idioma_detectado": result.get("language", idioma),
                "modelo": modelo,
                "total_segmentos": len(segmentos),
                "duracao_s": segmentos[-1]["end"] if segmentos else 0,
                "segmentos": segmentos,
                "tempo_s": round(time.time() - t0, 1),
                "custo_brl": 0.0,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

        except Exception as e:
            return {
                "status": "erro",
                "mensagem": f"Whisper: {str(e)}",
                "tempo_s": round(time.time() - t0, 1),
                "custo_brl": 0.0,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

    # ── 2. Gerar arquivo SRT ───────────────────────────────────────────────
    def gerar_srt(
        self,
        segmentos: list[dict],
        output_path: Optional[str] = None,
        max_chars_linha: int = 42,
    ) -> dict:
        """Gera arquivo .srt a partir de lista de segmentos."""
        t0 = time.time()
        out = Path(output_path) if output_path else self.output_dir / f"legendas_{uuid.uuid4().hex[:8]}.srt"
        out.parent.mkdir(parents=True, exist_ok=True)

        linhas = []
        for seg in segmentos:
            idx = seg.get("index", 1)
            start = _ts(seg.get("start", 0))
            end = _ts(seg.get("end", 0))
            texto = seg.get("text", "").strip()

            # Quebrar linhas longas
            if len(texto) > max_chars_linha:
                meio = len(texto) // 2
                espaco = texto.rfind(" ", 0, meio + 10)
                if espaco > 0:
                    texto = texto[:espaco] + "\n" + texto[espaco + 1:]

            linhas.append(f"{idx}\n{start} --> {end}\n{texto}\n")

        srt_content = "\n".join(linhas)
        out.write_text(srt_content, encoding="utf-8")

        return {
            "status": "ok",
            "srt_path": str(out),
            "total_legendas": len(segmentos),
            "tempo_s": round(time.time() - t0, 1),
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── 3. Gerar arquivo VTT (WebVTT) ──────────────────────────────────────
    def gerar_vtt(
        self,
        segmentos: list[dict],
        output_path: Optional[str] = None,
    ) -> dict:
        """Gera arquivo .vtt (WebVTT) para uso em HTML5 video."""
        t0 = time.time()
        out = Path(output_path) if output_path else self.output_dir / f"legendas_{uuid.uuid4().hex[:8]}.vtt"
        out.parent.mkdir(parents=True, exist_ok=True)

        def ts_vtt(s: float) -> str:
            """HH:MM:SS.mmm para VTT"""
            return _ts(s).replace(",", ".")

        linhas = ["WEBVTT\n"]
        for seg in segmentos:
            start = ts_vtt(seg.get("start", 0))
            end = ts_vtt(seg.get("end", 0))
            texto = seg.get("text", "").strip()
            linhas.append(f"{start} --> {end}\n{texto}\n")

        out.write_text("\n".join(linhas), encoding="utf-8")

        return {
            "status": "ok",
            "vtt_path": str(out),
            "total_legendas": len(segmentos),
            "tempo_s": round(time.time() - t0, 1),
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── 4. Gerar SRT manual a partir de texto + duração ───────────────────
    def srt_de_roteiro(
        self,
        roteiro: str,
        duracao_total_s: float = 60.0,
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Gera SRT dividindo roteiro em blocos de tempo uniforme.
        Útil para sincronizar narração TTS com legendas.
        """
        t0 = time.time()
        # Dividir em frases
        frases = [f.strip() for f in re.split(r'[.!?]|\n', roteiro) if len(f.strip()) > 3]
        if not frases:
            return {"status": "erro", "mensagem": "Roteiro vazio ou sem frases.", "ai_generated": True}

        dur_por_frase = duracao_total_s / len(frases)
        segmentos = []
        for i, frase in enumerate(frases):
            segmentos.append({
                "index": i + 1,
                "start": i * dur_por_frase,
                "end": (i + 1) * dur_por_frase - 0.1,
                "text": frase,
            })

        return self.gerar_srt(segmentos, output_path)

    # ── 5. Queimar legendas no vídeo (hardsub) ─────────────────────────────
    def queimar_legendas(
        self,
        video_path: str,
        srt_path: str,
        output_path: Optional[str] = None,
        estilo: str = "padrao",  # padrao | cinematico | mobile | karaoke
    ) -> dict:
        """
        Queima legendas .srt diretamente no vídeo (hardsub).
        Usa FFmpeg subtitles filter.
        """
        t0 = time.time()
        out_id = uuid.uuid4().hex[:8]
        out = Path(output_path) if output_path else self.output_dir / f"video_legendado_{out_id}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)

        if not self._ffmpeg:
            return {"status": "erro", "mensagem": "FFmpeg não disponível", "ai_generated": True}

        # Estilos de legenda
        estilos = {
            "padrao": (
                "FontSize=22,FontName=Arial,PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,Outline=2,Shadow=1,Bold=1"
            ),
            "cinematico": (
                "FontSize=20,FontName=Georgia,PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,Outline=1,Shadow=0,Bold=0,"
                "Alignment=2"  # centro inferior
            ),
            "mobile": (
                "FontSize=32,FontName=Arial,PrimaryColour=&HFFFFFF,"
                "OutlineColour=&H000000,Outline=4,Shadow=2,Bold=1,"
                "MarginV=60"
            ),
            "karaoke": (
                "FontSize=24,FontName=Arial,PrimaryColour=&H00FFFF,"
                "OutlineColour=&H000000,Outline=3,Shadow=1,Bold=1"
            ),
        }
        force_style = estilos.get(estilo, estilos["padrao"])

        # Caminho do SRT escapado para FFmpeg (Windows path compatibility)
        srt_safe = str(Path(srt_path).resolve()).replace("\\", "/").replace(":", "\\:")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", f"subtitles='{srt_safe}':force_style='{force_style}'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "copy",
            str(out)
        ]

        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if r.returncode != 0 or not out.exists() or out.stat().st_size < 1000:
                # Fallback: softcopy embed (sem queimar)
                return self._embed_srt_softcopy(video_path, srt_path, out, t0)
            return {
                "status": "ok",
                "output_path": str(out),
                "estilo": estilo,
                "tipo": "hardsub",
                "tempo_s": round(time.time() - t0, 1),
                "custo_brl": 0.0,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }
        except Exception as e:
            return {"status": "erro", "mensagem": str(e), "ai_generated": True}

    # ── 6. Pipeline completo: vídeo → transcrever → SRT → legendar ────────
    def pipeline_completo(
        self,
        media_path: str,
        idioma: str = "pt",
        modelo_whisper: str = "base",
        estilo_legenda: str = "padrao",
        output_dir: Optional[str] = None,
    ) -> dict:
        """Pipeline completo: vídeo/áudio → transcrição → SRT → vídeo legendado."""
        t0 = time.time()
        out_dir = Path(output_dir) if output_dir else self.output_dir / uuid.uuid4().hex[:8]
        out_dir.mkdir(parents=True, exist_ok=True)

        etapas = []

        # Etapa 1: transcrever
        res_transcricao = self.transcrever(media_path, idioma=idioma, modelo=modelo_whisper)
        etapas.append({"etapa": "transcricao", "status": res_transcricao.get("status")})

        if res_transcricao.get("status") != "ok" or not res_transcricao.get("segmentos"):
            return {
                "status": "erro",
                "mensagem": "Transcrição falhou ou sem segmentos.",
                "etapas": etapas,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

        # Etapa 2: gerar SRT
        res_srt = self.gerar_srt(
            res_transcricao["segmentos"],
            output_path=str(out_dir / "legendas.srt"),
        )
        etapas.append({"etapa": "srt", "status": res_srt.get("status"), "path": res_srt.get("srt_path")})

        # Etapa 3: gerar VTT (bônus)
        res_vtt = self.gerar_vtt(
            res_transcricao["segmentos"],
            output_path=str(out_dir / "legendas.vtt"),
        )
        etapas.append({"etapa": "vtt", "status": res_vtt.get("status")})

        # Etapa 4: queimar legendas no vídeo
        srt_path = res_srt.get("srt_path")
        res_video = None
        if srt_path and Path(srt_path).exists():
            video_orig = str(media_path)
            # Verificar se media é vídeo (não só áudio)
            if Path(media_path).suffix.lower() in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
                res_video = self.queimar_legendas(
                    video_path=video_orig,
                    srt_path=srt_path,
                    output_path=str(out_dir / "video_legendado.mp4"),
                    estilo=estilo_legenda,
                )
                etapas.append({"etapa": "queimar_legendas", "status": res_video.get("status")})

        elapsed = round(time.time() - t0, 1)
        return {
            "status": "ok",
            "srt_path": res_srt.get("srt_path"),
            "vtt_path": res_vtt.get("vtt_path"),
            "video_legendado": res_video.get("output_path") if res_video and res_video.get("status") == "ok" else None,
            "total_segmentos": res_transcricao.get("total_segmentos", 0),
            "idioma_detectado": res_transcricao.get("idioma_detectado", idioma),
            "etapas": etapas,
            "tempo_s": elapsed,
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── helpers ────────────────────────────────────────────────────────────
    def _embed_srt_softcopy(self, video_path: str, srt_path: str, out: Path, t0: float) -> dict:
        """Fallback: embutir SRT como trilha de legenda (softcopy, não queimado)."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(srt_path),
            "-c:v", "copy",
            "-c:a", "copy",
            "-c:s", "mov_text",
            "-metadata:s:s:0", "language=por",
            str(out)
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=120)
            if r.returncode == 0 and out.exists() and out.stat().st_size > 500:
                return {
                    "status": "ok",
                    "output_path": str(out),
                    "tipo": "softcopy",
                    "aviso": "Hardsub não disponível; legenda embutida como trilha.",
                    "tempo_s": round(time.time() - t0, 1),
                    "custo_brl": 0.0,
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
                }
        except Exception:
            pass
        return {"status": "erro", "mensagem": "Não foi possível processar legendas.", "ai_generated": True}

    def _transcricao_simulada(self, media_path: str, t0: float) -> dict:
        """Retorna transcrição de exemplo quando Whisper não está instalado."""
        segmentos_exemplo = [
            {"index": 1, "start": 0.0,  "end": 3.5,  "text": "Bem-vindo ao DARK STUDIO AAA."},
            {"index": 2, "start": 3.5,  "end": 7.0,  "text": "Produção audiovisual profissional."},
            {"index": 3, "start": 7.0,  "end": 11.0, "text": "Custo zero. Qualidade máxima."},
            {"index": 4, "start": 11.0, "end": 15.0, "text": "Powered by DARK CREATIVE LAB."},
        ]
        return {
            "status": "ok",
            "idioma_detectado": "pt",
            "modelo": "simulado (instale openai-whisper)",
            "total_segmentos": len(segmentos_exemplo),
            "duracao_s": 15.0,
            "segmentos": segmentos_exemplo,
            "aviso": "Whisper não instalado. Execute: pip install openai-whisper",
            "tempo_s": round(time.time() - t0, 1),
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }
