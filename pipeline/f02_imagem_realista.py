#!/usr/bin/env python3
"""
DARK CREATIVE LAB — PIPELINE F02: IMAGEM REALISTA
Pipeline de produção de vídeos com imagens estáticas fotorrealistas + Ken Burns.

Baseado no fluxo de produção real do usuário:
  roteiro → prompts visuais → imagens realistas → zoompan Ken Burns
  → narração → color grade → legendas → thumbnail → MP4 final

Fontes de pesquisa da comunidade:
  - n8n Animation Studio: pipeline imagem→vídeo com zoompan antijitter
  - FFmpeg Ken Burns: scale 4K + zoompan + scale final evita pixelação
  - Whisper + piper/edge_tts: transcrição e narração offline-first
  - HuggingFace SDXL / Stable Diffusion: geração de imagens open source

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  MAPEAMENTO NICHO → PRESET
# ─────────────────────────────────────────────────────────────────

NICHO_PARA_PRESET = {
    "psicologia":   "documentario",
    "batalhas":     "historia",
    "tecnologia":   "tecnologia",
    "stem":         "tecnologia",
    "filosofia":    "documentario",
    "historia":     "historia",
    "misterio":     "misterio",
    "educacao":     "documentario",
    "natureza":     "natureza",
    "ciencia":      "tecnologia",
    "financas":     "documentario",
    "saude":        "relaxamento",
    "relaxamento":  "relaxamento",
    "motivacao":    "storytelling_dark",
}

# Resoluções por formato
RESOLUCOES = {
    "horizontal": (1920, 1080),    # 16:9 YouTube padrão
    "vertical":   (1080, 1920),    # 9:16 Shorts
    "quadrado":   (1080, 1080),    # 1:1 Instagram
}

# ─────────────────────────────────────────────────────────────────
#  PASSO 1 — PLANEJAMENTO CINEMATOGRÁFICO
# ─────────────────────────────────────────────────────────────────

def planejar_cenas(roteiro: dict, canal_config: dict) -> dict:
    """
    Enriquece o roteiro com prompts visuais e dados cinematográficos.
    Chama AGENTE CINEMATIC DIRECTOR.
    """
    from core.cinematic_director import criar_plano_cenas
    return criar_plano_cenas(roteiro, canal_config)


# ─────────────────────────────────────────────────────────────────
#  PASSO 2 — GERAÇÃO DE IMAGENS REALISTAS POR CENA
# ─────────────────────────────────────────────────────────────────

def gerar_imagens_cenas(
    roteiro_cinematico: dict,
    output_dir: Path,
    formato: str = "horizontal",
    verbose: bool = True,
    visual_bank=None,   # ProjetoVisualBank opcional
    projeto_id: str = None,
) -> list[dict]:
    """
    Gera uma imagem fotorrealista para cada cena do roteiro.
    Chama AGENTE IMAGE ENGINE com prompt enriquecido pelo CINEMATIC DIRECTOR.
    Integra ProjetoVisualBank para consistência visual entre cenas.

    Returns:
        Lista de dicts com {cena_id, prompt, imagem_path, status}
    """
    from core.image_engine import gerar_imagem

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Mapear formato para preset de resolução do image_engine
    _FORMATO_PARA_RESOLUCAO = {
        "horizontal": "wallpaper_hd",    # 1920x1080
        "vertical":   "shorts",          # 1080x1920
        "quadrado":   "instagram_post",  # 1080x1080
    }
    resolucao_preset = _FORMATO_PARA_RESOLUCAO.get(formato, "wallpaper_hd")

    cenas = roteiro_cinematico.get("cenas", [])
    resultados = []

    for i, cena in enumerate(cenas):
        cena_id = cena.get("id", f"cena_{i+1:02d}")
        prompt = cena.get("prompt_visual", "")

        # Enriquecer prompt com parâmetros cinematográficos
        cinematografia = cena.get("cinematografia", {})
        color_temp = cinematografia.get("color_temp", "warm")
        enquadramento = cinematografia.get("enquadramento", "wide shot")
        grain = cinematografia.get("grain", 0.0)

        # Adicionar qualificadores fotorrealistas ao prompt
        prompt_enriquecido = _enriquecer_prompt_realista(
            prompt, enquadramento, color_temp, grain
        )

        # Injetar contexto de consistência visual do banco do projeto
        if visual_bank and projeto_id:
            try:
                prompt_enriquecido = visual_bank.gerar_prompt_consistente(
                    projeto_id=projeto_id,
                    cena=cena,
                    prompt_base=prompt_enriquecido,
                )
            except Exception:
                pass  # Fallback para prompt sem consistência

        img_path = output_dir / f"{cena_id}_img.png"

        if verbose:
            print(f"  📸 Gerando imagem — Cena {i+1}/{len(cenas)}: {cena_id}")
            print(f"     Prompt: {prompt_enriquecido[:80]}...")

        r = gerar_imagem(
            prompt=prompt_enriquecido,
            output_path=img_path,
            resolucao=resolucao_preset,
            estilo="cinematografico",
        )

        img_ok = r.get("status") == "ok"
        resultado = {
            "cena_id": cena_id,
            "cena_index": i,
            "prompt": prompt_enriquecido,
            "imagem_path": str(img_path) if img_ok else None,
            "status": r.get("status", "error"),
            "backend": r.get("backend", "unknown"),
            "duracao": float(cena.get("duracao", 5.0)),
        }
        resultados.append(resultado)

        # Registrar imagem gerada no banco visual (para continuidade futura)
        if img_ok and visual_bank and projeto_id:
            try:
                visual_bank.registrar_cena_produzida(
                    projeto_id=projeto_id,
                    idx=i,
                    imagem_path=str(img_path),
                    prompt_usado=prompt_enriquecido,
                    duracao_s=float(cena.get("duracao", 5.0)),
                )
                # Na primeira imagem bem-sucedida: extrair e salvar paleta
                if i == 0:
                    from core.visual_consistency import extrair_paleta_imagem
                    paleta = extrair_paleta_imagem(img_path, n_cores=5)
                    if paleta:
                        dados = visual_bank.carregar_projeto(projeto_id)
                        if dados:
                            dados["paleta"] = paleta
                            visual_bank.salvar_projeto(projeto_id, dados)
                            if verbose:
                                print(f"     🎨 Paleta extraída: {paleta}")
            except Exception:
                pass

        if not img_ok:
            print(f"  ⚠️  Imagem falhou para {cena_id}: {r.get('erro', '')}")

    return resultados


def _enriquecer_prompt_realista(
    prompt: str,
    enquadramento: str,
    color_temp: str,
    grain: float,
) -> str:
    """Adiciona qualificadores de fotorrealismo ao prompt."""
    qualificadores = [
        "photorealistic",
        "cinematic photography",
        "ultra detailed",
        "8K resolution",
        "professional lighting",
    ]

    # Temperatura de cor
    if color_temp == "warm":
        qualificadores.append("warm golden hour lighting")
    elif color_temp == "cool":
        qualificadores.append("cool blue hour lighting")
    elif color_temp == "sepia":
        qualificadores.append("vintage sepia tone, aged photograph")
    elif color_temp == "blue":
        qualificadores.append("cool blue neon lighting, tech aesthetic")

    # Grain para efeito de filme
    if grain > 0.03:
        qualificadores.append("film grain, analog photography")
    elif grain > 0.01:
        qualificadores.append("subtle film grain")

    # Enquadramento
    qualificadores.append(enquadramento)

    return f"{prompt}, {', '.join(qualificadores)}"


# ─────────────────────────────────────────────────────────────────
#  PASSO 3 — ANIMAÇÃO KEN BURNS (ZOOMPAN ANTIJITTER)
# ─────────────────────────────────────────────────────────────────

def animar_imagens_ken_burns(
    imagens_cenas: list[dict],
    roteiro_cinematico: dict,
    output_dir: Path,
    verbose: bool = True,
) -> list[dict]:
    """
    Anima cada imagem com efeito Ken Burns (zoompan + pan suave).
    Usa filtro antijitter: scale 4K → zoompan → scale final.
    Chama AGENTE CINEMATIC DIRECTOR para o filtro.

    Returns:
        Lista de dicts com {cena_id, clip_path, duracao, status}
    """
    from core.cinematic_director import gerar_filtro_zoompan_antijitter, CINEMA_PRESETS

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cenas = roteiro_cinematico.get("cenas", [])
    preset_global = roteiro_cinematico.get("cinematografia_global", {}).get("preset", "documentario")
    fps_global = CINEMA_PRESETS.get(preset_global, {}).get("fps", 24)

    clips = []

    for i, item in enumerate(imagens_cenas):
        cena_id = item["cena_id"]
        img_path = item.get("imagem_path")
        duracao = item.get("duracao", 5.0)
        status_img = item.get("status", "error")

        # Pegar preset específico da cena
        cena = cenas[i] if i < len(cenas) else {}
        cinematografia = cena.get("cinematografia", {})
        preset_cena = cinematografia.get("preset", preset_global)
        fps_cena = cinematografia.get("fps", fps_global)

        clip_path = output_dir / f"{cena_id}_clip.mp4"

        if verbose:
            print(f"  🎬 Ken Burns — Cena {i+1}/{len(imagens_cenas)}: {cena_id} ({duracao:.1f}s)")

        if status_img != "ok" or not img_path or not Path(img_path).exists():
            # Gerar clipe de placeholder (tela preta)
            _gerar_clip_placeholder(clip_path, duracao, fps_cena)
            clips.append({
                "cena_id": cena_id,
                "clip_path": str(clip_path),
                "duracao": duracao,
                "status": "placeholder",
                "transicao": cena.get("cinematografia", {}).get("transicao", "dissolve"),
            })
            continue

        # Gerar filtro zoompan antijitter
        filtro_zoom = gerar_filtro_zoompan_antijitter(preset_cena, duracao=duracao, fps=fps_cena)

        ok = _ffmpeg_ken_burns(
            img_path=img_path,
            output_path=clip_path,
            filtro_zoom=filtro_zoom,
            duracao=duracao,
            fps=fps_cena,
        )

        clips.append({
            "cena_id": cena_id,
            "clip_path": str(clip_path) if ok else None,
            "duracao": duracao,
            "status": "ok" if ok else "error",
            "transicao": cinematografia.get("transicao", "dissolve"),
        })

        if not ok:
            print(f"  ⚠️  Ken Burns falhou para {cena_id}, usando placeholder")
            _gerar_clip_placeholder(clip_path, duracao, fps_cena)
            clips[-1]["status"] = "placeholder"
            clips[-1]["clip_path"] = str(clip_path)

    return clips


def _ffmpeg_ken_burns(
    img_path: str,
    output_path: Path,
    filtro_zoom: str,
    duracao: float,
    fps: int = 24,
) -> bool:
    """
    Aplica Ken Burns via FFmpeg com filtro zoompan antijitter.
    Técnica: scale 4K → zoompan → scale final (elimina jitter de borda).
    """
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    n_frames = int(duracao * fps)

    cmd = [
        ffmpeg, "-y",
        "-loop", "1",
        "-i", str(img_path),
        "-vf", filtro_zoom,
        "-t", str(duracao),
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-an",
        str(output_path),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0 and Path(output_path).exists()
    except Exception:
        return False


def _gerar_clip_placeholder(output_path: Path, duracao: float, fps: int = 24):
    """Gera clipe preto como placeholder quando imagem falha."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi",
        "-i", f"color=black:size=1920x1080:rate={fps}",
        "-t", str(duracao),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        str(output_path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
#  PASSO 4 — NARRAÇÃO POR CENA
# ─────────────────────────────────────────────────────────────────

def gerar_narracoes(
    roteiro_cinematico: dict,
    output_dir: Path,
    verbose: bool = True,
) -> list[dict]:
    """
    Gera narração de áudio para cada cena.
    Chama AGENTE AUDIO MASTER (synthesize).
    Cascade: kokoro_local → piper_local → edge_tts → gtts → silêncio.
    """
    from core.audio_master import synthesize

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cenas = roteiro_cinematico.get("cenas", [])
    narracoes = []

    for i, cena in enumerate(cenas):
        cena_id = cena.get("id", f"cena_{i+1:02d}")
        texto = cena.get("narracao", cena.get("texto", ""))
        duracao = float(cena.get("duracao", 5.0))

        narr_path = output_dir / f"{cena_id}_narr.mp3"

        if verbose:
            print(f"  🎙️  Narração — Cena {i+1}/{len(cenas)}: {cena_id}")

        if not texto.strip():
            # Sem texto: silêncio
            narracoes.append({
                "cena_id": cena_id,
                "audio_path": None,
                "duracao": duracao,
                "status": "silencio",
            })
            continue

        r = synthesize(texto, str(narr_path), duracao_esperada=duracao, verbose=False)

        narracoes.append({
            "cena_id": cena_id,
            "audio_path": str(narr_path) if r.get("status") in ("ok", "silencio") else None,
            "duracao_real": r.get("duracao", duracao),
            "status": r.get("status", "error"),
            "backend": r.get("backend", "unknown"),
        })

    return narracoes


# ─────────────────────────────────────────────────────────────────
#  PASSO 5 — MONTAGEM: CLIPS + NARRAÇÃO + COLOR GRADE
# ─────────────────────────────────────────────────────────────────

def montar_video_final(
    clips: list[dict],
    narracoes: list[dict],
    roteiro_cinematico: dict,
    output_path: Path,
    trilha_path: Optional[str] = None,
    srt_path: Optional[str] = None,
    verbose: bool = True,
) -> dict:
    """
    Monta o vídeo final combinando:
    - Clips Ken Burns de cada cena
    - Narração de cada cena
    - Trilha sonora de fundo (opcional)
    - Color grade global
    - Legendas (opcional)

    Usa FFmpeg diretamente para máxima eficiência.
    """
    from core.cinematic_director import gerar_filtro_colorgrade

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    preset_global = roteiro_cinematico.get("cinematografia_global", {}).get("preset", "documentario")
    filtro_colorgrade = gerar_filtro_colorgrade(preset_global)

    if verbose:
        print(f"\n  🎞️  Montando vídeo final...")
        print(f"     Preset: {preset_global}")
        print(f"     Color grade: {filtro_colorgrade[:60]}...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # --- 5.1: Concatenar clips de vídeo ---
        clips_validos = [c for c in clips if c.get("clip_path") and Path(c["clip_path"]).exists()]
        if not clips_validos:
            return {"status": "error", "erro": "Nenhum clip de vídeo disponível"}

        concat_video = tmp / "concat_raw.mp4"
        ok_concat = _concatenar_clips(clips_validos, concat_video, verbose=verbose)
        if not ok_concat:
            return {"status": "error", "erro": "Falha na concatenação de clips"}

        # --- 5.2: Combinar narração de cada cena em uma trilha ---
        audio_narr = tmp / "narr_completa.mp3"
        ok_narr = _montar_audio_narracoes(narracoes, clips, audio_narr, verbose=verbose)

        # --- 5.3: Mixar narração + trilha sonora (se fornecida) ---
        audio_mix = tmp / "audio_mix.mp3"
        if ok_narr and trilha_path and Path(trilha_path).exists():
            ok_mix = _mixar_narr_trilha(audio_narr, Path(trilha_path), audio_mix, verbose=verbose)
            audio_final = audio_mix if ok_mix else audio_narr
        else:
            audio_final = audio_narr if ok_narr else None

        # --- 5.4: Aplicar color grade + adicionar áudio ---
        video_com_audio = tmp / "video_com_audio.mp4"
        ok_audio = _aplicar_colorgrade_e_audio(
            concat_video, audio_final, video_com_audio, filtro_colorgrade, verbose=verbose
        )

        video_pre_srt = video_com_audio if ok_audio else concat_video

        # --- 5.5: Legendas (opcional) ---
        if srt_path and Path(srt_path).exists():
            video_legendado = tmp / "video_legendado.mp4"
            ok_srt = _gravar_legendas(video_pre_srt, Path(srt_path), video_legendado, verbose=verbose)
            video_final_src = video_legendado if ok_srt else video_pre_srt
        else:
            video_final_src = video_pre_srt

        # --- 5.6: Exportar final ---
        shutil.copy2(video_final_src, output_path)

    if not output_path.exists():
        return {"status": "error", "erro": "Arquivo de saída não gerado"}

    tamanho = output_path.stat().st_size
    duracao_total = sum(c.get("duracao", 5.0) for c in clips_validos)

    if verbose:
        print(f"  ✅ Vídeo final: {output_path} ({tamanho / 1024 / 1024:.1f} MB)")

    return {
        "status": "ok",
        "output_path": str(output_path),
        "duracao_total": duracao_total,
        "n_cenas": len(clips_validos),
        "preset": preset_global,
        "tamanho_bytes": tamanho,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def _concatenar_clips(clips: list[dict], output: Path, verbose: bool = False) -> bool:
    """Concatena clips usando FFmpeg concat demuxer."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    # Criar arquivo de lista para concat
    lista_path = output.parent / "concat_list.txt"
    with open(lista_path, "w") as f:
        for clip in clips:
            f.write(f"file '{clip['clip_path']}'\n")

    cmd = [
        ffmpeg, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(lista_path),
        "-c", "copy",
        str(output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        return result.returncode == 0 and output.exists()
    except Exception:
        return False


def _montar_audio_narracoes(
    narracoes: list[dict],
    clips: list[dict],
    output: Path,
    verbose: bool = False,
) -> bool:
    """
    Monta trilha de narração concatenando áudios de cada cena.
    Preenche lacunas com silêncio quando narração não disponível.
    """
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    # Construir lista de áudios com silêncios
    segmentos = []
    for i, narr in enumerate(narracoes):
        duracao_clip = clips[i]["duracao"] if i < len(clips) else 5.0
        audio_path = narr.get("audio_path")

        if audio_path and Path(audio_path).exists() and narr.get("status") not in ("silencio", "error"):
            segmentos.append(("audio", audio_path, duracao_clip))
        else:
            segmentos.append(("silencio", None, duracao_clip))

    # Se tudo for silêncio, não gerar arquivo
    if all(s[0] == "silencio" for s in segmentos):
        return False

    # Construir filtro complex para concatenação
    inputs = []
    filter_parts = []
    idx = 0

    for tipo, path, dur in segmentos:
        if tipo == "audio" and path:
            inputs.extend(["-i", path])
            filter_parts.append(f"[{idx}:a]")
            idx += 1
        else:
            # Silêncio com lavfi
            inputs.extend([
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=mono:d={dur}",
            ])
            filter_parts.append(f"[{idx}:a]")
            idx += 1

    n = len(filter_parts)
    concat_filter = "".join(filter_parts) + f"concat=n={n}:v=0:a=1[aout]"

    cmd = [ffmpeg, "-y"] + inputs + [
        "-filter_complex", concat_filter,
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "4",
        str(output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0 and output.exists()
    except Exception:
        return False


def _mixar_narr_trilha(
    narr_path: Path,
    trilha_path: Path,
    output: Path,
    verbose: bool = False,
) -> bool:
    """Mixa narração (90%) com trilha de fundo (25%)."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    cmd = [
        ffmpeg, "-y",
        "-i", str(narr_path),
        "-i", str(trilha_path),
        "-filter_complex",
        "[0:a]volume=0.9[narr];[1:a]volume=0.25,aloop=loop=-1:size=2e+09[trilha];[narr][trilha]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "[aout]",
        "-c:a", "libmp3lame",
        "-q:a", "4",
        str(output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0 and output.exists()
    except Exception:
        return False


def _aplicar_colorgrade_e_audio(
    video_path: Path,
    audio_path: Optional[Path],
    output: Path,
    filtro_colorgrade: str,
    verbose: bool = False,
) -> bool:
    """Aplica color grade ao vídeo e adiciona trilha de áudio."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    cmd = [ffmpeg, "-y", "-i", str(video_path)]

    if audio_path and audio_path.exists():
        cmd += ["-i", str(audio_path)]
        cmd += [
            "-vf", filtro_colorgrade,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output),
        ]
    else:
        cmd += [
            "-vf", filtro_colorgrade,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-an",
            str(output),
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        return result.returncode == 0 and output.exists()
    except Exception:
        return False


def _gravar_legendas(
    video_path: Path,
    srt_path: Path,
    output: Path,
    verbose: bool = False,
) -> bool:
    """Grava legendas no vídeo via FFmpeg subtitles filter."""
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    cmd = [
        ffmpeg, "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,Bold=1'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-c:a", "copy",
        str(output),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        return result.returncode == 0 and output.exists()
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────
#  PASSO 6 — GERAÇÃO DE LEGENDAS SRT
# ─────────────────────────────────────────────────────────────────

def gerar_legendas_srt(
    roteiro_cinematico: dict,
    narracoes: list[dict],
    output_path: Path,
) -> bool:
    """
    Gera arquivo .srt de legendas baseado nas narrações por cena.
    Sincroniza timing com duração real de cada clipe.
    """
    output_path = Path(output_path)
    cenas = roteiro_cinematico.get("cenas", [])

    linhas_srt = []
    tempo_acumulado = 0.0

    for i, (cena, narr) in enumerate(zip(cenas, narracoes)):
        texto = cena.get("narracao", cena.get("texto", "")).strip()
        duracao = float(cena.get("duracao", 5.0))

        if not texto:
            tempo_acumulado += duracao
            continue

        inicio = tempo_acumulado
        fim = tempo_acumulado + duracao

        linhas_srt.append(str(i + 1))
        linhas_srt.append(f"{_ts(inicio)} --> {_ts(fim)}")
        linhas_srt.append(texto)
        linhas_srt.append("")

        tempo_acumulado += duracao

    if not linhas_srt:
        return False

    output_path.write_text("\n".join(linhas_srt), encoding="utf-8")
    return True


def _ts(segundos: float) -> str:
    """Converte segundos para formato SRT HH:MM:SS,mmm."""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ─────────────────────────────────────────────────────────────────
#  PASSO 7 — THUMBNAIL
# ─────────────────────────────────────────────────────────────────

def gerar_thumbnail_video(
    roteiro_cinematico: dict,
    imagens_cenas: list[dict],
    canal_config: dict,
    output_path: Path,
    verbose: bool = True,
) -> dict:
    """
    Gera thumbnail para YouTube usando:
    1. Imagem da cena de maior impacto (índice configurável)
    2. Sobreposição de título em destaque
    Chama AGENTE IMAGE ENGINE (gerar_thumbnail).
    """
    from core.image_engine import gerar_thumbnail

    titulo = roteiro_cinematico.get("titulo", canal_config.get("nome", "DARK STUDIO"))
    canal = canal_config.get("nicho", "documentario")

    # Escolher imagem base: cena de maior impacto (último terço)
    imagens_ok = [img for img in imagens_cenas if img.get("status") == "ok" and img.get("imagem_path")]
    if imagens_ok:
        idx_impacto = max(0, len(imagens_ok) * 2 // 3)
        imagem_base = imagens_ok[idx_impacto]["imagem_path"]
    else:
        imagem_base = None

    r = gerar_thumbnail(
        titulo=titulo,
        output_path=output_path,
        canal=canal,
        imagem_base=imagem_base,
    )

    if verbose:
        status = "✅" if r.get("status") == "ok" else "⚠️ "
        print(f"  {status} Thumbnail: {output_path}")

    return r


# ─────────────────────────────────────────────────────────────────
#  PASSO 8 — CONTROLE DE QUALIDADE
# ─────────────────────────────────────────────────────────────────

def verificar_qualidade_f02(
    video_path: Path,
    roteiro_cinematico: dict,
    verbose: bool = True,
) -> dict:
    """
    Executa QA no vídeo final.
    Chama AGENTE CREATIVE QA.
    """
    from core.creative_qa import verificar_qualidade

    n_cenas = len(roteiro_cinematico.get("cenas", []))
    duracao_esperada = sum(
        float(c.get("duracao", 5.0))
        for c in roteiro_cinematico.get("cenas", [])
    )

    r = verificar_qualidade(
        video_path=video_path,
        n_cenas=n_cenas,
        duracao_esperada=duracao_esperada,
    )

    if verbose:
        score = r.get("score", 0)
        status = "✅" if score >= 70 else "⚠️ "
        print(f"  {status} QA Score: {score}/100")

    return r


# ─────────────────────────────────────────────────────────────────
#  PIPELINE COMPLETO F02
# ─────────────────────────────────────────────────────────────────

def produzir_video_imagem_realista(
    roteiro: dict,
    canal_config: dict,
    output_dir: str,
    trilha_path: Optional[str] = None,
    formato: str = "horizontal",
    incluir_legendas: bool = True,
    verbose: bool = True,
) -> dict:
    """
    PIPELINE F02 — PRODUÇÃO COMPLETA: IMAGEM REALISTA

    Fluxo:
        roteiro → plano cinematográfico → imagens realistas
        → Ken Burns zoompan → narrações
        → montagem (colorgrade + áudio + legendas)
        → thumbnail → QA → MP4 final

    Args:
        roteiro:        Dict com título, cenas (id, narracao, duracao, etc.)
        canal_config:   Dict com nicho, nome, etc.
        output_dir:     Diretório de saída
        trilha_path:    Trilha sonora de fundo (opcional)
        formato:        "horizontal" (16:9) | "vertical" (9:16) | "quadrado"
        incluir_legendas: Gerar e queimar legendas .srt
        verbose:        Imprimir progresso

    Returns:
        Dict com status, output_path, relatório completo.
    """
    inicio = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    projeto_id = roteiro.get("id", "projeto")
    titulo = roteiro.get("titulo", "video")

    if verbose:
        print(f"\n{'═'*60}")
        print(f"  DARK CREATIVE LAB — PIPELINE F02: IMAGEM REALISTA")
        print(f"  Projeto: {projeto_id} | Canal: {canal_config.get('nicho', '?')}")
        print(f"  Formato: {formato} | Cenas: {len(roteiro.get('cenas', []))}")
        print(f"{'═'*60}\n")

    relatorio = {
        "projeto_id": projeto_id,
        "titulo": titulo,
        "canal": canal_config.get("nicho", ""),
        "formato": formato,
        "etapas": {},
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    # ── Banco Visual: inicializar consistência do projeto ──
    visual_bank = None
    try:
        from core.visual_consistency import ProjetoVisualBank, PALETAS_POR_NICHO
        nicho = canal_config.get("nicho", "default")
        preset_nome = NICHO_PARA_PRESET.get(nicho, "documentario")
        visual_bank = ProjetoVisualBank(output_dir)

        # Criar ou atualizar projeto no banco
        proj_existente = visual_bank.carregar_projeto(projeto_id)
        if not proj_existente:
            visual_bank.criar_projeto(
                projeto_id=projeto_id,
                titulo=titulo,
                nicho=nicho,
                preset=preset_nome,
                descricao=roteiro.get("hook", ""),
            )
        if verbose:
            print(f"  🎨 Banco visual inicializado: {projeto_id}")
    except Exception as e:
        if verbose:
            print(f"  ⚠️  Banco visual não disponível: {e}")
        visual_bank = None

    # ── Etapa 1: Planejamento cinematográfico ──
    if verbose:
        print("▶ ETAPA 1/7 — Planejamento Cinematográfico")
    try:
        roteiro_cine = planejar_cenas(roteiro, canal_config)
        relatorio["etapas"]["planejamento"] = {"status": "ok", "n_cenas": len(roteiro_cine.get("cenas", []))}
    except Exception as e:
        relatorio["etapas"]["planejamento"] = {"status": "error", "erro": str(e)}
        roteiro_cine = roteiro  # fallback sem enriquecimento

    # ── Etapa 2: Geração de imagens ──
    if verbose:
        print("\n▶ ETAPA 2/7 — Geração de Imagens Realistas")
    imgs_dir = output_dir / "imagens"
    try:
        imagens = gerar_imagens_cenas(
            roteiro_cine, imgs_dir,
            formato=formato, verbose=verbose,
            visual_bank=visual_bank,
            projeto_id=projeto_id,
        )
        n_ok = sum(1 for img in imagens if img["status"] == "ok")
        relatorio["etapas"]["imagens"] = {"status": "ok", "geradas": n_ok, "total": len(imagens)}
        if verbose:
            print(f"  → {n_ok}/{len(imagens)} imagens geradas")
    except Exception as e:
        relatorio["etapas"]["imagens"] = {"status": "error", "erro": str(e)}
        imagens = []

    # ── Etapa 3: Ken Burns / Zoompan ──
    if verbose:
        print("\n▶ ETAPA 3/7 — Animação Ken Burns")
    clips_dir = output_dir / "clips"
    try:
        clips = animar_imagens_ken_burns(imagens, roteiro_cine, clips_dir, verbose=verbose)
        n_clips = sum(1 for c in clips if c["status"] in ("ok", "placeholder"))
        relatorio["etapas"]["ken_burns"] = {"status": "ok", "clips": n_clips}
        if verbose:
            print(f"  → {n_clips}/{len(clips)} clips animados")
    except Exception as e:
        relatorio["etapas"]["ken_burns"] = {"status": "error", "erro": str(e)}
        clips = []

    # ── Etapa 4: Narrações ──
    if verbose:
        print("\n▶ ETAPA 4/7 — Narrações")
    narr_dir = output_dir / "narracoes"
    try:
        narracoes = gerar_narracoes(roteiro_cine, narr_dir, verbose=verbose)
        n_narr = sum(1 for n in narracoes if n["status"] in ("ok",))
        relatorio["etapas"]["narracoes"] = {"status": "ok", "geradas": n_narr, "total": len(narracoes)}
        if verbose:
            print(f"  → {n_narr}/{len(narracoes)} narrações geradas")
    except Exception as e:
        relatorio["etapas"]["narracoes"] = {"status": "error", "erro": str(e)}
        narracoes = []

    # ── Etapa 5: Legendas SRT ──
    srt_path = None
    if incluir_legendas and narracoes:
        if verbose:
            print("\n▶ ETAPA 5/7 — Legendas SRT")
        srt_path = output_dir / f"{projeto_id}.srt"
        try:
            ok_srt = gerar_legendas_srt(roteiro_cine, narracoes, srt_path)
            relatorio["etapas"]["legendas"] = {"status": "ok" if ok_srt else "skip"}
            if not ok_srt:
                srt_path = None
        except Exception as e:
            relatorio["etapas"]["legendas"] = {"status": "error", "erro": str(e)}
            srt_path = None

    # ── Etapa 6: Montagem final ──
    if verbose:
        print("\n▶ ETAPA 6/7 — Montagem Final")
    video_path = output_dir / f"{projeto_id}_final.mp4"
    try:
        r_mont = montar_video_final(
            clips=clips,
            narracoes=narracoes,
            roteiro_cinematico=roteiro_cine,
            output_path=video_path,
            trilha_path=trilha_path,
            srt_path=str(srt_path) if srt_path else None,
            verbose=verbose,
        )
        relatorio["etapas"]["montagem"] = r_mont
    except Exception as e:
        r_mont = {"status": "error", "erro": str(e)}
        relatorio["etapas"]["montagem"] = r_mont

    # ── Etapa 7: Thumbnail ──
    if verbose:
        print("\n▶ ETAPA 7/7 — Thumbnail")
    thumb_path = output_dir / f"{projeto_id}_thumb.jpg"
    try:
        r_thumb = gerar_thumbnail_video(
            roteiro_cine, imagens, canal_config, thumb_path, verbose=verbose
        )
        relatorio["etapas"]["thumbnail"] = r_thumb
    except Exception as e:
        relatorio["etapas"]["thumbnail"] = {"status": "error", "erro": str(e)}

    # ── QA final ──
    if r_mont.get("status") == "ok" and video_path.exists():
        try:
            r_qa = verificar_qualidade_f02(video_path, roteiro_cine, verbose=verbose)
            relatorio["qa"] = r_qa
        except Exception as e:
            relatorio["qa"] = {"status": "error", "erro": str(e)}

    # ── Relatório final ──
    elapsed = time.time() - inicio
    etapas_ok = sum(1 for e in relatorio["etapas"].values() if e.get("status") == "ok")
    total_etapas = len(relatorio["etapas"])

    relatorio.update({
        "status": "ok" if r_mont.get("status") == "ok" else "partial",
        "output_video": str(video_path) if video_path.exists() else None,
        "output_thumbnail": str(thumb_path) if thumb_path.exists() else None,
        "output_srt": str(srt_path) if srt_path and srt_path.exists() else None,
        "etapas_ok": etapas_ok,
        "total_etapas": total_etapas,
        "duracao_producao_s": round(elapsed, 1),
    })

    if verbose:
        print(f"\n{'═'*60}")
        ok_icon = "✅" if relatorio["status"] == "ok" else "⚠️ "
        print(f"  {ok_icon} F02 Concluído em {elapsed:.1f}s")
        print(f"  Etapas: {etapas_ok}/{total_etapas}")
        print(f"  Vídeo: {relatorio.get('output_video', 'N/A')}")
        print(f"  Thumb: {relatorio.get('output_thumbnail', 'N/A')}")
        print(f"  ai_generated: True")
        print(f"  ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")
        print(f"{'═'*60}\n")

    return relatorio


# ─────────────────────────────────────────────────────────────────
#  HELPERS DE NICHO
# ─────────────────────────────────────────────────────────────────

def carregar_canal_config(canal_id: int) -> dict:
    """Carrega configuração de um dos 12 canais."""
    base = Path(__file__).parent.parent / "config" / "canais"
    arquivo = base / f"canal_{canal_id:02d}_*.json"

    # Encontrar o arquivo
    import glob
    arquivos = sorted(glob.glob(str(arquivo)))
    if not arquivos:
        raise FileNotFoundError(f"Canal {canal_id:02d} não encontrado em {base}")

    with open(arquivos[0], encoding="utf-8") as f:
        return json.load(f)


def listar_canais() -> list[dict]:
    """Lista todos os 12 canais disponíveis."""
    base = Path(__file__).parent.parent / "config" / "canais"
    canais = []
    for p in sorted(base.glob("canal_*.json")):
        try:
            with open(p) as f:
                cfg = json.load(f)
            canais.append({"arquivo": p.name, "nicho": cfg.get("nicho"), "nome": cfg.get("nome")})
        except Exception:
            pass
    return canais


# ─────────────────────────────────────────────────────────────────
#  ROTEIRO DE EXEMPLO POR NICHO
# ─────────────────────────────────────────────────────────────────

ROTEIROS_EXEMPLO = {
    "psicologia": {
        "id": "psico_001",
        "titulo": "A Mente Humana: Segredos do Subconsciente",
        "cenas": [
            {"id": "c01", "narracao": "O subconsciente controla 95% das nossas decisões.", "duracao": 5.0, "descricao_visual": "Cérebro humano com sinapses iluminadas"},
            {"id": "c02", "narracao": "Estudos revelam padrões ocultos no comportamento.", "duracao": 5.0, "descricao_visual": "Pessoa olhando para espelho reflexivo"},
            {"id": "c03", "narracao": "Técnicas de reprogramação mental transformam vidas.", "duracao": 5.0, "descricao_visual": "Meditação em ambiente tranquilo"},
        ]
    },
    "historia": {
        "id": "hist_001",
        "titulo": "A Batalha que Mudou o Mundo",
        "cenas": [
            {"id": "c01", "narracao": "Em 1453, o Império Otomano cercou Constantinopla.", "duracao": 6.0, "descricao_visual": "Muralhas antigas ao amanhecer"},
            {"id": "c02", "narracao": "Após 53 dias, a cidade milenar caiu.", "duracao": 5.0, "descricao_visual": "Exército medieval em campo de batalha"},
            {"id": "c03", "narracao": "O mundo nunca mais seria o mesmo.", "duracao": 5.0, "descricao_visual": "Cidade histórica ao entardecer"},
        ]
    },
    "natureza": {
        "id": "nat_001",
        "titulo": "As Maravilhas Ocultas da Amazônia",
        "cenas": [
            {"id": "c01", "narracao": "A Amazônia abriga 10% de todas as espécies do planeta.", "duracao": 6.0, "descricao_visual": "Rio Amazonas visto de cima"},
            {"id": "c02", "narracao": "Cada dia, novas descobertas revelam sua complexidade.", "duracao": 5.0, "descricao_visual": "Floresta tropical densa com raios de sol"},
            {"id": "c03", "narracao": "Um tesouro natural que precisamos preservar.", "duracao": 5.0, "descricao_visual": "Pôr do sol sobre a floresta"},
        ]
    },
}


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT PARA TESTE
# ─────────────────────────────────────────────────────────────────

def check_pipeline_f02() -> dict:
    """Verifica se o pipeline F02 está operacional."""
    checks = {
        "cinematic_director": False,
        "image_engine": False,
        "audio_master": False,
        "cinema_editor": False,
        "creative_qa": False,
        "ffmpeg": False,
    }

    try:
        from core.cinematic_director import check_cinematic_director
        checks["cinematic_director"] = check_cinematic_director().get("status") == "ok"
    except Exception:
        pass

    try:
        from core.image_engine import check_image_engine
        checks["image_engine"] = check_image_engine().get("status") == "ok"
    except Exception:
        pass

    try:
        from core.audio_master import check_audio_master
        checks["audio_master"] = check_audio_master().get("status") == "ok"
    except Exception:
        pass

    try:
        from core.cinema_editor import check_cinema_editor
        checks["cinema_editor"] = check_cinema_editor().get("status") == "ok"
    except Exception:
        pass

    try:
        from core.creative_qa import check_creative_qa
        checks["creative_qa"] = check_creative_qa().get("status") == "ok"
    except Exception:
        pass

    checks["ffmpeg"] = bool(shutil.which("ffmpeg"))

    ok_count = sum(checks.values())
    total = len(checks)

    return {
        "status": "ok" if ok_count >= 5 else "degradado",
        "componentes": checks,
        "operacionais": f"{ok_count}/{total}",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


if __name__ == "__main__":
    import sys

    # Verificação rápida
    print("\n═══ DARK CREATIVE LAB — PIPELINE F02: VERIFICAÇÃO ═══\n")
    sys.path.insert(0, str(Path(__file__).parent.parent))
    r = check_pipeline_f02()
    print(f"  Status: {r['status']}")
    print(f"  Componentes: {r['operacionais']}")
    for nome, ok in r["componentes"].items():
        icon = "✅" if ok else "❌"
        print(f"    {icon} {nome}")
    print(f"\n  ai_generated: True")
    print(f"  ai_disclosure: {r['ai_disclosure']}\n")
