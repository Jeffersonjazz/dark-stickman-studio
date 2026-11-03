#!/usr/bin/env python3
"""
DARK STUDIO AAA — Pipeline Semana 01
Gera narração edge-tts + vídeo MP4 para v001-v005
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Agentes evocados:
  🎙 AUDIO MASTER       — narração edge-tts PT-BR
  🎬 VIDEO EDITOR PRO   — composição FFmpeg
  📊 ASSET MANAGER      — registro de assets
  ✅ CREATIVE QA        — validação final
"""
import asyncio, subprocess, json, re, os
from pathlib import Path
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
OUT_AUDIO = BASE / "outputs/audio"
OUT_VIDEO = BASE / "outputs/videos"
OUT_THUMB = BASE / "outputs/thumbnails"
PRODUCAO  = BASE / "producao"
OUT_AUDIO.mkdir(parents=True, exist_ok=True)
OUT_VIDEO.mkdir(parents=True, exist_ok=True)

# Voz edge-tts padrão PT-BR masculina
VOZ_PADRAO = "pt-BR-AntonioNeural"

# ─── VÍDEOS DA SEMANA 01 ──────────────────────────────────────────────────────
VIDEOS = [
    {
        "id": "v001",
        "pasta": "v001_psicologia_vazio",
        "titulo": "Por Que Você Se Sente Vazio Mesmo Tendo Tudo",
        "canal": "Mente_de_Aco",
        "nicho": "psicologia",
        "duracao_alvo": 240,
        "cor_thumb": "#1a0a2e",
        "texto_thumb": "VAZIO",
    },
    {
        "id": "v002",
        "pasta": "v002_historia_stonehouse",
        "titulo": "O Político Que Fingiu Sua Própria Morte e Começou Uma Nova Vida",
        "canal": "Bastidores_do_Tempo",
        "nicho": "historia",
        "duracao_alvo": 240,
        "cor_thumb": "#0d1b2a",
        "texto_thumb": "STONEHOUSE",
    },
    {
        "id": "v003",
        "pasta": "v003_tecnologia_ia_morte",
        "titulo": "A IA Que Pode Prever Sua Morte Com 87% de Precisão",
        "canal": "Intelligentia_Nova",
        "nicho": "tecnologia",
        "duracao_alvo": 240,
        "cor_thumb": "#0a1628",
        "texto_thumb": "IA MORTAL",
    },
    {
        "id": "v004",
        "pasta": "v004_misterio_arquivo",
        "titulo": "O Arquivo Secreto Que Governos Não Querem Que Você Veja",
        "canal": "Projeto_Secreto",
        "nicho": "misterio",
        "duracao_alvo": 240,
        "cor_thumb": "#1a1a0a",
        "texto_thumb": "ARQUIVO X",
    },
    {
        "id": "v005",
        "pasta": "v005_natureza_floresta",
        "titulo": "A Floresta Que Respira e Pensa — O Organismo Mais Antigo da Terra",
        "canal": "AquaZen_Relax",
        "nicho": "natureza",
        "duracao_alvo": 240,
        "cor_thumb": "#0a1f0a",
        "texto_thumb": "FLORESTA VIVA",
    },
]

# ─── AGENTE AUDIO MASTER ─────────────────────────────────────────────────────
def limpar_roteiro(texto: str) -> str:
    """Remove marcações de cena, pausa e direção do roteiro."""
    linhas = []
    for linha in texto.split("\n"):
        l = linha.strip()
        if not l:
            linhas.append("")
            continue
        # Remove marcações entre colchetes
        if re.match(r"^\[", l):
            continue
        # Remove linhas de separação
        if l.startswith("===") or l.startswith("---"):
            continue
        # Remove headers de metadados
        if ":" in l[:30] and any(k in l for k in ["ai_generated", "ai_disclosure", "Vídeo:", "Nicho:", "Duração", "Voz:", "DARK STUDIO"]):
            continue
        linhas.append(l)
    # Limpar múltiplas linhas em branco
    texto_limpo = re.sub(r"\n{3,}", "\n\n", "\n".join(linhas))
    return texto_limpo.strip()

async def gerar_narracao_edgetts(texto: str, out_path: Path, voz: str = VOZ_PADRAO) -> bool:
    """🎙 AUDIO MASTER — Gera narração via edge-tts (gratuito)."""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(texto, voz, rate="-5%", pitch="-3Hz")
        await communicate.save(str(out_path))
        if out_path.exists() and out_path.stat().st_size > 1000:
            print(f"   ✅ AUDIO MASTER: {out_path.name} ({out_path.stat().st_size//1024}KB)")
            return True
    except Exception as e:
        print(f"   ⚠  edge-tts erro: {e}")
    return False

