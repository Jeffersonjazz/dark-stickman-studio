#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║     DARK STUDIO AAA — DARK POSTER AUTO v2.0                  ║
║     Automação completa de postagem no YouTube                 ║
║     Agentes: 📤 ASSET MANAGER | ✅ CREATIVE QA | 🎬 DIRECTOR ║
╚══════════════════════════════════════════════════════════════╝
Fluxo:
  1. Gera narrações PT-BR locais (espeak-ng)
  2. Mixa áudio + vídeo via FFmpeg
  3. Faz upload para YouTube via Data API v3 (OAuth2)
  4. Aplica metadata SEO completo
  5. Define thumbnail personalizado
  6. Agenda ou publica imediatamente
"""

import os, sys, json, time, subprocess, wave, ctypes, struct
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE      = Path("/home/claude/dark-stickman-studio")
OUT_DIR   = BASE / "outputs"
VIDEOS    = OUT_DIR / "videos"
THUMBS    = OUT_DIR / "thumbnails"
AUDIO_DIR = OUT_DIR / "audio"
V2_DIR    = OUT_DIR / "videos_com_audio"
PKG_FILE  = OUT_DIR / "semana01_upload_package.json"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
V2_DIR.mkdir(parents=True, exist_ok=True)

# ── Narração PT-BR por vídeo ───────────────────────────────────────────────────
NARRACAO = {
    "v001": {
        "titulo": "Por Que Você Se Sente Vazio",
        "canal_id": "UCPRWgHoI85u-gmZmS9uVbqA",
        "arquivo_video": "v001_Por_Que_Você_Se_Sente_Vazio.mp4",
        "roteiro": (
            "Você já acordou pela manhã sentindo um vazio inexplicável? "
            "Como se algo estivesse faltando, mas você não consegue identificar o quê. "
            "Esse fenômeno tem um nome científico: vazio existencial. "
            "E acontece com milhões de pessoas todos os dias. "
            "A neurociência descobriu que esse estado está diretamente ligado ao sistema dopaminérgico. "
            "Quando nossas expectativas superam a realidade, o cérebro entra em modo de deficit motivacional. "
            "Viktor Frankl, sobrevivente do holocausto e pai da logoterapia, chamou isso de vácuo existencial. "
            "A busca de sentido é a força primária do ser humano. Quando ela falha, surge o vazio. "
            "Mas aqui está o que a psicologia moderna descobriu: o vazio não é fraqueza. "
            "É um sinal. Um chamado para reconectar com o que realmente importa. "
            "A diferença entre vazio e depressão está na temporalidade e na intensidade. "
            "O vazio é episódico. A depressão é crônica. "
            "Estudos mostram que práticas de mindfulness reduzem em quarenta por cento a sensação de vazio existencial. "
            "Não porque preenchem o vazio. Mas porque ensinam a estar com ele sem lutar contra ele. "
            "O que faz sentido na sua vida hoje? Essa é a pergunta que o vazio está te fazendo. "
            "Inscreva-se no canal. A próxima resposta pode ser exatamente o que você precisa ouvir."
        )
    },
    "v002": {
        "titulo": "Os Bastidores do Tempo",
        "canal_id": "UCMinaADQVJ6QbbhOr_idVdA",
        "arquivo_video": "v002_Os_Bastidores_do_Tempo.mp4",
        "roteiro": (
            "Por trás de cada grande evento histórico, existe uma decisão tomada em silêncio. "
            "Longe das câmeras. Longe dos livros. Nos bastidores onde a história real acontece. "
            "Em 1962, durante a Crise dos Mísseis de Cuba, o mundo esteve a quarenta e oito horas do apocalipse nuclear. "
            "O que os livros não contam é que um único oficial soviético salvou a humanidade. "
            "Vasili Arkhipov recusou autorizar o lançamento de torpedos nucleares de um submarino cercado por navios americanos. "
            "Ele não era presidente. Não era general. Era apenas um homem que disse não. "
            "Em 1989, quando o Muro de Berlim caiu, o mundo viu liberdade e celebração. "
            "Nos bastidores, um mal-entendido burocrático mudou o curso da história. "
            "Um porta-voz leu por engano que as fronteiras abririam imediatamente. "
            "Não era verdade. Mas as pessoas foram para as ruas, e a história teve que seguir. "
            "A grande lição dos bastidores é esta: a história não é feita por forças inevitáveis. "
            "É feita por pessoas, em momentos específicos, com informações incompletas. "
            "Cada decisão pequena pode ter consequências imensas. "
            "O que você decide hoje pode ser o bastidor que a história vai contar amanhã."
        )
    },
    "v003": {
        "titulo": "Intelligentia Nova — A IA Que Muda Tudo",
        "canal_id": "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "arquivo_video": "v003_Intelligentia_Nova.mp4",
        "roteiro": (
            "Existe uma revolução acontecendo agora mesmo. E a maioria das pessoas ainda não percebeu. "
            "A inteligência artificial não é mais ficção científica. É a nova realidade. "
            "Em dois mil e vinte e três, modelos de linguagem como GPT-4 já superavam médicos humanos em diagnósticos específicos. "
            "Em dois mil e vinte e quatro, sistemas de IA começaram a gerar código, música e arte em segundos. "
            "Hoje, pesquisadores estimam que estamos a menos de uma década da Inteligência Artificial Geral. "
            "Uma máquina que pensa como humano. Aprende como humano. E talvez supere o humano. "
            "O impacto no mercado de trabalho é real: quarenta por cento das tarefas rotineiras serão automatizadas até dois mil e trinta. "
            "Mas aqui está o que a mídia mainstream não mostra: cada revolução tecnológica criou mais empregos do que destruiu. "
            "A questão não é se a IA vai mudar tudo. Vai. "
            "A questão é: você vai surfar essa onda ou ser engolido por ela? "
            "Os que entendem a IA hoje terão vantagem enorme amanhã. "
            "Não para competir com máquinas. Mas para dirigí-las. "
            "Inscreva-se. Cada semana, um novo avanço que você precisa conhecer."
        )
    },
    "v004": {
        "titulo": "Projeto Secreto — Arquivos Que Não Deveriam Existir",
        "canal_id": "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "arquivo_video": "v004_Projeto_Secreto.mp4",
        "roteiro": (
            "Existem documentos que governos tentaram apagar da história. "
            "Alguns foram destruídos. Outros foram esquecidos. E alguns... vazaram. "
            "O Projeto MK Ultra foi um programa da CIA que durou vinte e um anos. "
            "Experiências com drogas, hipnose e manipulação mental em cidadãos americanos sem o conhecimento deles. "
            "Em mil novecentos e setenta e três, o diretor da CIA ordenou a destruição de todos os arquivos. "
            "Mas dois mil documentos sobreviveram por acidente. Arquivados no lugar errado. "
            "Em mil novecentos e setenta e sete, o Congresso americano teve que enfrentar a verdade. "
            "O Projeto VENONA revelou que espiões soviéticos haviam se infiltrado no governo americano por décadas. "
            "Incluindo participantes do Projeto Manhattan. A bomba atômica com informações vazadas para a URSS. "
            "O que esses projetos revelam não é que governos são maus. "
            "É que governos são feitos de seres humanos. Com medos, ambições e erros. "
            "E que a verdade, por mais que tentem esconder, sempre encontra um caminho para emergir. "
            "Os arquivos que você não deveria ver. As histórias que precisam ser contadas."
        )
    },
    "v005": {
        "titulo": "AquaZen — O Poder da Água",
        "canal_id": "UC89YZqbZ02RTaT2FYepPHCQ",
        "arquivo_video": "v005_AquaZen_—_O_Poder_da_Água.mp4",
        "roteiro": (
            "A água cobre setenta por cento do planeta. E setenta por cento do corpo humano. "
            "Essa não é uma coincidência. É uma relação profunda que a ciência está apenas começando a entender. "
            "O neurocientista Wallace J. Nichols pesquisou o que chamou de Blue Mind. "
            "O estado mental que acontece quando estamos perto da água. "
            "O cérebro entra em um modo de alerta relaxado. Criativo. Presente. "
            "Estudos mostram que ambientes aquáticos reduzem o cortisol em até quarenta e dois por cento. "
            "O cortisol é o hormônio do estresse. E a água tem o poder natural de diminuí-lo. "
            "Sons de água ativam a rede de modo padrão do cérebro. "
            "A mesma rede ativada durante meditação profunda. "
            "Não é superstição. É neurociência. "
            "Por isso olhar para o oceano nos faz sentir pequenos, mas de um jeito bom. "
            "Por isso uma chuva suave nos acalma sem nenhum esforço. "
            "A água não resolve os problemas. Mas ela nos leva ao estado mental onde soluções emergem naturalmente. "
            "Respira. Fecha os olhos. E deixa a água fazer o que ela sempre soube fazer."
        )
    }
}

# ── Mapa de canais ──────────────────────────────────────────────────────────────
CANAIS = {
    "UCPRWgHoI85u-gmZmS9uVbqA": "Mente de Aço",
    "UCMinaADQVJ6QbbhOr_idVdA": "Bastidores do Tempo",
    "UCoGPdIQM2Bt5zSlV0DW0HQg": "Intelligentia Nova",
    "UCOfXd8Hf_83Y2VHWmj3f3Vg": "Projeto Secreto",
    "UC89YZqbZ02RTaT2FYepPHCQ": "AquaZen Relax",
}


# ══════════════════════════════════════════════════════════════════════════════
#  AGENTE AUDIO MASTER — Geração de narração PT-BR local via espeak-ng
# ══════════════════════════════════════════════════════════════════════════════
def gerar_narracao_espeak(vid_id: str, texto: str, out_wav: Path) -> bool:
    """Gera narração usando espeak-ng via subprocess."""
    # Tenta binário espeak-ng direto
    for cmd in ["espeak-ng", "espeak"]:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True, text=True
            )
        except FileNotFoundError:
            continue
        if result.returncode == 0:
            print(f"  🎙️  {cmd} disponível — gerando narração...")
            proc = subprocess.run([
                cmd,
                "-v", "pt-br",
                "-s", "140",       # velocidade (palavras/min)
                "-p", "45",        # tom (0-99)
                "-a", "180",       # amplitude
                "-g", "8",         # gap entre palavras (ms)
                "-w", str(out_wav),
                texto
            ], capture_output=True, text=True)
            if proc.returncode == 0 and out_wav.exists() and out_wav.stat().st_size > 1000:
                size_kb = out_wav.stat().st_size // 1024
                print(f"  ✅ WAV gerado: {out_wav.name} ({size_kb}KB)")
                return True
            else:
                print(f"  ⚠️  {cmd} falhou: {proc.stderr[:200]}")

    # Fallback: gerar silêncio com metadados (placeholder)
    print(f"  ⚠️  espeak-ng indisponível — gerando placeholder de silêncio...")
    dur_segundos = max(30, len(texto) // 15)  # ~15 chars/segundo PT-BR
    sr = 22050
    n_frames = sr * dur_segundos
    with wave.open(str(out_wav), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        # Silêncio com pequeno pulso de teste a cada 5s
        frames = bytearray(n_frames * 2)
        for i in range(0, n_frames, sr * 5):
            if i < len(frames) - 2:
                frames[i]   = 0x00
                frames[i+1] = 0x10  # pequeno pulso
        wf.writeframes(bytes(frames))
    print(f"  ⚠️  Placeholder ({dur_segundos}s) — substitua pela narração real antes do upload")
    return False  # indica que é placeholder


# ══════════════════════════════════════════════════════════════════════════════
#  AGENTE VIDEO EDITOR PRO — Mixagem áudio + vídeo
# ══════════════════════════════════════════════════════════════════════════════
def mixar_audio_video(vid_id: str, video_path: Path, audio_wav: Path) -> Path | None:
    """Mixa narração com vídeo usando FFmpeg."""
    out_path = V2_DIR / video_path.name.replace(".mp4", "_narrado.mp4")

    print(f"  🎬  Mixando: {video_path.name}")
    # FFmpeg: combina vídeo original (baixo volume) + narração (alto)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_wav),
        "-filter_complex",
        "[0:a]volume=0.15[orig];"       # áudio original bem baixo
        "[1:a]volume=1.0[narr];"         # narração em destaque
        "[orig][narr]amix=inputs=2:duration=longest:dropout_transition=3[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        str(out_path)
    ]
    # Se vídeo não tem áudio, usa narração direta
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", str(video_path)],
        capture_output=True, text=True
    )
    has_audio = '"codec_type": "audio"' in probe.stdout

    if not has_audio:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_wav),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            str(out_path)
        ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0 and out_path.exists():
        size_mb = out_path.stat().st_size / 1_000_000
        print(f"  ✅ Vídeo narrado: {out_path.name} ({size_mb:.1f}MB)")
        return out_path
    else:
        print(f"  ❌ FFmpeg falhou: {proc.stderr[-300:]}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  AGENTE ASSET MANAGER — Upload YouTube via Data API v3
# ══════════════════════════════════════════════════════════════════════════════
def upload_youtube(video_path: Path, metadata: dict, credentials_file: str = "credentials/youtube_token.json") -> str | None:
    """
    Faz upload do vídeo para YouTube via Data API v3.
    Requer: google-api-python-client, google-auth-oauthlib
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import pickle
    except ImportError:
        print("  ⚠️  Instalando google-api-python-client...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--break-system-packages", "-q",
            "google-api-python-client", "google-auth-oauthlib", "google-auth-httplib2"
        ])
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

    creds_path = BASE / credentials_file
    if not creds_path.exists():
        print(f"\n  ❌ CREDENCIAIS NÃO ENCONTRADAS: {creds_path}")
        print("  📋 Para configurar:")
        print("     1. Acesse: https://console.cloud.google.com/apis/credentials")
        print("     2. Crie um OAuth 2.0 Client ID (Desktop app)")
        print("     3. Baixe o JSON e salve em: credentials/youtube_client_secret.json")
        print("     4. Execute: python3 producao/dark_poster_auto.py --auth")
        return None

    creds = Credentials.from_authorized_user_file(str(creds_path), [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": metadata["titulo_principal"],
            "description": metadata["descricao"],
            "tags": metadata["tags"],
            "categoryId": metadata["categoria"],
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR",
        },
        "status": {
            "privacyStatus": metadata.get("visibilidade", "public"),
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=5 * 1024 * 1024)
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"  📤  Enviando para YouTube: {video_path.name}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  ⏳  Upload: {pct}%", end="\r")

    video_id = response.get("id")
    print(f"  ✅  Upload concluído! ID: {video_id}")
    print(f"  🔗  https://youtu.be/{video_id}")
    return video_id


