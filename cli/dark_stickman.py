#!/usr/bin/env python3
"""
DARK STICKMAN STUDIO — CLI (Interface de Linha de Comando)
Produção de vídeos stickman via terminal.

Uso:
    dark-stickman produzir --canal psicologia --titulo "POR QUE PROCRASTINAMOS?"
    dark-stickman lote --canal psicologia --n 5
    dark-stickman thumbnail --canal psicologia --titulo "TÍTULO DO VÍDEO"
    dark-stickman status
    dark-stickman api

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Optional

# Adiciona o diretório raiz ao path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    TYPER_OK = True
except ImportError:
    TYPER_OK = False
    print("[ERRO] Instale: pip install typer rich")
    sys.exit(1)

app = typer.Typer(
    name="dark-stickman",
    help="🎬 DARK STICKMAN STUDIO — Pipeline de produção automatizada de vídeos YouTube",
    rich_markup_mode="rich",
    add_completion=False,
)
console = Console()

AI_DISCLOSURE = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
OUTPUT_ROOT = ROOT / "output"
CANAIS_DIR = ROOT / "config" / "canais"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _carregar_canal(nicho: str) -> dict:
    """Carrega config do canal pelo nicho."""
    for f in CANAIS_DIR.glob("canal_*.json"):
        try:
            cfg = json.loads(f.read_text(encoding="utf-8"))
            if cfg.get("nicho") == nicho:
                return cfg
        except Exception:
            pass
    # Fallback
    return {
        "nome": f"DARK STICKMAN — {nicho.upper()}",
        "nicho": nicho,
        "stickman_color": "#3B82F6",
        "stickman_seed": 42,
        "modelo_tts": "faber-medium",
        "velocidade_fala": 1.05,
        "watermark": True,
    }


def _roteiro_exemplo(titulo: str, nicho: str) -> dict:
    """Gera roteiro de exemplo para teste."""
    return {
        "titulo": titulo,
        "hook": f"O que você está prestes a descobrir vai mudar sua forma de pensar sobre {nicho}.",
        "cenas": [
            {
                "num": 1, "tipo": "hook", "duracao_s": 5,
                "stickman_acao": "olhando_camera",
                "narracao": f"Hoje vamos explorar um tema fascinante: {titulo}.",
                "fundo": "branco_minimalista",
            },
            {
                "num": 2, "tipo": "normal", "duracao_s": 8,
                "stickman_acao": "apontando",
                "narracao": "Este é um conteúdo produzido com inteligência artificial pelo DARK STUDIO.",
                "fundo": "azul_escuro",
            },
            {
                "num": 3, "tipo": "conclusao", "duracao_s": 6,
                "stickman_acao": "vitoria",
                "narracao": "Continue assistindo para saber mais!",
                "fundo": "branco_minimalista",
            },
        ],
        "cta": "Inscreva-se no canal para mais conteúdo!",
    }


def _banner():
    console.print(Panel.fit(
        "[bold blue]🎬 DARK STICKMAN STUDIO[/bold blue]\n"
        f"[dim]{AI_DISCLOSURE}[/dim]",
        border_style="blue",
    ))


# ─── Comando: produzir ────────────────────────────────────────────────────────

@app.command("produzir")
def produzir(
    canal: str = typer.Option(..., "--canal", "-c", help="Nicho do canal (psicologia, batalhas, etc.)"),
    titulo: str = typer.Option(..., "--titulo", "-t", help="Título do vídeo"),
    qualidade: str = typer.Option("medium_quality", "--qualidade", "-q",
                                   help="low_quality | medium_quality | high_quality"),
    formato: str = typer.Option("16:9", "--formato", "-f", help="16:9 | 9:16"),
    shorts: bool = typer.Option(False, "--shorts", help="Gerar versão Shorts (9:16)"),
    modo: str = typer.Option("stickman", "--modo", "-m",
                              help="stickman | realista — pipeline de produção"),
    trilha: Optional[str] = typer.Option(None, "--trilha", help="Trilha sonora de fundo (MP3/WAV)"),
    legendas: bool = typer.Option(True, "--legendas/--sem-legendas", help="Gerar legendas SRT"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Diretório de saída"),
    roteiro_json: Optional[str] = typer.Option(None, "--roteiro", "-r",
                                                 help="Caminho para arquivo JSON do roteiro"),
):
    """🎬 Produz um vídeo completo (stickman ou imagem realista)."""
    _banner()

    canal_cfg = _carregar_canal(canal)
    console.print(f"[green]✓[/green] Canal: [bold]{canal_cfg['nome']}[/bold]")

    # Carrega roteiro
    if roteiro_json:
        roteiro_path = Path(roteiro_json)
        if not roteiro_path.exists():
            console.print(f"[red]✗ Arquivo de roteiro não encontrado: {roteiro_json}[/red]")
            raise typer.Exit(1)
        roteiro = json.loads(roteiro_path.read_text(encoding="utf-8"))
        console.print(f"[green]✓[/green] Roteiro carregado: {roteiro.get('titulo', titulo)}")
    else:
        roteiro = _roteiro_exemplo(titulo, canal)
        console.print(f"[yellow]⚠[/yellow] Usando roteiro de exemplo para '{titulo}'")

    # Diretório de saída
    out_dir = Path(output) if output else OUTPUT_ROOT / canal_cfg["nome"].replace(" ", "_") / str(uuid.uuid4())[:8]
    out_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Saída: {out_dir}")

    # Pipeline
    console.print(f"\n[bold]🚀 Iniciando pipeline [{modo.upper()}]...[/bold]")

    fmt_map = {"16:9": "horizontal", "9:16": "vertical", "1:1": "quadrado"}
    fmt_real = fmt_map.get(formato, "horizontal")
    if shorts:
        fmt_real = "vertical"

    if modo == "realista":
        from pipeline.f02_imagem_realista import produzir_video_imagem_realista
        with console.status("[bold blue]Produzindo vídeo realista...[/bold blue]", spinner="dots"):
            resultado = produzir_video_imagem_realista(
                roteiro=roteiro,
                canal_config=canal_cfg,
                output_dir=out_dir,
                trilha_path=trilha,
                formato=fmt_real,
                incluir_legendas=legendas,
                verbose=False,
            )
        status_ok = resultado.get("status") in ("ok", "partial")
        video_key = "output_video"
        thumb_key = "output_thumbnail"
    else:
        from pipeline.f01_producao import produzir_video
        with console.status("[bold blue]Produzindo vídeo stickman...[/bold blue]", spinner="dots"):
            resultado = produzir_video(
                roteiro=roteiro,
                canal_config=canal_cfg,
                output_dir=out_dir,
                qualidade=qualidade,
                formato=formato,
                gerar_shorts=shorts,
            )
        status_ok = resultado.get("status") == "concluido"
        video_key = "output_path"
        thumb_key = "thumbnail_path"

    # Resultado
    if status_ok:
        console.print(f"\n[bold green]✅ Vídeo produzido com sucesso! (modo={modo})[/bold green]")
        console.print(f"  📹 Vídeo: [cyan]{resultado.get(video_key, 'N/A')}[/cyan]")
        console.print(f"  🖼  Thumbnail: [cyan]{resultado.get(thumb_key, 'N/A')}[/cyan]")
        if modo == "realista":
            console.print(f"  🎬 Cenas: {resultado.get('etapas', {}).get('imagens', {}).get('geradas', '?')}")
            console.print(f"  ⏱  Produção: {resultado.get('duracao_producao_s', 0):.1f}s")
        else:
            console.print(f"  ⏱  Duração: {resultado.get('duracao_s', 0):.1f}s")
        console.print(f"\n[dim]{AI_DISCLOSURE}[/dim]")
    else:
        console.print(f"\n[red]✗ Erro: {resultado.get('erro', resultado.get('etapas', {}))}[/red]")
        raise typer.Exit(1)


# ─── Comando: lote ────────────────────────────────────────────────────────────

@app.command("lote")
def lote(
    canal: str = typer.Option(..., "--canal", "-c", help="Nicho do canal"),
    n: int = typer.Option(3, "--n", help="Número de vídeos a produzir (1-20)"),
    roteiros_dir: Optional[str] = typer.Option(None, "--roteiros", help="Diretório com JSONs de roteiros"),
    qualidade: str = typer.Option("medium_quality", "--qualidade", "-q"),
):
    """📦 Produz múltiplos vídeos em lote."""
    _banner()

    canal_cfg = _carregar_canal(canal)
    console.print(f"[green]✓[/green] Canal: [bold]{canal_cfg['nome']}[/bold] | Vídeos: {n}")

    roteiros = []
    if roteiros_dir:
        p = Path(roteiros_dir)
        roteiros = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(p.glob("*.json"))[:n]]
        console.print(f"[green]✓[/green] {len(roteiros)} roteiros carregados de {roteiros_dir}")

    if not roteiros:
        roteiros = [_roteiro_exemplo(f"Vídeo {i+1}", canal) for i in range(min(n, 20))]
        console.print(f"[yellow]⚠[/yellow] Usando {len(roteiros)} roteiros de exemplo")

    from pipeline.f01_producao import produzir_lote as pl
    resultados = pl(roteiros, canal_cfg, OUTPUT_ROOT / canal_cfg["nome"].replace(" ", "_"), qualidade)

    # Tabela de resultados
    table = Table(title="Resultado do Lote")
    table.add_column("Vídeo", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Duração", style="yellow")
    table.add_column("Arquivo", style="dim")

    for i, r in enumerate(resultados, 1):
        status = "✅" if r.get("status") == "concluido" else "❌"
        dur = f"{r.get('duracao_s', 0):.0f}s"
        path = Path(r.get("output_path", "")).name if r.get("output_path") else "-"
        table.add_row(f"Vídeo {i}", status, dur, path)

    console.print(table)
    console.print(f"\n[dim]{AI_DISCLOSURE}[/dim]")


# ─── Comando: thumbnail ───────────────────────────────────────────────────────

@app.command("thumbnail")
def thumbnail(
    canal: str = typer.Option(..., "--canal", "-c"),
    titulo: str = typer.Option(..., "--titulo", "-t"),
    subtitulo: Optional[str] = typer.Option(None, "--subtitulo", "-s"),
    variacoes: int = typer.Option(1, "--variacoes", "-v", help="Número de variações A/B (1-3)"),
    output: Optional[str] = typer.Option(None, "--output", "-o"),
):
    """🖼  Gera thumbnail(s) para YouTube."""
    _banner()

    try:
        from core.thumbnail import gerar_thumbnail, gerar_variacao
    except ImportError:
        console.print("[red]✗ Pillow não instalado. Execute: pip install Pillow[/red]")
        raise typer.Exit(1)

    canal_cfg = _carregar_canal(canal)
    out_dir = Path(output) if output else OUTPUT_ROOT / "thumbnails" / canal_cfg["nome"].replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    with console.status("Gerando thumbnail..."):
        if variacoes == 1:
            out_path = out_dir / f"thumb_{uuid.uuid4().hex[:6]}.png"
            gerar_thumbnail(titulo, canal_cfg, out_path, subtitulo)
            paths = [out_path]
        else:
            paths = gerar_variacao(titulo, canal_cfg, out_dir, variacoes)

    for p in paths:
        if p and Path(p).exists():
            console.print(f"[green]✓[/green] {p}")

    console.print(f"\n[dim]{AI_DISCLOSURE}[/dim]")


# ─── Comando: status ──────────────────────────────────────────────────────────

@app.command("status")
def status():
    """📊 Mostra estatísticas de produção."""
    _banner()

    from core.ffmpeg_utils import check_ffmpeg
    from core.piper_tts import check_piper
    from core.manim_scene import check_manim

    table = Table(title="Status das Dependências")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", style="green")

    checks = [
        ("FFmpeg", check_ffmpeg()),
        ("Piper TTS", check_piper()),
        ("Manim CE", check_manim()),
    ]
    try:
        from PIL import Image
        checks.append(("Pillow", True))
    except ImportError:
        checks.append(("Pillow", False))

    try:
        import whisper
        checks.append(("Whisper", True))
    except ImportError:
        checks.append(("Whisper", False))

    for nome, ok in checks:
        table.add_row(nome, "✅ OK" if ok else "❌ Não encontrado")

    console.print(table)

    # Jobs
    db_path = ROOT / "db" / "dark_stickman.db"
    if db_path.exists():
        import sqlite3
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            cur.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            rows = cur.fetchall()
            conn.close()
            if rows:
                jtable = Table(title="Jobs de Produção")
                jtable.add_column("Status")
                jtable.add_column("Quantidade", justify="right")
                for r in rows:
                    jtable.add_row(r[0], str(r[1]))
                console.print(jtable)
        except Exception:
            pass

    console.print(f"\n[dim]{AI_DISCLOSURE}[/dim]")


# ─── Comando: api ─────────────────────────────────────────────────────────────

@app.command("api")
def api(
    porta: int = typer.Option(7870, "--porta", "-p", help="Porta da API"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host"),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload (desenvolvimento)"),
):
    """🌐 Inicia o servidor API REST para integração com DARK MANAGER."""
    _banner()
    try:
        import uvicorn
    except ImportError:
        console.print("[red]✗ uvicorn não instalado. Execute: pip install uvicorn[/red]")
        raise typer.Exit(1)

    console.print(f"[bold blue]🌐 API iniciando em http://{host}:{porta}[/bold blue]")
    console.print(f"[dim]Docs: http://localhost:{porta}/docs[/dim]\n")

    import uvicorn
    uvicorn.run("api.main:app", host=host, port=porta, reload=reload)


# ─── Comando: canais ──────────────────────────────────────────────────────────

@app.command("canais")
def canais():
    """📺 Lista os 12 canais configurados."""
    _banner()
    table = Table(title="Canais DARK STICKMAN STUDIO")
    table.add_column("#", style="dim")
    table.add_column("Nome", style="cyan")
    table.add_column("Nicho", style="yellow")
    table.add_column("Cor", style="magenta")
    table.add_column("Modelo TTS")

    for i, f in enumerate(sorted(CANAIS_DIR.glob("canal_*.json")), 1):
        try:
            cfg = json.loads(f.read_text(encoding="utf-8"))
            table.add_row(
                str(i),
                cfg.get("nome", "?"),
                cfg.get("nicho", "?"),
                cfg.get("stickman_color", "?"),
                cfg.get("modelo_tts", "?"),
            )
        except Exception:
            pass

    console.print(table)


# ─── Comando: banco ──────────────────────────────────────────────────────────

@app.command("banco")
def banco(
    acao: str = typer.Argument("listar", help="listar | criar | personagem | cenario | relatorio"),
    projeto: Optional[str] = typer.Option(None, "--projeto", "-p", help="ID do projeto"),
    titulo: Optional[str] = typer.Option(None, "--titulo", "-t"),
    nicho: Optional[str] = typer.Option(None, "--nicho", "-n"),
    nome: Optional[str] = typer.Option(None, "--nome", help="Nome do personagem ou cenário"),
    descricao: Optional[str] = typer.Option(None, "--descricao", "-d"),
    iluminacao: str = typer.Option("natural", "--iluminacao"),
    horario: str = typer.Option("dia", "--horario"),
    base_dir: Optional[str] = typer.Option(None, "--dir", help="Diretório base do banco visual"),
):
    """🎨 Gerencia banco de referências visuais por projeto (Fase 8)."""
    _banner()

    from core.visual_consistency import ProjetoVisualBank
    base = Path(base_dir) if base_dir else OUTPUT_ROOT / "_visual_bank"
    base.mkdir(parents=True, exist_ok=True)
    bank = ProjetoVisualBank(base)

    if acao == "listar":
        projetos = bank.listar_projetos()
        if not projetos:
            console.print("[yellow]Nenhum projeto no banco visual.[/yellow]")
        else:
            table = Table(title="Banco Visual — Projetos")
            table.add_column("ID", style="cyan")
            table.add_column("Título", style="bold")
            table.add_column("Nicho", style="yellow")
            table.add_column("Preset")
            table.add_column("Personagens", justify="right")
            table.add_column("Cenários", justify="right")
            table.add_column("Cenas", justify="right")
            for p in projetos:
                table.add_row(
                    p.get("projeto_id", "?"),
                    p.get("titulo", "?"),
                    p.get("nicho", "?"),
                    p.get("preset", "?"),
                    str(p.get("personagens", 0)),
                    str(p.get("cenarios", 0)),
                    str(p.get("cenas_registradas", 0)),
                )
            console.print(table)

    elif acao == "criar":
        if not projeto or not titulo or not nicho:
            console.print("[red]✗ --projeto, --titulo e --nicho são obrigatórios.[/red]")
            raise typer.Exit(1)
        dados = bank.criar_projeto(projeto, titulo, nicho, descricao=descricao or "")
        console.print(f"[green]✓[/green] Projeto criado: [bold]{projeto}[/bold] ({nicho})")
        console.print(f"  Paleta inicial: {dados.get('paleta', [])}")

    elif acao == "personagem":
        if not projeto or not nome or not descricao:
            console.print("[red]✗ --projeto, --nome e --descricao são obrigatórios.[/red]")
            raise typer.Exit(1)
        ok = bank.registrar_personagem(projeto, nome, descricao)
        if ok:
            console.print(f"[green]✓[/green] Personagem '{nome}' registrado em '{projeto}'.")
        else:
            console.print(f"[red]✗ Projeto '{projeto}' não encontrado. Use: banco criar[/red]")
            raise typer.Exit(1)

    elif acao == "cenario":
        if not projeto or not nome or not descricao:
            console.print("[red]✗ --projeto, --nome e --descricao são obrigatórios.[/red]")
            raise typer.Exit(1)
        ok = bank.registrar_cenario(projeto, nome, descricao, iluminacao=iluminacao, horario=horario)
        if ok:
            console.print(f"[green]✓[/green] Cenário '{nome}' registrado em '{projeto}'.")
        else:
            console.print(f"[red]✗ Projeto '{projeto}' não encontrado.[/red]")
            raise typer.Exit(1)

    elif acao == "relatorio":
        if not projeto:
            console.print("[red]✗ --projeto é obrigatório.[/red]")
            raise typer.Exit(1)
        rel = bank.exportar_relatorio(projeto)
        if "erro" in rel:
            console.print(f"[red]✗ {rel['erro']}[/red]")
            raise typer.Exit(1)
        console.print(Panel.fit(
            f"[bold]Projeto:[/bold] {rel['projeto']['titulo']}\n"
            f"[bold]Nicho:[/bold] {rel['projeto']['nicho']}\n"
            f"[bold]Preset:[/bold] {rel['projeto']['preset']}\n"
            f"[bold]Personagens:[/bold] {', '.join(rel['personagens']) or '(nenhum)'}\n"
            f"[bold]Cenários:[/bold]   {', '.join(rel['cenarios']) or '(nenhum)'}\n"
            f"[bold]Paleta:[/bold]     {' '.join(rel['paleta'])}\n"
            f"[bold]Imgs ref:[/bold]   {rel['imagens_referencia']}\n"
            f"[bold]Cenas prod.:[/bold]{rel['cenas_produzidas']}",
            title=f"[blue]Banco Visual — {projeto}[/blue]",
            border_style="blue",
        ))

    else:
        console.print(f"[red]✗ Ação desconhecida: {acao!r}[/red]")
        console.print("[dim]Ações: listar | criar | personagem | cenario | relatorio[/dim]")
        raise typer.Exit(1)

    console.print(f"\n[dim]{AI_DISCLOSURE}[/dim]")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
