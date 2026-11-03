#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   DARK YOUTUBE UPLOADER — SOLUÇÃO GRATUITA                  ║
║   DARK STUDIO AAA v1.4.0                                    ║
║                                                              ║
║   MÉTODO: YouTube Data API v3 + Device Flow OAuth2          ║
║   CUSTO:  R$ 0,00 — 100% gratuito                          ║
║   SEM:    servidor, redirect URI, hospedagem                ║
║                                                              ║
║   Agentes: VIDEO EDITOR PRO · ASSET MANAGER · CREATIVE QA  ║
╚══════════════════════════════════════════════════════════════╝

COMO FUNCIONA (Device Flow):
  1. Script pede um código ao Google
  2. Você abre uma URL no navegador e digita o código
  3. Script detecta aprovação e salva o token
  4. Upload automático de todos os vídeos

SETUP ÚNICO (gratuito):
  1. Acesse: https://console.cloud.google.com/
  2. Crie projeto → Ative "YouTube Data API v3"
  3. Credenciais → OAuth 2.0 → Tipo: "Aplicativo para TV e dispositivos limitados"
  4. Copie o CLIENT_ID e CLIENT_SECRET
  5. Cole abaixo em DEVICE_CLIENT_ID e DEVICE_CLIENT_SECRET
  6. Execute: python3 dark_youtube_uploader.py --auth
  7. Depois:  python3 dark_youtube_uploader.py --upload-todos

