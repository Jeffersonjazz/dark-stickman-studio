"""
DARK SHORTS FACTORY
Produção automatizada de vídeos verticais 9:16 (Shorts / Reels / TikTok)
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
Custo: R$0,00/mês
"""

from __future__ import annotations
import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Optional

BASE_OUT = Path("/tmp/dark-studio/shorts")
BASE_OUT.mkdir(parents=True, exist_ok=True)

# Formatos verticais suportados
FORMATOS = {
    "shorts":  {"w": 1080, "h": 1920, "fps": 60, "dur_max": 60,  "label": "YouTube Shorts"},
    "reels":   {"w": 1080, "h": 1920, "fps": 30, "dur_max": 90,  "label": "Instagram Reels"},
    "tiktok":  {"w": 1080, "h": 1920, "fps": 30, "dur_max": 60,  "label": "TikTok"},
    "story":   {"w": 1080, "h": 1920, "fps": 30, "dur_max": 15,  "label": "Story"},
}


def _ffmpeg_ok() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        return True
    except Exception:
        return False


class DarkShortsFactory:
    """Motor de produção automatizada de vídeos verticais 9:16."""

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir) if output_dir else BASE_OUT
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ffmpeg = _ffmpeg_ok()

    # ── 1. Converter vídeo horizontal → vertical ───────────────────────────
    def converter_para_vertical(
        self,
        video_path: str,
        formato: str = "shorts",
        modo: str = "crop_center",
        output_path: Optional[str] = None,
    ) -> dict:
        """
        Converte vídeo 16:9 → 9:16.
        modos: crop_center | blur_sides | pillarbox
        """
        t0 = time.time()
        fmt = FORMATOS.get(formato, FORMATOS["shorts"])
        w, h, fps = fmt["w"], fmt["h"], fmt["fps"]

        src = Path(video_path)
        out = Path(output_path) if output_path else self.output_dir / f"vertical_{src.stem}_{formato}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)

        if not self._ffmpeg:
            return self._resultado_erro("FFmpeg não disponível", t0)

        # Filtros por modo
        if modo == "crop_center":
            # Recorta o centro do vídeo original para encaixar em 9:16
            vf = (
                f"scale=-1:{h},"
                f"crop={w}:{h}"
            )
        elif modo == "blur_sides":
            # Fundo desfocado + vídeo centralizado
            vf = (
                f"split[original][blur];"
                f"[blur]scale={w}:{h},boxblur=20:20[bg];"
                f"[original]scale=-1:{h}[fg];"
                f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
            )
        else:  # pillarbox — barras pretas
            vf = f"scale=-2:{h},pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black"

        cmd = [
            "ffmpeg", "-y", "-i", str(src),
            "-vf", vf,
            "-r", str(fps),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(out)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0 or not out.exists() or out.stat().st_size < 1000:
                return self._resultado_erro(f"FFmpeg falhou: {result.stderr[-200:]}", t0)
            return self._resultado_ok(str(out), fmt, modo, t0)
        except Exception as e:
            return self._resultado_erro(str(e), t0)

    # ── 2. Gerar short a partir de imagens (slideshow vertical) ────────────
    def gerar_slideshow_vertical(
        self,
        imagens: list[str],
        duracao_por_imagem: float = 4.0,
        formato: str = "shorts",
        audio_path: Optional[str] = None,
        output_path: Optional[str] = None,
        titulo: str = "",
        nicho: str = "geral",
    ) -> dict:
        """Gera vídeo vertical 9:16 a partir de lista de imagens."""
        t0 = time.time()
        fmt = FORMATOS.get(formato, FORMATOS["shorts"])
        w, h, fps = fmt["w"], fmt["h"], fmt["fps"]

        out_id = uuid.uuid4().hex[:8]
        out = Path(output_path) if output_path else self.output_dir / f"short_{out_id}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp_dir = self.output_dir / f"tmp_{out_id}"
        tmp_dir.mkdir(exist_ok=True)

        if not self._ffmpeg:
            return self._resultado_erro("FFmpeg não disponível", t0)

        imgs_validas = [p for p in imagens if Path(p).exists() and Path(p).stat().st_size > 100]
        if not imgs_validas:
            return self._resultado_erro("Nenhuma imagem válida fornecida", t0)

        # Redimensionar cada imagem para 9:16 e criar clipes
        clips = []
        for i, img_path in enumerate(imgs_validas):
            clip = tmp_dir / f"clip_{i:03d}.mp4"
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
                "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1",
                "-t", str(duracao_por_imagem),
                "-r", str(fps),
                "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                str(clip)
            ]
            try:
                subprocess.run(cmd, capture_output=True, timeout=30)
                if clip.exists() and clip.stat().st_size > 100:
                    clips.append(str(clip))
            except Exception:
                pass

        if not clips:
            return self._resultado_erro("Falha ao processar imagens", t0)

        # Concatenar clips
        lista_concat = tmp_dir / "concat.txt"
        lista_concat.write_text("\n".join(f"file '{c}'" for c in clips), encoding="utf-8")

        concat_raw = tmp_dir / "concat_raw.mp4"
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(lista_concat),
            "-c", "copy",
            str(concat_raw)
        ]
        try:
            subprocess.run(cmd_concat, capture_output=True, timeout=60)
        except Exception as e:
            return self._resultado_erro(f"Concat falhou: {e}", t0)

        if not concat_raw.exists() or concat_raw.stat().st_size < 500:
            return self._resultado_erro("Vídeo concatenado vazio", t0)

        # Adicionar áudio (se houver) e exportar final
        dur_total = len(imgs_validas) * duracao_por_imagem
        dur_max = fmt["dur_max"]
        dur_final = min(dur_total, dur_max)

        if audio_path and Path(audio_path).exists():
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(concat_raw),
                "-i", str(audio_path),
                "-map", "0:v", "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "128k",
                "-shortest", "-t", str(dur_final),
                "-movflags", "+faststart",
                str(out)
            ]
        else:
            cmd_final = [
                "ffmpeg", "-y",
                "-i", str(concat_raw),
                "-c:v", "copy",
                "-an",
                "-t", str(dur_final),
                "-movflags", "+faststart",
                str(out)
            ]

        try:
            subprocess.run(cmd_final, capture_output=True, timeout=120)
        except Exception as e:
            return self._resultado_erro(f"Export final falhou: {e}", t0)

        # Limpar temporários
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass

        if not out.exists() or out.stat().st_size < 1000:
            return self._resultado_erro("Short gerado inválido", t0)

        return {
            **self._resultado_ok(str(out), fmt, "slideshow", t0),
            "total_imagens": len(imgs_validas),
            "duracao_s": dur_final,
            "titulo": titulo,
            "nicho": nicho,
        }

    # ── 3. Cortar short a partir de posição em vídeo longo ─────────────────
    def cortar_short(
        self,
        video_path: str,
        inicio_s: float,
        duracao_s: float = 60.0,
        formato: str = "shorts",
        output_path: Optional[str] = None,
    ) -> dict:
        """Extrai e converte trecho de vídeo para vertical."""
        t0 = time.time()
        fmt = FORMATOS.get(formato, FORMATOS["shorts"])
        w, h = fmt["w"], fmt["h"]
        duracao_s = min(duracao_s, fmt["dur_max"])

        out_id = uuid.uuid4().hex[:8]
        out = Path(output_path) if output_path else self.output_dir / f"short_cut_{out_id}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)

        if not self._ffmpeg:
            return self._resultado_erro("FFmpeg não disponível", t0)

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(inicio_s),
            "-i", str(video_path),
            "-t", str(duracao_s),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            str(out)
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=180)
            if r.returncode != 0 or not out.exists() or out.stat().st_size < 500:
                return self._resultado_erro(f"FFmpeg: {r.stderr[-200:]}", t0)
            return {**self._resultado_ok(str(out), fmt, "cut", t0), "inicio_s": inicio_s, "duracao_s": duracao_s}
        except Exception as e:
            return self._resultado_erro(str(e), t0)

    # ── 4. Adicionar legenda grande (mobile-friendly) ──────────────────────
    def adicionar_legenda_mobile(
        self,
        video_path: str,
        texto: str,
        posicao: str = "baixo",  # alto | centro | baixo
        output_path: Optional[str] = None,
    ) -> dict:
        """Adiciona legenda grande e legível em mobile (estilo Shorts viral)."""
        t0 = time.time()
        out_id = uuid.uuid4().hex[:8]
        out = Path(output_path) if output_path else self.output_dir / f"legenda_{out_id}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)

        if not self._ffmpeg:
            return self._resultado_erro("FFmpeg não disponível", t0)

        # Posição Y da legenda
        y_map = {"alto": "h*0.1", "centro": "(h-text_h)/2", "baixo": "h*0.75"}
        y = y_map.get(posicao, "h*0.75")

        # Texto seguro para filtro drawtext
        texto_safe = texto.replace("'", "\\'").replace(":", "\\:").replace(",", "\\,")

        # Fundo semi-transparente + texto branco com borda preta
        drawtext = (
            f"drawtext=text='{texto_safe}'"
            f":fontsize=72"
            f":fontcolor=white"
            f":borderw=4"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y={y}"
            f":box=1:boxcolor=black@0.4:boxborderw=20"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "copy",
            str(out)
        ]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=120)
            if r.returncode != 0 or not out.exists() or out.stat().st_size < 500:
                # Fallback: retornar vídeo original sem legenda
                import shutil
                shutil.copy2(video_path, out)
                return {**self._resultado_ok(str(out), {}, "legenda_fallback", t0), "aviso": "drawtext não disponível"}
            return {**self._resultado_ok(str(out), {}, "legenda", t0), "texto": texto[:80]}
        except Exception as e:
            return self._resultado_erro(str(e), t0)

    # ── 5. Pipeline completo: roteiro → short ─────────────────────────────
    def produzir_short_completo(
        self,
        roteiro: str,
        formato: str = "shorts",
        nicho: str = "geral",
        imagens: Optional[list[str]] = None,
        audio_path: Optional[str] = None,
        titulo: str = "",
        output_dir: Optional[str] = None,
    ) -> dict:
        """
        Pipeline completo: imagens → slideshow vertical → legenda → short final.
        """
        t0 = time.time()
        out_dir = Path(output_dir) if output_dir else self.output_dir / uuid.uuid4().hex[:8]
        out_dir.mkdir(parents=True, exist_ok=True)

        resultados = []

        # Etapa 1: gerar imagens se não fornecidas
        if not imagens:
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent))
                from dark_image_engine import DarkImageEngine
                engine_img = DarkImageEngine(output_dir=str(out_dir / "imagens"))

                # Dividir roteiro em cenas curtas para short
                linhas = [l.strip() for l in roteiro.strip().split("\n") if l.strip()]
                cenas_short = linhas[:5]  # máx 5 cenas para um short de 60s

                imgs_result = engine_img.gerar_lote(
                    [{"prompt": c, "nicho": nicho} for c in cenas_short]
                )
                imagens = [r["image_path"] for r in imgs_result if r.get("image_path") and Path(r["image_path"]).exists()]
                resultados.append({"etapa": "imagens", "count": len(imagens), "status": "ok"})
            except Exception as e:
                resultados.append({"etapa": "imagens", "status": "erro", "erro": str(e)})

        if not imagens:
            return {
                "status": "erro",
                "mensagem": "Nenhuma imagem disponível para o short",
                "etapas": resultados,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

        # Etapa 2: slideshow vertical
        res_slide = self.gerar_slideshow_vertical(
            imagens=imagens,
            duracao_por_imagem=max(2.0, 60.0 / max(len(imagens), 1)),
            formato=formato,
            audio_path=audio_path,
            output_path=str(out_dir / "short_base.mp4"),
            titulo=titulo,
            nicho=nicho,
        )
        resultados.append({"etapa": "slideshow", **{k: v for k, v in res_slide.items() if k != "ai_generated"}})

        short_base = res_slide.get("output_path")
        if not short_base or not Path(short_base).exists():
            return {
                "status": "erro",
                "mensagem": "Slideshow vertical falhou",
                "etapas": resultados,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

        # Etapa 3: adicionar legenda (se título informado)
        short_final = short_base
        if titulo:
            res_leg = self.adicionar_legenda_mobile(
                video_path=short_base,
                texto=titulo[:60],
                posicao="baixo",
                output_path=str(out_dir / "short_com_legenda.mp4"),
            )
            resultados.append({"etapa": "legenda", "status": res_leg.get("status", "ok")})
            if res_leg.get("output_path") and Path(res_leg["output_path"]).exists():
                short_final = res_leg["output_path"]

        elapsed = round(time.time() - t0, 1)
        return {
            "status": "ok",
            "output_path": short_final,
            "formato": FORMATOS.get(formato, {}).get("label", formato),
            "resolucao": "1080x1920",
            "total_imagens": len(imagens),
            "etapas": resultados,
            "tempo_s": elapsed,
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── helpers ────────────────────────────────────────────────────────────
    def _resultado_ok(self, path: str, fmt: dict, modo: str, t0: float) -> dict:
        return {
            "status": "ok",
            "output_path": path,
            "resolucao": f"{fmt.get('w', 1080)}x{fmt.get('h', 1920)}",
            "fps": fmt.get("fps", 30),
            "modo": modo,
            "tempo_s": round(time.time() - t0, 1),
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def _resultado_erro(self, msg: str, t0: float) -> dict:
        return {
            "status": "erro",
            "mensagem": msg,
            "tempo_s": round(time.time() - t0, 1),
            "custo_brl": 0.0,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }
