#!/usr/bin/env python3
"""AUDIO MASTER TTS — SHORT S005 — Dark Natureza
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA
"""
import asyncio, sys, json
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

NARRACAO = """Enquanto você assiste isso, florestas inteiras estão se comunicando.

Em 1997, Suzanne Simard descobriu que árvores compartilham nutrientes por redes de fungos. A 'internet das florestas'. Árvores-mãe alimentam as pequenas. Árvores moribundas transmitem recursos aos vizinhos. A floresta não é uma coleção de indivíduos. É um organismo.

Isso mudou como você vê uma floresta? 🌿"""

VOICE    = "pt-BR-AntonioNeural"
RATE     = "-8%"
PITCH    = "-2Hz"

async def gerar_edge_tts():
    try:
        import edge_tts
        out = AUDIO_DIR / "S005_short_narracao.mp3"
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
        out = AUDIO_DIR / "S005_short_narracao.mp3"
        gTTS(NARRACAO, lang="pt", slow=False).save(str(out))
        print(f"✅ gTTS → {out.name}")
        return True
    except Exception as e:
        print(f"⚠️ gTTS falhou: {e}")
        return False

def fallback_txt():
    para_gravar = AUDIO_DIR / "S005_short_para_gravar.txt"
    para_gravar.write_text(NARRACAO, encoding="utf-8")
    print(f"📝 Fallback → {para_gravar.name} (grave no Audacity ou ElevenLabs)")
    return True

def salvar_relatorio(metodo):
    rel = {
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "short_id": "S005",
        "canal": "Dark Natureza",
        "voice": VOICE, "rate": RATE, "pitch": PITCH,
        "metodo_tts": metodo,
        "duracao_alvo_s": 55,
        "palavras": 55,
    }
    (AUDIO_DIR / "relatorio_audio_short.json").write_text(
        json.dumps(rel, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    print(f"🎙️  AUDIO MASTER → SHORT S005 — Dark Natureza")
    if asyncio.run(gerar_edge_tts()):
        salvar_relatorio("edge_tts")
    elif gerar_gtts():
        salvar_relatorio("gtts")
    else:
        fallback_txt()
        salvar_relatorio("txt_fallback")
    print("✅ AUDIO MASTER concluído")
