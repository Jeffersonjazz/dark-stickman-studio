"""
DARK STICKMAN STUDIO — API REST FastAPI
Integração com DARK MANAGER via porta 7870.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import uuid
import sqlite3
from pathlib import Path
from typing import Optional, List
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_OK = True
except ImportError:
    FASTAPI_OK = False

from .models import (
    ProduzirRequest, ProduzirResponse,
    ProduzirLoteRequest, LoteResponse,
    ThumbnailRequest, ThumbnailResponse,
    JobStatus, HealthResponse,
)

# ─── Imports internos ────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ffmpeg_utils import check_ffmpeg
from core.piper_tts import check_piper
from core.manim_scene import check_manim
from pipeline.f01_producao import produzir_video, produzir_lote

try:
    from PIL import Image
    PILLOW_OK = True
except ImportError:
    PILLOW_OK = False

try:
    import whisper
    WHISPER_OK = True
except ImportError:
    WHISPER_OK = False

# ─── Constantes ──────────────────────────────────────────────────────────────
VERSION = "1.0.0"
DB_PATH = Path(__file__).parent.parent / "db" / "dark_stickman.db"
OUTPUT_ROOT = Path(__file__).parent.parent / "output"

AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="DARK STICKMAN STUDIO API",
    description="Pipeline de produção automatizada de vídeos stickman para YouTube. "
                "Integração com DARK MANAGER — DARK CREATIVE LAB.\n\n"
                "**ai_generated**: True | **ai_disclosure**: " + AI_DISCLOSURE,
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7870", "http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))


def _job_exists(job_id: str) -> bool:
    try:
        conn = _get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists
    except Exception:
        return False


def _get_job(job_id: str) -> Optional[dict]:
    try:
        conn = _get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception:
        return None


def _list_jobs(canal: Optional[str] = None, status: Optional[str] = None,
               limit: int = 50) -> list:
    try:
        conn = _get_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        q = "SELECT * FROM jobs WHERE 1=1"
        params = []
        if canal:
            q += " AND canal = ?"
            params.append(canal)
        if status:
            q += " AND status = ?"
            params.append(status)
        q += " ORDER BY criado_em DESC LIMIT ?"
        params.append(limit)
        cur.execute(q, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception:
        return []


# ─── Background task ─────────────────────────────────────────────────────────

def _run_pipeline(roteiro_dict: dict, canal_dict: dict, job_id: str,
                  qualidade: str, preset_cor: Optional[str],
                  formato: str, gerar_shorts: bool):
    """Executa pipeline em background."""
    out_dir = OUTPUT_ROOT / canal_dict.get("nome", "canal").replace(" ", "_") / job_id
    try:
        produzir_video(
            roteiro=roteiro_dict,
            canal_config=canal_dict,
            output_dir=out_dir,
            job_id=job_id,
            qualidade=qualidade,
            preset_cor=preset_cor,
            formato=formato,
            gerar_shorts=gerar_shorts,
        )
    except Exception as e:
        # Atualiza DB com erro (f01_producao já faz isso, mas por segurança)
        try:
            conn = _get_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE jobs SET status='erro', erro=?, atualizado_em=? WHERE job_id=?",
                (str(e), datetime.now().isoformat(), job_id),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health():
    """Verifica status do sistema e dependências."""
    return HealthResponse(
        status="ok",
        versao=VERSION,
        ffmpeg=check_ffmpeg(),
        piper=check_piper(),
        manim=check_manim(),
        pillow=PILLOW_OK,
        whisper=WHISPER_OK,
    )


@app.get("/", tags=["Sistema"])
async def root():
    return {
        "nome": "DARK STICKMAN STUDIO API",
        "versao": VERSION,
        "docs": "/docs",
        "ai_generated": True,
        "ai_disclosure": AI_DISCLOSURE,
    }


# ─── Produção ────────────────────────────────────────────────────────────────

@app.post("/produzir", response_model=ProduzirResponse, tags=["Produção"])
async def produzir(req: ProduzirRequest, background_tasks: BackgroundTasks):
    """
    Inicia a produção de um vídeo stickman completo.

    - Gera narração PT-BR com Piper TTS
    - Anima cenas com Manim CE
    - Monta com FFmpeg
    - Gera legendas (WhisperX)
    - Aplica color grade por nicho
    - Adiciona marca d'água de IA obrigatória
    - Gera thumbnail

    Retorna `job_id` para acompanhar em `/jobs/{job_id}`.
    """
    job_id = str(uuid.uuid4())[:12]
    roteiro_dict = req.roteiro.model_dump()
    canal_dict = req.canal.model_dump()

    background_tasks.add_task(
        _run_pipeline,
        roteiro_dict, canal_dict, job_id,
        req.qualidade, req.preset_cor, req.formato, req.gerar_shorts,
    )

    return ProduzirResponse(
        job_id=job_id,
        status="processando",
        mensagem=f"Pipeline iniciado para '{req.roteiro.titulo}'. Acompanhe em /jobs/{job_id}",
    )


@app.post("/produzir/lote", response_model=LoteResponse, tags=["Produção"])
async def produzir_lote_endpoint(req: ProduzirLoteRequest, background_tasks: BackgroundTasks):
    """Inicia produção em lote de múltiplos vídeos."""
    job_ids = [str(uuid.uuid4())[:12] for _ in req.videos]

    for item, job_id in zip(req.videos, job_ids):
        background_tasks.add_task(
            _run_pipeline,
            item.roteiro.model_dump(),
            item.canal.model_dump(),
            job_id,
            item.qualidade,
            None, "16:9", False,
        )

    return LoteResponse(
        total=len(job_ids),
        jobs=job_ids,
        status="processando",
    )


@app.post("/produzir/sincrono", response_model=ProduzirResponse, tags=["Produção"])
async def produzir_sincrono(req: ProduzirRequest):
    """
    Produz vídeo de forma síncrona (aguarda conclusão).
    Use apenas para testes ou vídeos curtos.
    """
    job_id = str(uuid.uuid4())[:12]
    roteiro_dict = req.roteiro.model_dump()
    canal_dict = req.canal.model_dump()
    out_dir = OUTPUT_ROOT / canal_dict.get("nome", "canal").replace(" ", "_") / job_id

    resultado = produzir_video(
        roteiro=roteiro_dict,
        canal_config=canal_dict,
        output_dir=out_dir,
        job_id=job_id,
        qualidade=req.qualidade,
        preset_cor=req.preset_cor,
        formato=req.formato,
        gerar_shorts=req.gerar_shorts,
    )

    status = "concluido" if resultado.get("status") == "concluido" else "erro"
    return ProduzirResponse(
        job_id=job_id,
        status=status,
        mensagem=resultado.get("mensagem", ""),
        resultado=resultado,
    )


# ─── Jobs ─────────────────────────────────────────────────────────────────────

@app.get("/jobs", tags=["Jobs"])
async def listar_jobs(
    canal: Optional[str] = Query(None, description="Filtrar por nome de canal"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    limit: int = Query(50, ge=1, le=200),
):
    """Lista jobs de produção com filtros opcionais."""
    jobs = _list_jobs(canal=canal, status=status, limit=limit)
    return {
        "total": len(jobs),
        "jobs": jobs,
        "ai_generated": True,
    }


@app.get("/jobs/{job_id}", response_model=JobStatus, tags=["Jobs"])
async def status_job(job_id: str):
    """Retorna status detalhado de um job."""
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' não encontrado")
    return JobStatus(**{
        "job_id": job.get("job_id", job_id),
        "status": job.get("status", "desconhecido"),
        "titulo": job.get("titulo", ""),
        "canal": job.get("canal", ""),
        "criado_em": job.get("criado_em", ""),
        "atualizado_em": job.get("atualizado_em", ""),
        "duracao_s": job.get("duracao_s"),
        "output_path": job.get("output_path"),
        "thumbnail_path": job.get("thumbnail_path"),
        "erro": job.get("erro"),
        "ai_generated": bool(job.get("ai_generated", 1)),
        "ai_disclosure": job.get("ai_disclosure", AI_DISCLOSURE),
    })


@app.delete("/jobs/{job_id}", tags=["Jobs"])
async def cancelar_job(job_id: str):
    """Marca um job como cancelado (não interrompe processamento em andamento)."""
    if not _job_exists(job_id):
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' não encontrado")
    try:
        conn = _get_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE jobs SET status='cancelado', atualizado_em=? WHERE job_id=? AND status='pendente'",
            (datetime.now().isoformat(), job_id),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"job_id": job_id, "status": "cancelado"}


# ─── Thumbnail ────────────────────────────────────────────────────────────────

@app.post("/thumbnail", response_model=ThumbnailResponse, tags=["Assets"])
async def gerar_thumbnail_endpoint(req: ThumbnailRequest):
    """Gera thumbnail(s) de YouTube para o canal."""
    try:
        from core.thumbnail import gerar_thumbnail, gerar_variacao
    except ImportError:
        raise HTTPException(status_code=503, detail="Pillow não instalado. Execute: pip install Pillow")

    canal_dict = req.canal.model_dump()
    out_dir = OUTPUT_ROOT / "thumbnails" / canal_dict.get("nome", "canal").replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    if req.n_variacoes == 1:
        out_path = out_dir / f"thumb_{uuid.uuid4().hex[:8]}.png"
        gerar_thumbnail(req.titulo, canal_dict, out_path, req.subtitulo, req.stickman_lado)
        paths = [str(out_path)]
    else:
        paths = [str(p) for p in gerar_variacao(req.titulo, canal_dict, out_dir, req.n_variacoes)]

    return ThumbnailResponse(paths=paths)


# ─── Canais ───────────────────────────────────────────────────────────────────

@app.get("/canais", tags=["Canais"])
async def listar_canais():
    """Lista configurações dos 12 canais disponíveis."""
    import json
    canais_dir = Path(__file__).parent.parent / "config" / "canais"
    canais = []
    for f in sorted(canais_dir.glob("canal_*.json")):
        try:
            canais.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return {"total": len(canais), "canais": canais, "ai_generated": True}


@app.get("/canais/{nicho}", tags=["Canais"])
async def config_canal(nicho: str):
    """Retorna configuração de canal por nicho."""
    import json
    canais_dir = Path(__file__).parent.parent / "config" / "canais"
    for f in canais_dir.glob("canal_*.json"):
        try:
            cfg = json.loads(f.read_text(encoding="utf-8"))
            if cfg.get("nicho") == nicho or cfg.get("nome", "").lower() == nicho.lower():
                return cfg
        except Exception:
            pass
    raise HTTPException(status_code=404, detail=f"Canal/nicho '{nicho}' não encontrado")


# ─── Presets ──────────────────────────────────────────────────────────────────

@app.get("/presets", tags=["Configuração"])
async def listar_presets():
    """Lista presets cinematográficos disponíveis."""
    import json
    presets_path = Path(__file__).parent.parent / "config" / "presets.json"
    if not presets_path.exists():
        return {"presets": [], "ai_generated": True}
    data = json.loads(presets_path.read_text(encoding="utf-8"))
    return {**data, "ai_generated": True}


# ─── Estatísticas ─────────────────────────────────────────────────────────────

@app.get("/stats", tags=["Sistema"])
async def estatisticas():
    """Estatísticas de produção do studio."""
    try:
        conn = _get_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM jobs")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobs WHERE status='concluido'")
        concluidos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobs WHERE status='erro'")
        erros = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM jobs WHERE status='processando'")
        processando = cur.fetchone()[0]

        cur.execute("SELECT SUM(duracao_s) FROM jobs WHERE status='concluido'")
        total_s = cur.fetchone()[0] or 0

        cur.execute("SELECT canal, COUNT(*) as n FROM jobs GROUP BY canal ORDER BY n DESC LIMIT 5")
        top_canais = [{"canal": r[0], "videos": r[1]} for r in cur.fetchall()]

        conn.close()

        return {
            "total_jobs": total,
            "concluidos": concluidos,
            "erros": erros,
            "processando": processando,
            "total_minutos_produzidos": round(total_s / 60, 1),
            "top_canais": top_canais,
            "ai_generated": True,
            "ai_disclosure": AI_DISCLOSURE,
        }
    except Exception as e:
        return {"erro": str(e), "ai_generated": True}


# ─── Entrada ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not FASTAPI_OK:
        print("FastAPI não instalado. Execute: pip install fastapi uvicorn")
    else:
        print("DARK STICKMAN STUDIO API — porta 7870")
        uvicorn.run("api.main:app", host="0.0.0.0", port=7870, reload=False)
