"""
DARK YOUTUBE PUBLISHER — Core Uploader
Agente Clone: integração direta com YouTube Data API v3
Sem dependência de vidIQ para publicação.
"""

import os
import json
import time
import tempfile
import requests
from pathlib import Path
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import io

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

CATEGORY_MAP = {
    "tech": "28",          # Ciência e Tecnologia
    "terror": "24",        # Entretenimento
    "historia": "27",      # Educação
    "conspiracao": "24",   # Entretenimento
    "natureza": "15",      # Animais e Natureza
    "filosofia": "27",     # Educação
    "investimentos": "25", # Notícias e Política
    "espaco": "28",        # Ciência e Tecnologia
    "ocultismo": "24",     # Entretenimento
    "motivacao": "26",     # Como fazer e Estilo
    "musica": "10",        # Música
    "viagens": "19",       # Viagens e Eventos
    "crimes": "25",        # Notícias e Política
    "curiosidades": "27",  # Educação
    "biblica": "27",       # Educação
}


class DarkYouTubeUploader:
    """Publica vídeos diretamente no YouTube via Data API v3."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.youtube = build("youtube", "v3", credentials=credentials)

    def upload_from_url(
        self,
        video_url: str,
        title: str,
        description: str,
        tags: list[str],
        category_key: str = "tech",
        privacy: str = "public",
        made_for_kids: bool = False,
        is_short: bool = True,
        notify_subscribers: bool = True,
    ) -> dict:
        """
        Baixa vídeo de uma URL (GCS, CDN, etc) e publica no YouTube.
        Retorna dict com videoId, url, status.
        """
        print(f"[DARK PUBLISHER] Baixando: {title}")

        # Baixar para buffer em memória (evita disco)
        resp = requests.get(video_url, stream=True, timeout=120)
        resp.raise_for_status()

        video_buffer = io.BytesIO()
        for chunk in resp.iter_content(chunk_size=8 * 1024 * 1024):
            video_buffer.write(chunk)
        video_buffer.seek(0)

        total_mb = video_buffer.getbuffer().nbytes / (1024 * 1024)
        print(f"[DARK PUBLISHER] {total_mb:.1f} MB baixados. Iniciando upload...")

        category_id = CATEGORY_MAP.get(category_key, "24")

        # Montar hashtags para Shorts
        hashtags = ""
        if is_short:
            hashtags = "\n\n#Shorts #DarkStudioAAA"

        body = {
            "snippet": {
                "title": title,
                "description": description + hashtags,
                "tags": tags + (["Shorts"] if is_short else []),
                "categoryId": category_id,
                "defaultLanguage": "pt",
                "defaultAudioLanguage": "pt",
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": made_for_kids,
                "madeForKids": made_for_kids,
                "notifySubscribers": notify_subscribers,
            },
            "localizations": {},
        }

        media = MediaIoBaseUpload(
            video_buffer,
            mimetype="video/mp4",
            chunksize=8 * 1024 * 1024,
            resumable=True,
        )

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        retry = 0
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    print(f"[DARK PUBLISHER] Upload: {pct}%")
            except Exception as e:
                retry += 1
                if retry > 5:
                    raise
                print(f"[DARK PUBLISHER] Erro chunk (tentativa {retry}): {e}")
                time.sleep(2 ** retry)

        video_id = response["id"]
        video_url_yt = f"https://www.youtube.com/shorts/{video_id}" if is_short else f"https://www.youtube.com/watch?v={video_id}"

        print(f"[DARK PUBLISHER] ✅ Publicado: {video_url_yt}")

        return {
            "videoId": video_id,
            "url": video_url_yt,
            "title": title,
            "status": privacy,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def set_thumbnail(self, video_id: str, thumbnail_url: str) -> bool:
        """Define thumbnail via URL."""
        try:
            img_data = requests.get(thumbnail_url, timeout=30).content
            media = MediaIoBaseUpload(
                io.BytesIO(img_data),
                mimetype="image/jpeg",
                resumable=False,
            )
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media,
            ).execute()
            return True
        except Exception as e:
            print(f"[DARK PUBLISHER] Erro thumbnail: {e}")
            return False

    def get_channel_info(self) -> dict:
        """Retorna info do canal autenticado."""
        resp = self.youtube.channels().list(
            part="snippet,statistics",
            mine=True,
        ).execute()
        if resp.get("items"):
            ch = resp["items"][0]
            return {
                "channelId": ch["id"],
                "title": ch["snippet"]["title"],
                "handle": ch["snippet"].get("customUrl", ""),
                "subscribers": ch["statistics"].get("subscriberCount", 0),
            }
        return {}
