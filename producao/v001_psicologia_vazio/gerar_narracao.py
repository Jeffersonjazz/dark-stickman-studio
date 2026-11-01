#!/usr/bin/env python3
"""
AGENTE AUDIO MASTER — DARK STUDIO AAA
Gera narração TTS pt-BR para V001 usando pipeline de fallback:
piper → edge_tts → gtts
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys, os, re, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

OUTPUT_DIR = Path(__file__).parent / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Texto de narração por cena
CENAS_NARRACAO = {
    "C01_hook": "Você tem emprego. Tem família. Talvez até dinheiro. Mas existe um vazio que nenhuma conquista consegue preencher. Esse sentimento tem um nome na psicologia — e entender isso pode mudar completamente a forma como você vê sua vida.",
    "C02_frankl": "Em 1946, o psiquiatra Viktor Frankl sobreviveu a campos de concentração nazistas. O que ele descobriu lá dentro contradiz tudo que a sociedade moderna nos ensina sobre felicidade. Frankl percebeu que o ser humano não busca prazer — ele busca sentido. Essa é a diferença entre a felicidade que compramos e a felicidade que construímos. Ele chamou essa descoberta de logoterapia — do grego logos, que significa significado. E ela mudou para sempre a forma como entendemos o sofrimento humano.",
    "C03_causas": "A psicologia moderna identifica três causas principais para esse vazio existencial. Primeira causa: a ausência de propósito. Quando nossas ações não têm significado além de nós mesmos. Segunda causa: a desconexão social. Não a solidão física — é a falta de vínculos profundos. Terceira causa: a armadilha da comparação. Vivemos conectados a versões curadas e irreais da vida alheia.",
    "C04_neurociencia": "A neurociência explica por que a conquista não preenche o vazio. Nosso cérebro libera dopamina na antecipação de uma recompensa — não na recompensa em si. Quando compramos o carro novo, conseguimos a promoção, ou atingimos o número de seguidores desejado, a dopamina já foi embora. O cérebro já está buscando o próximo objetivo. É um ciclo sem fim projetado pela evolução para nos manter em movimento — não para nos tornar felizes.",
    "C05_harvard": "Em 2021, a Universidade de Harvard publicou os resultados de um estudo iniciado em 1938. Oitenta anos acompanhando a vida de centenas de pessoas. A conclusão foi surpreendente: o que mais prevê satisfação com a vida não é riqueza, fama ou sucesso profissional. São os relacionamentos de qualidade. Não a quantidade de conexões, mas a profundidade delas.",
    "C06_estrategias": "Baseado em evidências científicas, existem cinco estratégias comprovadas para sair do ciclo do vazio. Um: cultive propósito além de você mesmo. Dois: invista em vínculos profundos, não em conexões superficiais. Três: pratique presença — o antídoto da comparação é a gratidão pelo que é real. Quatro: busque estados de flow — momentos de imersão total em atividades desafiadoras. E número cinco: contribua. O ato de ajudar outro ser humano ativa circuitos cerebrais que nenhuma compra consegue replicar.",
    "C07_eudaimonia": "Aristóteles já diferenciava dois tipos de felicidade há mais de dois mil anos. A hedonia: prazer, ausência de dor. É o que o consumo moderno vende. E a eudaimonia: felicidade pelo florescimento humano. A ciência confirma: pessoas com propósito eudaimônico apresentam menor inflamação crônica, melhor sistema imune, e maior longevidade. O vazio que você sente não é uma falha sua. É um sinal. Um chamado para construir algo mais profundo. A pergunta não é como eliminar o vazio — é o que ele está tentando te dizer.",
    "C08_cta": "Se esse vídeo fez sentido para você, compartilhe com alguém que também precisa ouvir isso. Curta, se inscreva, e ative o sino. Porque aqui, falamos sobre o que a ciência revela sobre a mente humana. Até o próximo."
}

def gerar_com_edge_tts(texto: str, arquivo_saida: str) -> bool:
    """Fallback: edge_tts com voz pt-BR masculina"""
    try:
        import asyncio
        import edge_tts

        async def _gerar():
            # Voz masculina pt-BR profissional
            communicate = edge_tts.Communicate(
                texto,
                voice="pt-BR-AntonioNeural",
                rate="-8%",   # levemente mais lento
                pitch="-5Hz"  # voz mais grave
            )
            await communicate.save(arquivo_saida)

        asyncio.run(_gerar())
        return True
    except Exception as e:
        print(f"  ⚠️ edge_tts falhou: {e}")
        return False

def gerar_com_gtts(texto: str, arquivo_saida: str) -> bool:
    """Fallback final: gTTS"""
    try:
        from gtts import gTTS
        tts = gTTS(text=texto, lang='pt', slow=False)
        tts.save(arquivo_saida)
        return True
    except Exception as e:
        print(f"  ⚠️ gTTS falhou: {e}")
        return False

def processar_texto(texto: str) -> str:
    """Limpa o texto para TTS: remove marcações, normaliza pausas"""
    # Remove marcadores de pausa [PAUSA Xs]
    texto = re.sub(r'\[PAUSA \d+(\.\d+)?s\]', '', texto)
    # Remove outras anotações entre colchetes
    texto = re.sub(r'\[.*?\]', '', texto)
    # Normaliza espaços
    texto = ' '.join(texto.split())
    return texto.strip()

def main():
    print("=" * 60)
    print("🎙️  AGENTE AUDIO MASTER — DARK STUDIO AAA")
    print("   V001 — Por Que Você Se Sente Vazio?")
    print("=" * 60)

    resultados = {}
    sucessos = 0

    for cena_id, texto_original in CENAS_NARRACAO.items():
        print(f"\n📢 Gerando: {cena_id}")
        texto = processar_texto(texto_original)
        print(f"   Texto: {texto[:60]}...")

        arquivo_mp3 = str(OUTPUT_DIR / f"{cena_id}.mp3")

        # Tenta edge_tts primeiro (melhor qualidade)
        if gerar_com_edge_tts(texto, arquivo_mp3):
            print(f"   ✅ edge_tts OK → {Path(arquivo_mp3).name}")
            resultados[cena_id] = {"arquivo": arquivo_mp3, "engine": "edge_tts", "status": "ok"}
            sucessos += 1
        elif gerar_com_gtts(texto, arquivo_mp3):
            print(f"   ✅ gTTS OK → {Path(arquivo_mp3).name}")
            resultados[cena_id] = {"arquivo": arquivo_mp3, "engine": "gtts", "status": "ok"}
            sucessos += 1
        else:
            print(f"   ❌ FALHOU — salvo como texto para processamento manual")
            txt_path = str(OUTPUT_DIR / f"{cena_id}_para_gravar.txt")
            Path(txt_path).write_text(texto, encoding='utf-8')
            resultados[cena_id] = {"arquivo": txt_path, "engine": "manual", "status": "pendente"}

    # Salva relatório
    relatorio = {
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "video": "V001",
        "agente": "AUDIO MASTER",
        "total_cenas": len(CENAS_NARRACAO),
        "sucessos": sucessos,
        "score": f"{sucessos}/{len(CENAS_NARRACAO)}",
        "resultados": resultados,
        "proximo_passo": "Executar montar_video.py para sincronizar com imagens"
    }

    relatorio_path = OUTPUT_DIR / "relatorio_narracao.json"
    relatorio_path.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))

    print(f"\n{'=' * 60}")
    print(f"📊 RESULTADO: {sucessos}/{len(CENAS_NARRACAO)} cenas geradas")
    print(f"📁 Áudios em: {OUTPUT_DIR}")
    print(f"📋 Relatório: {relatorio_path}")
    print("=" * 60)

    return relatorio

if __name__ == "__main__":
    main()
