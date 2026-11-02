"""
DARK STUDIO AAA — BATCH DE PRODUÇÃO SEMANAL
Semana: 03–08 Nov 2026 | 5 Shorts (1 por canal principal)
Agentes: IMAGE_ENGINE, AUDIO_MASTER, ASSET_MANAGER, CREATIVE_QA, VIDEO_EDITOR_PRO

Calendário oficial:
  Seg (03/11) 17h → Mente de Aço (Psicologia/Motivação)
  Ter (04/11) 17h → Intelligentia Nova (Tecnologia/IA)
  Qua (05/11) 17h → Bastidores do Tempo (História)
  Qui (06/11) 17h → Projeto Secreto (Conspirações)
  Sex (07/11) 17h → AquaZen Relax (Natureza/Sons)

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys, json, os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'dark_tube_engine'))
from fastapi.testclient import TestClient
from dark_tube_engine.api.main import app
from dark_tube_engine.agents.dark_manager import DarkManager

client = TestClient(app)
dm = DarkManager()

# ══════════════════════════════════════════
# PAUTA SEMANAL — 5 SHORTS
# ══════════════════════════════════════════
PAUTA = [
    {
        "dia": "Seg 03/11",
        "horario": "17:00 BRT",
        "canal": "Mente de Aço",
        "nicho": "motivacional",
        "titulo": "Por Que Você Nunca Executa Seus Planos?",
        "script": """Você já se perguntou por que tem tantos planos mas age tão pouco?
Não é falta de motivação. É neurociência.
Seu cérebro trata planos futuros como uma identidade separada — você de amanhã é quase um estranho.
Por isso é fácil prometer coisas que o "você de amanhã" vai fazer.
A solução não é mais força de vontade.
É reduzir a distância entre decisão e ação para menos de dois minutos.
Comece agora. Não amanhã.""",
        "emoji": "🧠",
        "tag_youtube": "#psicologia #motivacao #mentalidade #shorts"
    },
    {
        "dia": "Ter 04/11",
        "horario": "17:00 BRT",
        "canal": "Intelligentia Nova",
        "nicho": "tech_ia",
        "titulo": "A IA Que Prevê Sua Morte Antes de Você Saber",
        "script": """Algoritmos de IA já analisam milhões de prontuários médicos.
Em hospitais dos EUA, um sistema prevê com 78% de precisão quais pacientes morrerão em 24 horas.
Os médicos ficaram chocados: a IA acertava casos que eles consideravam estáveis.
Ela identificava padrões imperceptíveis — variações sutis na pressão, frequência cardíaca e exames.
Isso levanta uma questão ética brutal: você quer saber?
E se a IA prever sua morte, o que fazemos com esse dado?
O futuro da medicina é poderoso. E assustador.""",
        "emoji": "🤖",
        "tag_youtube": "#inteligenciaartificial #ia #tecnologia #shorts"
    },
    {
        "dia": "Qua 05/11",
        "horario": "17:00 BRT",
        "canal": "Bastidores do Tempo",
        "nicho": "documentario",
        "titulo": "Por Que Roma Escondeu Este Segredo por 1500 Anos?",
        "script": """Em 476 d.C., Roma caiu. Ou foi o que disseram.
O que poucos sabem é que existia um segundo Império Romano — Constantinopla.
Ela sobreviveu por mais mil anos enquanto a Europa Ocidental afundava no caos.
Bibliotecas preservadas. Leis mantidas. Ciência continuando.
Quando Constantinopla finalmente caiu em 1453, seus estudiosos fugiram para a Itália.
Trouxeram consigo manuscritos gregos esquecidos há séculos.
Isso desencadeou o Renascimento.
Roma não morreu em 476. Ela ressurgiu em Florença.""",
        "emoji": "🏛️",
        "tag_youtube": "#historia #roma #curiosidades #shorts"
    },
    {
        "dia": "Qui 06/11",
        "horario": "17:00 BRT",
        "canal": "Projeto Secreto",
        "nicho": "conspiracao",
        "titulo": "Por Que o Governo Lavou Cérebros de Cidadãos Reais?",
        "script": """Entre 1953 e 1973, a CIA conduziu experimentos secretos em cidadãos comuns.
