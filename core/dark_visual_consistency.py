"""
DARK VISUAL CONSISTENCY — FASE 8 do DARK CREATIVE LAB
Sistema de continuidade audiovisual para manter identidade visual entre cenas.

Responsabilidades:
  - Banco de referências visuais por projeto
  - Registro de personagens, cenários, objetos e estilos aprovados
  - Validação de consistência entre cenas
  - Paleta de cores aprovada por projeto
  - Regras de continuidade cinematográfica
  - Exportação de bíblia visual

Princípios:
  - Conteúdo sintético identificado como tal (ai_generated: True)
  - Sem apresentar cenas como registros documentais reais
  - Identidade visual coerente em todo o projeto

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════
# PALETAS APROVADAS POR NICHO
# ═══════════════════════════════════════════════════════
PALETAS_NICHO = {
    "cinematico": {
        "nome": "Cinemático Dark",
        "bg": "#0A0A0F",
        "fg": "#E8E0F0",
        "accent": "#9B59B6",
        "accent2": "#3498DB",
        "sombra": "#1A0A2E",
        "temperatura": "fria",
        "saturacao": "baixa",
        "contraste": "alto",
        "color_grade_ffmpeg": "curves=r='0/0 0.3/0.2 1/0.9':g='0/0 0.5/0.45 1/0.85':b='0/0 0.3/0.4 1/1',eq=contrast=1.3:saturation=0.7",
    },
    "misterio": {
        "nome": "Mistério e Suspense",
        "bg": "#080810",
        "fg": "#C0B8D0",
        "accent": "#5D6D7E",
        "accent2": "#7F8C8D",
        "sombra": "#050510",
        "temperatura": "muito fria",
        "saturacao": "muito baixa",
        "contraste": "muito alto",
        "color_grade_ffmpeg": "curves=r='0/0 0.25/0.15 1/0.85':g='0/0 0.5/0.42 1/0.8':b='0/0.02 0.5/0.55 1/1',eq=contrast=1.4:saturation=0.5",
    },
    "natureza": {
        "nome": "Natureza e Vida Selvagem",
        "bg": "#0D1A0D",
        "fg": "#E8F5E8",
        "accent": "#27AE60",
        "accent2": "#F39C12",
        "sombra": "#071007",
        "temperatura": "neutra a quente",
        "saturacao": "alta",
        "contraste": "natural",
        "color_grade_ffmpeg": "curves=r='0/0 0.5/0.52 1/1':g='0/0 0.5/0.55 1/1':b='0/0 0.5/0.45 1/0.95',eq=saturation=1.2:contrast=1.05",
    },
    "historia": {
        "nome": "Histórico e Documental",
        "bg": "#1A1208",
        "fg": "#F5ECD7",
        "accent": "#C8A165",
        "accent2": "#8B6914",
        "sombra": "#0D0A04",
        "temperatura": "quente sépia",
        "saturacao": "baixa sépia",
        "contraste": "moderado",
        "color_grade_ffmpeg": "curves=r='0/0.05 1/0.95':g='0/0 1/0.85':b='0/0 1/0.7',colorbalance=bs=-0.1:gs=-0.05:rs=0.1,eq=saturation=0.5",
    },
    "tecnologia": {
        "nome": "Tecnologia e IA",
        "bg": "#030810",
        "fg": "#B0C8E0",
        "accent": "#00BCD4",
        "accent2": "#7C4DFF",
        "sombra": "#010408",
        "temperatura": "muito fria",
        "saturacao": "moderada azul",
        "contraste": "alto high-tech",
        "color_grade_ffmpeg": "curves=b='0/0 0.5/0.6 1/1':r='0/0 0.5/0.45 1/0.95',colorbalance=bh=0.2:gh=0.1:rh=-0.1,eq=contrast=1.15:saturation=0.85",
    },
    "motivacao": {
        "nome": "Motivação e Lifestyle",
        "bg": "#0F0800",
        "fg": "#FFF8E8",
        "accent": "#F39C12",
        "accent2": "#E74C3C",
        "sombra": "#080400",
        "temperatura": "quente dourada",
        "saturacao": "alta vibrante",
        "contraste": "moderado alto",
        "color_grade_ffmpeg": "curves=r='0/0 0.5/0.6 1/1':g='0/0 0.5/0.52 1/0.98':b='0/0 0.5/0.4 1/0.85',eq=saturation=1.15:contrast=1.1",
    },
    "geral": {
        "nome": "Geral Dark",
        "bg": "#0D0D0D",
        "fg": "#DDDDDD",
        "accent": "#E74C3C",
        "accent2": "#3498DB",
        "sombra": "#050505",
        "temperatura": "neutra",
        "saturacao": "moderada",
        "contraste": "moderado",
        "color_grade_ffmpeg": "eq=contrast=1.1:saturation=0.9:brightness=-0.02",
    },
}

# REGRAS DE CONTINUIDADE
REGRAS_CONTINUIDADE = [
    "Manter mesma temperatura de cor entre cenas da mesma sequência",
    "Não mudar plano abruptamente sem transição ou corte motivado",
    "Preservar direção do olhar dos personagens (regra dos 180°)",
    "Color grade consistente dentro do mesmo episódio",
    "Movimento de câmera coerente com a emoção da cena",
    "Manter proporções e escala dos objetos entre planos",
    "Vestuário e aparência dos personagens devem ser idênticos entre cenas",
    "Iluminação coerente com horário e clima estabelecidos",
    "Paleta de cores aprovada pela bíblia visual do projeto",
    "Identificar explicitamente conteúdo gerado por IA quando necessário",
]

# ESTILOS FOTOGRÁFICOS
ESTILOS_FOTO = {
    "noir": "Alto contraste, preto e branco ou quase, sombras duras",
    "golden_hour": "Luz quente dourada de nascer/pôr do sol, sombras longas",
    "blue_hour": "Luz fria azulada do crepúsculo, tons silenciosos",
    "studio": "Iluminação controlada, sem sombras duras, profissional",
    "documentary": "Luz natural, câmera na mão, realismo",
    "cinematic_wide": "Grande angular, distorção suave, profundidade",
    "telephoto": "Teleobjetiva, compressão, fundo desfocado",
    "macro": "Detalhes extremos, profundidade de campo mínima",
}


class DarkVisualConsistency:
    """
    Agente de consistência visual do DARK STUDIO AAA.
    Mantém identidade visual coerente entre todas as cenas de um projeto.
    """

    def __init__(self, db_dir: str = "dados/biblia_visual"):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.projetos: Dict[str, dict] = {}
        self._carregar_projetos()

    # ── Persistência ──────────────────────────────────────────────────────────

    def _path_projeto(self, projeto_id: str) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in projeto_id)
        return self.db_dir / f"{safe}.json"

    def _carregar_projetos(self):
        for f in self.db_dir.glob("*.json"):
            try:
                with open(f, encoding="utf-8") as fp:
                    data = json.load(fp)
                self.projetos[data["projeto_id"]] = data
            except Exception:
                pass

    def _salvar_projeto(self, projeto_id: str):
        path = self._path_projeto(projeto_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.projetos[projeto_id], f, ensure_ascii=False, indent=2)

    # ── Criação de Projeto ────────────────────────────────────────────────────

    def criar_projeto(
        self,
        projeto_id: str,
        titulo: str,
        nicho: str = "cinematico",
        descricao: str = "",
        canal: str = "",
    ) -> dict:
        """
        Cria um novo projeto com bíblia visual inicial.
        """
        paleta = PALETAS_NICHO.get(nicho, PALETAS_NICHO["geral"])

        projeto = {
            "projeto_id": projeto_id,
            "titulo": titulo,
            "canal": canal,
            "nicho": nicho,
            "descricao": descricao,
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat(),
            "paleta_aprovada": paleta,
            "personagens": {},
            "cenarios": {},
            "objetos": {},
            "estilos_aprovados": [],
            "regras_continuidade": REGRAS_CONTINUIDADE.copy(),
            "cenas_registradas": [],
            "estilo_fotografico": "documentary",
            "color_grade_preset": nicho,
            "resolucao_padrao": "1080x1920",
            "fps_padrao": 30,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

        self.projetos[projeto_id] = projeto
        self._salvar_projeto(projeto_id)
        print(f"  [VISUAL_CONSISTENCY] Projeto criado: {titulo} ({nicho})")
        return projeto

    # ── Registro de Personagens ───────────────────────────────────────────────

    def registrar_personagem(
        self,
        projeto_id: str,
        nome: str,
        descricao_visual: str,
        vestuario: str = "",
        imagem_referencia: str = "",
        notas: str = "",
    ) -> dict:
        """
        Registra um personagem na bíblia visual do projeto.
        """
        if projeto_id not in self.projetos:
            return {"status": "erro", "msg": f"Projeto '{projeto_id}' não encontrado"}

        pid = hashlib.md5(nome.encode()).hexdigest()[:8]
        personagem = {
            "id": pid,
            "nome": nome,
            "descricao_visual": descricao_visual,
            "vestuario": vestuario,
            "imagem_referencia": imagem_referencia,
            "notas": notas,
            "registrado_em": datetime.now().isoformat(),
            "prompt_consistencia": self._gerar_prompt_personagem(
                nome, descricao_visual, vestuario
            ),
        }

        self.projetos[projeto_id]["personagens"][pid] = personagem
        self.projetos[projeto_id]["atualizado_em"] = datetime.now().isoformat()
        self._salvar_projeto(projeto_id)
        print(f"  [VISUAL_CONSISTENCY] Personagem registrado: {nome}")
        return {"status": "ok", "personagem_id": pid, "personagem": personagem}

    def _gerar_prompt_personagem(self, nome: str, descricao: str, vestuario: str) -> str:
        """Gera prompt de consistência para o personagem."""
        parts = [f"character consistency: {nome}", descricao]
        if vestuario:
            parts.append(f"wearing {vestuario}")
        parts += [
            "same appearance throughout all scenes",
            "consistent facial features",
            "consistent body proportions",
        ]
        return ", ".join(parts)

    # ── Registro de Cenários ──────────────────────────────────────────────────

    def registrar_cenario(
        self,
        projeto_id: str,
        nome: str,
        descricao_visual: str,
        iluminacao: str = "",
        epoca: str = "",
        notas: str = "",
    ) -> dict:
        """
        Registra um cenário (ambiente/locação) na bíblia visual.
        """
        if projeto_id not in self.projetos:
            return {"status": "erro", "msg": f"Projeto '{projeto_id}' não encontrado"}

        sid = hashlib.md5(nome.encode()).hexdigest()[:8]
        cenario = {
            "id": sid,
            "nome": nome,
            "descricao_visual": descricao_visual,
            "iluminacao": iluminacao,
            "epoca": epoca,
            "notas": notas,
            "registrado_em": datetime.now().isoformat(),
            "prompt_consistencia": self._gerar_prompt_cenario(
                nome, descricao_visual, iluminacao, epoca
            ),
        }

        self.projetos[projeto_id]["cenarios"][sid] = cenario
        self.projetos[projeto_id]["atualizado_em"] = datetime.now().isoformat()
        self._salvar_projeto(projeto_id)
        print(f"  [VISUAL_CONSISTENCY] Cenário registrado: {nome}")
        return {"status": "ok", "cenario_id": sid, "cenario": cenario}

    def _gerar_prompt_cenario(
        self, nome: str, descricao: str, iluminacao: str, epoca: str
    ) -> str:
        """Gera prompt de consistência para o cenário."""
        parts = [f"location: {nome}", descricao]
        if iluminacao:
            parts.append(f"lighting: {iluminacao}")
        if epoca:
            parts.append(f"time period: {epoca}")
        parts.append("consistent environment details")
        return ", ".join(parts)

    # ── Registro de Cenas ─────────────────────────────────────────────────────

    def registrar_cena(
        self,
        projeto_id: str,
        num_cena: int,
        descricao: str,
        personagens_ids: list = None,
        cenario_id: str = None,
        hora_dia: str = "indefinido",
        clima: str = "indefinido",
        notas: str = "",
    ) -> dict:
        """
        Registra uma cena e valida consistência com as anteriores.
        """
        if projeto_id not in self.projetos:
            return {"status": "erro", "msg": f"Projeto '{projeto_id}' não encontrado"}

        proj = self.projetos[projeto_id]
        personagens_ids = personagens_ids or []

        # Resolver personagens
        personagens_na_cena = [
            proj["personagens"].get(pid, {}) for pid in personagens_ids
        ]

        # Resolver cenário
        cenario_na_cena = proj["cenarios"].get(cenario_id, {}) if cenario_id else {}

        # Prompt de consistência completo
        prompt_parts = [descricao]
        if cenario_na_cena:
            prompt_parts.append(cenario_na_cena.get("prompt_consistencia", ""))
        for p in personagens_na_cena:
            prompt_parts.append(p.get("prompt_consistencia", ""))
        prompt_parts += [
            f"time of day: {hora_dia}",
            f"weather: {clima}",
            f"color palette: {proj['paleta_aprovada']['nome']}",
            f"cinematic style: {proj['nicho']}",
            "ai-generated content, not real footage",
        ]

        cena = {
            "num_cena": num_cena,
            "descricao": descricao,
            "personagens": personagens_na_cena,
            "cenario": cenario_na_cena,
            "hora_dia": hora_dia,
            "clima": clima,
            "notas": notas,
            "prompt_consistencia": ", ".join(filter(None, prompt_parts)),
            "registrado_em": datetime.now().isoformat(),
        }

        # Validação de continuidade
        alertas = self._validar_continuidade(proj, cena)
        cena["alertas_continuidade"] = alertas

        proj["cenas_registradas"].append(cena)
        proj["atualizado_em"] = datetime.now().isoformat()
        self._salvar_projeto(projeto_id)

        if alertas:
            print(f"  [VISUAL_CONSISTENCY] ⚠️  Cena {num_cena}: {len(alertas)} alerta(s)")
            for a in alertas:
                print(f"    - {a}")
        else:
            print(f"  [VISUAL_CONSISTENCY] ✅ Cena {num_cena} registrada e validada")

        return {"status": "ok", "cena": cena, "alertas": alertas}

    def _validar_continuidade(self, projeto: dict, cena_nova: dict) -> list:
        """
        Verifica se a nova cena é consistente com as anteriores.
        Retorna lista de alertas (vazia = sem problemas).
        """
        alertas = []
        cenas = projeto.get("cenas_registradas", [])
        if not cenas:
            return alertas

        ultima = cenas[-1]

        # Verificar mudanças abruptas de hora do dia
        if (
            ultima.get("hora_dia") != "indefinido"
            and cena_nova.get("hora_dia") != "indefinido"
            and ultima["hora_dia"] != cena_nova["hora_dia"]
        ):
            alertas.append(
                f"Mudança de hora do dia: {ultima['hora_dia']} → {cena_nova['hora_dia']} "
                "— verifique se há justificativa narrativa"
            )

        # Verificar mudanças de clima sem transição
        if (
            ultima.get("clima") != "indefinido"
            and cena_nova.get("clima") != "indefinido"
            and ultima["clima"] != cena_nova["clima"]
        ):
            alertas.append(
                f"Mudança de clima: {ultima['clima']} → {cena_nova['clima']} "
                "— certifique-se que há elipse temporal"
            )

        return alertas

    # ── Bíblia Visual ─────────────────────────────────────────────────────────

    def exportar_biblia(self, projeto_id: str, output_path: str = None) -> dict:
        """
        Exporta a bíblia visual completa do projeto como JSON.
        """
        if projeto_id not in self.projetos:
            return {"status": "erro", "msg": f"Projeto '{projeto_id}' não encontrado"}

        proj = self.projetos[projeto_id]
        if output_path is None:
            output_path = str(self.db_dir / f"biblia_{projeto_id}.json")

        biblia = {
            "titulo": f"Bíblia Visual — {proj['titulo']}",
            "projeto_id": projeto_id,
            "canal": proj.get("canal", ""),
            "nicho": proj["nicho"],
            "gerado_em": datetime.now().isoformat(),
            "paleta_aprovada": proj["paleta_aprovada"],
            "estilo_fotografico": proj.get("estilo_fotografico", "documentary"),
            "color_grade_preset": proj.get("color_grade_preset", "cinematic"),
            "resolucao_padrao": proj.get("resolucao_padrao", "1080x1920"),
            "fps_padrao": proj.get("fps_padrao", 30),
            "personagens": list(proj["personagens"].values()),
            "cenarios": list(proj["cenarios"].values()),
            "objetos": list(proj.get("objetos", {}).values()),
            "regras_continuidade": proj["regras_continuidade"],
            "total_cenas": len(proj.get("cenas_registradas", [])),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "aviso": "Conteúdo gerado por IA — não representa registros documentais reais",
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(biblia, f, ensure_ascii=False, indent=2)

        print(f"  [VISUAL_CONSISTENCY] 📖 Bíblia exportada: {output_path}")
        return {"status": "ok", "path": output_path, "biblia": biblia}

    def relatorio_projeto(self, projeto_id: str) -> dict:
        """Retorna relatório resumido do projeto."""
        if projeto_id not in self.projetos:
            return {"status": "erro", "msg": f"Projeto '{projeto_id}' não encontrado"}
        proj = self.projetos[projeto_id]
        return {
            "status": "ok",
            "projeto_id": projeto_id,
            "titulo": proj["titulo"],
            "nicho": proj["nicho"],
            "paleta": proj["paleta_aprovada"]["nome"],
            "total_personagens": len(proj["personagens"]),
            "total_cenarios": len(proj["cenarios"]),
            "total_cenas": len(proj.get("cenas_registradas", [])),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def gerar_prompt_com_consistencia(
        self,
        projeto_id: str,
        descricao_cena: str,
        personagem_ids: list = None,
        cenario_id: str = None,
    ) -> str:
        """
        Gera prompt visual completo com todos os elementos de consistência do projeto.
        """
        if projeto_id not in self.projetos:
            return descricao_cena

        proj = self.projetos[projeto_id]
        pal = proj["paleta_aprovada"]
        parts = [descricao_cena]

        # Adicionar personagens
        for pid in (personagem_ids or []):
            p = proj["personagens"].get(pid)
            if p:
                parts.append(p["prompt_consistencia"])

        # Adicionar cenário
        if cenario_id:
            c = proj["cenarios"].get(cenario_id)
            if c:
                parts.append(c["prompt_consistencia"])

        # Adicionar estilo e paleta
        parts += [
            f"color palette: {pal['nome']}, {pal['temperatura']} color temperature",
            f"visual style: {proj['nicho']} dark channel aesthetic",
            "cinematic quality, professional production",
            "ai-generated content",
        ]

        return ", ".join(filter(None, parts))

    def listar_projetos(self) -> list:
        """Lista todos os projetos registrados."""
        return [
            {
                "id": pid,
                "titulo": p["titulo"],
                "nicho": p["nicho"],
                "canal": p.get("canal", ""),
                "personagens": len(p["personagens"]),
                "cenarios": len(p["cenarios"]),
                "cenas": len(p.get("cenas_registradas", [])),
            }
            for pid, p in self.projetos.items()
        ]


# ═══════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════
CONTRACT = {
    "agente": "VISUAL_CONSISTENCY",
    "versao": "1.0.0",
    "descricao": "Mantém identidade visual, personagens, ambientes e estilo entre cenas",
    "metodos": {
        "criar_projeto": {
            "entrada": {
                "projeto_id": "str",
                "titulo": "str",
                "nicho": "str — cinematico|misterio|natureza|historia|tecnologia|motivacao|geral",
                "canal": "str?",
                "descricao": "str?",
            },
            "saida": "dict — projeto com paleta, regras e bíblia inicial",
        },
        "registrar_personagem": {
            "entrada": {
                "projeto_id": "str",
                "nome": "str",
                "descricao_visual": "str — aparência detalhada",
                "vestuario": "str?",
                "imagem_referencia": "str? — path",
            },
            "saida": {"status": "ok|erro", "personagem_id": "str"},
        },
        "registrar_cenario": {
            "entrada": {
                "projeto_id": "str",
                "nome": "str",
                "descricao_visual": "str",
                "iluminacao": "str?",
                "epoca": "str?",
            },
            "saida": {"status": "ok|erro", "cenario_id": "str"},
        },
        "registrar_cena": {
            "entrada": {
                "projeto_id": "str",
                "num_cena": "int",
                "descricao": "str",
                "personagens_ids": "list?",
                "cenario_id": "str?",
                "hora_dia": "str?",
                "clima": "str?",
            },
            "saida": {"status": "ok|erro", "alertas": "list"},
        },
        "gerar_prompt_com_consistencia": {
            "entrada": {
                "projeto_id": "str",
                "descricao_cena": "str",
                "personagem_ids": "list?",
                "cenario_id": "str?",
            },
            "saida": "str — prompt visual completo com consistência",
        },
        "exportar_biblia": {
            "entrada": {"projeto_id": "str", "output_path": "str?"},
            "saida": {"status": "ok|erro", "path": "str"},
        },
    },
    "nichos_disponiveis": list(PALETAS_NICHO.keys()),
    "estilos_fotograficos": list(ESTILOS_FOTO.keys()),
    "regras_continuidade": REGRAS_CONTINUIDADE,
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
}


if __name__ == "__main__":
    vc = DarkVisualConsistency()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK VISUAL CONSISTENCY — FASE 8                   ║")
    print("║   Sistema de Continuidade Audiovisual                ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    # Criar projeto de demonstração
    proj = vc.criar_projeto(
        projeto_id="dyatlov_2024",
        titulo="Dyatlov — 9 Mortes Sem Explicação",
        nicho="misterio",
        canal="DARK MYSTERIES",
        descricao="Documental sobre o incidente da Passagem Dyatlov em 1959",
    )

    # Registrar personagens
    r1 = vc.registrar_personagem(
        "dyatlov_2024",
        nome="Igor Dyatlov",
        descricao_visual="Jovem soviético, 23 anos, cabelo escuro, feições eslavas, expressão determinada",
        vestuario="Casaco de inverno soviético marrom-escuro, gorro de lã, botas de neve",
    )

    # Registrar cenário
    c1 = vc.registrar_cenario(
        "dyatlov_2024",
        nome="Montanhas Urais — Inverno 1959",
        descricao_visual="Paisagem nevada ártica, pinheiros cobertos de neve, céu noturno estrelado, silêncio total",
        iluminacao="Noite, luz da lua cheia, tons azuis frios",
        epoca="União Soviética, janeiro de 1959",
    )

    # Registrar cenas
    vc.registrar_cena(
        "dyatlov_2024",
        num_cena=1,
        descricao="Grupo de esquiadores partindo da cidade de Ivdel",
        personagens_ids=[r1["personagem_id"]],
        cenario_id=c1["cenario_id"],
        hora_dia="manhã",
        clima="neve leve",
    )

    vc.registrar_cena(
        "dyatlov_2024",
        num_cena=2,
        descricao="Barraca rasgada encontrada na neve, sem sinais de luta",
        personagens_ids=[],
        cenario_id=c1["cenario_id"],
        hora_dia="dia",
        clima="tempestade de neve",
    )

    # Gerar prompt com consistência
    prompt = vc.gerar_prompt_com_consistencia(
        "dyatlov_2024",
        "Investigador relendo documentos secretos classificados",
    )
    print(f"\nPROMPT COM CONSISTÊNCIA:\n  {prompt[:120]}...")

    # Exportar bíblia
    biblia = vc.exportar_biblia("dyatlov_2024")

    # Relatório
    rel = vc.relatorio_projeto("dyatlov_2024")
    print(f"\nRELATÓRIO DO PROJETO:")
    for k, v in rel.items():
        if k not in ("status", "ai_generated", "ai_disclosure"):
            print(f"  {k}: {v}")

    # Paletas disponíveis
    print(f"\nPALETAS DE NICHO DISPONÍVEIS:")
    for k, v in PALETAS_NICHO.items():
        print(f"  {k:15} — {v['nome']}")

    # Salvar contrato
    Path("core").mkdir(exist_ok=True)
    with open("core/dark_visual_consistency_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print(f"\n  Contrato: core/dark_visual_consistency_contract.json")
    print(f"  Banco de dados: dados/biblia_visual/")
    print(f"  Bíblia exportada: {biblia.get('path', 'N/A')}\n")
