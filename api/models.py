"""
DARK STICKMAN STUDIO — Modelos Pydantic para a API
Contratos JSON para comunicação com DARK MANAGER.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ─── Cena ────────────────────────────────────────────────────────────────────

class CenaInput(BaseModel):
    num: int = Field(..., description="Número da cena (1-based)")
    tipo: str = Field("normal", description="Tipo: hook, normal, revelaçao, conclusao, outro")
    duracao_s: float = Field(5.0, ge=1.0, le=60.0, description="Duração em segundos")
    stickman_acao: str = Field("parado", description="Ação: parado, correndo, lutando, vitoria, saltando, apontando, pensando")
    narracao: str = Field("", description="Texto de narração PT-BR")
    fundo: str = Field("branco_minimalista", description="Tipo de fundo visual")
    texto_tela: Optional[str] = Field(None, description="Texto exibido na tela")


# ─── Roteiro ─────────────────────────────────────────────────────────────────

class RoteiroInput(BaseModel):
    titulo: str = Field(..., max_length=200, description="Título do vídeo")
    descricao: Optional[str] = Field(None, max_length=500)
    hook: str = Field(..., description="Texto do gancho inicial (0-5s)")
    cenas: List[CenaInput] = Field(..., min_length=1, max_length=50)
    cta: str = Field("Inscreva-se no canal!", description="Call to action final")


# ─── Canal ────────────────────────────────────────────────────────────────────

class CanalConfig(BaseModel):
    nome: str = Field(..., description="Nome do canal")
    nicho: str = Field("default", description="Nicho: psicologia, batalhas, tecnologia, etc.")
    stickman_color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    stickman_seed: int = Field(42, description="Seed para consistência de personagem")
    modelo_tts: str = Field("faber-medium", description="Modelo Piper PT-BR")
    velocidade_fala: float = Field(1.05, ge=0.5, le=2.0)
    watermark: bool = Field(True, description="Adicionar marca d'água de IA")


# ─── Request: Produzir Vídeo ─────────────────────────────────────────────────

class ProduzirRequest(BaseModel):
    roteiro: RoteiroInput
    canal: CanalConfig
    qualidade: str = Field("medium_quality", description="low_quality | medium_quality | high_quality")
    formato: str = Field("16:9", description="16:9 | 9:16 | 1:1")
    preset_cor: Optional[str] = Field(None, description="Preset de color grade. None = automático por nicho")
    gerar_shorts: bool = Field(False, description="Gerar versão 9:16 para Shorts")

    model_config = {"json_schema_extra": {
        "example": {
            "roteiro": {
                "titulo": "POR QUE VOCÊ PROCRASTINA?",
                "hook": "E se a procrastinação fosse um mecanismo de defesa do cérebro?",
                "cenas": [
                    {"num": 1, "tipo": "normal", "duracao_s": 5,
                     "stickman_acao": "pensando",
                     "narracao": "Hoje vamos entender por que adiamos tarefas importantes.",
                     "fundo": "branco_minimalista"}
                ],
                "cta": "Inscreva-se para mais conteúdo!"
            },
            "canal": {
                "nome": "Stickman Psicologia",
                "nicho": "psicologia",
                "stickman_color": "#6366F1",
                "stickman_seed": 42,
                "modelo_tts": "faber-medium",
                "velocidade_fala": 1.05,
                "watermark": True
            }
        }
    }}


# ─── Response: Job ───────────────────────────────────────────────────────────

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pendente" | "processando" | "concluido" | "erro"
    titulo: str
    canal: str
    criado_em: str
    atualizado_em: str
    duracao_s: Optional[float] = None
    output_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    erro: Optional[str] = None
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"


class ProduzirResponse(BaseModel):
    job_id: str
    status: str
    mensagem: str
    resultado: Optional[Dict[str, Any]] = None
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"


# ─── Request: Lote ───────────────────────────────────────────────────────────

class LoteItem(BaseModel):
    roteiro: RoteiroInput
    canal: CanalConfig
    qualidade: str = "medium_quality"


class ProduzirLoteRequest(BaseModel):
    videos: List[LoteItem] = Field(..., min_length=1, max_length=20)
    paralelo: bool = Field(False, description="Processar em paralelo (requer GPU)")


class LoteResponse(BaseModel):
    total: int
    jobs: List[str]
    status: str
    ai_generated: bool = True


# ─── Thumbnail ────────────────────────────────────────────────────────────────

class ThumbnailRequest(BaseModel):
    titulo: str = Field(..., max_length=100)
    subtitulo: Optional[str] = Field(None, max_length=80)
    canal: CanalConfig
    stickman_lado: str = Field("right", pattern=r"^(right|left)$")
    n_variacoes: int = Field(1, ge=1, le=3)


class ThumbnailResponse(BaseModel):
    paths: List[str]
    ai_generated: bool = True


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    versao: str
    ffmpeg: bool
    piper: bool
    manim: bool
    pillow: bool
    whisper: bool
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
