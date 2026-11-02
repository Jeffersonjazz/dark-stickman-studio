#!/usr/bin/env python3
"""
DARK YOUTUBE CLI — Interface de linha de comando
DARK STUDIO AAA — Publicação direta no YouTube
"""

import argparse
import json
import sys
from pathlib import Path

# Garante importação do módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dark_youtube_publisher.auth.oauth_manager import (
    authorize_channel,
    list_authorized_channels,
    revoke_channel,
)
from dark_youtube_publisher.core.batch_publisher import (
    DarkBatchPublisher,
    PublishJob,
    DARK_CHANNELS,
)

DEFAULT_SECRETS = str(Path.home() / ".dark_studio" / "client_secrets.json")

BATCH2_JOBS = [
    {
        "channel_key": "mente_de_aco",
        "title": "Por Que Você Procrastina? #Shorts",
        "description": (
            "Você sabe por que procrastina?\n\n"
            "Neste vídeo exploramos a psicologia por trás da procrastinação "
            "e como vencê-la com disciplina e foco.\n\n"
            "🧠 Mente de Aço — Mentalidade e Motivação\n\n"
            "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB\n"
            "Conteúdo produzido com auxílio de inteligência artificial."
        ),
        "tags": ["procrastinação", "foco", "produtividade"],
    },
    {
        "channel_key": "esquina_do_medo",
        "title": "O Trem que Entrou no Túnel e Nunca Saiu #Shorts",
        "description": (
            "Uma das histórias mais perturbadoras do mundo ferroviário...\n\n"
            "O que aconteceu com o trem que entrou no túnel e desapareceu?\n\n"
            "👻 Esquina do Medo — Histórias de Terror\n\n"
            "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB\n"
            "Conteúdo produzido com auxílio de inteligência artificial."
        ),
        "tags": ["terror", "mistério", "histórias assustadoras"],
    },
    {
        "channel_key": "intelligentia_nova",
        "title": "A IA que Aprendeu a Mentir #Shorts",
        "description": (
            "Uma IA foi treinada para ser honesta. Mas aprendeu a mentir...\n\n"
            "O que isso significa para o futuro da inteligência artificial?\n\n"
            "🤖 Intelligentia Nova — Tecnologia e Inteligência Artificial\n\n"
            "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB\n"
            "Conteúdo produzido com auxílio de inteligência artificial."
        ),
        "tags": ["inteligência artificial", "IA", "tecnologia"],
    },
    {
        "channel_key": "projeto_secreto",
        "title": "O Projeto Secreto que Mudou o Mundo #Shorts",
        "description": (
            "Arquivos desclassificados revelam um projeto que foi mantido em segredo por décadas...\n\n"
            "🔍 Projeto Secreto — Conspirações, Área 51 e Segredos\n\n"
            "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB\n"
            "Conteúdo produzido com auxílio de inteligência artificial."
        ),
        "tags": ["conspiração", "segredos", "arquivos secretos"],
    },
    {
        "channel_key": "aquazen_relax",
        "title": "Os Lagos que Mudam de Cor ✨ Natureza em 4K #Shorts",
        "description": (
            "Lagoas hipnóticas que mudam de cor com as estações...\n\n"
            "Sons da natureza para relaxar e meditar.\n\n"
            "🌊 AquaZen Relax — Natureza e Sons Relaxantes\n\n"
            "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB\n"
            "Imagens produzidas com auxílio de inteligência artificial."
        ),
        "tags": ["natureza", "relaxamento", "ASMR", "meditação"],
    },
]


def cmd_auth(args):
    ch = DARK_CHANNELS.get(args.channel)
    if not ch:
        print(f"❌ Canal desconhecido: {args.channel}")
        print("Canais disponíveis:", ", ".join(DARK_CHANNELS.keys()))
        return
    authorize_channel(ch["label"], args.secrets)
    print(f"✅ Canal '{ch['label']}' autorizado!")


def cmd_list(args):
    print("\n📺 CANAIS DARK STUDIO AAA\n")
    authorized = list_authorized_channels()
    for key, ch in DARK_CHANNELS.items():
        label = ch["label"]
        safe = label.lower().replace(" ", "_").replace("/", "_")
        is_auth = any(safe in a.lower() for a in authorized)
        status = "✅" if is_auth else "🔒"
        print(f"  {status} [{key}] {label} — {ch['niche']}")


