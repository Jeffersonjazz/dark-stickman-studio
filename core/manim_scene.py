"""
DARK STICKMAN STUDIO — Cenas Manim CE com Stickman Animado
Gera clipes MP4 de animação stickman usando Manim Community Edition.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import subprocess
import shutil
import tempfile
import json
from pathlib import Path
from typing import Optional

MANIM_BIN = shutil.which("manim") or "manim"


def check_manim() -> bool:
    """Verifica se Manim CE está instalado."""
    try:
        result = subprocess.run([MANIM_BIN, "--version"], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def render_stickman_scene(
    cena: dict,
    output_dir: Path,
    canal_config: dict,
    fps: int = 30,
    quality: str = "medium_quality",
) -> Optional[Path]:
    """
    Renderiza uma cena stickman com Manim CE.

    Args:
        cena: Dict com campos: num, tipo, duracao_s, stickman_acao, narracao, fundo
        output_dir: Diretório de saída para os clipes MP4.
        canal_config: Config do canal com cor, seed, etc.
        fps: Frames por segundo.
        quality: 'low_quality', 'medium_quality', 'high_quality', 'production_quality'.

    Returns:
        Path do arquivo MP4 gerado, ou None se falhar.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Gera o script Python da cena Manim
    scene_script = _build_manim_script(cena, canal_config)

    # Salva em arquivo temporário
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, prefix="manim_cena_") as f:
        f.write(scene_script)
        script_path = Path(f.name)

    try:
        quality_flag = {
            "low_quality": "-ql",
            "medium_quality": "-qm",
            "high_quality": "-qh",
            "production_quality": "-qp",
        }.get(quality, "-qm")

        cmd = [
            MANIM_BIN,
            quality_flag,
            "--fps", str(fps),
            "--output_file", f"cena_{cena.get('num', 0):02d}.mp4",
            "--media_dir", str(output_dir),
            str(script_path),
            "StickmanScene",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=300)

        if result.returncode != 0:
            print(f"[MANIM] Erro na cena {cena.get('num')}: {result.stderr[-500:]}")
            return None

        # Localiza o arquivo MP4 gerado
        mp4_candidates = list(output_dir.rglob(f"cena_{cena.get('num', 0):02d}.mp4"))
        if mp4_candidates:
            return mp4_candidates[0]

        # Tenta encontrar qualquer MP4 recém-gerado
        all_mp4 = sorted(output_dir.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        return all_mp4[0] if all_mp4 else None

    except subprocess.TimeoutExpired:
        print(f"[MANIM] Timeout na cena {cena.get('num')} (>300s)")
        return None
    except Exception as e:
        print(f"[MANIM] Exceção na cena {cena.get('num')}: {e}")
        return None
    finally:
        script_path.unlink(missing_ok=True)


def _build_manim_script(cena: dict, canal_config: dict) -> str:
    """
    Gera o código Python Manim para uma cena stickman.
    Código limpo e original — sem cópia de terceiros.
    """
    cor = canal_config.get("stickman_color", "#3B82F6")
    fundo_tipo = cena.get("fundo", "branco_minimalista")
    acao = cena.get("stickman_acao", "parado")
    duracao = cena.get("duracao_s", 5)
    num_cena = cena.get("num", 1)
    tipo = cena.get("tipo", "normal")
    narracao = cena.get("narracao", "")

    # Cor de fundo por tipo de fundo
    bg_color_map = {
        "branco_minimalista": "#FFFFFF",
        "preto_elegante": "#0D0D0D",
        "azul_escuro": "#0F172A",
        "cinza_neutro": "#F1F5F9",
        "gradient_dark": "#1a1a2e",
        "historico": "#2D1B0E",
        "natureza": "#0F2B0F",
        "tecnologia": "#060B18",
        "suspense": "#1a0a2e",
    }
    bg_hex = bg_color_map.get(fundo_tipo, "#1a1a2e")

    # Texto a exibir na cena (primeiras palavras da narração)
    palavras = narracao.split()[:8] if narracao else []
    texto_cena = " ".join(palavras) + ("..." if len(palavras) >= 8 else "")

    script = f'''#!/usr/bin/env python3
"""
DARK STICKMAN STUDIO — Cena {num_cena} ({tipo})
Gerado automaticamente — DARK CREATIVE LAB
ai_generated: True
"""
from manim import *

config.background_color = ManimColor("{bg_hex}")


class StickmanScene(Scene):
    """Cena {num_cena}: {tipo} — duração {duracao}s"""

    # Configurações do canal (consistência visual)
    STICKMAN_COLOR = ManimColor("{cor}")
    STROKE_W = 4
    DURACAO = {duracao}

    def construct(self):
        # ── Grupos de elementos ──
        corpo = self._criar_stickman(acao="{acao}")
        self.add(corpo)

        # Título/legenda da cena
        if {repr(bool(texto_cena))}:
            legenda = self._criar_legenda({repr(texto_cena)})
            self.play(FadeIn(legenda), run_time=0.5)

        # Animação principal baseada na ação
        self._animar("{acao}", corpo)

        # Fade out no final
        self.play(FadeOut(corpo), run_time=0.5)

    def _criar_stickman(self, acao: str = "parado") -> VGroup:
        """Cria stickman vetorial em Manim."""
        c = self.STICKMAN_COLOR
        w = self.STROKE_W
        g = VGroup()

        # Cabeça
        cabeca = Circle(radius=0.3, color=c, fill_color=WHITE, fill_opacity=1, stroke_width=w)
        cabeca.move_to(UP * 2.5)
        g.add(cabeca)

        # Pescoço
        pescoco = Line(UP * 2.2, UP * 2.0, color=c, stroke_width=w)
        g.add(pescoco)

        # Torso
        torso = Line(UP * 2.0, UP * 0.5, color=c, stroke_width=w)
        g.add(torso)

        # Braços e pernas variam por ação
        if acao in ("correndo", "running"):
            b_esq = Line(UP * 1.5, UP * 0.8 + LEFT * 0.8, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 1.3 + RIGHT * 0.9, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, DOWN * 0.5 + LEFT * 0.5, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, UP * 0.1 + RIGHT * 0.7, color=c, stroke_width=w)
        elif acao in ("lutando", "fighting"):
            b_esq = Line(UP * 1.5, UP * 1.0 + LEFT * 0.5, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 1.8 + RIGHT * 1.0, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, DOWN * 0.8 + LEFT * 0.4, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, DOWN * 0.7 + RIGHT * 0.6, color=c, stroke_width=w)
            impacto = Circle(radius=0.2, color=ManimColor("{canal_config.get("stickman_color", "#F59E0B")}"), fill_opacity=0.7)
            impacto.move_to(UP * 1.8 + RIGHT * 1.2)
            g.add(impacto)
        elif acao in ("vitoria", "victory", "celebrando"):
            b_esq = Line(UP * 1.5, UP * 2.3 + LEFT * 0.7, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 2.3 + RIGHT * 0.7, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, DOWN * 0.8 + LEFT * 0.4, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, DOWN * 0.8 + RIGHT * 0.4, color=c, stroke_width=w)
        elif acao in ("saltando", "jumping", "voando"):
            b_esq = Line(UP * 1.5, UP * 2.2 + LEFT * 0.6, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 2.2 + RIGHT * 0.6, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, UP * 0.0 + LEFT * 0.6, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, UP * 0.0 + RIGHT * 0.6, color=c, stroke_width=w)
        elif acao in ("apontando", "pointing"):
            b_esq = Line(UP * 1.5, UP * 1.2 + LEFT * 0.5, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 1.5 + RIGHT * 1.2, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, DOWN * 0.8 + LEFT * 0.4, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, DOWN * 0.8 + RIGHT * 0.4, color=c, stroke_width=w)
        else:  # parado / olhando_camera / default
            b_esq = Line(UP * 1.5, UP * 0.8 + LEFT * 0.6, color=c, stroke_width=w)
            b_dir = Line(UP * 1.5, UP * 0.8 + RIGHT * 0.6, color=c, stroke_width=w)
            p_esq = Line(UP * 0.5, DOWN * 0.8 + LEFT * 0.35, color=c, stroke_width=w)
            p_dir = Line(UP * 0.5, DOWN * 0.8 + RIGHT * 0.35, color=c, stroke_width=w)

        g.add(b_esq, b_dir, p_esq, p_dir)
        return g

    def _criar_legenda(self, texto: str) -> Text:
        """Legenda na parte inferior da cena."""
        t = Text(texto, font_size=24, color=WHITE)
        t.move_to(DOWN * 3.2)
        t.set_max_width(12)
        return t

    def _animar(self, acao: str, corpo: VGroup):
        """Anima o stickman de acordo com a ação."""
        tempo_restante = max(1.0, self.DURACAO - 1.0)

        if acao in ("correndo", "running"):
            # Oscilação lateral simulando corrida
            self.play(
                corpo.animate.shift(RIGHT * 0.3).shift(UP * 0.05),
                run_time=0.3,
            )
            ciclos = int(tempo_restante / 0.6)
            for _ in range(ciclos):
                self.play(corpo.animate.shift(RIGHT * 0.5), run_time=0.3)
                self.play(corpo.animate.shift(LEFT * 0.5), run_time=0.3)

        elif acao in ("lutando", "fighting"):
            self.play(corpo.animate.shift(RIGHT * 0.3), run_time=0.2)
            self.play(corpo.animate.shift(LEFT * 0.6), run_time=0.15)
            self.play(corpo.animate.shift(RIGHT * 0.3), run_time=0.15)
            self.wait(tempo_restante - 0.5)

        elif acao in ("vitoria", "victory", "celebrando"):
            self.play(corpo.animate.shift(UP * 0.2), run_time=0.3)
            self.play(corpo.animate.shift(DOWN * 0.2), run_time=0.3)
            self.play(corpo.animate.shift(UP * 0.2), run_time=0.3)
            self.play(corpo.animate.shift(DOWN * 0.2), run_time=0.3)
            self.wait(max(0, tempo_restante - 1.2))

        elif acao in ("saltando", "jumping", "voando"):
            self.play(corpo.animate.shift(UP * 1.2), run_time=0.4)
            self.play(corpo.animate.shift(DOWN * 1.2), run_time=0.5)
            self.wait(max(0, tempo_restante - 0.9))

        elif acao in ("pensando", "thinking", "questionando"):
            self.play(corpo.animate.rotate(0.05), run_time=0.5)
            self.play(corpo.animate.rotate(-0.05), run_time=0.5)
            self.wait(max(0, tempo_restante - 1.0))

        else:
            # Ação padrão: idle breathing leve
            self.play(corpo.animate.scale(1.02), run_time=0.5)
            self.play(corpo.animate.scale(1/1.02), run_time=0.5)
            self.wait(max(0, tempo_restante - 1.0))
'''
    return script


def render_intro_hook(
    canal_config: dict,
    texto: str,
    output_path: Path,
    fps: int = 30,
) -> Optional[Path]:
    """Renderiza a tela de intro/hook (0-5s) com Manim."""
    output_path = Path(output_path)
    cena = {
        "num": 0,
        "tipo": "hook",
        "duracao_s": 5,
        "stickman_acao": "olhando_camera",
        "narracao": texto,
        "fundo": "preto_elegante",
    }
    return render_stickman_scene(cena, output_path.parent, canal_config, fps)


def render_outro_cta(
    canal_config: dict,
    cta_texto: str,
    output_path: Path,
    fps: int = 30,
) -> Optional[Path]:
    """Renderiza o outro/CTA final."""
    cena = {
        "num": 99,
        "tipo": "outro",
        "duracao_s": 8,
        "stickman_acao": "apontando",
        "narracao": cta_texto,
        "fundo": "preto_elegante",
    }
    return render_stickman_scene(cena, Path(output_path).parent, canal_config, fps)


def render_roteiro(
    cenas: list,
    output_dir: Path,
    canal_config: dict,
    fps: int = 30,
    quality: str = "medium_quality",
) -> list:
    """
    Renderiza todas as cenas de um roteiro com Manim.

    Returns:
        Lista de Paths dos MP4 gerados (None onde falhou).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    clips = []

    for cena in cenas:
        clip = render_stickman_scene(cena, output_dir, canal_config, fps, quality)
        clips.append(clip)
        status = "✓" if clip else "✗"
        print(f"[MANIM] Cena {cena.get('num', '?')} ({cena.get('tipo', '?')}): {status}")

    return clips
