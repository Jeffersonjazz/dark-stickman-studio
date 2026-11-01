#!/usr/bin/env python3
"""
DARK MANAGER — ORQUESTRADOR CENTRAL
DARK STUDIO AAA v1.3.0
Coordena: IMAGE ENGINE | AUDIO MASTER | VIDEO EDITOR PRO | MOTION GRAPHICS | CREATIVE QA
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys, os, json, time, subprocess
from pathlib import Path
from datetime import datetime

PRODUCAO_DIR = Path(__file__).parent
VIDEOS = [
    {"id": "V001", "dir": "v001_psicologia_vazio",      "nicho": "psicologia",   "titulo": "Por Que Você Se Sente Vazio?"},
    {"id": "V002", "dir": "v002_historia_stonehouse",   "nicho": "historia",     "titulo": "O Homem Que Fingiu Ser Morto"},
    {"id": "V003", "dir": "v003_tecnologia_ia_morte",   "nicho": "tecnologia",   "titulo": "A IA Que Previu Sua Morte"},
    {"id": "V004", "dir": "v004_misterio_arquivo",      "nicho": "misterio",     "titulo": "O Arquivo Que o Governo Apagou"},
    {"id": "V005", "dir": "v005_natureza_floresta",     "nicho": "natureza",     "titulo": "A Floresta Que Respira"},
]

def header(titulo, icone="🎬"):
    print(f"\n{'=' * 65}")
    print(f"  {icone}  {titulo}")
    print(f"{'=' * 65}")

def executar_script(script_path, descricao):
    """Executa um script Python e retorna sucesso/falha"""
    print(f"\n  ▶ {descricao}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            print(f"    ✅ Concluído")
            return True
        else:
            print(f"    ⚠️ Saiu com código {result.returncode}")
            if result.stderr:
                print(f"    stderr: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ⚠️ Timeout após 300s")
        return False
    except Exception as e:
        print(f"    ❌ Erro: {e}")
        return False

def agente_audio_master(video_dir, video_id):
    """AUDIO MASTER: Gera narração TTS para um vídeo"""
    script = video_dir / "gerar_narracao.py"
    if not script.exists():
        print(f"    ⚠️ Script TTS não encontrado: {script}")
        return False
    return executar_script(script, f"AUDIO MASTER → {video_id} TTS pt-BR")

def agente_video_editor_pro(video_dir, video_id, pacote):
    """VIDEO EDITOR PRO: Monta o vídeo com Ken Burns + narração"""
    audio_dir = video_dir / "audio"
    mp3_files = list(audio_dir.glob("*.mp3")) if audio_dir.exists() else []

    if not mp3_files:
        print(f"    ⚠️ Nenhum áudio disponível para {video_id} — montagem pulada")
        print(f"    💡 Execute primeiro: python gerar_narracao.py")
        return False

    print(f"    🎵 {len(mp3_files)} arquivos de áudio encontrados")

    # Gera script de montagem FFmpeg
    montagem_script = video_dir / "montar_video.py"
    color_grade = pacote.get("color_grading", "teal_orange")
    titulo = pacote.get("titulo", video_id)

    script_content = f'''#!/usr/bin/env python3
"""VIDEO EDITOR PRO — Montagem Ken Burns — {video_id}
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
COLOR_GRADES = {{
    "teal_orange_psicologia": "eq=contrast=1.1:brightness=-0.05:saturation=0.9,colorbalance=rs=-0.1:gs=0:bs=0.15:rm=0:gm=0:bm=0",
    "sepia_vintage_noir": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=contrast=1.2:brightness=-0.1",
    "tech_blue_clinical": "colorbalance=rs=-0.2:gs=-0.1:bs=0.3:rm=0:gm=0:bm=0.1,eq=contrast=1.15:saturation=0.85",
    "shadow_conspiracy_green": "colorbalance=rs=-0.1:gs=0.1:bs=-0.1:rm=0:gm=0.05:bm=0,eq=contrast=1.25:brightness=-0.1",
    "forest_green_gold": "colorbalance=rs=0:gs=0.1:bs=-0.15:rm=0:gm=0.05:bm=-0.1,eq=contrast=1.1:saturation=1.1"
}}

GRADE_FILTRO = COLOR_GRADES.get("{color_grade}", COLOR_GRADES["teal_orange_psicologia"])
TITULO = "{titulo}"

mp3_files = sorted(AUDIO_DIR.glob("*.mp3"))
if not mp3_files:
    print("⚠️ Nenhum arquivo de áudio encontrado")
    sys.exit(1)

print(f"🎬 VIDEO EDITOR PRO — {{len(mp3_files)}} cenas de áudio")

