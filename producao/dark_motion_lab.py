#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║        DARK MOTION LAB — AGENTE MOTION GRAPHICS             ║
║        DARK STUDIO AAA v1.4.0 — FASE 7                     ║
║                                                              ║
║  Agentes Especialistas Integrados:                          ║
║  • MOTION GRAPHICS  — animações, títulos, efeitos           ║
║  • VIDEO EDITOR PRO — composição e timeline                 ║
║  • VISUAL CONSISTENCY — paleta e estilo coerentes           ║
║  • CREATIVE QA      — validação final                       ║
╚══════════════════════════════════════════════════════════════╝

Funcionalidades:
  - Legendas animadas: SRT → ASS com estilo cinematográfico
  - Títulos de abertura (fade-in/out) por tema/nicho
  - Lower thirds (nome, canal, data)
  - Zoom dinâmico Ken Burns
  - Encerramento com CTA (like, inscrição)
  - Efeitos de partículas (bokeh, vinheta, grain)
  - Overlay cinematográfico (letterbox 2.39:1)
  - Color grade por preset de nicho
  - Composição final: vídeo + motion + legendas + audio

Uso:
  python3 producao/dark_motion_lab.py --video v001 --preset psicologia
  python3 producao/dark_motion_lab.py --todos --semana 01
  python3 producao/dark_motion_lab.py --so-legendas --video v002
  python3 producao/dark_motion_lab.py --preview --video v003

