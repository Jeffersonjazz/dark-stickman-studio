"""
DARK TUBE ENGINE — AGENTE CINEMATIC DIRECTOR v2.0
Direção de fotografia, composição, iluminação, enquadramentos e continuidade visual
Implementa planejamento multi-shot, geração de prompts visuais por cena e banco de referências

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import json
import os
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────
# PRESETS CINEMATOGRÁFICOS COMPLETOS (8 estilos)
# ─────────────────────────────────────────────────────────────
PRESETS_CINEMATOGRAFICOS: Dict[str, Dict] = {

    "documentario_cinematografico": {
        "descricao": "Documentário estilo Netflix — realista, sério, iluminação natural",
        "aspect_ratio": "16:9",
        "resolucao": "3840x2160",
        "color_grade": "neutro realista Rec709",
        "lut": "Rec709_clean",
        "temperatura_cor": "5500K",
        "iluminacao": "natural difusa, luz de janela, hora dourada",
        "profundidade_campo": "rasa — sujeito em foco, fundo desfocado f/2.8",
        "movimentos": ["panorâmica lenta 2°/s", "travelling suave steadicam", "plano estático trípode"],
        "tipos_plano": ["plano geral estabelecimento", "plano médio narrativa", "close up detalhe", "plano detalhe objeto"],
        "prompt_suffix": "documentary style, 4K cinematic, natural lighting, Rec709 color, shallow depth of field, handheld subtle, realistic, professional cinematography",
        "prompt_negativo": "cartoon, anime, CGI unrealistic, overexposed, oversaturated, fisheye, GoPro, shaky cam extreme",
        "velocidade_corte": "lento — 4-8s por plano",
        "musica_tipo": "orquestral sutil, ambient strings",
        "nicho_youtube": "documentario",
        "ffmpeg_lut": "lut3d=file=luts/rec709.cube",
    },

    "natureza_vida_selvagem": {
        "descricao": "Natureza estilo BBC/NatGeo — macro, fauna, flora, drones",
        "aspect_ratio": "16:9",
        "resolucao": "3840x2160",
        "color_grade": "verde vibrante, saturação +15, sky azul",
        "lut": "NatureVibrant",
        "temperatura_cor": "6500K",
        "iluminacao": "luz natural intensa, pôr do sol, macro luz difusa",
        "profundidade_campo": "variada — macro extremo ou paisagem total",
        "movimentos": ["drone aéreo suave", "travelling macro", "plano aéreo descendente", "pan lento panorâmico"],
        "tipos_plano": ["plano aéreo drone", "plano geral paisagem", "macro extremo animal", "plano detalhe textura"],
        "prompt_suffix": "wildlife photography, BBC nature style, 4K macro, golden hour light, vibrant colors, aerial drone shot, ultra realistic animal, National Geographic quality",
        "prompt_negativo": "people, urban, buildings, text, watermark, plastic, artificial",
        "velocidade_corte": "médio — 3-6s por plano",
        "musica_tipo": "orquestral épico, sons da natureza",
        "nicho_youtube": "documentario",
        "ffmpeg_lut": "lut3d=file=luts/nature.cube",
    },

    "historia_acontecimentos": {
        "descricao": "Reconstituição histórica — grão de filme, sépia, dramaticidade",
        "aspect_ratio": "16:9",
        "resolucao": "1920x1080",
        "color_grade": "sépia suave, desaturação -20, grão de filme 35mm",
        "lut": "FilmGrain_History",
        "temperatura_cor": "4800K",
        "iluminacao": "rembrandt lateral, luz de vela, névoa atmosférica",
        "profundidade_campo": "média — estilo fotografia de época",
        "movimentos": ["pan lento revelatório", "zoom lento aproximando", "plano estático solene"],
        "tipos_plano": ["plano geral cena histórica", "plano médio personagem época", "close up expressão drama", "detalhe objeto histórico"],
        "prompt_suffix": "historical reconstruction, cinematic, film grain 35mm, sepia tones, dramatic Rembrandt lighting, era-appropriate details, atmospheric haze, BBC documentary quality",
        "prompt_negativo": "modern objects, smartphones, cars, contemporary clothing, CGI obvious, plastic, neon",
        "velocidade_corte": "lento — 5-10s por plano",
        "musica_tipo": "orquestral histórico, instrumentos de época",
        "nicho_youtube": "historia",
        "ffmpeg_lut": "lut3d=file=luts/history.cube",
    },

    "tecnologia_ia": {
        "descricao": "Tech e IA — cyberpunk blue, holograma, dados, abstrato",
        "aspect_ratio": "16:9",
        "resolucao": "3840x2160",
        "color_grade": "neon azul ciano, fundo escuro, brilho LED",
        "lut": "CyberpunkBlue",
        "temperatura_cor": "9000K",
        "iluminacao": "LED azul lateral, rim light, luz de tela, brilho neon",
        "profundidade_campo": "rasa digital, bokeh hexagonal",
        "movimentos": ["câmera estática", "rack focus lento", "zoom digital suave", "parallax layers"],
        "tipos_plano": ["plano close circuito/chip", "plano abstrato dados", "plano holograma 3D", "plano pessoa tela/código"],
        "prompt_suffix": "cyberpunk tech aesthetic, blue neon lighting, dark background, holographic, AI neural network visualization, 8K ultra sharp, LED glow, digital particles, futuristic",
        "prompt_negativo": "retro analog, warm tones, nature, people casual, blurry, low resolution",
        "velocidade_corte": "médio-rápido — 2-4s por plano",
        "musica_tipo": "eletrônico, synth, ambient tech",
        "nicho_youtube": "tech_ia",
        "ffmpeg_lut": "lut3d=file=luts/cyberpunk.cube",
    },

    "misterio_suspense": {
        "descricao": "Mistério e conspiracy — sombras, verde, ângulos distorcidos",
        "aspect_ratio": "16:9",
        "resolucao": "1920x1080",
        "color_grade": "dessaturado esverdeado, sombras densas, alto contraste",
        "lut": "GreenGrade_Conspiracy",
        "temperatura_cor": "3800K",
        "iluminacao": "baixa chave lateral verde, sombras profundas",
        "profundidade_campo": "variada — planos fechados claustrofóbicos",
        "movimentos": ["câmera na mão leve", "dutch angle 10°", "zoom lento inquietante", "rack focus revelador"],
        "tipos_plano": ["plano fechado claustrofóbico", "dutch angle perturbador", "silhueta contra luz", "detalhe misterioso"],
        "prompt_suffix": "dark mystery, green tinted, conspiracy aesthetic, low key dramatic lighting, shadows, noir atmosphere, unsettling composition, Dutch angle, desaturated green",
        "prompt_negativo": "bright colors, happy faces, sunny outdoors, clean minimal, pastel",
        "velocidade_corte": "lento-médio — 3-6s por plano",
        "musica_tipo": "dark ambient, drones, suspense strings",
        "nicho_youtube": "conspiracao",
        "ffmpeg_lut": "lut3d=file=luts/mystery.cube",
    },

    "educacao": {
        "descricao": "Educacional limpo — high key, minimalista, foco no conteúdo",
        "aspect_ratio": "16:9",
        "resolucao": "1920x1080",
        "color_grade": "clean neutro, cores vivas de acento",
        "lut": "Educational_Clean",
        "temperatura_cor": "6000K",
        "iluminacao": "high key uniforme, sem sombras duras",
        "profundidade_campo": "ampla — tudo em foco",
        "movimentos": ["plano estático", "pan suave para elemento", "zoom suave de detalhe"],
        "tipos_plano": ["plano geral quadro branco/screen", "close detalhe objeto", "plano médio professor/narrador"],
        "prompt_suffix": "educational clean style, bright even lighting, clean background, modern classroom, whiteboard, 4K clear, vibrant accent colors, minimal distractions",
        "prompt_negativo": "dark, gritty, distracting background, low quality, blurry, complex clutter",
        "velocidade_corte": "médio — 3-5s por plano",
        "musica_tipo": "piano leve, ukulele, ambient positivo",
        "nicho_youtube": "educacao",
        "ffmpeg_lut": "eq=brightness=0.03:saturation=1.1",
    },

    "relaxamento": {
        "descricao": "ASMR/relaxamento — slow motion, cores pastel, natureza suave",
        "aspect_ratio": "16:9",
        "resolucao": "3840x2160",
        "color_grade": "pastel suave, +10 claridade, gradiente suave",
        "lut": "SoftPastel_Relax",
        "temperatura_cor": "5800K",
        "iluminacao": "luz natural suave, golden hour, névoa suave",
        "profundidade_campo": "rasa-média, bokeh suave circular",
        "movimentos": ["slow motion 60fps→24fps", "travelling ultra lento", "plano aberto estático"],
        "tipos_plano": ["plano aberto paisagem", "macro água/fogo/natureza", "plano detalhe textura calma"],
        "prompt_suffix": "relaxation aesthetic, soft pastel colors, slow motion, serene nature, ASMR visual, shallow depth of field, dreamy bokeh, golden hour, peaceful atmosphere",
        "prompt_negativo": "chaos, urban noise, dark colors, fast motion, harsh lighting, disturbing",
        "velocidade_corte": "muito lento — 6-12s por plano",
        "musica_tipo": "binaural beats, chuva, natureza, 432Hz",
        "nicho_youtube": "relaxamento",
        "ffmpeg_lut": "lut3d=file=luts/pastel.cube",
    },

    "storytelling_dark": {
        "descricao": "Dark channel storytelling — cinematografia dramática, sem apresentador",
        "aspect_ratio": "9:16",
        "resolucao": "1080x1920",
        "color_grade": "dark warm, contraste +20, profundidade de noir",
        "lut": "DarkNarrative",
        "temperatura_cor": "4200K",
        "iluminacao": "low key dramático, sombras expressivas, chiaroscuro",
        "profundidade_campo": "rasa, bokeh dramático",
        "movimentos": ["pan lento revelatório", "zoom suave in", "plano estático tenso", "travelling cinematográfico"],
        "tipos_plano": ["plano close expressivo", "plano médio narrativo", "plano detalhe simbólico", "plano geral atmosférico"],
        "prompt_suffix": "cinematic dark storytelling, dramatic chiaroscuro lighting, deep shadows, warm noir tones, emotional atmosphere, 9:16 vertical, ultra realistic, 4K",
        "prompt_negativo": "bright cheerful, comedy, cheap, low quality, text overlay, watermark",
        "velocidade_corte": "médio — 3-5s por plano",
        "musica_tipo": "orquestral dark, piano dramático, ambient noir",
        "nicho_youtube": "motivacional",
        "ffmpeg_lut": "lut3d=file=luts/dark_noir.cube",
    },
}

# ─────────────────────────────────────────────────────────────
# TIPOS DE ENQUADRAMENTO POR FUNÇÃO NARRATIVA
# ─────────────────────────────────────────────────────────────
ENQUADRAMENTOS_NARRATIVOS = {
    "abertura":      ["Extreme Wide Shot (EWS) — estabelece universo", "Aerial establishing shot"],
    "introducao":    ["Wide Shot (WS) — contexto completo", "Medium Wide Shot (MWS)"],
    "narrativa":     ["Medium Shot (MS) — ação principal", "Medium Close-Up (MCU) — expressão+contexto"],
    "emocao":        ["Close-Up (CU) — expressão facial", "Extreme Close-Up (ECU) — detalhe emocional"],
    "detalhe":       ["Insert Shot — objeto importante", "Point of View (POV) — perspectiva personagem"],
    "transicao":     ["Cutaway — contexto externo", "Match Cut — continuidade de movimento"],
    "encerramento":  ["Wide Shot revelador", "Fade to black gradual"],
}

# ─────────────────────────────────────────────────────────────
# BANCO DE REFERÊNCIAS VISUAIS (armazenamento por projeto)
# ─────────────────────────────────────────────────────────────
class BancoReferencias:
    """
    Armazena e recupera referências visuais por projeto:
    personagens, cenários, objetos, paleta, estilo.
    """

    def __init__(self, base_dir: str = "outputs/referencias"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _projeto_path(self, projeto_id: str) -> Path:
        p = self.base_dir / projeto_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _load(self, path: Path) -> dict:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self, path: Path, data: dict):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def criar_projeto(self, projeto_id: str, titulo: str, canal: str,
                      nicho: str, preset_nome: str) -> dict:
        """Inicializa banco de referências de um novo projeto."""
        preset = PRESETS_CINEMATOGRAFICOS.get(preset_nome, PRESETS_CINEMATOGRAFICOS["storytelling_dark"])
        projeto = {
            "projeto_id": projeto_id,
            "titulo": titulo,
            "canal": canal,
            "nicho": nicho,
            "preset": preset_nome,
            "preset_config": preset,
            "personagens": {},
            "cenarios": {},
            "objetos": {},
            "paleta_aprovada": preset.get("color_grade", ""),
            "estilo_aprovado": preset.get("prompt_suffix", ""),
            "cenas_aprovadas": [],
            "criado_em": datetime.now().isoformat(),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
        path = self._projeto_path(projeto_id) / "projeto.json"
        self._save(path, projeto)
        return projeto

    def registrar_personagem(self, projeto_id: str, nome: str,
                              descricao: str, prompt_consistencia: str,
                              vestuario: str = "", extras: dict = None) -> dict:
        """Registra personagem com referências visuais para consistência."""
        path = self._projeto_path(projeto_id) / "projeto.json"
        projeto = self._load(path)
        char_id = f"char_{uuid.uuid4().hex[:6]}"
        personagem = {
            "id": char_id,
            "nome": nome,
            "descricao": descricao,
            "prompt_consistencia": prompt_consistencia,
            "vestuario": vestuario,
            "extras": extras or {},
            "registrado_em": datetime.now().isoformat(),
            "nota_continuidade": f"Sempre incluir '{prompt_consistencia}' em prompts com {nome}"
        }
        if "personagens" not in projeto:
            projeto["personagens"] = {}
        projeto["personagens"][char_id] = personagem
        self._save(path, projeto)
        return {"char_id": char_id, "personagem": personagem}

    def registrar_cenario(self, projeto_id: str, nome: str,
                           descricao: str, prompt_cenario: str,
                           horario: str = "dia", clima: str = "bom") -> dict:
        """Registra cenário/ambiente com referências visuais."""
        path = self._projeto_path(projeto_id) / "projeto.json"
        projeto = self._load(path)
        cen_id = f"scene_{uuid.uuid4().hex[:6]}"
        cenario = {
            "id": cen_id,
            "nome": nome,
            "descricao": descricao,
            "prompt_cenario": prompt_cenario,
            "horario": horario,
            "clima": clima,
            "registrado_em": datetime.now().isoformat(),
        }
        if "cenarios" not in projeto:
            projeto["cenarios"] = {}
        projeto["cenarios"][cen_id] = cenario
        self._save(path, projeto)
        return {"cen_id": cen_id, "cenario": cenario}

    def obter_projeto(self, projeto_id: str) -> dict:
        path = self._projeto_path(projeto_id) / "projeto.json"
        return self._load(path)

    def listar_projetos(self) -> List[str]:
        return [p.name for p in self.base_dir.iterdir() if p.is_dir()]

    def construir_prompt_cena(self, projeto_id: str, descricao_cena: str,
                               personagens_ids: List[str] = None,
                               cenario_id: str = None) -> str:
        """Monta prompt de cena com referências de personagens/cenário aprovados."""
        projeto = self.obter_projeto(projeto_id)
        preset_nome = projeto.get("preset", "storytelling_dark")
        preset = PRESETS_CINEMATOGRAFICOS.get(preset_nome, {})

        partes = [descricao_cena]

        # Adicionar referências de personagens
        if personagens_ids:
            for pid in personagens_ids:
                char = projeto.get("personagens", {}).get(pid, {})
                if char.get("prompt_consistencia"):
                    partes.append(char["prompt_consistencia"])

        # Adicionar referências de cenário
        if cenario_id:
            cen = projeto.get("cenarios", {}).get(cenario_id, {})
            if cen.get("prompt_cenario"):
                partes.append(cen["prompt_cenario"])

        # Adicionar sufixo do preset
        if preset.get("prompt_suffix"):
            partes.append(preset["prompt_suffix"])

        return ", ".join(partes)


# ─────────────────────────────────────────────────────────────
# PLANEJADOR DE CENAS MULTI-SHOT
# ─────────────────────────────────────────────────────────────
def planejar_cenas_do_script(script: str, preset_nome: str,
                              n_imagens: int = 6) -> List[Dict]:
    """
    Divide script em cenas e gera plano multi-shot com:
    - Enquadramento por função narrativa
    - Movimento de câmera
    - Prompt visual base
    - Duração sugerida
    """
    preset = PRESETS_CINEMATOGRAFICOS.get(preset_nome, PRESETS_CINEMATOGRAFICOS["storytelling_dark"])

    # Dividir script em blocos
    sentencas = [s.strip() for s in script.replace(".", ".|").replace("!", "!|").replace("?", "?|").split("|") if s.strip()]
    n_sentencas = len(sentencas)
    bloco_size = max(1, n_sentencas // n_imagens)

    cenas = []
    funcoes = list(ENQUADRAMENTOS_NARRATIVOS.keys())
    movimentos = preset.get("movimentos", ["pan lento"])
    tipos = preset.get("tipos_plano", ["plano médio"])

    for i in range(n_imagens):
        inicio = i * bloco_size
        fim = inicio + bloco_size if i < n_imagens - 1 else n_sentencas
        texto_cena = " ".join(sentencas[inicio:fim]) if inicio < n_sentencas else ""

        funcao_idx = min(i, len(funcoes) - 1)
        funcao = funcoes[funcao_idx]
        enquadramento = ENQUADRAMENTOS_NARRATIVOS[funcao][0]
        movimento = movimentos[i % len(movimentos)]
        tipo_plano = tipos[i % len(tipos)]

        prompt_visual = (
            f"{texto_cena[:80]} — {tipo_plano}, {preset['iluminacao']}, "
            f"{preset['color_grade']}, {preset.get('prompt_suffix', '')}"
        )

        cenas.append({
            "cena": i + 1,
            "funcao_narrativa": funcao,
            "enquadramento": enquadramento,
            "tipo_plano": tipo_plano,
            "movimento_camera": movimento,
            "texto_narrativo": texto_cena,
            "prompt_visual": prompt_visual,
            "prompt_negativo": preset.get("prompt_negativo", ""),
            "duracao_sugerida": _calcular_duracao(funcao, preset),
            "temperatura_cor": preset.get("temperatura_cor", "5500K"),
            "lut": preset.get("lut", ""),
        })

    return cenas


def _calcular_duracao(funcao: str, preset: dict) -> str:
    """Duração sugerida por função e velocidade do preset."""
    vel = preset.get("velocidade_corte", "médio — 3-5s por plano")
    if "muito lento" in vel:
        base = {"abertura": "8-12s", "introducao": "7-10s", "encerramento": "10-15s"}.get(funcao, "6-10s")
    elif "lento" in vel:
        base = {"abertura": "6-8s", "introducao": "5-7s", "encerramento": "7-10s"}.get(funcao, "4-7s")
    elif "rápido" in vel:
        base = {"abertura": "2-3s", "introducao": "2-3s", "encerramento": "3-4s"}.get(funcao, "1-3s")
    else:  # médio
        base = {"abertura": "4-6s", "introducao": "3-5s", "encerramento": "5-7s"}.get(funcao, "3-5s")
    return base


# ─────────────────────────────────────────────────────────────
# VERIFICADOR DE CONTINUIDADE VISUAL
# ─────────────────────────────────────────────────────────────
def verificar_continuidade(cenas: List[Dict], preset_nome: str) -> Dict:
    """
    Avalia continuidade entre cenas: temperatura, movimento, enquadramento.
    Retorna checklist com alertas e sugestões.
    """
    preset = PRESETS_CINEMATOGRAFICOS.get(preset_nome, {})
    alertas = []
    ok = []

    temp_ref = preset.get("temperatura_cor", "5500K")
    for i, c in enumerate(cenas):
        if c.get("temperatura_cor") != temp_ref:
            alertas.append(f"Cena {i+1}: temperatura {c.get('temperatura_cor')} difere do preset ({temp_ref})")

    # Regra dos 180°: movimentos contrários sem cutaway
    movimentos_hist = [c.get("movimento_camera", "") for c in cenas]
    for i in range(1, len(movimentos_hist)):
        if ("left" in movimentos_hist[i-1] and "right" in movimentos_hist[i]) or \
           ("right" in movimentos_hist[i-1] and "left" in movimentos_hist[i]):
            alertas.append(f"Cenas {i}-{i+1}: inversão de direção sem cutaway intermediário")

    if not alertas:
        ok.append("Temperatura de cor consistente em todas as cenas")
        ok.append("Direção de movimento coerente")
        ok.append("Regra dos 180° respeitada")

    return {
        "preset": preset_nome,
        "total_cenas": len(cenas),
        "status": "aprovado" if not alertas else "alertas_encontrados",
        "alertas": alertas,
        "aprovados": ok,
        "checklist_obrigatorio": [
            "Paleta de cores consistente entre todas as cenas",
            "LUT aplicado uniformemente",
            "Personagens com mesma aparência e vestuário",
            "Iluminação coerente com horário/local da cena",
            "Proporções de objetos mantidas",
            "Conteúdo sintético NÃO apresentado como documental real",
            "AI disclosure visível quando exigido",
        ]
    }


# ─────────────────────────────────────────────────────────────
# GERADOR DE PROMPT VISUAL COMPLETO
# ─────────────────────────────────────────────────────────────
def gerar_prompt_visual_completo(
    descricao: str,
    preset_nome: str,
    personagens: List[str] = None,
    cenario: str = "",
    estilo_extra: str = ""
) -> Dict:
    """Monta prompt positivo + negativo para geração de imagem/vídeo."""
    preset = PRESETS_CINEMATOGRAFICOS.get(preset_nome, PRESETS_CINEMATOGRAFICOS["storytelling_dark"])

    partes_positivo = [descricao]
    if personagens:
        partes_positivo.extend(personagens)
    if cenario:
        partes_positivo.append(cenario)
    partes_positivo.append(preset["iluminacao"])
    partes_positivo.append(preset["color_grade"])
    partes_positivo.append(preset["prompt_suffix"])
    if estilo_extra:
        partes_positivo.append(estilo_extra)

    return {
        "prompt_positivo": ", ".join(partes_positivo),
        "prompt_negativo": preset.get("prompt_negativo", ""),
        "preset": preset_nome,
        "temperatura_cor": preset["temperatura_cor"],
        "lut": preset.get("lut", ""),
        "aspect_ratio": preset["aspect_ratio"],
        "resolucao": preset["resolucao"],
    }


# ─────────────────────────────────────────────────────────────
# AGENTE PRINCIPAL
# ─────────────────────────────────────────────────────────────
class CinematicDirectorAgent:
    """
    AGENTE CINEMATIC DIRECTOR v2.0 — Direção cinematográfica completa
    - 8 presets de estilo cinematográfico
    - Planejamento multi-shot a partir de script
    - Geração de prompts visuais por cena
    - Banco de referências por projeto (personagens, cenários, paleta)
    - Verificação de continuidade visual
    - Integração com BancoReferencias
    """

    AGENT_ID = "cinematic_director"
    VERSION = "2.0.0"

    def __init__(self, base_dir: str = "outputs"):
        self.banco = BancoReferencias(base_dir=os.path.join(base_dir, "referencias"))

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "").lower()
        payload = contrato.get("payload", {})

        roteamento = {
            "planejar_cenas":        self.planejar_cenas,
            "gerar_prompt":          self.gerar_prompt,
            "composicao":            self.gerar_composicao,
            "enquadramento":         self.gerar_composicao,
            "verificar_continuidade":self.verificar_continuidade_cenas,  # ANTES de "continuidade"
            "continuidade":          self.plano_continuidade,
            "criar_projeto":         self.criar_projeto_referencia,
            "registrar_personagem":  self.registrar_personagem,
            "registrar_cenario":     self.registrar_cenario,
            "banco_referencias":     self.consultar_banco,
            "listar_presets":        self.listar_presets,
            "status":                lambda p: self.status(),
        }

        for chave, metodo in roteamento.items():
            if chave in tarefa:
                return metodo(payload)

        # fallback
        return self.gerar_composicao(payload)

    def planejar_cenas(self, payload: dict) -> dict:
        script = payload.get("script", "")
        preset = payload.get("preset", payload.get("nicho", "storytelling_dark"))
        n = payload.get("n_imagens", payload.get("n_cenas", 6))
        canal = payload.get("canal", "")
        titulo = payload.get("titulo", "")

        cenas = planejar_cenas_do_script(script, preset, n_imagens=int(n))
        preset_cfg = PRESETS_CINEMATOGRAFICOS.get(preset, {})

        return {
            "agente": self.AGENT_ID,
            "titulo": titulo,
            "canal": canal,
            "preset": preset,
            "descricao_preset": preset_cfg.get("descricao", ""),
            "total_cenas": len(cenas),
            "cenas": cenas,
            "prompt_negativo_global": preset_cfg.get("prompt_negativo", ""),
            "musica_sugerida": preset_cfg.get("musica_tipo", ""),
            "custo": "GRATUITO — planejamento local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def gerar_prompt(self, payload: dict) -> dict:
        result = gerar_prompt_visual_completo(
            descricao=payload.get("descricao", ""),
            preset_nome=payload.get("preset", payload.get("nicho", "storytelling_dark")),
            personagens=payload.get("personagens", []),
            cenario=payload.get("cenario", ""),
            estilo_extra=payload.get("estilo_extra", ""),
        )
        result["agente"] = self.AGENT_ID
        result["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return result

    def gerar_composicao(self, payload: dict) -> dict:
        nicho = payload.get("nicho", payload.get("preset", "storytelling_dark"))
        script = payload.get("script", "")
        canal = payload.get("canal", "")
        n_cenas = max(3, len(script.split(".")) // 3) if script else 5

        preset = PRESETS_CINEMATOGRAFICOS.get(nicho, PRESETS_CINEMATOGRAFICOS["storytelling_dark"])
        funcoes = list(ENQUADRAMENTOS_NARRATIVOS.keys())
        cenas = []
        for i in range(n_cenas):
            funcao = funcoes[i % len(funcoes)]
            cenas.append({
                "cena": i + 1,
                "funcao_narrativa": funcao,
                "enquadramento": ENQUADRAMENTOS_NARRATIVOS[funcao][0],
                "movimento_camera": preset["movimentos"][i % len(preset["movimentos"])],
                "tipo_plano": preset["tipos_plano"][i % len(preset["tipos_plano"])],
                "duracao_sugerida": _calcular_duracao(funcao, preset),
            })

        return {
            "agente": self.AGENT_ID,
            "canal": canal,
            "nicho": nicho,
            "preset_cinematografico": preset,
            "cenas": cenas,
            "total_cenas": len(cenas),
            "custo": "GRATUITO — geração local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def plano_continuidade(self, payload: dict) -> dict:
        return {
            "agente": self.AGENT_ID,
            "regras_continuidade": [
                "Manter mesma temperatura de cor entre cenas contínuas",
                "Respeitar regra dos 180° — não inverter direção de câmera sem cutaway",
                "Corte no movimento garante fluidez — cortar quando ator/objeto está em movimento",
                "Match cut para continuidade visual de posição e enquadramento",
                "Manter proporção e posição dos elementos entre cortes",
                "LUT idêntico em todas as cenas da mesma sequência",
                "Personagens com mesma aparência, vestuário e cabelo em toda a cena",
                "Iluminação coerente com horário/local estabelecido na cena",
            ],
            "checklist_producao": [
                "✓ Paleta de cores definida e aprovada",
                "✓ LUT selecionado e aplicado uniformemente",
                "✓ Direção de câmera consistente (esq→dir ou dir→esq, não misturar)",
                "✓ Iluminação reflete horário do dia da cena",
                "✓ Personagens com aparência idêntica entre cortes",
                "✓ Objetos de prop posicionados corretamente",
                "✓ Cenas sintéticas NÃO apresentadas como documentais reais",
                "✓ AI disclosure visível quando exigido pela plataforma",
            ],
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def verificar_continuidade_cenas(self, payload: dict) -> dict:
        cenas = payload.get("cenas", [])
        preset = payload.get("preset", payload.get("nicho", "storytelling_dark"))
        result = verificar_continuidade(cenas, preset)
        result["agente"] = self.AGENT_ID
        result["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return result

    def criar_projeto_referencia(self, payload: dict) -> dict:
        projeto_id = payload.get("projeto_id", f"proj_{uuid.uuid4().hex[:8]}")
        projeto = self.banco.criar_projeto(
            projeto_id=projeto_id,
            titulo=payload.get("titulo", ""),
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho", "storytelling_dark"),
            preset_nome=payload.get("preset", payload.get("nicho", "storytelling_dark")),
        )
        return {
            "agente": self.AGENT_ID,
            "projeto_id": projeto_id,
            "projeto": projeto,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def registrar_personagem(self, payload: dict) -> dict:
        result = self.banco.registrar_personagem(
            projeto_id=payload.get("projeto_id", "default"),
            nome=payload.get("nome", "Personagem"),
            descricao=payload.get("descricao", ""),
            prompt_consistencia=payload.get("prompt_consistencia", ""),
            vestuario=payload.get("vestuario", ""),
            extras=payload.get("extras", {}),
        )
        result["agente"] = self.AGENT_ID
        result["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return result

    def registrar_cenario(self, payload: dict) -> dict:
        result = self.banco.registrar_cenario(
            projeto_id=payload.get("projeto_id", "default"),
            nome=payload.get("nome", "Cenário"),
            descricao=payload.get("descricao", ""),
            prompt_cenario=payload.get("prompt_cenario", ""),
            horario=payload.get("horario", "dia"),
            clima=payload.get("clima", "bom"),
        )
        result["agente"] = self.AGENT_ID
        result["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return result

    def consultar_banco(self, payload: dict) -> dict:
        projeto_id = payload.get("projeto_id")
        if projeto_id:
            projeto = self.banco.obter_projeto(projeto_id)
            return {
                "agente": self.AGENT_ID,
                "projeto": projeto,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
            }
        projetos = self.banco.listar_projetos()
        return {
            "agente": self.AGENT_ID,
            "projetos_disponiveis": projetos,
            "total": len(projetos),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def listar_presets(self, payload: dict) -> dict:
        return {
            "agente": self.AGENT_ID,
            "total_presets": len(PRESETS_CINEMATOGRAFICOS),
            "presets": {
                nome: {
                    "descricao": cfg["descricao"],
                    "aspect_ratio": cfg["aspect_ratio"],
                    "color_grade": cfg["color_grade"],
                    "nicho_youtube": cfg.get("nicho_youtube", ""),
                }
                for nome, cfg in PRESETS_CINEMATOGRAFICOS.items()
            },
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        projetos = self.banco.listar_projetos()
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "presets_disponiveis": list(PRESETS_CINEMATOGRAFICOS.keys()),
            "total_presets": len(PRESETS_CINEMATOGRAFICOS),
            "projetos_no_banco": projetos,
            "capacidades": [
                "planejar_cenas_multi_shot",
                "gerar_prompt_visual",
                "composicao_enquadramento",
                "verificar_continuidade",
                "banco_referencias_personagens",
                "banco_referencias_cenarios",
                "8_presets_cinematograficos",
            ],
            "custo": "GRATUITO — planejamento e geração de prompts 100% local",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
