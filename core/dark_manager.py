"""
DARK CREATIVE LAB — DARK MANAGER
Orquestrador central dos agentes especializados.

Roteia tarefas para os agentes corretos com base no tipo de operação
e retorna resultado padronizado em JSON.

Agentes disponíveis:
- IMAGE ENGINE       → core/image_engine.py ✅
- VIDEO GENERATOR    → core/video_generator.py ✅
- CINEMATIC DIRECTOR → core/cinematic_director.py
- VIDEO EDITOR PRO   → core/ffmpeg_utils.py (wrapper)
- MOTION GRAPHICS    → core/motion_graphics.py ✅
- AUDIO MASTER       → core/audio_master.py
- VISUAL CONSISTENCY → core/visual_consistency.py
- ASSET MANAGER      → core/asset_manager.py ✅
- CREATIVE QA        → core/creative_qa.py ✅

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
    "gerar_cenas":         "VIDEO_GENERATOR",

    # Cinematografia
    "plano_cenas":         "CINEMATIC_DIRECTOR",
    "filtro_zoompan":      "CINEMATIC_DIRECTOR",
    "color_grade":         "CINEMATIC_DIRECTOR",
    "prompt_visual":       "CINEMATIC_DIRECTOR",

    # Edição (CINEMA EDITOR)
    "concat_clips":        "VIDEO_EDITOR_PRO",
    "add_audio":           "VIDEO_EDITOR_PRO",
    "exportar_final":      "VIDEO_EDITOR_PRO",
    "legendas":            "VIDEO_EDITOR_PRO",
    "montar_automatico":   "VIDEO_EDITOR_PRO",
    "renderizar":          "VIDEO_EDITOR_PRO",
    "exportar_resolucoes": "VIDEO_EDITOR_PRO",
    "remover_silencio":    "VIDEO_EDITOR_PRO",
    "renderizar_lote":     "VIDEO_EDITOR_PRO",

    # Motion
    "titulo_animado":      "MOTION_GRAPHICS",
    "legenda_animada":     "MOTION_GRAPHICS",
    "infografico":         "MOTION_GRAPHICS",
    "gerar_intro":         "MOTION_GRAPHICS",
    "gerar_outro":         "MOTION_GRAPHICS",
    "pacote_canal":        "MOTION_GRAPHICS",

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
    "organizar_projeto":   "ASSET_MANAGER",
    "listar_assets":       "ASSET_MANAGER",
    "varredura":           "ASSET_MANAGER",
    "validar_licenca":     "ASSET_MANAGER",

    # QA
    "verificar_qualidade": "CREATIVE_QA",
    "verificar_resolucao": "CREATIVE_QA",
    "verificar_audio_qa":  "CREATIVE_QA",
    "verificar_legenda":   "CREATIVE_QA",
    "verificar_conformidade": "CREATIVE_QA",

    # Performance (Fase 11)
    "benchmark":           "PERFORMANCE",
    "profiling":           "PERFORMANCE",
    "relatorio_custo":     "PERFORMANCE",
    "params_ffmpeg":       "PERFORMANCE",
    "stats_cache":         "PERFORMANCE",
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

    # ── VIDEO EDITOR PRO (CINEMA EDITOR) ─────────────────────────
    if agente == "VIDEO_EDITOR_PRO":
        from core.cinema_editor import (
            montar_automatico, renderizar, exportar_multi_resolucao,
            remover_silencio, renderizar_lote, Timeline, check_cinema_editor,
        )
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
        if tarefa == "montar_automatico":
            clips_v = [Path(c) for c in params["clips_video"]]
            narrs = [Path(n) for n in params["narracoes"]]
            tl = montar_automatico(
                clips_v, narrs,
                Path(params["output_dir"]),
                params["canal_config"],
                srt_path=Path(params["srt"]) if params.get("srt") else None,
                trilha_path=Path(params["trilha"]) if params.get("trilha") else None,
            )
            return {"timeline": str(Path(params["output_dir"]) / "timeline.json")}
        if tarefa == "renderizar":
            tl = Timeline.importar_json(Path(params["timeline_json"]))
            return renderizar(tl, Path(params["output"]))
        if tarefa == "exportar_resolucoes":
            return exportar_multi_resolucao(
                Path(params["input"]),
                Path(params["output_dir"]),
                resolucoes=params.get("resolucoes", ["1080p", "720p"]),
            )
        if tarefa == "remover_silencio":
            return remover_silencio(
                Path(params["input"]), Path(params["output"]),
                silence_threshold=params.get("threshold", -40.0),
            )
        if tarefa == "renderizar_lote":
            return {"resultados": renderizar_lote(params["projetos"])}

    # ── MOTION GRAPHICS ───────────────────────────────────────────
    if agente == "MOTION_GRAPHICS":
        from core.motion_graphics import (
            gerar_titulo_animado, gerar_lower_third,
            gerar_intro, gerar_outro, gerar_pacote_canal, gerar_contador,
        )
        if tarefa == "titulo_animado":
            return gerar_titulo_animado(
                params["texto"],
                Path(params["output"]),
                duracao=params.get("duracao", 4.0),
                animacao=params.get("animacao", "fade"),
                resolucao=params.get("resolucao", "1920x1080"),
            )
        if tarefa == "legenda_animada":
            return gerar_lower_third(
                params["titulo"],
                subtitulo=params.get("subtitulo", ""),
                output_path=Path(params["output"]),
                duracao=params.get("duracao", 5.0),
                resolucao=params.get("resolucao", "1920x1080"),
            )
        if tarefa == "infografico":
            # Contador animado como infográfico numérico
            return gerar_contador(
                params["valor"],
                params.get("label", ""),
                Path(params["output"]),
                duracao=params.get("duracao", 3.0),
                resolucao=params.get("resolucao", "1920x1080"),
            )
        if tarefa == "gerar_intro":
            return gerar_intro(
                params["canal_config"],
                Path(params["output"]),
                estilo=params.get("estilo", "documentario"),
                resolucao=params.get("resolucao", "1920x1080"),
            )
        if tarefa == "gerar_outro":
            return gerar_outro(
                params["canal_config"],
                Path(params["output"]),
                cta_texto=params.get("cta", "INSCREVA-SE"),
                resolucao=params.get("resolucao", "1920x1080"),
            )
        if tarefa == "pacote_canal":
            return gerar_pacote_canal(
                params["canal_config"],
                Path(params["output_dir"]),
                titulo_video=params.get("titulo", ""),
                resolucao=params.get("resolucao", "1920x1080"),
            )

    # ── ASSET MANAGER ─────────────────────────────────────────────
    if agente == "ASSET_MANAGER":
        from core.asset_manager import (
            registrar_asset, buscar_asset, organizar_projeto,
            listar_assets_projeto, varredura_assets, validar_licenca,
        )
        if tarefa == "registrar_asset":
            return registrar_asset(
                Path(params["arquivo"]),
                Path(params["projeto_dir"]),
                canal=params.get("canal", "global"),
                tags=params.get("tags", []),
                licenca=params.get("licenca", "MIT"),
                descricao=params.get("descricao", ""),
                copiar=params.get("copiar", False),
            )
        if tarefa == "buscar_asset":
            return buscar_asset(
                Path(params["projeto_dir"]),
                asset_id=params.get("asset_id"),
                tipo=params.get("tipo"),
                canal=params.get("canal"),
                tag=params.get("tag"),
                licenca=params.get("licenca"),
            )
        if tarefa == "organizar_projeto":
            return organizar_projeto(Path(params["projeto_dir"]), params.get("canal_config", {}))
        if tarefa == "listar_assets":
            return listar_assets_projeto(Path(params["projeto_dir"]))
        if tarefa == "varredura":
            return varredura_assets(Path(params["projeto_dir"]), canal=params.get("canal", "global"))
        if tarefa == "validar_licenca":
            return validar_licenca(params["licenca"])

    # ── CREATIVE QA ───────────────────────────────────────────────
    if agente == "CREATIVE_QA":
        from core.creative_qa import (
            verificar_qualidade, verificar_resolucao,
            verificar_audio, verificar_legenda, verificar_conformidade_ia,
        )
        if tarefa == "verificar_qualidade":
            return verificar_qualidade(
                Path(params["video"]),
                srt_path=Path(params["srt"]) if params.get("srt") else None,
                canal_config=params.get("canal_config"),
                minimo_s=params.get("minimo_s", 240),
            )
        if tarefa == "verificar_resolucao":
            return verificar_resolucao(Path(params["video"]))
        if tarefa == "verificar_audio_qa":
            return verificar_audio(Path(params["video"]))
        if tarefa == "verificar_legenda":
            return verificar_legenda(Path(params["srt"]))
        if tarefa == "verificar_conformidade":
            return verificar_conformidade_ia(Path(params["video"]))

    # ── PERFORMANCE ───────────────────────────────────────────────
    if agente == "PERFORMANCE":
        from core.performance import (
            ffmpeg_params_otimizados,
            sugerir_perfil_ffmpeg,
            check_performance,
            AssetCache,
            PipelineProfiler,
            CustoEstimador,
        )
        if tarefa == "params_ffmpeg":
            return {
                "status": "ok",
                "params": ffmpeg_params_otimizados(params.get("perfil", "balanced")),
                "perfil": params.get("perfil", "balanced"),
                "ai_generated": True,
            }
        if tarefa == "benchmark":
            return check_performance()
        if tarefa == "profiling":
            # Retorna relatório de profiling de um job salvo
            job_id = params.get("job_id", "unknown")
            output_dir = Path(params.get("output_dir", "."))
            profiler_file = output_dir / f"profiler_{job_id}.json"
            if profiler_file.exists():
                import json
                return {"status": "ok", "relatorio": json.loads(profiler_file.read_text())}
            return {"status": "not_found", "mensagem": f"Relatório de profiling não encontrado: {profiler_file}"}
        if tarefa == "relatorio_custo":
            # Retorna relatório de custo de um job (usa CustoEstimador como exemplo)
            estimador = CustoEstimador()
            return {"status": "ok", "relatorio": estimador.relatorio(), "ai_generated": True}
        if tarefa == "stats_cache":
            cache_dir = Path(params.get("cache_dir", "."))
            cache = AssetCache(cache_dir)
            return {"status": "ok", "stats": cache.estatisticas(), "ai_generated": True}
        return {"status": "error", "mensagem": f"Tarefa '{tarefa}' não reconhecida para PERFORMANCE"}

    # ── IMAGE ENGINE ──────────────────────────────────────────────
    if agente == "IMAGE_ENGINE":
        from core.image_engine import (
            gerar_imagem, upscalar_imagem, remover_fundo,
            corrigir_imagem, redimensionar, gerar_thumbnail,
        )
        if tarefa == "gerar_imagem":
            return gerar_imagem(
                prompt=params.get("prompt", "dark cinematic scene"),
                estilo=params.get("estilo", "cinematografico"),
                resolucao=params.get("resolucao", "youtube_thumbnail"),
                output_path=params.get("output_path"),
                engine=params.get("engine", "auto"),
                steps=params.get("steps", 30),
            )
        if tarefa == "upscale_imagem":
            return upscalar_imagem(
                input_path=params["input_path"],
                fator=params.get("fator", 2),
                output_path=params.get("output_path"),
            )
        if tarefa == "remover_fundo":
            return remover_fundo(
                input_path=params["input_path"],
                output_path=params.get("output_path"),
            )
        if tarefa == "corrigir_imagem":
            return corrigir_imagem(
                input_path=params["input_path"],
                brilho=params.get("brilho", 1.0),
                contraste=params.get("contraste", 1.0),
                saturacao=params.get("saturacao", 1.0),
                nitidez=params.get("nitidez", 1.0),
                output_path=params.get("output_path"),
            )
        if tarefa == "redimensionar":
            return redimensionar(
                input_path=params["input_path"],
                largura=params.get("largura"),
                altura=params.get("altura"),
                resolucao_preset=params.get("resolucao_preset"),
                manter_proporcao=params.get("manter_proporcao", True),
                output_path=params.get("output_path"),
            )
        if tarefa == "thumbnail":
            return gerar_thumbnail(
                titulo=params.get("titulo", "DARK VIDEO"),
                subtitulo=params.get("subtitulo", ""),
                background_path=params.get("background_path"),
                output_path=params.get("output_path"),
                estilo=params.get("estilo", "dark_channel"),
                canal=params.get("canal", "DARK STUDIO AAA"),
            )
        return {"status": "error", "mensagem": f"Tarefa '{tarefa}' não reconhecida para IMAGE_ENGINE"}

    # ── VIDEO GENERATOR ───────────────────────────────────────────
    if agente == "VIDEO_GENERATOR":
        from core.video_generator import (
            gerar_video, imagem_para_video, gerar_broll, gerar_cenas_video,
        )
        if tarefa == "gerar_video":
            return gerar_video(
                prompt=params.get("prompt", "dark cinematic scene"),
                output_path=params.get("output_path"),
                resolucao=params.get("resolucao", "1080p"),
                duracao_s=int(params.get("duracao_s", 8)),
                estilo=params.get("estilo", "cinematografico"),
                movimento=params.get("movimento", "zoom_in"),
                engine=params.get("engine", "auto"),
                steps=int(params.get("steps", 20)),
            )
        if tarefa == "animar_imagem":
            return imagem_para_video(
                input_path=params["input_path"],
                output_path=params.get("output_path"),
                duracao_s=int(params.get("duracao_s", 8)),
                movimento=params.get("movimento", "zoom_in"),
                resolucao=params.get("resolucao", "1080p"),
                estilo=params.get("estilo", "cinematografico"),
                fps=int(params.get("fps", 30)),
            )
        if tarefa == "b_roll":
            return {
                "status": "ok",
                "clips": gerar_broll(
                    prompt=params.get("prompt", "natureza cinematografica"),
                    output_dir=params["output_dir"],
                    num_clips=int(params.get("num_clips", 3)),
                    duracao_s=int(params.get("duracao_s", 6)),
                    resolucao=params.get("resolucao", "1080p"),
                    estilo=params.get("estilo", "documentario"),
                ),
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }
        if tarefa == "gerar_cenas":
            paths = gerar_cenas_video(
                cenas=params["cenas"],
                output_dir=params["output_dir"],
                preset=params.get("preset", "documentario"),
                verbose=params.get("verbose", False),
            )
            return {
                "status": "ok",
                "videos": paths,
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }
        return {"status": "error", "mensagem": f"Tarefa '{tarefa}' não reconhecida para VIDEO_GENERATOR"}

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

    # Cinema Editor (Video Editor Pro)
    try:
        from core.cinema_editor import check_cinema_editor
        resultados["VIDEO_EDITOR_PRO"] = check_cinema_editor()
    except Exception as e:
        resultados["VIDEO_EDITOR_PRO"] = {"status": "error", "erro": str(e)}

    # Motion Graphics
    try:
        from core.motion_graphics import check_motion_graphics
        resultados["MOTION_GRAPHICS"] = check_motion_graphics()
    except Exception as e:
        resultados["MOTION_GRAPHICS"] = {"status": "error", "erro": str(e)}

    # Asset Manager
    try:
        from core.asset_manager import check_asset_manager
        resultados["ASSET_MANAGER"] = check_asset_manager()
    except Exception as e:
        resultados["ASSET_MANAGER"] = {"status": "error", "erro": str(e)}

    # Creative QA
    try:
        from core.creative_qa import check_creative_qa
        resultados["CREATIVE_QA"] = check_creative_qa()
    except Exception as e:
        resultados["CREATIVE_QA"] = {"status": "error", "erro": str(e)}

    # Performance (Fase 11)
    try:
        from core.performance import check_performance
        resultados["PERFORMANCE"] = check_performance()
    except Exception as e:
        resultados["PERFORMANCE"] = {"status": "error", "erro": str(e)}

    # Image Engine (Fase 2 — implementado)
    try:
        from core.image_engine import check_image_engine
        resultados["IMAGE_ENGINE"] = check_image_engine()
    except Exception as e:
        resultados["IMAGE_ENGINE"] = {"status": "error", "erro": str(e)}

    # Video Generator (Fase 3 — implementado)
    try:
        from core.video_generator import check_video_generator
        resultados["VIDEO_GENERATOR"] = check_video_generator()
    except Exception as e:
        resultados["VIDEO_GENERATOR"] = {"status": "error", "erro": str(e)}

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
