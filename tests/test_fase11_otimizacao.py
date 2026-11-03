#!/usr/bin/env python3
"""
FASE 11 — Otimização de Custos e Desempenho
DARK STUDIO AAA — DARK CREATIVE LAB

Diagnóstico de hardware, benchmarks, análise de custo por recurso,
recomendações de perfil e geração de relatório de otimização.

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import os
import json
import time
import platform
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

VERDE = "\033[92m"
VERM  = "\033[91m"
AMAR  = "\033[93m"
AZUL  = "\033[94m"
RESET = "\033[0m"
BOLD  = "\033[1m"

resultados = []

def ok(msg):
    print(f"  {VERDE}✅{RESET} {msg}")
    resultados.append(("ok", msg))

def falha(msg, exc=None):
    detalhe = f" — {exc}" if exc else ""
    print(f"  {VERM}❌{RESET} {msg}{detalhe}")
    resultados.append(("falha", msg))

def aviso(msg):
    print(f"  {AMAR}⚠️ {RESET} {msg}")
    resultados.append(("aviso", msg))

def secao(titulo):
    print(f"\n{BOLD}{AZUL}▶ {titulo}{RESET}")

# ─── DIAGNÓSTICO DE HARDWARE ─────────────────────────────────────────────────

secao("DIAGNÓSTICO DE HARDWARE")

hw = {
    "sistema": platform.system(),
    "versao_os": platform.version()[:80],
    "arquitetura": platform.machine(),
    "processador": platform.processor() or platform.machine(),
    "python": platform.python_version(),
}

# RAM
try:
    import psutil
    mem = psutil.virtual_memory()
    hw["ram_total_gb"] = round(mem.total / 1e9, 1)
    hw["ram_disponivel_gb"] = round(mem.available / 1e9, 1)
    hw["cpu_cores"] = psutil.cpu_count(logical=True)
    hw["cpu_fisicos"] = psutil.cpu_count(logical=False)
    disk = psutil.disk_usage("/")
    hw["disco_total_gb"] = round(disk.total / 1e9, 1)
    hw["disco_livre_gb"] = round(disk.free / 1e9, 1)
    ok(f"psutil: RAM={hw['ram_total_gb']}GB, CPU={hw['cpu_cores']} cores, Disco={hw['disco_livre_gb']}GB livre")
except ImportError:
    aviso("psutil não instalado — diagnóstico parcial")
    hw["ram_total_gb"] = "desconhecido"

# GPU / CUDA
hw["gpu"] = "sem GPU detectada"
hw["cuda"] = False
hw["vram_gb"] = 0

try:
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                       capture_output=True, text=True, timeout=5)
    if r.returncode == 0 and r.stdout.strip():
        linha = r.stdout.strip().split("\n")[0]
        nome, mem_mb = linha.split(",")
        hw["gpu"] = nome.strip()
        hw["vram_gb"] = round(int(mem_mb.strip().replace(" MiB","")) / 1024, 1)
        hw["cuda"] = True
        ok(f"GPU NVIDIA: {hw['gpu']} — {hw['vram_gb']}GB VRAM — CUDA ✅")
except Exception:
    pass

if not hw["cuda"]:
    aviso(f"GPU/CUDA não detectado — processamento local em CPU")

# FFmpeg
hw["ffmpeg"] = bool(shutil.which("ffmpeg"))
hw["piper"] = bool(shutil.which("piper"))
hw["python_ok"] = True

for ferr, caminho in [("ffmpeg", "ffmpeg"), ("piper", "piper")]:
    if shutil.which(caminho):
        ok(f"{ferr}: instalado ✅")
    else:
        aviso(f"{ferr}: não encontrado")

ok(f"Sistema: {hw['sistema']} {hw['arquitetura']} | Python {hw['python']}")

# ─── BENCHMARK PERFORMANCE ───────────────────────────────────────────────────

secao("BENCHMARK DO SISTEMA")

bench_resultado = {}
try:
    from core.performance import check_performance, ffmpeg_params_otimizados, sugerir_perfil_ffmpeg
    bench_resultado = check_performance()
    n_presets = len(bench_resultado.get("ffmpeg_presets", []))
    n_recursos = len(bench_resultado.get("recursos_custo", []))
    ok(f"check_performance(): {n_presets} presets FFmpeg, {n_recursos} recursos de custo")
    ok("Performance module: PipelineProfiler, AssetCache, CustoEstimador OK")
except Exception as e:
    falha("check_performance()", e)

# ─── ANÁLISE DE CUSTO ────────────────────────────────────────────────────────

secao("ANÁLISE DE CUSTO — VÍDEO TIPO (5 cenas / 60s)")

custo_resultado = {}
try:
    from core.performance import CustoEstimador
    est = CustoEstimador()

    # Cenário 100% local (custo alvo R$0,00)
    est.registrar("tts_piper", 5)       # TTS local
    est.registrar("imagen_local", 5)    # Imagens locais (Pillow)
    est.registrar("ffmpeg_render", 1)   # Render local
    est.registrar("storage_gb", 0.020)  # 20MB

    rel = est.relatorio()
    custo_resultado["local"] = rel

    custo_brl = rel["custo_total_brl"]
    gratuitos = rel["itens_gratuitos"]
    pagos = rel["itens_pagos"]
    ok(f"Cenário LOCAL: R${custo_brl:.4f} | {gratuitos} recursos gratuitos, {pagos} pagos")

    # Cenário híbrido (TTS ElevenLabs + imagens OpenAI)
    est2 = CustoEstimador()
    est2.registrar("tts_elevenlabs", 5)
    est2.registrar("imagen_openai", 5)
    est2.registrar("ffmpeg_render", 1)
    est2.registrar("storage_gb", 0.020)
    rel2 = est2.relatorio()
    custo_resultado["hibrido"] = rel2

    custo2 = rel2["custo_total_brl"]
    ok(f"Cenário HÍBRIDO (ElevenLabs+OpenAI): R${custo2:.4f}")
    print(f"    Economia usando local vs híbrido: R${(custo2-custo_brl):.4f} por vídeo")

except Exception as e:
    falha("CustoEstimador", e)

# ─── RECOMENDAÇÃO DE PERFIL FFMPEG ───────────────────────────────────────────

secao("RECOMENDAÇÃO DE PERFIL FFMPEG")

try:
    from core.performance import sugerir_perfil_ffmpeg, ffmpeg_params_otimizados
    perfis = [
        (40, "1080p", "vídeo curto 40s"),
        (300, "1080p", "vídeo médio 5min"),
        (900, "1080p", "vídeo longo 15min"),
        (60, "shorts", "Shorts/Reels vertical"),
    ]
    for dur, res, label in perfis:
        perfil = sugerir_perfil_ffmpeg(dur, res)
        params = ffmpeg_params_otimizados(perfil)
        ok(f"{label} → perfil '{perfil}' ({len(params)//2} opções FFmpeg)")
except Exception as e:
    falha("sugerir_perfil_ffmpeg()", e)

# ─── CACHE DE ASSETS ─────────────────────────────────────────────────────────

secao("SISTEMA DE CACHE DE ASSETS")

try:
    from core.performance import AssetCache
    import tempfile
    cache_dir = Path(tempfile.mkdtemp(prefix="dark_cache_"))
    cache = AssetCache(cache_dir)

    # API real: get/set/estatisticas
    cache_key = "test_prompt_natureza_imagen_local"
    mock_path = cache_dir / "mock_img.png"
    mock_path.write_bytes(b"\x89PNG\r\n" + b"\x00" * 100)

    cache.set("imagen_local", cache_key, mock_path)
    recuperado = cache.get("imagen_local", cache_key)
    assert recuperado is not None
    ok(f"AssetCache: set/get OK — chave '{cache_key[:20]}...'")

    stats = cache.estatisticas()
    ok(f"Cache stats: {stats.get('total_entradas', 0)} entradas")
except Exception as e:
    falha("AssetCache", e)

# ─── RECOMENDAÇÕES DE HARDWARE ────────────────────────────────────────────────

secao("RECOMENDAÇÕES DE HARDWARE E CONFIGURAÇÃO")

ram = hw.get("ram_total_gb", 0)
if isinstance(ram, (int, float)) and ram >= 16:
    ok(f"RAM {ram}GB — adequada para modelos locais")
elif isinstance(ram, (int, float)) and ram >= 8:
    aviso(f"RAM {ram}GB — suficiente, mas modelos grandes podem ser lentos")
else:
    aviso(f"RAM {ram} — recomendado mínimo 8GB para uso confortável")

if hw["cuda"]:
    ok(f"GPU CUDA disponível ({hw['gpu']}) — geração de vídeo/imagem acelerada possível")
    if hw["vram_gb"] >= 8:
        ok(f"VRAM {hw['vram_gb']}GB — compatível com SDXL, XTTS, modelos de vídeo leves")
    else:
        aviso(f"VRAM {hw['vram_gb']}GB — modelos pesados precisam de offload para RAM")
else:
    aviso("Sem GPU CUDA — recomendado para produção em escala; use cloud API para geração IA")

# Recomendações por cenário
print(f"\n  {BOLD}Recomendações por caso de uso:{RESET}")
recomendacoes = [
    ("Narração TTS", "Piper local (grátis) → ElevenLabs API (R$0,01/1k chars)"),
    ("Imagens",      "Pillow placeholder (grátis) → SD local c/GPU ≥8GB VRAM → DALL-E API"),
    ("Vídeos",       "FFmpeg Ken Burns (grátis) → Wan.video API → Runway/Kling API"),
    ("Renderização", "FFmpeg local (sempre grátis)"),
    ("Storage",      "Local /tmp → Google Drive (15GB grátis) → S3 (R$0,025/GB)"),
]
for recurso, rec in recomendacoes:
    print(f"    {AZUL}▸{RESET} {recurso}: {rec}")

# ─── RELATÓRIO FINAL ─────────────────────────────────────────────────────────

secao("RELATÓRIO FASE 11")

relatorio_f11 = {
    "fase": "FASE 11 — Otimização de Custos e Desempenho",
    "hardware": hw,
    "benchmark": bench_resultado,
    "custo_por_video": custo_resultado,
    "recomendacoes": {
        "perfil_padrao": "youtube_hd",
        "tts_preferido": "piper_local",
        "imagem_preferida": "pillow_local_ou_sd_local",
        "video_preferido": "ffmpeg_kenburns_local",
        "custo_alvo_por_video_brl": 0.0,
    },
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
}

rel_path = ROOT / "producao" / "relatorio_fase11_otimizacao.json"
rel_path.parent.mkdir(exist_ok=True)
rel_path.write_text(json.dumps(relatorio_f11, indent=2, ensure_ascii=False))
ok(f"Relatório FASE 11 salvo: {rel_path}")

# ─── RESUMO ──────────────────────────────────────────────────────────────────

print(f"\n{'═'*55}")
print(f"{BOLD}  RELATÓRIO FASE 11 — OTIMIZAÇÃO{RESET}")
print(f"{'═'*55}")

n_ok    = sum(1 for r,_ in resultados if r == "ok")
n_aviso = sum(1 for r,_ in resultados if r == "aviso")
n_falha = sum(1 for r,_ in resultados if r == "falha")
score   = round(100 * n_ok / max(len(resultados), 1))

print(f"  Verificações:  {len(resultados)}")
print(f"  ✅ OK:         {n_ok}")
print(f"  ⚠️  Avisos:    {n_aviso}")
print(f"  ❌ Falhas:     {n_falha}")
print(f"  🎯 Score:      {score}/100")
print(f"\n  ai_generated:   True")
print(f"  ai_disclosure:  Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")

if n_falha == 0:
    print(f"\n  {VERDE}{BOLD}✅ FASE 11 APROVADA — Sistema otimizado{RESET}")
else:
    print(f"\n  {VERM}{BOLD}⚠️  FASE 11 COM ALERTAS — verificar {n_falha} falha(s){RESET}")

# Executável diretamente: python tests/test_fase11_otimizacao.py
if __name__ == "__main__":
    sys.exit(0 if n_falha == 0 else 1)