ai_generated: True
ai_disclosure: "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
"""

import os
import sys
import json
import time
import subprocess
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime

# ── CONFIGURAÇÃO — preencha após criar credenciais gratuitas ─────────────
# Tipo de credencial: "Aplicativo para TV e dispositivos limitados"
DEVICE_CLIENT_ID     = os.environ.get("YT_CLIENT_ID", "SEU_CLIENT_ID_AQUI")
DEVICE_CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET", "SEU_CLIENT_SECRET_AQUI")

# ── Caminhos ──────────────────────────────────────────────────────────────
BASE         = Path(__file__).parent.parent
VIDEOS_DIR   = BASE / "outputs" / "videos_finais"
THUMBS_DIR   = BASE / "outputs" / "thumbnails"
CREDS_DIR    = BASE / "credentials"
TOKEN_FILE   = CREDS_DIR / "youtube_token.json"
UPLOAD_LOG   = BASE / "outputs" / "relatorio_upload.json"
CREDS_DIR.mkdir(parents=True, exist_ok=True)

# ── URLs da API ───────────────────────────────────────────────────────────
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL       = "https://oauth2.googleapis.com/token"
UPLOAD_URL      = "https://www.googleapis.com/upload/youtube/v3/videos"
THUMB_URL       = "https://www.googleapis.com/youtube/v3/thumbnails/set"
SCOPES          = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"

# ── Mapeamento vídeo → canal ──────────────────────────────────────────────
VIDEOS = {
    "v001": {
        "arquivo":    "v001_final.mp4",
        "thumbnail":  "v001_thumb.jpg",
        "canal_id":   "UCPRWgHoI85u-gmZmS9uVbqA",
        "canal_nome": "Mente de Aço",
        "titulo":     "Por Que Você Se Sente Vazio? A Resposta Que Ninguém Te Deu",
        "descricao":  (
            "Você acorda cedo, cumpre suas obrigações, faz tudo certo — "
            "mas ainda assim sente um vazio inexplicável por dentro.\n\n"
            "Neste vídeo, vamos explorar as razões psicológicas por trás "
            "dessa sensação e como construir uma vida com mais significado.\n\n"
            "🧠 Mente de Aço — Psicologia aplicada à vida real.\n\n"
            "#psicologia #mentedeaco #autoconhecimento #desenvolvimento #motivacao\n\n"
            "⚠️ Conteúdo produzido com DARK STUDIO AAA — IA Generativa."
        ),
        "tags":       ["psicologia", "vazio existencial", "autoconhecimento", "motivacao", "mente", "desenvolvimento pessoal"],
        "categoria":  "22",  # People & Blogs
        "privacidade": "public",
    },
    "v002": {
        "arquivo":    "v002_final.mp4",
        "thumbnail":  "v002_thumb.jpg",
        "canal_id":   "UCMinaADQVJ6QbbhOr_idVdA",
        "canal_nome": "Bastidores do Tempo",
        "titulo":     "Os Bastidores do Tempo: O Que a História Oficial Não Conta",
        "descricao":  (
            "Por trás de cada grande evento histórico, existem segredos, "
            "contradições e histórias que foram apagadas dos livros.\n\n"
            "Mergulhe nos bastidores do tempo e descubra o que realmente aconteceu.\n\n"
            "📜 Bastidores do Tempo — História sem filtros.\n\n"
            "#historia #documentario #bastidores #misterios #passado\n\n"
            "⚠️ Conteúdo produzido com DARK STUDIO AAA — IA Generativa."
        ),
        "tags":       ["historia", "documentario", "bastidores", "misterios historicos", "passado"],
        "categoria":  "27",  # Education
        "privacidade": "public",
    },
    "v003": {
        "arquivo":    "v003_final.mp4",
        "thumbnail":  "v003_thumb.jpg",
        "canal_id":   "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "canal_nome": "Intelligentia Nova",
        "titulo":     "Intelligentia Nova: A Revolução da IA Que Vai Mudar Tudo em 2025",
        "descricao":  (
            "A inteligência artificial está avançando em uma velocidade sem precedentes. "
            "Quais são as implicações reais para o futuro da humanidade?\n\n"
            "🤖 Intelligentia Nova — Tecnologia e IA sem jargões.\n\n"
            "#inteligenciaartificial #ia #tecnologia #futuro #inovacao\n\n"
            "⚠️ Conteúdo produzido com DARK STUDIO AAA — IA Generativa."
        ),
        "tags":       ["inteligencia artificial", "ia", "tecnologia", "futuro", "inovacao", "machine learning"],
        "categoria":  "28",  # Science & Technology
        "privacidade": "public",
    },
    "v004": {
        "arquivo":    "v004_final.mp4",
        "thumbnail":  "v004_thumb.jpg",
        "canal_id":   "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "canal_nome": "Projeto Secreto",
        "titulo":     "Projeto Secreto: O Que Eles Não Querem Que Você Saiba",
        "descricao":  (
            "Existem projetos, experimentos e documentos que permaneceram "
            "ocultos por décadas. Hoje vamos revelar o que estava escondido.\n\n"
            "🔴 Projeto Secreto — O que está além do véu.\n\n"
            "#projetosecreto #misterio #conspiracoes #segredos #oculto\n\n"
            "⚠️ Conteúdo produzido com DARK STUDIO AAA — IA Generativa. "
            "As informações apresentadas são de caráter especulativo e educativo."
        ),
        "tags":       ["misterio", "projeto secreto", "conspiracao", "segredos", "oculto", "documentario"],
        "categoria":  "22",  # People & Blogs
        "privacidade": "public",
    },
    "v005": {
        "arquivo":    "v005_final.mp4",
        "thumbnail":  "v005_thumb.jpg",
        "canal_id":   "UC89YZqbZ02RTaT2FYepPHCQ",
        "canal_nome": "AquaZen Relax",
        "titulo":     "AquaZen: Sons da Natureza Para Relaxar, Dormir e Meditar 🌿",
        "descricao":  (
            "Deixe-se levar pelos sons relaxantes da natureza. "
            "Perfeito para meditação, sono profundo, foco e bem-estar.\n\n"
            "💚 AquaZen Relax — Paz que você merece.\n\n"
            "#relaxamento #natureza #meditacao #sono #aquazen #lofi\n\n"
            "⚠️ Conteúdo produzido com DARK STUDIO AAA — IA Generativa."
        ),
        "tags":       ["relaxamento", "natureza", "meditacao", "sono", "zen", "aquazen", "lofi", "asmr"],
        "categoria":  "22",  # People & Blogs
        "privacidade": "public",
    },
}


# ═════════════════════════════════════════════════════════════════════════════
# DEVICE FLOW OAUTH2 — 100% GRATUITO
# ═════════════════════════════════════════════════════════════════════════════

def _post(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def autenticar() -> dict:
    """Device Flow: abre URL no navegador, aguarda aprovação, salva token."""

    if DEVICE_CLIENT_ID == "SEU_CLIENT_ID_AQUI":
        print("""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  CONFIGURAÇÃO NECESSÁRIA — APENAS UMA VEZ              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Acesse: https://console.cloud.google.com/               ║
