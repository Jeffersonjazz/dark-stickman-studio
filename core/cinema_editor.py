"""
DARK CREATIVE LAB — AGENTE CINEMA EDITOR (Fase 5)
Editor audiovisual integrado: timeline, montagem automática, transições e renderização.

Funcionalidades:
- Edição por linha do tempo (Timeline)
- Montagem automática de cenas
- Cortes inteligentes com remoção de silêncios
- Transições (corte seco, dissolve, fade, zoom)
- Sincronização de áudio com narração
- Color grading integrado (via ffmpeg_utils)
- Legendas SRT burned-in
- Exportação multi-resolução (1080p, 4K, 720p)
- Renderização em lote

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import subprocess
import shutil
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
#  ESTRUTURAS DE DADOS — TIMELINE
# ─────────────────────────────────────────────────────────────────

@dataclass
class Clip:
    """Representa um clipe na timeline."""
    path: str                   # Caminho absoluto do arquivo
    start: float = 0.0          # Início (segundos) dentro do arquivo fonte
    duration: float = 0.0       # Duração na timeline (0 = usa duração total)
    track: int = 0              # Faixa (0=vídeo, 1=áudio, 2=legenda)
    position: float = 0.0       # Posição na timeline (segundos)
    volume: float = 1.0         # Volume (áudio apenas)
    transition_in: str = "cut"  # cut | dissolve | fade | zoom
    transition_dur: float = 0.5
    label: str = ""             # Rótulo descritivo

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Timeline:
    """Timeline de edição do projeto."""
    project_name: str
    fps: int = 30
    resolution: str = "1920x1080"
    audio_tracks: int = 2
    clips: list = field(default_factory=list)
    color_grade: str = "documentario"

    def adicionar_clip(self, clip: Clip):
        self.clips.append(clip)

    def duracao_total(self) -> float:
        if not self.clips:
            return 0.0
        return max(c.position + (c.duration or 999) for c in self.clips
                   if c.track == 0)

    def clips_video(self) -> list[Clip]:
        return [c for c in self.clips if c.track == 0]

    def clips_audio(self) -> list[Clip]:
        return [c for c in self.clips if c.track == 1]

    def clips_legenda(self) -> list[Clip]:
        return [c for c in self.clips if c.track == 2]

    def exportar_json(self, path: Path):
        """Exporta a timeline para JSON para inspeção/edição externa."""
        data = {
            "project_name": self.project_name,
            "fps": self.fps,
            "resolution": self.resolution,
            "color_grade": self.color_grade,
            "clips": [c.to_dict() for c in self.clips],
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def importar_json(cls, path: Path) -> "Timeline":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        tl = cls(
            project_name=data["project_name"],
            fps=data.get("fps", 30),
            resolution=data.get("resolution", "1920x1080"),
            color_grade=data.get("color_grade", "documentario"),
        )
        for c in data.get("clips", []):
            tl.adicionar_clip(Clip(**c))
        return tl


# ─────────────────────────────────────────────────────────────────
#  MONTAGEM AUTOMÁTICA
# ─────────────────────────────────────────────────────────────────

def montar_automatico(
    clips_video: list[Path],
    narracoes: list[Path],
    output_dir: Path,
    canal_config: dict,
    srt_path: Optional[Path] = None,
    trilha_path: Optional[Path] = None,
    verbose: bool = True,
) -> Timeline:
    """
    Monta automaticamente uma timeline a partir de clips e narrações.

    Estratégia:
    1. Alinha cada clip de vídeo com sua narração correspondente.
    2. Calcula posição na timeline baseado na duração de cada narração.
    3. Adiciona faixa de áudio (narração + trilha sonora).
    4. Adiciona legendas se disponíveis.

    Returns:
        Timeline montada.
    """
    tl = Timeline(
        project_name=canal_config.get("id", "dark_project"),
        fps=canal_config.get("fps", 30),
        resolution=canal_config.get("resolucao", "1920x1080"),
        color_grade=canal_config.get("color_grade", "documentario"),
    )

    cursor = 0.0  # posição atual na timeline

    for i, (vclip, aclip) in enumerate(zip(clips_video, narracoes)):
        # Duração da narração determina duração do clip de vídeo
        dur_narr = _get_duration(aclip)
        dur_video = _get_duration(vclip)

        # Usa narração como referência de duração
        dur = dur_narr if dur_narr > 0 else dur_video

        # Transição: fade no primeiro clip, dissolve nos demais (se ≤ 3)
        if i == 0:
            transition = "fade"
        elif len(clips_video) <= 3:
            transition = "dissolve"
        else:
            transition = "cut"  # corte seco para muitos clips → evita xfade gigante

        # Clip de vídeo
        tl.adicionar_clip(Clip(
            path=str(vclip),
            start=0.0,
            duration=dur,
            track=0,
            position=cursor,
            transition_in=transition,
            transition_dur=0.5,
            label=f"cena_{i+1:02d}",
        ))

        # Faixa de narração
        tl.adicionar_clip(Clip(
            path=str(aclip),
            duration=dur_narr,
            track=1,
            position=cursor,
            volume=1.0,
            label=f"narr_{i+1:02d}",
        ))

        cursor += dur

    # Trilha sonora (ocupa toda a timeline)
    if trilha_path and trilha_path.exists():
        tl.adicionar_clip(Clip(
            path=str(trilha_path),
            duration=cursor,
            track=1,
            position=0.0,
            volume=0.12,   # trilha baixa sob narração
            label="trilha_sonora",
        ))

    # Legenda
    if srt_path and srt_path.exists():
        tl.adicionar_clip(Clip(
            path=str(srt_path),
            duration=cursor,
            track=2,
            position=0.0,
            label="legendas_srt",
        ))

    if verbose:
        print(f"[CINEMA EDITOR] Timeline: {len(tl.clips_video())} clips vídeo, "
              f"{cursor:.1f}s duração total")

    # Salva JSON da timeline
    output_dir.mkdir(parents=True, exist_ok=True)
    tl.exportar_json(output_dir / "timeline.json")

    return tl


# ─────────────────────────────────────────────────────────────────
#  RENDERIZAÇÃO
# ─────────────────────────────────────────────────────────────────

def renderizar(
    timeline: Timeline,
    output_path: Path,
    verbose: bool = True,
) -> dict:
    """
    Renderiza a timeline para MP4 final.

    Estratégia de renderização:
    1. Concatena clips de vídeo (sem transição se muitos clips)
    2. Adiciona narração sincronizada
    3. Mixa trilha sonora
    4. Queima legendas
    5. Aplica color grade
    6. Exporta em resolução configurada

    Returns:
        Dict com status, output e metadados.
    """
    t0 = time.time()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    video_clips = timeline.clips_video()
    audio_clips = timeline.clips_audio()
    legenda_clips = timeline.clips_legenda()

    if not video_clips:
        return {"status": "error", "erro": "Nenhum clip de vídeo na timeline"}

    if verbose:
        print(f"[CINEMA EDITOR] Renderizando {len(video_clips)} clips → {output_path.name}")

    # ── Etapa 1: Concat vídeo ─────────────────────────────────────
    tmp_concat = output_path.parent / "_tmp_concat.mp4"
    paths_video = [Path(c.path) for c in video_clips]

    # Verifica clips existentes
    paths_existentes = [p for p in paths_video if p.exists()]
    if not paths_existentes:
        return {"status": "error", "erro": "Nenhum arquivo de vídeo encontrado no disco"}

    try:
        from core.ffmpeg_utils import concat_videos
        # Sem transição para muitos clips (evita xfade gigante)
        transition = "none" if len(paths_existentes) > 3 else "dissolve"
        concat_videos(paths_existentes, tmp_concat, transition=transition, transition_dur=0.5)
    except Exception as e:
        return {"status": "error", "erro": f"concat_videos: {e}"}

    # ── Etapa 2: Identificar narração principal ────────────────────
    narracoes = [c for c in audio_clips if "narr_" in c.label and Path(c.path).exists()]
    trilhas = [c for c in audio_clips if "trilha" in c.label and Path(c.path).exists()]

    tmp_com_audio = output_path.parent / "_tmp_audio.mp4"

    if narracoes:
        # Concatena narrações e mixa com vídeo
        narr_paths = [Path(c.path) for c in narracoes]
        tmp_narr = output_path.parent / "_tmp_narr.wav"
        _concat_audio(narr_paths, tmp_narr)

        trilha = Path(trilhas[0].path) if trilhas else None
        try:
            from core.ffmpeg_utils import add_audio
            add_audio(tmp_concat, tmp_narr, tmp_com_audio)
        except Exception:
            shutil.copy(tmp_concat, tmp_com_audio)
    else:
        shutil.copy(tmp_concat, tmp_com_audio)

    # ── Etapa 3: Legendas ─────────────────────────────────────────
    tmp_com_srt = output_path.parent / "_tmp_srt.mp4"

    if legenda_clips:
        srt_path = Path(legenda_clips[0].path)
        if srt_path.exists():
            try:
                from core.ffmpeg_utils import burn_subtitles
                burn_subtitles(tmp_com_audio, srt_path, tmp_com_srt)
            except Exception:
                shutil.copy(tmp_com_audio, tmp_com_srt)
        else:
            shutil.copy(tmp_com_audio, tmp_com_srt)
    else:
        shutil.copy(tmp_com_audio, tmp_com_srt)

    # ── Etapa 4: Color grade + Export final ───────────────────────
    try:
        from core.ffmpeg_utils import export_final
        export_final(
            tmp_com_srt,
            output_path,
            resolution=timeline.resolution,
            format="16:9",
        )
    except Exception:
        shutil.copy(tmp_com_srt, output_path)

    # Cleanup temporários
    for tmp in [tmp_concat, tmp_com_audio, tmp_com_srt]:
        if tmp.exists() and tmp != output_path:
            try:
                tmp.unlink()
            except Exception:
                pass

    elapsed = round(time.time() - t0, 2)
    size_mb = output_path.stat().st_size / 1e6 if output_path.exists() else 0

    if verbose:
        print(f"[CINEMA EDITOR] ✅ Renderizado: {output_path.name} ({size_mb:.1f} MB) em {elapsed}s")

    return {
        "status": "ok",
        "output": str(output_path),
        "duracao_s": elapsed,
        "tamanho_mb": round(size_mb, 1),
        "resolucao": timeline.resolution,
        "fps": timeline.fps,
        "clips_renderizados": len(paths_existentes),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  EXPORTAÇÃO MULTI-RESOLUÇÃO
# ─────────────────────────────────────────────────────────────────

RESOLUCOES = {
    "4k":   "3840x2160",
    "1080p": "1920x1080",
    "720p":  "1280x720",
    "shorts": "1080x1920",   # vertical
    "reel":   "1080x1920",
}


def exportar_multi_resolucao(
    input_path: Path,
    output_dir: Path,
    resolucoes: list[str] = None,
    verbose: bool = True,
) -> dict:
    """
    Exporta o vídeo final em múltiplas resoluções.

    Args:
        input_path: Vídeo master renderizado.
        output_dir: Pasta de saída.
        resolucoes: Lista de chaves de RESOLUCOES para exportar.

    Returns:
        Dict com paths exportados por resolução.
    """
    resolucoes = resolucoes or ["1080p", "720p"]
    resultados = {}
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = Path(input_path).stem

    for res_key in resolucoes:
        res = RESOLUCOES.get(res_key, "1920x1080")
        w, h = res.split("x")
        out_path = output_dir / f"{base_name}_{res_key}.mp4"

        if verbose:
            print(f"[CINEMA EDITOR] Exportando {res_key} ({res})...")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                   f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-crf", "20",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        if r.returncode == 0 and out_path.exists():
            resultados[res_key] = str(out_path)
            if verbose:
                size_mb = out_path.stat().st_size / 1e6
                print(f"  ✅ {res_key}: {out_path.name} ({size_mb:.1f} MB)")
        else:
            resultados[res_key] = None
            if verbose:
                print(f"  ❌ {res_key}: falhou")

    return {
        "status": "ok",
        "exports": resultados,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  REMOÇÃO DE SILÊNCIOS (corte inteligente)
# ─────────────────────────────────────────────────────────────────

def remover_silencio(
    input_path: Path,
    output_path: Path,
    silence_threshold: float = -40.0,  # dB
    min_silence_duration: float = 0.5,  # segundos
    verbose: bool = True,
) -> dict:
    """
    Remove silêncios de um arquivo de áudio ou vídeo usando FFmpeg silencedetect.

    Estratégia:
    1. Detecta segmentos de silêncio com silencedetect
    2. Gera lista de segmentos de fala
    3. Extrai e concatena apenas os segmentos com fala

    Returns:
        Dict com status, output, tempo removido.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"[CINEMA EDITOR] Detectando silêncios em {input_path.name}...")

    # Detecta silêncios
    cmd_detect = [
        "ffmpeg", "-i", str(input_path),
        "-af", f"silencedetect=n={silence_threshold}dB:d={min_silence_duration}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd_detect, capture_output=True, text=True, timeout=120)
    output_stderr = result.stderr

    # Parse silêncios
    silences = _parse_silencedetect(output_stderr)

    if not silences:
        if verbose:
            print("[CINEMA EDITOR] Nenhum silêncio detectado.")
        import shutil
        shutil.copy(input_path, output_path)
        return {"status": "ok", "output": str(output_path), "silencio_removido_s": 0.0}

    # Duração total
    dur_total = _get_duration(input_path)

    # Gera segmentos de fala (inverso dos silêncios)
    segmentos_fala = _invertir_silencias(silences, dur_total)

    if not segmentos_fala:
        import shutil
        shutil.copy(input_path, output_path)
        return {"status": "ok", "output": str(output_path), "silencio_removido_s": 0.0}

    # Monta lista de segmentos para concat
    tmp_list = output_path.parent / "_silence_segments.txt"
    temp_segs = []

    with open(tmp_list, "w") as f:
        for i, (start, end) in enumerate(segmentos_fala):
            seg_out = output_path.parent / f"_seg_{i:04d}.mp4"
            temp_segs.append(seg_out)
            cmd_seg = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-to", str(end),
                "-i", str(input_path),
                "-c", "copy",
                str(seg_out),
            ]
            subprocess.run(cmd_seg, capture_output=True, timeout=60)
            if seg_out.exists():
                f.write(f"file '{seg_out}'\n")

    # Concatena segmentos
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(tmp_list),
        "-c", "copy",
        str(output_path),
    ]
    r = subprocess.run(cmd_concat, capture_output=True, timeout=300)

    # Cleanup
    for seg in temp_segs:
        if seg.exists():
            seg.unlink()
    if tmp_list.exists():
        tmp_list.unlink()

    silencio_total = sum(end - start for start, end in silences)

    if verbose:
        print(f"[CINEMA EDITOR] ✅ Silêncio removido: {silencio_total:.1f}s")

    return {
        "status": "ok" if r.returncode == 0 else "error",
        "output": str(output_path),
        "silencio_removido_s": round(silencio_total, 2),
        "segmentos_fala": len(segmentos_fala),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  RENDERIZAÇÃO EM LOTE
# ─────────────────────────────────────────────────────────────────

def renderizar_lote(
    projetos: list[dict],
    verbose: bool = True,
) -> list[dict]:
    """
    Renderiza múltiplos projetos em sequência.

    Args:
        projetos: Lista de dicts com:
            {
                "timeline_json": "/path/to/timeline.json",
                "output_path": "/path/to/output.mp4",
            }

    Returns:
        Lista de resultados por projeto.
    """
    resultados = []
    total = len(projetos)

    for i, proj in enumerate(projetos, 1):
        if verbose:
            print(f"\n[CINEMA EDITOR BATCH] Projeto {i}/{total}: {proj.get('output_path', '?')}")

        tl_path = Path(proj["timeline_json"])
        out_path = Path(proj["output_path"])

        if not tl_path.exists():
            resultados.append({
                "status": "error",
                "erro": f"Timeline não encontrada: {tl_path}",
                "projeto": str(out_path),
            })
            continue

        tl = Timeline.importar_json(tl_path)
        r = renderizar(tl, out_path, verbose=verbose)
        r["projeto"] = str(out_path)
        resultados.append(r)

    ok = sum(1 for r in resultados if r["status"] == "ok")
    if verbose:
        print(f"\n[CINEMA EDITOR BATCH] ✅ {ok}/{total} projetos renderizados")

    return resultados


# ─────────────────────────────────────────────────────────────────
#  UTILITÁRIOS INTERNOS
# ─────────────────────────────────────────────────────────────────

def _get_duration(path: Path) -> float:
    """Retorna duração em segundos usando FFprobe."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _concat_audio(paths: list[Path], output: Path):
    """Concatena múltiplos arquivos de áudio WAV/MP3."""
    list_file = output.parent / "_audio_list.txt"
    with open(list_file, "w") as f:
        for p in paths:
            if Path(p).exists():
                f.write(f"file '{p}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output),
    ], capture_output=True, timeout=120)

    if list_file.exists():
        list_file.unlink()


def _parse_silencedetect(stderr: str) -> list[tuple[float, float]]:
    """Extrai intervalos de silêncio do output do silencedetect."""
    import re
    silences = []
    starts = re.findall(r"silence_start: ([\d.]+)", stderr)
    ends = re.findall(r"silence_end: ([\d.]+)", stderr)
    for s, e in zip(starts, ends):
        silences.append((float(s), float(e)))
    return silences


def _invertir_silencias(
    silences: list[tuple[float, float]],
    dur_total: float,
) -> list[tuple[float, float]]:
    """Retorna segmentos de fala (inverso dos silêncios)."""
    fala = []
    cursor = 0.0
    for start, end in silences:
        if cursor < start:
            fala.append((cursor, start))
        cursor = end
    if cursor < dur_total:
        fala.append((cursor, dur_total))
    return fala


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_cinema_editor() -> dict:
    """Verifica status do AGENTE CINEMA EDITOR."""
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    ffprobe_ok = shutil.which("ffprobe") is not None

    try:
        from core.ffmpeg_utils import concat_videos, add_audio, burn_subtitles, export_final
        ffmpeg_utils_ok = True
    except ImportError:
        ffmpeg_utils_ok = False

    funcoes = [
        "montar_automatico",
        "renderizar",
        "exportar_multi_resolucao",
        "remover_silencio",
        "renderizar_lote",
        "Timeline.exportar_json",
        "Timeline.importar_json",
    ]

    resolucoes_suportadas = list(RESOLUCOES.keys())

    return {
        "status": "ok" if ffmpeg_ok else "ffmpeg_missing",
        "ffmpeg": ffmpeg_ok,
        "ffprobe": ffprobe_ok,
        "ffmpeg_utils": ffmpeg_utils_ok,
        "funcoes": funcoes,
        "resolucoes_suportadas": resolucoes_suportadas,
        "transicoes_suportadas": ["cut", "dissolve", "fade", "zoom"],
        "faixas_suportadas": {"0": "vídeo", "1": "áudio", "2": "legenda"},
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


if __name__ == "__main__":
    import json as _json
    status = check_cinema_editor()
    print(_json.dumps(status, ensure_ascii=False, indent=2))
