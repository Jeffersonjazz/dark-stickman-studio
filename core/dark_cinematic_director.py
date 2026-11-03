"""
DARK CINEMATIC DIRECTOR — FASE 4 do DARK CREATIVE LAB
Direção de fotografia, composição, iluminação e continuidade visual.

Responsabilidades:
  - Definir estilo cinematográfico por preset
  - Gerar prompts visuais por cena com parâmetros de câmera
  - Manter consistência visual entre cenas
  - Integrar com IMAGE ENGINE e VIDEO GENERATOR

Presets disponíveis:
  - documentary    — tom documental, câmera na mão, naturalista
  - dark_thriller  — suspense, noir, contraste alto
  - nature         — wildlife, golden hour, teleobjetiva
  - history        — tom sépia, granulação de filme, documental
  - sci_tech       — futurista, luzes frias, câmera precisa
  - relaxation     — suave, warmth, slow motion
  - education      — claro, direto, dinâmico
  - music          — ritmo visual, cortes rápidos, close-ups

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════
# ESTILOS CINEMATOGRÁFICOS
# ═══════════════════════════════════════════════════════
ESTILOS = {
    "documentary": {
        "nome": "Documentário Cinematográfico",
        "camera": "hand-held camera, slight shake, observational",
        "lente": "24mm to 50mm lens, natural depth of field",
        "iluminacao": "natural light, available light, realistic shadows",
        "paleta": "desaturated, neutral, realistic tones",
        "movimento": "slow pan, gentle tilt, observational tracking",
        "color_grade": "slightly muted, documentary look, slight vignette",
        "fps": 24,
        "ratio": "16:9",
        "referencia": "Werner Herzog, National Geographic, BBC documentaries",
        "prompt_suffix": "documentary style, natural lighting, cinematic realism, 4K"
    },
    "dark_thriller": {
        "nome": "Thriller / Suspense Dark",
        "camera": "static shot or slow creep, unsettling angles",
        "lente": "wide angle 18-28mm for distortion, or telephoto for compression",
        "iluminacao": "low key, single light source, deep shadows, chiaroscuro",
        "paleta": "high contrast, desaturated, cold blues and deep blacks",
        "movimento": "slow push in, Dutch angle, slow reveal",
        "color_grade": "teal and orange, high contrast, crushed blacks",
        "fps": 24,
        "ratio": "2.39:1 anamorphic",
        "referencia": "David Fincher, Denis Villeneuve, Ridley Scott",
        "prompt_suffix": "dark cinematic thriller, high contrast, moody lighting, noir"
    },
    "nature": {
        "nome": "Natureza e Vida Selvagem",
        "camera": "telephoto, stabilized, patient observation",
        "lente": "200mm-600mm telephoto, macro for details",
        "iluminacao": "golden hour, blue hour, natural only",
        "paleta": "vibrant but natural, warm golds, rich greens",
        "movimento": "slow motion, locked off tripod, ultra slow pan",
        "color_grade": "slightly saturated, warm, natural colors",
        "fps": "120fps for slow motion, 24fps for normal",
        "ratio": "16:9 or 2.39:1",
        "referencia": "BBC Planet Earth, David Attenborough, NatGeo Wild",
        "prompt_suffix": "wildlife documentary, golden hour light, telephoto lens, 4K nature"
    },
    "history": {
        "nome": "Histórico e Documental",
        "camera": "archival feel, static or very slow movement",
        "lente": "moderate telephoto 50-85mm, slight film vignette",
        "iluminacao": "warm, sepia, period-accurate",
        "paleta": "sepia tones, desaturated, aged film look",
        "movimento": "very slow pan, minimal movement",
        "color_grade": "grain, sepia, aged, archival look",
        "fps": 24,
        "ratio": "16:9 or 4:3 for archival",
        "referencia": "Ken Burns effect, archival footage style",
        "prompt_suffix": "historical documentary, archival footage style, sepia tone, aged film grain"
    },
    "sci_tech": {
        "nome": "Tecnologia e Inteligência Artificial",
        "camera": "precise, controlled, clinical",
        "lente": "macro for details, wide for scale",
        "iluminacao": "cool LEDs, blue/cyan accents, precise highlights",
        "paleta": "cold blues, whites, neon accents on dark bg",
        "movimento": "smooth dolly, drone, robotic precision",
        "color_grade": "teal highlights, cold, high tech feel",
        "fps": 24,
        "ratio": "16:9 or 2.39:1",
        "referencia": "Ex Machina, Blade Runner 2049, tech reveal videos",
        "prompt_suffix": "futuristic tech aesthetic, blue neon lighting, ultra sharp, high tech"
    },
    "relaxation": {
        "nome": "Relaxamento e Bem-estar",
        "camera": "smooth, flowing, gentle",
        "lente": "50mm standard or wide angle",
        "iluminacao": "soft, warm, diffused, magical hour",
        "paleta": "warm pastels, soft greens and blues, gentle",
        "movimento": "ultra slow, floating, gentle drift",
        "color_grade": "warm, slightly faded, dreamlike",
        "fps": "60fps for smoothness",
        "ratio": "16:9",
        "referencia": "meditation videos, ASMR, ambient channels",
        "prompt_suffix": "peaceful, warm light, soft focus, dreamlike, calming"
    },
    "education": {
        "nome": "Educação e Explicativo",
        "camera": "clear, frontal, informative",
        "lente": "50-85mm standard",
        "iluminacao": "bright, even, studio look",
        "paleta": "clean, bright, engaging colors",
        "movimento": "smooth, deliberate",
        "color_grade": "bright, saturated, clean",
        "fps": 24,
        "ratio": "16:9",
        "referencia": "TED talks, Kurzgesagt, educational YouTube",
        "prompt_suffix": "clear educational style, bright lighting, informative visual"
    },
    "music": {
        "nome": "Conteúdo Musical",
        "camera": "dynamic, rhythmic, expressive",
        "lente": "varied, wide to telephoto",
        "iluminacao": "concert lighting, dramatic, colorful",
        "paleta": "vibrant, high saturation, expressive",
        "movimento": "rhythm-matched cuts, dynamic camera",
        "color_grade": "high contrast, vibrant",
        "fps": "24 or 60 depending on energy",
        "ratio": "16:9 or 9:16 for shorts",
        "referencia": "music videos, concert films",
        "prompt_suffix": "music video aesthetic, dynamic lighting, vibrant colors, dramatic"
    }
}


# ═══════════════════════════════════════════════════════
# MOVIMENTOS DE CÂMERA
# ═══════════════════════════════════════════════════════
MOVIMENTOS_CAMERA = {
    "static": "locked off tripod, completely still",
    "slow_pan": "slow horizontal pan, left to right",
    "slow_tilt": "slow vertical tilt, down to up",
    "push_in": "slow dolly push toward subject",
    "pull_out": "slow dolly pull away from subject",
    "crane_up": "crane or drone rising from low to high",
    "crane_down": "crane or drone descending",
    "orbit": "slow orbital movement around subject",
    "tracking": "side tracking shot following movement",
    "dutch_angle": "tilted frame, unsettling perspective",
    "drone_aerial": "high aerial drone shot looking down",
    "handheld": "slight handheld shake, natural movement",
    "slow_reveal": "starting tight, slowly revealing wider scene",
    "whip_pan": "fast whip pan transition between scenes",
}

# PLANOS
PLANOS = {
    "ECU": "Extreme Close Up — detalhe extremo, olhos ou objeto pequeno",
    "CU": "Close Up — rosto ou objeto em destaque",
    "MCU": "Medium Close Up — do peito para cima",
    "MS": "Medium Shot — da cintura para cima",
    "MLS": "Medium Long Shot — do joelho para cima",
    "LS": "Long Shot — corpo inteiro no quadro",
    "VLS": "Very Long Shot — ambiente e personagem",
    "ELS": "Extreme Long Shot — paisagem, grandiosidade",
    "OTS": "Over The Shoulder — perspectiva de diálogo",
    "POV": "Point Of View — câmera na perspectiva do personagem",
    "AERIAL": "Vista aérea de cima",
    "WORM": "Câmera no nível do chão, olhando para cima",
}


class DarkCinematicDirector:
    """
    Agente de direção cinematográfica do DARK STUDIO AAA.
    Gera prompts visuais coerentes para cada cena do projeto.
    """

    def __init__(self, projeto: str = "dark_studio"):
        self.projeto = projeto
        self.banco_referencias = {}
        self.historico_cenas = []
        self.paleta_aprovada = None

    def definir_estilo(self, preset: str) -> dict:
        """Retorna o perfil cinematográfico completo para o preset."""
        est = ESTILOS.get(preset, ESTILOS["documentary"])
        return {
            "preset": preset,
            "perfil": est,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def gerar_prompt_visual(self, descricao: str, estilo: str = "documentary",
                             plano: str = "MS", movimento: str = "slow_pan",
                             num_cena: int = 1) -> dict:
        """
        Gera prompt visual completo para uma cena.
        """
        est = ESTILOS.get(estilo, ESTILOS["documentary"])
        mov = MOVIMENTOS_CAMERA.get(movimento, movimento)
        pla = PLANOS.get(plano, plano)

        prompt = (
            f"{descricao}, "
            f"{pla}, "
            f"{mov}, "
            f"{est['camera']}, "
            f"{est['iluminacao']}, "
            f"{est['paleta']}, "
            f"{est['prompt_suffix']}, "
            f"highly detailed, professional cinematography, masterful composition"
        )

        cena = {
            "num_cena": num_cena,
            "descricao": descricao,
            "estilo": estilo,
            "plano": plano,
            "movimento": movimento,
            "prompt_final": prompt,
            "parametros": {
                "camera": est["camera"],
                "lente": est["lente"],
                "iluminacao": est["iluminacao"],
                "paleta": est["paleta"],
                "color_grade": est["color_grade"],
                "fps": est["fps"],
                "ratio": est["ratio"],
            },
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
        self.historico_cenas.append(cena)
        return cena

    def sequenciar_cenas(self, roteiro: list, estilo: str = "documentary") -> list:
        """
        Recebe lista de cenas [{descricao, plano?, movimento?}]
        e gera sequência visual coerente.
        """
        sequencia = []
        # Regra: variar planos progressivamente
        planos_seq = ["ELS", "LS", "MS", "MCU", "CU", "MCU", "MS", "LS"]
        movimentos_seq = ["slow_pan", "static", "push_in", "slow_tilt",
                          "static", "pull_out", "slow_pan", "crane_up"]

        for i, cena in enumerate(roteiro):
            plano = cena.get("plano") or planos_seq[i % len(planos_seq)]
            movimento = cena.get("movimento") or movimentos_seq[i % len(movimentos_seq)]
            result = self.gerar_prompt_visual(
                descricao=cena["descricao"],
                estilo=estilo,
                plano=plano,
                movimento=movimento,
                num_cena=i + 1
            )
            sequencia.append(result)

        return sequencia

    def criar_biblia_visual(self, projeto: str, estilo: str,
                             personagens: list = None,
                             cenarios: list = None) -> dict:
        """
        Cria a bíblia visual do projeto (banco de referências).
        """
        biblia = {
            "projeto": projeto,
            "estilo_base": estilo,
            "perfil_cinematografico": ESTILOS.get(estilo, ESTILOS["documentary"]),
            "personagens": personagens or [],
            "cenarios": cenarios or [],
            "paleta_aprovada": self.paleta_aprovada,
            "regras_continuidade": [
                "Manter mesma temperatura de cor entre cenas da mesma sequência",
                "Não mudar plano abrupto sem transição",
                "Preservar direção do olhar dos personagens (regra dos 180°)",
                "Color grade consistente dentro do mesmo episódio",
                "Movimento de câmera coerente com a emoção da cena",
            ],
            "gerado_em": datetime.now().isoformat(),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
        self.banco_referencias[projeto] = biblia
        return biblia

    def gerar_roteiro_de_camera(self, titulo: str, cenas: list,
                                 estilo: str = "documentary") -> dict:
        """
        Pipeline completo: roteiro textual → roteiro de câmera com prompts visuais.
        """
        print(f"\n[CINEMATIC_DIRECTOR] Roteiro de câmera: {titulo}")

        sequencia = self.sequenciar_cenas(cenas, estilo)
        biblia = self.criar_biblia_visual(titulo, estilo)

        roteiro_final = {
            "titulo": titulo,
            "estilo": estilo,
            "perfil": ESTILOS.get(estilo, {}),
            "total_cenas": len(sequencia),
            "cenas": sequencia,
            "biblia_visual": biblia,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

        print(f"  ✅ {len(sequencia)} cenas com prompts visuais gerados")
        return roteiro_final


# ═══════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════
CONTRACT = {
    "agente": "CINEMATIC_DIRECTOR",
    "versao": "1.0.0",
    "descricao": "Direção de fotografia, composição, iluminação e continuidade visual",
    "entrada": {
        "roteiro": "list — lista de cenas [{descricao, plano?, movimento?}]",
        "estilo": "str — documentary|dark_thriller|nature|history|sci_tech|relaxation|education|music",
        "titulo": "str — título do projeto",
        "personagens": "list? — descrição visual dos personagens",
        "cenarios": "list? — descrição dos ambientes"
    },
    "saida": {
        "cenas": "list — prompts visuais por cena",
        "biblia_visual": "dict — banco de referências do projeto",
        "ai_generated": True,
        "ai_disclosure": "str"
    },
    "estilos_disponiveis": list(ESTILOS.keys()),
    "planos_disponiveis": list(PLANOS.keys()),
    "movimentos_disponiveis": list(MOVIMENTOS_CAMERA.keys()),
}


if __name__ == "__main__":
    director = DarkCinematicDirector("dark_studio_aaa")

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK CINEMATIC DIRECTOR — FASE 4                   ║")
    print("║   Direção de Fotografia e Continuidade Visual         ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    # Teste: roteiro de câmera para Short "Dyatlov"
    cenas_teste = [
        {"descricao": "Montanhas Urais cobertas de neve à noite, silêncio total"},
        {"descricao": "Barraca rasgada no meio da neve, sem sinais de luta"},
        {"descricao": "Trilha de pegadas no gelo levando para o escuro"},
        {"descricao": "Arquivo soviético classificado, papel amarelado"},
        {"descricao": "Close nos olhos de um investigador relendo o processo"},
    ]

    roteiro = director.gerar_roteiro_de_camera(
        titulo="Dyatlov — 9 Mortes Sem Explicação",
        cenas=cenas_teste,
        estilo="dark_thriller"
    )

    print("\nROTEIRO DE CÂMERA:")
    for cena in roteiro["cenas"]:
        print(f"\n  CENA {cena['num_cena']} [{cena['plano']} — {cena['movimento']}]")
        print(f"  {cena['prompt_final'][:100]}...")

    print(f"\nESTILOS DISPONÍVEIS:")
    for k, v in ESTILOS.items():
        print(f"  {k:15} — {v['nome']}")

    # Salvar contrato
    Path("core").mkdir(exist_ok=True)
    with open("core/dark_cinematic_director_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print("\n  Contrato: core/dark_cinematic_director_contract.json")
