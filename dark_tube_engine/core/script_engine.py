"""
DARK TUBE ENGINE — Script Engine (clone vidiq_generate_script)
Agente: CINEMATIC DIRECTOR + VIDEO EDITOR PRO
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import os
import json
import uuid
from typing import Optional
from pathlib import Path

# Templates de roteiro por nicho — engenharia reversa dos padrões vidIQ
TEMPLATES = {
    "motivacional": {
        "estrutura": ["gancho_emocional", "problema", "virada", "licao", "cta"],
        "duracao_alvo_s": 60,
        "estilo": "direto, impactante, segunda pessoa"
    },
    "terror": {
        "estrutura": ["cena_atmosfera", "personagem", "evento_estranho", "escalada", "final_perturbador"],
        "duracao_alvo_s": 75,
        "estilo": "suspense crescente, narração em primeira pessoa"
    },
    "tech_ia": {
        "estrutura": ["dado_chocante", "contexto", "como_funciona", "implicacoes", "reflexao_cta"],
        "duracao_alvo_s": 60,
        "estilo": "informativo, jornalístico, números reais"
    },
    "conspiracao": {
        "estrutura": ["revelacao_inicial", "evidencias", "conexoes", "o_que_nao_querem", "conclusao"],
        "duracao_alvo_s": 75,
        "estilo": "investigativo, referências documentadas"
    },
    "relaxamento": {
        "estrutura": ["convite", "descricao_lugar1", "descricao_lugar2", "descricao_lugar3", "encerramento_zen"],
        "duracao_alvo_s": 90,
        "estilo": "poético, sensorial, segunda pessoa"
    },
    "documentario": {
        "estrutura": ["abertura_cena", "contexto_historico", "desenvolvimento", "revelacao", "impacto_atual"],
        "duracao_alvo_s": 75,
        "estilo": "narrador onisciente, fatos verificados"
    }
}

CANAL_PARA_NICHO = {
    "Mente de Aço": "motivacional",
    "Esquina do Medo": "terror",
    "Intelligentia Nova": "tech_ia",
    "Projeto Secreto": "conspiracao",
    "AquaZen Relax": "relaxamento",
    "Dark Nature": "documentario",
    "Historia Sombria": "documentario",
    "Psique Dark": "motivacional",
    "Tech Noir": "tech_ia",
    "Cripto Sombrio": "conspiracao",
    "Sons do Universo": "relaxamento",
    "Mentes Brilhantes": "motivacional"
}


def gerar_prompt_script(titulo: str, canal: str, nicho: str = None,
                         duracao_alvo: int = 60, palavras_chave: list = None) -> str:
    """Gera prompt otimizado para LLM criar roteiro — clone da lógica vidIQ"""
    if not nicho:
        nicho = CANAL_PARA_NICHO.get(canal, "documentario")
    template = TEMPLATES.get(nicho, TEMPLATES["documentario"])
    estrutura = " → ".join(template["estrutura"])
    estilo = template["estilo"]
    kw = ", ".join(palavras_chave) if palavras_chave else titulo

    prompt = f"""Crie um roteiro de Short do YouTube para o canal "{canal}" com o título "{titulo}".

REQUISITOS TÉCNICOS:
- Duração: {duracao_alvo} segundos de narração (aproximadamente {duracao_alvo * 2} palavras)
- Nicho: {nicho}
- Estilo: {estilo}
- Estrutura obrigatória: {estrutura}
- Palavras-chave a incluir: {kw}
- Formato: SEM apresentador, narração off (faceless channel)
- Idioma: Português Brasileiro natural e fluente
- Deve ter gancho nos primeiros 3 segundos

DIRETRIZES:
- Início IMEDIATO no tema, sem "Olá, bem-vindos"
- Frases curtas e impactantes
- Uma ideia por frase
- Final com chamada para ação sutil (curtir/comentar/seguir)
- Tom: {estilo}

ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Escreva APENAS o roteiro, sem metadados ou explicações."""
    return prompt


def criar_job_script(titulo: str, canal: str, nicho: str = None,
                     duracao_alvo: int = 60, palavras_chave: list = None) -> dict:
    """
    Cria job de geração de script — clone do vidiq_generate_script
    Retorna estrutura de job compatível com o sistema DARK TUBE
    """
    job_id = f"dtjob_{uuid.uuid4().hex[:16]}"
    nicho_detectado = nicho or CANAL_PARA_NICHO.get(canal, "documentario")
    return {
        "job_id": job_id,
        "status": "pending",
        "tipo": "generate_script",
        "payload": {
            "titulo": titulo,
            "canal": canal,
            "nicho": nicho_detectado,
            "duracao_alvo": duracao_alvo,
            "palavras_chave": palavras_chave or [],
            "template": TEMPLATES.get(nicho_detectado),
            "prompt": gerar_prompt_script(titulo, canal, nicho_detectado,
                                          duracao_alvo, palavras_chave)
        },
        "resultado": None,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
    }


def salvar_script(titulo: str, canal: str, conteudo: str,
                  output_dir: str = "outputs/scripts") -> dict:
    """Salva roteiro em arquivo e retorna metadados"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    script_id = str(uuid.uuid4())[:8]
    slug = titulo.lower().replace(" ", "_")[:40]
    filename = f"script_{script_id}_{slug}.txt"
    path = os.path.join(output_dir, filename)

    meta_content = f"""# {titulo}
# Canal: {canal}
# DARK TUBE ENGINE — Script
# ai_generated: True
# ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
# script_id: {script_id}
---
{conteudo}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(meta_content)

    chars = len(conteudo)
    palavras = len(conteudo.split())
    duracao_est = palavras / 2.5  # ~2.5 palavras/segundo PT-BR

    return {
        "script_id": script_id,
        "titulo": titulo,
        "canal": canal,
        "path": path,
        "filename": filename,
        "chars": chars,
        "palavras": palavras,
        "duracao_estimada_s": round(duracao_est),
        "status": "saved"
    }
