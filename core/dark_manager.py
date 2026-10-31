"""
DARK CREATIVE LAB — DARK MANAGER
Orquestrador central dos agentes especializados.

Roteia tarefas para os agentes corretos com base no tipo de operação
e retorna resultado padronizado em JSON.

Agentes disponíveis:
- IMAGE ENGINE       → core/image_engine.py (placeholder)
- VIDEO GENERATOR    → core/video_generator.py (placeholder)
- CINEMATIC DIRECTOR → core/cinematic_director.py
- VIDEO EDITOR PRO   → core/ffmpeg_utils.py (wrapper)
- MOTION GRAPHICS    → core/motion_graphics.py (placeholder)
- AUDIO MASTER       → core/audio_master.py
- VISUAL CONSISTENCY → core/visual_consistency.py
- ASSET MANAGER      → core/asset_manager.py (placeholder)
- CREATIVE QA        → core/creative_qa.py (placeholder)

Todos os contratos de entrada/saída usam dicts JSON documentados.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import time
from pathlib import Path
from typing import Any, Optional


# ─────────────────────────────────────────────────────────────────
#  TIPOS DE TAREFA SUPORTADOS
# ─────────────────────────────────────────────────────────────────

TASK_TYPES = {
    # Imagem
    "gerar_imagem":        "IMAGE_ENGINE",
    "editar_imagem":       "IMAGE_ENGINE",
    "upscale_imagem":      "IMAGE_ENGINE",
    "thumbnail":           "IMAGE_ENGINE",

    # Vídeo
    "gerar_video":         "VIDEO_GENERATOR",
    "animar_imagem":       "VIDEO_GENERATOR",
    "b_roll":              "VIDEO_GENERATOR",

    # Cinematografia
    "plano_cenas":         "CINEMATIC_DIRECTOR",
    "filtro_zoompan":      "CINEMATIC_DIRECTOR",
    "color_grade":         "CINEMATIC_DIRECTOR",
    "prompt_visual":       "CINEMATIC_DIRECTOR",

    # Edição
    "concat_clips":        "VIDEO_EDITOR_PRO",
    "add_audio":           "VIDEO_EDITOR_PRO",
    "exportar_final":      "VIDEO_EDITOR_PRO",
    "legendas":            "VIDEO_EDITOR_PRO",

    # Motion
    "titulo_animado":      "MOTION_GRAPHICS",
    "legenda_animada":     "MOTION_GRAPHICS",
    "infografico":         "MOTION_GRAPHICS",

    # Áudio
    "narrar":              "AUDIO_MASTER",
    "masterizar":          "AUDIO_MASTER",
    "mixar":               "AUDIO_MASTER",
    "normalizar_audio":    "AUDIO_MASTER",

    # Consistência
    "setup_projeto":       "VISUAL_CONSISTENCY",
    "validar_consistencia":"VISUAL_CONSISTENCY",
    "prompt_continuidade": "VISUAL_CONSISTENCY",

    # Assets
    "registrar_asset":     "ASSET_MANAGER",
    "buscar_asset":        "ASSET_MANAGER",

    # QA
    "verificar_qualidade": "CREATIVE_QA",
    "verificar_resolucao": "CREATIVE_QA",
}


# ─────────────────────────────────────────────────────────────────
#  DISPATCHER PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def executar(tarefa: str, params: dict, verbose: bool = True) -> dict:
    """
    DARK MANAGER — Roteia tarefa para o agente especializado correto.

    Args:
        tarefa: Nome da tarefa (ver TASK_TYPES).
        params: Parâmetros da tarefa em dict.
        verbose: Imprimir logs de orquestração.

    Returns:
        Dict padronizado com:
        {
            "status": "ok" | "error",
            "agente": str,
            "tarefa": str,
            "resultado": Any,
            "tempo_s": float,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    Contrato JSON documentado — todos os agentes devem seguir este formato.
    """
    t0 = time.time()
    agente_nome = TASK_TYPES.get(tarefa, "DESCONHECIDO")

    if verbose:
        print(f"[DARK MANAGER] Tarefa={tarefa} → Agente={agente_nome}")

    try:
        resultado = _despachar(tarefa, agente_nome, params)
        status = "ok"
    except Exception as e:
        resultado = {"erro": str(e)}
        status = "error"
        if verbose:
            print(f"[DARK MANAGER] ERRO em {agente_nome}: {e}")

    elapsed = round(time.time() - t0, 3)

    return {
        "status": status,
        "agente": agente_nome,
        "tarefa": tarefa,
        "resultado": resultado,
        "tempo_s": elapsed,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def _despachar(tarefa: str, agente: str, params: dict) -> Any:
    """Roteamento interno — chama a função correta do agente."""

    # ── CINEMATIC DIRECTOR ────────────────────────────────────────
    if agente == "CINEMATIC_DIRECTOR":
        from core.cinematic_director import (
            criar_plano_cenas, gerar_prompt_visual,
            gerar_filtro_zoompan_antijitter, gerar_filtro_colorgrade,
            check_cinematic_director,
        )
        if tarefa == "plano_cenas":
            return criar_plano_cenas(params["roteiro"], params["canal_config"])
        if tarefa == "prompt_visual":
            return gerar_prompt_visual(params["cena"], params.get("preset", "documentario"))
        if tarefa == "filtro_zoompan":
            return gerar_filtro_zoompan_antijitter(
                params.get("preset", "documentario"),
                params.get("duracao", 5.0),
            )
        if tarefa == "color_grade":
            return gerar_filtro_colorgrade(params.get("preset", "documentario"))

    # ── AUDIO MASTER ──────────────────────────────────────────────
    if agente == "AUDIO_MASTER":
        from core.audio_master import (
            synthesize, masterizar, mixar_narr_trilha,
            normalizar_lufs, narrar_roteiro_completo,
        )
        if tarefa == "narrar":
            return synthesize(
                params["texto"],
                Path(params["output_path"]),
                duracao_esperada=params.get("duracao", 5.0),
            )
        if tarefa == "masterizar":
            p = masterizar(Path(params["input"]), Path(params["output"]))
            return {"output": str(p)}
        if tarefa == "mixar":
            p = mixar_narr_trilha(
                Path(params["narr"]), Path(params["trilha"]), Path(params["output"]),
                vol_narr=params.get("vol_narr", 1.0),
                vol_trilha=params.get("vol_trilha", 0.12),
            )
            return {"output": str(p)}
        if tarefa == "normalizar_audio":
            p = normalizar_lufs(Path(params["input"]), Path(params["output"]))
            return {"output": str(p)}

    # ── VISUAL CONSISTENCY ────────────────────────────────────────
    if agente == "VISUAL_CONSISTENCY":
        from core.visual_consistency import (
            setup_projeto, validar_consistencia_roteiro,
            gerar_prompt_com_continuidade, VisualConsistencyDB,
        )
        if tarefa == "setup_projeto":
            db = setup_projeto(
                Path(params["output_dir"]),
                params["canal_config"],
                preset_nome=params.get("preset"),
            )
            return {"db_path": str(db.db_path)}
        if tarefa == "validar_consistencia":
            db = VisualConsistencyDB(Path(params["output_dir"]))
            return validar_consistencia_roteiro(params["cenas"], db)
        if tarefa == "prompt_continuidade":
            db = VisualConsistencyDB(Path(params["output_dir"]))
            return gerar_prompt_com_continuidade(
                params["cena"], db, params.get("prompt_base", "")
            )

    # ── VIDEO EDITOR PRO ──────────────────────────────────────────
    if agente == "VIDEO_EDITOR_PRO":
        from core.ffmpeg_utils import (
            concat_videos, add_audio, export_final, burn_subtitles,
        )
        if tarefa == "concat_clips":
            clips = [Path(c) for c in params["clips"]]
            output = Path(params["output"])
            n = len(clips)
            transition = params.get("transition", "none" if n > 3 else "dissolve")
            concat_videos(clips, output, transition=transition)
            return {"output": str(output)}
        if tarefa == "add_audio":
            p = add_audio(Path(params["video"]), Path(params["audio"]), Path(params["output"]))
            return {"output": str(p)}
        if tarefa == "exportar_final":
            p = export_final(
                Path(params["video"]), Path(params["output"]),
                resolution=params.get("resolution", "1920x1080"),
                format=params.get("format", "16:9"),
            )
            return {"output": str(p)}
        if tarefa == "legendas":
            p = burn_subtitles(Path(params["video"]), Path(params["srt"]), Path(params["output"]))
            return {"output": str(p)}

    # ── AGENTES PLACEHOLDER (a implementar nas próximas fases) ────
    if agente in ("IMAGE_ENGINE", "VIDEO_GENERATOR", "MOTION_GRAPHICS",
                   "ASSET_MANAGER", "CREATIVE_QA"):
        return _placeholder(agente, tarefa, params)

    raise ValueError(f"Tarefa '{tarefa}' não mapeada para nenhum agente disponível.")


def _placeholder(agente: str, tarefa: str, params: dict) -> dict:
    """Retorna resultado de placeholder para agentes ainda não implementados."""
    return {
        "status": "placeholder",
        "agente": agente,
        "tarefa": tarefa,
        "mensagem": f"Agente {agente} será implementado nas próximas fases do DARK CREATIVE LAB.",
        "params_recebidos": list(params.keys()),
    }


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO DE TODOS OS AGENTES
# ─────────────────────────────────────────────────────────────────

def check_all_agents() -> dict:
    """Verifica status de todos os agentes disponíveis."""
    resultados = {}

    # Cinematic Director
    try:
        from core.cinematic_director import check_cinematic_director
        resultados["CINEMATIC_DIRECTOR"] = check_cinematic_director()
    except Exception as e:
        resultados["CINEMATIC_DIRECTOR"] = {"status": "error", "erro": str(e)}

    # Audio Master
    try:
        from core.audio_master import check_audio_master
        resultados["AUDIO_MASTER"] = check_audio_master()
    except Exception as e:
        resultados["AUDIO_MASTER"] = {"status": "error", "erro": str(e)}

    # Visual Consistency
    try:
        from core.visual_consistency import check_visual_consistency
        resultados["VISUAL_CONSISTENCY"] = check_visual_consistency()
    except Exception as e:
        resultados["VISUAL_CONSISTENCY"] = {"status": "error", "erro": str(e)}

    # FFmpeg (Video Editor Pro)
    try:
        from core.ffmpeg_utils import check_ffmpeg
        resultados["VIDEO_EDITOR_PRO"] = {"status": "ok" if check_ffmpeg() else "ffmpeg_missing"}
    except Exception as e:
        resultados["VIDEO_EDITOR_PRO"] = {"status": "error", "erro": str(e)}

    # Placeholders
    for agente in ("IMAGE_ENGINE", "VIDEO_GENERATOR", "MOTION_GRAPHICS",
                    "ASSET_MANAGER", "CREATIVE_QA"):
        resultados[agente] = {
            "status": "placeholder",
            "fase": _fase_agente(agente),
        }

    n_ok = sum(1 for v in resultados.values() if v.get("status") in ("ok", "placeholder"))

    return {
        "status": "ok",
        "agentes": resultados,
        "total": len(resultados),
        "operacionais": n_ok,
        "tarefas_suportadas": list(TASK_TYPES.keys()),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def _fase_agente(agente: str) -> str:
    mapa = {
        "IMAGE_ENGINE":   "Fase 2 — Image Studio",
        "VIDEO_GENERATOR":"Fase 3 — Video Generator",
        "MOTION_GRAPHICS":"Fase 7 — Motion Graphics",
        "ASSET_MANAGER":  "Fase 9 — Integração DARK STUDIO AAA",
        "CREATIVE_QA":    "Fase 10 — Testes de produção",
    }
    return mapa.get(agente, "A implementar")