║  2. Crie um projeto (ex: "dark-studio-upload")              ║
║  3. APIs → Ativar "YouTube Data API v3" (GRATUITO)         ║
║  4. Credenciais → Criar OAuth 2.0                           ║
║     Tipo: "Aplicativo para TV e dispositivos limitados"     ║
║  5. Copie o CLIENT_ID e CLIENT_SECRET                       ║
║  6. Execute:                                                 ║
║                                                              ║
║     export YT_CLIENT_ID="seu_client_id"                     ║
║     export YT_CLIENT_SECRET="seu_client_secret"             ║
║     python3 producao/dark_youtube_uploader.py --auth        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
        sys.exit(1)

    print("  [AUTH] 🔑 Solicitando código de dispositivo ao Google...")
    resp = _post(DEVICE_CODE_URL, {
        "client_id": DEVICE_CLIENT_ID,
        "scope":     SCOPES,
    })

    device_code   = resp["device_code"]
    user_code     = resp["user_code"]
    verify_url    = resp.get("verification_url", "https://google.com/device")
    interval      = resp.get("interval", 5)
    expires_in    = resp.get("expires_in", 1800)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🌐 AUTENTICAÇÃO YOUTUBE — ABRA NO NAVEGADOR               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  URL:    {verify_url:<50} ║
║  CÓDIGO: {user_code:<50} ║
║                                                              ║
║  1. Abra a URL acima no navegador                           ║
║  2. Digite o código acima                                   ║
║  3. Faça login com: jefferson75elaine@gmail.com             ║
║  4. Clique em "Permitir"                                    ║
║  5. Aguarde — este script detecta automaticamente           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token_resp = _post(TOKEN_URL, {
                "client_id":     DEVICE_CLIENT_ID,
                "client_secret": DEVICE_CLIENT_SECRET,
                "device_code":   device_code,
                "grant_type":    "urn:ietf:params:oauth2:grant-type:device_code",
            })
        except Exception:
            continue

        if "access_token" in token_resp:
            token_resp["expires_at"] = time.time() + token_resp.get("expires_in", 3600)
            token_resp["client_id"]     = DEVICE_CLIENT_ID
            token_resp["client_secret"] = DEVICE_CLIENT_SECRET
            TOKEN_FILE.write_text(json.dumps(token_resp, indent=2))
            print(f"  [AUTH] ✅ Autenticado! Token salvo em {TOKEN_FILE}")
            return token_resp

        error = token_resp.get("error", "")
        if error == "authorization_pending":
            print("  [AUTH] ⏳ Aguardando aprovação...", end="\r")
        elif error == "slow_down":
            interval += 5
        elif error in ("expired_token", "access_denied"):
            print(f"\n  [AUTH] ❌ {error} — tente novamente.")
            sys.exit(1)

    print("\n  [AUTH] ❌ Tempo esgotado. Execute --auth novamente.")
    sys.exit(1)


def carregar_token() -> dict:
    """Carrega token salvo, renova se expirado."""
    if not TOKEN_FILE.exists():
        print("  [AUTH] ❌ Token não encontrado. Execute: python3 ... --auth")
        sys.exit(1)

    token = json.loads(TOKEN_FILE.read_text())

    # Renovar se expirado
    if time.time() >= token.get("expires_at", 0) - 60:
        print("  [AUTH] 🔄 Token expirado, renovando...")
        resp = _post(TOKEN_URL, {
            "client_id":     token["client_id"],
            "client_secret": token["client_secret"],
            "refresh_token": token["refresh_token"],
            "grant_type":    "refresh_token",
        })
        token["access_token"] = resp["access_token"]
        token["expires_at"]   = time.time() + resp.get("expires_in", 3600)
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
        print("  [AUTH] ✅ Token renovado.")

    return token


# ═════════════════════════════════════════════════════════════════════════════
# UPLOAD RESUMABLE — YouTube Data API v3
# ═════════════════════════════════════════════════════════════════════════════

