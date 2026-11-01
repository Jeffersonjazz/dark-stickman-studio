#!/usr/bin/env python3
"""
AGENTE AUDIO MASTER — DARK STUDIO AAA
V003 — A IA Que Previu Sua Morte
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys, re, json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CENAS_NARRACAO = {
    "C01_hook": "Em 2019, um hospital programou uma inteligência artificial para prever quais pacientes morreriam nas próximas 24 horas. Ela acertou 90% das vezes. Mas a pergunta que ninguém conseguia responder era: o que fazer com essa informação?",
    "C02_como_funciona": "A IA hospitalar funciona como um sistema de reconhecimento de padrões em tempo real. Ela analisa simultaneamente centenas de variáveis: pressão arterial, frequência cardíaca, níveis de oxigênio, resultados de exames, histórico médico, medicações administradas — e identifica combinações invisíveis ao olho humano que precedem o colapso.",
    "C03_estudo": "O estudo que mudou tudo foi publicado na Nature Medicine em 2019 por pesquisadores da Universidade da Califórnia. O sistema analisou registros de 216 mil pacientes ao longo de 10 anos. Resultado: a IA identificou deterioração clínica significativa com 24 a 48 horas de antecedência — antes de qualquer sintoma visível.",
    "C04_deepmind": "A DeepMind, divisão de IA do Google, foi além. Em 2020, desenvolveu um sistema capaz de prever insuficiência renal aguda até 48 horas antes dos exames convencionais detectarem qualquer anomalia. Em testes, o sistema teria prevenido 50% dos casos graves — se médicos tivessem agido com base em suas previsões.",
    "C05_dilema": "Mas aqui surge o dilema que a medicina nunca enfrentou. Se uma IA prevê que um paciente morrerá nas próximas 12 horas, com 90% de certeza — mas o paciente está consciente e aparentemente estável — você conta a ele? Você conta à família? Qual é a obrigação ética de um algoritmo?",
    "C06_china": "Na China, o governo implementou um sistema de score de saúde social que usa dados de wearables, histórico médico e comportamento para prever doenças e até expectativa de vida. O sistema é usado por seguradoras, empregadores e bancos. Se seu score de saúde for baixo, seu crédito pode ser negado.",
    "C07_brasil": "No Brasil, os hospitais Albert Einstein e Sírio-Libanês já utilizam sistemas de IA para triagem de risco. O Hospital das Clínicas de São Paulo testa algoritmos para predição de sepse — uma das principais causas de morte hospitalar. Estamos na transição — e a velocidade dessa mudança vai nos surpreender.",
    "C08_cta": "A pergunta que vai definir a medicina dos próximos 20 anos não é se a IA pode prever doenças melhor que médicos. Ela já pode. A pergunta é: quando uma máquina sabe quando você vai morrer — com que direito ela guarda esse segredo de você? Se esse vídeo abriu sua mente para algo novo, compartilhe. Até o próximo."
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
    print("🎙️  AUDIO MASTER — V003 TECNOLOGIA: IA MORTAL")
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

    relatorio = {"ai_generated": True, "video": "V003", "agente": "AUDIO MASTER",
                 "total_cenas": len(CENAS_NARRACAO), "sucessos": sucessos,
                 "score": f"{sucessos}/{len(CENAS_NARRACAO)}", "resultados": resultados}
    (OUTPUT_DIR / "relatorio_narracao.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"\n📊 {sucessos}/{len(CENAS_NARRACAO)} cenas geradas → {OUTPUT_DIR}")
    return relatorio

if __name__ == "__main__":
    main()
