#!/usr/bin/env python3
"""
DARK STUDIO AAA — Gerador Rápido v2
Gera vídeos por concatenação de segmentos curtos (~8s cada)
Sem filtros complexos — um drawtext por clip + concat

Agentes: 🎬 CINEMATIC DIRECTOR | ✂️ VIDEO EDITOR PRO | ✅ CREATIVE QA
"""

import subprocess, json, os, textwrap
from pathlib import Path

PROJETO = Path("/home/claude/dark-stickman-studio")
OUT_DIR = PROJETO / "outputs" / "videos"
TMP_DIR = PROJETO / "outputs" / "tmp_segs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

TEMAS = {
    "psicologia": {"bg": "0x0D0D1A", "accent": "6A5AFF", "txt": "E8E0FF"},
    "historia":   {"bg": "0x1A0D0A", "accent": "CC7B1F", "txt": "FFF0DC"},
    "tecnologia": {"bg": "0x050F0D", "accent": "00FFCC", "txt": "D0FFF5"},
    "misterio":   {"bg": "0x08000F", "accent": "AA00FF", "txt": "F0D0FF"},
    "natureza":   {"bg": "0x030D07", "accent": "00CC66", "txt": "D0FFE8"},
}

def gerar_segmento(texto: str, out: Path, bg: str, cor: str, dur: float = 8.0) -> bool:
    """Gera um clip de texto único com fade in/out."""
    linhas = textwrap.wrap(texto, 40)
    txt_fmt = r"\n".join(
        l.replace("\\","\\\\").replace("'","\\'")
         .replace(":","\\:").replace(",","\\,").replace("%","%%")
        for l in linhas
    )
    fontsize = 48 if len(texto) > 60 else 58

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg}:size=1920x1080:rate=24",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", (
            f"drawtext=text='{txt_fmt}':"
            f"fontsize={fontsize}:"
            f"fontcolor=#{cor}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"line_spacing=12:"
            f"alpha='if(lt(t,1),(t/1),if(lt(t,{dur-1:.1f}),1,({dur:.1f}-t)/1))',"
            "vignette=angle=PI/4:mode=backward"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "64k",
        "-t", str(dur), "-pix_fmt", "yuv420p",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=30)
    return r.returncode == 0

def gerar_titulo_seg(titulo: str, out: Path, bg: str, acc: str, dur: float = 5.0) -> bool:
    """Slide de título do vídeo."""
    linhas = textwrap.wrap(titulo, 28)
    txt_fmt = r"\n".join(
        l.replace("\\","\\\\").replace("'","\\'")
         .replace(":","\\:").replace(",","\\,")
        for l in linhas
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg}:size=1920x1080:rate=24",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-vf", (
            f"drawtext=text='{txt_fmt}':"
            f"fontsize=72:fontcolor=#{acc}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"line_spacing=16:"
            "alpha='if(lt(t,1.5),(t/1.5),if(lt(t,3.5),1,1))',"
            "vignette=angle=PI/3:mode=backward"
        ),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
        "-c:a", "aac", "-b:a", "64k",
        "-t", str(dur), "-pix_fmt", "yuv420p",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=20)
    return r.returncode == 0