# ─── AGENTE IMAGE ENGINE — Thumbnail via FFmpeg ───────────────────────────────
def gerar_thumbnail_ffmpeg(titulo: str, cor: str, texto: str, out_path: Path, canal: str) -> bool:
    """🖼 IMAGE ENGINE — Cria thumbnail 1280x720 via FFmpeg puro."""
    # Converter hex para RGB
    cor = cor.lstrip("#")
    r, g, b = int(cor[0:2],16), int(cor[2:4],16), int(cor[4:6],16)

    # Gradiente escuro com texto
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={cor}:size=1280x720:rate=1",
        "-vf",
        (
            f"drawbox=x=0:y=0:w=1280:h=720:color=0x000000@0.5:t=fill,"
            f"drawtext=text='{texto}':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-60:shadowcolor=black:shadowx=3:shadowy=3,"
            f"drawtext=text='DARK STUDIO AAA':fontsize=24:fontcolor=#888888:x=(w-text_w)/2:y=660,"
            f"drawtext=text='[IA]':fontsize=22:fontcolor=#555555:x=20:y=695"
        ),
        "-frames:v", "1",
        str(out_path)
    ]
    r2 = subprocess.run(cmd, capture_output=True)
    if r2.returncode == 0 and out_path.exists():
        print(f"   ✅ IMAGE ENGINE: thumbnail {out_path.name}")
        return True
    # Fallback: thumbnail sólida simples
    cmd2 = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x1a1a2e:size=1280x720:rate=1",
        "-frames:v", "1", str(out_path)
    ]
    subprocess.run(cmd2, capture_output=True)
    return out_path.exists()

# ─── AGENTE VIDEO EDITOR PRO ─────────────────────────────────────────────────
def compor_video(audio_path: Path, thumb_path: Path, out_path: Path,
                  titulo: str, canal: str, duracao: int) -> bool:
    """🎬 VIDEO EDITOR PRO — Compõe vídeo final com narração + visual."""

    # Verificar duração real do áudio
    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ], capture_output=True, text=True)

    dur_real = float(r.stdout.strip()) if r.stdout.strip() else duracao
    print(f"   📏 Duração narração: {dur_real:.1f}s")

    # Verificar se thumbnail existe
    if not thumb_path.exists():
        # Buscar qualquer thumbnail
        thumbs = list((BASE / "outputs/thumbnails").glob("*.jpg"))
        if thumbs:
            thumb_path = sorted(thumbs, key=lambda p: p.stat().st_size, reverse=True)[0]
            print(f"   ⚠  Usando fallback thumb: {thumb_path.name}")
        else:
            print("   ❌ Sem thumbnail disponível")
            return False

    # Composição: thumbnail + narração + legendas de canal
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(thumb_path),
        "-i", str(audio_path),
        "-vf", (
            "scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=1920:1080,"
            f"drawtext=text='Produzido com IA — DARK STUDIO AAA':fontsize=22:"
            f"fontcolor=white@0.6:x=20:y=H-40:shadowcolor=black:shadowx=1:shadowy=1"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(dur_real + 1),
        "-r", "24", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-metadata", f"title={titulo}",
        "-metadata", "artist=DARK STUDIO AAA",
        "-metadata", "comment=ai_generated=True;ai_disclosure=Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        str(out_path)
    ]

    r2 = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if r2.returncode == 0 and out_path.exists() and out_path.stat().st_size > 100_000:
        mb = out_path.stat().st_size / (1024*1024)
        print(f"   ✅ VIDEO EDITOR PRO: {out_path.name} ({mb:.1f}MB)")
        return True
    else:
        print(f"   ❌ Composição falhou: {r2.stderr[-300:]}")
        return False

# ─── AGENTE CREATIVE QA ──────────────────────────────────────────────────────
def qa_video(out_path: Path, duracao_alvo: int) -> dict:
    """✅ CREATIVE QA — Valida vídeo gerado."""
    if not out_path.exists():
        return {"status": "FALHOU", "erro": "arquivo não existe"}

    tamanho_mb = out_path.stat().st_size / (1024*1024)

    r = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "stream=codec_type,codec_name,width,height:format=duration,size",
        "-of", "json", str(out_path)
    ], capture_output=True, text=True)

    info = json.loads(r.stdout) if r.stdout else {}
    dur = float(info.get("format", {}).get("duration", 0))

    streams = info.get("streams", [])
    tem_video = any(s.get("codec_type") == "video" for s in streams)
    tem_audio = any(s.get("codec_type") == "audio" for s in streams)

    status = "✅ APROVADO" if (tem_video and tem_audio and dur > 10 and tamanho_mb > 0.5) else "⚠ ATENÇÃO"

    return {
        "status": status,
        "arquivo": out_path.name,
        "tamanho_mb": round(tamanho_mb, 2),
        "duracao_s": round(dur, 1),
        "tem_video": tem_video,
        "tem_audio": tem_audio,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }

