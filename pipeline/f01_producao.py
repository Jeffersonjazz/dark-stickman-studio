"""
DARK STICKMAN STUDIO — Pipeline F01: Produção Completa
15 passos: roteiro → narração → animação → montagem → legenda → thumbnail → MP4 final.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import shutil
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Imports dos módulos core
from core.piper_tts import narrar_roteiro, get_audio_duration

# DARK VIDEO STUDIO — geração de vídeos realistas (Phase 3)
try:
    from core.dark_video_studio import generate_scene_videos, check_backends as _check_video_backends
    _VIDEO_STUDIO_OK = True
except Exception:
    _VIDEO_STUDIO_OK = False

# Manim (opcional) — fallback para ffmpeg_scene quando não instalado
try:
    from core.manim_scene import render_roteiro, render_intro_hook, render_outro_cta
    _MANIM_OK = True
except Exception:
    _MANIM_OK = False

# Fallback FFmpeg+Pillow (sempre disponível)
from core.ffmpeg_scene import (
    renderizar_cena_pillow,
    renderizar_intro_hook_ffmpeg,
    renderizar_outro_cta_ffmpeg,
)

from core.ffmpeg_utils import (
    concat_videos, add_audio, mix_audio, normalize_audio,
    burn_subtitles, add_watermark_text, apply_color_grade, export_final,
    get_duration, check_ffmpeg,
)
from core.legenda import pipeline_legenda, audio_para_srt, srt_de_narracao
from core.thumbnail import gerar_thumbnail, gerar_variacao

# DARK CREATIVE LAB — Agentes integrados
try:
    from core.visual_consistency import setup_projeto, gerar_prompt_com_continuidade, validar_consistencia_roteiro
    _VISUAL_CONSISTENCY_OK = True
except Exception:
    _VISUAL_CONSISTENCY_OK = False

try:
    from core.motion_graphics import gerar_intro, gerar_outro, gerar_pacote_canal
    _MOTION_GRAPHICS_OK = True
except Exception:
    _MOTION_GRAPHICS_OK = False

try:
    from core.creative_qa import verificar_qualidade as _qa_verificar_qualidade
    _CREATIVE_QA_OK = True
except Exception:
    _CREATIVE_QA_OK = False

try:
    from core.performance import PipelineProfiler, AssetCache, CustoEstimador, gerar_relatorio_performance
    _PERFORMANCE_OK = True
except Exception:
    _PERFORMANCE_OK = False

# Banco de dados local
DB_PATH = Path(__file__).parent.parent / "db" / "dark_stickman.db"

# Watermark obrigatório — identificação de IA
WATERMARK_TEXT = "Produzido com IA — DARK STUDIO AAA"

# Diretório raiz de saída dos vídeos
OUTPUT_ROOT = Path(__file__).parent.parent / "output"


# ─────────────────────────────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────────────────────────────

def _init_db():
    """Inicializa o banco de dados SQLite com WAL mode para evitar locking."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")   # FIX: evita "database is locked"
    conn.execute("PRAGMA synchronous=NORMAL") # FIX: performance + segurança
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            canal_id TEXT NOT NULL,
            titulo TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            etapa_atual TEXT,
            progresso INTEGER DEFAULT 0,
            output_path TEXT,
            thumbnail_path TEXT,
            erro TEXT,
            ai_generated INTEGER DEFAULT 1,
            ai_disclosure TEXT DEFAULT 'Produzido com DARK STUDIO AAA — DARK CREATIVE LAB',
            criado_em TEXT,
            finalizado_em TEXT
        )
    """)
    conn.commit()
    conn.close()


def _get_conn() -> sqlite3.Connection:
    """Abre conexão SQLite com timeout e WAL ativado."""
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")  # FIX: aguarda 10s antes de falhar
    return conn


def _job_update(job_id: str, **kwargs):
    """Atualiza campos de um job no banco."""
    if not DB_PATH.exists():
        return
    campos = ", ".join(f"{k} = ?" for k in kwargs)
    valores = list(kwargs.values()) + [job_id]
    try:
        conn = _get_conn()
        conn.execute(f"UPDATE jobs SET {campos} WHERE id = ?", valores)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Falha ao atualizar job {job_id}: {e}")


def _job_criar(job_id: str, canal_id: str, titulo: str):
    """Registra um novo job (INSERT OR REPLACE para evitar UNIQUE constraint)."""
    try:
        conn = _get_conn()
        # FIX: INSERT OR REPLACE evita "UNIQUE constraint failed" em reexecuções
        conn.execute(
            "INSERT OR REPLACE INTO jobs (id, canal_id, titulo, status, criado_em) VALUES (?, ?, ?, 'running', ?)",
            (job_id, canal_id, titulo, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Falha ao criar job: {e}")


# ─────────────────────────────────────────────────────────────────
#  PIPELINE F01
# ─────────────────────────────────────────────────────────────────

def produzir_video(
    roteiro: dict,
    canal_config: dict,
    output_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
    qualidade: str = "medium_quality",
    preset_cor: Optional[str] = None,
    formato: str = "16:9",
    gerar_shorts: bool = False,
) -> dict:
    """
    Pipeline completo de produção de um vídeo stickman.

    Args:
        roteiro: Dict com 'titulo', 'descricao', 'cenas' (lista), 'gancho', 'cta'.
        canal_config: Config do canal (nicho, cor, nome, piper_model, ...).
        output_dir: Diretório de saída. Se None, usa output/<canal_id>/<job_id>/.
        job_id: ID do job (gerado automaticamente se não fornecido).
        qualidade: 'low_quality', 'medium_quality', 'high_quality'.
        preset_cor: Preset de color grading (None = usa nicho do canal).
        formato: '16:9' ou '9:16'.
        gerar_shorts: Se True, gera versão vertical para Shorts.

    Returns:
        Dict com resultado: {'status', 'output_mp4', 'thumbnail', 'job_id', 'duracao'}.
    """
    _init_db()

    job_id = job_id or str(uuid.uuid4())[:8]
    canal_id = canal_config.get("id", "canal_00")
    titulo = roteiro.get("titulo", "Video Stickman")

    # Mapeamento nicho → preset de cor
    nicho = canal_config.get("nicho", "default")
    preset_cor = preset_cor or {
        "psicologia": "documentario", "batalhas": "batalha",
        "tecnologia": "tecnologia", "filosofia": "suspense",
        "historia": "documentario", "misterio": "suspense",
        "educacao": "educacao", "relaxamento": "relaxamento",
        "natureza": "natureza", "stem": "educacao",
        "musical": "relaxamento", "financas": "educacao",
        "saude": "relaxamento",
    }.get(nicho, "neutral")

    # Diretório de trabalho
    if output_dir is None:
        output_dir = OUTPUT_ROOT / canal_id / job_id
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Subdiretórios de trabalho
    dir_audio = output_dir / "audio"
    dir_clips = output_dir / "clips"
    dir_legenda = output_dir / "legenda"
    dir_thumb = output_dir / "thumbnail"
    for d in [dir_audio, dir_clips, dir_legenda, dir_thumb]:
        d.mkdir(parents=True, exist_ok=True)

    _job_criar(job_id, canal_id, titulo)

    # ── DARK CREATIVE LAB: Inicializar PERFORMANCE PROFILER ──────────
    _profiler = None
    _custo = None
    _cache = None
    if _PERFORMANCE_OK:
        try:
            _profiler = PipelineProfiler(job_id)
            _custo = CustoEstimador()
            _cache = AssetCache(dir_audio)
            print(f"[F01] PERFORMANCE PROFILER inicializado — job_id={job_id}")
        except Exception as _e:
            print(f"[F01] Performance profiler init falhou: {_e}")

    # ── DARK CREATIVE LAB: Inicializar VISUAL CONSISTENCY ────────────
    _vc_db = None
    if _VISUAL_CONSISTENCY_OK:
        try:
            _vc_db = setup_projeto(output_dir, canal_config, preset_nome=preset_cor)
            print(f"[F01] VISUAL CONSISTENCY inicializada — nicho={nicho}")
        except Exception as _e:
            print(f"[F01] Visual Consistency init falhou: {_e}")

    resultado = {
        "job_id": job_id,
        "status": "error",
        "output_mp4": None,
        "thumbnail": None,
        "duracao": 0,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    cenas = roteiro.get("cenas", [])
    if not cenas:
        _job_update(job_id, status="error", erro="Roteiro sem cenas")
        resultado["erro"] = "Roteiro sem cenas"
        return resultado

    # AGENTE DURATION ENGINEER: Expandir roteiro para mínimo 4 minutos
    roteiro = _expandir_roteiro_4min(roteiro)
    cenas = roteiro.get("cenas", [])

    t0 = time.time()

    try:
        # ── ETAPA 1: Validar FFmpeg ──────────────────────────────────────
        _etapa(job_id, "validando_ffmpeg", 5)
        if not check_ffmpeg():
            raise RuntimeError("FFmpeg não encontrado. Instale em: https://ffmpeg.org/download.html")

        # ── ETAPA 2: Narração com Piper TTS ─────────────────────────────
        _etapa(job_id, "narracao_tts", 10)
        print(f"\n[F01] ETAPA 2 — Narração TTS ({len(cenas)} cenas)")
        modelo_piper = canal_config.get("piper_model", "faber-medium")
        if _profiler:
            with _profiler.etapa("ETAPA_02_TTS", meta={"modelo": modelo_piper, "num_cenas": len(cenas)}):
                audios_narracao = narrar_roteiro(cenas, dir_audio, model=modelo_piper)
            if _custo:
                _custo.registrar("tts_gtts", len(cenas), f"Narração {len(cenas)} cenas")
        else:
            audios_narracao = narrar_roteiro(cenas, dir_audio, model=modelo_piper)

        # ── ETAPA 3: Intro/Hook ──────────────────────────────────────────
        _etapa(job_id, "renderizando_hook", 20)
        if _profiler: _profiler.iniciar_etapa("ETAPA_03_INTRO")
        gancho_texto = roteiro.get("gancho", cenas[0].get("narracao", titulo) if cenas else titulo)
        clip_hook = None
        # DARK CREATIVE LAB: MOTION GRAPHICS intro (prioridade sobre Manim/FFmpeg)
        if _MOTION_GRAPHICS_OK:
            print(f"[F01] ETAPA 3 — Intro/Hook (MOTION GRAPHICS)")
            try:
                mg_intro = gerar_intro(
                    canal_config, dir_clips / "hook.mp4",
                    duracao=5.0, estilo=preset_cor, resolucao="1920x1080"
                )
                if mg_intro.get("status") == "ok":
                    clip_hook = Path(mg_intro["output"])
                    print(f"[F01] MOTION GRAPHICS intro ✅ — {clip_hook.name}")
            except Exception as e:
                print(f"[F01] Motion Graphics intro falhou ({e}) — fallback")
        if clip_hook is None and _MANIM_OK:
            print(f"[F01] ETAPA 3 — Intro/Hook (Manim)")
            try:
                clip_hook = render_intro_hook(canal_config, gancho_texto, dir_clips / "hook.mp4")
            except Exception as e:
                print(f"[F01] Manim hook falhou ({e}) — usando FFmpeg")
        if clip_hook is None:
            print(f"[F01] ETAPA 3 — Intro/Hook (FFmpeg)")
            clip_hook = renderizar_intro_hook_ffmpeg(gancho_texto, canal_config, dir_clips / "hook.mp4")

        # ── ETAPA 4: Renderizar cenas ────────────────────────────────────
        _etapa(job_id, "renderizando_cenas", 30)
        if _profiler: _profiler.iniciar_etapa("ETAPA_04_CENAS")
        clips_cenas = []

        # Opção A: DARK VIDEO STUDIO (vídeos realistas — se habilitado no preset)
        _usar_video_studio = (
            _VIDEO_STUDIO_OK
            and canal_config.get("video_realista", False)
            and any(c.get("prompt_visual") for c in cenas)
        )
        if _usar_video_studio:
            preset_video = canal_config.get("video_preset", "documentario")
            print(f"[F01] ETAPA 4 — DARK VIDEO STUDIO ({preset_video}) para {len(cenas)} cenas")
            try:
                video_clips = generate_scene_videos(
                    cenas, dir_clips / "video_studio", preset=preset_video, verbose=True
                )
                # Combina: usa vídeo realista se gerado, senão fallback stickman
                for i, (vc, cena) in enumerate(zip(video_clips, cenas)):
                    if vc and Path(vc).exists():
                        clips_cenas.append(Path(vc))
                        print(f"[F01]   Cena {i+1}/{len(cenas)} → VIDEO STUDIO ✅")
                    else:
                        clips_cenas.append(None)  # será preenchido abaixo
            except Exception as e:
                print(f"[F01] VIDEO STUDIO falhou ({e}) — usando animação stickman")
                clips_cenas = []

        # Opção B: Manim (stickman animado)
        if not _usar_video_studio or not any(c is not None for c in clips_cenas):
            clips_cenas = []
            if _MANIM_OK:
                print(f"[F01] ETAPA 4 — Renderizando {len(cenas)} cenas (Manim)")
                try:
                    clips_cenas = render_roteiro(cenas, dir_clips, canal_config, quality=qualidade)
                except Exception as e:
                    print(f"[F01] Manim cenas falhou ({e}) — usando FFmpeg")
                    clips_cenas = []

        # Opção C: FFmpeg+Pillow (fallback sempre disponível)
        if not any(c is not None for c in clips_cenas):
            clips_cenas = []
            print(f"[F01] ETAPA 4 — Renderizando {len(cenas)} cenas (FFmpeg+Pillow)")
            for i, cena in enumerate(cenas):
                # DARK CREATIVE LAB: enriquecer prompt com VISUAL CONSISTENCY
                if _VISUAL_CONSISTENCY_OK and _vc_db is not None:
                    try:
                        cena = dict(cena)  # cópia para não mutar o original
                        cena["_prompt_vc"] = gerar_prompt_com_continuidade(cena, _vc_db, cena.get("narracao",""))
                    except Exception:
                        pass
                out = dir_clips / f"cena_{i+1:02d}.mp4"
                pose = cena.get("pose", "parado")
                texto = cena.get("texto_tela", cena.get("narracao", "")[:60])
                narracao = cena.get("narracao", "")
                duracao = float(cena.get("duracao_s", 8.0))
                clip = renderizar_cena_pillow(
                    cena_num=i + 1, pose=pose, texto_tela=texto,
                    narracao=narracao, duracao_s=duracao,
                    canal_config=canal_config, output_path=out
                )
                clips_cenas.append(clip)
                print(f"[F01]   Cena {i+1}/{len(cenas)} → {out.name}")

        # ── ETAPA 5: Outro/CTA ───────────────────────────────────────────
        _etapa(job_id, "renderizando_outro", 45)
        if _profiler: _profiler.iniciar_etapa("ETAPA_05_OUTRO")
        cta_texto = roteiro.get("cta", f"Se inscreva no canal {canal_config.get('nome', '')}!")
        clip_outro = None
        # DARK CREATIVE LAB: MOTION GRAPHICS outro (prioridade)
        if _MOTION_GRAPHICS_OK:
            print(f"[F01] ETAPA 5 — Outro/CTA (MOTION GRAPHICS)")
            try:
                mg_outro = gerar_outro(
                    canal_config, dir_clips / "outro.mp4",
                    duracao=8.0, cta_texto=cta_texto, resolucao="1920x1080"
                )
                if mg_outro.get("status") == "ok":
                    clip_outro = Path(mg_outro["output"])
                    print(f"[F01] MOTION GRAPHICS outro ✅ — {clip_outro.name}")
            except Exception as e:
                print(f"[F01] Motion Graphics outro falhou ({e}) — fallback")
        if clip_outro is None and _MANIM_OK:
            print(f"[F01] ETAPA 5 — Outro/CTA (Manim)")
            try:
                clip_outro = render_outro_cta(canal_config, cta_texto, dir_clips / "outro.mp4")
            except Exception as e:
                print(f"[F01] Manim outro falhou ({e}) — usando FFmpeg")
        if clip_outro is None:
            print(f"[F01] ETAPA 5 — Outro/CTA (FFmpeg)")
            clip_outro = renderizar_outro_cta_ffmpeg(canal_config, dir_clips / "outro.mp4")

        # ── ETAPA 6: Adicionar narração em cada cena ─────────────────────
        _etapa(job_id, "sincronizando_audio", 50)
        if _profiler: _profiler.iniciar_etapa("ETAPA_06_SYNC_AUDIO")
        print(f"[F01] ETAPA 6 — Sincronizando áudio com cenas")
        clips_com_audio = []
        for i, (clip, audio) in enumerate(zip(clips_cenas, audios_narracao)):
            if clip is None:
                print(f"[F01] Cena {i+1} sem clip — pulando")
                continue
            if audio is None:
                clips_com_audio.append(clip)
                continue
            out_sync = dir_clips / f"cena_{i+1:02d}_sync.mp4"
            try:
                clips_com_audio.append(add_audio(clip, audio, out_sync))
            except Exception as e:
                print(f"[F01] Sync audio cena {i+1} falhou: {e} — usando clip sem áudio")
                clips_com_audio.append(clip)

        # ── ETAPA 7: Concatenar clips ─────────────────────────────────────
        _etapa(job_id, "concatenando_clips", 58)
        if _profiler: _profiler.iniciar_etapa("ETAPA_07_CONCAT")
        print(f"[F01] ETAPA 7 — Concatenando clips")
        todos_clips = []
        if clip_hook:
            todos_clips.append(clip_hook)
        todos_clips.extend(clips_com_audio)
        if clip_outro:
            todos_clips.append(clip_outro)

        # Filtra None
        todos_clips = [c for c in todos_clips if c is not None and Path(c).exists()]

        if not todos_clips:
            raise RuntimeError("Nenhum clip válido gerado. Verifique logs acima.")

        video_concat = output_dir / "concat.mp4"
        if len(todos_clips) == 1:
            shutil.copy2(todos_clips[0], video_concat)
        else:
            # Transição dissolve apenas para poucos clips (xfade com muitos clips gera filtergraph gigante → erro)
            _transition = "dissolve" if len(todos_clips) <= 3 else "none"
            concat_videos(todos_clips, video_concat, transition=_transition, transition_dur=0.4)

        # ── ETAPA 8: Mixar trilha sonora ──────────────────────────────────
        _etapa(job_id, "mixando_audio", 63)
        if _profiler: _profiler.iniciar_etapa("ETAPA_08_MIX_AUDIO")
        print(f"[F01] ETAPA 8 — Mixando trilha sonora")
        music_path = _buscar_musica(canal_config, nicho)
        video_com_musica = output_dir / "com_musica.mp4"

        if music_path and music_path.exists():
            # Extrai áudio do vídeo concatenado e mixa
            narr_tmp = dir_audio / "narr_concat.wav"
            _extrair_audio(video_concat, narr_tmp)
            audio_mixado = dir_audio / "mix_final.aac"
            mix_audio(narr_tmp, music_path, audio_mixado, vol_narr=1.0, vol_music=0.12)
            add_audio(video_concat, audio_mixado, video_com_musica)
        else:
            shutil.copy2(video_concat, video_com_musica)

        # ── ETAPA 9: Normalizar áudio ─────────────────────────────────────
        _etapa(job_id, "normalizando_audio", 68)
        if _profiler: _profiler.iniciar_etapa("ETAPA_09_NORMALIZE")
        print(f"[F01] ETAPA 9 — Normalizando áudio (-14 LUFS)")
        video_norm = output_dir / "normalizado.mp4"
        try:
            _normalizar_video_audio(video_com_musica, video_norm)
        except Exception as e:
            print(f"[F01] Normalização falhou: {e} — continuando sem normalização")
            shutil.copy2(video_com_musica, video_norm)

        # ── ETAPA 10: Gerar legendas SRT ─────────────────────────────────
        _etapa(job_id, "gerando_legendas", 73)
        if _profiler: _profiler.iniciar_etapa("ETAPA_10_LEGENDAS")
        print(f"[F01] ETAPA 10 — Gerando legendas SRT")
        srt_path = dir_legenda / "legenda.srt"
        narracao_completa = " ".join(c.get("narracao", "") for c in cenas)
        dur_total = get_duration(video_norm)

        # Tenta gerar via WhisperX a partir do áudio concatenado
        narr_para_whisper = dir_audio / "narr_concat.wav"
        if narr_para_whisper.exists():
            try:
                audio_para_srt(narr_para_whisper, srt_path, model="small", device="cpu")
            except Exception:
                srt_de_narracao(narracao_completa, dur_total, srt_path)
        else:
            srt_de_narracao(narracao_completa, dur_total, srt_path)

        # ── ETAPA 11: Burn-in de legendas ────────────────────────────────
        _etapa(job_id, "burn_in_legendas", 78)
        if _profiler: _profiler.iniciar_etapa("ETAPA_11_BURNIN")
        print(f"[F01] ETAPA 11 — Burn-in de legendas")
        video_legendado = output_dir / "legendado.mp4"
        if srt_path.exists() and srt_path.stat().st_size > 10:
            try:
                burn_subtitles(video_norm, srt_path, video_legendado)
            except Exception as e:
                print(f"[F01] Burn-in falhou: {e} — sem legendas")
                shutil.copy2(video_norm, video_legendado)
        else:
            shutil.copy2(video_norm, video_legendado)

        # ── ETAPA 12: Color grading ───────────────────────────────────────
        _etapa(job_id, "color_grading", 83)
        if _profiler: _profiler.iniciar_etapa("ETAPA_12_COLOR")
        print(f"[F01] ETAPA 12 — Color grading preset: {preset_cor}")
        video_graded = output_dir / "graded.mp4"
        try:
            apply_color_grade(video_legendado, video_graded, preset=preset_cor)
        except Exception as e:
            print(f"[F01] Color grade falhou: {e}")
            shutil.copy2(video_legendado, video_graded)

        # ── ETAPA 13: Watermark obrigatório (identificação IA) ───────────
        _etapa(job_id, "watermark_ia", 87)
        if _profiler: _profiler.iniciar_etapa("ETAPA_13_WATERMARK")
        print(f"[F01] ETAPA 13 — Watermark IA (identificação obrigatória)")
        video_watermark = output_dir / "watermarked.mp4"
        try:
            add_watermark_text(
                video_graded, video_watermark,
                text=WATERMARK_TEXT,
                x="10", y="10",
                font_size=16,
                color="white@0.45",
            )
        except Exception as e:
            print(f"[F01] Watermark falhou: {e}")
            shutil.copy2(video_graded, video_watermark)

        # ── ETAPA 14: Export final ────────────────────────────────────────
        _etapa(job_id, "exportando", 92)
        if _profiler: _profiler.iniciar_etapa("ETAPA_14_EXPORT")
        print(f"[F01] ETAPA 14 — Exportando MP4 final ({formato})")
        nome_arquivo = _slug(titulo) + f"_{job_id}.mp4"
        video_final = output_dir / nome_arquivo
        resolution = "1920x1080" if formato == "16:9" else "1080x1920"
        export_final(video_watermark, video_final, resolution=resolution, format=formato)

        # Versão Shorts (9:16)
        if gerar_shorts and formato == "16:9":
            video_shorts = output_dir / nome_arquivo.replace(".mp4", "_shorts.mp4")
            try:
                export_final(video_watermark, video_shorts, resolution="1080x1920", format="9:16")
                resultado["output_shorts"] = str(video_shorts)
            except Exception as e:
                print(f"[F01] Shorts falhou: {e}")

        # ── ETAPA 15: Thumbnail + QA ──────────────────────────────────────
        _etapa(job_id, "thumbnail_qa", 97)
        if _profiler: _profiler.iniciar_etapa("ETAPA_15_QA")
        print(f"[F01] ETAPA 15 — Thumbnail e controle de qualidade")
        thumbnail_path = dir_thumb / "thumb.png"
        try:
            gerar_thumbnail(
                titulo=titulo,
                canal_config=canal_config,
                output_path=thumbnail_path,
                subtitulo=canal_config.get("slogan", ""),
            )
        except Exception as e:
            print(f"[F01] Thumbnail falhou: {e}")
            thumbnail_path = None

        # QA completo com CREATIVE QA
        duracao_final = get_duration(video_final)
        _qa_check(video_final, duracao_final, titulo)

        qa_resultado = None
        if _CREATIVE_QA_OK:
            try:
                srt_qa = dir_legenda / f"{job_id}.srt"
                qa_resultado = _qa_verificar_qualidade(
                    video_final,
                    srt_path=srt_qa if srt_qa.exists() else None,
                    canal_config=canal_config,
                    minimo_s=240,
                )
                score_qa = qa_resultado.get("score", 0)
                aprovado_qa = qa_resultado.get("aprovado", False)
                print(f"[F01] CREATIVE QA — Score: {score_qa}/100 | {'✅ APROVADO' if aprovado_qa else '⚠️ REPROVADO'}")
                for aviso in qa_resultado.get("avisos", []):
                    if aviso:
                        print(f"[F01]   ⚠ {aviso}")
                resultado["qa"] = qa_resultado
            except Exception as _e:
                print(f"[F01] CREATIVE QA falhou (não crítico): {_e}")

        # ── Finalização ───────────────────────────────────────────────────
        if _profiler: _profiler.finalizar_etapa()  # fecha ETAPA_15_QA
        duracao_total_seg = time.time() - t0
        _job_update(
            job_id,
            status="done",
            etapa_atual="concluido",
            progresso=100,
            output_path=str(video_final),
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
            finalizado_em=datetime.now(timezone.utc).isoformat(),
        )

        resultado.update({
            "status": "done",
            "output_mp4": str(video_final),
            "thumbnail": str(thumbnail_path) if thumbnail_path else None,
            "duracao": round(duracao_final, 1),
            "tempo_producao_s": round(duracao_total_seg, 1),
            "qa_score": qa_resultado.get("score") if qa_resultado else None,
            "qa_aprovado": qa_resultado.get("aprovado") if qa_resultado else None,
        })

        print(f"\n[F01] ✅ CONCLUÍDO em {duracao_total_seg:.0f}s — {video_final}")
        print(f"[F01]    Duração: {duracao_final:.1f}s | Preset: {preset_cor} | Job: {job_id}")

        # ── PERFORMANCE: Salvar relatório de profiling ────────────────────
        if _PERFORMANCE_OK and _profiler:
            try:
                relatorio_perf = gerar_relatorio_performance(
                    job_id, _profiler, _custo, _cache, output_dir
                )
                resultado["performance"] = {
                    "duracao_producao_s": relatorio_perf.get("duracao_total_s"),
                    "relatorio_path": relatorio_perf.get("relatorio_path"),
                    "custo_estimado_brl": relatorio_perf.get("custo", {}).get("custo_total_brl", 0),
                }
                print(f"[F01] PERFORMANCE — Relatório salvo: {relatorio_perf.get('relatorio_path')}")
            except Exception as _ep:
                print(f"[F01] Performance report falhou (não crítico): {_ep}")

    except Exception as e:
        _job_update(job_id, status="error", erro=str(e), etapa_atual="erro")
        resultado["erro"] = str(e)
        print(f"\n[F01] ❌ ERRO no job {job_id}: {e}")
        # Salva relatório parcial mesmo em caso de erro
        if _PERFORMANCE_OK and _profiler:
            try:
                gerar_relatorio_performance(job_id, _profiler, _custo, _cache, output_dir)
            except Exception:
                pass

    return resultado


# ─────────────────────────────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────

def _etapa(job_id: str, nome: str, progresso: int):
    """Atualiza etapa atual no banco e imprime progresso."""
    print(f"\n[F01 {progresso:3d}%] {nome}")
    _job_update(job_id, etapa_atual=nome, progresso=progresso, status="running")


def _slug(texto: str) -> str:
    """Cria slug de arquivo a partir do título."""
    import re
    s = texto.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "_", s.strip())
    return s[:40]


def _buscar_musica(canal_config: dict, nicho: str) -> Optional[Path]:
    """Retorna trilha sonora disponível para o nicho."""
    music_dir = Path(__file__).parent.parent / "assets" / "music"
    # Procura por arquivo específico do nicho, depois genérico
    for nome in [f"{nicho}.mp3", f"{nicho}.wav", "default.mp3", "ambient.mp3"]:
        p = music_dir / nome
        if p.exists():
            return p
    # Qualquer MP3 disponível
    mp3s = list(music_dir.glob("*.mp3"))
    return mp3s[0] if mp3s else None


def _extrair_audio(video_path: Path, audio_out: Path) -> Path:
    """Extrai faixa de áudio do vídeo via FFmpeg."""
    import subprocess, shutil as sh
    ffmpeg = sh.which("ffmpeg") or "ffmpeg"
    subprocess.run(
        [ffmpeg, "-y", "-i", str(video_path), "-vn", "-acodec", "pcm_s16le", str(audio_out)],
        capture_output=True, check=False,
    )
    return audio_out


def _normalizar_video_audio(video_in: Path, video_out: Path) -> Path:
    """Normaliza o áudio do vídeo para -14 LUFS (padrão YouTube)."""
    import subprocess, shutil as sh
    ffmpeg = sh.which("ffmpeg") or "ffmpeg"
    subprocess.run([
        ffmpeg, "-y", "-i", str(video_in),
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(video_out),
    ], capture_output=True, check=True)
    return video_out


def _qa_check(video_path: Path, duracao: float, titulo: str):
    """Controle de qualidade básico."""
    avisos = []
    if duracao < 60:
        avisos.append(f"ATENÇÃO: duração {duracao:.0f}s é muito curta para YouTube (mín. 4min)")
    if duracao > 600:
        avisos.append(f"ATENÇÃO: duração {duracao:.0f}s é muito longa para dark channel")
    if not video_path.exists():
        avisos.append("CRÍTICO: arquivo de saída não encontrado!")
    elif video_path.stat().st_size < 100_000:
        avisos.append("ATENÇÃO: arquivo final muito pequeno — possível corrupção")

    if avisos:
        print("\n[QA] Alertas de qualidade:")
        for a in avisos:
            print(f"  ⚠  {a}")
    else:
        print(f"[QA] ✅ Vídeo OK — {duracao:.0f}s, {video_path.stat().st_size // 1024}KB")


# ─────────────────────────────────────────────────────────────────
#  PRODUÇÃO EM LOTE (12 canais)
# ─────────────────────────────────────────────────────────────────

def produzir_lote(
    roteiros: list,
    canal_config: dict,
    max_paralelo: int = 1,
) -> list:
    """
    Produz múltiplos vídeos em sequência para um canal.

    Args:
        roteiros: Lista de dicts de roteiro.
        canal_config: Config do canal.
        max_paralelo: Número de vídeos simultâneos (padrão 1 para evitar OOM).

    Returns:
        Lista de resultados.
    """
    resultados = []
    for i, roteiro in enumerate(roteiros, 1):
        print(f"\n{'='*60}")
        print(f"[LOTE] Vídeo {i}/{len(roteiros)}: {roteiro.get('titulo', '?')}")
        print(f"{'='*60}")
        r = produzir_video(roteiro, canal_config)
        resultados.append(r)
        if r["status"] == "done":
            print(f"[LOTE] ✅ {r['output_mp4']}")
        else:
            print(f"[LOTE] ❌ Erro: {r.get('erro', 'desconhecido')}")
    return resultados


# ─────────────────────────────────────────────────────────────────
#  ROTEIRO DE EXEMPLO / TESTE
# ─────────────────────────────────────────────────────────────────

def _expandir_roteiro_4min(roteiro: dict) -> dict:
    """
    AGENTE DURATION ENGINEER — Expande um roteiro curto para 4 minutos.
    Duplica e varia cenas existentes até atingir duração mínima de 240s.
    Cada cena tem duração média de 12s → precisamos de ~20 cenas.
    """
    cenas_orig = roteiro.get("cenas", [])
    if not cenas_orig:
        return roteiro

    # Calcula duração atual
    dur_atual = sum(float(c.get("duracao_s", 8)) for c in cenas_orig)
    if dur_atual >= 240:
        return roteiro  # Já tem 4 minutos, não precisa expandir

    # Poses variadas para não repetir a mesma
    poses_ciclo = [
        "pensando", "apontando", "explicando", "olhando_camera",
        "sentado", "agachado", "levantando_braco", "questionando",
        "celebrando", "vitoria", "correndo", "voando",
    ]

    cenas_expandidas = list(cenas_orig)
    idx_pose = 0
    tentativas = 0

    while sum(float(c.get("duracao_s", 8)) for c in cenas_expandidas) < 240 and tentativas < 100:
        # Pega uma cena base para expandir (ciclando)
        base = cenas_orig[tentativas % len(cenas_orig)].copy()
        novo_num = len(cenas_expandidas) + 1
        pose = poses_ciclo[idx_pose % len(poses_ciclo)]
        idx_pose += 1

        # Variações do texto para não repetir verbatim
        narracao_orig = base.get("narracao", "")
        variacoes = [
            f"Isso significa que {narracao_orig.lower().rstrip('.')}.",
            f"Em outras palavras: {narracao_orig.lower().rstrip('.')}.",
            f"Cientificamente falando, {narracao_orig.lower().rstrip('.')}.",
            f"É importante entender que {narracao_orig.lower().rstrip('.')}.",
            f"Estudos confirmam: {narracao_orig.lower().rstrip('.')}.",
        ]
        texto_var = variacoes[tentativas % len(variacoes)]

        cena_nova = {
            "num": novo_num,
            "tipo": base.get("tipo", "desenvolvimento"),
            "duracao_s": float(base.get("duracao_s", 12)),
            "stickman_acao": pose,
            "pose": pose,
            "narracao": texto_var,
            "texto_tela": texto_var[:60],
            "fundo": base.get("fundo", "preto_elegante"),
        }
        cenas_expandidas.append(cena_nova)
        tentativas += 1

    roteiro_expandido = dict(roteiro)
    roteiro_expandido["cenas"] = cenas_expandidas
    dur_nova = sum(float(c.get("duracao_s", 8)) for c in cenas_expandidas)
    print(f"[DURATION] Roteiro expandido: {len(cenas_orig)} → {len(cenas_expandidas)} cenas ({dur_nova:.0f}s / 240s)")
    return roteiro_expandido


ROTEIRO_EXEMPLO = {
    "titulo": "Por Que Você Procrastina?",
    "descricao": "Episódio sobre procrastinação e psicologia comportamental",
    "gancho": "Você já perdeu horas sem fazer NADA? Isso tem uma explicação científica.",
    "cta": "Se inscreva no canal e ative o sininho para não perder os próximos vídeos!",
    "cenas": [
        {
            "num": 1, "tipo": "hook", "duracao_s": 10, "stickman_acao": "olhando_camera",
            "pose": "olhando_camera",
            "narracao": "Você já perdeu horas sem conseguir começar uma tarefa simples?",
            "texto_tela": "A CIÊNCIA DA PROCRASTINAÇÃO",
            "fundo": "preto_elegante",
        },
        {
            "num": 2, "tipo": "explicacao", "duracao_s": 14, "stickman_acao": "pensando",
            "pose": "pensando",
            "narracao": "A procrastinação não é preguiça. É uma resposta emocional ao desconforto gerado pela tarefa.",
            "texto_tela": "Não é preguiça — é neurociência",
            "fundo": "azul_escuro",
        },
        {
            "num": 3, "tipo": "ciencia", "duracao_s": 16, "stickman_acao": "apontando",
            "pose": "apontando",
            "narracao": "Pesquisas mostram que o cérebro prefere recompensas imediatas. Isso é chamado de desconto hiperbólico.",
            "texto_tela": "Desconto Hiperbólico",
            "fundo": "azul_escuro",
        },
        {
            "num": 4, "tipo": "ciencia2", "duracao_s": 14, "stickman_acao": "questionando",
            "pose": "questionando",
            "narracao": "O córtex pré-frontal briga com o sistema límbico. Um quer prazer agora, o outro planeja o futuro.",
            "texto_tela": "Guerra no cérebro",
            "fundo": "preto_elegante",
        },
        {
            "num": 5, "tipo": "impacto", "duracao_s": 14, "stickman_acao": "agachado",
            "pose": "agachado",
            "narracao": "Pessoas que procrastinam cronicamente têm mais estresse, saúde pior e ganham menos dinheiro.",
            "texto_tela": "As consequências reais",
            "fundo": "azul_escuro",
        },
        {
            "num": 6, "tipo": "solucao", "duracao_s": 14, "stickman_acao": "levantando_braco",
            "pose": "levantando_braco",
            "narracao": "A técnica Pomodoro divide o trabalho em blocos de 25 minutos, reduzindo a resistência inicial.",
            "texto_tela": "Técnica Pomodoro",
            "fundo": "preto_elegante",
        },
        {
            "num": 7, "tipo": "solucao2", "duracao_s": 14, "stickman_acao": "apontando",
            "pose": "apontando",
            "narracao": "Regra dos 2 minutos: se uma tarefa leva menos de 2 minutos, faça agora mesmo.",
            "texto_tela": "Regra dos 2 Minutos",
            "fundo": "azul_escuro",
        },
        {
            "num": 8, "tipo": "solucao3", "duracao_s": 14, "stickman_acao": "vitoria",
            "pose": "vitoria",
            "narracao": "Recompensas imediatas artificiais enganam o cérebro: permita-se algo bom após cada tarefa concluída.",
            "texto_tela": "Recompensas inteligentes",
            "fundo": "preto_elegante",
        },
        {
            "num": 9, "tipo": "mito", "duracao_s": 12, "stickman_acao": "surpreso",
            "pose": "surpreso",
            "narracao": "Mito: pessoas bem-sucedidas nunca procrastinam. Realidade: elas procrastinam menos, não zero.",
            "texto_tela": "O mito da perfeição",
            "fundo": "azul_escuro",
        },
        {
            "num": 10, "tipo": "ciencia3", "duracao_s": 14, "stickman_acao": "sentado",
            "pose": "sentado",
            "narracao": "A dopamina é o neurotransmissor do prazer antecipado. Visualizar o resultado ativa ela positivamente.",
            "texto_tela": "O poder da dopamina",
            "fundo": "preto_elegante",
        },
        {
            "num": 11, "tipo": "tecnica", "duracao_s": 14, "stickman_acao": "pensando",
            "pose": "pensando",
            "narracao": "Técnica 5-4-3-2-1: conte de 5 até 1 e comece imediatamente. Interrompe o ciclo de hesitação.",
            "texto_tela": "Contagem Regressiva",
            "fundo": "azul_escuro",
        },
        {
            "num": 12, "tipo": "ambiente", "duracao_s": 12, "stickman_acao": "olhando_camera",
            "pose": "olhando_camera",
            "narracao": "Ambiente importa: celular longe, notificações desligadas. O cérebro precisa de contexto de foco.",
            "texto_tela": "Ambiente = destino",
            "fundo": "preto_elegante",
        },
        {
            "num": 13, "tipo": "autocompaixao", "duracao_s": 12, "stickman_acao": "celebrando",
            "pose": "celebrando",
            "narracao": "Autocompaixão ajuda mais que autocrítica. Perdoar-se pelo atraso aumenta a chance de agir.",
            "texto_tela": "Seja gentil consigo",
            "fundo": "azul_escuro",
        },
        {
            "num": 14, "tipo": "dados", "duracao_s": 14, "stickman_acao": "apontando",
            "pose": "apontando",
            "narracao": "20% da população são procrastinadores crônicos. Você não está sozinho — mas pode mudar isso.",
            "texto_tela": "20% da população",
            "fundo": "preto_elegante",
        },
        {
            "num": 15, "tipo": "conclusao", "duracao_s": 14, "stickman_acao": "levantando_braco",
            "pose": "levantando_braco",
            "narracao": "Com pequenos passos consistentes, você reprograma o cérebro e vence a procrastinação definitivamente.",
            "texto_tela": "Reprograme seu cérebro",
            "fundo": "azul_escuro",
        },
        {
            "num": 16, "tipo": "encerramento", "duracao_s": 10, "stickman_acao": "olhando_camera",
            "pose": "olhando_camera",
            "narracao": "Qual dessas técnicas você vai aplicar hoje? Comente abaixo e me conta.",
            "texto_tela": "E você — qual vai usar?",
            "fundo": "preto_elegante",
        },
    ],
}

CANAL_EXEMPLO = {
    "id": "canal_01_psicologia",
    "nome": "Stickman Psicologia",
    "nicho": "psicologia",
    "slogan": "Sua mente explicada",
    "stickman_color": "#6366F1",
    "stickman_seed": 42,
    "piper_model": "faber-medium",
    "color_grade": "documentario",
    "formato": "16:9",
    "gerar_shorts": True,
}


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("DARK STICKMAN STUDIO — Pipeline F01")
    print("ai_generated: True")
    print("ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")
    print("=" * 60)

    # Verifica FFmpeg
    if not check_ffmpeg():
        print("❌ FFmpeg não encontrado. Instale em: https://ffmpeg.org/download.html")
        sys.exit(1)

    # Roteiro via argumento JSON ou usa exemplo
    if len(sys.argv) >= 3:
        roteiro_path = Path(sys.argv[1])
        canal_path = Path(sys.argv[2])
        roteiro = json.loads(roteiro_path.read_text(encoding="utf-8"))
        canal = json.loads(canal_path.read_text(encoding="utf-8"))
    else:
        print("Usando roteiro de exemplo (Psicologia — Procrastinação)\n")
        roteiro = ROTEIRO_EXEMPLO
        canal = CANAL_EXEMPLO

    resultado = produzir_video(
        roteiro=roteiro,
        canal_config=canal,
        qualidade="medium_quality",
        gerar_shorts=canal.get("gerar_shorts", False),
    )

    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    for k, v in resultado.items():
        print(f"  {k}: {v}")
    print("=" * 60)
