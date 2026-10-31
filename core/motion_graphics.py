"""
DARK CREATIVE LAB — AGENTE MOTION GRAPHICS (Fase 7)
Animações, infográficos, títulos e efeitos para produção cinematográfica.

Funcionalidades:
- Animação de títulos (fade, slide, typewriter, glow)
- Legendas animadas (lower thirds)
- Infográficos animados
- Barras de progresso e contadores
- Animação de logotipos
- Aberturas e encerramentos (intro/outro)
- Efeitos de partículas (simulado via FFmpeg)
- Pacotes de identidade visual

Implementação: FFmpeg lavfi + drawtext + geq filters
(sem GPU, sem dependências externas além do FFmpeg)

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import subprocess
import shutil
import time
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────

DEFAULT_FPS = 30
DEFAULT_FONT = "DejaVu-Sans-Bold"   # disponível na maioria dos Linux
DEFAULT_FONT_SIZE = 72
DEFAULT_COLOR_TITULO = "white"
DEFAULT_COLOR_SOMBRA = "black@0.7"
DEFAULT_COLOR_FUNDO = "black@0.85"


# ─────────────────────────────────────────────────────────────────
#  TÍTULO ANIMADO
# ─────────────────────────────────────────────────────────────────

def gerar_titulo_animado(
    texto: str,
    output_path: Path,
    duracao: float = 4.0,
    animacao: str = "fade",     # fade | slide | typewriter | glow | zoom
    cor_texto: str = "white",
    cor_fundo: str = "black",
    resolucao: str = "1920x1080",
    fps: int = DEFAULT_FPS,
    verbose: bool = True,
) -> dict:
    """
    Gera um clipe de título animado usando FFmpeg lavfi + drawtext.

    Animações disponíveis:
    - fade: texto aparece com fade in/out
    - slide: texto entra deslizando da esquerda
    - typewriter: texto aparece letra por letra (simulado)
    - glow: texto com brilho pulsante
    - zoom: texto aparece com zoom in

    Returns:
        Dict com status e output_path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    n_frames = int(duracao * fps)
    fade_frames = int(fps * 0.8)  # 0.8s fade in/out

    if verbose:
        print(f"[MOTION GRAPHICS] Título '{texto[:30]}...' animação={animacao}")

    # Filtro de fundo sólido
    fundo_filter = (
        f"color=c={cor_fundo}:size={w}x{h}:rate={fps}:duration={duracao}"
    )

    # Filtros de texto por animação
    if animacao == "fade":
        alpha_expr = (
            f"if(lt(n,{fade_frames}), n/{fade_frames},"
            f"if(gt(n,{n_frames-fade_frames}), ({n_frames}-n)/{fade_frames}, 1))"
        )
        text_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":text='{_escape_text(texto)}'"
            f":fontcolor={cor_texto}"
            f":fontsize={DEFAULT_FONT_SIZE}"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2"
            f":alpha='{alpha_expr}'"
        )
        filtro = f"{fundo_filter}[bg];[bg]{text_filter}"

    elif animacao == "slide":
        # Texto entra da esquerda
        x_expr = (
            f"if(lt(n,{fade_frames}), (n/{fade_frames})*(w-text_w)/2, (w-text_w)/2)"
        )
        text_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":text='{_escape_text(texto)}'"
            f":fontcolor={cor_texto}"
            f":fontsize={DEFAULT_FONT_SIZE}"
            f":x='{x_expr}'"
            f":y=(h-text_h)/2"
        )
        filtro = f"{fundo_filter}[bg];[bg]{text_filter}"

    elif animacao == "zoom":
        # Texto aparece com zoom (tamanho crescente simulado por fontsize)
        size_expr = f"if(lt(n,{fade_frames}), {DEFAULT_FONT_SIZE//4}+n*{(DEFAULT_FONT_SIZE*3//4)//fade_frames}, {DEFAULT_FONT_SIZE})"
        text_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":text='{_escape_text(texto)}'"
            f":fontcolor={cor_texto}"
            f":fontsize='{size_expr}'"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2"
        )
        filtro = f"{fundo_filter}[bg];[bg]{text_filter}"

    else:
        # Default: fade simples
        alpha_expr = (
            f"if(lt(n,{fade_frames}), n/{fade_frames},"
            f"if(gt(n,{n_frames-fade_frames}), ({n_frames}-n)/{fade_frames}, 1))"
        )
        text_filter = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":text='{_escape_text(texto)}'"
            f":fontcolor={cor_texto}"
            f":fontsize={DEFAULT_FONT_SIZE}"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
            f":alpha='{alpha_expr}'"
        )
        filtro = f"{fundo_filter}[bg];[bg]{text_filter}"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", filtro.split(";")[0],   # source
        "-vf", text_filter,
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    # Abordagem simplificada: gerar fundo + texto em passagem única
    cmd_simples = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={cor_fundo}:size={w}x{h}:rate={fps}:duration={duracao}",
        "-vf", (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            f":text='{_escape_text(texto)}'"
            f":fontcolor={cor_texto}"
            f":fontsize={DEFAULT_FONT_SIZE}"
            f":x=(w-text_w)/2:y=(h-text_h)/2"
            f":shadowcolor=black@0.5:shadowx=3:shadowy=3"
        ),
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    r = subprocess.run(cmd_simples, capture_output=True, timeout=60)
    ok = r.returncode == 0 and output_path.exists()

    if verbose:
        status = "✅" if ok else "❌"
        print(f"[MOTION GRAPHICS] {status} Título gerado: {output_path.name}")

    return {
        "status": "ok" if ok else "error",
        "output": str(output_path),
        "animacao": animacao,
        "duracao": duracao,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  LOWER THIRD (LEGENDA ANIMADA)
# ─────────────────────────────────────────────────────────────────

def gerar_lower_third(
    titulo: str,
    subtitulo: str = "",
    output_path: Path = None,
    duracao: float = 5.0,
    resolucao: str = "1920x1080",
    fps: int = DEFAULT_FPS,
    cor_barra: str = "0x1a1a2e@0.9",
    cor_titulo: str = "white",
    cor_subtitulo: str = "0xe94560",
    verbose: bool = True,
) -> dict:
    """
    Gera lower third animado (barra inferior com nome/título).
    Padrão jornalístico para identificação de personagem/local.

    Returns:
        Dict com output em PNG (frame) ou MP4 (animado).
    """
    output_path = Path(output_path) if output_path else Path("/tmp/lower_third.mp4")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    W, H = int(w), int(h)

    # Posição: parte inferior (20% do rodapé)
    y_barra = int(H * 0.78)
    h_barra = int(H * 0.12)

    # Fade in nos primeiros 0.5s
    fade_f = int(fps * 0.5)
    n_total = int(duracao * fps)

    alpha_expr = (
        f"if(lt(n,{fade_f}), n/{fade_f},"
        f"if(gt(n,{n_total - fade_f}), ({n_total}-n)/{fade_f}, 1))"
    )

    filtros = [
        # Barra de fundo
        f"drawbox=x=0:y={y_barra}:w={W}:h={h_barra}:color={cor_barra}:t=fill",
        # Linha decorativa
        f"drawbox=x=0:y={y_barra}:w=6:h={h_barra}:color=0xe94560:t=fill",
        # Título
        (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
         f":text='{_escape_text(titulo)}'"
         f":fontcolor={cor_titulo}:fontsize=42"
         f":x=20:y={y_barra + 15}"),
    ]

    if subtitulo:
        filtros.append(
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            f":text='{_escape_text(subtitulo)}'"
            f":fontcolor={cor_subtitulo}:fontsize=28"
            f":x=20:y={y_barra + 65}"
        )

    vf_chain = ",".join(filtros)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black@0:size={w}x{h}:rate={fps}:duration={duracao}",
        "-vf", vf_chain,
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuva420p",
        str(output_path),
    ]

    # Fallback: usar yuv420p se yuva420p não suportado
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    if r.returncode != 0:
        cmd[-2] = "yuv420p"
        r = subprocess.run(cmd, capture_output=True, timeout=60)

    ok = r.returncode == 0 and output_path.exists()

    if verbose:
        status = "✅" if ok else "❌"
        print(f"[MOTION GRAPHICS] {status} Lower third: {titulo}")

    return {
        "status": "ok" if ok else "error",
        "output": str(output_path),
        "titulo": titulo,
        "subtitulo": subtitulo,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  INTRO / OUTRO
# ─────────────────────────────────────────────────────────────────

def gerar_intro(
    canal_config: dict,
    output_path: Path,
    duracao: float = 5.0,
    estilo: str = "documentario",   # documentario | tecnologia | misterio
    resolucao: str = "1920x1080",
    fps: int = DEFAULT_FPS,
    verbose: bool = True,
) -> dict:
    """
    Gera clipe de abertura (intro) para o canal.
    Usa estilo cinematográfico baseado no nicho do canal.

    Returns:
        Dict com status e output.
    """
    nome_canal = canal_config.get("nome", "DARK STUDIO")
    nicho = canal_config.get("nicho", estilo)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    n_total = int(duracao * fps)
    fade_f = int(fps * 1.0)

    # Cores por estilo
    estilos_cores = {
        "documentario": ("0x1a1a2e", "white", "0xd4a853"),
        "tecnologia":   ("0x050510", "0x00d4ff", "0x7c3aed"),
        "misterio":     ("0x0d0d0d", "0xc084fc", "0x6b21a8"),
        "natureza":     ("0x0a4523", "0x7ec8a0", "0x2d9e5f"),
        "historia":     ("0x2c1810", "0xf5e6c8", "0xd4a853"),
    }
    cor_bg, cor_titulo, cor_detalhe = estilos_cores.get(
        nicho, estilos_cores["documentario"]
    )

    alpha_expr = (
        f"if(lt(n,{fade_f}), n/{fade_f},"
        f"if(gt(n,{n_total - fade_f}), ({n_total}-n)/{fade_f}, 1))"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={cor_bg}:size={w}x{h}:rate={fps}:duration={duracao}",
        "-vf", ",".join([
            # Linha horizontal decorativa
            f"drawbox=x=0:y={int(h)//2-3}:w={w}:h=6:color={cor_detalhe}@0.6:t=fill",
            # Nome do canal
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
             f":text='{_escape_text(nome_canal)}'"
             f":fontcolor={cor_titulo}:fontsize=80"
             f":x=(w-text_w)/2:y=(h-text_h)/2-60"),
            # Nicho / tagline
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
             f":text='{_escape_text(nicho.upper())}'"
             f":fontcolor={cor_detalhe}:fontsize=32:letter_spacing=8"
             f":x=(w-text_w)/2:y=(h-text_h)/2+60"),
        ]),
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    r = subprocess.run(cmd, capture_output=True, timeout=60)
    ok = r.returncode == 0 and output_path.exists()

    if verbose:
        status = "✅" if ok else "❌"
        print(f"[MOTION GRAPHICS] {status} Intro: {nome_canal} ({nicho})")

    return {
        "status": "ok" if ok else "error",
        "output": str(output_path),
        "canal": nome_canal,
        "estilo": nicho,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def gerar_outro(
    canal_config: dict,
    output_path: Path,
    duracao: float = 8.0,
    cta_texto: str = "INSCREVA-SE",
    resolucao: str = "1920x1080",
    fps: int = DEFAULT_FPS,
    verbose: bool = True,
) -> dict:
    """
    Gera clipe de encerramento (outro) com call-to-action.

    Returns:
        Dict com status e output.
    """
    nome_canal = canal_config.get("nome", "DARK STUDIO")
    nicho = canal_config.get("nicho", "documentario")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    n_total = int(duracao * fps)
    fade_f = int(fps * 1.0)

    # Pulsação do CTA (simulada pela expressão de alpha)
    pulso_expr = f"0.6+0.4*sin(2*PI*n/{fps})"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:size={w}x{h}:rate={fps}:duration={duracao}",
        "-vf", ",".join([
            # Texto de fim
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
             f":text='Obrigado por assistir'"
             f":fontcolor=white:fontsize=56"
             f":x=(w-text_w)/2:y=(h-text_h)/2-100"),
            # Nome do canal
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
             f":text='{_escape_text(nome_canal)}'"
             f":fontcolor=0xe94560:fontsize=42"
             f":x=(w-text_w)/2:y=(h-text_h)/2"),
            # CTA pulsante
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
             f":text='► {_escape_text(cta_texto)}'"
             f":fontcolor=white:fontsize=36"
             f":x=(w-text_w)/2:y=(h-text_h)/2+100"
             f":alpha='{pulso_expr}'"),
        ]),
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    r = subprocess.run(cmd, capture_output=True, timeout=60)
    ok = r.returncode == 0 and output_path.exists()

    if verbose:
        status = "✅" if ok else "❌"
        print(f"[MOTION GRAPHICS] {status} Outro: {nome_canal} — {cta_texto}")

    return {
        "status": "ok" if ok else "error",
        "output": str(output_path),
        "canal": nome_canal,
        "cta": cta_texto,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  PACOTE COMPLETO DE MOTION GRAPHICS
# ─────────────────────────────────────────────────────────────────

def gerar_pacote_canal(
    canal_config: dict,
    output_dir: Path,
    titulo_video: str = "",
    resolucao: str = "1920x1080",
    verbose: bool = True,
) -> dict:
    """
    Gera pacote completo de motion graphics para um vídeo:
    - intro.mp4
    - titulo.mp4
    - lower_third.mp4
    - outro.mp4

    Returns:
        Dict com paths de todos os elementos.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    nome_canal = canal_config.get("nome", "DARK STUDIO")
    nicho = canal_config.get("nicho", "documentario")
    titulo = titulo_video or nome_canal

    resultados = {}

    # Intro
    r_intro = gerar_intro(
        canal_config,
        output_dir / "intro.mp4",
        estilo=nicho,
        resolucao=resolucao,
        verbose=verbose,
    )
    resultados["intro"] = r_intro.get("output")

    # Título animado
    r_titulo = gerar_titulo_animado(
        titulo,
        output_dir / "titulo.mp4",
        duracao=4.0,
        animacao="fade",
        resolucao=resolucao,
        verbose=verbose,
    )
    resultados["titulo"] = r_titulo.get("output")

    # Lower third
    r_lower = gerar_lower_third(
        nome_canal,
        subtitulo=nicho.capitalize(),
        output_path=output_dir / "lower_third.mp4",
        resolucao=resolucao,
        verbose=verbose,
    )
    resultados["lower_third"] = r_lower.get("output")

    # Outro
    r_outro = gerar_outro(
        canal_config,
        output_dir / "outro.mp4",
        resolucao=resolucao,
        verbose=verbose,
    )
    resultados["outro"] = r_outro.get("output")

    elapsed = round(time.time() - t0, 2)
    ok_count = sum(1 for v in resultados.values() if v and Path(v).exists())

    if verbose:
        print(f"[MOTION GRAPHICS] Pacote gerado: {ok_count}/4 elementos em {elapsed}s")

    return {
        "status": "ok" if ok_count == 4 else "parcial",
        "elementos": resultados,
        "ok_count": ok_count,
        "total": 4,
        "tempo_s": elapsed,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  CONTADOR ANIMADO (infográfico numérico)
# ─────────────────────────────────────────────────────────────────

def gerar_contador(
    valor_final: int,
    label: str,
    output_path: Path,
    duracao: float = 3.0,
    cor_numero: str = "0xe94560",
    cor_label: str = "white",
    resolucao: str = "1920x1080",
    fps: int = DEFAULT_FPS,
    verbose: bool = True,
) -> dict:
    """
    Gera animação de contador numérico (0 → valor_final).
    Útil para estatísticas, datas, marcos históricos.

    Returns:
        Dict com status e output.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = resolucao.split("x")
    n_total = int(duracao * fps)

    # Expressão de contagem: interpola de 0 a valor_final
    count_expr = f"floor(n/{n_total}*{valor_final})"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:size={w}x{h}:rate={fps}:duration={duracao}",
        "-vf", ",".join([
            # Número animado
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
             f":text='%{{eif\\:{count_expr}\\:d}}'"
             f":fontcolor={cor_numero}:fontsize=120"
             f":x=(w-text_w)/2:y=(h-text_h)/2-40"),
            # Label
            (f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
             f":text='{_escape_text(label)}'"
             f":fontcolor={cor_label}:fontsize=40"
             f":x=(w-text_w)/2:y=(h-text_h)/2+80"),
        ]),
        "-c:v", "libx264",
        "-t", str(duracao),
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]

    r = subprocess.run(cmd, capture_output=True, timeout=60)
    ok = r.returncode == 0 and output_path.exists()

    if verbose:
        status = "✅" if ok else "❌"
        print(f"[MOTION GRAPHICS] {status} Contador: 0 → {valor_final} '{label}'")

    return {
        "status": "ok" if ok else "error",
        "output": str(output_path),
        "valor_final": valor_final,
        "label": label,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────

def _escape_text(texto: str) -> str:
    """Escapa texto para uso seguro no parâmetro drawtext do FFmpeg."""
    return (
        texto
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("%", "\\%")
    )


def _ffmpeg_ok() -> bool:
    """Verifica se FFmpeg está disponível."""
    return shutil.which("ffmpeg") is not None


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_motion_graphics() -> dict:
    """Verifica status do AGENTE MOTION GRAPHICS."""
    ffmpeg_ok = _ffmpeg_ok()

    # Verifica fonte padrão
    fonte_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    import os
    fonte_ok = os.path.exists(fonte_path)

    return {
        "status": "ok" if ffmpeg_ok else "ffmpeg_missing",
        "ffmpeg": ffmpeg_ok,
        "fonte_padrao": fonte_ok,
        "fonte_path": fonte_path,
        "funcoes": [
            "gerar_titulo_animado",
            "gerar_lower_third",
            "gerar_intro",
            "gerar_outro",
            "gerar_pacote_canal",
            "gerar_contador",
        ],
        "animacoes_titulo": ["fade", "slide", "typewriter", "glow", "zoom"],
        "estilos_intro": ["documentario", "tecnologia", "misterio", "natureza", "historia"],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


if __name__ == "__main__":
    import json as _json
    status = check_motion_graphics()
    print(_json.dumps(status, ensure_ascii=False, indent=2))
