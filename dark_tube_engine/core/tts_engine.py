"""
DARK TUBE ENGINE — TTS Engine (clone edge-tts voiceover)
Agente: AUDIO MASTER
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import asyncio
import os
import uuid
import json
from pathlib import Path
from typing import Optional

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import gtts
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Vozes PT-BR disponíveis (edge-tts) — equivalentes às vozes vidIQ
VOZES_PTBR = {
    "narrativa": {
        "id": "pt-BR-AntonioNeural",
        "nome": "Antonio",
        "genero": "masculino",
        "estilo": "narrativa, motivacional",
        "canal_recomendado": "Mente de Aço, storytelling"
    },
    "terror": {
        "id": "pt-BR-FranciscaNeural",
        "nome": "Francisca",
        "genero": "feminino",
        "estilo": "suspense, terror",
        "canal_recomendado": "Esquina do Medo"
    },
    "tech": {
        "id": "pt-BR-AntonioNeural",
        "nome": "Antonio",
        "genero": "masculino",
        "estilo": "profissional, tech",
        "canal_recomendado": "Intelligentia Nova"
    },
    "conspiracao": {
        "id": "pt-BR-AntonioNeural",
        "nome": "Antonio",
        "genero": "masculino",
        "estilo": "misterioso, conspiratorio",
        "canal_recomendado": "Projeto Secreto"
    },
    "relaxamento": {
        "id": "pt-BR-FranciscaNeural",
        "nome": "Francisca",
        "genero": "feminino",
        "estilo": "calmo, relaxante",
        "canal_recomendado": "AquaZen Relax"
    }
}

VOZES_EXTRAS = [
    {"id": "pt-BR-AntonioNeural", "nome": "Antonio", "genero": "masculino", "idioma": "pt-BR"},
    {"id": "pt-BR-FranciscaNeural", "nome": "Francisca", "genero": "feminino", "idioma": "pt-BR"},
    {"id": "pt-BR-ThalitaMultilingualNeural", "nome": "Thalita", "genero": "feminino", "idioma": "pt-BR"},
    {"id": "pt-BR-MacerioMultilingualNeural", "nome": "Macerio", "genero": "masculino", "idioma": "pt-BR"},
]


async def listar_vozes() -> list:
    """Lista todas as vozes PT-BR disponíveis via edge-tts"""
    if not EDGE_TTS_AVAILABLE:
        return [{"id": v["id"], "nome": v["nome"], "genero": v["genero"], "idioma": "pt-BR", "backend": "gtts"}
                for v in VOZES_EXTRAS]
    try:
        voices = await edge_tts.list_voices()
        ptbr = [v for v in voices if v.get("Locale", "").startswith("pt-BR")]
        return [
            {
                "id": v["ShortName"],
                "nome": v["FriendlyName"],
                "genero": v.get("Gender", "N/A"),
                "idioma": v.get("Locale", "pt-BR"),
                "backend": "edge-tts"
            }
            for v in ptbr
        ]
    except Exception:
        return VOZES_EXTRAS


async def gerar_voiceover(
    script: str,
    voice_id: str = "pt-BR-AntonioNeural",
    output_dir: str = "outputs/audio",
    rate: str = "+0%",
    volume: str = "+0%"
) -> dict:
    """
    Gera narração MP3 a partir de texto — clone da funcionalidade vidiq_voiceover_generate
    Retorna: {job_id, status, audio_path, duracao_estimada, chars}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    filename = f"vo_{job_id}.mp3"
    output_path = os.path.join(output_dir, filename)

    chars = len(script)

    if EDGE_TTS_AVAILABLE:
        try:
            communicate = edge_tts.Communicate(
                text=script,
                voice=voice_id,
                rate=rate,
                volume=volume
            )
            await communicate.save(output_path)
            duracao_est = chars / 15  # ~15 chars/segundo
            return {
                "job_id": job_id,
                "status": "completed",
                "audio_path": output_path,
                "filename": filename,
                "chars": chars,
                "duracao_estimada_s": round(duracao_est, 1),
                "voice_id": voice_id,
                "backend": "edge-tts",
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
            }
        except Exception as e:
            return {"job_id": job_id, "status": "failed", "error": str(e)}

    elif GTTS_AVAILABLE:
        try:
            from gtts import gTTS
            tts = gTTS(text=script, lang="pt", slow=False)
            tts.save(output_path)
            return {
                "job_id": job_id,
                "status": "completed",
                "audio_path": output_path,
                "filename": filename,
                "chars": chars,
                "duracao_estimada_s": round(chars / 15, 1),
                "voice_id": "gtts-pt",
                "backend": "gtts",
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
            }
        except Exception as e:
            return {"job_id": job_id, "status": "failed", "error": str(e)}

    return {"job_id": job_id, "status": "failed", "error": "Nenhum backend TTS disponível"}


def gerar_voiceover_sync(script: str, voice_id: str = "pt-BR-AntonioNeural",
                          output_dir: str = "outputs/audio") -> dict:
    """Versão síncrona para uso em FastAPI"""
    return asyncio.run(gerar_voiceover(script, voice_id, output_dir))
