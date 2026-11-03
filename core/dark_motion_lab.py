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

    # ── Contagem regressiva ───────────────────────────────────────────────────

    def contagem_regressiva(
        self,
        output_path: str,
        segundos: int = 5,
        estilo: str = "cinematico",
        resolucao: tuple = (1920, 1080),
    ) -> dict:
        """
        Gera vídeo de contagem regressiva estilo cinema (clone After Effects countdown).
        Contagem de `segundos` até 1, seguida de flash branco.
        Usa FFmpeg drawtext com expressão de tempo — custo R$0,00.
        """
        w, h = resolucao
        pal = PALETAS.get(estilo, PALETAS["cinematico"])
        fonte = self._fonte("titulo")
        fs = max(120, w // 10)
        duracao_total = float(segundos + 0.5)  # +0.5s para o flash

        # Cada dígito aparece por 1s; expr arredonda o segundo restante
        # Flash branco no último 0.3s
        filtros = [
            # Número da contagem regressiva
            f"drawtext={fonte}"
            f"text='%{{eif\\:max(0\\,{segundos}-floor(t))\\:d}}':"
            f"fontcolor={pal['fg']}:fontsize={fs}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='lte(t,{segundos})'",
            # Linha de progresso embaixo
            f"drawbox=x=0:y={h-8}:w='iw*min(t/{segundos},1)':h=8:"
            f"color={pal['accent']}:t=fill:"
            f"enable='lte(t,{segundos})'",
            # Flash branco no final
            f"fade=in:st={segundos}:d=0.15:color=white",
            f"fade=out:st={segundos+0.15}:d=0.35",
        ]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={pal['bg']}:size={w}x{h}:rate=30:duration={duracao_total}",
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            "-t", str(duracao_total),
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            res = self._resultado(output_path, "ok", f"Contagem regressiva {segundos}s gerada")
            res.update({"output": output_path, "duracao": duracao_total})
            return res
        return self._resultado(None, "erro", r.stderr.decode()[:300])

    # ── Animação de logo ──────────────────────────────────────────────────────

    def animacao_logo(
        self,
        canal_nome: str,
        output_path: str,
        duracao: float = 3.0,
        cor_primaria: str = "#FFFFFF",
        resolucao: tuple = (1920, 1080),
    ) -> dict:
        """
        Gera animação de entrada do logo/nome do canal.
        Efeito: fade-in com escala gradual + brilho (glow) via FFmpeg.
        Custo R$0,00.
        """
        w, h = resolucao
        # Converter cor hex para formato FFmpeg (0xRRGGBB)
        cor_hex = cor_primaria.lstrip("#")
        cor_ffmpeg = f"0x{cor_hex.upper()}"
        fs = max(80, w // 14)
        fonte = self._fonte("titulo")

        # Fundo escuro com gradiente radial simulado via vignette
        # Texto com alpha crescente + escala via zoompan no fundo
        fade_in = min(1.2, duracao * 0.4)
        fade_out = min(0.5, duracao * 0.15)

        # Camada 1: sombra/glow (texto ligeiramente maior, desfocado, cor accent)
        # Camada 2: texto principal com fade-in
        filtros = [
            # Texto principal com fade-in e leve escala via zoom no background
            f"drawtext={fonte}text='{self._esc(canal_nome.upper())}':"
            f"fontcolor={cor_ffmpeg}:fontsize={fs}:"
            f"shadowcolor=white:shadowx=0:shadowy=0:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"alpha='if(lt(t,{fade_in}),pow(t/{fade_in},2),"
            f"if(gt(t,{duracao-fade_out}),({duracao}-t)/{fade_out},1))'",
            # Sublinha accent que cresce da esquerda para direita
            f"drawbox=x='(w-iw*0.4)/2':y='(h/2)+{int(fs*0.7)}':"
            f"w='iw*0.4*min(t/{fade_in},1)':h=4:"
            f"color={cor_ffmpeg}:t=fill",
            # Fade-in do vídeo inteiro
            f"fade=in:st=0:d={fade_in*0.5}",
            f"fade=out:st={duracao-fade_out}:d={fade_out}",
        ]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x080808:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            "-t", str(duracao),
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            res = self._resultado(output_path, "ok", f"Animação de logo '{canal_nome}' gerada")
            res.update({"output": output_path, "duracao": duracao})
            return res
        return self._resultado(None, "erro", r.stderr.decode()[:300])

    # ── Infográfico em vídeo ──────────────────────────────────────────────────

    def infografico_video(
        self,
        dados: list,          # [{"label": str, "valor": float, "cor": str}, ...]
        titulo: str,
        output_path: str,
        duracao: float = 8.0,
        resolucao: tuple = (1920, 1080),
    ) -> dict:
        """
        Gera vídeo de infográfico com barras animadas crescendo progressivamente.
        Cada barra cresce ao longo do tempo via expressões FFmpeg — custo R$0,00.
        """
        if not dados:
            return self._resultado(None, "erro", "Lista de dados vazia")

        w, h = resolucao
        fonte_tit = self._fonte("titulo")
        fonte_sub = self._fonte("corpo")
        n = len(dados)
        max_val = max(d["valor"] for d in dados)
        anim_dur = duracao * 0.6   # barras crescem nos primeiros 60% do tempo
        bar_max_h = int(h * 0.55)
        bar_w = min(160, (w - 200) // n)
        bar_gap = (w - 200) // n
        margin_left = 100
        base_y = int(h * 0.80)
        fs_tit = max(40, w // 30)
        fs_label = max(22, w // 60)
        fs_val = max(26, w // 50)

        filtros = []
        # Título
        if titulo:
            filtros.append(
                f"drawtext={fonte_tit}text='{self._esc(titulo)}':"
                f"fontcolor=0xFFFFFF:fontsize={fs_tit}:"
                f"x=(w-text_w)/2:y={int(h*0.07)}:"
                f"alpha='if(lt(t,0.5),t/0.5,1)'"
            )

        # Barras animadas: cada uma aparece com 0.3s de delay entre si
        for i, item in enumerate(dados):
            delay = (i / n) * anim_dur * 0.4
            bar_frac = item["valor"] / max_val
            bar_h_final = int(bar_frac * bar_max_h)
            x = margin_left + i * bar_gap + (bar_gap - bar_w) // 2
            # Cor da barra: usa a cor do item se fornecida, senão accent azul
            cor_raw = item.get("cor", "#3B82F6").lstrip("#")
            cor_box = f"0x{cor_raw.upper()}"

            # Barra cresce de baixo para cima
            filtros.append(
                f"drawbox="
                f"x={x}:"
                f"y='max({base_y-bar_h_final},{base_y}-{bar_h_final}*"
                f"max(0,min(1,(t-{delay:.2f})/{anim_dur:.2f})))':"
                f"w={bar_w}:"
                f"h='{bar_h_final}*max(0,min(1,(t-{delay:.2f})/{anim_dur:.2f}))':"
                f"color={cor_box}@0.9:t=fill"
            )
            # Label abaixo da barra
            label_text = self._esc(str(item["label"])[:12])
            filtros.append(
                f"drawtext={fonte_sub}text='{label_text}':"
                f"fontcolor=0xCCCCCC:fontsize={fs_label}:"
                f"x={x + bar_w//2 - len(item['label'])*fs_label//4}:y={base_y+12}:"
                f"enable='gte(t,{delay:.2f})'"
            )
            # Valor acima da barra (aparece quando barra está quase cheia)
            val_text = self._esc(str(item["valor"]))
            filtros.append(
                f"drawtext={fonte_sub}text='{val_text}%':"
                f"fontcolor=0xFFFFFF:fontsize={fs_val}:"
                f"x={x + bar_w//2 - fs_val}:y={base_y-bar_h_final-fs_val-8}:"
                f"enable='gte(t,{delay+anim_dur*0.5:.2f})'"
            )

        # Linha de base
        filtros.append(
            f"drawbox=x={margin_left}:y={base_y}:w={w-200}:h=2:color=0x555555:t=fill"
        )
        # Fade final
        filtros.append(f"fade=out:st={duracao-0.5}:d=0.5")

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x0A0A0A:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
            "-t", str(duracao),
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode == 0:
            res = self._resultado(output_path, "ok", f"Infográfico vídeo com {n} barras gerado")
            res.update({"output": output_path, "duracao": duracao})
            return res
        return self._resultado(None, "erro", r.stderr.decode()[:300])

    # ── Contador de estatísticas ──────────────────────────────────────────────

    def contador_estatisticas(
        self,
        numero: float,
        label: str,
        output_path: str,
        duracao: float = 3.0,
        cor: str = "#FFFFFF",
        resolucao: tuple = (1920, 1080),
    ) -> dict:
        """
        Anima contagem de 0 até `numero` com efeito de odômetro.
        Usa FFmpeg drawtext com expressão de tempo — custo R$0,00.
        """
        w, h = resolucao
        fonte_num = self._fonte("titulo")
        fonte_lbl = self._fonte("corpo")
        cor_hex = cor.lstrip("#")
        cor_ffmpeg = f"0x{cor_hex.upper()}"
        fs_num = max(160, w // 8)
        fs_lbl = max(50, w // 28)
        accel_dur = duracao * 0.8  # aceleração nos primeiros 80%

        # Número inteiro ou decimal
        is_int = isinstance(numero, int) or numero == int(numero)
        num_fmt = "%d" if is_int else "%.1f"
        numero_int = int(numero) if is_int else numero

        # Expressão: odômetro com easing (ease-out: t/dur ao quadrado invertido)
        # eif = evaluate integer format; min(t, dur)/dur controla o progresso
        prog_expr = f"min(t,{accel_dur})/{accel_dur}"
        # Ease-out quadrático: prog = 1 - (1-t)^2
        eased = f"(2*{prog_expr})-({prog_expr}*{prog_expr})"

        if is_int:
            num_expr = f"%{{eif\\:round({eased}*{numero_int})\\:d}}"
        else:
            # Para decimal usamos inteiro e dividimos mentalmente (limitação FFmpeg)
            num_expr = f"%{{eif\\:round({eased}*{numero_int})\\:d}}"

        # Gradiente de fundo (simulado com dois drawbox sobrepostos)
        grad_mid = int(h * 0.55)
        filtros = [
            # Fundo degradê: parte superior mais escura
            f"drawbox=x=0:y=0:w={w}:h={grad_mid}:color=0x050505:t=fill",
            f"drawbox=x=0:y={grad_mid}:w={w}:h={h-grad_mid}:color=0x0F0F0F:t=fill",
            # Número principal (odômetro)
            f"drawtext={fonte_num}text='{num_expr}':"
            f"fontcolor={cor_ffmpeg}:fontsize={fs_num}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-{fs_lbl//2}:"
            f"shadowcolor=black:shadowx=3:shadowy=3",
            # Label abaixo do número
            f"drawtext={fonte_lbl}text='{self._esc(label)}':"
            f"fontcolor=0xAAAAAA:fontsize={fs_lbl}:"
            f"x=(w-text_w)/2:y=(h+{fs_num}//2)/2+20:"
            f"alpha='if(lt(t,0.3),t/0.3,1)'",
            # Linha accent embaixo do número
            f"drawbox=x=(w-{w//4})/2:y={int(h*0.72)}:w={w//4}:h=3:"
            f"color={cor_ffmpeg}@0.6:t=fill:"
            f"enable='gte(t,{accel_dur*0.3:.2f})'",
            # Fade in e fade out
            f"fade=in:st=0:d=0.3",
            f"fade=out:st={duracao-0.4}:d=0.4",
        ]

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=0x080808:size={w}x{h}:rate=30:duration={duracao}",
            "-vf", ",".join(filtros),
            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
            "-t", str(duracao),
            output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode == 0:
            res = self._resultado(output_path, "ok", f"Contador '{label}': 0→{numero} em {duracao}s")
            res.update({"output": output_path, "duracao": duracao})
            return res
        return self._resultado(None, "erro", r.stderr.decode()[:300])

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
                "infografico_barras", "contagem_regressiva",
                "animacao_logo", "infografico_video", "contador_estatisticas",
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
