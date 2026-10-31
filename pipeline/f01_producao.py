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
from datetime import datetime
from pathlib import Path
from typing import Optional

# Imports dos módulos core
from core.piper_tts import narrar_roteiro, get_audio_duration
from core.manim_scene import render_roteiro, render_intro_hook, render_outro_cta
from core.ffmpeg_utils import (
    concat_videos, add_audio, mix_audio, normalize_audio,
    burn_subtitles, add_watermark_text, apply_color_grade, export_final,
    get_duration, check_ffmpeg,
)
from core.legenda import pipeline_legenda, audio_para_srt, srt_de_narracao
from core.thumbnail import gerar_thumbnail, gerar_variacao

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
    """Inicializa o banco de dados SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
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


def _job_update(job_id: str, **kwargs):
    """Atualiza campos de um job no banco."""
    if not DB_PATH.exists():
        return
    campos = ", ".join(f"{k} = ?" for k in kwargs)
    valores = list(kwargs.values()) + [job_id]
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(f"UPDATE jobs SET {campos} WHERE id = ?", valores)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Falha ao atualizar job {job_id}: {e}")


def _job_criar(job_id: str, canal_id: str, titulo: str):
    """Registra um novo job no banco."""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            "INSERT INTO jobs (id, canal_id, titulo, status, criado_em) VALUES (?, ?, ?, 'running', ?)",
            (job_id, canal_id, titulo, datetime.utcnow().isoformat()),
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
        audios_narracao = narrar_roteiro(cenas, dir_audio, model=modelo_piper)

        # ── ETAPA 3: Intro/Hook ──────────────────────────────────────────
        _etapa(job_id, "renderizando_hook", 20)
        print(f"[F01] ETAPA 3 — Intro/Hook")
        gancho_texto = roteiro.get("gancho", cenas[0].get("narracao", titulo) if cenas else titulo)
        clip_hook = render_intro_hook(canal_config, gancho_texto, dir_clips / "hook.mp4")

        # ── ETAPA 4: Renderizar cenas com Manim ─────────────────────────
        _etapa(job_id, "renderizando_cenas", 30)
        print(f"[F01] ETAPA 4 — Renderizando {len(cenas)} cenas com Manim")
        clips_cenas = render_roteiro(cenas, dir_clips, canal_config, quality=qualidade)

        # ── ETAPA 5: Outro/CTA ───────────────────────────────────────────
        _etapa(job_id, "renderizando_outro", 45)
        print(f"[F01] ETAPA 5 — Outro/CTA")
        cta_texto = roteiro.get("cta", f"Se inscreva no canal {canal_config.get('nome', '')}!")
        clip_outro = render_outro_cta(canal_config, cta_texto, dir_clips / "outro.mp4")

        # ── ETAPA 6: Adicionar narração em cada cena ─────────────────────
        _etapa(job_id, "sincronizando_audio", 50)
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
            raise RuntimeError("Nenhum clip válido gerado. Verifique a instalação do Manim.")

        video_concat = output_dir / "concat.mp4"
        if len(todos_clips) == 1:
            shutil.copy2(todos_clips[0], video_concat)
        else:
            concat_videos(todos_clips, video_concat, transition="dissolve", transition_dur=0.4)

        # ── ETAPA 8: Mixar trilha sonora ──────────────────────────────────
        _etapa(job_id, "mixando_audio", 63)
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
        print(f"[F01] ETAPA 9 — Normalizando áudio (-14 LUFS)")
        video_norm = output_dir / "normalizado.mp4"
        try:
            _normalizar_video_audio(video_com_musica, video_norm)
        except Exception as e:
            print(f"[F01] Normalização falhou: {e} — continuando sem normalização")
            shutil.copy2(video_com_musica, video_norm)

        # ── ETAPA 10: Gerar legendas SRT ─────────────────────────────────
        _etapa(job_id, "gerando_legendas", 73)
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
        print(f"[F01] ETAPA 12 — Color grading preset: {preset_cor}")
        video_graded = output_dir / "graded.mp4"
        try:
            apply_color_grade(video_legendado, video_graded, preset=preset_cor)
        except Exception as e:
            print(f"[F01] Color grade falhou: {e}")
            shutil.copy2(video_legendado, video_graded)

        # ── ETAPA 13: Watermark obrigatório (identificação IA) ───────────
        _etapa(job_id, "watermark_ia", 87)
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

        # QA básico
        duracao_final = get_duration(video_final)
        _qa_check(video_final, duracao_final, titulo)

        # ── Finalização ───────────────────────────────────────────────────
        duracao_total_seg = time.time() - t0
        _job_update(
            job_id,
            status="done",
            etapa_atual="concluido",
            progresso=100,
            output_path=str(video_final),
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
            finalizado_em=datetime.utcnow().isoformat(),
        )

        resultado.update({
            "status": "done",
            "output_mp4": str(video_final),
            "thumbnail": str(thumbnail_path) if thumbnail_path else None,
            "duracao": round(duracao_final, 1),
            "tempo_producao_s": round(duracao_total_seg, 1),
        })

        print(f"\n[F01] ✅ CONCLUÍDO em {duracao_total_seg:.0f}s — {video_final}")
        print(f"[F01]    Duração: {duracao_final:.1f}s | Preset: {preset_cor} | Job: {job_id}")

    except Exception as e:
        _job_update(job_id, status="error", erro=str(e), etapa_atual="erro")
        resultado["erro"] = str(e)
        print(f"\n[F01] ❌ ERRO no job {job_id}: {e}")

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

ROTEIRO_EXEMPLO = {
    "titulo": "Por Que Você Procrastina?",
    "descricao": "Episódio sobre procrastinação e psicologia comportamental",
    "gancho": "Você já perdeu horas sem fazer NADA? Isso tem uma explicação científica.",
    "cta": "Se inscreva no canal e ative o sininho para não perder os próximos vídeos!",
    "cenas": [
        {
            "num": 1, "tipo": "hook",
            "duracao_s": 8, "stickman_acao": "olhando_camera",
            "narracao": "Você já perdeu horas sem conseguir começar uma tarefa simples?",
            "fundo": "preto_elegante",
        },
        {
            "num": 2, "tipo": "explicacao",
            "duracao_s": 15, "stickman_acao": "pensando",
            "narracao": "A procrastinação não é preguiça. É uma resposta emocional ao desconforto gerado pela tarefa.",
            "fundo": "azul_escuro",
        },
        {
            "num": 3, "tipo": "ciencia",
            "duracao_s": 20, "stickman_acao": "apontando",
            "narracao": "Pesquisas mostram que o cérebro prefere recompensas imediatas. Isso é chamado de desconto hiperbólico.",
            "fundo": "azul_escuro",
        },
        {
            "num": 4, "tipo": "solucao",
            "duracao_s": 18, "stickman_acao": "vitoria",
            "narracao": "A técnica Pomodoro divide o trabalho em blocos de 25 minutos, reduzindo a resistência inicial.",
            "fundo": "preto_elegante",
        },
        {
            "num": 5, "tipo": "conclusao",
            "duracao_s": 12, "stickman_acao": "olhando_camera",
            "narracao": "Com pequenos passos consistentes, você vence a procrastinação definitivamente.",
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