def fazer_upload(vid_id: str, token: dict) -> dict:
    """Upload resumable de um vídeo para o canal correto."""
    dados  = VIDEOS[vid_id]
    access = token["access_token"]

    video_path = VIDEOS_DIR / dados["arquivo"]
    thumb_path = THUMBS_DIR / dados["thumbnail"]

    if not video_path.exists():
        return {"vid_id": vid_id, "status": "erro", "motivo": f"arquivo não encontrado: {video_path}"}

    tamanho = video_path.stat().st_size
    print(f"\n  [UPLOAD] 🎬 {vid_id}: {dados['titulo'][:50]}...")
    print(f"  [UPLOAD] 📺 Canal: {dados['canal_nome']}")
    print(f"  [UPLOAD] 📦 Tamanho: {tamanho/1024/1024:.1f} MB")

    # Metadados do vídeo
    metadata = {
        "snippet": {
            "title":       dados["titulo"],
            "description": dados["descricao"],
            "tags":        dados["tags"],
            "categoryId":  dados["categoria"],
        },
        "status": {
            "privacyStatus":           dados["privacidade"],
            "selfDeclaredMadeForKids": False,
        },
    }

    meta_json = json.dumps(metadata).encode("utf-8")

    # 1. Iniciar sessão resumable
    init_req = urllib.request.Request(
        f"{UPLOAD_URL}?uploadType=resumable&part=snippet,status",
        data=meta_json,
        method="POST",
    )
    init_req.add_header("Authorization",        f"Bearer {access}")
    init_req.add_header("Content-Type",         "application/json; charset=UTF-8")
    init_req.add_header("X-Upload-Content-Type","video/mp4")
    init_req.add_header("X-Upload-Content-Length", str(tamanho))

    try:
        with urllib.request.urlopen(init_req, timeout=30) as r:
            upload_uri = r.getheader("Location")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"vid_id": vid_id, "status": "erro", "motivo": f"HTTP {e.code}: {body[:200]}"}

    if not upload_uri:
        return {"vid_id": vid_id, "status": "erro", "motivo": "sem Location header"}

    print(f"  [UPLOAD] 🚀 Enviando vídeo... (pode demorar alguns minutos)")

    # 2. Enviar arquivo em chunks de 50MB
    chunk_size = 50 * 1024 * 1024
    enviado    = 0
    video_id   = None

    with open(video_path, "rb") as f:
        while enviado < tamanho:
            chunk = f.read(chunk_size)
            fim   = enviado + len(chunk) - 1

            upload_req = urllib.request.Request(upload_uri, data=chunk, method="PUT")
            upload_req.add_header("Authorization",  f"Bearer {access}")
            upload_req.add_header("Content-Type",   "video/mp4")
            upload_req.add_header("Content-Length", str(len(chunk)))
            upload_req.add_header("Content-Range",  f"bytes {enviado}-{fim}/{tamanho}")

            pct = int((enviado + len(chunk)) / tamanho * 100)
            print(f"  [UPLOAD] ⬆️  {pct}% enviado...", end="\r")

            try:
                with urllib.request.urlopen(upload_req, timeout=120) as r:
                    if r.status in (200, 201):
                        resp_data  = json.loads(r.read())
                        video_id   = resp_data.get("id")
            except urllib.error.HTTPError as e:
                if e.code == 308:  # Resume Incomplete — continua
                    range_hdr = e.headers.get("Range", "")
                    if range_hdr:
                        enviado = int(range_hdr.split("-")[1]) + 1
                    else:
                        enviado += len(chunk)
                    continue
                else:
                    body = e.read().decode()
                    return {"vid_id": vid_id, "status": "erro", "motivo": f"HTTP {e.code}: {body[:200]}"}

            enviado += len(chunk)

    if not video_id:
        return {"vid_id": vid_id, "status": "erro", "motivo": "video_id não retornado"}

    url_video = f"https://youtu.be/{video_id}"
    print(f"\n  [UPLOAD] ✅ Vídeo publicado: {url_video}")

    # 3. Upload da thumbnail
    if thumb_path.exists():
        print(f"  [UPLOAD] 🖼️  Enviando thumbnail...")
        thumb_data = thumb_path.read_bytes()
        thumb_req  = urllib.request.Request(
            f"{THUMB_URL}?videoId={video_id}",
            data=thumb_data, method="POST"
        )
        thumb_req.add_header("Authorization",  f"Bearer {access}")
        thumb_req.add_header("Content-Type",   "image/jpeg")
        thumb_req.add_header("Content-Length", str(len(thumb_data)))
        try:
            with urllib.request.urlopen(thumb_req, timeout=60):
                print(f"  [UPLOAD] ✅ Thumbnail aplicada.")
        except Exception as e:
            print(f"  [UPLOAD] ⚠️  Thumbnail falhou: {e}")

    return {
        "vid_id":    vid_id,
        "video_id":  video_id,
        "url":       url_video,
        "canal":     dados["canal_nome"],
        "titulo":    dados["titulo"],
        "status":    "publicado",
        "timestamp": datetime.now().isoformat(),
        "ai_generated":  True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def upload_todos() -> list:
    """Faz upload de todos os 5 vídeos."""
    print("""
╔══════════════════════════════════════════════════════════╗
║  🚀 DARK YOUTUBE UPLOADER — UPLOAD SEMANA 01           ║
║  5 vídeos → 5 canais — 100% GRATUITO                  ║
╚══════════════════════════════════════════════════════════╝
""")
    token = carregar_token()
    resultados = []

    for vid_id in VIDEOS:
        r = fazer_upload(vid_id, token)
        resultados.append(r)
        if r["status"] == "publicado":
            print(f"  ✅ {vid_id}: {r['url']}")
        else:
            print(f"  ❌ {vid_id}: {r['motivo']}")
        time.sleep(3)  # respeitar rate limit

    # Salvar relatório
    log = {
        "semana":    "01",
        "timestamp": datetime.now().isoformat(),
        "total":     len(resultados),
        "publicados": sum(1 for r in resultados if r["status"] == "publicado"),
        "erros":     sum(1 for r in resultados if r["status"] != "publicado"),
        "videos":    resultados,
        "ai_generated":  True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
    UPLOAD_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2))

    print(f"""
════════════════════════════════════════════════════════════
  📊 RESULTADO UPLOAD SEMANA 01:
  ✅ Publicados: {log['publicados']}/5
  ❌ Erros:      {log['erros']}/5
  📄 Log: {UPLOAD_LOG}
════════════════════════════════════════════════════════════
""")
    return resultados


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="DARK YOUTUBE UPLOADER — Upload gratuito via Device Flow OAuth2"
    )
    parser.add_argument("--auth",         action="store_true", help="Autenticar com o Google (uma vez)")
    parser.add_argument("--upload-todos", action="store_true", help="Fazer upload de todos os vídeos")
    parser.add_argument("--upload",       metavar="VID_ID",   help="Fazer upload de um vídeo específico")
    parser.add_argument("--listar",       action="store_true", help="Listar vídeos configurados")
    parser.add_argument("--status-token", action="store_true", help="Verificar token salvo")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║   DARK YOUTUBE UPLOADER — DARK STUDIO AAA v1.4.0           ║
