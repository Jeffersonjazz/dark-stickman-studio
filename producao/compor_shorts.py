"""
DARK STUDIO AAA — Composição de Shorts com FFmpeg
Pipeline: Thumbnail (imagem) + Áudio (MP3) → MP4 vertical 1080x1920
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════
# MAPA: Short → Thumbnail + Script (para calcular duração)
# ═══════════════════════════════════════════════════════
SHORTS = [
    {
        "id": "short1",
        "canal": "Mente de Aço",
        "dia": "Seg 03/11",
        "titulo": "Por Que Você Nunca Executa Seus Planos?",
        "thumbnail": "outputs/thumbnails/thumb_1634b955_por_que_você_nunca_executa_seu.jpg",
        "script_chars": 390,  # estimativa de duração baseada em chars
        "tags": "#psicologia #motivacao #mentalidade #shorts",
        "nicho": "mentalidade"
    },
    {
        "id": "short2",
        "canal": "Intelligentia Nova",
        "dia": "Ter 04/11",
        "titulo": "A IA Que Prevê Sua Morte Antes de Você Saber",
        "thumbnail": "outputs/thumbnails/thumb_4d7b1b20_a_ia_que_prevê_sua_morte_antes.jpg",
        "script_chars": 450,
        "tags": "#inteligenciaartificial #ia #tecnologia #shorts",
        "nicho": "tech_ia"
    },
    {
        "id": "short3",
        "canal": "Bastidores do Tempo",
        "dia": "Qua 05/11",
        "titulo": "Por Que Roma Escondeu Este Segredo por 1500 Anos?",
        "thumbnail": "outputs/thumbnails/thumb_b6e78d75_por_que_roma_escondeu_este_seg.jpg",
        "script_chars": 430,
        "tags": "#historia #roma #curiosidades #shorts",
        "nicho": "historia"
    },
    {
        "id": "short4",
        "canal": "Projeto Secreto",
        "dia": "Qui 06/11",
        "titulo": "Por Que o Governo Lavou Cérebros de Cidadãos Reais?",
        "thumbnail": "outputs/thumbnails/thumb_27018b80_por_que_o_governo_lavou_cérebr.jpg",
        "script_chars": 480,
        "tags": "#conspiracao #cia #mkultra #shorts",
        "nicho": "conspiracao"
    },
    {
        "id": "short5",
        "canal": "AquaZen Relax",
        "dia": "Sex 07/11",
        "titulo": "Você NUNCA Dormiu Tão Bem Quanto Com Estes Sons da Natureza",
        "thumbnail": "outputs/thumbnails/thumb_ff3b6fd6_você_nunca_dormiu_tão_bem_quan.jpg",
        "script_chars": 190,
        "tags": "#relaxamento #natureza #sonoeprofundo #shorts",
        "nicho": "relaxamento"
    }
]

OUT_DIR = Path("outputs/videos")
AUDIO_DIR = Path("outputs/audio")
OUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def estimar_duracao(chars: int, nicho: str) -> int:
    """Estima duração em segundos baseada em chars do script"""
    # ~12 chars/segundo narração normal, 8 para relaxamento
    wpm = 8 if nicho == "relaxamento" else 12
    return max(30, min(60, chars // wpm))


def gerar_audio_silent(nome: str, duracao: int) -> str:
    """Gera MP3 de silêncio com duração correta via FFmpeg"""
    out = AUDIO_DIR / f"{nome}.mp3"
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=mono:sample_rate=44100",
        "-t", str(duracao),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        str(out)
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return str(out)


def escapar_texto_ffmpeg(texto: str) -> str:
    """Escapa texto para uso no filtro drawtext do FFmpeg"""
    # Remover/substituir caracteres problemáticos
    texto = texto.replace("'", "")      # aspas simples
    texto = texto.replace("|", "-")     # pipe
    texto = texto.replace(":", r"\:")   # dois pontos
    texto = texto.replace("\\", "")     # backslash
    texto = texto.replace("[", "(").replace("]", ")")
    return texto


def compor_short_mp4(short: dict) -> dict:
    """
    Compõe Short vertical 1080x1920 MP4:
    - Fundo: thumbnail estendida + blur (background fill)
    - Foreground: thumbnail original centralizada
    - Texto: título sobreposto
    - Áudio: placeholder silent (aguardando TTS real)
    """
    nome = short["id"]
    thumb_path = short["thumbnail"]
    duracao = estimar_duracao(short["script_chars"], short["nicho"])
    out_mp4 = OUT_DIR / f"{nome}_{short['canal'].replace(' ', '_')}.mp4"

    print(f"\n[VIDEO_EDITOR_PRO] Compondo {nome} — {duracao}s")
    print(f"  Thumbnail: {thumb_path}")

    # Verificar se thumbnail existe, senão usar placeholder
    if not os.path.exists(thumb_path):
        # Buscar qualquer thumbnail disponível
        thumbs = list(Path("outputs/thumbnails").glob("*.jpg"))
        if thumbs:
            thumb_path = str(thumbs[0])
            print(f"  ⚠️  Usando thumb alternativa: {Path(thumb_path).name}")
        else:
            print("  ❌ Nenhuma thumbnail encontrada")
            return {"id": nome, "status": "erro", "motivo": "thumbnail não encontrada"}

    # Gerar áudio silent
    audio_path = gerar_audio_silent(nome, duracao)
    print(f"  Áudio: {audio_path} ({duracao}s)")

    # Título formatado para vídeo (quebra de linha a cada 25 chars)
    titulo = short["titulo"]
    palavras = titulo.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= 22:
            linha_atual += (" " if linha_atual else "") + palavra
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    titulo_video = escapar_texto_ffmpeg(r"\n".join(linhas[:3]))
    canal_texto = escapar_texto_ffmpeg(short["canal"].upper())
    rodape_texto = "Produzido com IA - DARK STUDIO AAA"

    # Cor por nicho
    cor_nicho = {
        "mentalidade": "0x4A90D9",
        "tech_ia": "0x00BFFF",
        "historia": "0xFFD700",
        "conspiracao": "0xFF4500",
        "relaxamento": "0x00CED1",
    }.get(short["nicho"], "0xFFFFFF")

    # FFmpeg: thumbnail → vídeo vertical 1080x1920 com texto
    # Pipeline: scale+blur (fundo) + thumbnail centralizada + drawtext
    filtro = (
        # Escalar thumbnail para 1080x1920 com crop (fundo)
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"boxblur=20:20[bg];"
        # Thumbnail original: fit dentro de 1080x1200 (área superior)
        f"[0:v]scale=1080:-1:force_original_aspect_ratio=decrease,"
        f"pad=1080:1920:0:100:black@0[fg];"
        # Combinar fundo + foreground
        f"[bg][fg]overlay=0:0[base];"
        # Faixa escura no topo para texto
        f"[base]drawbox=x=0:y=0:w=1080:h=250:color=black@0.7:t=fill[boxed];"
        # Canal (pequeno, topo)
        f"[boxed]drawtext=text='{canal_texto}':"
        f"fontsize=36:fontcolor=white:x=(w-text_w)/2:y=30:"
        f"shadowcolor=black:shadowx=2:shadowy=2[c1];"
        # Barra colorida do nicho
        f"[c1]drawbox=x=0:y=90:w=1080:h=6:color={cor_nicho}:t=fill[bar];"
        # Título
        f"[bar]drawtext=text='{titulo_video}':"
        f"fontsize=46:fontcolor=white:x=(w-text_w)/2:y=110:"
        f"shadowcolor=black:shadowx=3:shadowy=3[titled];"
        # AI disclosure no rodapé
        f"[titled]drawtext=text='{rodape_texto}':"
        f"fontsize=24:fontcolor=white@0.6:x=(w-text_w)/2:y=h-60[final]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",           # imagem em loop
        "-i", thumb_path,       # thumbnail como vídeo
        "-i", audio_path,       # áudio
        "-filter_complex", filtro,
        "-map", "[final]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-t", str(duracao),
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_mp4)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0 and out_mp4.exists():
            size_mb = out_mp4.stat().st_size / (1024 * 1024)
            print(f"  ✅ {out_mp4.name} — {size_mb:.1f} MB")
            return {
                "id": nome,
                "canal": short["canal"],
                "dia": short["dia"],
                "status": "COMPOSTO",
                "arquivo": str(out_mp4),
                "duracao_s": duracao,
                "tamanho_mb": round(size_mb, 2),
                "titulo_youtube": short["titulo"],
                "tags": short["tags"],
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
                "nota": "Áudio placeholder — substituir por TTS real antes do upload"
            }
        else:
            erro = result.stderr[-500:] if result.stderr else "erro desconhecido"
            print(f"  ❌ FFmpeg erro: {erro[-200:]}")
            return {"id": nome, "status": "erro_ffmpeg", "log": erro[-200:]}
    except subprocess.TimeoutExpired:
        return {"id": nome, "status": "timeout"}
    except Exception as e:
        return {"id": nome, "status": "erro", "motivo": str(e)}


# ═══════════════════════════════════════════════════════
# EXECUTAR COMPOSIÇÃO
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   VIDEO_EDITOR_PRO — Composição de 5 Shorts          ║")
    print("║   Pipeline: Thumbnail → MP4 vertical 1080x1920       ║")
    print("╚══════════════════════════════════════════════════════╝")

    resultados = []
    for short in SHORTS:
        r = compor_short_mp4(short)
        resultados.append(r)

    # Relatório
    out_dir = Path("producao/semana_01_nov_2026")
    out_dir.mkdir(parents=True, exist_ok=True)
    relatorio = {
        "batch": "Composição de Vídeos — Semana 01 Nov 2026",
        "gerado_em": datetime.now().isoformat(),
        "total": len(resultados),
        "compostos": sum(1 for r in resultados if r.get("status") == "COMPOSTO"),
        "videos": resultados,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "proximo_passo": "Substituir audio placeholder por TTS real + upload YouTube"
    }

    with open(out_dir / "relatorio_composicao.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"\n{'═'*55}")
    compostos = relatorio["compostos"]
    print(f"  RESULTADO: {compostos}/{len(SHORTS)} vídeos compostos")
    for r in resultados:
        icon = "✅" if r.get("status") == "COMPOSTO" else "❌"
        print(f"  {icon} {r['id']} — {r.get('status','?')} "
              f"{'('+str(r.get('tamanho_mb',''))+'MB)' if r.get('tamanho_mb') else ''}")
    print(f"{'═'*55}")
    print(f"\n  Próximo passo: Upload via YouTube Data API v3")
    print(f"  Ou: abrir YouTube Studio e fazer upload manual dos MP4s")
    print(f"  Local: {OUT_DIR.absolute()}\n")