def set_thumbnail(video_id: str, thumb_path: Path, credentials_file: str = "credentials/youtube_token.json"):
    """Define thumbnail personalizado."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = Credentials.from_authorized_user_file(
            str(BASE / credentials_file),
            ["https://www.googleapis.com/auth/youtube.force-ssl"]
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        youtube = build("youtube", "v3", credentials=creds)
        media = MediaFileUpload(str(thumb_path), mimetype="image/jpeg")
        youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
        print(f"  ✅  Thumbnail definido para {video_id}")
    except Exception as e:
        print(f"  ⚠️  Thumbnail falhou: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  AGENTE CREATIVE QA — Verificação pré-upload
# ══════════════════════════════════════════════════════════════════════════════
def verificar_video(video_path: Path) -> dict:
    """Verifica qualidade do vídeo antes do upload."""
    result = {"ok": False, "erros": [], "info": {}}
    if not video_path.exists():
        result["erros"].append(f"Arquivo não encontrado: {video_path}")
        return result
    size_mb = video_path.stat().st_size / 1_000_000
    if size_mb < 0.1:
        result["erros"].append(f"Arquivo muito pequeno: {size_mb:.2f}MB")
        return result
    if size_mb > 256 * 1024:  # 256GB limite YouTube
        result["erros"].append(f"Arquivo muito grande: {size_mb:.0f}MB")
        return result
    # FFprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(video_path)],
        capture_output=True, text=True
    )
    if probe.returncode == 0:
        data = json.loads(probe.stdout)
        fmt = data.get("format", {})
        dur = float(fmt.get("duration", 0))
        result["info"] = {
            "duracao_s": round(dur, 1),
            "tamanho_mb": round(size_mb, 1),
            "bitrate_kbps": round(int(fmt.get("bit_rate", 0)) / 1000, 0)
        }
        if dur < 10:
            result["erros"].append(f"Duração muito curta: {dur:.1f}s")
    result["ok"] = len(result["erros"]) == 0
    return result


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════
def rodar_pipeline(vid_ids: list = None, pular_narracao: bool = False, pular_upload: bool = False):
    """Pipeline completo: narração → mixagem → QA → upload → thumbnail."""
    pkg = json.loads(PKG_FILE.read_text(encoding="utf-8"))
    videos_meta = {v["id"]: v for v in pkg["videos"]}

    if vid_ids is None:
        vid_ids = list(NARRACAO.keys())

    resultados = []
    print("\n" + "═" * 62)
    print("  🎬  DARK POSTER AUTO — Pipeline de Postagem Semana 01")
    print("═" * 62)

    for vid_id in vid_ids:
        info = NARRACAO[vid_id]
        meta = videos_meta.get(vid_id, {})
        canal_nome = CANAIS.get(info["canal_id"], "?")
        print(f"\n▶ [{vid_id}] {info['titulo']} → {canal_nome}")
        print("─" * 50)

        resultado = {"id": vid_id, "status": "ok", "erros": []}

        # 1. AGENTE AUDIO MASTER — Narração
        audio_wav = AUDIO_DIR / f"{vid_id}_narracao.wav"
        narracao_real = True
        if not pular_narracao and not audio_wav.exists():
            print("  🎙️  [AUDIO MASTER] Gerando narração PT-BR...")
            narracao_real = gerar_narracao_espeak(vid_id, info["roteiro"], audio_wav)
        elif audio_wav.exists():
            print(f"  ✅  Narração existente: {audio_wav.name}")

        # 2. AGENTE VIDEO EDITOR PRO — Mixagem
        video_src = VIDEOS / info["arquivo_video"]
        if not video_src.exists():
            # Tenta nome alternativo
            alternativas = list(VIDEOS.glob(f"{vid_id}_*.mp4"))
            if alternativas:
                video_src = alternativas[0]
                print(f"  🔄  Alternativa: {video_src.name}")
            else:
                resultado["erros"].append(f"Vídeo não encontrado: {info['arquivo_video']}")
                resultado["status"] = "erro"
                resultados.append(resultado)
                continue

        video_final = V2_DIR / f"{vid_id}_final.mp4"
        if not video_final.exists():
            if audio_wav.exists():
                print("  🎬  [VIDEO EDITOR PRO] Mixando áudio + vídeo...")
                v = mixar_audio_video(vid_id, video_src, audio_wav)
                if v:
                    video_final = v
                else:
                    video_final = video_src  # usa original se falhar
            else:
                video_final = video_src
        else:
            print(f"  ✅  Vídeo final existente: {video_final.name}")

        # 3. AGENTE CREATIVE QA — Verificação
        print("  ✅  [CREATIVE QA] Verificando qualidade...")
        qa = verificar_video(video_final)
        if qa["ok"]:
            info_v = qa["info"]
            print(f"  ✅  QA OK: {info_v.get('duracao_s')}s | {info_v.get('tamanho_mb')}MB")
        else:
            print(f"  ❌  QA FALHOU: {'; '.join(qa['erros'])}")
            resultado["erros"].extend(qa["erros"])

        resultado["video_final"] = str(video_final)
        resultado["qa"] = qa

        # 4. AGENTE ASSET MANAGER — Upload YouTube
        if not pular_upload:
            print("  📤  [ASSET MANAGER] Iniciando upload YouTube...")
            video_id = upload_youtube(video_final, meta)
            resultado["youtube_video_id"] = video_id

            if video_id:
                # 5. Thumbnail
                thumb = THUMBS / f"{vid_id}_thumbnail.jpg"
                if thumb.exists():
                    set_thumbnail(video_id, thumb)
                resultado["youtube_url"] = f"https://youtu.be/{video_id}"
                resultado["status"] = "publicado"
            else:
                resultado["status"] = "aguardando_credenciais"
        else:
            print("  ⏭️   Upload pulado (modo --dry-run)")
            resultado["status"] = "pronto_para_upload"

        resultados.append(resultado)

    # Salva relatório
    relatorio = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "resultados": resultados
    }
    rel_path = OUT_DIR / "relatorio_postagem.json"
    rel_path.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "═" * 62)
    ok  = sum(1 for r in resultados if r["status"] in ("publicado", "pronto_para_upload"))
    print(f"  📊  RESULTADO: {ok}/{len(resultados)} vídeos processados")
    for r in resultados:
        icon = "✅" if r["status"] == "publicado" else "📦" if "pronto" in r["status"] else "❌"
        url  = r.get("youtube_url", r.get("video_final", ""))
        print(f"  {icon}  {r['id']}: {r['status']} — {url}")
    print(f"\n  📄  Relatório: {rel_path}")
    print("═" * 62)
    return resultados


# ══════════════════════════════════════════════════════════════════════════════
#  SETUP DE AUTENTICAÇÃO YOUTUBE
# ══════════════════════════════════════════════════════════════════════════════
def setup_oauth():
    """Guia o usuário pelo setup de OAuth2 para YouTube API v3."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     DARK POSTER AUTO — SETUP DE AUTENTICAÇÃO YOUTUBE         ║
