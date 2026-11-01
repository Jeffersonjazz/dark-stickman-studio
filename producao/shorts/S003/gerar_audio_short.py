#!/usr/bin/env python3
"""AUDIO MASTER TTS — SHORT S003 — Dark Tech
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA
"""
import asyncio, sys, json
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

NARRACAO = """Uma IA previu a morte de pacientes com 90% de precisão.

O algoritmo do DeepMind analisou 700 mil registros médicos. Identificou insuficiência renal antes dos médicos. Salvou vidas — mas também levantou uma questão perturbadora: você quer saber quando vai morrer? A tecnologia já pode te dizer. A pergunta é: você está pronto para ouvir?

Comenta: você deixaria a IA decidir seu tratamento?"""

VOICE    = "pt-BR-AntonioNeural"
RATE     = "-4%"
PITCH    = "-2Hz"

async def gerar_edge_tts():
    try:
        import edge_tts
        out = AUDIO_DIR / "S003_short_narracao.mp3"
        communicate = edge_tts.Communicate(NARRACAO, VOICE, rate=RATE, pitch=PITCH)
        await communicate.save(str(out))
        size = out.stat().st_size / 1024
        print(f"✅ edge_tts → {out.name} ({size:.0f} KB)")
        return True
    except Exception as e:
        print(f"⚠️ edge_tts falhou: {e}")
        return False

def gerar_gtts():
    try:
        from gtts import gTTS
        out = AUDIO_DIR / "S003_short_narracao.mp3"
        gTTS(NARRACAO, lang="pt", slow=False).save(str(out))
        print(f"✅ gTTS → {out.name}")
        return True
    except Exception as e:
        print(f"⚠️ gTTS falhou: {e}")
        return False

def fallback_txt():
    para_gravar = AUDIO_DIR / "S003_short_para_gravar.txt"
    para_gravar.write_text(NARRACAO, encoding="utf-8")
    print(f"📝 Fallback → {para_gravar.name} (grave no Audacity ou ElevenLabs)")
    return True

def salvar_relatorio(metodo):
    rel = {
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "short_id": "S003",
        "canal": "Dark Tech",
        "voice": VOICE, "rate": RATE, "pitch": PITCH,
        "metodo_tts": metodo,
        "duracao_alvo_s": 55,
        "palavras": 63,
    }
    (AUDIO_DIR / "relatorio_audio_short.json").write_text(
        json.dumps(rel, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    print(f"🎙️  AUDIO MASTER → SHORT S003 — Dark Tech")
    if asyncio.run(gerar_edge_tts()):
        salvar_relatorio("edge_tts")
    elif gerar_gtts():
        salvar_relatorio("gtts")
    else:
        fallback_txt()
        salvar_relatorio("txt_fallback")
    print("✅ AUDIO MASTER concluído")
