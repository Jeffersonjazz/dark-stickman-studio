#!/usr/bin/env python3
"""VIDEO EDITOR PRO — Montagem Ken Burns — V005
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA
"""
import subprocess, json, sys
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
AUDIO_DIR = VIDEO_DIR / "audio"
IMAGENS_DIR = VIDEO_DIR / "imagens"
OUTPUT_DIR = VIDEO_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuração de color grade
COLOR_GRADES = {
    "teal_orange_psicologia": "eq=contrast=1.1:brightness=-0.05:saturation=0.9,colorbalance=rs=-0.1:gs=0:bs=0.15:rm=0:gm=0:bm=0",
    "sepia_vintage_noir": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.2:brightness=-0.1",
    "tech_blue_clinical": "colorbalance=rs=-0.2:gs=-0.1:bs=0.3:rm=0:gm=0:bm=0.1,eq=contrast=1.15:saturation=0.85",
    "shadow_conspiracy_green": "colorbalance=rs=-0.1:gs=0.1:bs=-0.1:rm=0:gm=0.05:bm=0,eq=contrast=1.25:brightness=-0.1",
    "forest_green_gold": "colorbalance=rs=0:gs=0.1:bs=-0.15:rm=0:gm=0.05:bm=-0.1,eq=contrast=1.1:saturation=1.1"
}

GRADE_FILTRO = COLOR_GRADES.get("forest_green_gold", COLOR_GRADES["teal_orange_psicologia"])
TITULO = "A Floresta Que Respira"

mp3_files = sorted(AUDIO_DIR.glob("*.mp3"))
if not mp3_files:
    print("⚠️ Nenhum arquivo de áudio encontrado")
    sys.exit(1)

print(f"🎬 VIDEO EDITOR PRO — {len(mp3_files)} cenas de áudio")

# Etapa 1: Concatenar narração
concat_list = OUTPUT_DIR / "concat_audio.txt"
with open(concat_list, "w") as f:
    for mp3 in mp3_files:
        f.write(f"file \'{mp3}\'\n")

narration_combined = OUTPUT_DIR / "narracao_completa.mp3"
cmd_concat = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy", str(narration_combined)
]
result = subprocess.run(cmd_concat, capture_output=True)
if result.returncode == 0:
    print(f"✅ Narração concatenada: {narration_combined.name}")
else:
    print(f"⚠️ Concat falhou: {result.stderr.decode()[:200]}")
    narration_combined = mp3_files[0]

# Etapa 2: Verificar imagens ou usar placeholder
imagens = list(IMAGENS_DIR.glob("*.png")) + list(IMAGENS_DIR.glob("*.jpg")) if IMAGENS_DIR.exists() else []

if imagens:
    print(f"🖼️  {len(imagens)} imagens encontradas — montando slideshow")
    # Cria slideshow com Ken Burns
    img_list = OUTPUT_DIR / "images.txt"
    with open(img_list, "w") as f:
        for img in imagens:
            f.write(f"file \'{img}\'\n")
            f.write("duration 8\n")

    video_path = OUTPUT_DIR / "V005_final.mp4"
    ken_burns = f"zoompan=z=\'min(zoom+0.0008,1.5)\':d=240:x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':s=1920x1080"
    cmd_video = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(img_list),
        "-i", str(narration_combined),
        "-vf", f"{ken_burns},{GRADE_FILTRO}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        str(video_path)
    ]
    result = subprocess.run(cmd_video, capture_output=True)
    if result.returncode == 0:
        size_mb = video_path.stat().st_size / 1024 / 1024
        print(f"✅ Vídeo gerado: {video_path.name} ({size_mb:.1f} MB)")
    else:
        print(f"⚠️ Falha na renderização: {result.stderr.decode()[:300]}")
else:
    print("⚠️ Sem imagens — gerando slideshow de cor com narração")
    # Placeholder: vídeo preto com narração (para testar pipeline)
    video_path = OUTPUT_DIR / "V005_audio_only.mp4"
    cmd_placeholder = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=25",
        "-i", str(narration_combined),
        "-c:v", "libx264", "-crf", "28", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-pix_fmt", "yuv420p",
        str(video_path)
    ]
    result = subprocess.run(cmd_placeholder, capture_output=True)
    if result.returncode == 0:
        size_mb = video_path.stat().st_size / 1024 / 1024
        print(f"✅ Áudio montado: {video_path.name} ({size_mb:.1f} MB)")
    else:
        print(f"⚠️ Placeholder falhou: {result.stderr.decode()[:200]}")

relatorio = {
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    "video": "V005",
    "agente": "VIDEO EDITOR PRO",
    "color_grade": "forest_green_gold",
    "cenas_audio": len(mp3_files),
    "imagens_usadas": len(imagens),
    "output_dir": str(OUTPUT_DIR)
}
(OUTPUT_DIR / "relatorio_montagem.json").write_text(__import__("json").dumps(relatorio, ensure_ascii=False, indent=2))
print(f"\n📋 Relatório salvo em {OUTPUT_DIR / 'relatorio_montagem.json'}")
