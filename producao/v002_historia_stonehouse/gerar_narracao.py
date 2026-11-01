#!/usr/bin/env python3
"""
AGENTE AUDIO MASTER — DARK STUDIO AAA
V002 — O Homem Que Fingiu Ser Morto Por 35 Anos
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys, os, re, json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CENAS_NARRACAO = {
    "C01_hook": "Em novembro de 1974, um homem deixou suas roupas numa praia em Miami e desapareceu. O mundo inteiro acreditou que ele tinha se afogado. Mas John Stonehouse estava vivo — e havia planejado cada detalhe da sua própria morte.",
    "C02_perfil": "John Stonehouse era membro do Parlamento britânico. Ministro do governo Wilson. Um homem de poder, influência e aparente sucesso. Mas por trás da fachada impecável, havia dívidas, uma amante, investigações que se aproximavam — e uma psique à beira do colapso.",
    "C03_dissociacao": "A psicologia tem nome para o que Stonehouse fez: fuga dissociativa. Em situações de pressão extrema, o cérebro pode criar uma nova identidade como mecanismo de defesa. Ele passou meses preparando documentos falsos, contas bancárias no exterior, e uma nova vida. Uma nova pessoa.",
    "C04_fuga": "No dia 20 de novembro de 1974, Stonehouse voou para Miami, deixou suas roupas na praia, e embarcou num avião para a Austrália sob identidade falsa. A polícia britânica concluiu: afogamento acidental. A imprensa publicou necrológios. A família chorou.",
    "C05_captura": "Seis semanas depois, a polícia australiana, investigando uma fraude diferente, encontrou um homem usando identidade falsa em Melbourne. Era Stonehouse. A descoberta virou escândalo internacional. Ele foi extraditado, julgado, e condenado a 7 anos de prisão.",
    "C06_casos": "O caso Stonehouse não foi único. Em 1987, Ken Kesey desapareceu fingindo suicídio no México. Em 2002, John Darwin, um professor britânico, passou 5 anos morto para sua própria família enquanto vivia numa casa ao lado. A psicologia chama esses casos de pseudocídio — e eles são mais comuns do que imaginamos.",
    "C07_psicologia": "O que leva um ser humano a apagar a própria existência? Segundo a psiquiatra Elizabeth Howell, especialista em dissociação, a resposta está em pressão insustentável combinada com a incapacidade de pedir ajuda. A fuga não é fraqueza — é um sistema de emergência que o cérebro ativa quando não vê outra saída.",
    "CTA": "A história de John Stonehouse é um lembrete de que as pressões invisíveis podem ser as mais destrutivas. Se você conhece alguém sob pressão extrema, às vezes a coisa mais importante é simplesmente perguntar: como você está de verdade? Se esse vídeo te fez pensar, compartilhe. Até o próximo."
}

def gerar_com_edge_tts(texto, arquivo_saida):
    try:
        import asyncio, edge_tts
        async def _gerar():
            communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural", rate="-8%", pitch="-5Hz")
            await communicate.save(arquivo_saida)
        asyncio.run(_gerar())
        return True
    except Exception as e:
        print(f"  ⚠️ edge_tts falhou: {e}")
        return False

def gerar_com_gtts(texto, arquivo_saida):
    try:
        from gtts import gTTS
        gTTS(text=texto, lang='pt', slow=False).save(arquivo_saida)
        return True
    except Exception as e:
        print(f"  ⚠️ gTTS falhou: {e}")
        return False

def processar_texto(texto):
    texto = re.sub(r'\[PAUSA \d+(\.\d+)?s\]', '', texto)
    texto = re.sub(r'\[.*?\]', '', texto)
    return ' '.join(texto.split()).strip()

def main():
    print("=" * 60)
    print("🎙️  AUDIO MASTER — V002 HISTÓRIA: STONEHOUSE")
    print("=" * 60)
    resultados = {}
    sucessos = 0
    for cena_id, texto_original in CENAS_NARRACAO.items():
        print(f"\n📢 {cena_id}")
        texto = processar_texto(texto_original)
        arquivo_mp3 = str(OUTPUT_DIR / f"{cena_id}.mp3")
        if gerar_com_edge_tts(texto, arquivo_mp3):
            print(f"   ✅ edge_tts → {Path(arquivo_mp3).name}")
            resultados[cena_id] = {"arquivo": arquivo_mp3, "engine": "edge_tts", "status": "ok"}
            sucessos += 1
        elif gerar_com_gtts(texto, arquivo_mp3):
            print(f"   ✅ gTTS → {Path(arquivo_mp3).name}")
            resultados[cena_id] = {"arquivo": arquivo_mp3, "engine": "gtts", "status": "ok"}
            sucessos += 1
        else:
            txt_path = str(OUTPUT_DIR / f"{cena_id}_para_gravar.txt")
            Path(txt_path).write_text(texto, encoding='utf-8')
            resultados[cena_id] = {"arquivo": txt_path, "engine": "manual", "status": "pendente"}

    relatorio = {"ai_generated": True, "video": "V002", "agente": "AUDIO MASTER",
                 "total_cenas": len(CENAS_NARRACAO), "sucessos": sucessos,
                 "score": f"{sucessos}/{len(CENAS_NARRACAO)}", "resultados": resultados}
    (OUTPUT_DIR / "relatorio_narracao.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"\n📊 {sucessos}/{len(CENAS_NARRACAO)} cenas geradas → {OUTPUT_DIR}")
    return relatorio

if __name__ == "__main__":
    main()