# Etapa 1: Concatenar narração
concat_list = OUTPUT_DIR / "concat_audio.txt"
with open(concat_list, "w") as f:
    for mp3 in mp3_files:
        f.write(f"file \\'{{mp3}}\\'\\n")

narration_combined = OUTPUT_DIR / "narracao_completa.mp3"
cmd_concat = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy", str(narration_combined)
]
result = subprocess.run(cmd_concat, capture_output=True)
if result.returncode == 0:
    print(f"✅ Narração concatenada: {{narration_combined.name}}")
else:
    print(f"⚠️ Concat falhou: {{result.stderr.decode()[:200]}}")
    narration_combined = mp3_files[0]

# Etapa 2: Verificar imagens ou usar placeholder
imagens = list(IMAGENS_DIR.glob("*.png")) + list(IMAGENS_DIR.glob("*.jpg")) if IMAGENS_DIR.exists() else []

if imagens:
    print(f"🖼️  {{len(imagens)}} imagens encontradas — montando slideshow")
    # Cria slideshow com Ken Burns
    img_list = OUTPUT_DIR / "images.txt"
    with open(img_list, "w") as f:
        for img in imagens:
            f.write(f"file \\'{{img}}\\'\\n")
            f.write("duration 8\\n")

    video_path = OUTPUT_DIR / "{video_id}_final.mp4"
    ken_burns = f"zoompan=z=\\'min(zoom+0.0008,1.5)\\':d=240:x=\\'iw/2-(iw/zoom/2)\\':y=\\'ih/2-(ih/zoom/2)\\':s=1920x1080"
    cmd_video = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(img_list),
        "-i", str(narration_combined),
        "-vf", f"{{ken_burns}},{{GRADE_FILTRO}}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-pix_fmt", "yuv420p",
        str(video_path)
    ]
    result = subprocess.run(cmd_video, capture_output=True)
    if result.returncode == 0:
        size_mb = video_path.stat().st_size / 1024 / 1024
        print(f"✅ Vídeo gerado: {{video_path.name}} ({{size_mb:.1f}} MB)")
    else:
        print(f"⚠️ Falha na renderização: {{result.stderr.decode()[:300]}}")
else:
    print("⚠️ Sem imagens — gerando slideshow de cor com narração")
    # Placeholder: vídeo preto com narração (para testar pipeline)
    video_path = OUTPUT_DIR / "{video_id}_audio_only.mp4"
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
        print(f"✅ Áudio montado: {{video_path.name}} ({{size_mb:.1f}} MB)")
    else:
        print(f"⚠️ Placeholder falhou: {{result.stderr.decode()[:200]}}")

