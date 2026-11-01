#!/usr/bin/env python3
"""VIDEO EDITOR PRO — Montagem Short S004 — Dark Arquivo
Formato: 1080x1920 · 9:16 · 50s · YouTube Shorts
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA
"""
import subprocess, json, sys
from pathlib import Path

SHORT_DIR  = Path(__file__).parent
AUDIO_DIR  = SHORT_DIR / "audio"
IMG_DIR    = SHORT_DIR / "imagens"
OUTPUT_DIR = SHORT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLOR_GRADE = "colorbalance=rs=-0.1:gs=0.1:bs=-0.1:rm=0:gm=0.05:bm=0,eq=contrast=1.25:brightness=-0.1"
CANAL       = "Dark Arquivo"
SHORT_ID    = "S004"
DURACAO_S   = 50

# Ken Burns vertical 9:16 (1080x1920)
KEN_BURNS_V = (
    "zoompan=z='min(zoom+0.0006,1.3)':"
    "d=90:"
    "x='iw/2-(iw/zoom/2)':"
    "y='ih/4-(ih/zoom/4)':"
    "s=1080x1920"
)

# Textos overlay
HOOK_TEXT = "Em 2013, o DOJ tentou deletar este arquivo. Não conseguiu."
CANAL_TAG  = "Dark Arquivo"
CTA_TEXT   = "O que eles não querem que você saiba? Comenta abai"

drawtext_filters = (
    # Watermark canal
    f"drawtext=text={CANAL_TAG!r}:fontsize=22:fontcolor=white@0.8:"
    f"x=w-tw-20:y=20:shadowcolor=black:shadowx=1:shadowy=1:enable='gte(t,2)',"
    # CTA final
    f"drawtext=text={CTA_TEXT!r}:fontsize=34:fontcolor=white:"
    f"x=(w-tw)/2:y=h*0.78:shadowcolor=black:shadowx=2:shadowy=2:"
    f"enable='between(t,38,50)'"
)

# Áudio
mp3_files = sorted(AUDIO_DIR.glob("*.mp3"))

if not mp3_files:
    print("⚠️ Nenhum áudio — usando silêncio como placeholder")
    # Gera silêncio
    silencio = OUTPUT_DIR / "silencio.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"anullsrc=r=44100:cl=mono", "-t", str(DURACAO_S),
        str(silencio)
    ], capture_output=True)
    narration = silencio
else:
    narration = mp3_files[0]
    print(f"🎵 Áudio: {narration.name}")

# Imagens
imagens = sorted(list(IMG_DIR.glob("*.png")) + list(IMG_DIR.glob("*.jpg"))) if IMG_DIR.exists() else []

if imagens:
    print(f"🖼️  {len(imagens)} imagens encontradas")
    img_list = OUTPUT_DIR / "images_short.txt"
    with open(img_list, "w") as f:
        dur_img = max(3, DURACAO_S // len(imagens))
        for img in imagens:
            f.write(f"file \'{img}\'\n")
            f.write(f"duration {dur_img}\n")

    video_path = OUTPUT_DIR / f"{SHORT_ID}_short_final.mp4"
    vf_chain = f"{KEN_BURNS_V},{COLOR_GRADE},{drawtext_filters}"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(img_list),
        "-i", str(narration),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(DURACAO_S),
        "-shortest", "-pix_fmt", "yuv420p",
        str(video_path)
    ]
else:
    print("⚠️ Sem imagens — gerando placeholder preto vertical")
    video_path = OUTPUT_DIR / f"{SHORT_ID}_short_audio_only.mp4"
    vf_chain = f"scale=1080:1920,{COLOR_GRADE},{drawtext_filters}"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1080x1920:r=30",
        "-i", str(narration),
        "-vf", vf_chain,
        "-c:v", "libx264", "-crf", "28", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(DURACAO_S),
        "-shortest", "-pix_fmt", "yuv420p",
        str(video_path)
    ]

result = subprocess.run(cmd, capture_output=True)
if result.returncode == 0:
    size_mb = video_path.stat().st_size / 1024 / 1024
    print(f"✅ Short gerado: {video_path.name} ({size_mb:.1f} MB)")
else:
    print(f"⚠️ Erro FFmpeg: {result.stderr.decode()[:300]}")

relatorio = {
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    "short_id": SHORT_ID,
    "canal": CANAL,
    "color_grade": "shadow_conspiracy_green",
    "formato": "1080x1920 9:16",
    "duracao_alvo_s": DURACAO_S,
    "imagens_usadas": len(imagens),
    "audio": str(narration.name),
    "output": str(video_path)
}
(OUTPUT_DIR / "relatorio_montagem_short.json").write_text(
    __import__("json").dumps(relatorio, ensure_ascii=False, indent=2))
print(f"📋 Relatório: output/relatorio_montagem_short.json")
