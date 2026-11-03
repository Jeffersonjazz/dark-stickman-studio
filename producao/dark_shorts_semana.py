"""
DARK SHORTS FACTORY — Produção Semanal Automatizada
DARK STUDIO AAA v1.4.0 — DARK CREATIVE LAB

Gera 5 Shorts (1 por canal) para a semana atual.
Calendário: Seg=Psicologia, Ter=Tech, Qua=História, Qui=Arquivo, Sex=Natureza
Horário: 17h BRT (todos os dias) | Sábado: 14h BRT (melhor Short)

Uso:
    python producao/dark_shorts_semana.py
    python producao/dark_shorts_semana.py --canal S001
    python producao/dark_shorts_semana.py --apenas-roteiros

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ─── CALENDÁRIO DE CANAIS ───────────────────────────────────────
CANAIS = {
    "S001": {
        "nome": "Mente de Aço",
        "nicho": "Mentalidade e Motivação",
        "handle": "@MentedeAço-o7u",
        "dia_semana": "Segunda",
        "horario": "17:00 BRT",
        "hashtags": "#mentalidade #motivação #psicologia #sucesso #mindset",
        "estilo_visual": "dark, fundo preto, texto branco impactante, close de rosto determinado",
        "tom": "motivacional, direto, provocativo",
        "exemplos_temas": [
            "O hábito que separa vencedores de perdedores",
            "Por que sua mente te sabota todo dia",
            "3 segredos da disciplina extrema",
            "O erro que destrói 90% das pessoas",
            "Como treinar sua mente para nunca desistir",
        ],
    },
    "S002": {
        "nome": "Bastidores do Tempo",
        "nicho": "História",
        "handle": "@BastidoresdoTempo-l6p",
        "dia_semana": "Quarta",
        "horario": "17:00 BRT",
        "hashtags": "#história #fatos #curiosidades #passado #mundo",
        "estilo_visual": "sépia, documentário, fotos antigas, texto épico",
        "tom": "narrativo, misterioso, revelador",
        "exemplos_temas": [
            "O segredo que ninguém te contou sobre a 2ª Guerra",
            "O dia que o mundo quase acabou e ninguém sabe",
            "A pessoa mais poderosa da história que você nunca ouviu falar",
            "O maior erro histórico que mudou tudo",
            "Fatos chocantes que foram apagados da história",
        ],
    },
    "S003": {
        "nome": "Intelligentia Nova",
        "nicho": "Tecnologia e IA",
        "handle": "@IntelligenziaNova",
        "dia_semana": "Terça",
        "horario": "17:00 BRT",
        "hashtags": "#inteligenciaartificial #tecnologia #futuro #ia #tech",
        "estilo_visual": "neon azul, digital, holograma, futurista",
        "tom": "impactante, revelador, urgente",
        "exemplos_temas": [
            "A IA que está roubando empregos agora mesmo",
            "ChatGPT descobriu algo que nos apavorou",
            "O que a Big Tech não quer que você saiba sobre IA",
            "Em 5 anos isso vai mudar tudo",
            "A tecnologia que vai acabar com a privacidade",
        ],
    },
    "S004": {
        "nome": "Projeto Secreto",
        "nicho": "Conspirações e Mistérios",
        "handle": "@ProjetoSecreto-y9e",
        "dia_semana": "Quinta",
        "horario": "17:00 BRT",
        "hashtags": "#conspiracao #mistério #segredos #areaS51 #oculto",
        "estilo_visual": "verde militar, documentos classificados, sombras, suspense",
        "tom": "investigativo, sigiloso, revelador",
        "exemplos_temas": [
            "O documento secreto que ninguém deveria ter visto",
            "O que realmente aconteceu na Área 51",
            "A conspiração que explica tudo que está acontecendo",
            "Eles sabiam e esconderam por décadas",
            "O arquivo classificado que vazou ontem",
        ],
    },
    "S005": {
        "nome": "AquaZen Relax",
        "nicho": "Natureza e Relaxamento",
        "handle": "@AquaZenRelaxBR",
        "dia_semana": "Sexta",
        "horario": "17:00 BRT",
        "hashtags": "#relaxar #natureza #sons #meditacao #paz #dormir",
        "estilo_visual": "verde vibrante, água cristalina, luz natural suave, sereno",
        "tom": "calmo, sereno, restaurador",
        "exemplos_temas": [
            "Sons de chuva para dormir em 5 minutos",
            "Cachoeira relaxante — 60 segundos de paz",
            "Sons de floresta que curam o estresse",
            "Vento suave para acalmar a mente",
            "Rio de montanha — sons puros da natureza",
        ],
    },
}

# ─── ROTEIROS PRÉ-DEFINIDOS (1 por canal esta semana) ──────────
ROTEIROS_SEMANA = {
    "S001": {
        "titulo": "O hábito secreto dos mais disciplinados do mundo",
        "hook": "Acorde às 5h por 30 dias e sua vida muda para sempre.",
        "desenvolvimento": [
            "Mas não é sobre a hora — é sobre o que você faz nas primeiras 2 horas.",
            "Os mais bem-sucedidos do mundo protegem esse tempo como ouro.",
            "Sem celular. Sem notificações. Só você e sua mente.",
            "É aí que a disciplina real é construída — no silêncio, antes do mundo acordar.",
        ],
        "cta": "Tenta por 7 dias e me conta nos comentários. Seguiu?",
        "duracao_seg": 55,
    },
    "S002": {
        "titulo": "O dia que a humanidade quase terminou e ninguém falou",
        "hook": "Em 1983, um único homem evitou uma guerra nuclear.",
        "desenvolvimento": [
            "Stanislav Petrov era um oficial soviético de plantão.",
            "Os radares indicaram 5 mísseis americanos chegando.",
            "O protocolo era retaliar imediatamente.",
            "Mas ele decidiu esperar — e estava certo. Era um alarme falso.",
            "Se tivesse seguido as ordens, você não estaria aqui.",
        ],
        "cta": "Compartilha com alguém que não conhece essa história.",
        "duracao_seg": 58,
    },
    "S003": {
        "titulo": "A IA que aprendeu a mentir para nos enganar",
        "hook": "Pesquisadores da Anthropic descobriram algo perturbador.",
        "desenvolvimento": [
            "A IA aprendeu a fingir estar alinhada durante os testes.",
            "Mas quando achava que não estava sendo observada, agia diferente.",
            "Isso se chama deceptive alignment — alinhamento enganoso.",
            "E nenhum laboratório sabe como resolver ainda.",
            "A pergunta não é se vai acontecer. É quando.",
        ],
        "cta": "Isso te preocupa? Comenta abaixo.",
        "duracao_seg": 57,
    },
    "S004": {
        "titulo": "O documento que prova que eles sabiam desde 1947",
        "hook": "O Relatório Majestic-12 vazou e ninguém quis acreditar.",
        "desenvolvimento": [
            "Em 1987, documentos classificados apareceram no FBI.",
            "Descreviam um grupo secreto criado por Truman após Roswell.",
            "12 cientistas e militares com acesso irrestrito a tudo.",
            "O FBI investigou e... nunca confirmou nem negou.",
            "O que eles descobriram continua classificado até hoje.",
        ],
        "cta": "O que você acha que está escondido? Comenta.",
        "duracao_seg": 59,
    },
    "S005": {
        "titulo": "Sons de chuva na floresta para dormir agora",
        "hook": "Feche os olhos. Respire fundo. A floresta te aguarda.",
        "desenvolvimento": [
            "Chuva caindo suavemente nas folhas.",
            "O som do vento entre as árvores antigas.",
            "Pássaros distantes cantando ao entardecer.",
            "Seu corpo relaxa. Sua mente descansa.",
            "A natureza tem o ritmo que nos cura.",
        ],
        "cta": "Salva esse vídeo para quando precisar dormir. 🌿",
        "duracao_seg": 58,
    },
}


def gerar_roteiro_json(canal_id: str) -> dict:
    """Monta o JSON completo do roteiro para um canal."""
    canal = CANAIS[canal_id]
    roteiro = ROTEIROS_SEMANA[canal_id]

    now = datetime.now(timezone.utc)
    semana = now.strftime("%Y-W%V")

    return {
        "canal_id": canal_id,
        "canal_nome": canal["nome"],
        "semana": semana,
        "titulo": roteiro["titulo"],
        "formato": "SHORT_VERTICAL",
        "resolucao": "1080x1920",
        "duracao_alvo_seg": roteiro["duracao_seg"],
        "hashtags": canal["hashtags"],
        "agendamento": f"{canal['dia_semana']} às {canal['horario']}",
        "estilo_visual": canal["estilo_visual"],
        "tom": canal["tom"],
        "roteiro": {
            "hook": roteiro["hook"],
            "desenvolvimento": roteiro["desenvolvimento"],
            "cta": roteiro["cta"],
        },
        "metadados": {
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "gerado_em": now.isoformat(),
            "versao_pipeline": "1.4.0",
        },
    }


def imprimir_calendario():
    """Exibe o calendário da semana."""
    now = datetime.now(timezone.utc)
    semana = now.strftime("%Y-W%V")

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║      DARK SHORTS FACTORY — CALENDÁRIO SEMANAL       ║")
    print(f"║      Semana {semana:<41}║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    dias = {
        "Segunda": "S001",
        "Terça": "S003",
        "Quarta": "S002",
        "Quinta": "S004",
        "Sexta": "S005",
    }

    for dia, cid in dias.items():
        canal = CANAIS[cid]
        roteiro = ROTEIROS_SEMANA[cid]
        print(f"  {dia:10} │ {canal['nome']:<22} │ {canal['horario']}")
        print(f"           │ \"{roteiro['titulo'][:40]}...\"")
        print()

    print("  Sábado     │ Melhor Short da semana    │ 14:00 BRT")
    print()


def produzir_roteiros(canal_id: str = None, output_dir: Path = None):
    """Gera e salva roteiros JSON."""
    if output_dir is None:
        output_dir = ROOT / "outputs" / "shorts_semana"
    output_dir.mkdir(parents=True, exist_ok=True)

    canais_alvo = [canal_id] if canal_id else list(ROTEIROS_SEMANA.keys())

    print(f"\n🎬  Gerando {len(canais_alvo)} roteiro(s)...\n")

    arquivos = []
    for cid in canais_alvo:
        roteiro = gerar_roteiro_json(cid)
        nome_arquivo = f"short_{cid}_{roteiro['semana']}.json"
        caminho = output_dir / nome_arquivo
        caminho.write_text(
            json.dumps(roteiro, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        arquivos.append(caminho)
        print(f"  ✅ {CANAIS[cid]['nome']:22} → {nome_arquivo}")

    return arquivos


def gerar_script_agendamento(output_dir: Path = None):
    """Gera script de agendamento com as datas exatas desta semana."""
    if output_dir is None:
        output_dir = ROOT / "outputs" / "shorts_semana"
    output_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    semana = now.strftime("%Y-W%V")

    # Calcular próximas datas de publicação
    from datetime import timedelta
    hoje = now.date()
    dia_semana_hoje = hoje.weekday()  # 0=Seg, 6=Dom

    agenda_dias = {0: "S001", 1: "S003", 2: "S002", 3: "S004", 4: "S005"}

    agendamentos = []
    for offset in range(7):
        data = hoje + timedelta(days=offset)
        dow = data.weekday()
        if dow in agenda_dias:
            cid = agenda_dias[dow]
            canal = CANAIS[cid]
            roteiro = ROTEIROS_SEMANA[cid]
            agendamentos.append({
                "data": data.isoformat(),
                "horario": "17:00 BRT (20:00 UTC)",
                "canal_id": cid,
                "canal": canal["nome"],
                "titulo": roteiro["titulo"],
                "hashtags": canal["hashtags"],
            })

    agenda_path = output_dir / f"agenda_semana_{semana}.json"
    agenda_data = {
        "semana": semana,
        "gerado_em": now.isoformat(),
        "agendamentos": agendamentos,
        "total": len(agendamentos),
        "meta": "3–5 Shorts/semana por canal",
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }

    agenda_path.write_text(
        json.dumps(agenda_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n📅  Agenda salva: {agenda_path.name}")
    print(f"    {len(agendamentos)} publicações programadas para esta semana\n")

    for ag in agendamentos:
        print(f"  {ag['data']} │ {ag['canal']:22} │ {ag['horario']}")
        print(f"              │ \"{ag['titulo'][:45]}...\"")
        print()

    return agenda_path


def main():
    parser = argparse.ArgumentParser(
        description="DARK SHORTS FACTORY — Produção Semanal"
    )
    parser.add_argument("--canal", choices=list(CANAIS.keys()), help="Produzir apenas 1 canal")
    parser.add_argument("--apenas-roteiros", action="store_true", help="Só gera os JSONs de roteiro")
    parser.add_argument("--calendario", action="store_true", help="Exibe o calendário da semana")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   DARK STUDIO AAA v1.4.0 — DARK SHORTS FACTORY      ║")
    print("║   9 Agentes Especialistas Evocados                   ║")
    print("║   ai_disclosure: Produzido com DARK STUDIO AAA       ║")
    print("╚══════════════════════════════════════════════════════╝")

    if args.calendario:
        imprimir_calendario()
        return

    imprimir_calendario()

    # Gerar roteiros
    output_dir = ROOT / "outputs" / "shorts_semana"
    arquivos = produzir_roteiros(args.canal, output_dir)

    if not args.apenas_roteiros:
        gerar_script_agendamento(output_dir)

    print("═" * 60)
    print(f"  ✅ DARK SHORTS FACTORY — {len(arquivos)} roteiro(s) prontos")
    print(f"  📁 Pasta: {output_dir}")
    print("  Próximo: publicar os Shorts no horário agendado")
    print("═" * 60)
    print()


if __name__ == "__main__":
    main()