╚══════════════════════════════════════════════════════════════╝

PASSO A PASSO:

1. Acesse o Google Cloud Console:
   https://console.cloud.google.com/

2. Crie um projeto ou selecione "DARK STUDIO AAA"

3. Ative a YouTube Data API v3:
   APIs & Services → Library → YouTube Data API v3 → Enable

4. Crie credenciais OAuth 2.0:
   APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
   Tipo: Desktop app
   Nome: DARK POSTER AUTO

5. Baixe o arquivo JSON das credenciais
   Salve como: /home/claude/dark-stickman-studio/credentials/youtube_client_secret.json

6. Execute a autenticação:
   python3 producao/dark_poster_auto.py --auth

7. O browser abrirá para você autorizar. Faça login com a conta
   dos canais: jefferson75elaine@gmail.com

8. O token será salvo automaticamente em:
   credentials/youtube_token.json

Após isso, execute:
   python3 producao/dark_poster_auto.py --upload
""")

    # Se o client_secret existir, faz o fluxo OAuth
    secret_file = BASE / "credentials/youtube_client_secret.json"
    if secret_file.exists():
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            SCOPES = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
            flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
            creds = flow.run_local_server(port=0)
            token_path = BASE / "credentials/youtube_token.json"
            token_path.parent.mkdir(exist_ok=True)
            token_path.write_text(creds.to_json())
            print(f"\n  ✅  Token salvo: {token_path}")
        except Exception as e:
            print(f"\n  ❌  Erro no OAuth: {e}")
    else:
        print(f"\n  ⚠️  Arquivo não encontrado: {secret_file}")
        print("  Siga os passos acima primeiro.")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DARK POSTER AUTO — Postagem automática YouTube")
    parser.add_argument("--auth",           action="store_true", help="Configura autenticação OAuth2")
    parser.add_argument("--dry-run",        action="store_true", help="Processa sem fazer upload")
    parser.add_argument("--so-audio",       action="store_true", help="Gera só as narrações")
    parser.add_argument("--video",          type=str, default=None, help="Processa só este vídeo (v001..v005)")
    parser.add_argument("--pular-narracao", action="store_true", help="Usa vídeos já processados")
    args = parser.parse_args()

    if args.auth:
        setup_oauth()
    elif args.so_audio:
        for vid_id, info in NARRACAO.items():
            audio_wav = AUDIO_DIR / f"{vid_id}_narracao.wav"
            print(f"\n🎙️  [{vid_id}] {info['titulo']}")
            gerar_narracao_espeak(vid_id, info["roteiro"], audio_wav)
    else:
        vid_ids = [args.video] if args.video else None
        rodar_pipeline(
            vid_ids=vid_ids,
            pular_narracao=args.pular_narracao,
            pular_upload=args.dry_run
        )
