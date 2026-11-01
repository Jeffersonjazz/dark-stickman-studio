#!/usr/bin/env python3
"""
AGENTE AUDIO MASTER — V005 — A Floresta Que Respira
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import re, json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CENAS_NARRACAO = {
    "C01_hook": "Em 1997, uma cientista canadense publicou uma descoberta que a maioria dos biólogos achou impossível. As árvores de uma floresta não apenas vivem lado a lado — elas se comunicam. Compartilham recursos. Cuidam umas das outras. E a rede que as conecta é mais complexa que o cérebro humano.",
    "C02_simard": "Suzanne Simard era pesquisadora florestal quando notou algo estranho: quando árvores de uma espécie eram removidas, árvores de outras espécies nas proximidades adoeciam — mesmo sem competição por luz ou água. Ela passou anos investigando o solo. O que encontrou foi uma rede subterrânea de fungos micorrizais que conectava as raízes de centenas de árvores.",
    "C03_rede": "A rede micelial funciona como um sistema nervoso subterrâneo. Árvores maiores, as árvores-mãe, enviam carbono e nutrientes para mudas menores que crescem à sua sombra. Mas vai além: quando uma árvore é atacada por insetos, ela emite compostos químicos pela rede que alertam outras árvores — que então produzem toxinas defensivas antes de serem atacadas.",
    "C04_mae": "As árvores-mãe — geralmente os indivíduos mais velhos e maiores da floresta — mantêm conexões com centenas de outras árvores simultaneamente. Estudos mostram que quando uma árvore-mãe está morrendo, ela deliberadamente aumenta o envio de carbono e sinais químicos para seus filhos — como se passasse um testamento biológico para a próxima geração.",
    "C05_sinais": "Em 2016, pesquisadores descobriram que a rede não é apenas de nutrição — é de comunicação ativa. Quando uma árvore sofre estresse hídrico, ela emite sinais elétricos pela rede micelial. Outras árvores, a metros de distância, fecham seus estômatos em resposta — conservando água antes de precisar.",
    "C06_implicacoes": "Simard hoje afirma que a floresta funciona como um organismo único — não uma coleção de indivíduos competindo por recursos, mas uma comunidade que evolui em cooperação. Essa descoberta está mudando como gerenciamos florestas: remover árvores-mãe idosas, como se fazia em manejo florestal convencional, pode colapsar a rede inteira.",
    "C07_tempo": "A floresta que parece silenciosa está em constante conversa. E essa conversa começou muito antes dos humanos. Os fungos micorrizais existem há 450 milhões de anos — eles ajudaram as primeiras plantas a colonizar a terra. Somos jovens demais para entender completamente o que estamos destruindo.",
    "CTA": "A próxima vez que você estiver numa floresta, lembre: você está caminhando sobre uma internet que tem 450 milhões de anos. E ela está conversando. Se esse vídeo abriu seus olhos para a inteligência da natureza, compartilhe. Até o próximo."
}

def gerar_com_edge_tts(texto, arquivo_saida):
    try:
        import asyncio, edge_tts
        async def _gerar():
            communicate = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural", rate="-10%", pitch="-3Hz")
            await communicate.save(arquivo_saida)
        asyncio.run(_gerar())
        return True
    except Exception as e:
        print(f"  ⚠️ edge_tts: {e}")
        return False

def gerar_com_gtts(texto, arquivo_saida):
    try:
        from gtts import gTTS
        gTTS(text=texto, lang='pt', slow=False).save(arquivo_saida)
        return True
    except Exception as e:
        print(f"  ⚠️ gTTS: {e}")
        return False

def processar_texto(texto):
    texto = re.sub(r'\[.*?\]', '', texto)
    return ' '.join(texto.split()).strip()

def main():
    print("=" * 60)
    print("🎙️  AUDIO MASTER — V005 NATUREZA: FLORESTA")
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

    relatorio = {"ai_generated": True, "video": "V005", "sucessos": sucessos,
                 "score": f"{sucessos}/{len(CENAS_NARRACAO)}", "resultados": resultados}
    (OUTPUT_DIR / "relatorio_narracao.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"\n📊 {sucessos}/{len(CENAS_NARRACAO)} cenas → {OUTPUT_DIR}")
    return relatorio

if __name__ == "__main__":
    main()