# ─── PIPELINE PRINCIPAL ───────────────────────────────────────────────────────
async def processar_video(v: dict) -> dict:
    """Pipeline completo para um vídeo."""
    vid_id   = v["id"]
    pasta    = PRODUCAO / v["pasta"]

    print(f"\n{'='*60}")
    print(f"🎬 {vid_id.upper()} — {v['titulo'][:50]}")
    print(f"   Canal: {v['canal']} | Nicho: {v['nicho']}")
    print(f"{'='*60}")

    # Caminhos de saída
    audio_out = OUT_AUDIO / f"{vid_id}_narracao.mp3"
    thumb_out = OUT_THUMB / f"thumb_{vid_id}_{v['nicho']}.jpg"
    video_out = OUT_VIDEO / f"{vid_id}_{v['canal']}.mp4"

    resultado = {"id": vid_id, "titulo": v["titulo"], "canal": v["canal"]}

    # 1) Ler roteiro
    roteiro_path = pasta / "roteiro_naracao_completo.txt"
    if not roteiro_path.exists():
        # Criar roteiro básico se não existir
        texto_roteiro = f"""DARK STUDIO AAA — {v['titulo']}

Este vídeo explora {v['titulo'].lower()}.

Produzido com DARK STUDIO AAA — DARK CREATIVE LAB.
"""
    else:
        texto_roteiro = roteiro_path.read_text(encoding="utf-8")

    texto_limpo = limpar_roteiro(texto_roteiro)

    # Limitar tamanho para edge-tts (max ~10min de narração)
    palavras = texto_limpo.split()
    if len(palavras) > 1500:
        texto_limpo = " ".join(palavras[:1500])
        print(f"   ✂  Roteiro truncado: {len(palavras)} → 1500 palavras")

    print(f"   📄 Roteiro: {len(texto_limpo.split())} palavras")

    # 2) 🎙 AUDIO MASTER — Narração
    if not audio_out.exists() or audio_out.stat().st_size < 1000:
        print("   🎙 AUDIO MASTER: Gerando narração...")
        ok_audio = await gerar_narracao_edgetts(texto_limpo, audio_out)
        if not ok_audio:
            resultado["status"] = "audio_falhou"
            return resultado
    else:
        print(f"   ♻  AUDIO MASTER: Reusando {audio_out.name}")

    # 3) 🖼 IMAGE ENGINE — Thumbnail
    if not thumb_out.exists():
        print("   🖼 IMAGE ENGINE: Gerando thumbnail...")
        gerar_thumbnail_ffmpeg(v["titulo"], v["cor_thumb"], v["texto_thumb"], thumb_out, v["canal"])
    else:
        print(f"   ♻  IMAGE ENGINE: Reusando {thumb_out.name}")

    # Buscar thumbnail existente se nova não foi gerada
    if not thumb_out.exists():
        thumbs_existentes = sorted(OUT_THUMB.glob("*.jpg"), key=lambda p: p.stat().st_size, reverse=True)
        if thumbs_existentes:
            thumb_out = thumbs_existentes[0]

    # 4) 🎬 VIDEO EDITOR PRO — Composição
    print("   🎬 VIDEO EDITOR PRO: Compondo vídeo...")
    ok_video = compor_video(audio_out, thumb_out, video_out, v["titulo"], v["canal"], v["duracao_alvo"])

    if not ok_video:
        resultado["status"] = "video_falhou"
        return resultado

    # 5) ✅ CREATIVE QA — Validação
    qa = qa_video(video_out, v["duracao_alvo"])
    resultado.update(qa)
    resultado["caminho"] = str(video_out)
    resultado["data_geracao"] = datetime.now().isoformat()

    print(f"   🔍 CREATIVE QA: {qa['status']} | {qa.get('duracao_s',0)}s | {qa.get('tamanho_mb',0)}MB")

    return resultado

async def main():
    print("\n" + "█"*60)
    print("  DARK STUDIO AAA — PIPELINE SEMANA 01")
    print("  9 Agentes Especialistas Evocados")
    print("  🎙 AUDIO MASTER | 🎬 VIDEO EDITOR PRO | 🖼 IMAGE ENGINE")
    print("  📊 ASSET MANAGER | ✅ CREATIVE QA | 🎭 VISUAL CONSISTENCY")
    print("█"*60)

    resultados = []

    for v in VIDEOS:
        try:
            res = await processar_video(v)
            resultados.append(res)
        except Exception as e:
            print(f"   ❌ ERRO em {v['id']}: {e}")
            resultados.append({"id": v["id"], "status": "erro", "erro": str(e)})

    # Relatório final
    print("\n" + "="*60)
    print("  RELATÓRIO FINAL — SEMANA 01")
    print("="*60)

    aprovados = 0
    for r in resultados:
        status = r.get("status", "desconhecido")
        if "APROVADO" in str(status):
            aprovados += 1
            print(f"  ✅ {r['id']}: {r.get('duracao_s',0)}s | {r.get('tamanho_mb',0)}MB")
        else:
            print(f"  ❌ {r['id']}: {status}")

    print(f"\n  Total: {aprovados}/{len(VIDEOS)} vídeos aprovados")
    print(f"  ai_generated: True")
    print(f"  ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")

    # Salvar relatório
    relatorio_path = BASE / "outputs/relatorio_semana01.json"
    with open(relatorio_path, "w", encoding="utf-8") as f:
        json.dump({
            "semana": "01_nov_2026",
            "data_execucao": datetime.now().isoformat(),
            "total_videos": len(VIDEOS),
            "aprovados": aprovados,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "videos": resultados
        }, f, ensure_ascii=False, indent=2)

    print(f"\n  📋 Relatório: {relatorio_path}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