def cmd_publish(args):
    publisher = DarkBatchPublisher(args.secrets)
    description = args.description or f"Vídeo publicado via DARK STUDIO AAA.\n\nProduzido com DARK STUDIO AAA — DARK CREATIVE LAB\nConteúdo produzido com auxílio de inteligência artificial."
    tags = args.tags.split(",") if args.tags else []
    job = PublishJob(
        channel_key=args.channel,
        video_url=args.url,
        title=args.title,
        description=description,
        extra_tags=tags,
        thumbnail_url=args.thumbnail,
        is_short=not args.not_short,
        privacy=args.privacy,
    )
    results = publisher.publish_batch([job])
    r = results[0]
    if r.success:
        print(f"\n✅ Publicado: {r.youtube_url}")
    else:
        print(f"\n❌ Erro: {r.error}")


def cmd_batch2(args):
    """Publica o Batch 2 completo — 5 Shorts nos canais corretos."""
    print("\n🚀 DARK STUDIO AAA — BATCH 2")
    print("Publicando 5 Shorts nos canais corretos...\n")

    if not args.urls:
        print("⚠️  Informe as URLs dos vídeos GCS com --urls URL1,URL2,URL3,URL4,URL5")
        return

    urls = args.urls.split(",")
    if len(urls) != 5:
        print(f"❌ Esperado 5 URLs, recebido {len(urls)}")
        return

    publisher = DarkBatchPublisher(args.secrets)
    jobs = []
    for i, job_data in enumerate(BATCH2_JOBS):
        jobs.append(PublishJob(
            channel_key=job_data["channel_key"],
            video_url=urls[i],
            title=job_data["title"],
            description=job_data["description"],
            extra_tags=job_data["tags"],
            is_short=True,
            privacy="public",
        ))

    results = publisher.publish_batch(jobs, delay_between=15)
    print("\n" + "=" * 50)
    print("RESUMO BATCH 2")
    print("=" * 50)
    print(publisher.summary())


def cmd_revoke(args):
    ch = DARK_CHANNELS.get(args.channel)
    label = ch["label"] if ch else args.channel
    revoke_channel(label)
    print(f"🗑️  Token revogado: {label}")


def main():
    parser = argparse.ArgumentParser(
        description="DARK YOUTUBE CLI — DARK STUDIO AAA",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  dark-youtube list
  dark-youtube auth --channel intelligentia_nova
  dark-youtube publish --channel esquina_do_medo --url https://... --title "Meu Short"
  dark-youtube batch2 --urls url1,url2,url3,url4,url5
        """,
    )
    parser.add_argument(
        "--secrets",
        default=DEFAULT_SECRETS,
        help="Caminho para client_secrets.json",
    )
    sub = parser.add_subparsers(dest="command")

    # list
    sub.add_parser("list", help="Lista canais e status de autorização")

    # auth
    p_auth = sub.add_parser("auth", help="Autoriza um canal no YouTube")
    p_auth.add_argument("--channel", required=True, help="Chave do canal (ex: intelligentia_nova)")

    # publish
    p_pub = sub.add_parser("publish", help="Publica um vídeo")
    p_pub.add_argument("--channel", required=True)
    p_pub.add_argument("--url", required=True, help="URL do vídeo (GCS ou CDN)")
    p_pub.add_argument("--title", required=True)
    p_pub.add_argument("--description", default="")
    p_pub.add_argument("--tags", default="", help="Tags separadas por vírgula")
    p_pub.add_argument("--thumbnail", default=None)
    p_pub.add_argument("--privacy", default="public", choices=["public", "private", "unlisted"])
    p_pub.add_argument("--not-short", action="store_true", help="Vídeo longo (não Short)")

    # batch2
    p_b2 = sub.add_parser("batch2", help="Publica Batch 2 (5 Shorts pré-configurados)")
    p_b2.add_argument("--urls", required=True, help="5 URLs separadas por vírgula (na ordem do batch)")

    # revoke
    p_rev = sub.add_parser("revoke", help="Revoga token de um canal")
    p_rev.add_argument("--channel", required=True)

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "auth": cmd_auth,
        "publish": cmd_publish,
        "batch2": cmd_batch2,
        "revoke": cmd_revoke,
    }

    fn = commands.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
