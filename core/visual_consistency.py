"""
DARK CREATIVE LAB — AGENTE VISUAL CONSISTENCY
Mantém identidade visual, personagens, ambientes, paleta de cores e estilo entre cenas.

Funções:
- Banco de referências visuais por projeto
- Registro de personagens, cenários, objetos e estilos aprovados
- Extração automática de paleta de cores
- Validação de consistência entre cenas
- Geração de prompts com contexto de continuidade

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  BANCO DE REFERÊNCIAS
# ─────────────────────────────────────────────────────────────────

class VisualConsistencyDB:
    """
    Banco de referências visuais por projeto.

    Persiste em JSON no diretório do projeto:
    {output_dir}/.visual_consistency.json
    """

    def __init__(self, projeto_dir: Path):
        self.projeto_dir = Path(projeto_dir)
        self.db_path = self.projeto_dir / ".visual_consistency.json"
        self._db = self._load()

    def _load(self) -> dict:
        if self.db_path.exists():
            try:
                return json.loads(self.db_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "personagens": {},
            "cenarios": {},
            "objetos": {},
            "estilos": {},
            "paleta_global": [],
            "preset_cinematografico": None,
            "historico_cenas": [],
        }

    def _save(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(
            json.dumps(self._db, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── PERSONAGENS ────────────────────────────────────────────────

    def registrar_personagem(self, nome: str, descricao: str, atributos: dict = None):
        """Registra personagem com descrição e atributos visuais."""
        self._db["personagens"][nome] = {
            "descricao": descricao,
            "atributos": atributos or {},
            "aparicoes": 0,
        }
        self._save()

    def get_personagem(self, nome: str) -> Optional[dict]:
        return self._db["personagens"].get(nome)

    def incrementar_aparicao(self, nome: str):
        if nome in self._db["personagens"]:
            self._db["personagens"][nome]["aparicoes"] += 1
            self._save()

    # ── CENÁRIOS ──────────────────────────────────────────────────

    def registrar_cenario(self, nome: str, descricao: str, iluminacao: str = "natural"):
        self._db["cenarios"][nome] = {
            "descricao": descricao,
            "iluminacao": iluminacao,
            "usos": 0,
        }
        self._save()

    def get_cenario(self, nome: str) -> Optional[dict]:
        return self._db["cenarios"].get(nome)

    # ── ESTILOS ───────────────────────────────────────────────────

    def registrar_estilo(self, nome: str, params: dict):
        """Registra parâmetros de estilo aprovado (preset cinematográfico, cor, etc.)."""
        self._db["estilos"][nome] = params
        self._save()

    def set_preset(self, preset_nome: str):
        self._db["preset_cinematografico"] = preset_nome
        self._save()

    def get_preset(self) -> Optional[str]:
        return self._db.get("preset_cinematografico")

    # ── PALETA ────────────────────────────────────────────────────

    def set_paleta(self, cores: list[str]):
        """Define paleta de cores global do projeto (lista de hex)."""
        self._db["paleta_global"] = cores
        self._save()

    def get_paleta(self) -> list[str]:
        return self._db.get("paleta_global", [])

    # ── HISTÓRICO DE CENAS ────────────────────────────────────────

    def registrar_cena(self, idx: int, resumo: dict):
        """Registra dados visuais da cena no histórico."""
        self._db["historico_cenas"].append({
            "idx": idx,
            **resumo,
        })
        self._save()

    def ultima_cena(self) -> Optional[dict]:
        hist = self._db.get("historico_cenas", [])
        return hist[-1] if hist else None


# ─────────────────────────────────────────────────────────────────
#  GERAÇÃO DE PROMPTS COM CONTINUIDADE
# ─────────────────────────────────────────────────────────────────

def gerar_prompt_com_continuidade(
    cena: dict,
    db: VisualConsistencyDB,
    prompt_base: str = "",
) -> str:
    """
    Enriquece um prompt visual com informações de continuidade do banco de referências.

    Args:
        cena: Dict da cena com 'narracao', 'personagens', 'cenario', etc.
        db: Banco de referências do projeto.
        prompt_base: Prompt base da cena (se já gerado pelo cinematic_director).

    Returns:
        Prompt enriquecido com contexto de continuidade.
    """
    partes = []

    # Preset cinematográfico
    preset = db.get_preset()
    if preset:
        partes.append(f"cinematic style: {preset}")

    # Personagens da cena
    personagens_cena = cena.get("personagens", [])
    for nome_pers in personagens_cena:
        pers = db.get_personagem(nome_pers)
        if pers:
            partes.append(f"character '{nome_pers}': {pers['descricao']}")
            db.incrementar_aparicao(nome_pers)

    # Cenário
    cenario_nome = cena.get("cenario", "")
    if cenario_nome:
        cenario = db.get_cenario(cenario_nome)
        if cenario:
            partes.append(f"setting: {cenario['descricao']}, lighting: {cenario['iluminacao']}")

    # Paleta de cores
    paleta = db.get_paleta()
    if paleta:
        partes.append(f"color palette: {', '.join(paleta[:4])}")

    # Prompt base ou narracao
    base = prompt_base or cena.get("narracao", "")
    if base:
        partes.append(base)

    # Marcação de conteúdo IA (obrigatório)
    partes.append("AI-generated content — DARK STUDIO AAA")
    partes.append("NO PRESENTER, NO TEXT OVERLAY, NO WATERMARK")

    return ", ".join(partes)


# ─────────────────────────────────────────────────────────────────
#  EXTRAÇÃO DE PALETA (sem GPU — análise de cores básica)
# ─────────────────────────────────────────────────────────────────

def extrair_paleta_imagem(imagem_path: Path, n_cores: int = 5) -> list[str]:
    """
    Extrai paleta dominante de uma imagem usando Pillow + quantização.
    Retorna lista de cores em hex.
    """
    try:
        from PIL import Image

        img = Image.open(imagem_path).convert("RGB")
        img = img.resize((150, 150))  # Reduz para velocidade
        img_quantized = img.quantize(colors=n_cores)
        palette_data = img_quantized.getpalette()

        cores = []
        for i in range(n_cores):
            r = palette_data[i * 3]
            g = palette_data[i * 3 + 1]
            b = palette_data[i * 3 + 2]
            cores.append(f"#{r:02x}{g:02x}{b:02x}")
        return cores
    except ImportError:
        return ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#ffffff"]
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────
#  VALIDAÇÃO DE CONSISTÊNCIA
# ─────────────────────────────────────────────────────────────────

def validar_consistencia_roteiro(cenas: list[dict], db: VisualConsistencyDB) -> dict:
    """
    Verifica consistência visual entre todas as cenas do roteiro.

    Returns:
        Dict com 'ok', 'avisos', 'erros'.
    """
    avisos = []
    erros = []

    # Verifica se preset está definido
    if not db.get_preset():
        avisos.append("Preset cinematográfico não definido. Usando padrão.")

    # Verifica personagens mencionados mas não registrados
    for i, cena in enumerate(cenas):
        for nome_pers in cena.get("personagens", []):
            if not db.get_personagem(nome_pers):
                avisos.append(f"Cena {i+1}: personagem '{nome_pers}' não registrado no banco.")

        # Verifica cenário
        cenario = cena.get("cenario", "")
        if cenario and not db.get_cenario(cenario):
            avisos.append(f"Cena {i+1}: cenário '{cenario}' não registrado.")

    return {
        "ok": len(erros) == 0,
        "avisos": avisos,
        "erros": erros,
        "total_cenas": len(cenas),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  SETUP PADRÃO PARA CANAL
# ─────────────────────────────────────────────────────────────────

PALETAS_POR_NICHO = {
    "psicologia":   ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#f5f5f5"],
    "misterio":     ["#0d0d0d", "#1a0533", "#6b21a8", "#c084fc", "#f0abfc"],
    "historia":     ["#2c1810", "#8b4513", "#d4a853", "#f5e6c8", "#1a1a1a"],
    "natureza":     ["#0a4523", "#1a6b3c", "#2d9e5f", "#7ec8a0", "#c8f0d8"],
    "tecnologia":   ["#050510", "#0a0a2e", "#1a1a4e", "#00d4ff", "#7c3aed"],
    "batalhas":     ["#1a0a0a", "#3d0b0b", "#7c2020", "#c0392b", "#f5c0c0"],
    "educacao":     ["#f0f4f8", "#2563eb", "#1d4ed8", "#dbeafe", "#1e40af"],
    "relaxamento":  ["#e8f5e9", "#a5d6a7", "#4caf50", "#388e3c", "#f1f8e9"],
    "default":      ["#1a1a2e", "#16213e", "#0f3460", "#e94560", "#ffffff"],
}


def setup_projeto(
    output_dir: Path,
    canal_config: dict,
    preset_nome: str = None,
) -> VisualConsistencyDB:
    """
    Inicializa banco de consistência para um projeto.

    Args:
        output_dir: Diretório de saída do projeto.
        canal_config: Configuração do canal (nicho, etc.).
        preset_nome: Nome do preset cinematográfico.

    Returns:
        VisualConsistencyDB inicializado.
    """
    db = VisualConsistencyDB(output_dir)

    # Paleta baseada no nicho
    nicho = canal_config.get("nicho", "default")
    paleta = PALETAS_POR_NICHO.get(nicho, PALETAS_POR_NICHO["default"])
    db.set_paleta(paleta)

    # Preset cinematográfico
    if preset_nome:
        db.set_preset(preset_nome)

    # Estilo padrão do canal
    estilo = canal_config.get("estilo_visual", {})
    if estilo:
        db.registrar_estilo("canal_padrao", estilo)

    return db


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_visual_consistency() -> dict:
    try:
        from PIL import Image
        pillow_ok = True
    except ImportError:
        pillow_ok = False

    return {
        "status": "ok",
        "pillow": pillow_ok,
        "funcoes": [
            "registrar_personagem",
            "registrar_cenario",
            "gerar_prompt_com_continuidade",
            "extrair_paleta_imagem",
            "validar_consistencia_roteiro",
            "setup_projeto",
        ],
        "paletas_nichos": list(PALETAS_POR_NICHO.keys()),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