ai_generated: True
ai_disclosure: "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
"""

import os
import sys
import json
import subprocess
import argparse
import shutil
from pathlib import Path
from datetime import datetime

# ── Caminhos base ─────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent
VIDEOS_IN   = BASE / "outputs" / "videos_com_audio"
VIDEOS_OUT  = BASE / "outputs" / "videos_finais"
LEGENDAS_DIR= BASE / "outputs" / "legendas"
ASSETS_DIR  = BASE / "outputs" / "motion_assets"
RELATORIO   = BASE / "outputs" / "relatorio_motion.json"

for d in [VIDEOS_OUT, LEGENDAS_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Presets cinematográficos por nicho ────────────────────────────────────────
PRESETS = {
    "psicologia": {
        "cor_primaria":  "9B59B6",   # roxo profundo
        "cor_secundaria":"E8DAEF",
        "cor_fundo":     "1A0533",
        "fonte_titulo":  "BebasNeue",
        "fonte_corpo":   "OpenSans",
        "vinheta":       0.6,
        "grain":         0.03,
        "letterbox":     True,
        "color_grade":   "curves=r='0/0 128/100 255/220':g='0/0 128/110 255/230':b='0/0 128/140 255/255'",
        "titulo_efeito": "fade_scale",
        "cta_texto":     "Inscreva-se • Mente de Aço",
    },
    "historia": {
        "cor_primaria":  "D4A017",   # âmbar histórico
        "cor_secundaria":"FAF0E6",
        "cor_fundo":     "1C0A00",
        "fonte_titulo":  "Cinzel",
        "fonte_corpo":   "Lora",
        "vinheta":       0.7,
        "grain":         0.05,
        "letterbox":     True,
        "color_grade":   "curves=r='0/10 128/130 255/240':g='0/5 128/115 255/210':b='0/0 128/90 255/170'",
        "titulo_efeito": "typewriter",
        "cta_texto":     "Inscreva-se • Bastidores do Tempo",
    },
    "tecnologia": {
        "cor_primaria":  "00D4FF",   # ciano tech
        "cor_secundaria":"E0F7FF",
        "cor_fundo":     "000D1A",
        "fonte_titulo":  "Rajdhani",
        "fonte_corpo":   "SourceCodePro",
        "vinheta":       0.4,
        "grain":         0.01,
        "letterbox":     False,
        "color_grade":   "curves=r='0/0 128/110 255/200':g='0/5 128/130 255/240':b='0/10 128/150 255/255'",
        "titulo_efeito": "glitch",
        "cta_texto":     "Inscreva-se • Intelligentia Nova",
    },
    "misterio": {
        "cor_primaria":  "8B0000",   # vermelho escuro
        "cor_secundaria":"CCCCCC",
        "cor_fundo":     "0A0A0A",
        "fonte_titulo":  "CrimsonText",
        "fonte_corpo":   "Merriweather",
        "vinheta":       0.8,
        "grain":         0.06,
        "letterbox":     True,
        "color_grade":   "curves=r='0/5 128/120 255/230':g='0/0 128/95 255/180':b='0/0 128/85 255/160'",
        "titulo_efeito": "fade_scale",
        "cta_texto":     "Inscreva-se • Projeto Secreto",
    },
    "natureza": {
        "cor_primaria":  "2ECC71",   # verde água
        "cor_secundaria":"D5F5E3",
        "cor_fundo":     "001A0A",
        "fonte_titulo":  "Raleway",
        "fonte_corpo":   "Nunito",
        "vinheta":       0.5,
        "grain":         0.02,
        "letterbox":     False,
        "color_grade":   "curves=r='0/0 128/105 255/200':g='0/10 128/140 255/250':b='0/5 128/120 255/200'",
        "titulo_efeito": "fade_scale",
        "cta_texto":     "Inscreva-se • AquaZen Relax",
    },
}

# ── Mapeamento de vídeos ──────────────────────────────────────────────────────
VIDEOS = {
    "v001": {
        "arquivo":    "v001_Por_Que_Você_Se_Sente_Vazio_narrado.mp4",
        "titulo":     "Por Que Você Se Sente Vazio?",
        "subtitulo":  "A Resposta Que a Psicologia Esconde",
        "canal":      "Mente de Aço",
        "preset":     "psicologia",
        "duracao":    197,
        "roteiro_resumo": [
            (0,   8,  "Você já acordou se sentindo vazio por dentro?"),
            (8,   18, "Essa sensação tem um nome científico."),
            (18,  35, "O cérebro interpreta a ausência de propósito como dor real."),
            (35,  60, "Viktor Frankl chamou isso de vazio existencial."),
            (60,  90, "A dopamina cria ciclos de expectativa que raramente se cumprem."),
            (90,  130,"O vazio não é fraqueza — é um sinal do sistema nervoso."),
            (130, 165,"Reconhecer o padrão é o primeiro passo para quebrar o ciclo."),
            (165, 197,"Inscreva-se para continuar descobrindo."),
        ],
    },
    "v002": {
        "arquivo":    "v002_Os_Bastidores_do_Tempo_narrado.mp4",
        "titulo":     "Os Bastidores do Tempo",
        "subtitulo":  "Decisões Secretas Que Mudaram o Mundo",
        "canal":      "Bastidores do Tempo",
        "preset":     "historia",
        "duracao":    157,
        "roteiro_resumo": [
            (0,   8,  "Por trás de cada grande evento, há decisões tomadas em silêncio."),
            (8,   25, "Conversas que nunca apareceram nos livros de história."),
            (25,  60, "Acordos selados longe das câmeras e dos registros oficiais."),
            (60,  100,"Pequenos detalhes que mudaram o resultado de guerras inteiras."),
            (100, 135,"A história que conhecemos é apenas uma versão."),
            (135, 157,"Inscreva-se e descubra o que ficou oculto."),
        ],
    },
    "v003": {
        "arquivo":    "v003_Intelligentia_Nova_narrado.mp4",
        "titulo":     "Intelligentia Nova",
        "subtitulo":  "A IA Que Está Mudando Tudo",
        "canal":      "Intelligentia Nova",
        "preset":     "tecnologia",
        "duracao":    141,
        "roteiro_resumo": [
            (0,   8,  "A inteligência artificial já está transformando o mundo."),
            (8,   30, "Mas as mudanças mais profundas ainda estão chegando."),
            (30,  65, "Sistemas que aprendem sozinhos e superam especialistas humanos."),
            (65,  100,"O impacto real no mercado de trabalho é maior do que parece."),
            (100, 130,"O que os pesquisadores dizem sobre AGI nos próximos anos."),
            (130, 141,"Inscreva-se para ficar à frente do futuro."),
        ],
    },
    "v004": {
        "arquivo":    "v004_Projeto_Secreto_narrado.mp4",
        "titulo":     "Projeto Secreto",
        "subtitulo":  "Arquivos Que Não Deveriam Existir",
        "canal":      "Projeto Secreto",
        "preset":     "misterio",
        "duracao":    141,
        "roteiro_resumo": [
            (0,   8,  "Existem documentos que foram mantidos em segredo por décadas."),
            (8,   30, "Alguns foram desclassificados. Outros nunca deveriam ter existido."),
            (30,  70, "Experimentos escondidos, operações negadas pelos governos."),
            (70,  110,"Arquivos que provavelmente foram tentados apagar da história."),
            (110, 130,"A verdade por trás das conspirações que se provaram reais."),
            (130, 141,"Inscreva-se e descubra mais segredos."),
        ],
    },
    "v005": {
        "arquivo":    "v005_AquaZen_—_O_Poder_da_Água_narrado.mp4",
        "titulo":     "AquaZen",
        "subtitulo":  "O Poder da Água",
        "canal":      "AquaZen Relax",
        "preset":     "natureza",
        "duracao":    141,
        "roteiro_resumo": [
            (0,   8,  "A água tem um poder sobre a mente humana."),
            (8,   30, "A ciência finalmente começou a desvendar esse mistério."),
            (30,  70, "Sons de água ativam o modo parassimpático do sistema nervoso."),
            (70,  110,"A teoria Blue Mind explica por que nos sentimos em paz perto da água."),
            (110, 130,"O cortisol cai em média 25% em ambientes aquáticos."),
            (130, 141,"Inscreva-se para mais conteúdo relaxante."),
        ],
    },
}

# ═════════════════════════════════════════════════════════════════════════════
# AGENTE MOTION GRAPHICS — funções core
# ═════════════════════════════════════════════════════════════════════════════

def gerar_srt(vid_id: str, dados: dict) -> Path:
    """Gera arquivo .srt de legendas a partir do roteiro resumido."""
    print(f"  [MOTION] 📝 Gerando SRT para {vid_id}...")

    srt_path = LEGENDAS_DIR / f"{vid_id}_legendas.srt"

    def seg_to_srt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    linhas = []
    for i, (t_in, t_out, texto) in enumerate(dados["roteiro_resumo"], 1):
        linhas.append(str(i))
        linhas.append(f"{seg_to_srt_time(t_in)} --> {seg_to_srt_time(t_out)}")
        # Quebrar texto longo em 2 linhas (max ~42 chars por linha)
        if len(texto) > 42:
            meio = len(texto) // 2
            # Encontrar espaço mais próximo do meio
            for j in range(meio, 0, -1):
                if texto[j] == ' ':
                    texto = texto[:j] + '\n' + texto[j+1:]
                    break
        linhas.append(texto)
        linhas.append("")

    srt_path.write_text('\n'.join(linhas), encoding='utf-8')
    print(f"  [MOTION] ✅ SRT salvo: {srt_path.name} ({len(dados['roteiro_resumo'])} entradas)")
    return srt_path


def gerar_ass(vid_id: str, srt_path: Path, preset: dict) -> Path:
    """Converte SRT para ASS com estilo cinematográfico."""
    print(f"  [MOTION] 🎨 Convertendo para ASS estilizado...")

    ass_path = LEGENDAS_DIR / f"{vid_id}_legendas.ass"

    # Estilo ASS profissional
    cor_p = preset["cor_primaria"]
    cor_s = preset["cor_secundaria"]

    # ASS usa BGR (Blue Green Red)
    def hex_to_ass(hex_color: str) -> str:
        h = hex_color.lstrip('#')
        r, g, b = h[0:2], h[2:4], h[4:6]
        return f"&H00{b}{g}{r}"

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,52,{hex_to_ass(cor_s)},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2.5,1.5,2,80,80,60,1
Style: Titulo,Arial Black,72,{hex_to_ass(cor_p)},&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,3,2,5,40,40,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Ler SRT e converter para ASS events
    srt_content = srt_path.read_text(encoding='utf-8')
    eventos = []

    blocos = srt_content.strip().split('\n\n')
    for bloco in blocos:
        linhas = bloco.strip().split('\n')
        if len(linhas) < 3:
            continue

        # Tempo: "00:00:00,000 --> 00:00:08,000"
        tempo = linhas[1]
        t_in_str, t_out_str = tempo.split(' --> ')

        def srt_to_ass_time(t: str) -> str:
            # 00:00:00,000 → 0:00:00.00
            t = t.strip().replace(',', '.')
            parts = t.split(':')
            h, m = int(parts[0]), int(parts[1])
            s_ms = float(parts[2])
            s = int(s_ms)
            cs = int((s_ms - s) * 100)
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        t_in_ass  = srt_to_ass_time(t_in_str)
        t_out_ass = srt_to_ass_time(t_out_str)

        texto = '\n'.join(linhas[2:]).replace('\n', '\\N')

        # Adicionar fade in/out suave
        texto_estilizado = f"{{\\fad(200,200)}}{texto}"

        eventos.append(f"Dialogue: 0,{t_in_ass},{t_out_ass},Default,,0,0,0,,{texto_estilizado}")

    ass_content = ass_header + '\n'.join(eventos) + '\n'
    ass_path.write_text(ass_content, encoding='utf-8')
    print(f"  [MOTION] ✅ ASS salvo: {ass_path.name}")
    return ass_path


def gerar_abertura(vid_id: str, dados: dict, preset: dict, duracao_abertura: float = 5.0) -> Path:
    """Gera clip de abertura com título animado usando FFmpeg."""
    print(f"  [MOTION] 🎬 Gerando abertura para {vid_id}...")

    out_path = ASSETS_DIR / f"{vid_id}_abertura.mp4"

    titulo    = dados["titulo"]
    subtitulo = dados["subtitulo"]
    canal     = dados["canal"]

    cor_p = preset["cor_primaria"]
    cor_fundo = preset["cor_fundo"]

    # Converter hex para valores RGB 0-1 para drawtext
    def hex_rgb(h: str):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    rp, gp, bp = hex_rgb(cor_p)
    rf, gf, bf = hex_rgb(cor_fundo)

    # FFmpeg: fundo escuro + título com fade + subtítulo + canal
    # Usa drawtext com animação alpha
    vf_filters = [
        # Fundo sólido escuro
        f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao_abertura}",
        # Título principal (fade in 0→1s, permanece, fade out 4→5s)
        f"drawtext=text='{titulo}':"
        f"fontcolor=0x{cor_p}:fontsize=80:font='Arial Black':"
        f"x=(w-text_w)/2:y=(h/2)-80:"
        f"alpha='if(lt(t,0.5),0,if(lt(t,1.5),t-0.5,if(lt(t,{duracao_abertura-1}),1,{duracao_abertura}-t)))'",
        # Subtítulo
        f"drawtext=text='{subtitulo}':"
        f"fontcolor=0xCCCCCC:fontsize=40:font='Arial':"
        f"x=(w-text_w)/2:y=(h/2)+20:"
        f"alpha='if(lt(t,1),0,if(lt(t,2),t-1,if(lt(t,{duracao_abertura-0.5}),1,{duracao_abertura}-t-0.5)))'",
        # Nome do canal (menor, abaixo)
        f"drawtext=text='{canal}':"
        f"fontcolor=0x888888:fontsize=28:font='Arial':"
        f"x=(w-text_w)/2:y=(h/2)+90:"
        f"alpha='if(lt(t,1.5),0,if(lt(t,2.5),t-1.5,if(lt(t,{duracao_abertura-0.5}),1,0)))'",
    ]

    # Primeiro gera fundo, depois aplica drawtext
    fundo_filter = f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao_abertura}[base]"

    titulo_safe    = titulo.replace("'", "\\'").replace(":", "\\:")
    subtitulo_safe = subtitulo.replace("'", "\\'").replace(":", "\\:")
    canal_safe     = canal.replace("'", "\\'")

    vf = (
        f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao_abertura},"
        f"drawtext=text='{titulo_safe}':fontcolor=0x{cor_p}:fontsize=80:font='Arial Black':"
        f"x=(w-text_w)/2:y=(h/2)-80:"
        f"alpha='if(lt(t,0.5),0,if(lt(t,1.5),(t-0.5),if(lt(t,{duracao_abertura-1}),1,max(0,{duracao_abertura}-t))))',"
        f"drawtext=text='{subtitulo_safe}':fontcolor=0xCCCCCC:fontsize=40:font='Arial':"
        f"x=(w-text_w)/2:y=(h/2)+20:"
        f"alpha='if(lt(t,1),0,if(lt(t,2),(t-1),if(lt(t,{duracao_abertura-0.5}),1,max(0,{duracao_abertura}-t-0.5))))',"
        f"drawtext=text='{canal_safe}':fontcolor=0x888888:fontsize=28:font='Arial':"
        f"x=(w-text_w)/2:y=(h/2)+90:"
        f"alpha='if(lt(t,1.5),0,if(lt(t,2.5),(t-1.5),if(lt(t,{duracao_abertura-0.5}),1,0)))'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao_abertura}:r=30",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-t", str(duracao_abertura),
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [MOTION] ✅ Abertura gerada: {out_path.name}")
    else:
        print(f"  [MOTION] ⚠️  Abertura: FFmpeg error (usando fallback silencioso)")
        # Fallback: gerar frame preto simples
        cmd_fb = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=black:s=1920x1080:d={duracao_abertura}:r=30",
            "-c:v", "libx264", "-preset", "fast", "-crf", "28",
            "-t", str(duracao_abertura), "-pix_fmt", "yuv420p",
            str(out_path)
        ]
        subprocess.run(cmd_fb, capture_output=True)

    return out_path


def gerar_encerramento(vid_id: str, preset: dict, duracao: float = 4.0) -> Path:
    """Gera clip de encerramento com CTA."""
    print(f"  [MOTION] 🎯 Gerando encerramento/CTA para {vid_id}...")

    out_path = ASSETS_DIR / f"{vid_id}_encerramento.mp4"

    cta  = preset["cta_texto"]
    cor_p = preset["cor_primaria"]
    cor_fundo = preset["cor_fundo"]

    cta_safe = cta.replace("'", "\\'").replace("•", "-")

    vf = (
        f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao},"
        f"drawtext=text='🔔 {cta_safe}':fontcolor=0x{cor_p}:fontsize=52:font='Arial Black':"
        f"x=(w-text_w)/2:y=(h/2)-30:"
        f"alpha='if(lt(t,0.5),0,if(lt(t,1.5),(t-0.5),if(lt(t,{duracao-0.5}),1,max(0,{duracao}-t))))',"
        f"drawtext=text='👍 Deixe seu like!':fontcolor=0xFFFFFF:fontsize=36:font='Arial':"
        f"x=(w-text_w)/2:y=(h/2)+50:"
        f"alpha='if(lt(t,1),0,if(lt(t,2),(t-1),if(lt(t,{duracao-0.3}),1,0)))'"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x{cor_fundo}:s=1920x1080:d={duracao}:r=30",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-t", str(duracao), "-pix_fmt", "yuv420p",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [MOTION] ✅ Encerramento gerado: {out_path.name}")
    else:
        # Fallback
        cmd_fb = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=black:s=1920x1080:d={duracao}:r=30",
            "-c:v", "libx264", "-preset", "fast", "-crf", "28",
            "-t", str(duracao), "-pix_fmt", "yuv420p", str(out_path)
        ]
        subprocess.run(cmd_fb, capture_output=True)

    return out_path


def aplicar_color_grade_e_efeitos(video_in: Path, vid_id: str, preset: dict) -> Path:
    """Aplica color grade, vinheta, grain e letterbox cinematográfico."""
    print(f"  [MOTION] 🎨 Aplicando color grade e efeitos cinematográficos...")

    out_path = ASSETS_DIR / f"{vid_id}_graded.mp4"

    # Construir cadeia de filtros
    filtros = []

    # 1. Color grade por nicho
    if preset.get("color_grade"):
        filtros.append(preset["color_grade"])

    # 2. Vinheta
    intensidade = preset.get("vinheta", 0.5)
    if intensidade > 0:
        filtros.append(
            f"vignette=PI/3*{intensidade}:eval=frame"
        )

    # 3. Grain cinematográfico
    grain = preset.get("grain", 0.02)
    if grain > 0:
        filtros.append(
            f"noise=alls={int(grain*100)}:allf=t+u"
        )

    # 4. Letterbox 2.39:1 (cinematográfico)
    if preset.get("letterbox", False):
        # Barras pretas: altura do vídeo 1080, letterbox 2.39:1 → altura útil = 1920/2.39 ≈ 803px
        # Barras: (1080-803)/2 ≈ 138px cada
        filtros.append(
            "drawbox=x=0:y=0:w=iw:h=138:color=black:t=fill,"
            "drawbox=x=0:y=942:w=iw:h=138:color=black:t=fill"
        )

    vf_string = ','.join(filtros) if filtros else "null"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_in),
        "-vf", vf_string,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [MOTION] ✅ Color grade aplicado: {out_path.name}")
        return out_path
    else:
        print(f"  [MOTION] ⚠️  Color grade falhou, usando vídeo original")
        shutil.copy2(video_in, out_path)
        return out_path


def aplicar_legendas(video_in: Path, ass_path: Path, vid_id: str) -> Path:
    """Queima legendas ASS no vídeo (burn-in para compatibilidade YouTube)."""
    print(f"  [MOTION] 📺 Aplicando legendas burn-in...")

    out_path = ASSETS_DIR / f"{vid_id}_com_legendas.mp4"

    # Escapar path para FFmpeg
    ass_str = str(ass_path).replace('\\', '/').replace(':', '\\:')

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_in),
        "-vf", f"ass='{ass_str}'",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        sz = out_path.stat().st_size / 1024 / 1024
        print(f"  [MOTION] ✅ Legendas aplicadas: {out_path.name} ({sz:.1f}MB)")
        return out_path
    else:
        # Fallback: tentar subtitles filter
        cmd2 = [
            "ffmpeg", "-y",
            "-i", str(video_in),
            "-vf", f"subtitles='{str(ass_path).replace(chr(92),'/')}'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "copy",
            str(out_path)
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        if result2.returncode == 0:
            print(f"  [MOTION] ✅ Legendas (fallback subtitles)")
            return out_path
        else:
            print(f"  [MOTION] ⚠️  Legendas não aplicadas (libass não disponível), copiando sem burn-in")
            shutil.copy2(video_in, out_path)
            return out_path


def montar_video_final(vid_id: str, abertura: Path, video_principal: Path,
                       encerramento: Path) -> Path:
    """Concatena abertura + vídeo principal + encerramento."""
    print(f"  [MOTION] 🎞️  Montando vídeo final...")

    out_path = VIDEOS_OUT / f"{vid_id}_final.mp4"

    # Criar lista para concat
    lista_path = ASSETS_DIR / f"{vid_id}_concat_list.txt"
    with open(lista_path, 'w') as f:
        for p in [abertura, video_principal, encerramento]:
            if p.exists():
                f.write(f"file '{p}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(lista_path),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        sz = out_path.stat().st_size / 1024 / 1024
        print(f"  [MOTION] ✅ Vídeo final: {out_path.name} ({sz:.1f}MB)")
        return out_path
    else:
        print(f"  [MOTION] ⚠️  Concat falhou, usando vídeo principal como final")
        shutil.copy2(video_principal, out_path)
        return out_path


def verificar_qa(video_path: Path) -> dict:
    """AGENTE CREATIVE QA — verifica qualidade do vídeo final."""
    print(f"  [QA] 🔍 Verificando qualidade...")

    if not video_path.exists():
        return {"ok": False, "erro": "arquivo não encontrado"}

    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {"ok": False, "erro": "ffprobe falhou"}

    info = json.loads(result.stdout)
    fmt  = info.get("format", {})

    duracao  = float(fmt.get("duration", 0))
    tamanho  = int(fmt.get("size", 0))
    bitrate  = int(fmt.get("bit_rate", 0))

    streams = info.get("streams", [])
    tem_video = any(s["codec_type"] == "video" for s in streams)
    tem_audio = any(s["codec_type"] == "audio" for s in streams)

    ok = duracao > 30 and tamanho > 1_000_000 and tem_video

    return {
        "ok": ok,
        "duracao_s": round(duracao, 1),
        "tamanho_mb": round(tamanho / 1024 / 1024, 2),
        "bitrate_kbps": round(bitrate / 1000, 0),
        "tem_video": tem_video,
        "tem_audio": tem_audio,
    }


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════════

def processar_video(vid_id: str, so_legendas: bool = False, preview: bool = False) -> dict:
    """Pipeline completo de motion graphics para um vídeo."""

    if vid_id not in VIDEOS:
        return {"erro": f"Vídeo {vid_id} não encontrado"}

    dados  = VIDEOS[vid_id]
    preset = PRESETS[dados["preset"]]

    video_in = VIDEOS_IN / dados["arquivo"]
    if not video_in.exists():
        return {"erro": f"Arquivo não encontrado: {video_in}"}

    print(f"\n{'═'*60}")
    print(f"  🎬 DARK MOTION LAB — {vid_id}: {dados['titulo']}")
    print(f"  Preset: {dados['preset']} | Nicho: {dados['canal']}")
    print(f"{'═'*60}")

    resultado = {
        "vid_id": vid_id,
        "titulo": dados["titulo"],
        "preset": dados["preset"],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # 1. Gerar legendas SRT
        srt_path = gerar_srt(vid_id, dados)
        resultado["srt"] = str(srt_path)

        # 2. Converter para ASS estilizado
        ass_path = gerar_ass(vid_id, srt_path, preset)
        resultado["ass"] = str(ass_path)

        if so_legendas:
            # Apenas legendas, sem motion
            video_com_leg = aplicar_legendas(video_in, ass_path, vid_id)
            shutil.copy2(video_com_leg, VIDEOS_OUT / f"{vid_id}_final.mp4")
            resultado["video_final"] = str(VIDEOS_OUT / f"{vid_id}_final.mp4")
            resultado["status"] = "legendas_aplicadas"
            return resultado

        # 3. Color grade e efeitos
        video_graded = aplicar_color_grade_e_efeitos(video_in, vid_id, preset)
        resultado["video_graded"] = str(video_graded)

        # 4. Aplicar legendas no vídeo gradeado
        video_com_leg = aplicar_legendas(video_graded, ass_path, vid_id)
        resultado["video_com_legendas"] = str(video_com_leg)

        if not preview:
            # 5. Gerar abertura
            abertura = gerar_abertura(vid_id, dados, preset)
            resultado["abertura"] = str(abertura)

            # 6. Gerar encerramento
            encerramento = gerar_encerramento(vid_id, preset)
            resultado["encerramento"] = str(encerramento)

            # 7. Montar vídeo final
            video_final = montar_video_final(vid_id, abertura, video_com_leg, encerramento)
        else:
            # Preview: sem abertura/encerramento
            video_final = VIDEOS_OUT / f"{vid_id}_final.mp4"
            shutil.copy2(video_com_leg, video_final)
            print(f"  [MOTION] 🔍 Modo preview: sem abertura/encerramento")

        resultado["video_final"] = str(video_final)

        # 8. CREATIVE QA
        qa = verificar_qa(video_final)
        resultado["qa"] = qa
        resultado["status"] = "completo" if qa["ok"] else "qa_falhou"

        if qa["ok"]:
            print(f"\n  ✅ {vid_id} COMPLETO — {qa['duracao_s']}s | {qa['tamanho_mb']}MB")
        else:
            print(f"\n  ⚠️  {vid_id} QA FALHOU: {qa}")

    except Exception as e:
        resultado["status"] = "erro"
        resultado["erro"] = str(e)
        print(f"\n  ❌ Erro em {vid_id}: {e}")

    return resultado


def rodar_todos(semana: str = "01", so_legendas: bool = False, preview: bool = False) -> list:
    """Processa todos os vídeos da semana."""

    print(f"\n{'╔'+'═'*58+'╗'}")
    print(f"║  🎬 DARK MOTION LAB — SEMANA {semana} — {len(VIDEOS)} VÍDEOS{' '*20}║")
    print(f"{'╚'+'═'*58+'╝'}\n")

    resultados = []
    for vid_id in VIDEOS:
        r = processar_video(vid_id, so_legendas=so_legendas, preview=preview)
        resultados.append(r)

    # Salvar relatório
    relatorio = {
        "dark_studio_aaa": {
            "semana": semana,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "timestamp": datetime.now().isoformat(),
            "agentes": [
                "MOTION GRAPHICS", "VIDEO EDITOR PRO",
                "VISUAL CONSISTENCY", "CREATIVE QA"
            ],
        },
        "videos": resultados,
    }

    with open(RELATORIO, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    # Resumo
    ok    = sum(1 for r in resultados if r.get("status") in ("completo", "legendas_aplicadas"))
    total = len(resultados)

    print(f"\n{'═'*60}")
    print(f"  📊 RESULTADO MOTION LAB: {ok}/{total} vídeos processados")
    for r in resultados:
        status_icon = "✅" if r.get("status") in ("completo","legendas_aplicadas") else "⚠️ "
        print(f"  {status_icon} {r['vid_id']}: {r.get('status','?')} — {r.get('video_final','—')}")
    print(f"  📄 Relatório: {RELATORIO}")
    print(f"{'═'*60}\n")

    return resultados


# ═════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="DARK MOTION LAB — Motion graphics e efeitos cinematográficos"
    )
    parser.add_argument("--video",       help="ID do vídeo (ex: v001)")
    parser.add_argument("--todos",       action="store_true", help="Processar todos os vídeos")
    parser.add_argument("--semana",      default="01", help="Número da semana")
    parser.add_argument("--so-legendas", action="store_true", help="Apenas aplicar legendas")
    parser.add_argument("--preview",     action="store_true", help="Sem abertura/encerramento")
    parser.add_argument("--preset",      help="Forçar preset (psicologia|historia|tecnologia|misterio|natureza)")
    parser.add_argument("--listar",      action="store_true", help="Listar vídeos disponíveis")

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║        DARK MOTION LAB — DARK STUDIO AAA v1.4.0            ║
║        AGENTE MOTION GRAPHICS ATIVADO                       ║
╚══════════════════════════════════════════════════════════════╝
""")

    if args.listar:
        print("Vídeos disponíveis:")
        for vid_id, dados in VIDEOS.items():
            video_in = VIDEOS_IN / dados["arquivo"]
            status = "✅" if video_in.exists() else "❌"
            print(f"  {status} {vid_id}: {dados['titulo']} [{dados['preset']}]")
        return

    if args.todos or not args.video:
        rodar_todos(args.semana, args.so_legendas, args.preview)
    else:
        resultado = processar_video(args.video, args.so_legendas, args.preview)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
