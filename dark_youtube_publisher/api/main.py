"""
DARK YOUTUBE PUBLISHER — FastAPI Server
Endpoints para publicação no YouTube via DARK STUDIO AAA.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import time
from pathlib import Path

from dark_youtube_publisher.core.batch_publisher import (
    DarkBatchPublisher,
    PublishJob,
    DARK_CHANNELS,
)
from dark_youtube_publisher.auth.oauth_manager import list_authorized_channels

app = FastAPI(
    title="DARK YOUTUBE PUBLISHER",
    description="Integração DARK STUDIO AAA — YouTube Data API v3",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazena status de jobs em memória
JOBS: dict[str, dict] = {}

CLIENT_SECRETS = str(Path.home() / ".dark_studio" / "client_secrets.json")


class PublishRequest(BaseModel):
    channel_key: str
    video_url: str
    title: str
    description: str
    tags: list[str] = []
    thumbnail_url: Optional[str] = None
    is_short: bool = True
    privacy: str = "public"


class BatchPublishRequest(BaseModel):
    jobs: list[PublishRequest]
    delay_between: int = 10


@app.get("/")
def root():
    return {
        "service": "DARK YOUTUBE PUBLISHER",
        "version": "1.0.0",
        "studio": "DARK STUDIO AAA",
        "status": "online",
    }


@app.get("/channels")
def list_channels():
    """Lista todos os canais configurados e quais têm autorização OAuth."""
    authorized = list_authorized_channels()
    channels = []
    for key, ch in DARK_CHANNELS.items():
        label = ch["label"]
        safe = label.lower().replace(" ", "_").replace("/", "_")
        is_auth = any(safe in a.lower() for a in authorized)
        channels.append({
            "key": key,
            "label": label,
            "handle": ch.get("handle", ""),
            "niche": ch["niche"],
            "authorized": is_auth,
        })
    return {"channels": channels, "total": len(channels)}


@app.post("/publish")
def publish_single(req: PublishRequest, background_tasks: BackgroundTasks):
    """Publica um único vídeo em um canal."""
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "created_at": time.time()}

    def do_publish():
        JOBS[job_id]["status"] = "running"
        try:
            publisher = DarkBatchPublisher(CLIENT_SECRETS)
            job = PublishJob(
                channel_key=req.channel_key,
                video_url=req.video_url,
                title=req.title,
                description=req.description,
                extra_tags=req.tags,
                thumbnail_url=req.thumbnail_url,
                is_short=req.is_short,
                privacy=req.privacy,
            )
            results = publisher.publish_batch([job])
            r = results[0]
            JOBS[job_id].update({
                "status": "done" if r.success else "error",
                "result": {
                    "success": r.success,
                    "videoId": r.video_id,
                    "url": r.youtube_url,
                    "error": r.error,
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
                },
            })
        except Exception as e:
            JOBS[job_id].update({"status": "error", "error": str(e)})

    background_tasks.add_task(do_publish)
    return {"job_id": job_id, "status": "queued"}


@app.post("/publish/batch")
def publish_batch(req: BatchPublishRequest, background_tasks: BackgroundTasks):
    """Publica múltiplos vídeos em background."""
    batch_id = str(uuid.uuid4())
    JOBS[batch_id] = {
        "status": "queued",
        "total": len(req.jobs),
        "created_at": time.time(),
    }

    def do_batch():
        JOBS[batch_id]["status"] = "running"
        try:
            publisher = DarkBatchPublisher(CLIENT_SECRETS)
            jobs = [
                PublishJob(
                    channel_key=j.channel_key,
                    video_url=j.video_url,
                    title=j.title,
                    description=j.description,
                    extra_tags=j.tags,
                    thumbnail_url=j.thumbnail_url,
                    is_short=j.is_short,
                    privacy=j.privacy,
                )
                for j in req.jobs
            ]
            results = publisher.publish_batch(jobs, delay_between=req.delay_between)
            JOBS[batch_id].update({
                "status": "done",
                "results": [
                    {
                        "channel": r.channel_label,
                        "title": r.title,
                        "success": r.success,
                        "url": r.youtube_url,
                        "error": r.error,
                    }
                    for r in results
                ],
                "summary": publisher.summary(),
            })
        except Exception as e:
            JOBS[batch_id].update({"status": "error", "error": str(e)})

    background_tasks.add_task(do_batch)
    return {"batch_id": batch_id, "status": "queued", "total": len(req.jobs)}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """Verifica status de um job de publicação."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return {"job_id": job_id, **job}


@app.get("/jobs")
def list_jobs():
    """Lista todos os jobs desta sessão."""
    return {
        "jobs": [
            {"job_id": jid, **info}
            for jid, info in sorted(JOBS.items(), key=lambda x: x[1].get("created_at", 0), reverse=True)
        ]
    }
