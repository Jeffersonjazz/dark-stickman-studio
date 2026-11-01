#!/usr/bin/env python3
"""
FASE 11 — Relatório de Otimização de Custos e Backends
DARK STUDIO AAA — DARK CREATIVE LAB

Analisa cada etapa do pipeline e gera:
- Matriz custo × qualidade por módulo
- Recomendação de backend por orçamento
- Custo estimado mensal por canal (12 canais × meta de vídeos/dia)
- Estratégia de escalonamento gratuito → pago

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ─── Constantes ──────────────────────────────────────────────────────────────

VERDE  = "\033[92m"
AMAR   = "\033[93m"
AZUL   = "\033[94m"
CIANO  = "\033[96m"
VERM   = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

# Meta de produção: 2 vídeos/dia × 12 canais × 30 dias = 720 vídeos/mês
VIDEOS_DIA     = 2
N_CANAIS       = 12
DIAS_MES       = 30
VIDEOS_MES     = VIDEOS_DIA * N_CANAIS * DIAS_MES  # 720

# Duração média por vídeo (segundos)
DURACAO_MEDIA_S = 240  # 4 minutos

# ─── Matriz de backends por módulo ───────────────────────────────────────────

MATRIZ_BACKENDS = {
    "TTS — Síntese de Voz": {
        "backends": [
            {
                "nome": "Kokoro (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 8,
                "velocidade": "média (CPU)",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "pip install kokoro",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
            {
                "nome": "Piper TTS (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 7,
                "velocidade": "rápida (CPU)",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "pip install piper-tts",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
            {
                "nome": "Edge TTS (Microsoft nuvem)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 8,
                "velocidade": "rápida (nuvem)",
                "disponibilidade": "requer internet",
                "limite": "informal — sem cota publicada",
                "instalacao": "pip install edge-tts",
                "status": "✅ ativo (fallback 3)",
                "tier": "GRATUITO (informal)",
            },
            {
                "nome": "HF MMS-TTS (Hugging Face API)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 6,
                "velocidade": "lenta (fila HF)",
                "disponibilidade": "requer internet",
                "limite": "fila gratuita HF",
                "instalacao": "requests",
                "status": "✅ ativo (fallback 4)",
                "tier": "GRATUITO",
            },
            {
                "nome": "gTTS (Google TTS)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 5,
                "velocidade": "rápida",
                "disponibilidade": "requer internet",
                "limite": "informal",
                "instalacao": "pip install gtts",
                "status": "✅ ativo (fallback 5)",
                "tier": "GRATUITO (informal)",
            },
            {
                "nome": "ElevenLabs",
                "custo_por_video": 0.12,
                "custo_mensal": 0.12 * VIDEOS_MES,
                "qualidade": 10,
                "velocidade": "rápida (nuvem)",
                "disponibilidade": "requer API key",
                "limite": "por plano",
                "instalacao": "pip install elevenlabs",
                "status": "⚙️  opcional (premium)",
                "tier": "PAGO",
            },
        ],
        "recomendacao": "Kokoro → Piper → Edge TTS (cascade atual — custo R$0,00)",
        "custo_atual_mensal": 0.00,
    },

    "Geração de Imagens": {
        "backends": [
            {
                "nome": "Pillow (gradiente local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 3,
                "velocidade": "instantânea",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "pip install Pillow",
                "status": "✅ ativo (fallback padrão)",
                "tier": "GRATUITO",
            },
            {
                "nome": "Stable Diffusion local (AUTOMATIC1111 / ComfyUI)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 8,
                "velocidade": "lenta sem GPU / rápida com GPU",
                "disponibilidade": "requer GPU 6GB+ VRAM",
                "limite": "ilimitado",
                "instalacao": "AUTOMATIC1111 ou ComfyUI",
                "status": "⚙️  recomendado (com GPU)",
                "tier": "GRATUITO (hardware próprio)",
            },
            {
                "nome": "HF Inference API (FLUX/SDXL gratuito)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 7,
                "velocidade": "lenta (fila)",
                "disponibilidade": "requer internet",
                "limite": "cota HF gratuita",
                "instalacao": "requests + token HF",
                "status": "⚙️  integrar (próxima fase)",
                "tier": "GRATUITO",
            },
            {
                "nome": "Replicate (FLUX Schnell)",
                "custo_por_video": 0.003,
                "custo_mensal": 0.003 * VIDEOS_MES * 5,  # 5 imagens/vídeo
                "qualidade": 9,
                "velocidade": "rápida (nuvem GPU)",
                "disponibilidade": "requer API key",
                "limite": "por crédito",
                "instalacao": "pip install replicate",
                "status": "⚙️  opcional (baixo custo)",
                "tier": "PAGO (baixo custo)",
            },
            {
                "nome": "DALL-E 3 (OpenAI)",
                "custo_por_video": 0.24,
                "custo_mensal": 0.24 * VIDEOS_MES,
                "qualidade": 10,
                "velocidade": "rápida",
                "disponibilidade": "requer API key",
                "limite": "por crédito",
                "instalacao": "pip install openai",
                "status": "⚙️  opcional (premium)",
                "tier": "PAGO",
            },
        ],
        "recomendacao": "Pillow (atual) → SD local com GPU → HF Inference → Replicate",
        "custo_atual_mensal": 0.00,
    },

    "Animação de Vídeo (Ken Burns / Zoompan)": {
        "backends": [
            {
                "nome": "FFmpeg zoompan (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 7,
                "velocidade": "média (CPU) / rápida (GPU nvenc)",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "apt install ffmpeg",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
            {
                "nome": "MoviePy (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 6,
                "velocidade": "lenta (Python)",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "pip install moviepy",
                "status": "✅ fallback",
                "tier": "GRATUITO",
            },
            {
                "nome": "Runway Gen-3 / Kling AI",
                "custo_por_video": 0.50,
                "custo_mensal": 0.50 * VIDEOS_MES,
                "qualidade": 10,
                "velocidade": "média (nuvem)",
                "disponibilidade": "requer créditos",
                "limite": "por crédito",
                "instalacao": "API REST",
                "status": "⚙️  para vídeos premium",
                "tier": "PAGO",
            },
        ],
        "recomendacao": "FFmpeg zoompan (atual) — qualidade suficiente para YouTube documentário",
        "custo_atual_mensal": 0.00,
    },

    "Edição e Montagem": {
        "backends": [
            {
                "nome": "FFmpeg concat (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 9,
                "velocidade": "rápida",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "apt install ffmpeg",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
        ],
        "recomendacao": "FFmpeg concat — padrão da indústria, gratuito e robusto",
        "custo_atual_mensal": 0.00,
    },

    "Geração de Legendas": {
        "backends": [
            {
                "nome": "SRT local (timecodes das cenas)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 8,
                "velocidade": "instantânea",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "built-in",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
            {
                "nome": "OpenAI Whisper (local STT → SRT)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 10,
                "velocidade": "lenta (whisper-large) / rápida (whisper-tiny)",
                "disponibilidade": "sempre (após download)",
                "limite": "ilimitado",
                "instalacao": "pip install openai-whisper",
                "status": "⚙️  integrar para vídeos com áudio real",
                "tier": "GRATUITO",
            },
        ],
        "recomendacao": "SRT por timecodes (atual) + Whisper local para revisão de sincronismo",
        "custo_atual_mensal": 0.00,
    },

    "Thumbnail e Capa": {
        "backends": [
            {
                "nome": "Pillow (local)",
                "custo_por_video": 0.00,
                "custo_mensal": 0.00,
                "qualidade": 7,
                "velocidade": "instantânea",
                "disponibilidade": "sempre",
                "limite": "ilimitado",
                "instalacao": "pip install Pillow",
                "status": "✅ ativo",
                "tier": "GRATUITO",
            },
        ],
        "recomendacao": "Pillow local com templates por nicho — R$0,00/mês",
        "custo_atual_mensal": 0.00,
    },
}

# ─── Cálculo de custo mensal ──────────────────────────────────────────────────

def calcular_custo_total():
    total = sum(m["custo_atual_mensal"] for m in MATRIZ_BACKENDS.values())
    return total

def custo_escalonado():
    """Projeção de custo em 3 cenários: gratuito, híbrido, premium."""
    return {
        "gratuito": {
            "descricao": "Stack atual — 100% gratuito/local",
            "tts": "Kokoro → Piper → Edge TTS",
            "imagens": "Pillow gradiente",
            "video": "FFmpeg zoompan",
            "custo_por_video": 0.00,
            "custo_mensal": 0.00,
            "qualidade_estimada": "6–7/10",
            "recomendado_para": "início / todos os canais",
        },
        "hibrido": {
            "descricao": "Imagens via HF Inference (FLUX gratuito) + TTS local",
            "tts": "Kokoro local",
            "imagens": "HF FLUX Schnell (gratuito) → Pillow fallback",
            "video": "FFmpeg zoompan",
            "custo_por_video": 0.00,
            "custo_mensal": 0.00,
            "qualidade_estimada": "8/10",
            "recomendado_para": "canais em crescimento (>1k subs)",
        },
        "premium": {
            "descricao": "Replicate FLUX + ElevenLabs TTS",
            "tts": "ElevenLabs (R$0,12/vídeo)",
            "imagens": "Replicate FLUX Schnell (R$0,015/vídeo × 5 img)",
            "video": "FFmpeg zoompan",
            "custo_por_video": 0.12 + 0.015,
            "custo_mensal": (0.12 + 0.015) * VIDEOS_MES,
            "qualidade_estimada": "9–10/10",
            "recomendado_para": "canais monetizados (>10k subs)",
        },
    }

# ─── Verificar o que está instalado ──────────────────────────────────────────

def checar_dependencias():
    deps = {
        "ffmpeg":    shutil.which("ffmpeg") is not None,
        "ffprobe":   shutil.which("ffprobe") is not None,
        "python":    True,
        "pillow":    False,
        "edge_tts":  False,
        "gtts":      False,
        "kokoro":    False,
        "piper":     False,
        "whisper":   False,
        "replicate": False,
        "openai":    False,
    }
    try:
        import PIL; deps["pillow"] = True
    except ImportError: pass
    try:
        import edge_tts; deps["edge_tts"] = True
    except ImportError: pass
    try:
        import gtts; deps["gtts"] = True
    except ImportError: pass
    try:
        import kokoro; deps["kokoro"] = True
    except ImportError: pass
    try:
        import whisper; deps["whisper"] = True
    except ImportError: pass
    try:
        import replicate; deps["replicate"] = True
    except ImportError: pass
    try:
        import openai; deps["openai"] = True
    except ImportError: pass
    return deps

# ─── Exibir relatório ────────────────────────────────────────────────────────

def imprimir_relatorio():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    custo_atual = calcular_custo_total()
    cenarios = custo_escalonado()
    deps = checar_dependencias()

    print(f"\n{'═'*65}")
    print(f"{BOLD}{AZUL}  FASE 11 — RELATÓRIO DE OTIMIZAÇÃO DE CUSTOS{RESET}")
    print(f"  DARK STUDIO AAA — DARK CREATIVE LAB    {now}")
    print(f"{'═'*65}")

    print(f"\n{BOLD}📊 META DE PRODUÇÃO{RESET}")
    print(f"  {N_CANAIS} canais × {VIDEOS_DIA} vídeos/dia × {DIAS_MES} dias = {VIDEOS_MES} vídeos/mês")
    print(f"  Duração média: {DURACAO_MEDIA_S//60} minutos por vídeo")

    print(f"\n{BOLD}🔧 DEPENDÊNCIAS INSTALADAS{RESET}")
    for dep, ok in deps.items():
        ico = f"{VERDE}✅{RESET}" if ok else f"{AMAR}⬜{RESET}"
        print(f"  {ico} {dep}")

    print(f"\n{BOLD}💰 MATRIZ CUSTO × QUALIDADE POR MÓDULO{RESET}")
    print(f"  {'Módulo':<35} {'Custo/mês':>12}  {'Recomendação'}")
    print(f"  {'─'*35} {'─'*12}  {'─'*30}")

    for modulo, dados in MATRIZ_BACKENDS.items():
        custo = dados["custo_atual_mensal"]
        cor = VERDE if custo == 0 else AMAR
        print(f"  {modulo:<35} {cor}R$ {custo:>8.2f}{RESET}  {dados['recomendacao'][:45]}")

        # Top 3 opções gratuitas
        gratuitos = [b for b in dados["backends"] if b["tier"] == "GRATUITO"]
        pagos     = [b for b in dados["backends"] if b["tier"] != "GRATUITO"]
        for b in gratuitos[:2]:
            print(f"    {VERDE}○{RESET} {b['nome']:<30} qualidade {b['qualidade']}/10  {b['status']}")
        for b in pagos[:1]:
            print(f"    {AMAR}◌{RESET} {b['nome']:<30} qualidade {b['qualidade']}/10  {b['status']}")

    print(f"\n{BOLD}🎯 CUSTO TOTAL ATUAL: {VERDE}R$ {custo_atual:.2f}/mês{RESET}")
    print(f"  {VERDE}{BOLD}→ Stack 100% gratuita — R$0,00 para {VIDEOS_MES} vídeos/mês{RESET}")

    print(f"\n{BOLD}📈 PROJEÇÃO POR CENÁRIO{RESET}")
    print(f"  {'Cenário':<12} {'Custo/vídeo':>13}  {'Custo/mês':>12}  {'Qualidade':>10}  Quando usar")
    print(f"  {'─'*12} {'─'*13}  {'─'*12}  {'─'*10}  {'─'*25}")
    for nome, c in cenarios.items():
        cor = VERDE if c["custo_mensal"] == 0 else AMAR if c["custo_mensal"] < 200 else VERM
        print(f"  {nome:<12} {cor}R$ {c['custo_por_video']:>10.3f}{RESET}  {cor}R$ {c['custo_mensal']:>9.2f}{RESET}  {c['qualidade_estimada']:>10}  {c['recomendado_para']}")

    print(f"\n{BOLD}🗺️  ROADMAP DE UPGRADE{RESET}")
    etapas = [
        ("Fase atual",    "0–1k subs",   "Stack 100% gratuita — Pillow + FFmpeg + Edge TTS",     "R$ 0,00/mês"),
        ("Upgrade 1",     "1k–10k subs", "Integrar HF FLUX Schnell (gratuito) para imagens",     "R$ 0,00/mês"),
        ("Upgrade 2",     "10k–100k",    "ElevenLabs TTS (qualidade 10/10) nos canais top",       f"R$ {0.12 * 60:.0f}–{0.12 * VIDEOS_MES:.0f}/mês"),
        ("Upgrade 3",     ">100k subs",  "GPU própria (RTX 4090) — SD local + kokoro premium",    "R$ 0,00/mês após hardware"),
        ("Monetizado",    ">$10/dia",    "Replicate FLUX + ElevenLabs — qualidade máxima",        f"R$ {(0.12 + 0.015) * VIDEOS_MES:.0f}/mês"),
    ]
    for etapa, subs, descricao, custo in etapas:
        print(f"  {CIANO}{etapa:<14}{RESET} [{subs:<12}] {descricao[:48]:<48}  {custo}")

    print(f"\n{BOLD}⚡ PRÓXIMAS OTIMIZAÇÕES RECOMENDADAS{RESET}")
    otimizacoes = [
        ("ALTO IMPACTO",  "Integrar HF FLUX Schnell gratuito → imagens realistas sem custo"),
        ("ALTO IMPACTO",  "Activar GPU nvenc no FFmpeg → 3× mais rápido na animação Ken Burns"),
        ("MÉDIO IMPACTO", "Whisper local (tiny) → melhor sincronismo de legendas"),
        ("MÉDIO IMPACTO", "Cache de thumbnails por nicho → evitar regerar imagens iguais"),
        ("BAIXO IMPACTO", "Batch de jobs por canal → paralelizar produção dos 12 canais"),
    ]
    for prioridade, desc in otimizacoes:
        cor = VERDE if "ALTO" in prioridade else AMAR if "MÉDIO" in prioridade else CIANO
        print(f"  {cor}[{prioridade}]{RESET} {desc}")

    print(f"\n{'─'*65}")
    print(f"  ai_generated:  True")
    print(f"  ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")
    print(f"{'═'*65}\n")

    return {
        "data": now,
        "videos_mes": VIDEOS_MES,
        "custo_atual_mensal": custo_atual,
        "cenarios": cenarios,
        "dependencias": deps,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

def salvar_relatorio(dados: dict, path: Path):
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2))
    print(f"  💾 Relatório JSON: {path}")

# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    dados = imprimir_relatorio()
    out = ROOT / "docs" / "custo_report.json"
    out.parent.mkdir(exist_ok=True)
    salvar_relatorio(dados, out)
