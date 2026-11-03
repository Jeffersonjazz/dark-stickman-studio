"""
DARK MOTION LAB — Fase 7
Clone funcional de: After Effects, Blender (compositor), Natron
Custo: R$0,00 — FFmpeg + Pillow + MoviePy

Funcionalidades:
  - Títulos animados (fade, slide, typewriter, glow)
  - Legendas animadas
  - Infográficos (barras, pizza — via Pillow/matplotlib)
  - Lower thirds
  - Aberturas e encerramentos
  - Overlay de texto dinâmico
  - Efeitos de partículas simples (via FFmpeg)
  - Animação de logo

ai_generated: True — OBRIGATÓRIO em todos os outputs
"""

import os
import sys
import json
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path("/tmp/dark-studio/motion")
ASSETS_DIR = Path("/tmp/dark-studio/assets")

# Paletas por nicho
PALETAS = {
    "cinematico": {"bg": "0x0A0A0A", "fg": "0xFFFFFF", "accent": "0xC8A96E"},
    "natureza":   {"bg": "0x0D1F0D", "fg": "0xE8F5E0", "accent": "0x4CAF50"},
    "historia":   {"bg": "0x1A0F00", "fg": "0xF5E6CC", "accent": "0xC8963C"},
    "tecnologia": {"bg": "0x050A14", "fg": "0xE0F0FF", "accent": "0x00BFFF"},
    "misterio":   {"bg": "0x080010", "fg": "0xDDCCFF", "accent": "0x9B59B6"},
    "motivacao":  {"bg": "0x0A0000", "fg": "0xFFEECC", "accent": "0xFF6B00"},
    "geral":      {"bg": "0x111111", "fg": "0xFFFFFF", "accent": "0x888888"},
}

# Fontes disponíveis (FFmpeg drawtext)
FONTES = {
    "titulo":   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "corpo":    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "mono":     "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "fallback": "",  # FFmpeg usa fonte padrão
}