def concat_segmentos(segs: list[Path], out: Path, titulo: str) -> bool:
    """Concatena segmentos via FFmpeg concat."""
    # Criar lista de arquivos
    lista_path = TMP_DIR / "concat_list.txt"
    with open(lista_path, "w") as f:
        for seg in segs:
            f.write(f"file '{seg.absolute()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(lista_path),
        "-c", "copy",
        "-metadata", f"title={titulo}",
        "-metadata", "artist=DARK STUDIO AAA",
        "-metadata", "comment=ai_generated:True | ai_disclosure:DARK STUDIO AAA — DARK CREATIVE LAB",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return r.returncode == 0

def processar_video(v: dict) -> dict:
    """Pipeline completo para um vídeo."""
    tema = TEMAS[v["tema"]]
    bg = tema["bg"]
    acc = tema["accent"]
    txt = tema["txt"]
    cenas = v["cenas"]

    print(f"\n  📹 {v['id']}: {v['titulo']}")
    print(f"     {len(cenas)} cenas → segmentos de ~8s cada")

    segs = []
    # Slide de título
    seg_titulo = TMP_DIR / f"{v['id']}_t00.mp4"
    if gerar_titulo_seg(v["titulo"], seg_titulo, bg, acc, dur=5.0):
        segs.append(seg_titulo)
        print(f"     ✓ Título")
    else:
        print(f"     ✗ Título falhou")

    # Segmentos de conteúdo
    for i, cena in enumerate(cenas):
        dur = 8.0
        seg = TMP_DIR / f"{v['id']}_c{i:02d}.mp4"
        # Alternar cor: destaque para cenas importantes
        cor = acc if i % 5 == 0 else txt
        ok = gerar_segmento(cena, seg, bg, cor, dur)
        if ok:
            segs.append(seg)
        else:
            print(f"     ✗ Cena {i} falhou")

    if not segs:
        return {"id": v["id"], "sucesso": False, "qa": {"status": "❌ sem segmentos"}}

    print(f"     ✓ {len(segs)} segmentos gerados — concatenando...")

    # Concatenar
    slug = v["titulo"].replace(" ", "_")[:40]
    out_path = OUT_DIR / f"{v['id']}_{slug}.mp4"
    ok = concat_segmentos(segs, out_path, v["titulo"])

    if ok:
        size = out_path.stat().st_size / 1024 / 1024
        # ffprobe
        r = subprocess.run(
            ["ffprobe","-v","quiet","-show_format","-print_format","json", str(out_path)],
            capture_output=True, text=True
        )
        dur = float(json.loads(r.stdout).get("format",{}).get("duration",0)) if r.returncode==0 else 0
        qa = {"status": "✅ APROVADO", "duracao": f"{dur:.0f}s", "tamanho": f"{size:.1f}MB"}
        print(f"     ✅ {out_path.name} — {dur:.0f}s | {size:.1f}MB")
    else:
        qa = {"status": "❌ concat falhou"}
        print(f"     ❌ Concatenação falhou")

    # Limpar segmentos temporários
    for seg in segs:
        try: seg.unlink()
        except: pass

    return {"id": v["id"], "titulo": v["titulo"], "arquivo": str(out_path) if ok else "", "sucesso": ok, "qa": qa}

# ─── DEFINIÇÃO DOS VÍDEOS ─────────────────────────────────────────────────────

VIDEOS = [
    {
        "id": "v001", "titulo": "Por Que Você Se Sente Vazio",
        "tema": "psicologia",
        "cenas": [
            "Você tem emprego. Tem família. Talvez até dinheiro.",
            "Mas existe um vazio... que nenhuma conquista consegue preencher.",
            "Esse sentimento tem um nome na psicologia.",
            "Em 1946, Viktor Frankl sobreviveu a campos de concentração nazistas.",
            "O que ele descobriu contradiz tudo que a sociedade nos ensina.",
            "Frankl percebeu: o ser humano não busca prazer. Ele busca sentido.",
            "Ele chamou isso de logoterapia — do grego logos: significado.",
            "Causa 1: a ausência de propósito.",
            "Trabalhamos para pagar contas. Consumimos para distrair. Vivemos no piloto automático.",
            "Causa 2: a desconexão social.",
            "Você pode estar rodeado de pessoas e ainda assim profundamente sozinho.",
            "Causa 3: a armadilha da comparação.",
            "Todos parecem mais felizes, mais realizados, mais completos do que você.",
            "A neurociência explica: o cérebro libera dopamina na antecipação, não na recompensa.",
            "Quando você conquista algo, a dopamina já foi embora.",
            "Harvard acompanhou 800 pessoas por 80 anos e chegou a uma conclusão surpreendente.",
            "O que mais prevê satisfação com a vida não é riqueza. Não é fama.",
            "São os relacionamentos de qualidade.",
            "Estratégia 1: cultive propósito além de você mesmo.",
            "Estratégia 2: invista em vínculos profundos, não em conexões superficiais.",
            "Estratégia 3: pratique presença — o antídoto da comparação é a gratidão.",
            "O vazio que você sente não é uma falha. É um sinal.",
            "A pergunta não é como eliminar o vazio — é o que ele está tentando te dizer.",
            "Compartilhe com quem precisa ouvir isso. Inscreva-se.",
        ],
    },
    {
        "id": "v002", "titulo": "Os Bastidores do Tempo",
        "tema": "historia",
        "cenas": [
            "Os registros históricos contam apenas uma parte da história.",
            "Por trás de cada grande evento, existem decisões em salas fechadas.",
            "1914. Francisco Fernando é assassinado em Sarajevo.",
            "O que parecia isolado desencadeou uma guerra mundial.",
            "Documentos desclassificados revelam: os austríacos já sabiam do plano.",
            "A decisão de ignorar os alertas foi deliberada.",
            "A história que aprendemos na escola é a versão dos vencedores.",
            "Em 1962, o mundo esteve a 13 minutos de uma guerra nuclear.",
            "O que salvou a humanidade não foi a diplomacia — foi um único homem.",
            "Vasili Arkhipov recusou autorizar o lançamento de torpedo nuclear.",
            "Seu nome foi mantido em segredo por décadas.",
            "A história está cheia de heróis anônimos que ninguém conhece.",
            "E de vilões que a história transformou em heróis.",
            "1986, Stanislav Petrov recebeu alerta de ataque nuclear americano.",
            "Os sistemas indicavam 5 mísseis em rota para Moscou.",
            "Petrov decidiu que era um erro de sistema. E estava certo.",
            "Ele não seguiu o protocolo. E salvou o mundo.",
            "O passado nunca está morto. Ele nem passou.",
            "Compartilhe se acredita que a história merece ser questionada.",
        ],
    },
    {
        "id": "v003", "titulo": "Intelligentia Nova",
        "tema": "tecnologia",
        "cenas": [
            "Em 2024, a inteligência artificial deixou de ser ficção científica.",
            "Ela entrou nos hospitais, nos tribunais, nas escolas.",
            "E ninguém pediu nossa permissão.",
            "Modelos de IA processam mais texto em um dia do que você leria na vida inteira.",
            "GPT-4 passou no exame da OAB com nota maior que 90% dos humanos.",
            "IA médica detecta câncer com precisão superior a radiologistas.",
            "McKinsey: 300 milhões de empregos afetados até 2030.",
            "Mas não apenas substituídos — transformados.",
            "Os empregos do futuro ainda não existem.",
            "A IA não é boa nem má. É uma ferramenta de amplificação.",
            "Ela amplifica o que o ser humano já é.",
            "A pergunta não é: a IA vai me substituir?",
            "A pergunta é: como me torno insubstituível num mundo com IA?",
            "Empatia. Criatividade. Julgamento moral. Liderança.",
            "Essas são habilidades que as máquinas ainda não têm.",
            "O futuro pertence a quem souber trabalhar junto com a IA.",
            "Inscreva-se para entender a revolução que está acontecendo agora.",
        ],
    },
    {
        "id": "v004", "titulo": "Projeto Secreto",
        "tema": "misterio",
        "cenas": [
            "Existem projetos classificados que nunca chegaram ao público.",
            "Não por conspirações — mas por protocolos de segurança.",
            "O Projeto MKUltra foi real.",
            "A CIA conduziu experimentos de controle mental entre 1953 e 1973.",
            "Usando drogas, hipnose e privação sensorial em cidadãos comuns.",
            "Sem consentimento. Sem ética. Com financiamento federal.",
            "Os documentos foram destruídos em 1973.",
            "Mas 20.000 arquivos sobreviveram — encontrados por acaso em 1977.",
            "O que eles revelaram foi perturbador.",
            "O Projeto STARGATE treinou espiões psíquicos para o exército americano.",
            "Durante 20 anos e 20 milhões de dólares.",
            "A conclusão oficial: resultados inconclusivos.",
            "Mas os participantes relataram experiências que a ciência não explica.",
            "A fronteira entre ciência e mistério é mais tênue do que parece.",
            "Cada arquivo desclassificado revela que o impossível às vezes é real.",
            "O que mais existe nos cofres que ainda não vimos?",
            "Inscreva-se. Porque nem tudo que é real é visível.",
        ],
    },
    {
        "id": "v005", "titulo": "AquaZen — O Poder da Água",
        "tema": "natureza",
        "cenas": [
            "O ser humano é 70% água.",
            "E a mente é profundamente afetada pela presença da água.",
            "A neurociência chama isso de Blue Mind — a mente azul.",
            "Estar perto da água reduz o cortisol — o hormônio do estresse.",
            "Aumenta dopamina e serotonina.",
            "Ativa o estado de flow — presença plena e imersão total.",
            "Não é acaso que as civilizações nasceram às margens dos rios.",
            "O Nilo, o Tigre, o Eufrates, o Ganges, o Amazonas.",
            "A água é a mãe da civilização humana.",
            "Mas o mundo moderno nos afastou da natureza.",
            "70% da humanidade vive em cidades com cada vez menos água.",
            "Estudos mostram: 20 minutos perto de água natural...",
            "...produzem o mesmo efeito que 45 minutos de meditação.",
            "O som da água ativa o sistema parassimpático.",
            "O sistema do descanso e da cura.",
            "Quando foi a última vez que você ficou em silêncio perto da água?",
            "A natureza tem respostas que a tecnologia não tem. Inscreva-se.",
        ],
    },
]

# ─── MAIN ─────────────────────────────────────────────────────────────────────

print("=" * 55)
print("🎬 DARK STUDIO AAA — Pipeline Semana 01 (v2 Rápido)")
print("=" * 55)

resultados = []
for v in VIDEOS:
    res = processar_video(v)
    resultados.append(res)

print(f"\n{'═' * 55}")
print("📊 RELATÓRIO FINAL")
aprovados = sum(1 for r in resultados if r["sucesso"])
print(f"✅ {aprovados}/{len(resultados)} vídeos aprovados")
for r in resultados:
    s = "✅" if r["sucesso"] else "❌"
    print(f"  {s} {r['id']}: {r.get('qa',{}).get('duracao','?')} | {r.get('qa',{}).get('tamanho','?')}")

# Manifesto
manifesto = OUT_DIR / "semana01_manifesto.json"
with open(manifesto, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)
print(f"\n📋 Manifesto: {manifesto}")
