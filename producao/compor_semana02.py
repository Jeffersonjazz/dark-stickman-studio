"""
DARK STUDIO AAA — Composição de Shorts Semana 02
Pipeline: Thumbnail + Silent Audio → MP4 1080x1920
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import subprocess, json
from pathlib import Path
from datetime import datetime

BASE = Path("/home/claude/dark-stickman-studio")
THUMB_DIR = BASE / "outputs/thumbnails"
AUDIO_DIR = BASE / "outputs/audio"
OUT_DIR = BASE / "outputs/videos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SHORTS_S02 = [
    {"id": "s02_short1", "canal": "Esquina_do_Medo",   "dur": 38,
     "thumb": "s02_thumb_5d631686_o_fenômeno_de_dyatlov.jpg"},
    {"id": "s02_short2", "canal": "Horizonte_Cosmico",  "dur": 35,
     "thumb": "s02_thumb_76346198_o_objeto_mais_brilhante_do_uni.jpg"},
    {"id": "s02_short3", "canal": "Mestre_do_Oculto",   "dur": 36,
     "thumb": "s02_thumb_b2c93240_kryptos.jpg"},
    {"id": "s02_short4", "canal": "Raizes_da_Terra",     "dur": 33,
     "thumb": "s02_thumb_d34e0484_o_maior_ser_vivo_da_terra.jpg"},
    {"id": "s02_short5", "canal": "Pulso_Digital",       "dur": 38,
     "thumb": "s02_thumb_04c689fa_o_chip_que_vai_substituir_o_sm.jpg"},
]

resultados = []
for s in SHORTS_S02:
    nome = s["id"]
    thumb = THUMB_DIR / s["thumb"]
    dur = s["dur"]
    audio = AUDIO_DIR / f"{nome}_silent.mp3"
    out = OUT_DIR / f"{nome}_{s['canal']}.mp4"

    print(f"\n▶  {nome} — {s['canal']} ({dur}s)")

    # Gerar silent
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", str(dur), "-q:a", "9", "-acodec", "libmp3lame", str(audio)
    ], capture_output=True)

    # Thumb fallback
    if not thumb.exists():
        thumbs = sorted(THUMB_DIR.glob("*.jpg"), key=lambda p: p.stat().st_size, reverse=True)
        thumb = thumbs[0] if thumbs else None
    if not thumb:
        print("  ✗ sem thumb"); resultados.append({"id": nome, "status": "sem_thumb"}); continue

    r = subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(thumb),
        "-i", str(audio),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "96k",
        "-t", str(dur), "-r", "24", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out)
    ], capture_output=True, text=True, timeout=120)

    if r.returncode == 0 and out.exists() and out.stat().st_size > 10000:
        mb = out.stat().st_size / 1024 / 1024
        print(f"  ✅ {out.name} — {mb:.1f} MB")
        resultados.append({
            "id": nome, "canal": s["canal"], "dur": dur,
            "arquivo": str(out), "mb": round(mb, 2),
            "status": "COMPOSTO",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        })
    else:
        err = r.stderr[-200:] if r.stderr else "?"
        print(f"  ✗ erro: {err[-80:]}")
        resultados.append({"id": nome, "status": "erro"})

ok = sum(1 for r in resultados if r.get("status") == "COMPOSTO")
print(f"\n{'═'*52}")
print(f"  SEMANA 02: {ok}/{len(SHORTS_S02)} Shorts compostos")
for r in resultados:
    icon = "✅" if r.get("status") == "COMPOSTO" else "❌"
    print(f"  {icon} {r['id']} — {r.get('status')} {r.get('mb','')}")
print(f"{'═'*52}")

rel = Path("producao/semana_02_nov_2026/relatorio_s02.json")
rel.parent.mkdir(parents=True, exist_ok=True)
with open(rel, "w", encoding="utf-8") as f:
    json.dump({"gerado_em": datetime.now().isoformat(), "ok": ok, "total": len(SHORTS_S02),
               "videos": resultados, "ai_generated": True,
               "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}, f, indent=2)