relatorio = {{
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    "video": "{video_id}",
    "agente": "VIDEO EDITOR PRO",
    "color_grade": "{color_grade}",
    "cenas_audio": len(mp3_files),
    "imagens_usadas": len(imagens),
    "output_dir": str(OUTPUT_DIR)
}}
(OUTPUT_DIR / "relatorio_montagem.json").write_text(__import__("json").dumps(relatorio, ensure_ascii=False, indent=2))
print(f"\\n📋 Relatório salvo em {{OUTPUT_DIR / 'relatorio_montagem.json'}}")
'''
    montagem_script.write_text(script_content, encoding='utf-8')
    print(f"    📝 Script de montagem criado: {montagem_script.name}")

    # Executa montagem
    return executar_script(montagem_script, f"VIDEO EDITOR PRO → {video_id} montagem FFmpeg")

def agente_creative_qa(video_dir, video_id):
    """CREATIVE QA: Verifica output gerado"""
    output_dir = video_dir / "output"
    audio_dir = video_dir / "audio"

    resultado_qa = {
        "video_id": video_id,
        "timestamp": datetime.now().isoformat(),
        "checklist": {}
    }

    # Verifica áudios
    mp3s = list(audio_dir.glob("*.mp3")) if audio_dir.exists() else []
    resultado_qa["checklist"]["narracao_gerada"] = len(mp3s) > 0
    resultado_qa["checklist"]["cenas_audio"] = len(mp3s)

    # Verifica vídeo montado
    mp4s = list(output_dir.glob("*.mp4")) if output_dir.exists() else []
    resultado_qa["checklist"]["video_montado"] = len(mp4s) > 0
    if mp4s:
        size_mb = mp4s[0].stat().st_size / 1024 / 1024
        resultado_qa["checklist"]["tamanho_mb"] = round(size_mb, 2)
        resultado_qa["checklist"]["tamanho_ok"] = size_mb > 0.1

    # Verifica relatórios
    resultado_qa["checklist"]["relatorio_audio"] = (audio_dir / "relatorio_narracao.json").exists() if audio_dir.exists() else False
    resultado_qa["checklist"]["relatorio_montagem"] = (output_dir / "relatorio_montagem.json").exists() if output_dir.exists() else False

    # Score QA
    checks = [v for v in resultado_qa["checklist"].values() if isinstance(v, bool)]
    score = sum(checks) / len(checks) * 100 if checks else 0
    resultado_qa["score_qa"] = round(score, 1)
    resultado_qa["status"] = "APROVADO" if score >= 60 else "PENDENTE"
    resultado_qa["ai_generated"] = True
    resultado_qa["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

    # Salva relatório QA
    qa_path = video_dir / "relatorio_qa.json"
    qa_path.write_text(json.dumps(resultado_qa, ensure_ascii=False, indent=2))

    status_icon = "✅" if resultado_qa["status"] == "APROVADO" else "⚠️"
    print(f"    {status_icon} QA Score: {score:.0f}% — {resultado_qa['status']}")
    print(f"       Áudios: {len(mp3s)} | Vídeos: {len(mp4s)}")
    return resultado_qa

def main():
    inicio = time.time()

    header("DARK MANAGER — ORQUESTRADOR CENTRAL", "🎭")
    print(f"  DARK STUDIO AAA v1.3.0")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"  {len(VIDEOS)} vídeos em produção")

    relatorio_geral = {
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "inicio": datetime.now().isoformat(),
        "videos": {}
    }

    for video in VIDEOS:
        video_id = video["id"]
        video_dir = PRODUCAO_DIR / video["dir"]

        header(f"{video_id} — {video['titulo']}", "🎬")
        print(f"  Nicho: {video['nicho']} | Dir: {video['dir']}")

        # Carrega pacote de produção se existir
        pacote = {}
        pacote_path = video_dir / "pacote_producao.json"
        if pacote_path.exists():
            try:
                with open(pacote_path) as f:
                    pacote = json.load(f)
                print(f"  📦 Pacote de produção carregado")
            except:
                pass

        resultado_video = {"id": video_id, "titulo": video["titulo"], "etapas": {}}

        # ── ETAPA 1: AUDIO MASTER ──────────────────────────────
        print(f"\n  📡 CHAMANDO: AGENTE AUDIO MASTER")
        sucesso_audio = agente_audio_master(video_dir, video_id)
        resultado_video["etapas"]["audio_master"] = "ok" if sucesso_audio else "falhou"

        # ── ETAPA 2: VIDEO EDITOR PRO ──────────────────────────
        print(f"\n  📡 CHAMANDO: AGENTE VIDEO EDITOR PRO")
        sucesso_video = agente_video_editor_pro(video_dir, video_id, pacote)
        resultado_video["etapas"]["video_editor_pro"] = "ok" if sucesso_video else "falhou/pendente"

        # ── ETAPA 3: CREATIVE QA ───────────────────────────────
        print(f"\n  📡 CHAMANDO: AGENTE CREATIVE QA")
        qa = agente_creative_qa(video_dir, video_id)
        resultado_video["etapas"]["creative_qa"] = qa["status"]
        resultado_video["score_qa"] = qa["score_qa"]

        relatorio_geral["videos"][video_id] = resultado_video

    # ── RELATÓRIO FINAL ────────────────────────────────────────
    duracao = time.time() - inicio
    relatorio_geral["duracao_segundos"] = round(duracao, 1)
    relatorio_geral["fim"] = datetime.now().isoformat()

    header("RELATÓRIO FINAL — DARK MANAGER", "📊")
    aprovados = 0
    for vid_id, dados in relatorio_geral["videos"].items():
        score = dados.get("score_qa", 0)
        status = "✅" if score >= 60 else "⚠️"
        aprovados += 1 if score >= 60 else 0
        print(f"  {status} {vid_id}: QA {score:.0f}% | Audio: {dados['etapas'].get('audio_master','?')} | Vídeo: {dados['etapas'].get('video_editor_pro','?')}")

    print(f"\n  🏆 APROVADOS: {aprovados}/{len(VIDEOS)}")
    print(f"  ⏱  Tempo total: {duracao:.0f}s")
    print(f"  💰 Custo estimado: R$0,00 (pipeline 100% local)")

    relatorio_path = PRODUCAO_DIR / "relatorio_orquestrador.json"
    relatorio_path.write_text(json.dumps(relatorio_geral, ensure_ascii=False, indent=2))
    print(f"\n  📋 Relatório completo: {relatorio_path}")
    print(f"\n{'=' * 65}")
    print(f"  DARK STUDIO AAA — PRODUÇÃO CONCLUÍDA")
    print(f"{'=' * 65}\n")

    return relatorio_geral

if __name__ == "__main__":
    main()
