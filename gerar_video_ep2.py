#!/usr/bin/env python3
"""
Mente de Aço Ep.2 — Gerador via FFmpeg (rápido)
Gera PNGs por cena e monta vídeo via concat demuxer
"""
import sys, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
import numpy as np

AUDIO_PATH = sys.argv[1] if len(sys.argv) > 1 else "audio_ep2.mp3"
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "ep2_final.mp4"
WORK_DIR    = sys.argv[3] if len(sys.argv) > 3 else "/tmp/ep2_frames"

W, H = 1920, 1080

SCENES = [
    (5,  "O atleta que ganhou o ouro", "acordou sem vontade de treinar.", "hook"),
    (20, "Paris, 2024.", "6.200 treinos. 847 dias de exaustão.", "intro"),
    (15, "A maioria das pessoas", "espera sentir motivação antes de agir.", "body"),
    (12, "Motivação não é uma causa.", "É uma consequência.", "quote"),
    (18, "Você não se motiva para agir.", "Você age — e a motivação aparece depois.", "body"),
    (20, "500 atletas de alto rendimento.", "Nenhum usou motivação como pré-requisito.", "data"),
    (20, "Homeostase:", "o mecanismo do cérebro para conservar energia.", "body"),
    (15, "Não porque você é fraco.", "Porque seu cérebro funciona como foi programado.", "body"),
    (20, "Simone Biles:", '"Meu eu futuro vai agradecer ao eu presente\npor ter ido mesmo assim."', "quote"),
    (15, "O bloqueio não é sinal para parar.", "É sinal de que você está crescendo.", "highlight"),
    (20, "Técnica 1:", "IDENTIDADE ANTES DA AÇÃO", "technique"),
    (25, '"Eu quero ser disciplinado"', '→  "Eu SOU uma pessoa disciplinada"', "body"),
    (20, "Stanford University:", "2,3× mais chances de manter o hábito.", "data"),
    (20, "Técnica 2:", "O CONTRATO DOS 5 MINUTOS", "technique"),
    (25, "5 minutos. Só 5 minutos.", "Efeito Zeigarnik: tarefas iniciadas pedem conclusão.", "body"),
    (20, "Técnica 3:", "O AMBIENTE COMO ALIADO", "technique"),
    (25, "Remova os obstáculos entre", "intenção e ação. +40% de execução.", "data"),
    (15, "Não é força de vontade.", "É engenharia de comportamento.", "highlight"),
    (20, "O ouro olímpico não foi conquistado", "em um dia de grande motivação.", "body"),
    (20, "O que separa os que chegam:", "Um sistema. Uma identidade.", "body"),
    (20, "A motivação vai e vem como a maré.", "O sistema permanece.", "quote"),
    (25, "Mente de Aço — Ep.3:", "O PROTOCOLO DE 21 DIAS", "cta"),
]

COLOR_MAP = {
    "hook":      ("#FFFFFF", "#CCCCCC", 72, 36),
    "intro":     ("#E0E0E0", "#888888", 56, 28),
    "body":      ("#D0D0D0", "#888888", 52, 26),
    "quote":     ("#F5C842", "#CCCCCC", 58, 30),
    "data":      ("#64B5F6", "#AAAAAA", 54, 28),
    "highlight": ("#FF4444", "#CCCCCC", 60, 30),
    "technique": ("#FFFFFF", "#FF4444", 42, 52),
    "cta":       ("#F5C842", "#FFFFFF", 50, 36),
}


def make_frame(text_main, text_sub, style):
    img = Image.new("RGB", (W, H), (8, 8, 12))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(0, 300, 3):
        alpha = int((i / 300) ** 1.5 * 180)
        odraw.ellipse([i, i, W - i, H - i], outline=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    main_color, sub_color, main_size, sub_size = COLOR_MAP.get(style, ("#FFFFFF", "#AAAAAA", 52, 28))

    draw.line([(W//2 - 60, H//2 - 90), (W//2 + 60, H//2 - 90)], fill="#444444", width=2)

    try:
        fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", main_size)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", sub_size)
    except Exception:
        fm = fs = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text_main, font=fm)
    draw.text(((W - (bbox[2]-bbox[0]))//2, H//2 - 50), text_main, font=fm, fill=main_color)

    for i, line in enumerate(text_sub.split("\n")):
        bbox2 = draw.textbbox((0, 0), line, font=fs)
        draw.text(((W - (bbox2[2]-bbox2[0]))//2, H//2 + 20 + i*(sub_size+8)), line, font=fs, fill=sub_color)

    draw.line([(W//2 - 60, H//2 + 100), (W//2 + 60, H//2 + 100)], fill="#333333", width=1)

    try:
        fwm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        fwm = ImageFont.load_default()
    draw.text((40, H - 50), "MENTE DE AÇO", font=fwm, fill="#333333")

    return img


def get_audio_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True
    )
    return float(r.stdout.strip())


def main():
    os.makedirs(WORK_DIR, exist_ok=True)

    print(f"[1/4] Medindo áudio: {AUDIO_PATH}")
    total_dur = get_audio_duration(AUDIO_PATH)
    total_scene = sum(d for d, *_ in SCENES)
    scale = total_dur / total_scene
    print(f"      Áudio: {total_dur:.1f}s | Escala: {scale:.3f}x")

    print("[2/4] Gerando frames PNG...")
    concat_lines = []
    for idx, (dur, tm, ts, style) in enumerate(SCENES):
        adj = dur * scale
        png = os.path.join(WORK_DIR, f"scene_{idx:02d}.png")
        make_frame(tm, ts, style).save(png)
        concat_lines.append(f"file '{png}'")
        concat_lines.append(f"duration {adj:.4f}")
        if idx % 5 == 0:
            print(f"      [{idx+1}/{len(SCENES)}] {tm[:40]}")

    # FFmpeg concat demuxer: last file needs to be listed twice
    concat_lines.append(f"file '{concat_lines[-2].split(chr(39))[1]}'")

    concat_file = os.path.join(WORK_DIR, "concat.txt")
    with open(concat_file, "w") as f:
        f.write("\n".join(concat_lines))

    print("[3/4] Montando vídeo com FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-i", AUDIO_PATH,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-shortest",
        OUTPUT_PATH
    ]
    print(f"      CMD: {' '.join(cmd[:8])} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERRO FFMPEG:", result.stderr[-2000:])
        sys.exit(1)

    size_mb = os.path.getsize(OUTPUT_PATH) / 1024 / 1024
    print(f"\n✅ Vídeo: {OUTPUT_PATH}")
    print(f"   Tamanho: {size_mb:.1f} MB | Duração: {total_dur:.0f}s")


if __name__ == "__main__":
    main()
