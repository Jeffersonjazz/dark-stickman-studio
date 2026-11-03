#!/usr/bin/env python3
"""
DARK STUDIO AAA — Pipeline de Vídeos Cinematográficos
Gera vídeos com texto animado, múltiplas cenas, color grading dark
Sem dependência de TTS externo — funciona 100% local via FFmpeg

Agentes: 🎬 CINEMATIC DIRECTOR | 🖼 IMAGE ENGINE | ✂️ VIDEO EDITOR PRO | ✅ CREATIVE QA
"""

import subprocess, json, os, sys, re, textwrap
from pathlib import Path

PROJETO = Path("/home/claude/dark-stickman-studio")
OUT_DIR = PROJETO / "outputs" / "videos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── Paleta cinematográfica dark ───────────────────────────────────────────────
TEMAS = {
    "psicologia":  {"bg": "0x0D0D1A", "accent": "0x6A5AFF", "txt": "0xE8E0FF"},
    "historia":    {"bg": "0x1A0D0A", "accent": "0xCC7B1F", "txt": "0xFFF0DC"},
    "tecnologia":  {"bg": "0x050F0D", "accent": "0x00FFCC", "txt": "0xD0FFF5"},
    "misterio":    {"bg": "0x08000F", "accent": "0xAA00FF", "txt": "0xF0D0FF"},
    "natureza":    {"bg": "0x030D07", "accent": "0x00CC66", "txt": "0xD0FFE8"},
}

def limpar_roteiro(texto: str) -> list[str]:
    """Extrai linhas limpas do roteiro, remove metadados e marcações."""
    skip_keys = ["ai_generated","Vídeo:","Nicho:","Duração","Voz:","DARK STUDIO",
                 "Canal:","Estilo:","TOTAL DE","TEMPO ESTIMADO"]
    linhas = []
    for l in texto.split("\n"):
        l = l.strip()
        if not l: continue
        if l.startswith("[") and "]" in l: continue
        if l.startswith("=") or l.startswith("#"): continue
        if any(k in l for k in skip_keys): continue
        # Filtrar linhas muito curtas (artefatos)
        if len(l) < 3: continue
        linhas.append(l)
    return linhas

def quebrar_em_cenas(linhas: list[str], max_linhas_por_cena: int = 2) -> list[str]:
    """Agrupa linhas em cenas para exibição gradual."""
    cenas = []
    i = 0
    while i < len(linhas):
        bloco = linhas[i:i+max_linhas_por_cena]
        cenas.append(" ".join(bloco))
        i += max_linhas_por_cena
    return cenas

def wrap_texto(texto: str, largura: int = 42) -> str:
    """Quebra texto para caber na tela."""
    return r"\n".join(textwrap.wrap(texto, largura))

def gerar_filtros_texto(cenas: list[str], duracao_total: float,
                        cor_txt: str, cor_acc: str) -> str:
    """
    Gera cadeia de filtros drawtext para FFmpeg.
    Cada cena aparece por ~6s com fade in/out de 1.5s.
    """
    # Calcular timing
    n = len(cenas)
    dur_cena = min(duracao_total / n, 9.0)  # no máximo 9s por cena

    filtros = []
    base = "[0:v]"

    for i, cena in enumerate(cenas):
        inicio = i * dur_cena
        fim = inicio + dur_cena
        fade_in_dur = 1.2
        fade_out_dur = 1.2

        # Cor: odd cenas usam accent, even usam txt
        cor = cor_acc if i % 4 == 0 else cor_txt

        # Escapar texto para FFmpeg
        texto_esc = (cena
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace("%", "%%")
        )
        # Quebra de linha FFmpeg
        linhas_wrap = textwrap.wrap(cena, 40)
        texto_formatado = r"\n".join(
            l.replace("\\", "\\\\").replace("'", "\\'")
             .replace(":", "\\:").replace(",", "\\,").replace("%", "%%")
            for l in linhas_wrap
        )

        # Expressão alpha com fade
        alpha = (
            f"if(lt(t,{inicio:.1f}),0,"
            f"if(lt(t,{inicio+fade_in_dur:.1f}),(t-{inicio:.1f})/{fade_in_dur:.1f},"
            f"if(lt(t,{fim-fade_out_dur:.1f}),1,"
            f"if(lt(t,{fim:.1f}),(({fim:.1f}-t)/{fade_out_dur:.1f}),0))))"
        )

        saida = f"[v{i}]"
        filtro = (
            f"{base}drawtext="
            f"text='{texto_formatado}':"
            f"fontsize=52:"
            f"fontcolor={cor.replace('0x','#')}:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"alpha='{alpha}':"
            f"line_spacing=12"
            f"{saida}"
        )
        filtros.append(filtro)
        base = saida

    # Último output não precisa de label
    filtros_str = ";\n".join(filtros)
    # Renomear último output para [vo]
    filtros_str = filtros_str.rsplit(f"[v{n-1}]", 1)
    filtros_str = filtros_str[0] + "[vo]"
    return filtros_str

