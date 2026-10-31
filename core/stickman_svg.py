"""
DARK STICKMAN STUDIO — Gerador SVG de Stickman
Cria poses vetoriais parametrizadas para animação frame a frame.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import math
import random
from pathlib import Path
from typing import Tuple, Optional

# ── Paleta de cores padrão (customizável por canal) ──────────────
DEFAULT_COLOR   = "#1a1a2e"
DEFAULT_ACCENT  = "#3B82F6"
STROKE_WIDTH    = 3

# ── Dimensões do canvas SVG ───────────────────────────────────────
SVG_W = 200
SVG_H = 300

# ── Proporções corporais (relativas à altura total) ───────────────
HEAD_R    = 20    # raio da cabeça
NECK_LEN  = 12
TORSO_LEN = 70
ARM_LEN   = 55
LEG_LEN   = 75
LIMB_W    = STROKE_WIDTH


def _svg_header(w: int = SVG_W, h: int = SVG_H) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
    )


def _svg_footer() -> str:
    return "</svg>"


def _circle(cx: float, cy: float, r: float, fill: str, stroke: str) -> str:
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{STROKE_WIDTH}"/>\n'
    )


def _line(x1: float, y1: float, x2: float, y2: float, color: str, width: int = STROKE_WIDTH) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>\n'
    )


def _offset(cx: float, cy: float, angle_deg: float, length: float) -> Tuple[float, float]:
    """Calcula ponto final dado origem, ângulo (graus) e comprimento."""
    rad = math.radians(angle_deg)
    return cx + math.sin(rad) * length, cy + math.cos(rad) * length


# ─────────────────────────────────────────────────────────────────
#  POSES DISPONÍVEIS
# ─────────────────────────────────────────────────────────────────

POSES = {
    "parado":            "neutral",
    "correndo":          "running",
    "lutando":           "fighting",
    "vitoria":           "victory",
    "queda":             "falling",
    "olhando_camera":    "looking_camera",
    "pensando":          "thinking",
    "surpreso":          "surprised",
    "apontando":         "pointing",
    "sentado":           "sitting",
    "voando":            "flying",
    "agachado":          "crouching",
    "empurrando":        "pushing",
    "levantando_braco":  "raising_arm",
    "dormindo":          "sleeping",
    "celebrando":        "celebrating",
    "chutando":          "kicking",
    "saltando":          "jumping",
    "deitado":           "lying",
    "questionando":      "questioning",
}


def render_pose(
    pose: str = "parado",
    color: str = DEFAULT_COLOR,
    accent: str = DEFAULT_ACCENT,
    seed: Optional[int] = None,
) -> str:
    """
    Renderiza um stickman em SVG na pose indicada.

    Args:
        pose: Nome da pose (ver POSES).
        color: Cor principal do stickman (stroke/fill).
        accent: Cor de destaque para detalhes.
        seed: Semente para pequenas variações aleatórias.

    Returns:
        String SVG completa.
    """
    if seed is not None:
        random.seed(seed)

    fn = _POSE_FNS.get(pose, _pose_neutral)
    body = fn(color, accent)
    return _svg_header() + body + _svg_footer()


# ── Implementações de pose ────────────────────────────────────────

def _head_torso(color: str, cx: float = 100, head_y: float = 35) -> str:
    """Cabeça + pescoço + torso base."""
    neck_y  = head_y + HEAD_R
    torso_y = neck_y + NECK_LEN + TORSO_LEN
    svg  = _circle(cx, head_y, HEAD_R, "white", color)
    svg += _line(cx, neck_y, cx, neck_y + NECK_LEN, color)
    svg += _line(cx, neck_y + NECK_LEN, cx, torso_y, color, LIMB_W)
    return svg, neck_y + NECK_LEN, torso_y


def _pose_neutral(color: str, accent: str) -> str:
    svg, shoulder_y, hip_y = _head_torso(color)[0], 47, 117
    svg = _circle(100, 35, HEAD_R, "white", color)
    svg += _line(100, 55, 100, 120, color)
    # braços para baixo
    svg += _line(100, 70, 60, 100, color)
    svg += _line(100, 70, 140, 100, color)
    # pernas abertas
    svg += _line(100, 120, 75, 200, color)
    svg += _line(100, 120, 125, 200, color)
    return svg


def _pose_running(color: str, accent: str) -> str:
    svg = _circle(110, 35, HEAD_R, "white", color)
    svg += _line(110, 55, 100, 120, color)
    # braço esquerdo para frente, direito para trás
    svg += _line(100, 75, 60, 55, color)
    svg += _line(100, 75, 145, 95, color)
    # perna esquerda para frente, direita para trás
    svg += _line(100, 120, 70, 185, color)
    svg += _line(100, 120, 130, 175, color)
    # pé esquerdo
    svg += _line(70, 185, 45, 200, color)
    svg += _line(130, 175, 145, 195, color)
    return svg


def _pose_fighting(color: str, accent: str) -> str:
    svg = _circle(95, 40, HEAD_R, "white", color)
    svg += _line(95, 60, 90, 125, color)
    # soco à frente
    svg += _line(90, 80, 135, 65, color)
    svg += _line(90, 80, 55, 100, color)
    # pernas em posição de luta
    svg += _line(90, 125, 60, 200, color)
    svg += _line(90, 125, 120, 200, color)
    # destaque de impacto
    svg += f'<circle cx="150" cy="60" r="8" fill="{accent}" opacity="0.7"/>\n'
    return svg


def _pose_victory(color: str, accent: str) -> str:
    svg = _circle(100, 30, HEAD_R, "white", color)
    svg += _line(100, 50, 100, 120, color)
    # braços levantados em V
    svg += _line(100, 70, 55, 30, color)
    svg += _line(100, 70, 145, 30, color)
    # pernas abertas
    svg += _line(100, 120, 75, 205, color)
    svg += _line(100, 120, 125, 205, color)
    # estrelas de vitória
    svg += f'<text x="30" y="35" font-size="18" fill="{accent}">★</text>\n'
    svg += f'<text x="150" y="35" font-size="18" fill="{accent}">★</text>\n'
    return svg


def _pose_falling(color: str, accent: str) -> str:
    # stickman inclinado (caindo)
    svg = _circle(130, 80, HEAD_R, "white", color)
    svg += _line(130, 100, 85, 140, color)
    svg += _line(110, 115, 155, 100, color)
    svg += _line(110, 115, 80, 170, color)
    svg += _line(85, 140, 55, 190, color)
    svg += _line(85, 140, 115, 185, color)
    # linhas de movimento
    for i in range(3):
        y = 60 + i * 20
        svg += f'<line x1="40" y1="{y}" x2="60" y2="{y+5}" stroke="{accent}" stroke-width="2" opacity="0.5"/>\n'
    return svg


def _pose_looking_camera(color: str, accent: str) -> str:
    svg = _circle(100, 35, HEAD_R, "white", color)
    # olhos direcionados para a câmera (pontos)
    svg += f'<circle cx="93" cy="33" r="3" fill="{color}"/>\n'
    svg += f'<circle cx="107" cy="33" r="3" fill="{color}"/>\n'
    svg += _line(100, 55, 100, 120, color)
    svg += _line(100, 70, 60, 90, color)
    svg += _line(100, 70, 140, 90, color)
    svg += _line(100, 120, 80, 205, color)
    svg += _line(100, 120, 120, 205, color)
    return svg


def _pose_thinking(color: str, accent: str) -> str:
    svg = _circle(100, 35, HEAD_R, "white", color)
    svg += _line(100, 55, 100, 120, color)
    # mão no queixo
    svg += _line(100, 70, 130, 55, color)
    svg += _line(130, 55, 120, 40, color)
    svg += _line(100, 70, 65, 95, color)
    svg += _line(100, 120, 80, 205, color)
    svg += _line(100, 120, 120, 205, color)
    # balão de pensamento
    svg += f'<circle cx="145" cy="20" r="5" fill="{accent}" opacity="0.6"/>\n'
    svg += f'<circle cx="158" cy="12" r="7" fill="{accent}" opacity="0.6"/>\n'
    svg += f'<circle cx="173" cy="8" r="10" fill="{accent}" opacity="0.6"/>\n'
    svg += f'<text x="165" y="13" font-size="10" fill="white" text-anchor="middle">?</text>\n'
    return svg


def _pose_surprised(color: str, accent: str) -> str:
    svg = _circle(100, 35, HEAD_R, "white", color)
    # boca aberta (O)
    svg += f'<circle cx="100" cy="40" r="5" fill="{color}"/>\n'
    # braços para o alto em susto
    svg += _line(100, 55, 100, 120, color)
    svg += _line(100, 70, 55, 40, color)
    svg += _line(100, 70, 145, 40, color)
    svg += _line(100, 120, 80, 205, color)
    svg += _line(100, 120, 120, 205, color)
    # linhas de susto
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        x1 = 100 + 25 * math.sin(rad)
        y1 = 35 + 25 * math.cos(rad)
        x2 = 100 + 35 * math.sin(rad)
        y2 = 35 + 35 * math.cos(rad)
        svg += f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{accent}" stroke-width="2"/>\n'
    return svg


def _pose_pointing(color: str, accent: str) -> str:
    svg = _circle(100, 35, HEAD_R, "white", color)
    svg += _line(100, 55, 100, 120, color)
    # braço apontando para frente
    svg += _line(100, 70, 155, 65, color)
    svg += f'<circle cx="158" cy="64" r="4" fill="{accent}"/>\n'
    svg += _line(100, 70, 60, 90, color)
    svg += _line(100, 120, 80, 205, color)
    svg += _line(100, 120, 120, 205, color)
    return svg


def _pose_jumping(color: str, accent: str) -> str:
    svg = _circle(100, 20, HEAD_R, "white", color)
    svg += _line(100, 40, 100, 105, color)
    svg += _line(100, 60, 55, 45, color)
    svg += _line(100, 60, 145, 45, color)
    # pernas dobradas no ar
    svg += _line(100, 105, 70, 155, color)
    svg += _line(70, 155, 85, 185, color)
    svg += _line(100, 105, 130, 155, color)
    svg += _line(130, 155, 115, 185, color)
    # sombra no chão
    svg += f'<ellipse cx="100" cy="250" rx="30" ry="6" fill="{color}" opacity="0.2"/>\n'
    return svg


def _pose_sitting(color: str, accent: str) -> str:
    svg = _circle(100, 35, HEAD_R, "white", color)
    svg += _line(100, 55, 100, 120, color)
    svg += _line(100, 70, 60, 90, color)
    svg += _line(100, 70, 140, 90, color)
    # pernas dobradas sentado
    svg += _line(100, 120, 60, 145, color)
    svg += _line(60, 145, 40, 145, color)
    svg += _line(100, 120, 140, 145, color)
    svg += _line(140, 145, 160, 145, color)
    # chão/cadeira
    svg += f'<line x1="25" y1="150" x2="175" y2="150" stroke="{accent}" stroke-width="3" opacity="0.4"/>\n'
    return svg


def _pose_generic(color: str, accent: str) -> str:
    return _pose_neutral(color, accent)


# ── Mapeamento pose_name → função ────────────────────────────────
_POSE_FNS = {
    "parado":           _pose_neutral,
    "correndo":         _pose_running,
    "lutando":          _pose_fighting,
    "vitoria":          _pose_victory,
    "queda":            _pose_falling,
    "olhando_camera":   _pose_looking_camera,
    "pensando":         _pose_thinking,
    "surpreso":         _pose_surprised,
    "apontando":        _pose_pointing,
    "saltando":         _pose_jumping,
    "sentado":          _pose_sitting,
    "voando":           _pose_jumping,     # alias
    "celebrando":       _pose_victory,     # alias
    "questionando":     _pose_thinking,    # alias
    "levantando_braco": _pose_pointing,    # alias
}


# ─────────────────────────────────────────────────────────────────
#  UTILITÁRIOS DE ARQUIVO
# ─────────────────────────────────────────────────────────────────

def save_pose(
    pose: str,
    path: Path,
    color: str = DEFAULT_COLOR,
    accent: str = DEFAULT_ACCENT,
    seed: int = 0,
) -> Path:
    """Salva SVG da pose em disco."""
    svg = render_pose(pose, color, accent, seed)
    path = Path(path)
    path.write_text(svg, encoding="utf-8")
    return path


def save_all_poses(out_dir: Path, color: str = DEFAULT_COLOR, accent: str = DEFAULT_ACCENT) -> list:
    """Salva todas as poses em out_dir/."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for pose_name in POSES:
        p = out_dir / f"stickman_{pose_name}.svg"
        save_pose(pose_name, p, color, accent)
        saved.append(p)
    return saved


if __name__ == "__main__":
    import sys
    pose = sys.argv[1] if len(sys.argv) > 1 else "parado"
    svg  = render_pose(pose, accent="#F59E0B")
    print(svg)
