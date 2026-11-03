"""
DARK STUDIO AAA — Recompilação de Shorts com Áudio Real
Substitui áudio silent pelos MP3s do ElevenLabs e gera MP4s finais.

USO:
  python recompilar_com_audio.py

REQUISITO:
  Colocar os MP3s em outputs/audio/ com os nomes:
    short1_narration.mp3  → Mente de Aço
    short2_narration.mp3  → Intelligentia Nova
    short3_narration.mp3  → Bastidores do Tempo
    short4_narration.mp3  → Projeto Secreto
    short5_narration.mp3  → AquaZen Relax

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

BASE = Path("/home/claude/dark-stickman-studio")
AUDIO_DIR = BASE / "outputs/audio"
VIDEO_DIR = BASE / "outputs/videos"
THUMB_DIR = BASE / "outputs/thumbnails"

SHORTS = [
    {
        "id": "short1",
        "canal": "Mente_de_Aco",
        "dur": 32,
        "audio_real": "short1_narration.mp3",
        "audio_silent": "short1_silent.mp3",
        "thumb": "thumb_1634b955_por_que_você_nunca_executa_seu.jpg",
        "out": "short1_Mente_de_Aco_FINAL.mp4",
    },
    {
        "id": "short2",
        "canal": "Intelligentia_Nova",
        "dur": 37,
        "audio_real": "short2_narration.mp3",
        "audio_silent": "short2_silent.mp3",
        "thumb": "thumb_4d7b1b20_a_ia_que_prevê_sua_morte_antes.jpg",
        "out": "short2_Intelligentia_Nova_FINAL.mp4",
    },
    {
        "id": "short3",
        "canal": "Bastidores_do_Tempo",
        "dur": 35,
        "audio_real": "short3_narration.mp3",
        "audio_silent": "short3_silent.mp3",
        "thumb": "thumb_b6e78d75_por_que_roma_escondeu_este_seg.jpg",
        "out": "short3_Bastidores_do_Tempo_FINAL.mp4",
    },
    {
        "id": "short4",
        "canal": "Projeto_Secreto",
        "dur": 40,
        "audio_real": "short4_narration.mp3",
        "audio_silent": "short4_silent.mp3",
        "thumb": "thumb_27018b80_por_que_o_governo_lavou_cérebr.jpg",
        "out": "short4_Projeto_Secreto_FINAL.mp4",
    },
    {
        "id": "short5",
        "canal": "AquaZen_Relax",
        "dur": 30,
        "audio_real": "short5_narration.mp3",
        "audio_silent": "short5_silent.mp3",
        "thumb": "thumb_ff3b6fd6_você_nunca_dormiu_tão_bem_quan.jpg",
        "out": "short5_AquaZen_Relax_FINAL.mp4",
    },
]


def get_audio_duration(mp3_path: str) -> float:
    """Obtém duração real do MP3 via ffprobe"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", mp3_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def recompilar(s: dict) -> dict:
    """Recompila Short com áudio real do ElevenLabs"""
    nome = s["id"]
    canal = s["canal"]

    # Selecionar áudio (real ou silent como fallback)
    audio_real = AUDIO_DIR / s["audio_real"]
    audio_silent = AUDIO_DIR / s["audio_silent"]

    if audio_real.exists() and audio_real.stat().st_size > 1000:
        audio = str(audio_real)
        dur_audio = get_audio_duration(audio)
        dur = max(dur_audio + 1, float(s["dur"]))  # +1s padding
        tipo_audio = "NARRAÇÃO REAL (ElevenLabs)"
    elif audio_silent.exists():
        audio = str(audio_silent)
        dur = float(s["dur"])
        tipo_audio = "SILENT (placeholder)"
    else:
        print(f"  ✗ {nome}: nenhum áudio encontrado")
        return {"id": nome, "status": "sem_audio"}

    # Selecionar thumbnail
    thumb = THUMB_DIR / s["thumb"]
    if not thumb.exists():
        thumbs = sorted(THUMB_DIR.glob("*.jpg"), key=lambda p: p.stat().st_size, reverse=True)
        if not thumbs:
            print(f"  ✗ {nome}: nenhuma thumbnail")
            return {"id": nome, "status": "sem_thumb"}
        thumb = thumbs[0]
        print(f"  ⚠ usando thumb fallback: {thumb.name}")

    out = VIDEO_DIR / s["out"]
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n▶  {nome} — {canal}")
    print(f"   Áudio: {tipo_audio}")
    print(f"   Duração: {dur:.1f}s")

    # Compor MP4: thumbnail loop + áudio real
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(thumb),
        "-i", audio,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(dur),
        "-r", "30", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if result.returncode == 0 and out.exists() and out.stat().st_size > 10000:
        mb = out.stat().st_size / (1024 * 1024)
        print(f"   ✅ {out.name} — {mb:.1f} MB")
        return {
            "id": nome, "canal": canal,
            "status": "OK",
            "audio_tipo": tipo_audio,
            "arquivo": str(out),
            "duracao_s": round(dur, 1),
            "tamanho_mb": round(mb, 2),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }
    else:
        err = result.stderr[-300:] if result.stderr else "?"
        print(f"   ✗ FFmpeg erro: {err[-150:]}")
        return {"id": nome, "status": "erro", "log": err[-150:]}


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK STUDIO AAA — Recompilação com Áudio Real      ║")
    print("║   Pipeline: Thumbnail + Narração → MP4 1080x1920     ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    # Listar áudios disponíveis
    print("Áudios encontrados:")
    for f in sorted(AUDIO_DIR.glob("*.mp3")):
        kb = f.stat().st_size / 1024
        dur = get_audio_duration(str(f))
        print(f"  {f.name} — {kb:.0f} KB — {dur:.1f}s")

    resultados = []
    for s in SHORTS:
        r = recompilar(s)
        resultados.append(r)

    ok = sum(1 for r in resultados if r.get("status") == "OK")
    print(f"\n{'═'*55}")
    print(f"  RESULTADO: {ok}/{len(SHORTS)} Shorts recompilados")
    for r in resultados:
        icon = "✅" if r.get("status") == "OK" else "❌"
        tipo = r.get("audio_tipo", r.get("status", "?"))
        print(f"  {icon} {r['id']} — {tipo}")
    print(f"{'═'*55}")

    # Salvar relatório
    rel = {
        "gerado_em": datetime.now().isoformat(),
        "total": len(resultados), "ok": ok,
        "videos": resultados,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "instrucoes_upload": "Ver producao/semana_01_nov_2026/guia_upload_youtube.md"
    }
    rel_path = BASE / "producao/semana_01_nov_2026/relatorio_recompilacao.json"
    with open(rel_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=2)
    print(f"\n  Relatório: {rel_path}")
    print(f"  Vídeos FINAL em: {VIDEO_DIR}\n")
