"""
DARK YOUTUBE PUBLISHER — OAuth Manager
Gerencia tokens OAuth2 para múltiplos canais YouTube.
Persiste tokens por channelId em ~/.dark_studio/tokens/
"""

import os
import json
import webbrowser
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

TOKENS_DIR = Path.home() / ".dark_studio" / "tokens"
TOKENS_DIR.mkdir(parents=True, exist_ok=True)


def get_token_path(channel_label: str) -> Path:
    safe = channel_label.lower().replace(" ", "_").replace("/", "_")
    return TOKENS_DIR / f"{safe}_token.json"


def load_credentials(channel_label: str) -> Credentials | None:
    """Carrega credenciais salvas para um canal. Renova se expirado."""
    token_path = get_token_path(channel_label)
    if not token_path.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(channel_label, creds)

    return creds if (creds and creds.valid) else None


def save_credentials(channel_label: str, creds: Credentials):
    """Salva credenciais em disco."""
    token_path = get_token_path(channel_label)
    with open(token_path, "w") as f:
        f.write(creds.to_json())
    print(f"[AUTH] Token salvo: {token_path}")


def authorize_channel(
    channel_label: str,
    client_secrets_path: str,
    port: int = 8080,
) -> Credentials:
    """
    Inicia fluxo OAuth para autorizar um canal.
    Abre o navegador automaticamente.
    """
    print(f"\n[AUTH] Autorizando canal: {channel_label}")
    print(f"[AUTH] Abrindo navegador para autorização...")

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_path,
        scopes=SCOPES,
    )

    creds = flow.run_local_server(
        port=port,
        prompt="consent",
        access_type="offline",
        open_browser=True,
    )

    save_credentials(channel_label, creds)
    print(f"[AUTH] ✅ Canal '{channel_label}' autorizado com sucesso!")
    return creds


def list_authorized_channels() -> list[str]:
    """Lista canais com tokens salvos."""
    return [
        p.stem.replace("_token", "").replace("_", " ").title()
        for p in TOKENS_DIR.glob("*_token.json")
    ]


def revoke_channel(channel_label: str):
    """Remove token de um canal."""
    token_path = get_token_path(channel_label)
    if token_path.exists():
        token_path.unlink()
        print(f"[AUTH] Token removido: {channel_label}")