Sem consentimento. Sem conhecimento. Sem remorso.
LSD administrado em hospitais psiquiátricos. Choques elétricos. Privação de sono.
O objetivo: desenvolver técnicas de controle mental para a Guerra Fria.
Os documentos foram destruídos em 1973 — por ordem direta.
Em 1977, alguns sobreviveram. O Congresso ficou horrorizado.
20.000 documentos revelados pelo FOIA mostram o que restou.
MKUltra foi real. E não foi o único programa.""",
        "emoji": "🕵️",
        "tag_youtube": "#conspiracao #cia #mkultra #shorts"
    },
    {
        "dia": "Sex 07/11",
        "horario": "17:00 BRT",
        "canal": "AquaZen Relax",
        "nicho": "relaxamento",
        "titulo": "Você NUNCA Dormiu Tão Bem Quanto Com Estes Sons da Natureza",
        "script": """Deixe os sons da natureza guiarem você para um sono profundo.
Água correndo sobre pedras antigas.
Vento entre as árvores.
Pássaros ao amanhecer.
Sem pensamentos. Sem preocupações.
Apenas o presente.""",
        "emoji": "🌊",
        "tag_youtube": "#relaxamento #natureza #sonoeprofundo #shorts"
    }
]

def produzir_short(item: dict, idx: int) -> dict:
    """Executa pipeline completo de produção via DarkManager"""
    print(f"\n{'═'*55}")
    print(f"  SHORT {idx+1}/5 — {item['dia']} às {item['horario']}")
    print(f"  CANAL: {item['canal']}")
    print(f"  TÍTULO: {item['titulo']}")
    print(f"{'═'*55}")

    resultado = {"short": idx+1, "canal": item["canal"], "dia": item["dia"], "etapas": {}}

    # ── AGENTE ASSET_MANAGER: Score do Título ─────────────────
    print("\n[ASSET_MANAGER] Analisando título...")
    r_score = client.post('/script/score-titulo', json={"titulo": item["titulo"]})
    score_data = r_score.json()
    score = score_data.get("score", 0)
    grade = score_data.get("grade", "?")
    print(f"  Score SEO: {score}/100 ({grade})")
    resultado["etapas"]["score_titulo"] = {"score": score, "grade": grade}

    # ── AGENTE AUDIO_MASTER: Keywords ─────────────────────────
    print("\n[ASSET_MANAGER] Pesquisando keywords...")
    r_kw = client.post('/keywords/pesquisar', json={"tema": item["titulo"], "max_results": 8})
    kw_data = r_kw.json()
    kw_raw = kw_data.get("keywords", [])[:5]
    # keywords pode ser lista de dicts {"palavra": ..., "score": ...} ou lista de strings
    keywords = [k["palavra"] if isinstance(k, dict) else k for k in kw_raw]
    print(f"  Keywords: {', '.join(keywords[:3])}...")
    resultado["etapas"]["keywords"] = keywords

    # ── AGENTE IMAGE_ENGINE: Thumbnail ─────────────────────────
    print("\n[IMAGE_ENGINE] Gerando thumbnail 1080x1920 (Shorts)...")
    r_thumb = client.post('/thumbnail/gerar', json={
        "titulo": item["titulo"],
        "canal": item["canal"],
        "nicho": item["nicho"],
        "subtitulo": item.get("tag_youtube", "").split(" ")[0],
        "tamanho": "thumbnail_shorts",
        "emoji": item.get("emoji", "")
    })
    thumb_data = r_thumb.json()
    thumb_path = thumb_data.get("path", "")
    print(f"  Thumbnail: {thumb_path}")
    resultado["etapas"]["thumbnail"] = thumb_path

    # ── AGENTE AUDIO_MASTER: Voiceover ─────────────────────────
    print("\n[AUDIO_MASTER] Gerando narração PT-BR...")
    voice_map = {
        "Mente de Aço": "pt-BR-AntonioNeural",
        "Intelligentia Nova": "pt-BR-AntonioNeural",
        "Bastidores do Tempo": "pt-BR-AntonioNeural",
        "Projeto Secreto": "pt-BR-AntonioNeural",
        "AquaZen Relax": "pt-BR-FranciscaNeural",
    }
    voice_id = voice_map.get(item["canal"], "pt-BR-AntonioNeural")
    r_audio = client.post('/voiceover/gerar', json={
        "script": item["script"],
        "voice_id": voice_id,
        "rate": "+5%" if item["nicho"] != "relaxamento" else "-10%"
    })
    audio_data = r_audio.json()
    job_id = audio_data.get("job_id", "")
    print(f"  Job áudio: {job_id} | Backend: edge-tts (gratuito)")
    resultado["etapas"]["audio"] = {"job_id": job_id, "voice": voice_id}

    # ── AGENTE SCRIPT: Criar job roteiro ──────────────────────
    print("\n[VIDEO_EDITOR_PRO] Criando roteiro estruturado...")
    r_script = client.post('/script/criar', json={
        "titulo": item["titulo"],
        "canal": item["canal"],
        "nicho": item["nicho"],
        "duracao_alvo": 60,
        "palavras_chave": keywords[:3]
    })
    script_data = r_script.json()
    print(f"  Script job: {script_data.get('job_id', 'ok')}")
    resultado["etapas"]["script"] = script_data.get("job_id", "")

    # ── AGENTE CREATIVE_QA: Verificação ───────────────────────
    print("\n[CREATIVE_QA] Verificação de qualidade...")
    qa_ok = score >= 50 and len(item["script"]) >= 100
    print(f"  Score SEO ≥ 50: {'✅' if score >= 50 else '❌'}")
    print(f"  Script ≥ 100 chars: {'✅' if len(item['script']) >= 100 else '❌'}")
    print(f"  Thumbnail gerado: {'✅' if thumb_path else '❌'}")
    resultado["etapas"]["qa"] = {"aprovado": qa_ok, "score": score}

    # ── DARK MANAGER: Roteamento e contrato ───────────────────
    contrato = dm.rotear(f"compose_short_{item['nicho']}", {
        "titulo": item["titulo"],
        "canal": item["canal"],
        "script": item["script"][:200]
    })
    resultado["contrato_id"] = contrato["contrato"]["contrato_id"]

    resultado["status"] = "PRONTO_PARA_POSTAGEM" if qa_ok else "REVISAO_NECESSARIA"
    resultado["postagem"] = {
        "data": item["dia"],
        "horario": item["horario"],
        "titulo_youtube": item["titulo"],
        "tags": item["tag_youtube"],
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "ai_generated_tag": True
    }
    return resultado

# ══════════════════════════════════════════
# EXECUTAR BATCH
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("\n")
    print("╔══════════════════════════════════════════════════════╗")
    print("║   DARK STUDIO AAA — BATCH SEMANAL NOV/2026          ║")
    print("║   9 Agentes Evocados | 5 Shorts | 5 Canais          ║")
    print("╚══════════════════════════════════════════════════════╝")

    status_dm = dm.status_agentes()
    print(f"\n✅ {status_dm['total_agentes']} agentes ativos | Session: {status_dm['session_id']}")

    batch_resultado = []
    for i, item in enumerate(PAUTA):
        res = produzir_short(item, i)
        batch_resultado.append(res)

    # Salvar relatório
    out_dir = Path("producao/semana_01_nov_2026")
    out_dir.mkdir(parents=True, exist_ok=True)
    relatorio_path = out_dir / "relatorio_batch.json"

    relatorio = {
        "batch": "Semana 01 — Nov 2026",
        "gerado_em": datetime.now().isoformat(),
        "total_shorts": len(batch_resultado),
        "canais": [r["canal"] for r in batch_resultado],
        "shorts": batch_resultado,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }

    with open(relatorio_path, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    # Resumo final
    print("\n")
    print("╔══════════════════════════════════════════════════════╗")
    print("║              RESUMO DO BATCH SEMANAL                ║")
    print("╠══════════════════════════════════════════════════════╣")
    aprovados = sum(1 for r in batch_resultado if r["status"] == "PRONTO_PARA_POSTAGEM")
    print(f"║  Total produzido:  {len(batch_resultado)}/5 Shorts               ║")
    print(f"║  Aprovados QA:     {aprovados}/5                              ║")
    print(f"║  Custo total:      R$0,00 (100% gratuito)          ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  CALENDÁRIO DE POSTAGEM:                            ║")
    for r in batch_resultado:
        status_icon = "✅" if r["status"] == "PRONTO_PARA_POSTAGEM" else "⚠️"
        canal_curto = r["canal"][:20].ljust(20)
        print(f"║  {status_icon} {r['dia']} 17h | {canal_curto}  ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  Relatório: {str(relatorio_path):<39} ║")
    print("╚══════════════════════════════════════════════════════╝")
    print("\nPROXIMO PASSO: Abrir YouTube Studio e agendar postagem via /publish/upload")
    print("Ou usar: app.vidiq.com → Upload → colar metadados do relatório JSON\n")
