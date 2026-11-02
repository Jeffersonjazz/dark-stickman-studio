"""
DARK TUBE ENGINE — FastAPI Backend
Clone funcional do vidIQ com 9 agentes especializados
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import asyncio
import os
import sys
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.script_engine import criar_job_script, salvar_script
from core.tts_engine import listar_vozes, gerar_voiceover, VOZES_PTBR
from core.thumbnail_engine import gerar_thumbnail_pillow, gerar_pack_thumbnails
from core.keyword_engine import (calcular_score_titulo, pesquisar_palavras_chave_youtube,
                                  analisar_tendencias_nicho)
from core.video_composer import pipeline_compose_short, verificar_ffmpeg, gerar_srt_do_script

# Import condicional do publisher
try:
    from core.youtube_publisher import (autenticar_youtube, fazer_upload_video,
                                         gerar_descricao_otimizada)
    YT_PUBLISHER_OK = True
except Exception:
    YT_PUBLISHER_OK = False

app = FastAPI(
    title="DARK TUBE ENGINE",
    description="Clone funcional do vidIQ — DARK STUDIO AAA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Jobs em memória (produção: usar Redis)
JOBS: dict = {}

# ──────────────────────────────────────────────
# MODELOS
# ──────────────────────────────────────────────

class ScriptRequest(BaseModel):
    titulo: str
    canal: str
    nicho: Optional[str] = None
    duracao_alvo: Optional[int] = 60
    palavras_chave: Optional[List[str]] = []

class ScriptSaveRequest(BaseModel):
    titulo: str
    canal: str
    conteudo: str

class VoiceoverRequest(BaseModel):
    script: str
    voice_id: Optional[str] = "pt-BR-AntonioNeural"
    rate: Optional[str] = "+0%"

class ThumbnailRequest(BaseModel):
    titulo: str
    canal: str
    nicho: Optional[str] = None
    subtitulo: Optional[str] = ""
    tamanho: Optional[str] = "thumbnail_horizontal"
    emoji: Optional[str] = ""

class KeywordRequest(BaseModel):
    termo: str
    api_key: Optional[str] = None
    max_results: Optional[int] = 10

class TituloScoreRequest(BaseModel):
    titulo: str

class ComposeRequest(BaseModel):
    titulo: str
    canal: str
    script: str
    audio_path: str
    resolucao: Optional[str] = "1080x1920"

class PublishRequest(BaseModel):
    video_path: str
    titulo: str
    descricao: Optional[str] = ""
    canal: Optional[str] = ""
    tags: Optional[List[str]] = []
    privacidade: Optional[str] = "public"
    thumbnail_path: Optional[str] = None

class DescricaoRequest(BaseModel):
    titulo: str
    script: str
    canal: str
    tags: Optional[List[str]] = []

# ──────────────────────────────────────────────
# HEALTH
# ──────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "engine": "DARK TUBE ENGINE",
        "versao": "1.0.0",
        "status": "online",
        "agentes": 9,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "endpoints": [
            "/script/criar", "/script/salvar", "/script/score-titulo",
            "/voiceover/gerar", "/voiceover/vozes",
            "/thumbnail/gerar", "/thumbnail/pack",
            "/keywords/pesquisar", "/keywords/tendencias",
            "/video/compor", "/video/status",
            "/publish/descricao",
            "/jobs/{job_id}",
            "/sistema/status"
        ]
    }

@app.get("/sistema/status")
def sistema_status():
    ffmpeg = verificar_ffmpeg()
    try:
        import edge_tts
        tts_backend = "edge-tts"
    except ImportError:
        try:
            import gtts
            tts_backend = "gtts"
        except ImportError:
            tts_backend = "indisponivel"

    try:
        from PIL import Image
        pillow_ok = True
    except ImportError:
        pillow_ok = False

    return {
        "ffmpeg": ffmpeg,
        "tts_backend": tts_backend,
        "pillow": pillow_ok,
        "youtube_publisher": YT_PUBLISHER_OK,
        "agentes_ativos": [
            "SCRIPT AGENT", "VOICEOVER AGENT", "THUMBNAIL AGENT",
            "KEYWORD AGENT", "VIDEO COMPOSER", "PUBLISHER AGENT",
            "ANALYTICS AGENT", "ASSET MANAGER", "CREATIVE QA"
        ],
        "jobs_em_memoria": len(JOBS),
        "timestamp": datetime.now().isoformat()
    }

# ──────────────────────────────────────────────
# AGENTE SCRIPT
# ──────────────────────────────────────────────

@app.post("/script/criar")
def criar_script(req: ScriptRequest):
    """
    Cria job de geração de roteiro — clone do vidiq_generate_script
    Retorna: job_id + prompt para usar com LLM
    """
    job = criar_job_script(
        titulo=req.titulo,
        canal=req.canal,
        nicho=req.nicho,
        duracao_alvo=req.duracao_alvo or 60,
        palavras_chave=req.palavras_chave or []
    )
    JOBS[job["job_id"]] = job
    return job

@app.post("/script/salvar")
def salvar_script_endpoint(req: ScriptSaveRequest):
    """Salva roteiro gerado em arquivo local"""
    return salvar_script(req.titulo, req.canal, req.conteudo)

@app.post("/script/score-titulo")
def score_titulo(req: TituloScoreRequest):
    """Pontua título YouTube — clone do vidiq_score_title"""
    return calcular_score_titulo(req.titulo)

# ──────────────────────────────────────────────
# AGENTE VOICEOVER (AUDIO MASTER)
# ──────────────────────────────────────────────

@app.get("/voiceover/vozes")
async def listar_vozes_endpoint():
    """Lista vozes PT-BR disponíveis — clone do vidiq_voiceover_list_voices"""
    vozes = await listar_vozes()
    vozes_nicho = [
        {"id": k, **v} for k, v in VOZES_PTBR.items()
    ]
    return {
        "total": len(vozes),
        "vozes": vozes,
        "vozes_por_nicho": vozes_nicho,
        "backend": "edge-tts (gratuito)"
    }

@app.post("/voiceover/gerar")
async def gerar_voiceover_endpoint(req: VoiceoverRequest, background_tasks: BackgroundTasks):
    """
    Gera narração MP3 — clone do vidiq_voiceover_generate
    GRATUITO via edge-tts (sem limite de créditos)
    """
    if len(req.script) > 5000:
        raise HTTPException(400, "Script muito longo (máx 5000 chars)")

    job_id = f"vo_{uuid.uuid4().hex[:16]}"
    JOBS[job_id] = {"job_id": job_id, "status": "inprogress", "tipo": "voiceover"}

    async def executar():
        resultado = await gerar_voiceover(
            script=req.script,
            voice_id=req.voice_id or "pt-BR-AntonioNeural",
            output_dir="outputs/audio",
            rate=req.rate or "+0%"
        )
        JOBS[job_id].update(resultado)
        JOBS[job_id]["status"] = resultado.get("status", "completed")

    background_tasks.add_task(executar)
    return {"job_id": job_id, "status": "inprogress",
            "message": "Gerando narração — poll /jobs/{job_id}"}

# ──────────────────────────────────────────────
# AGENTE THUMBNAIL (IMAGE ENGINE)
# ──────────────────────────────────────────────

@app.post("/thumbnail/gerar")
def gerar_thumbnail_endpoint(req: ThumbnailRequest):
    """
    Gera thumbnail YouTube com Pillow — clone do vidiq_generate_thumbnail
    GRATUITO, sem API externa
    """
    return gerar_thumbnail_pillow(
        titulo=req.titulo,
        canal=req.canal,
        nicho=req.nicho,
        subtitulo=req.subtitulo or "",
        tamanho=req.tamanho or "thumbnail_horizontal",
        emoji=req.emoji or ""
    )

@app.post("/thumbnail/pack")
def gerar_pack_endpoint(req: ThumbnailRequest):
    """Gera pack de 2 thumbnails (horizontal + shorts) para o mesmo vídeo"""
    return {
        "pack": gerar_pack_thumbnails(req.titulo, req.canal, req.nicho),
        "total": 2
    }

# ──────────────────────────────────────────────
# AGENTE KEYWORDS (ASSET MANAGER)
# ──────────────────────────────────────────────

@app.post("/keywords/pesquisar")
def pesquisar_keywords(req: KeywordRequest):
    """Pesquisa palavras-chave — clone do vidiq_keyword_research"""
    return pesquisar_palavras_chave_youtube(
        termo=req.termo,
        api_key=req.api_key,
        max_results=req.max_results or 10
    )

@app.get("/keywords/tendencias/{nicho}")
def tendencias_nicho(nicho: str):
    """Retorna tópicos em alta por nicho"""
    return analisar_tendencias_nicho(nicho)

# ──────────────────────────────────────────────
# AGENTE VIDEO COMPOSER (VIDEO EDITOR PRO)
# ──────────────────────────────────────────────

@app.post("/video/compor")
def compor_video(req: ComposeRequest, background_tasks: BackgroundTasks):
    """
    Compõe Short vertical — clone do vidiq_compose
    Requer: arquivo de áudio já gerado pelo /voiceover/gerar
    """
    if not os.path.exists(req.audio_path):
        raise HTTPException(404, f"Áudio não encontrado: {req.audio_path}")

    job_id = f"vid_{uuid.uuid4().hex[:16]}"
    JOBS[job_id] = {"job_id": job_id, "status": "inprogress", "tipo": "compose"}

    def executar():
        resultado = pipeline_compose_short(
            titulo=req.titulo,
            canal=req.canal,
            script=req.script,
            audio_path=req.audio_path,
            resolucao=req.resolucao or "1080x1920"
        )
        JOBS[job_id].update(resultado)

    background_tasks.add_task(executar)
    return {"job_id": job_id, "status": "inprogress",
            "message": "Compondo vídeo — poll /jobs/{job_id}"}

@app.get("/video/status")
def status_ffmpeg():
    return verificar_ffmpeg()

# ──────────────────────────────────────────────
# AGENTE PUBLISHER (YOUTUBE)
# ──────────────────────────────────────────────

@app.post("/publish/descricao")
def gerar_descricao(req: DescricaoRequest):
    """Gera descrição SEO-otimizada para YouTube"""
    return {
        "descricao": gerar_descricao_otimizada(req.titulo, req.script, req.canal, req.tags)
    }

@app.post("/publish/upload")
def upload_youtube(req: PublishRequest):
    """
    Faz upload para YouTube — requer credentials em config/client_secrets.json
    Clone do vidiq_video_upload
    """
    if not YT_PUBLISHER_OK:
        raise HTTPException(503, "google-api-python-client não instalado. Execute: pip install google-api-python-client google-auth-oauthlib")
    if not os.path.exists(req.video_path):
        raise HTTPException(404, f"Vídeo não encontrado: {req.video_path}")

    try:
        yt = autenticar_youtube()
        resultado = fazer_upload_video(
            youtube=yt,
            video_path=req.video_path,
            titulo=req.titulo,
            descricao=req.descricao or "",
            canal=req.canal or "",
            tags=req.tags or [],
            privacidade=req.privacidade or "public",
            thumbnail_path=req.thumbnail_path
        )
        return resultado
    except Exception as e:
        raise HTTPException(500, str(e))

# ──────────────────────────────────────────────
# JOBS
# ──────────────────────────────────────────────

@app.get("/jobs/{job_id}")
def poll_job(job_id: str):
    """Poll de job assíncrono — clone do vidiq_job_poll"""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, f"Job {job_id} não encontrado")
    return job

@app.get("/jobs")
def listar_jobs():
    return {"total": len(JOBS), "jobs": list(JOBS.values())}

# ──────────────────────────────────────────────
# PAINEL
# ──────────────────────────────────────────────

panel_dir = Path(__file__).parent.parent / "panel"
if panel_dir.exists():
    app.mount("/panel", StaticFiles(directory=str(panel_dir), html=True), name="panel")

@app.get("/ui", include_in_schema=False)
def ui_redirect():
    return FileResponse(str(panel_dir / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=True)