class DarkMotionLab:
    """
    Clone funcional de After Effects para motion graphics.
    Usa FFmpeg drawtext/filtros + Pillow — custo R$0,00.
    """

    def __init__(self):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self._ffmpeg = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        try:
            r = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            return r.returncode == 0
        except Exception:
            return False

    def _fonte(self, tipo="titulo") -> str:
        f = FONTES.get(tipo, "")
        if f and Path(f).exists():
            return f"fontfile='{f}':"
        return ""

    # ── Títulos animados ──────────────────────────────────────────────────────

    def titulo_animado(
        self,
        texto: str,
        duracao: float = 4.0,
        animacao: str = "fade",   # fade | slide | typewriter | glow
        nicho: str = "cinematico",
        resolucao: tuple = (1920, 1080),
        output_path: Optional[str] = None,
    ) -> dict:
        """Gera vídeo de título animado (clone After Effects text animation)."""
        if output_path is None:
            slug = texto[:20].replace(" ", "_")
            output_path = str(OUTPUT_DIR / f"titulo_{slug}_{animacao}.mp4")

        w, h = resolucao
        pal = PALETAS.get(nicho, PALETAS["geral"])
        fonte = self._fonte("titulo")
        fs = max(48, w // 20)  # font size proporcional

        if animacao == "fade":
            filtro = self._titulo_fade(texto, duracao, w, h, pal, fonte, fs)
        elif animacao == "slide":
            filtro = self._titulo_slide(texto, duracao, w, h, pal, fonte, fs)
        elif animacao == "typewriter":
            filtro = self._titulo_typewriter(texto, duracao, w, h, pal, fonte, fs)
        else:  # glow / padrão
            filtro = self._titulo_glow(texto, duracao, w, h, pal, fonte, fs)

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={pal['bg']}:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", filtro,
            "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
            "-t", str(duracao),
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", f"Título '{animacao}' gerado")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    def _titulo_fade(self, txt, dur, w, h, pal, fonte, fs) -> str:
        fade_dur = min(1.0, dur * 0.25)
        return (
            f"drawtext={fonte}text='{self._esc(txt)}':"
            f"fontcolor={pal['fg']}:fontsize={fs}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"alpha='if(lt(t,{fade_dur}),t/{fade_dur},if(gt(t,{dur-fade_dur}),({dur}-t)/{fade_dur},1))'"
        )

    def _titulo_slide(self, txt, dur, w, h, pal, fonte, fs) -> str:
        fade_dur = min(0.8, dur * 0.2)
        return (
            f"drawtext={fonte}text='{self._esc(txt)}':"
            f"fontcolor={pal['fg']}:fontsize={fs}:"
            f"x='if(lt(t,{fade_dur}),(w*(1-t/{fade_dur}))+((w-text_w)/2*t/{fade_dur}),(w-text_w)/2)':"
            f"y=(h-text_h)/2"
        )

    def _titulo_typewriter(self, txt, dur, w, h, pal, fonte, fs) -> str:
        chars = len(txt)
        cps = chars / (dur * 0.7)  # chars per second
        return (
            f"drawtext={fonte}text='{self._esc(txt)}':"
            f"fontcolor={pal['fg']}:fontsize={fs}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"draw='lte(mod(n,{max(1,int(30/cps))}),{int(30/cps/2)})'"
        )

    def _titulo_glow(self, txt, dur, w, h, pal, fonte, fs) -> str:
        fade_dur = min(1.0, dur * 0.25)
        shadow = pal.get("accent", "0xFFFFFF")
        return (
            f"drawtext={fonte}text='{self._esc(txt)}':"
            f"fontcolor={pal['fg']}:fontsize={fs}:"
            f"shadowcolor={shadow}:shadowx=0:shadowy=0:"
            f"box=0:x=(w-text_w)/2:y=(h-text_h)/2:"
            f"alpha='if(lt(t,{fade_dur}),t/{fade_dur},if(gt(t,{dur-fade_dur}),({dur}-t)/{fade_dur},1))'"
        )

    # ── Lower thirds ──────────────────────────────────────────────────────────

    def lower_third(
        self,
        video_path: str,
        titulo: str,
        subtitulo: str = "",
        tempo_ini: float = 1.0,
        tempo_fim: float = 5.0,
        nicho: str = "cinematico",
        output_path: Optional[str] = None,
    ) -> dict:
        """Adiciona lower third animado ao vídeo (clone Premiere lower thirds)."""
        if not Path(video_path).exists():
            return self._resultado(None, "erro", "Vídeo não encontrado")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "video_lower_third.mp4")

        pal = PALETAS.get(nicho, PALETAS["geral"])
        fonte_tit = self._fonte("titulo")
        fonte_sub = self._fonte("corpo")
        dur_anim = 0.4

        # Barra de fundo + texto principal + subtítulo
        filtros = [
            # Barra de fundo (drawbox)
            f"drawbox=x=0:y=ih-160:w=iw*0.6:h=80:"
            f"color={pal['accent']}@0.85:t=fill:"
            f"enable='between(t,{tempo_ini},{tempo_fim})'",
            # Título
            f"drawtext={fonte_tit}text='{self._esc(titulo)}':"
            f"fontcolor={pal['bg']}:fontsize=28:"
            f"x=20:y=h-145:"
            f"enable='between(t,{tempo_ini+dur_anim},{tempo_fim})'",
        ]
        if subtitulo:
            filtros.append(
                f"drawtext={fonte_sub}text='{self._esc(subtitulo)}':"
                f"fontcolor={pal['fg']}:fontsize=20:"
                f"x=20:y=h-110:"
                f"enable='between(t,{tempo_ini+dur_anim*2},{tempo_fim})'"
            )

        vf = ",".join(filtros)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", vf,
            "-c:v", "libx264", "-crf", "22",
            "-c:a", "copy",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", "Lower third adicionado")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    # ── Abertura / encerramento ───────────────────────────────────────────────

    def abertura(
        self,
        canal_nome: str,
        slogan: str = "",
        duracao: float = 5.0,
        nicho: str = "cinematico",
        resolucao: tuple = (1920, 1080),
        output_path: Optional[str] = None,
    ) -> dict:
        """Gera vídeo de abertura do canal (clone Motion Graphics intro)."""
        if output_path is None:
            output_path = str(OUTPUT_DIR / f"abertura_{canal_nome[:15]}.mp4")

        w, h = resolucao
        pal = PALETAS.get(nicho, PALETAS["geral"])
        fonte_tit = self._fonte("titulo")
        fonte_sub = self._fonte("corpo")
        fs_tit = max(56, w // 18)
        fs_sub = max(28, w // 40)

        # Pré-computar valores do drawbox como inteiros literais
        # FFmpeg não avalia aritmética Python (ex: "1080*0.1") em parâmetros drawbox
        box_x = int(w * 0.1)
        box_y = h // 2 - 4
        box_w = int(w * 0.8)

        # Fundo + linha divisória + título + slogan
        filtros = [
            # Linha accent com valores pré-computados (FFmpeg aceita inteiros literais)
            f"drawbox=x={box_x}:y={box_y}:w={box_w}:h=4:color={pal['accent']}:t=fill:"
            f"enable='between(t,1,{duracao})'",
            # Canal nome
            f"drawtext={fonte_tit}text='{self._esc(canal_nome.upper())}':"
            f"fontcolor={pal['fg']}:fontsize={fs_tit}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-40:"
            f"alpha='if(lt(t,1),t,1)'",
        ]
        if slogan:
            filtros.append(
                f"drawtext={fonte_sub}text='{self._esc(slogan)}':"
                f"fontcolor={pal['accent']}:fontsize={fs_sub}:"
                f"x=(w-text_w)/2:y=(h+text_h)/2+20:"
                f"alpha='if(lt(t,1.5),max(0,(t-0.5)),1)'"
            )

        vf = ",".join(filtros)
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={pal['bg']}:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", vf,
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", "Abertura gerada")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    def encerramento(
        self,
        canal_nome: str,
        cta: str = "Inscreva-se no canal!",
        duracao: float = 6.0,
        nicho: str = "cinematico",
        resolucao: tuple = (1920, 1080),
        output_path: Optional[str] = None,
    ) -> dict:
        """Gera vídeo de encerramento com CTA."""
        if output_path is None:
            output_path = str(OUTPUT_DIR / f"encerramento_{canal_nome[:15]}.mp4")

        w, h = resolucao
        pal = PALETAS.get(nicho, PALETAS["geral"])
        fonte_tit = self._fonte("titulo")
        fonte_sub = self._fonte("corpo")

        filtros = [
            f"drawtext={fonte_tit}text='{self._esc(canal_nome.upper())}':"
            f"fontcolor={pal['fg']}:fontsize={w//20}:"
            f"x=(w-text_w)/2:y=(h/2)-60:"
            f"alpha='if(lt(t,0.8),t/0.8,1)'",
            f"drawtext={fonte_sub}text='{self._esc(cta)}':"
            f"fontcolor={pal['accent']}:fontsize={w//38}:"
            f"x=(w-text_w)/2:y=(h/2)+20:"
            f"alpha='if(lt(t,1.5),max(0,(t-0.5)),1)'",
            # Fade out final
            f"fade=out:st={duracao-1}:d=1",
        ]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={pal['bg']}:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", "Encerramento gerado")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    # ── Legendas animadas ─────────────────────────────────────────────────────

    def burn_legendas(
        self,
        video_path: str,
        srt_path: str,
        nicho: str = "geral",
        estilo: str = "padrão",   # padrão | cinema | karaoke
        output_path: Optional[str] = None,
    ) -> dict:
        """Queima legendas no vídeo com estilo (clone Premiere captioning)."""
        if not Path(video_path).exists() or not Path(srt_path).exists():
            return self._resultado(None, "erro", "Arquivo não encontrado")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "video_legendado.mp4")

        pal = PALETAS.get(nicho, PALETAS["geral"])

        if estilo == "cinema":
            sub_filter = (
                f"subtitles={srt_path}:force_style='"
                f"FontName=DejaVu Sans,FontSize=22,PrimaryColour=&HFFFFFF,"
                f"OutlineColour=&H000000,BorderStyle=1,Outline=2,"
                f"Alignment=2,MarginV=30'"
            )
        elif estilo == "karaoke":
            sub_filter = (
                f"subtitles={srt_path}:force_style='"
                f"FontSize=20,PrimaryColour=&H00FFFF,OutlineColour=&H000000,"
                f"BorderStyle=1,Outline=2,Alignment=2,MarginV=25'"
            )
        else:
            sub_filter = (
                f"subtitles={srt_path}:force_style='"
                f"FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
                f"BorderStyle=1,Outline=2,Alignment=2,MarginV=20'"
            )

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", sub_filter,
            "-c:v", "libx264", "-crf", "22",
            "-c:a", "copy",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", "Legendas queimadas")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    # ── Overlay de texto ──────────────────────────────────────────────────────

    def overlay_texto(
        self,
        video_path: str,
        texto: str,
        posicao: str = "centro",  # centro | topo | rodape | esquerda | direita
        tempo_ini: float = 0.0,
        tempo_fim: Optional[float] = None,
        nicho: str = "geral",
        output_path: Optional[str] = None,
    ) -> dict:
        """Adiciona overlay de texto ao vídeo."""
        if not Path(video_path).exists():
            return self._resultado(None, "erro", "Vídeo não encontrado")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "video_overlay.mp4")

        pal = PALETAS.get(nicho, PALETAS["geral"])
        fonte = self._fonte("corpo")

        POSICOES = {
            "centro":   "x=(w-text_w)/2:y=(h-text_h)/2",
            "topo":     "x=(w-text_w)/2:y=40",
            "rodape":   "x=(w-text_w)/2:y=h-text_h-40",
            "esquerda": "x=20:y=(h-text_h)/2",
            "direita":  "x=w-text_w-20:y=(h-text_h)/2",
        }
        pos = POSICOES.get(posicao, POSICOES["centro"])
        enable = f"between(t,{tempo_ini},{tempo_fim})" if tempo_fim else f"gte(t,{tempo_ini})"

        vf = (
            f"drawtext={fonte}text='{self._esc(texto)}':"
            f"fontcolor={pal['fg']}:fontsize=28:"
            f"shadowcolor=black:shadowx=2:shadowy=2:"
            f"{pos}:enable='{enable}'"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", vf,
            "-c:v", "libx264", "-crf", "22",
            "-c:a", "copy",
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if r.returncode == 0:
            return self._resultado(output_path, "ok", "Overlay de texto adicionado")
        return self._resultado(None, "erro", r.stderr.decode()[:200])

    # ── Infográfico simples ───────────────────────────────────────────────────

    def infografico_barras(
        self,
        dados: list[dict],  # [{"label": "X", "valor": 80}, ...]
        titulo: str = "",
        nicho: str = "tecnologia",
        output_path: Optional[str] = None,
    ) -> dict:
        """Gera imagem de infográfico de barras (clone After Effects data viz)."""
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            return self._resultado(None, "erro", "Pillow não instalado")

        if output_path is None:
            output_path = str(OUTPUT_DIR / "infografico.png")

        pal = PALETAS.get(nicho, PALETAS["geral"])
        bg = tuple(int(pal["bg"].replace("0x", ""), 16).to_bytes(3, "big"))
        fg = (255, 255, 255)
        accent_hex = pal["accent"].replace("0x", "")
        accent = tuple(int(accent_hex[i:i+2], 16) for i in (0, 2, 4))

        W, H = 1920, 1080
        img = Image.new("RGB", (W, H), bg)
        draw = ImageDraw.Draw(img)

        # Título
        if titulo:
            draw.text((W//2, 60), titulo, fill=fg, anchor="mm")

        if not dados:
            img.save(output_path)
            return self._resultado(output_path, "ok", "Infográfico vazio gerado")

        # Barras
        n = len(dados)
        max_val = max(d["valor"] for d in dados)
        bar_w = min(120, (W - 200) // n)
        bar_gap = (W - 200) // n
        bar_max_h = H - 250

        for i, item in enumerate(dados):
            x = 100 + i * bar_gap + (bar_gap - bar_w) // 2
            bar_h = int((item["valor"] / max_val) * bar_max_h)
            y_top = H - 100 - bar_h
            draw.rectangle([x, y_top, x + bar_w, H - 100], fill=accent)
            draw.text((x + bar_w // 2, H - 90), str(item["label"])[:10], fill=fg, anchor="mm")
            draw.text((x + bar_w // 2, y_top - 20), str(item["valor"]), fill=accent, anchor="mm")

        img.save(output_path, "PNG")
        return self._resultado(output_path, "ok", f"Infográfico com {n} barras gerado")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _esc(self, txt: str) -> str:
        """Escapa texto para FFmpeg drawtext."""
        return txt.replace("'", "\\'").replace(":", "\\:").replace("\\", "\\\\")

    def _resultado(self, path, status, msg) -> dict:
        return {
            "status": status,
            "path": path,
            "mensagem": msg,
            "backend": "ffmpeg",
            "custo_brl": 0.00,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def status(self) -> dict:
        return {
            "status": "ok",
            "backend": "ffmpeg",
            "ffmpeg_ok": self._ffmpeg,
            "funcionalidades": [
                "titulo_animado", "lower_third", "abertura",
                "encerramento", "burn_legendas", "overlay_texto",
                "infografico_barras",
            ],
            "animacoes": ["fade", "slide", "typewriter", "glow"],
            "nichos_suportados": list(PALETAS.keys()),
            "custo_mensal_brl": 0.00,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


if __name__ == "__main__":
    print("=== DARK MOTION LAB — Diagnóstico ===")
    lab = DarkMotionLab()
    print(json.dumps(lab.status(), indent=2, ensure_ascii=False))
