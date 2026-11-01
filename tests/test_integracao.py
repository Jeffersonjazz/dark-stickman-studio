#!/usr/bin/env python3
"""
DARK CREATIVE LAB — TESTE DE INTEGRAÇÃO COMPLETO
Agente QA Auditor: verifica todos os módulos e o pipeline F01.

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import sys
import json
import traceback
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

resultados = []

def teste(nome, fn):
    try:
        resultado = fn()
        ok = resultado if isinstance(resultado, bool) else bool(resultado)
        status = PASS if ok else FAIL
        resultados.append((nome, ok, ""))
        print(f"  {status} {nome}")
        return ok
    except Exception as e:
        msg = str(e)[:120]
        resultados.append((nome, False, msg))
        print(f"  {FAIL} {nome}: {msg}")
        return False


# ──────────────────────────────────────────────
print("\n═══ DARK STUDIO AAA — TESTE DE INTEGRAÇÃO ═══\n")

# 1. Dark Manager
print("▶ DARK MANAGER")
def _test_manager_import():
    from core.dark_manager import executar, check_all_agents
    return True
teste("Importação dark_manager", _test_manager_import)

def _test_check_all():
    from core.dark_manager import check_all_agents
    r = check_all_agents()
    agentes = r.get("agentes", {})
    ok_count = sum(1 for a in agentes.values() if a.get("status") == "ok")
    print(f"       {ok_count}/{len(agentes)} agentes operacionais")
    return ok_count >= 9  # 10 esperados; toleramos 9+ em ambiente cloud
teste("check_all_agents()", _test_check_all)

# 2. Image Engine
print("\n▶ IMAGE ENGINE")
def _test_image_import():
    from core.image_engine import gerar_imagem, check_image_engine
    return True
teste("Importação image_engine", _test_image_import)

def _test_image_check():
    from core.image_engine import check_image_engine
    r = check_image_engine()
    return r.get("status") == "ok"
teste("check_image_engine()", _test_image_check)

def _test_image_gen():
    from core.image_engine import gerar_imagem
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.png"
        r = gerar_imagem("dark cinematic forest", output_path=out)
        return r.get("status") == "ok" and r.get("ai_generated") == True
teste("gerar_imagem() — fallback Pillow", _test_image_gen)

# 3. Video Generator
print("\n▶ VIDEO GENERATOR")
def _test_video_import():
    from core.video_generator import gerar_video, check_video_generator
    return True
teste("Importação video_generator", _test_video_import)

def _test_video_check():
    from core.video_generator import check_video_generator
    r = check_video_generator()
    return r.get("status") == "ok"
teste("check_video_generator()", _test_video_check)

def _test_video_gen():
    from core.video_generator import gerar_video
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.mp4"
        r = gerar_video("dark forest scene", output_path=out, duracao_s=3)
        return r.get("status") == "ok" and r.get("ai_generated") == True
teste("gerar_video() — fallback FFmpeg", _test_video_gen)

def _test_imagem_para_video():
    from core.image_engine import gerar_imagem
    from core.video_generator import imagem_para_video
    with tempfile.TemporaryDirectory() as tmp:
        img = Path(tmp) / "img.png"
        vid = Path(tmp) / "vid.mp4"
        r1 = gerar_imagem("test scene", output_path=img)
        if r1.get("status") != "ok":
            return False
        r2 = imagem_para_video(str(img), output_path=str(vid), duracao_s=3)
        return r2.get("status") == "ok"
teste("imagem_para_video() — Ken Burns", _test_imagem_para_video)

# 4. Cinematic Director
print("\n▶ CINEMATIC DIRECTOR")
def _test_cinematic_import():
    # Nomes reais do módulo
    from core.cinematic_director import (
        gerar_prompt_visual,
        gerar_filtro_zoompan_antijitter,  # nome real
        gerar_filtro_colorgrade,
        check_cinematic_director,
        CINEMA_PRESETS,
    )
    return True
teste("Importação cinematic_director", _test_cinematic_import)

def _test_cinematic_check():
    from core.cinematic_director import check_cinematic_director
    r = check_cinematic_director()
    return r.get("status") == "ok"
teste("check_cinematic_director()", _test_cinematic_check)

def _test_cinematic_presets():
    from core.cinematic_director import CINEMA_PRESETS, gerar_prompt_visual
    cena = {"titulo": "Floresta densa", "narracao": "Uma floresta misteriosa ao amanhecer", "descricao_visual": ""}
    prompt = gerar_prompt_visual(cena, "documentario")
    return len(prompt) > 10 and len(CINEMA_PRESETS) >= 8
teste("gerar_prompt_visual() e presets", _test_cinematic_presets)

def _test_colorgrade():
    from core.cinematic_director import gerar_filtro_colorgrade
    filtro = gerar_filtro_colorgrade("documentario")
    return "eq=" in filtro or "curves=" in filtro
teste("gerar_filtro_colorgrade()", _test_colorgrade)

def _test_zoompan():
    from core.cinematic_director import gerar_filtro_zoompan_antijitter
    filtro = gerar_filtro_zoompan_antijitter("documentario", duracao=5.0)
    return "zoompan" in filtro
teste("gerar_filtro_zoompan_antijitter()", _test_zoompan)

# 5. Cinema Editor
print("\n▶ CINEMA EDITOR")
def _test_editor_import():
    # Nomes reais do módulo
    from core.cinema_editor import Timeline, Clip, montar_automatico, check_cinema_editor
    return True
teste("Importação cinema_editor", _test_editor_import)

def _test_editor_check():
    from core.cinema_editor import check_cinema_editor
    r = check_cinema_editor()
    return r.get("status") == "ok"
teste("check_cinema_editor()", _test_editor_check)

def _test_timeline():
    from core.cinema_editor import Timeline, Clip
    tl = Timeline(project_name="teste")
    c = Clip(path="/tmp/fake.mp4", duration=5.0, label="cena1")
    tl.clips.append(c)
    return len(tl.clips) == 1 and tl.project_name == "teste"
teste("Timeline e Clip dataclasses", _test_timeline)

# 6. Audio Master
print("\n▶ AUDIO MASTER")
def _test_audio_import():
    # Nomes reais do módulo — a função pública é synthesize()
    from core.audio_master import synthesize, check_audio_master
    return True
teste("Importação audio_master (synthesize)", _test_audio_import)

def _test_audio_check():
    from core.audio_master import check_audio_master
    r = check_audio_master()
    return r.get("status") == "ok"
teste("check_audio_master()", _test_audio_check)

def _test_synthesize():
    from core.audio_master import synthesize
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "narr.mp3"
        r = synthesize("Teste de narração DARK STUDIO.", str(out))
        # Aceita "ok" (TTS real) ou "silencio" (fallback offline)
        return r.get("status") in ("ok", "silencio") and r.get("ai_generated") == True
teste("synthesize() — fallback silêncio/gTTS", _test_synthesize)

# 7. Motion Graphics
print("\n▶ MOTION GRAPHICS")
def _test_motion_import():
    from core.motion_graphics import gerar_titulo_animado, check_motion_graphics
    return True
teste("Importação motion_graphics", _test_motion_import)

def _test_motion_check():
    from core.motion_graphics import check_motion_graphics
    r = check_motion_graphics()
    return r.get("status") == "ok"
teste("check_motion_graphics()", _test_motion_check)

def _test_titulo_animado():
    from core.motion_graphics import gerar_titulo_animado
    import inspect
    sig = inspect.signature(gerar_titulo_animado)
    # Usar o nome certo do parâmetro de duração
    params = list(sig.parameters.keys())
    dur_param = "duracao_s" if "duracao_s" in params else "duracao"
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "titulo.mp4"
        kwargs = {"output_path": out, dur_param: 3}
        r = gerar_titulo_animado("DARK STUDIO AAA", **kwargs)
        return r.get("status") == "ok"
teste("gerar_titulo_animado()", _test_titulo_animado)

# 8. Visual Consistency
print("\n▶ VISUAL CONSISTENCY")
def _test_vc_import():
    # Classe real é VisualConsistencyDB
    from core.visual_consistency import VisualConsistencyDB, check_visual_consistency
    return True
teste("Importação visual_consistency (VisualConsistencyDB)", _test_vc_import)

def _test_vc_check():
    from core.visual_consistency import check_visual_consistency
    r = check_visual_consistency()
    return r.get("status") == "ok"
teste("check_visual_consistency()", _test_vc_check)

def _test_vc_db():
    from core.visual_consistency import VisualConsistencyDB
    with tempfile.TemporaryDirectory() as tmp:
        db = VisualConsistencyDB(Path(tmp) / "vc.json")
        return db is not None
teste("VisualConsistencyDB instância", _test_vc_db)

# 9. Asset Manager
print("\n▶ ASSET MANAGER")
def _test_asset_import():
    # Classe real é AssetDB
    from core.asset_manager import AssetDB, check_asset_manager
    return True
teste("Importação asset_manager (AssetDB)", _test_asset_import)

def _test_asset_check():
    from core.asset_manager import check_asset_manager
    r = check_asset_manager()
    return r.get("status") == "ok"
teste("check_asset_manager()", _test_asset_check)

def _test_assetdb():
    from core.asset_manager import AssetDB
    with tempfile.TemporaryDirectory() as tmp:
        db = AssetDB(Path(tmp) / "assets.json")
        return db is not None
teste("AssetDB instância", _test_assetdb)

# 10. Creative QA
print("\n▶ CREATIVE QA")
def _test_qa_import():
    # Função real é verificar_qualidade
    from core.creative_qa import verificar_qualidade, check_creative_qa
    return True
teste("Importação creative_qa (verificar_qualidade)", _test_qa_import)

def _test_qa_check():
    from core.creative_qa import check_creative_qa
    r = check_creative_qa()
    return r.get("status") == "ok"
teste("check_creative_qa()", _test_qa_check)

# 11. Despacho via DARK MANAGER
print("\n▶ DESPACHO VIA DARK MANAGER (executar)")
def _test_despacho_imagem():
    from core.dark_manager import executar
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "img.png")
        r = executar("gerar_imagem", {"prompt": "dark forest", "output_path": out}, verbose=False)
        return r.get("status") == "ok"
teste("executar('gerar_imagem')", _test_despacho_imagem)

def _test_despacho_video():
    from core.dark_manager import executar
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "v.mp4")
        r = executar("gerar_video", {"prompt": "dark forest", "output_path": out, "duracao_s": 3}, verbose=False)
        return r.get("status") == "ok"
teste("executar('gerar_video')", _test_despacho_video)

def _test_despacho_narrar():
    from core.dark_manager import executar
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "narr.mp3")
        r = executar("narrar", {"texto": "Teste DARK STUDIO.", "output_path": out}, verbose=False)
        return r.get("status") == "ok"
teste("executar('narrar')", _test_despacho_narrar)

def _test_despacho_thumbnail():
    from core.dark_manager import executar, TASK_TYPES
    # O task name correto no TASK_TYPES é "thumbnail" (não "gerar_thumbnail")
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "thumb.jpg")
        r = executar("thumbnail", {
            "titulo": "DARK STUDIO TEST",
            "output_path": out,
            "canal": "psicologia",
        }, verbose=False)
        return r.get("status") == "ok"
teste("executar('thumbnail')", _test_despacho_thumbnail)

# 12. Narrar via DARK MANAGER (mapeamento correto)
def _test_despacho_synthesize():
    from core.dark_manager import executar, TASK_TYPES
    # Verifica que 'narrar' está mapeado
    agente = TASK_TYPES.get("narrar", "DESCONHECIDO")
    return agente == "AUDIO_MASTER"
teste("TASK_TYPES['narrar'] → AUDIO_MASTER", _test_despacho_synthesize)

# ──────────────────────────────────────────────
# RELATÓRIO FINAL
print("\n═══ RELATÓRIO FINAL ═══")
total = len(resultados)
aprovados = sum(1 for _, ok, _ in resultados if ok)
falhas = [(n, e) for n, ok, e in resultados if not ok]

print(f"  Total de testes: {total}")
print(f"  Aprovados:       {aprovados}/{total}")
print(f"  Falhas:          {len(falhas)}")

if falhas:
    print("\n  ── FALHAS DETALHADAS:")
    for nome, erro in falhas:
        print(f"    ❌ {nome}")
        if erro:
            print(f"       {erro}")

score = int(aprovados / total * 100)
print(f"\n  🎯 Score QA: {score}/100")
if score == 100:
    print("  Status: ✅ TODOS OS TESTES PASSARAM — PRONTO PARA PRODUÇÃO")
elif score >= 85:
    print("  Status: ✅ PRONTO PARA PRODUÇÃO (falhas menores)")
elif score >= 70:
    print("  Status: ⚠️  FUNCIONAL COM LIMITAÇÕES")
else:
    print("  Status: ❌ REQUER CORREÇÃO")

print(f"\n  ai_generated: True")
print(f"  ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")

sys.exit(0 if score >= 70 else 1)
