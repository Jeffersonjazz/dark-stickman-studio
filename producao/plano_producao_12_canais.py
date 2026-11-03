#!/usr/bin/env python3
"""
DARK STUDIO AAA — PLANO DE PRODUÇÃO 12 CANAIS
Gerado automaticamente pelo DARK MANAGER + 9 Agentes Especialistas
ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# DADOS DOS 12 CANAIS COM ANÁLISE DE RPM E PRIORIDADE
# ============================================================
CANAIS = [
    {
        "id": "canal_11_financas", "nome": "Stickman Finanças", "nicho": "finanças",
        "rpm_usd": 28, "prioridade": 1, "frequencia_semanal": 4,
        "horario_pub": "17:00", "tipo": "Shorts+Long",
        "cor": "#FCD34D", "rpm_q4_boost": 2.0,
        "alertas": ["Verificar advertiser-friendliness", "Evitar conteúdo político"],
        "estrategia": "Shorts: dicas rápidas de 60s | Longs: casos reais de investimento",
        "temas_semana": ["Como investir R$100", "Erro fatal no PIX", "Juros compostos em 60s", "Tesouro Direto vale?"]
    },
    {
        "id": "canal_03_tecnologia", "nome": "Stickman Tech", "nicho": "tecnologia/IA",
        "rpm_usd": 13, "prioridade": 2, "frequencia_semanal": 4,
        "horario_pub": "18:00", "tipo": "Shorts+Long",
        "cor": "#3B82F6", "rpm_q4_boost": 1.9,
        "alertas": ["IA: declarar conteúdo gerado", "Checar claims técnicos"],
        "estrategia": "Shorts: WTF moments de IA | Longs: Como X vai mudar tudo",
        "temas_semana": ["IA que substitui médicos", "ChatGPT vs Gemini vs Claude", "Chip 3nm o que é", "IA detecta câncer antes"]
    },
    {
        "id": "canal_04_stem", "nome": "Stickman STEM", "nicho": "educação/ciência",
        "rpm_usd": 12, "prioridade": 3, "frequencia_semanal": 3,
        "horario_pub": "16:00", "tipo": "Shorts+Long",
        "cor": "#22C55E", "rpm_q4_boost": 1.5,
        "alertas": ["Público jovem — clareza essencial"],
        "estrategia": "Shorts: experimentos em 60s | Longs: descobertas chocantes",
        "temas_semana": ["Por que o céu é azul?", "Maior número primo", "Buracos negros revelados"]
    },
    {
        "id": "canal_10_ciencia", "nome": "Stickman Ciência", "nicho": "ciência",
        "rpm_usd": 10, "prioridade": 4, "frequencia_semanal": 3,
        "horario_pub": "16:00", "tipo": "Shorts+Long",
        "cor": "#34D399", "rpm_q4_boost": 1.4,
        "alertas": ["Citar fontes científicas na descrição"],
        "estrategia": "Shorts: curiosidades de 45s | Longs: explicações profundas",
        "temas_semana": ["Micróbios que controlam seu cérebro", "O universo vai morrer assim", "DNA alien confirmado?"]
    },
    {
        "id": "canal_06_historia", "nome": "Stickman História", "nicho": "história",
        "rpm_usd": 9, "prioridade": 5, "frequencia_semanal": 3,
        "horario_pub": "17:00", "tipo": "Shorts+Long",
        "cor": "#F59E0B", "rpm_q4_boost": 1.3,
        "alertas": ["Verificar datas e fatos históricos"],
        "estrategia": "Shorts: fatos chocantes | Longs: batalhas animadas",
        "temas_semana": ["A verdade sobre Cleópatra", "Como Roma caiu em 1 minuto", "Stonehenge revelado"]
    },
    {
        "id": "canal_02_batalhas", "nome": "Stickman Batalhas", "nicho": "história militar",
        "rpm_usd": 9, "prioridade": 6, "frequencia_semanal": 3,
        "horario_pub": "17:00", "tipo": "Shorts+Long",
        "cor": "#EF4444", "rpm_q4_boost": 1.3,
        "alertas": ["Não glorificar violência", "Contexto histórico obrigatório"],
        "estrategia": "Shorts: quem teria vencido? | Longs: reconstrução de batalhas",
        "temas_semana": ["Vikings vs Romanos", "Batalha de Termópilas", "Guerreiro mais letal da história"]
    },
    {
        "id": "canal_01_psicologia", "nome": "Stickman Psicologia", "nicho": "psicologia",
        "rpm_usd": 8, "prioridade": 7, "frequencia_semanal": 3,
        "horario_pub": "19:00", "tipo": "Shorts+Long",
        "cor": "#6366F1", "rpm_q4_boost": 1.2,
        "alertas": ["Não dar conselhos médicos", "Indicar profissionais quando necessário"],
        "estrategia": "Shorts: gatilhos mentais | Longs: análise comportamental",
        "temas_semana": ["Como manipuladores te controlam", "Por que você procrastina", "Efeito do isolamento"]
    },
    {
        "id": "canal_08_motivacao", "nome": "Stickman Motivação", "nicho": "motivação",
        "rpm_usd": 7.5, "prioridade": 8, "frequencia_semanal": 3,
        "horario_pub": "06:00", "tipo": "Shorts+Long",
        "cor": "#60A5FA", "rpm_q4_boost": 1.2,
        "alertas": ["Evitar clickbait excessivo", "Valor real no conteúdo"],
        "estrategia": "Shorts: citações impactantes | Longs: histórias de superação",
        "temas_semana": ["Hábito que mudou minha vida", "O segredo dos vencedores", "Acorde às 5h por 30 dias"]
    },
    {
        "id": "canal_07_misterio", "nome": "Stickman Mistério", "nicho": "mistério",
        "rpm_usd": 8, "prioridade": 9, "frequencia_semanal": 2,
        "horario_pub": "21:00", "tipo": "Shorts+Long",
        "cor": "#8B5CF6", "rpm_q4_boost": 1.1,
        "alertas": ["ATENÇÃO: temas sensíveis reduzem RPM 50-80%", "Evitar true crime com crimes reais recentes"],
        "estrategia": "Shorts: teaser do mistério | Longs: investigação completa",
        "temas_semana": ["O arquivo que a NASA não quer que você veja", "Civilização desaparecida em 1h"]
    },
    {
        "id": "canal_09_natureza", "nome": "Stickman Natureza", "nicho": "natureza",
        "rpm_usd": 7, "prioridade": 10, "frequencia_semanal": 2,
        "horario_pub": "08:00", "tipo": "Shorts+Long",
        "cor": "#4ADE80", "rpm_q4_boost": 1.2,
        "alertas": ["Forte no Q2 (primavera/verão BR)"],
        "estrategia": "Shorts: animal de 60s | Longs: documentário animado",
        "temas_semana": ["Animal mais perigoso do mundo", "Floresta que respira"]
    },
    {
        "id": "canal_05_filosofia", "nome": "Stickman Filosofia", "nicho": "filosofia",
        "rpm_usd": 7, "prioridade": 11, "frequencia_semanal": 2,
        "horario_pub": "20:00", "tipo": "Shorts+Long",
        "cor": "#A855F7", "rpm_q4_boost": 1.1,
        "alertas": ["Nicho de nicho — crescimento lento mas fiel"],
        "estrategia": "Shorts: paradoxos em 60s | Longs: análise filosófica",
        "temas_semana": ["Você é real ou simulação?", "O que Nietzsche diria hoje"]
    },
    {
        "id": "canal_12_saude", "nome": "Stickman Saúde", "nicho": "saúde/bem-estar",
        "rpm_usd": 6, "prioridade": 12, "frequencia_semanal": 2,
        "horario_pub": "07:00", "tipo": "Shorts+Long",
        "cor": "#F472B6", "rpm_q4_boost": 1.2,
        "alertas": ["NUNCA dar diagnósticos", "Sempre recomendar médico", "Verificar claims de saúde"],
        "estrategia": "Shorts: dicas de 60s | Longs: hábitos saudáveis animados",
        "temas_semana": ["Dormir 6h é suficiente?", "O que acontece ao parar o açúcar"]
    },
]

# ============================================================
# GERAR CALENDÁRIO SEMANAL
# ============================================================
def gerar_calendario_semana(data_inicio: str = "2026-11-03"):
    dt = datetime.strptime(data_inicio, "%Y-%m-%d")
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    calendario = {}
    for d in range(7):
        data = dt + timedelta(days=d)
        dia = dias[d]
        calendario[dia] = {"data": data.strftime("%d/%m"), "publicacoes": []}
    
    # Distribuir canais por dia priorizando maior RPM
    canais_ordenados = sorted(CANAIS, key=lambda x: x["prioridade"])
    
    dia_idx = 0
    for canal in canais_ordenados:
        freq = canal["frequencia_semanal"]
        publicados = 0
        for i in range(7):
            if publicados >= freq:
                break
            dia = dias[(dia_idx + i) % 7]
            calendario[dia]["publicacoes"].append({
                "canal": canal["nome"],
                "horario": canal["horario_pub"],
                "tipo": "Short",
                "tema": canal["temas_semana"][publicados % len(canal["temas_semana"])]
            })
            publicados += 1
        dia_idx = (dia_idx + 2) % 7
    
    return calendario

# ============================================================
# RELATÓRIO DOS 9 AGENTES ESPECIALISTAS
# ============================================================
RELATORIO_AGENTES = {
    "AGENTE IMAGE ENGINE": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "Pillow + FFmpeg (zero custo)",
        "ferramenta_ideal": "FLUX.1 local (8GB VRAM mínimo)",
        "analise": "Thumbnails gerados via dark_image_engine.py. Upscaling com ESRGAN open-source. Para thumbnails YouTube 1280x720 o sistema atual é suficiente.",
        "acao_imediata": "Implementar DARK THUMBNAIL PRO com templates por nicho",
        "custo_mensal": "R$0 (local) ou R$50-200 (FLUX API)",
        "bloqueio": None
    },
    "AGENTE VIDEO GENERATOR": {
        "status": "⚠️ PARCIAL",
        "viabilidade": "MÉDIA",
        "ferramenta_atual": "FFmpeg + imagens estáticas animadas",
        "ferramenta_ideal": "CogVideoX local ou Wan2.1 (16GB VRAM)",
        "analise": "Para Shorts faceless o motion via Ken Burns + zoom é suficiente. Vídeos realistas requerem GPU A100. Alternativa imediata: AnimateDiff CPU-only (lento mas funcional).",
        "acao_imediata": "Implementar zoom_cinematico() no dark_video_generator.py",
        "custo_mensal": "R$0 (Ken Burns) ou R$800-2000 (Runway/Kling API)",
        "bloqueio": "GPU de alta VRAM para vídeos realistas"
    },
    "AGENTE CINEMATIC DIRECTOR": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "dark_cinematic_director.py com 7 presets",
        "ferramenta_ideal": "Igual ao atual + biblioteca de B-roll",
        "analise": "Color grading FFmpeg nativo cobre 90% dos casos. Presets: documentary, nature, mystery, history, technology, motivation, science. Sistema maduro.",
        "acao_imediata": "Criar banco de 500 B-rolls por nicho (CC0 licença)",
        "custo_mensal": "R$0 (Pexels/Pixabay CC0)",
        "bloqueio": None
    },
    "AGENTE VIDEO EDITOR PRO": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "dark_cinema_editor.py + FFmpeg",
        "ferramenta_ideal": "Igual + remoção automática de silêncios",
        "analise": "Pipeline de edição automática funcional. Falta: detecção de silêncio (Silero VAD — gratuito), jump cuts automáticos, sincronização beat.",
        "acao_imediata": "Integrar Silero VAD para remoção de silêncios",
        "custo_mensal": "R$0",
        "bloqueio": None
    },
    "AGENTE MOTION GRAPHICS": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "dark_motion_lab.py com abertura/encerramento",
        "ferramenta_ideal": "Igual + contagem_regressiva, animacao_logo, infografico",
        "analise": "Base sólida. Faltam 4 métodos planejados: contagem_regressiva(), animacao_logo(), infografico_video(), contador_estatisticas(). Prioridade FASE 7.",
        "acao_imediata": "Implementar os 4 métodos faltantes (estimativa: 2h)",
        "custo_mensal": "R$0",
        "bloqueio": None
    },
    "AGENTE AUDIO MASTER": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "edge-tts (Microsoft, gratuito) + FFmpeg EQ",
        "ferramenta_ideal": "XTTS v2 local (voz clonada em PT-BR)",
        "analise": "edge-tts (pt-BR-AntonioNeural) gera narração aceitável. Para qualidade premium: XTTS v2 (4GB VRAM, Apache 2.0). ElevenLabs MCP offline permanente nesta sessão — fallback confirmado.",
        "acao_imediata": "Instalar XTTS v2 para qualidade cinematográfica",
        "custo_mensal": "R$0 (edge-tts) ou R$0 (XTTS local) ou R$90/mês (ElevenLabs)",
        "bloqueio": "ElevenLabs MCP: 404 permanente — usar edge-tts"
    },
    "AGENTE VISUAL CONSISTENCY": {
        "status": "✅ OPERACIONAL — FASE 8 COMPLETA",
        "viabilidade": "ALTA",
        "ferramenta_atual": "dark_visual_consistency.py + bíblia visual JSON",
        "ferramenta_ideal": "Igual + validação por embedding de imagem",
        "analise": "Sistema de continuidade completo: 7 paletas de nicho, bíblia visual persistida, validação de cenas. Resultado dos testes: STATUS ok | ALERTAS: [] | BÍBLIA: ok.",
        "acao_imediata": "Adicionar validação por CLIP embeddings (Hugging Face gratuito)",
        "custo_mensal": "R$0",
        "bloqueio": None
    },
    "AGENTE ASSET MANAGER": {
        "status": "⚠️ BÁSICO",
        "viabilidade": "MÉDIA-ALTA",
        "ferramenta_atual": "Sistema de pastas em producao/",
        "ferramenta_ideal": "dark_asset_manager.py com banco SQLite + tags",
        "analise": "Falta módulo dedicado. Assets dispersos em producao/. Necessário: índice SQLite de assets, sistema de tags, deduplicação, controle de licenças.",
        "acao_imediata": "Criar core/dark_asset_manager.py (estimativa: 3h)",
        "custo_mensal": "R$0",
        "bloqueio": None
    },
    "AGENTE CREATIVE QA": {
        "status": "✅ OPERACIONAL",
        "viabilidade": "ALTA",
        "ferramenta_atual": "dark_creative_qa.py — verificação automática",
        "ferramenta_ideal": "Igual + análise de retenção preditiva",
        "analise": "QA automático verifica: resolução, duração, áudio, legenda, disclosure IA, watermark. Integrado ao DarkManager (FASE 9 ✅). Resultado pipeline: QA aprovado.",
        "acao_imediata": "Adicionar check de CTR estimado (análise do thumbnail)",
        "custo_mensal": "R$0",
        "bloqueio": None
    }
}

# ============================================================
# MÉTRICAS PROJETADAS (CONSERVADORAS)
# ============================================================
def calcular_projecao_mensal():
    total_videos_mes = sum(c["frequencia_semanal"] * 4 for c in CANAIS)
    
    projecoes = []
    for canal in CANAIS:
        videos_mes = canal["frequencia_semanal"] * 4
        # Views estimadas: 200-2000/vídeo para canal iniciante
        views_estimadas_baixo = videos_mes * 200
        views_estimadas_alto = videos_mes * 2000
        
        receita_baixo = (views_estimadas_baixo / 1000) * canal["rpm_usd"] * 5.8  # USD→BRL
        receita_alto = (views_estimadas_alto / 1000) * canal["rpm_usd"] * 5.8
        
        projecoes.append({
            "canal": canal["nome"],
            "videos_mes": videos_mes,
            "views_baixo": views_estimadas_baixo,
            "views_alto": views_estimadas_alto,
            "receita_brl_baixo": round(receita_baixo, 2),
            "receita_brl_alto": round(receita_alto, 2)
        })
    
    return projecoes, total_videos_mes

if __name__ == "__main__":
    print("=" * 70)
    print("DARK STUDIO AAA — PLANO DE PRODUÇÃO 12 CANAIS")
    print("Data: 02/11/2026 | Versão: 1.0")
    print("ai_generated: True | DARK CREATIVE LAB")
    print("=" * 70)
    
    print("\n📊 RANKING POR PRIORIDADE (RPM USD):")
    for c in CANAIS:
        bar = "█" * int(c["rpm_usd"])
        print(f"  P{c['prioridade']:2d} | {c['nome']:25s} | ${c['rpm_usd']:5.1f} | {bar}")
    
    print("\n📅 CALENDÁRIO SEMANA 02-08/11/2026:")
    cal = gerar_calendario_semana("2026-11-03")
    total_pub = 0
    for dia, info in cal.items():
        pubs = info["publicacoes"]
        total_pub += len(pubs)
        if pubs:
            print(f"\n  {dia} {info['data']}:")
            for p in pubs:
                print(f"    {p['horario']} | {p['canal']}: \"{p['tema']}\"")
    print(f"\n  TOTAL SEMANA: {total_pub} publicações")
    
    print("\n🤖 STATUS DOS 9 AGENTES ESPECIALISTAS:")
    for agente, dados in RELATORIO_AGENTES.items():
        print(f"\n  {dados['status']} {agente}")
        print(f"    Viabilidade: {dados['viabilidade']}")
        print(f"    Custo/mês: {dados['custo_mensal']}")
        if dados['bloqueio']:
            print(f"    ⚠️  BLOQUEIO: {dados['bloqueio']}")
        print(f"    Ação: {dados['acao_imediata']}")
    
    print("\n💰 PROJEÇÃO FINANCEIRA MENSAL (CONSERVADORA):")
    projecoes, total = calcular_projecao_mensal()
    print(f"  Total de vídeos/mês: {total}")
    total_baixo = sum(p["receita_brl_baixo"] for p in projecoes)
    total_alto = sum(p["receita_brl_alto"] for p in projecoes)
    for p in projecoes[:5]:
        print(f"  {p['canal']:25s} | {p['videos_mes']:2d} vids | R${p['receita_brl_baixo']:8.2f} – R${p['receita_brl_alto']:,.2f}")
    print(f"  {'TOTAL (12 CANAIS)':25s} |          | R${total_baixo:8.2f} – R${total_alto:,.2f}")
    
    print("\n✅ CAMINHO TÉCNICO CORRETO? VEREDICTO DOS AGENTES:")
    corretos = sum(1 for a in RELATORIO_AGENTES.values() if "✅" in a["status"])
    parciais = sum(1 for a in RELATORIO_AGENTES.values() if "⚠️" in a["status"])
    print(f"  {corretos}/9 agentes OPERACIONAIS ✅")
    print(f"  {parciais}/9 agentes PARCIAIS ⚠️ (precisam de GPU ou módulo)")
    print(f"  Custo total do sistema: R$0/mês (stack 100% gratuito)")
    print(f"\n  VEREDICTO: ✅ SIM — caminho técnico CORRETO e VIÁVEL")
    print(f"  Stack: Python + FFmpeg + edge-tts + Pillow + open-source")
    print(f"  Limitação: Vídeos realistas precisam de GPU (nuvem opcional)")
    print()

