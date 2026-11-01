"""
DARK CREATIVE LAB — MÓDULO DE PERFORMANCE E CACHE
Fase 11 — Otimização de custos e desempenho.

Funcionalidades:
- Profiling por etapa do Pipeline F01 (tempo real de execução)
- Cache de assets gerados (TTS, thumbnails, clips)
- Relatório de custo estimado por job
- Otimizações FFmpeg (presets de codec)
- Sistema de deduplicação via hash MD5

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import hashlib
import json
import time
import functools
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import Callable, Optional, Any

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────

# Custo estimado por operação (em R$ ou unidade de crédito)
CUSTO_ESTIMADO = {
    "tts_edge":       0.000,   # Edge TTS — gratuito (Microsoft)
    "tts_gtts":       0.000,   # Google TTS — gratuito (limite de uso)
    "tts_piper":      0.000,   # Piper — local, gratuito
    "tts_kokoro":     0.000,   # Kokoro — local, gratuito
    "tts_elevenlabs": 0.030,   # ElevenLabs por 1k chars
    "imagen_local":   0.000,   # Geração local
    "imagen_openai":  0.040,   # DALL-E 3 por imagem
    "imagen_replicate": 0.003, # Flux via Replicate por imagem
    "video_runway":   0.200,   # Runway Gen-3 por segundo
    "video_kling":    0.100,   # Kling por segundo
    "ffmpeg_render":  0.000,   # Renderização local
    "storage_gb":     0.025,   # R2/S3 por GB/mês
}

# Parâmetros FFmpeg otimizados por perfil
FFMPEG_PRESETS = {
    "ultra_fast": {
        "codec": "libx264",
        "preset": "ultrafast",
        "crf": "28",
        "audio_codec": "aac",
        "audio_bitrate": "128k",
        "nota": "Mais rápido, maior arquivo, menor qualidade",
    },
    "fast": {
        "codec": "libx264",
        "preset": "veryfast",
        "crf": "23",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "nota": "Rápido, bom equilíbrio",
    },
    "balanced": {
        "codec": "libx264",
        "preset": "medium",
        "crf": "20",
        "audio_codec": "aac",
        "audio_bitrate": "256k",
        "nota": "Padrão recomendado para YouTube",
    },
    "quality": {
        "codec": "libx264",
        "preset": "slow",
        "crf": "18",
        "audio_codec": "aac",
        "audio_bitrate": "320k",
        "nota": "Alta qualidade, mais lento",
    },
    "youtube_hd": {
        "codec": "libx264",
        "preset": "medium",
        "crf": "18",
        "audio_codec": "aac",
        "audio_bitrate": "384k",
        "movflags": "+faststart",
        "nota": "Otimizado para upload YouTube 1080p",
    },
    "shorts": {
        "codec": "libx264",
        "preset": "veryfast",
        "crf": "22",
        "audio_codec": "aac",
        "audio_bitrate": "192k",
        "movflags": "+faststart",
        "nota": "Otimizado para Shorts verticais",
    },
}


# ─────────────────────────────────────────────────────────────────
#  PROFILER DE ETAPAS
# ─────────────────────────────────────────────────────────────────

class PipelineProfiler:
    """
    Registra tempo de execução de cada etapa do pipeline F01.
    Gera relatório JSON com breakdown por fase.
    """

    def __init__(self, job_id: str):
        self.job_id = job_id
        self._etapas: list[dict] = []
        self._inicio_job = time.time()
        self._etapa_ativa: Optional[str] = None
        self._etapa_inicio: Optional[float] = None

    def iniciar_etapa(self, nome: str):
        """Registra início de uma etapa."""
        if self._etapa_ativa:
            self.finalizar_etapa(status="interrompida")
        self._etapa_ativa = nome
        self._etapa_inicio = time.time()

    def finalizar_etapa(self, status: str = "ok", meta: dict = None):
        """Registra fim da etapa com status e metadados opcionais."""
        if not self._etapa_ativa:
            return
        duracao = time.time() - (self._etapa_inicio or time.time())
        self._etapas.append({
            "etapa": self._etapa_ativa,
            "duracao_s": round(duracao, 3),
            "status": status,
            "meta": meta or {},
        })
        self._etapa_ativa = None
        self._etapa_inicio = None

    @contextmanager
    def etapa(self, nome: str, meta: dict = None):
        """Context manager para medir uma etapa automaticamente."""
        self.iniciar_etapa(nome)
        try:
            yield self
            self.finalizar_etapa(status="ok", meta=meta or {})
        except Exception as e:
            self.finalizar_etapa(status=f"erro: {type(e).__name__}")
            raise

    def relatorio(self) -> dict:
        """Gera relatório completo de profiling."""
        if self._etapa_ativa:
            self.finalizar_etapa(status="em_andamento")

        duracao_total = time.time() - self._inicio_job
        etapas_ok = [e for e in self._etapas if e["status"] == "ok"]
        etapas_erro = [e for e in self._etapas if e["status"].startswith("erro")]

        # Top 3 etapas mais demoradas
        ordenadas = sorted(self._etapas, key=lambda x: x["duracao_s"], reverse=True)
        top_lentas = ordenadas[:3]

        # Percentual de cada etapa
        for e in self._etapas:
            e["percentual"] = round(
                (e["duracao_s"] / duracao_total * 100) if duracao_total > 0 else 0, 1
            )

        return {
            "job_id": self.job_id,
            "duracao_total_s": round(duracao_total, 2),
            "duracao_total_formatada": _formatar_duracao(duracao_total),
            "total_etapas": len(self._etapas),
            "etapas_ok": len(etapas_ok),
            "etapas_erro": len(etapas_erro),
            "etapas": self._etapas,
            "top_3_mais_lentas": [
                {"etapa": e["etapa"], "duracao_s": e["duracao_s"]}
                for e in top_lentas
            ],
            "gerado_em": _agora(),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def salvar(self, output_dir: Path) -> Path:
        """Salva relatório de profiling em JSON."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"profiling_{self.job_id}.json"
        path.write_text(
            json.dumps(self.relatorio(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


# ─────────────────────────────────────────────────────────────────
#  CACHE DE ASSETS
# ─────────────────────────────────────────────────────────────────

class AssetCache:
    """
    Cache de assets gerados (TTS, thumbnails, clips processados).
    Evita re-geração de conteúdo idêntico.
    Persiste em JSON no diretório de cache do projeto.
    """

    CACHE_FILE = ".perf_cache.json"

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = self.cache_dir / self.CACHE_FILE
        self._db = self._load()

    def _load(self) -> dict:
        if self._db_path.exists():
            try:
                return json.loads(self._db_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {"entradas": {}, "hits": 0, "misses": 0, "criado_em": _agora()}

    def _save(self):
        self._db["atualizado_em"] = _agora()
        self._db_path.write_text(
            json.dumps(self._db, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _chave(self, tipo: str, dados: str | bytes) -> str:
        """Gera chave única baseada no tipo e conteúdo."""
        conteudo = dados if isinstance(dados, bytes) else dados.encode("utf-8")
        return f"{tipo}:{hashlib.md5(conteudo).hexdigest()}"

    def get(self, tipo: str, dados: str | bytes) -> Optional[Path]:
        """
        Retorna caminho do arquivo em cache se existir.
        Incrementa hit/miss counter.
        """
        chave = self._chave(tipo, dados)
        entrada = self._db["entradas"].get(chave)
        if entrada:
            caminho = Path(entrada["caminho"])
            if caminho.exists():
                self._db["hits"] = self._db.get("hits", 0) + 1
                entrada["ultimo_acesso"] = _agora()
                entrada["acessos"] = entrada.get("acessos", 0) + 1
                self._save()
                return caminho
        self._db["misses"] = self._db.get("misses", 0) + 1
        return None

    def set(self, tipo: str, dados: str | bytes, caminho: Path, meta: dict = None):
        """Registra arquivo no cache."""
        chave = self._chave(tipo, dados)
        self._db["entradas"][chave] = {
            "tipo": tipo,
            "caminho": str(caminho),
            "criado_em": _agora(),
            "ultimo_acesso": _agora(),
            "acessos": 1,
            "tamanho_bytes": caminho.stat().st_size if caminho.exists() else 0,
            "meta": meta or {},
        }
        self._save()

    def estatisticas(self) -> dict:
        """Retorna estatísticas de eficiência do cache."""
        total = self._db.get("hits", 0) + self._db.get("misses", 0)
        hit_rate = (self._db.get("hits", 0) / total * 100) if total > 0 else 0
        tamanho_total = sum(
            e.get("tamanho_bytes", 0) for e in self._db["entradas"].values()
        )
        return {
            "entradas": len(self._db["entradas"]),
            "hits": self._db.get("hits", 0),
            "misses": self._db.get("misses", 0),
            "hit_rate_pct": round(hit_rate, 1),
            "tamanho_total_mb": round(tamanho_total / 1024 / 1024, 2),
        }

    def limpar_invalidos(self) -> int:
        """Remove entradas cujos arquivos não existem mais."""
        removidos = 0
        chaves = list(self._db["entradas"].keys())
        for chave in chaves:
            caminho = Path(self._db["entradas"][chave]["caminho"])
            if not caminho.exists():
                del self._db["entradas"][chave]
                removidos += 1
        if removidos:
            self._save()
        return removidos


# ─────────────────────────────────────────────────────────────────
#  ESTIMATIVA DE CUSTO
# ─────────────────────────────────────────────────────────────────

class CustoEstimador:
    """
    Estima o custo total de um job de produção.
    Rastreia uso de cada recurso.
    """

    def __init__(self):
        self._itens: list[dict] = []

    def registrar(self, recurso: str, quantidade: float = 1.0, descricao: str = ""):
        """
        Registra uso de um recurso.

        Args:
            recurso: Chave em CUSTO_ESTIMADO (ex: "tts_edge", "ffmpeg_render")
            quantidade: Quantidade de unidades
            descricao: Descrição do uso
        """
        custo_unit = CUSTO_ESTIMADO.get(recurso, 0.0)
        custo_total = custo_unit * quantidade
        self._itens.append({
            "recurso": recurso,
            "quantidade": quantidade,
            "custo_unitario": custo_unit,
            "custo_total": round(custo_total, 6),
            "descricao": descricao,
        })

    def relatorio(self) -> dict:
        """Gera relatório de custo do job."""
        custo_total = sum(i["custo_total"] for i in self._itens)
        gratuitos = [i for i in self._itens if i["custo_total"] == 0]
        pagos = [i for i in self._itens if i["custo_total"] > 0]

        return {
            "custo_total_brl": round(custo_total, 4),
            "itens_gratuitos": len(gratuitos),
            "itens_pagos": len(pagos),
            "itens": self._itens,
            "resumo": {
                "tts": sum(i["custo_total"] for i in self._itens if "tts" in i["recurso"]),
                "imagem": sum(i["custo_total"] for i in self._itens if "imagen" in i["recurso"]),
                "video": sum(i["custo_total"] for i in self._itens if "video" in i["recurso"]),
                "render": sum(i["custo_total"] for i in self._itens if "ffmpeg" in i["recurso"]),
            },
            "ai_generated": True,
        }


# ─────────────────────────────────────────────────────────────────
#  PARÂMETROS FFMPEG OTIMIZADOS
# ─────────────────────────────────────────────────────────────────

def ffmpeg_params_otimizados(perfil: str = "balanced") -> list[str]:
    """
    Retorna lista de parâmetros FFmpeg otimizados para o perfil especificado.

    Args:
        perfil: "ultra_fast", "fast", "balanced", "quality", "youtube_hd", "shorts"

    Returns:
        Lista de argumentos FFmpeg para inserir no comando.
    """
    preset = FFMPEG_PRESETS.get(perfil, FFMPEG_PRESETS["balanced"])

    params = [
        "-c:v", preset["codec"],
        "-preset", preset["preset"],
        "-crf", preset["crf"],
        "-c:a", preset["audio_codec"],
        "-b:a", preset["audio_bitrate"],
    ]

    if "movflags" in preset:
        params += ["-movflags", preset["movflags"]]

    return params


def sugerir_perfil_ffmpeg(duracao_s, resolucao: str = "1080p") -> str:
    # Aceita dict de contexto ou float direto
    if isinstance(duracao_s, dict):
        ctx = duracao_s
        duracao_s = ctx.get("duracao_total", ctx.get("duracao_s", 60))
        resolucao = ctx.get("resolucao", resolucao)
        if ctx.get("gpu_disponivel"):
            resolucao = resolucao  # GPU futuro: manter perfil
    """
    Sugere o melhor perfil FFmpeg baseado na situação.

    Args:
        duracao_s: Duração do vídeo em segundos.
        resolucao: "4k", "1080p", "720p", "shorts"

    Returns:
        Nome do perfil recomendado.
    """
    if resolucao.lower() in ("shorts", "reel"):
        return "shorts"
    if resolucao.lower() == "4k":
        return "quality"
    if duracao_s < 120:
        return "quality"      # Vídeos curtos: prioriza qualidade
    if duracao_s < 600:
        return "youtube_hd"   # Até 10 min: perfil YouTube
    return "fast"             # Vídeos longos: prioriza velocidade


# ─────────────────────────────────────────────────────────────────
#  DECORATOR DE PROFILING
# ─────────────────────────────────────────────────────────────────

def profiled(nome_etapa: str):
    """
    Decorator que envolve uma função com profiling automático.
    Requer que o primeiro argumento da função seja o profiler.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Procura profiler nos args
            profiler = None
            for arg in args:
                if isinstance(arg, PipelineProfiler):
                    profiler = arg
                    break
            if not profiler:
                profiler = kwargs.get("profiler")

            if profiler:
                with profiler.etapa(nome_etapa):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


# ─────────────────────────────────────────────────────────────────
#  RELATÓRIO DE PERFORMANCE COMPLETO
# ─────────────────────────────────────────────────────────────────

def gerar_relatorio_performance(
    job_id: str,
    profiler: PipelineProfiler,
    custo: CustoEstimador,
    cache: AssetCache,
    output_dir: Path,
) -> dict:
    """
    Gera relatório completo de performance para um job.
    Combina profiling, custo e estatísticas de cache.

    Returns:
        Dict com relatório completo.
    """
    rel_profiling = profiler.relatorio()
    rel_custo = custo.relatorio()
    rel_cache = cache.estatisticas()

    relatorio = {
        "job_id": job_id,
        "gerado_em": _agora(),
        "performance": {
            "duracao_total_s": rel_profiling["duracao_total_s"],
            "duracao_formatada": rel_profiling["duracao_total_formatada"],
            "etapas_ok": rel_profiling["etapas_ok"],
            "etapas_erro": rel_profiling["etapas_erro"],
            "top_3_mais_lentas": rel_profiling["top_3_mais_lentas"],
        },
        "custo": rel_custo,
        "cache": rel_cache,
        "profiling_detalhado": rel_profiling,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    # Salva relatório
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"performance_{job_id}.json"
    path.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return relatorio


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_performance() -> dict:
    """Diagnóstico do módulo de performance."""
    # Teste básico do profiler
    p = PipelineProfiler("test_diagnostico")
    with p.etapa("teste_dummy"):
        time.sleep(0.01)
    rel = p.relatorio()

    # Teste do cache
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        cache = AssetCache(Path(tmp))
        stats_cache = cache.estatisticas()

    return {
        "status": "ok",
        "profiler_ok": rel["etapas_ok"] == 1,
        "cache_ok": stats_cache["entradas"] == 0,
        "ffmpeg_presets": list(FFMPEG_PRESETS.keys()),
        "recursos_custo": list(CUSTO_ESTIMADO.keys()),
        "funcoes": [
            "PipelineProfiler",
            "AssetCache",
            "CustoEstimador",
            "ffmpeg_params_otimizados",
            "sugerir_perfil_ffmpeg",
            "gerar_relatorio_performance",
        ],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  HELPERS PRIVADOS
# ─────────────────────────────────────────────────────────────────

def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _formatar_duracao(segundos: float) -> str:
    s = int(segundos)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{round(segundos, 1)}s"
