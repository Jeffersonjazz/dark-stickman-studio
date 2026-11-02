"""
DARK STUDIO AAA — Composição Rápida de Shorts
Pipeline simplificado: Thumbnail + Silent Audio → MP4 1080x1920
SEM drawtext (mais rápido, menos dependências de font)
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import subprocess, os, json
from pathlib import Path
from datetime import datetime

SHORTS = [
    {"id": "short1", "canal": "Mente_de_Aco",       "dur": 32,
     "titulo": "Por Que Voce Nunca Executa Seus Planos",
     "thumb": "outputs/thumbnails/thumb_1634b955_por_que_você_nunca_executa_seu.jpg"},
    {"id": "short2", "canal": "Intelligentia_Nova",   "dur": 37,
     "titulo": "A IA Que Preve Sua Morte Antes de Voce Saber",
     "thumb": "outputs/thumbnails/thumb_4d7b1b20_a_ia_que_prevê_sua_morte_antes.jpg"},
    {"id": "short3", "canal": "Bastidores_do_Tempo",  "dur": 35,
     "titulo": "Por Que Roma Escondeu Este Segredo por 1500 Anos",
     "thumb": "outputs/thumbnails/thumb_b6e78d75_por_que_roma_escondeu_este_seg.jpg"},
    {"id": "short4", "canal": "Projeto_Secreto",      "dur": 40,
     "titulo": "Por Que o Governo Lavou Cerebros de Cidadaos Reais",
     "thumb": "outputs/thumbnails/thumb_27018b80_por_que_o_governo_lavou_cérebr.jpg"},
    {"id": "short5", "canal": "AquaZen_Relax",        "dur": 30,
     "titulo": "Voce NUNCA Dormiu Tao Bem Com Estes Sons da Natureza",
     "thumb": "outputs/thumbnails/thumb_ff3b6fd6_você_nunca_dormiu_tão_bem_quan.jpg"},
]

OUT = Path("outputs/videos")
AUD = Path("outputs/audio")
OUT.mkdir(parents=True, exist_ok=True)
AUD.mkdir(parents=True, exist_ok=True)

resultados = []

for s in SHORTS:
    nome = s["id"]
    thumb = s["thumb"]
    dur = s["dur"]
    out_mp4 = OUT / f"{nome}_{s['canal']}.mp4"
    audio = AUD / f"{nome}_silent.mp3"

    print(f"\n▶  {nome} — {s['canal']} ({dur}s)")

    # 1) Verificar thumbnail
    if not os.path.exists(thumb):
        fallbacks = list(Path("outputs/thumbnails").glob("*.jpg"))
        if fallbacks:
            thumb = str(sorted(fallbacks, key=lambda p: p.stat().st_size, reverse=True)[0])
            print(f"   ⚠ fallback: {Path(thumb).name}")
        else:
            print("   ✗ sem thumbnail"); resultados.append({"id": nome, "status": "sem_thumb"}); continue

    # 2) Gerar áudio silent
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", str(dur), "-q:a", "9", "-acodec", "libmp3lame", str(audio)
    ], capture_output=True)
    if r.returncode != 0:
        print("   ✗ áudio falhou"); resultados.append({"id": nome, "status": "audio_falhou"}); continue
    print(f"   ✓ áudio silent: {audio.name}")

    # 3) Compor MP4: thumbnail vertical + áudio
    # Filtro simples: escalar para 1080x1920 (crop de cima)
    r2 = subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", thumb,
        "-i", str(audio),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "96k",
        "-t", str(dur), "-r", "24", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_mp4)
    ], capture_output=True, text=True, timeout=120)

    if r2.returncode == 0 and out_mp4.exists() and out_mp4.stat().st_size > 10000:
        mb = out_mp4.stat().st_size / (1024*1024)
        print(f"   ✓ {out_mp4.name} — {mb:.1f} MB")
        resultados.append({
            "id": nome, "canal": s["canal"], "dur": dur,
            "arquivo": str(out_mp4), "mb": round(mb, 2),
            "status": "COMPOSTO",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "nota_upload": f"Título YouTube: {s['titulo']}"
        })
    else:
        err = r2.stderr[-300:] if r2.stderr else "?"
        print(f"   ✗ FFmpeg falhou: {err[-100:]}")
        resultados.append({"id": nome, "status": "erro", "log": err[-100:]})

# Relatório
rel_path = Path("producao/semana_01_nov_2026/relatorio_composicao.json")
rel_path.parent.mkdir(parents=True, exist_ok=True)
with open(rel_path, "w", encoding="utf-8") as f:
    json.dump({
        "gerado_em": datetime.now().isoformat(),
        "total": len(resultados),
        "compostos": sum(1 for r in resultados if r.get("status") == "COMPOSTO"),
        "videos": resultados,
        "proximo_passo": "Upload manual no YouTube Studio ou via YouTube Data API v3",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }, f, ensure_ascii=False, indent=2)

print(f"\n{'═'*52}")
ok = sum(1 for r in resultados if r.get("status") == "COMPOSTO")
print(f"  RESULTADO: {ok}/{len(SHORTS)} Shorts compostos")
for r in resultados:
    icon = "✅" if r.get("status") == "COMPOSTO" else "❌"
    print(f"  {icon} {r['id']} — {r.get('status')} {r.get('mb','')}")
print(f"{'═'*52}")
print(f"  Vídeos em: {OUT.absolute()}")