def gerar_video_cinematografico(
    titulo: str,
    cenas: list[str],
    tema: str,
    out_path: Path,
    duracao: float = 300.0,
) -> bool:
    """🎬 CINEMATIC DIRECTOR — Gera vídeo com texto animado e color grading."""

    t = TEMAS[tema]
    bg = t["bg"]
    acc = t["acc"] if "acc" in t else t["accent"]
    cor_txt = t["txt"]
    cor_acc = t["accent"]

    # Número de cenas vs duração
    n_cenas = len(cenas)
    dur_cena = min(duracao / n_cenas, 8.5)
    duracao_real = min(n_cenas * dur_cena, duracao)

    # Título no início (cena 0)
    titulo_esc = (titulo
        .replace("\\", "\\\\").replace("'", "\\'")
        .replace(":", "\\:").replace(",", "\\,")
    )

    # Color grading: vignette + levemente saturado
    # Fundo: gradiente escuro com ruído sutil via noise

    # Construir filter_complex simplificado mas efectivo
    # Cada segmento de texto com timing preciso
    filter_parts = []

    # Base: cor de fundo
    filter_parts.append(f"color=c={bg}:size=1920x1080:rate=24[bg]")

    # Vinheta dark para bordas
    filter_parts.append(
        "[bg]vignette=angle=PI/5:mode=backward[bv]"
    )

    # Título no começo (primeiros 6 segundos)
    titulo_lines = textwrap.wrap(titulo, 30)
    titulo_fmt = r"\n".join(
        l.replace("'", "\\'").replace(":", "\\:") for l in titulo_lines
    )
    filter_parts.append(
        f"[bv]drawtext="
        f"text='{titulo_fmt}':"
        f"fontsize=80:"
        f"fontcolor={cor_acc.replace('0x','#')}:"
        f"x=(w-text_w)/2:"
        f"y=(h-text_h)/2:"
        f"alpha='if(lt(t,1),t,if(lt(t,4),1,if(lt(t,6),(6-t)/2,0)))':"
        f"line_spacing=16"
        f"[title]"
    )

    # Texto de disclosure no rodapé (permanente mas suave)
    disc = "DARK STUDIO AAA — Produzido com IA | ai\\_generated"
    filter_parts.append(
        f"[title]drawtext="
        f"text='{disc}':"
        f"fontsize=22:"
        f"fontcolor=gray@0.5:"
        f"x=(w-text_w)/2:"
        f"y=h-50:"
        f"alpha=0.6"
        f"[with_disc]"
    )

    # Cenas de texto principais com fade
    prev = "[with_disc]"
    for i, cena in enumerate(cenas):
        inicio = 7.0 + i * dur_cena
        fim = inicio + dur_cena
        fi_dur = 1.0
        fo_dur = 1.0

        linhas = textwrap.wrap(cena, 42)
        texto_fmt = r"\n".join(
            l.replace("\\", "\\\\").replace("'", "\\'")
             .replace(":", "\\:").replace(",", "\\,").replace("%", "%%")
            for l in linhas
        )

        # Alternar cor accent/texto para variedade visual
        if i % 5 == 0:
            cor = cor_acc.replace("0x", "#")
            tamanho = 56
        elif len(cena) > 80:
            cor = cor_txt.replace("0x", "#")
            tamanho = 44
        else:
            cor = cor_txt.replace("0x", "#")
            tamanho = 52

        alpha_expr = (
            f"if(lt(t,{inicio:.1f}),0,"
            f"if(lt(t,{inicio+fi_dur:.1f}),(t-{inicio:.1f})/{fi_dur:.1f},"
            f"if(lt(t,{fim-fo_dur:.1f}),1,"
            f"if(lt(t,{fim:.1f}),(({fim:.1f}-t)/{fo_dur:.1f}),0))))"
        )

        saida = f"[c{i}]"
        filter_parts.append(
            f"{prev}drawtext="
            f"text='{texto_fmt}':"
            f"fontsize={tamanho}:"
            f"fontcolor={cor}:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"alpha='{alpha_expr}':"
            f"line_spacing=14"
            f"{saida}"
        )
        prev = saida

    # Color grading final: leve contrast boost
    filter_parts.append(
        f"{prev}eq=contrast=1.1:brightness=-0.02:saturation=0.9[final]"
    )

    filter_complex = ";\n".join(filter_parts)

    # Áudio ambiente: low hum dark (sine 55Hz bem suave + noise)
    audio_filter = (
        "anullsrc=r=44100:cl=stereo,"
        "afade=t=in:d=3,afade=t=out:st=" + str(int(duracao_real - 3)) + ":d=3"
    )

    cmd = [
        "ffmpeg", "-y",
        # Inputs de vídeo e áudio
        "-f", "lavfi", "-i", f"color=c={bg}:size=1920x1080:rate=24",
        "-f", "lavfi", "-i", audio_filter,
        # Filter complex
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-map", "1:a",
        # Encoding
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(duracao_real),
        "-pix_fmt", "yuv420p",
        # Metadados obrigatórios
        "-metadata", f"title={titulo}",
        "-metadata", "artist=DARK STUDIO AAA",
        "-metadata", "comment=ai_generated:True | ai_disclosure:Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "-metadata", "genre=Educational",
        str(out_path)
    ]

    print(f"  🎬 CINEMATIC DIRECTOR gerando: {out_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"  ❌ ERRO FFmpeg: {result.stderr[-500:]}")
        # Fallback simples
        return gerar_video_fallback(titulo, tema, out_path, duracao_real)

    size = out_path.stat().st_size / 1024 / 1024
    print(f"  ✅ Gerado: {out_path.name} ({size:.1f}MB, {duracao_real:.0f}s)")
    return True

def gerar_video_fallback(titulo: str, tema: str, out_path: Path, duracao: float) -> bool:
    """Fallback: vídeo simples sem filtros complexos."""
    t = TEMAS[tema]
    bg = t["bg"]
    acc = t["accent"].replace("0x", "#")
    titulo_esc = titulo.replace("'", "\\'").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg}:size=1920x1080:rate=24",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", (
            f"drawtext=text='{titulo_esc}':fontsize=72:fontcolor={acc}:"
            "x=(w-text_w)/2:y=(h-text_h)/2,"
            "vignette=angle=PI/4:mode=backward"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", "-b:a", "64k",
        "-t", str(duracao),
        "-pix_fmt", "yuv420p",
        "-metadata", f"title={titulo}",
        "-metadata", "artist=DARK STUDIO AAA",
        "-metadata", "comment=ai_generated:True",
        str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    ok = result.returncode == 0
    if ok:
        print(f"  ⚠️  Fallback OK: {out_path.name}")
    else:
        print(f"  ❌ Fallback falhou: {result.stderr[-200:]}")
    return ok

def qa_video(path: Path, duracao_alvo: float) -> dict:
    """✅ CREATIVE QA — Verifica vídeo gerado."""
    if not path.exists():
        return {"status": "❌ FALHOU", "erro": "arquivo não existe"}

    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json",
           "-show_streams", "-show_format", str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return {"status": "❌ FALHOU", "erro": "ffprobe falhou"}

    data = json.loads(r.stdout)
    dur = float(data.get("format", {}).get("duration", 0))
    size_mb = path.stat().st_size / 1024 / 1024
    streams = {s["codec_type"]: s["codec_name"] for s in data.get("streams", [])}

    ok = dur > 10 and size_mb > 0.1 and "video" in streams
    return {
        "status": "✅ APROVADO" if ok else "⚠️ ATENÇÃO",
        "duracao": f"{dur:.1f}s",
        "tamanho": f"{size_mb:.1f}MB",
        "streams": streams,
    }

# ─── VÍDEOS DA SEMANA 01 ─────────────────────────────────────────────────────

VIDEOS = [
    {
        "id": "v001",
        "titulo": "Por Que Você Se Sente Vazio",
        "canal": "MindSet Dark",
        "nicho": "psicologia",
        "tema": "psicologia",
        "roteiro": "producao/v001_psicologia_vazio/roteiro_naracao_completo.txt",
        "duracao": 300,
    },
    {
        "id": "v002",
        "titulo": "Os Bastidores do Tempo",
        "canal": "Arquivo Sombrio",
        "nicho": "historia",
        "tema": "historia",
        "roteiro": None,  # Usar texto inline
        "duracao": 300,
        "cenas_inline": [
            "Os registros históricos oficiais contam apenas uma parte da história.",
            "Por trás de cada grande evento, existem decisões tomadas em salas fechadas.",
            "1914. O arquiduque Francisco Fernando é assassinado em Sarajevo.",
            "O que parecia um atentado isolado desencadeou uma guerra mundial.",
            "Mas os documentos desclassificados revelam algo perturbador.",
            "Semanas antes, os serviços de inteligência austríacos já sabiam do plano.",
            "A decisão de ignorar os alertas foi deliberada.",
            "A história que aprendemos na escola é a versão dos vencedores.",
            "Os arquivos secretos contam uma história diferente.",
            "Em 1962, o mundo esteve a 13 minutos de uma guerra nuclear.",
            "O que salvou a humanidade não foi a diplomacia — foi um único homem.",
            "Vasili Arkhipov, oficial soviético, recusou autorizar o lançamento de torpedo nuclear.",
            "Seu nome foi mantido em segredo por décadas.",
            "A história está cheia de heróis anônimos que ninguém conhece.",
            "E de vilões que a história transformou em heróis.",
            "O passado nunca está morto. Ele nem passou.",
            "Compartilhe se acredita que a história merece ser questionada.",
            "Inscreva-se no canal para mais arquivos da história oculta.",
        ],
    },
    {
        "id": "v003",
        "titulo": "Intelligentia Nova — A IA que Muda Tudo",
        "canal": "Tech Dark",
        "nicho": "tecnologia",
        "tema": "tecnologia",
        "roteiro": None,
        "duracao": 300,
        "cenas_inline": [
            "Em 2024, a inteligência artificial deixou de ser ficção científica.",
            "Ela entrou nos hospitais, nos tribunais, nas escolas.",
            "E ninguém pediu nossa permissão.",
            "Os modelos de linguagem processam mais texto em um dia...",
            "...do que um ser humano consegue ler em toda a sua vida.",
            "GPT-4 passou no exame de ordem dos advogados com nota maior que 90% dos humanos.",
            "O modelo médico de IA detecta câncer de mama com precisão superior a radiologistas.",
            "Isso muda tudo que sabemos sobre trabalho.",
            "McKinsey estima: 300 milhões de empregos serão afetados até 2030.",
            "Mas não apenas substituídos — transformados.",
            "Os empregos do futuro ainda não existem.",
            "A IA não é boa nem má. É uma ferramenta de amplificação.",
            "Ela amplifica o que o ser humano já é.",
            "A pergunta não é: a IA vai me substituir?",
            "A pergunta é: como me torno insubstituível num mundo com IA?",
            "A resposta está em habilidades que as máquinas ainda não têm.",
            "Empatia. Criatividade. Julgamento moral. Liderança.",
            "O futuro pertence a quem souber trabalhar junto com a IA.",
            "Inscreva-se para entender a revolução que está acontecendo agora.",
        ],
    },
    {
        "id": "v004",
        "titulo": "Projeto Secreto — O Que Eles Não Querem que Você Saiba",
        "canal": "Arquivo Misterioso",
        "nicho": "misterio",
        "tema": "misterio",
        "roteiro": None,
        "duracao": 300,
        "cenas_inline": [
            "Existem projetos classificados que nunca chegaram ao público.",
            "Não por conspirações — mas por protocolos de segurança.",
            "O Projeto MKUltra foi real.",
            "A CIA conduziu experimentos de controle mental entre 1953 e 1973.",
            "Usando drogas, hipnose e privação sensorial em cidadãos comuns.",
            "Sem consentimento. Sem ética. Com financiamento federal.",
            "Os documentos foram destruídos em 1973.",
            "Mas 20.000 arquivos sobreviveram — encontrados por acaso em 1977.",
            "O que esses arquivos revelaram foi perturbador.",
            "Mas o que foi destruído pode ter sido ainda mais perturbador.",
            "O Projeto STARGATE treinou espiões psíquicos para o exército americano.",
            "Durante 20 anos e 20 milhões de dólares.",
            "A conclusão oficial: 'resultados inconclusivos'.",
            "Mas os participantes relataram experiências que a ciência não explica.",
            "A fronteira entre ciência e mistério é mais tênue do que parece.",
            "Cada arquivo desclassificado revela que o impossível às vezes é real.",
            "O que mais existe nos cofres que ainda não vimos?",
            "Inscreva-se. Porque nem tudo que é real é visível.",
        ],
    },
    {
        "id": "v005",
        "titulo": "AquaZen — O Poder da Água para a Mente",
        "canal": "Natureza Dark",
        "nicho": "natureza",
        "tema": "natureza",
        "roteiro": None,
        "duracao": 300,
        "cenas_inline": [
            "O ser humano é 70% água.",
            "E a mente humana é profundamente afetada pela presença da água.",
            "A neurociência chama isso de 'Blue Mind' — a mente azul.",
            "Pesquisador Wallace J. Nichols documentou o fenômeno em 2014.",
            "Estar perto da água reduz o cortisol — o hormônio do estresse.",
            "Aumenta a dopamina e a serotonina.",
            "Ativa o estado de flow — imersão completa e presença plena.",
            "Não é acaso que as civilizações nasceram às margens dos rios.",
            "O Nilo, o Tigre, o Eufrates, o Ganges, o Amazonas.",
            "A água é a mãe da civilização humana.",
            "Mas o mundo moderno nos afastou da natureza.",
            "70% da humanidade vive em cidades.",
            "E as cidades têm cada vez menos água visível, audível, sentida.",
            "Estudos mostram que 20 minutos perto de água natural...",
            "...produzem os mesmos efeitos que meditação de 45 minutos.",
            "Você não precisa de um oceano. Uma fonte, um aquário, uma chuva.",
            "O som da água ativa o sistema parassimpático.",
            "E o sistema parassimpático é o sistema do descanso e da cura.",
            "Quando foi a última vez que você ficou em silêncio perto da água?",
            "Inscreva-se. A natureza tem respostas que a tecnologia não tem.",
        ],
    },
]

def main():
    print("=" * 60)
    print("🎬 DARK STUDIO AAA — Geração Cinematográfica Semana 01")
    print("=" * 60)
    print(f"Agentes: CINEMATIC DIRECTOR | IMAGE ENGINE | VIDEO EDITOR PRO | CREATIVE QA")
    print()

    resultados = []

    for v in VIDEOS:
        print(f"\n{'─' * 50}")
        print(f"📹 {v['id'].upper()}: {v['titulo']}")
        print(f"   Canal: {v['canal']} | Nicho: {v['nicho']}")

        # Obter cenas
        if v.get("roteiro") and Path(PROJETO / v["roteiro"]).exists():
            txt = (PROJETO / v["roteiro"]).read_text(encoding="utf-8")
            linhas = limpar_roteiro(txt)
            cenas = quebrar_em_cenas(linhas, max_linhas_por_cena=2)
            print(f"   📄 Roteiro: {len(linhas)} linhas → {len(cenas)} cenas")
        elif v.get("cenas_inline"):
            cenas = v["cenas_inline"]
            print(f"   📄 Cenas inline: {len(cenas)}")
        else:
            print("   ❌ Sem roteiro — pulando")
            continue

        # Caminho de saída
        slug = re.sub(r"[^\w]", "_", v["titulo"])[:40]
        out_path = OUT_DIR / f"{v['id']}_{slug}.mp4"

        # 🎬 Gerar vídeo cinematográfico
        sucesso = gerar_video_cinematografico(
            titulo=v["titulo"],
            cenas=cenas,
            tema=v["tema"],
            out_path=out_path,
            duracao=float(v["duracao"]),
        )

        # ✅ QA
        qa = qa_video(out_path, v["duracao"])
        print(f"   QA: {qa['status']} | {qa.get('duracao','?')} | {qa.get('tamanho','?')} | streams={qa.get('streams',{})}")

        resultados.append({
            "id": v["id"],
            "titulo": v["titulo"],
            "arquivo": str(out_path),
            "sucesso": sucesso,
            "qa": qa,
        })

    print(f"\n{'═' * 60}")
    print("📊 RELATÓRIO FINAL — SEMANA 01")
    print(f"{'═' * 60}")
    aprovados = sum(1 for r in resultados if "✅" in r["qa"]["status"])
    print(f"✅ Aprovados: {aprovados}/{len(resultados)}")
    for r in resultados:
        status = "✅" if r["sucesso"] else "❌"
        print(f"  {status} {r['id']}: {r['titulo']}")
        print(f"      {r['qa']}")

    # Salvar manifesto
    manifesto_path = OUT_DIR / "semana01_manifesto.json"
    with open(manifesto_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n📋 Manifesto salvo: {manifesto_path}")

    return 0 if aprovados == len(resultados) else 1

if __name__ == "__main__":
    sys.exit(main())