║   Solução 100% Gratuita — Device Flow OAuth2               ║
╚══════════════════════════════════════════════════════════════╝
""")

    if args.listar:
        print("  Vídeos configurados:")
        for vid_id, d in VIDEOS.items():
            v = VIDEOS_DIR / d["arquivo"]
            existe = "✅" if v.exists() else "❌"
            sz = f"{v.stat().st_size/1024/1024:.1f}MB" if v.exists() else "—"
            print(f"  {existe} {vid_id}: {d['titulo'][:50]} [{d['canal_nome']}] {sz}")
        return

    if args.status_token:
        if TOKEN_FILE.exists():
            t = json.loads(TOKEN_FILE.read_text())
            exp = datetime.fromtimestamp(t.get("expires_at", 0))
            print(f"  Token: {'✅ válido' if time.time() < t.get('expires_at',0) else '⚠️ expirado (auto-renova)'}")
            print(f"  Expira: {exp.strftime('%d/%m/%Y %H:%M')}")
        else:
            print("  ❌ Nenhum token — execute: --auth")
        return

    if args.auth:
        autenticar()
        return

    if args.upload_todos:
        upload_todos()
        return

    if args.upload:
        if args.upload not in VIDEOS:
            print(f"  ❌ {args.upload} não encontrado. Use --listar para ver os disponíveis.")
            return
        token = carregar_token()
        r = fazer_upload(args.upload, token)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    # Sem args: mostrar ajuda
    parser.print_help()
    print("""
  GUIA RÁPIDO (gratuito):
  ─────────────────────────────────────────────────────────
  1. Obtenha credenciais GRATUITAS:
     https://console.cloud.google.com/
     → YouTube Data API v3 → OAuth 2.0 → "TV e dispositivos"

  2. Configure:
     export YT_CLIENT_ID="seu_id"
     export YT_CLIENT_SECRET="seu_secret"

  3. Autentique (1x por conta):
     python3 producao/dark_youtube_uploader.py --auth

  4. Faça o upload:
     python3 producao/dark_youtube_uploader.py --upload-todos
  ─────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    main()
