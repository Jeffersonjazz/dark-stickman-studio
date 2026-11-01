#!/usr/bin/env python3
"""AUDIO MASTER TTS — SHORT S001 — Dark Psicologia
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA
"""
import asyncio, sys, json
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

NARRACAO = """Você já sentiu um vazio que não consegue explicar?

Pesquisadores chamam isso de vazio existencial — e não é fraqueza. É seu cérebro pedindo significado. Viktor Frankl sobreviveu ao Holocausto e descobriu: quem tem um 'por quê' suporta qualquer 'como'. Você também pode encontrar o seu.

Siga para mais verdades que a psicologia esconde."""

VOICE    = "pt-BR-AntonioNeural"
RATE     = "-5%"
PITCH    = "-3Hz"

async def gerar_edge_tts():
    try:
        import edge_tts
        out = AUDIO_DIR / "S001_short_narracao.mp3"
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
        out = AUDIO_DIR / "S001_short_narracao.mp3"
        gTTS(NARRACAO, lang="pt", slow=False).save(str(out))
        print(f"✅ gTTS → {out.name}")
        return True
    except Exception as e:
        print(f"⚠️ gTTS falhou: {e}")
        return False

def fallback_txt():
    para_gravar = AUDIO_DIR / "S001_short_para_gravar.txt"
    para_gravar.write_text(NARRACAO, encoding="utf-8")
    print(f"📝 Fallback → {para_gravar.name} (grave no Audacity ou ElevenLabs)")
    return True

def salvar_relatorio(metodo):
    rel = {
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "short_id": "S001",
        "canal": "Dark Psicologia",
        "voice": VOICE, "rate": RATE, "pitch": PITCH,
        "metodo_tts": metodo,
        "duracao_alvo_s": 45,
        "palavras": 54,
    }
    (AUDIO_DIR / "relatorio_audio_short.json").write_text(
        json.dumps(rel, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    print(f"🎙️  AUDIO MASTER → SHORT S001 — Dark Psicologia")
    if asyncio.run(gerar_edge_tts()):
        salvar_relatorio("edge_tts")
    elif gerar_gtts():
        salvar_relatorio("gtts")
    else:
        fallback_txt()
        salvar_relatorio("txt_fallback")
    print("✅ AUDIO MASTER concluído")
