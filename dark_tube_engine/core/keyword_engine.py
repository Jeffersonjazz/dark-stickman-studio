"""
DARK TUBE ENGINE — Keyword Research Engine (clone vidiq keyword research)
Agente: ASSET MANAGER + CREATIVE QA
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
import json
import re
from typing import Optional
from datetime import datetime

try:
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def calcular_score_titulo(titulo: str) -> dict:
    """
    Pontua um título YouTube — clone do vidiq_score_title
    Critérios: comprimento, palavras-chave emocionais, números, perguntas
    """
    score = 0
    feedback = []

    # Comprimento ideal: 40-60 chars
    n = len(titulo)
    if 40 <= n <= 60:
        score += 25
        feedback.append("✅ Comprimento ideal (40-60 chars)")
    elif 30 <= n < 40 or 60 < n <= 70:
        score += 15
        feedback.append("⚠️ Comprimento aceitável")
    else:
        score += 5
        feedback.append("❌ Comprimento fora do ideal")

    # Palavras de alto impacto
    palavras_impacto = [
        "você", "seu", "sua", "por que", "como", "segredo", "revelado",
        "nunca", "sempre", "agora", "real", "verdade", "proibido",
        "chocante", "incrível", "impossível", "descobri", "mistério"
    ]
    titulo_lower = titulo.lower()
    hits = [p for p in palavras_impacto if p in titulo_lower]
    score += min(30, len(hits) * 10)
    if hits:
        feedback.append(f"✅ Palavras de impacto: {', '.join(hits[:3])}")
    else:
        feedback.append("⚠️ Sem palavras de alto impacto")

    # Pergunta = gancho
    if "?" in titulo:
        score += 15
        feedback.append("✅ Pergunta = gancho forte")

    # Número = especificidade
    if re.search(r'\d+', titulo):
        score += 10
        feedback.append("✅ Contém número")

    # Maiúsculas estratégicas
    palavras = titulo.split()
    maiusculas = sum(1 for p in palavras if p.isupper() and len(p) > 1)
    if 0 < maiusculas <= 3:
        score += 10
        feedback.append("✅ Ênfase em maiúsculas")

    # Emoji
    emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
    if emoji_pattern.search(titulo):
        score += 10
        feedback.append("✅ Emoji detectado")

    score = min(100, score)
    nivel = "Excelente" if score >= 80 else "Bom" if score >= 60 else "Regular" if score >= 40 else "Fraco"

    return {
        "titulo": titulo,
        "score": score,
        "nivel": nivel,
        "feedback": feedback,
        "chars": n,
        "recomendacao": _recomendar_titulo(titulo, score)
    }


def _recomendar_titulo(titulo: str, score: int) -> str:
    if score >= 80:
        return "Título otimizado — pronto para publicar"
    if score >= 60:
        return "Adicione uma palavra de impacto emocional ou uma pergunta"
    if score >= 40:
        return "Reescreva com foco em emoção + especificidade (número ou pergunta)"
    return "Reformule completamente — muito genérico ou longo demais"


def pesquisar_palavras_chave_youtube(termo: str, api_key: str = None,
                                      max_results: int = 10) -> dict:
    """
    Pesquisa palavras-chave via YouTube Data API v3 — clone vidiq keyword research
    Fallback: análise semântica local se sem API key
    """
    if api_key and YOUTUBE_API_AVAILABLE:
        try:
            yt = build("youtube", "v3", developerKey=api_key)
            req = yt.search().list(
                q=termo,
                part="snippet",
                type="video",
                maxResults=max_results,
                relevanceLanguage="pt",
                regionCode="BR",
                order="relevance"
            )
            resp = req.execute()
            videos = resp.get("items", [])
            titulos = [v["snippet"]["title"] for v in videos]

            # Extrai palavras-chave dos títulos encontrados
            todas_palavras = " ".join(titulos).lower().split()
            stopwords = {"de", "a", "o", "que", "e", "do", "da", "em", "um", "para",
                         "com", "uma", "os", "no", "se", "na", "por", "mais", "as", "dos",
                         "como", "mas", "ao", "ele", "das", "à", "seu", "sua", "ou", "ser",
                         "quando", "muito", "há", "nos", "já", "está", "eu", "também", "só",
                         "pelo", "pela", "até", "isso", "ela", "entre", "depois", "sem", "mesmo"}
            freq = {}
            for p in todas_palavras:
                p_clean = re.sub(r'[^a-zA-ZÀ-ɏ]', '', p)
                if len(p_clean) > 3 and p_clean not in stopwords:
                    freq[p_clean] = freq.get(p_clean, 0) + 1

            keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:15]
            return {
                "termo": termo,
                "fonte": "youtube_api",
                "keywords": [{"palavra": k, "frequencia": f, "score_estimado": min(100, f * 10)}
                              for k, f in keywords],
                "videos_analisados": len(videos),
                "titulos_referencia": titulos[:5]
            }
        except Exception as e:
            pass  # Fallback abaixo

    # Fallback: expansão semântica local
    return _keyword_expansion_local(termo)


def _keyword_expansion_local(termo: str) -> dict:
    """Expansão semântica local sem API — gera variações e compostos"""
    base = termo.lower().split()
    sufixos = ["revelado", "explicado", "completo", "verdadeiro", "secreto",
                "proibido", "chocante", "real", "hoje", "2025", "2026"]
    prefixos = ["por que", "como", "o que é", "quando", "onde", "a verdade sobre"]

    variações = []
    for s in sufixos:
        variações.append({"palavra": f"{termo} {s}", "score_estimado": 65, "tipo": "composto"})
    for p in prefixos:
        variações.append({"palavra": f"{p} {termo}", "score_estimado": 70, "tipo": "pergunta"})
    for b in base:
        if len(b) > 3:
            variações.append({"palavra": b, "score_estimado": 50, "tipo": "base"})

    return {
        "termo": termo,
        "fonte": "local_expansion",
        "keywords": variações[:15],
        "aviso": "Análise local — conecte YouTube Data API para dados reais",
        "videos_analisados": 0
    }


def analisar_tendencias_nicho(nicho: str) -> dict:
    """Retorna tópicos em alta por nicho — base de conhecimento curada"""
    tendencias = {
        "motivacional": ["por que você procrastina", "psicologia do sucesso",
                         "hábitos de pessoas ricas", "como parar de se sabotar",
                         "mentalidade de crescimento"],
        "terror": ["casas assombradas reais", "histórias de terror brasileiras",
                   "fenômenos inexplicáveis", "lendas urbanas verdadeiras",
                   "experimentos perturbadores"],
        "tech_ia": ["inteligência artificial perigosa", "algoritmos que preveem o futuro",
                    "robôs substituindo humanos", "deepfake e manipulação",
                    "vida digital após a morte"],
        "conspiracao": ["documentos classificados revelados", "experimentos secretos do governo",
                        "operações militares secretas", "programas de controle mental",
                        "arquivos desclassificados CIA"],
        "relaxamento": ["cachoeiras escondidas do mundo", "lugares mais calmos da terra",
                        "sons da natureza para dormir", "paisagens hipnóticas",
                        "ambientes subaquáticos"],
        "documentario": ["eventos históricos esquecidos", "civilizações perdidas",
                         "descobertas arqueológicas", "mistérios do oceano",
                         "fenômenos climáticos extremos"]
    }
    return {
        "nicho": nicho,
        "tendencias": tendencias.get(nicho, []),
        "atualizado": datetime.now().strftime("%Y-%m-%d"),
        "fonte": "dark_tube_engine_knowledge_base"
    }
