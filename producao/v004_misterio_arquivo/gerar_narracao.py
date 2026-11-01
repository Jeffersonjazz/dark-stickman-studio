#!/usr/bin/env python3
"""
AGENTE AUDIO MASTER — V004 — O Arquivo Que o Governo Apagou
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import re, json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CENAS_NARRACAO = {
    "C01_hook": "Em 2013, às 14 horas e 37 minutos de uma terça-feira, um arquivo de 847 páginas foi publicado acidentalmente no servidor público do Departamento de Justiça dos Estados Unidos. Em 4 horas, foi removido. Mas três pessoas já tinham feito cópias completas.",
    "C02_conteudo": "O documento era um relatório interno sobre operações de vigilância em massa realizadas entre 2001 e 2013. Não era o Programa PRISM — esse viria a público com Snowden no mesmo ano. Era algo diferente: detalhava acordos secretos com 23 corporações privadas para acesso irrestrito a dados de comunicação de cidadãos americanos.",
    "C03_vazamento": "As três pessoas que baixaram o arquivo permaneceram anônimas por semanas. Então, gradualmente, fragmentos começaram a aparecer em fóruns, blogs e publicações independentes — nunca o documento completo, sempre partes calculadas. Alguém estava controlando a revelação.",
    "C04_revelacoes": "O que as cópias revelaram mudou a percepção sobre privacidade digital. Três descobertas principais: primeiro, acordos de acesso a metadados com empresas de telefonia e internet firmados antes de qualquer autorização judicial conhecida. Segundo, operações de infiltração em fóruns privados de jornalistas. Terceiro, um programa de pontuação de risco social para cidadãos americanos — semelhante ao que a China formalizaria anos depois.",
    "C05_streisand": "Isso nos leva ao Paradoxo de Streisand: em 1994, Barbara Streisand processou um fotógrafo para remover uma foto de sua mansão da internet. Resultado? A foto, que tinha tido 6 visualizações, foi vista por 400 mil pessoas em um mês. Toda tentativa de apagar informação na era digital tende a amplificá-la.",
    "C06_historico": "Três casos históricos provam esse padrão: o Pentágono Papers, vazado pelo analista Daniel Ellsberg em 1971 — o governo Nixon obteve ordem judicial para suprimir. O New York Times publicou na mesma semana. Os Arquivos da CIA sobre Chile, publicados em 1998 — cada tentativa de redação criou mais interesse nas partes censuradas. E os E-mails do DNC em 2016 — a tentativa de suprimir criou o maior escândalo político do ano.",
    "C07_destinos": "Quanto às três pessoas que copiaram o documento original de 2013, o que aconteceu com elas? Uma identificada posteriormente era jornalista freelancer que assinou acordo de não divulgação. Uma segunda era pesquisadora acadêmica que recebeu visita de agentes federais e optou por não publicar. A terceira permanece desconhecida. Mas os fragmentos que ela liberou ainda circulam — e continuam sendo verificados.",
    "CTA": "A internet não esquece. E talvez seja exatamente isso que o poder mais teme. Se esse vídeo abriu seus olhos para algo, compartilhe — porque informação suprimida ainda quer ser livre. Até o próximo."
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
    print("🎙️  AUDIO MASTER — V004 MISTÉRIO: ARQUIVO SECRETO")
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

    relatorio = {"ai_generated": True, "video": "V004", "sucessos": sucessos,
                 "score": f"{sucessos}/{len(CENAS_NARRACAO)}", "resultados": resultados}
    (OUTPUT_DIR / "relatorio_narracao.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
    print(f"\n📊 {sucessos}/{len(CENAS_NARRACAO)} cenas → {OUTPUT_DIR}")
    return relatorio

if __name__ == "__main__":
    main()
