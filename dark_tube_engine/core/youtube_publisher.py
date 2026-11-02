"""
DARK TUBE ENGINE — YouTube Publisher (clone vidiq_video_upload + vidiq_update_video)
Agente: ASSET MANAGER
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import pickle
    YOUTUBE_UPLOAD_AVAILABLE = True
except ImportError:
    YOUTUBE_UPLOAD_AVAILABLE = False

# Escopos necessários para upload + update
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

# Categorias YouTube (IDs oficiais)
CATEGORIAS = {
    "Educação": "27",
    "Entretenimento": "24",
    "Ciência e Tecnologia": "28",
    "Pessoas e Blogs": "22",
    "Viagens e Eventos": "19",
    "Música": "10",
    "Filmes e Animação": "1",
    "Notícias e Política": "25"
}

# Configurações de monetização por canal
CONFIG_CANAIS = {
    "Mente de Aço": {"categoria": "22", "tags_base": ["psicologia", "motivação", "mente", "sucesso"]},
    "Esquina do Medo": {"categoria": "24", "tags_base": ["terror", "medo", "história assombrada", "suspense"]},
    "Intelligentia Nova": {"categoria": "28", "tags_base": ["inteligência artificial", "tecnologia", "ia", "futuro"]},
    "Projeto Secreto": {"categoria": "25", "tags_base": ["conspiração", "segredos", "governo", "revelado"]},
    "AquaZen Relax": {"categoria": "19", "tags_base": ["relaxamento", "natureza", "meditação", "água"]},
}


def autenticar_youtube(credentials_path: str = "config/client_secrets.json",
                        token_path: str = "config/token.pickle") -> object:
    """
    Autentica com YouTube Data API v3 via OAuth2
    Clone da lógica vidiq_authorize_with_youtube + vidiq_connect_youtube_channel
    """
    if not YOUTUBE_UPLOAD_AVAILABLE:
        raise ImportError("Instale: pip install google-auth google-auth-oauthlib google-api-python-client")

    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def fazer_upload_video(
    youtube,
    video_path: str,
    titulo: str,
    descricao: str,
    canal: str = "",
    tags: list = None,
    categoria_id: str = "22",
    privacidade: str = "public",
    thumbnail_path: Optional[str] = None,
    made_for_kids: bool = False
) -> dict:
    """
    Faz upload de vídeo para YouTube — clone do vidiq_video_upload
    Retorna video_id e URL
    """
    config_canal = CONFIG_CANAIS.get(canal, {})
    tags_finais = (config_canal.get("tags_base", []) + (tags or []))[:500]
    categoria_final = config_canal.get("categoria", categoria_id)

    body = {
        "snippet": {
            "title": titulo[:100],
            "description": descricao[:5000],
            "tags": tags_finais,
            "categoryId": categoria_final,
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR"
        },
        "status": {
            "privacyStatus": privacidade,
            "selfDeclaredMadeForKids": made_for_kids,
            "madeForKids": made_for_kids
        }
    }

    media = MediaFileUpload(
        video_path,
        chunksize=1024 * 1024,
        resumable=True,
        mimetype="video/mp4"
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    shorts_url = f"https://www.youtube.com/shorts/{video_id}"

    # Upload thumbnail se fornecida
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
        except Exception as e:
            pass  # Thumbnail não é crítica

    return {
        "status": "published",
        "video_id": video_id,
        "url": url,
        "shorts_url": shorts_url,
        "titulo": titulo,
        "canal": canal,
        "privacidade": privacidade,
        "publicado_em": datetime.now().isoformat(),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }


def atualizar_metadados_video(
    youtube,
    video_id: str,
    titulo: str = None,
    descricao: str = None,
    tags: list = None,
    privacidade: str = None
) -> dict:
    """Atualiza metadados de vídeo já publicado — clone do vidiq_update_video"""
    body = {"id": video_id, "snippet": {}, "status": {}}
    parts = ["id"]

    if titulo or descricao or tags:
        parts.append("snippet")
        if titulo:
            body["snippet"]["title"] = titulo[:100]
        if descricao:
            body["snippet"]["description"] = descricao[:5000]
        if tags:
            body["snippet"]["tags"] = tags[:500]
        body["snippet"]["categoryId"] = "22"

    if privacidade:
        parts.append("status")
        body["status"]["privacyStatus"] = privacidade

    response = youtube.videos().update(
        part=",".join(parts),
        body=body
    ).execute()

    return {
        "status": "updated",
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "atualizado_em": datetime.now().isoformat()
    }


def gerar_descricao_otimizada(
    titulo: str,
    script: str,
    canal: str,
    tags: list = None
) -> str:
    """Gera descrição SEO-otimizada para YouTube — clone da lógica vidIQ"""
    tags_str = " ".join([f"#{t.replace(' ', '')}" for t in (tags or [])[:10]])
    desc = f"""{titulo}

{script[:800]}...

━━━━━━━━━━━━━━━━━━━━━━━
🔔 Ative as notificações para não perder nenhum vídeo!
👍 Curta se gostou do conteúdo
💬 Comente o que você achou

━━━━━━━━━━━━━━━━━━━━━━━
Canal: {canal}
Produzido com DARK STUDIO AAA

{tags_str}

#shorts #{canal.lower().replace(' ', '')} #youtube
━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Conteúdo produzido com auxílio de Inteligência Artificial
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"""
    return desc
