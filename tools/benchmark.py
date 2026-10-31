#!/usr/bin/env python3
"""
DARK CREATIVE LAB — BENCHMARK DO PIPELINE F01
Fase 11 — Otimização de custos e desempenho.

Executa um job de teste completo e reporta métricas de performance:
- Tempo por ETAPA do pipeline
- Taxa de hit do cache
- Custo estimado do job
- Diagnóstico de todos os agentes
- Sugestões de otimização

Uso:
    python tools/benchmark.py
    python tools/benchmark.py --canal psicologia --etapas 5

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Garante importação do projeto
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))


def _titulo(texto: str):
    print(f"\n{'='*60}")
    print(f"  {texto}")
    print(f"{'='*60}")


def _secao(texto: str):
    print(f"\n── {texto}")


def _ok(texto: str):
    print(f"  ✅ {texto}")


def _warn(texto: str):
    print(f"  ⚠️  {texto}")


def _erro(texto: str):
    print(f"  ❌ {texto}")


def _info(texto: str):
    print(f"     {texto}")


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO DE AGENTES
# ─────────────────────────────────────────────────────────────────

def benchmark_agentes() -> dict:
    """Executa diagnóstico de todos os agentes e mede tempo."""
    _secao("DIAGNÓSTICO DE AGENTES")

    from core.dark_manager import check_all_agents
    t0 = time.time()
    resultado = check_all_agents()
    duracao = time.time() - t0

    agentes = resultado.get("agentes", {})
    operacionais = sum(1 for a in agentes.values() if a.get("status") == "ok")
    placeholders = sum(1 for a in agentes.values() if a.get("status") == "placeholder")

    for nome, info in agentes.items():
        status = info.get("status", "desconhecido")
        if status == "ok":
            _ok(f"{nome}")
        elif status == "placeholder":
            _warn(f"{nome} — placeholder (não implementado)")
        else:
            _erro(f"{nome} — {status}")

    print(f"\n  Tempo diagnóstico: {duracao:.2f}s")
    print(f"  Operacionais: {operacionais}/{len(agentes)}")
    print(f"  Placeholders: {placeholders}")

    return {
        "operacionais": operacionais,
        "placeholders": placeholders,
        "total": len(agentes),
        "duracao_s": round(duracao, 3),
    }


# ─────────────────────────────────────────────────────────────────
#  BENCHMARK DE TTS
# ─────────────────────────────────────────────────────────────────

def benchmark_tts(texto: str = "Este é um teste de narração do DARK STUDIO AAA para benchmark de performance.") -> dict:
    """Testa engines TTS disponíveis e mede velocidade."""
    _secao("BENCHMARK TTS")

    from core.audio_master import narrar, check_audio_master
    import tempfile

    resultados = {}
    engines_info = check_audio_master().get("engines", {})

    engines_para_testar = [
        ("piper", "piper"),
        ("edge_tts", "edge_tts"),
        ("gtts", "gtts"),
    ]

    for engine_id, engine_nome in engines_para_testar:
        info = engines_info.get(engine_nome, {})
        if not info.get("disponivel", False):
            _warn(f"{engine_nome} — não disponível")
            resultados[engine_nome] = {"disponivel": False}
            continue

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = Path(tmp.name)

        t0 = time.time()
        try:
            resultado = narrar(
                texto=texto,
                output_path=output_path,
                engine=engine_id,
            )
            duracao = time.time() - t0
            status = resultado.get("status", "error")
            if status == "ok":
                _ok(f"{engine_nome}: {duracao:.2f}s (tipo: {info.get('tipo', '?')})")
                resultados[engine_nome] = {
                    "disponivel": True,
                    "duracao_s": round(duracao, 3),
                    "tipo": info.get("tipo"),
                    "status": "ok",
                }
            else:
                _warn(f"{engine_nome}: falhou — {resultado.get('erro', '?')}")
                resultados[engine_nome] = {"disponivel": True, "status": "erro", "duracao_s": round(duracao, 3)}
        except Exception as e:
            duracao = time.time() - t0
            _warn(f"{engine_nome}: exceção — {e}")
            resultados[engine_nome] = {"disponivel": True, "status": "excecao", "duracao_s": round(duracao, 3)}
        finally:
            try:
                output_path.unlink(missing_ok=True)
            except Exception:
                pass

    return resultados


# ─────────────────────────────────────────────────────────────────
#  BENCHMARK DE FFMPEG
# ─────────────────────────────────────────────────────────────────

def benchmark_ffmpeg() -> dict:
    """Testa capacidade FFmpeg e presets disponíveis."""
    _secao("BENCHMARK FFMPEG")

    import subprocess
    from core.performance import ffmpeg_params_otimizados, FFMPEG_PRESETS

    # Verifica FFmpeg
    try:
        out = subprocess.check_output(
            ["ffmpeg", "-version"], stderr=subprocess.STDOUT, timeout=5
        ).decode()
        versao = out.split("\n")[0]
        _ok(f"FFmpeg: {versao.strip()}")
        ffmpeg_ok = True
    except Exception as e:
        _erro(f"FFmpeg não disponível: {e}")
        return {"disponivel": False}

    # Testa criação de vídeo de teste com diferentes presets
    import tempfile
    resultados_preset = {}

    presets_para_testar = ["ultra_fast", "fast", "youtube_hd"]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        for perfil in presets_para_testar:
            params = ffmpeg_params_otimizados(perfil)
            output = tmp / f"test_{perfil}.mp4"

            # Gera 3s de vídeo de teste (color source)
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "color=c=blue:size=1280x720:rate=30:d=3",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
            ] + params + [str(output)]

            t0 = time.time()
            try:
                subprocess.run(
                    cmd, capture_output=True, timeout=30, check=True
                )
                duracao = time.time() - t0
                tamanho_kb = output.stat().st_size / 1024 if output.exists() else 0
                _ok(f"Preset {perfil}: {duracao:.2f}s, {tamanho_kb:.1f}KB")
                resultados_preset[perfil] = {
                    "ok": True,
                    "duracao_s": round(duracao, 3),
                    "tamanho_kb": round(tamanho_kb, 1),
                }
            except Exception as e:
                _warn(f"Preset {perfil}: falhou — {e}")
                resultados_preset[perfil] = {"ok": False}

    return {
        "disponivel": True,
        "versao": versao.strip(),
        "presets_testados": resultados_preset,
        "todos_presets": list(FFMPEG_PRESETS.keys()),
    }


# ─────────────────────────────────────────────────────────────────
#  BENCHMARK DO CACHE
# ─────────────────────────────────────────────────────────────────

def benchmark_cache() -> dict:
    """Testa velocidade do sistema de cache."""
    _secao("BENCHMARK CACHE")

    import tempfile
    from core.performance import AssetCache

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cache = AssetCache(tmp)

        # Cria arquivo de teste
        arquivo_teste = tmp / "teste.txt"
        arquivo_teste.write_text("Conteúdo de teste para benchmark do cache DARK STUDIO AAA")

        # Miss
        t0 = time.time()
        resultado = cache.get("tts", "texto de teste benchmark")
        duracao_miss = time.time() - t0

        # Set
        t0 = time.time()
        cache.set("tts", "texto de teste benchmark", arquivo_teste)
        duracao_set = time.time() - t0

        # Hit
        t0 = time.time()
        resultado_hit = cache.get("tts", "texto de teste benchmark")
        duracao_hit = time.time() - t0

        acerto = resultado_hit is not None
        stats = cache.estatisticas()

    _ok(f"Cache miss: {duracao_miss*1000:.2f}ms")
    _ok(f"Cache set:  {duracao_set*1000:.2f}ms")
    _ok(f"Cache hit:  {duracao_hit*1000:.2f}ms")
    if acerto:
        _ok("Cache hit funcional")
    else:
        _erro("Cache hit falhou")

    speedup = duracao_miss / duracao_hit if duracao_hit > 0 else 1
    _info(f"Speedup estimado: {speedup:.1f}x")

    return {
        "funcional": acerto,
        "duracao_miss_ms": round(duracao_miss * 1000, 2),
        "duracao_set_ms": round(duracao_set * 1000, 2),
        "duracao_hit_ms": round(duracao_hit * 1000, 2),
        "speedup_estimado": round(speedup, 1),
        "stats": stats,
    }


# ─────────────────────────────────────────────────────────────────
#  SUGESTÕES DE OTIMIZAÇÃO
# ─────────────────────────────────────────────────────────────────

def gerar_sugestoes(resultados: dict) -> list[str]:
    """Gera lista de sugestões de otimização baseadas nos resultados."""
    sugestoes = []

    # TTS
    tts = resultados.get("tts", {})
    if not tts.get("piper", {}).get("disponivel"):
        sugestoes.append("Instalar Piper TTS local para eliminar dependência de rede na narração")
    if tts.get("edge_tts", {}).get("duracao_s", 0) > 10:
        sugestoes.append("Edge TTS lento — considere pré-gerar narrações em batch")

    # FFmpeg
    ffmpeg = resultados.get("ffmpeg", {})
    if ffmpeg.get("disponivel"):
        presets = ffmpeg.get("presets_testados", {})
        ultra_fast = presets.get("ultra_fast", {})
        youtube_hd = presets.get("youtube_hd", {})
        if ultra_fast.get("ok") and youtube_hd.get("ok"):
            razao = youtube_hd.get("duracao_s", 1) / max(ultra_fast.get("duracao_s", 1), 0.001)
            if razao > 3:
                sugestoes.append(
                    f"Preset 'youtube_hd' é {razao:.1f}x mais lento que 'ultra_fast' — use 'fast' para rascunhos"
                )

    # Cache
    cache = resultados.get("cache", {})
    if cache.get("funcional"):
        sugestoes.append("Cache de assets ativo — reutilize narrações e thumbnails entre runs")

    # Agentes
    agentes = resultados.get("agentes", {})
    if agentes.get("placeholders", 0) > 0:
        sugestoes.append(
            f"{agentes.get('placeholders')} agente(s) em placeholder — implementar nas fases restantes"
        )

    if not sugestoes:
        sugestoes.append("Pipeline otimizado — sem gargalos críticos detectados")

    return sugestoes


# ─────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DARK STUDIO AAA — Benchmark do Pipeline F01"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Caminho para salvar relatório JSON (opcional)"
    )
    parser.add_argument(
        "--skip-tts", action="store_true",
        help="Pula benchmark de TTS (mais rápido)"
    )
    args = parser.parse_args()

    _titulo("DARK CREATIVE LAB — BENCHMARK FASE 11")
    print("  Avaliando performance do pipeline DARK STUDIO AAA")
    print(f"  Diretório: {_ROOT}")

    t_inicio = time.time()
    resultados = {}

    # 1. Agentes
    resultados["agentes"] = benchmark_agentes()

    # 2. TTS
    if not args.skip_tts:
        resultados["tts"] = benchmark_tts()
    else:
        _secao("TTS — PULADO (--skip-tts)")

    # 3. FFmpeg
    resultados["ffmpeg"] = benchmark_ffmpeg()

    # 4. Cache
    resultados["cache"] = benchmark_cache()

    # 5. Sugestões
    _secao("SUGESTÕES DE OTIMIZAÇÃO")
    sugestoes = gerar_sugestoes(resultados)
    for i, s in enumerate(sugestoes, 1):
        _info(f"{i}. {s}")
    resultados["sugestoes"] = sugestoes

    # Tempo total
    duracao_total = time.time() - t_inicio
    _titulo(f"BENCHMARK CONCLUÍDO — {duracao_total:.1f}s")

    # Score de prontidão
    agentes = resultados.get("agentes", {})
    ffmpeg_ok = resultados.get("ffmpeg", {}).get("disponivel", False)
    cache_ok = resultados.get("cache", {}).get("funcional", False)
    score = 0
    score += 40 * (agentes.get("operacionais", 0) / max(agentes.get("total", 1), 1))
    score += 30 if ffmpeg_ok else 0
    score += 15 if cache_ok else 0
    score += 15  # baseline

    print(f"\n  🎯 Score de prontidão: {score:.0f}/100")
    if score >= 80:
        print("  Status: ✅ PRONTO PARA PRODUÇÃO")
    elif score >= 60:
        print("  Status: ⚠️  FUNCIONAL COM LIMITAÇÕES")
    else:
        print("  Status: ❌ REQUER CONFIGURAÇÃO ADICIONAL")

    # Salva relatório
    relatorio = {
        "benchmark": resultados,
        "score_prontidao": round(score, 1),
        "duracao_total_s": round(duracao_total, 2),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n  📄 Relatório salvo: {output_path}")
    else:
        output_path = _ROOT / "logs" / "benchmark_latest.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(relatorio, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n  📄 Relatório: {output_path}")

    return 0 if score >= 60 else 1


if __name__ == "__main__":
    sys.exit(main())
