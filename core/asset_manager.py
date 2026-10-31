"""
DARK CREATIVE LAB — AGENTE ASSET MANAGER
Administra imagens, vídeos, músicas, fontes, licenças e arquivos de produção.

Funções:
- Registro e catalogação de assets por tipo e canal
- Busca de assets por tipo, tag, canal ou nicho
- Licenciamento e validação de uso
- Organização automática de diretórios de produção
- Relatório de assets disponíveis

Licença: MIT — DARK CREATIVE LAB
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations
import json
import hashlib
import mimetypes
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────
#  CONSTANTES
# ─────────────────────────────────────────────────────────────────

ASSET_TYPES = {
    "imagem":   [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".svg"],
    "video":    [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "audio":    [".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a"],
    "fonte":    [".ttf", ".otf", ".woff", ".woff2"],
    "legenda":  [".srt", ".vtt", ".ass", ".sub"],
    "projeto":  [".json", ".yaml", ".yml"],
    "documento":[".pdf", ".txt", ".md", ".docx"],
}

LICENCAS_VALIDAS = [
    "MIT", "CC0", "CC-BY", "CC-BY-SA", "CC-BY-NC", "Apache-2.0",
    "GPL-3.0", "LGPL-2.1", "Proprio", "Royalty-Free", "Custom",
]

ASSET_DB_NAME = ".asset_db.json"


# ─────────────────────────────────────────────────────────────────
#  BANCO DE ASSETS
# ─────────────────────────────────────────────────────────────────

class AssetDB:
    """
    Banco de dados de assets por projeto.
    Persiste em JSON: {output_dir}/.asset_db.json
    """

    def __init__(self, projeto_dir: Path):
        self.projeto_dir = Path(projeto_dir)
        self.db_path = self.projeto_dir / ASSET_DB_NAME
        self._db = self._load()

    def _load(self) -> dict:
        if self.db_path.exists():
            try:
                return json.loads(self.db_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "assets": {},
            "total": 0,
            "criado_em": _agora(),
            "atualizado_em": _agora(),
        }

    def _save(self):
        self.projeto_dir.mkdir(parents=True, exist_ok=True)
        self._db["atualizado_em"] = _agora()
        self._db["total"] = len(self._db["assets"])
        self.db_path.write_text(
            json.dumps(self._db, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def registrar(self, asset_id: str, meta: dict):
        self._db["assets"][asset_id] = meta
        self._save()

    def buscar(self, asset_id: str) -> Optional[dict]:
        return self._db["assets"].get(asset_id)

    def listar(
        self,
        tipo: str = None,
        canal: str = None,
        tag: str = None,
        licenca: str = None,
    ) -> list[dict]:
        resultados = []
        for aid, meta in self._db["assets"].items():
            if tipo and meta.get("tipo") != tipo:
                continue
            if canal and meta.get("canal") != canal:
                continue
            if tag and tag not in meta.get("tags", []):
                continue
            if licenca and meta.get("licenca") != licenca:
                continue
            resultados.append({"id": aid, **meta})
        return resultados

    def remover(self, asset_id: str) -> bool:
        if asset_id in self._db["assets"]:
            del self._db["assets"][asset_id]
            self._save()
            return True
        return False

    def estatisticas(self) -> dict:
        por_tipo: dict = {}
        por_canal: dict = {}
        for meta in self._db["assets"].values():
            t = meta.get("tipo", "desconhecido")
            por_tipo[t] = por_tipo.get(t, 0) + 1
            c = meta.get("canal", "global")
            por_canal[c] = por_canal.get(c, 0) + 1
        return {
            "total": self._db["total"],
            "por_tipo": por_tipo,
            "por_canal": por_canal,
        }


# ─────────────────────────────────────────────────────────────────
#  FUNÇÕES PÚBLICAS
# ─────────────────────────────────────────────────────────────────

def registrar_asset(
    arquivo: Path,
    projeto_dir: Path,
    canal: str = "global",
    tags: list[str] = None,
    licenca: str = "MIT",
    descricao: str = "",
    copiar: bool = False,
) -> dict:
    """
    Registra um arquivo no banco de assets do projeto.

    Args:
        arquivo: Caminho para o arquivo.
        projeto_dir: Diretório raiz do projeto.
        canal: ID do canal dono do asset.
        tags: Lista de tags para busca.
        licenca: Licença do asset.
        descricao: Descrição curta.
        copiar: Se True, copia o arquivo para o diretório de assets do projeto.

    Returns:
        Dict com id, tipo, caminho, metadados.
    """
    arquivo = Path(arquivo)
    if not arquivo.exists():
        return {
            "status": "error",
            "erro": f"Arquivo não encontrado: {arquivo}",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # Determina tipo
    tipo = _detectar_tipo(arquivo)

    # Calcula hash MD5 para deduplicação
    asset_id = _hash_arquivo(arquivo)

    # Copia para diretório organizado, se solicitado
    destino = arquivo
    if copiar:
        dir_assets = Path(projeto_dir) / "assets" / tipo
        dir_assets.mkdir(parents=True, exist_ok=True)
        destino = dir_assets / arquivo.name
        if not destino.exists():
            shutil.copy2(arquivo, destino)

    meta = {
        "tipo": tipo,
        "nome": arquivo.name,
        "caminho": str(destino),
        "tamanho_bytes": arquivo.stat().st_size,
        "extensao": arquivo.suffix.lower(),
        "canal": canal,
        "tags": tags or [],
        "licenca": licenca,
        "descricao": descricao,
        "registrado_em": _agora(),
        "ai_generated": True,
    }

    db = AssetDB(projeto_dir)
    db.registrar(asset_id, meta)

    return {
        "status": "ok",
        "id": asset_id,
        "tipo": tipo,
        "nome": arquivo.name,
        "caminho": str(destino),
        "licenca": licenca,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def buscar_asset(
    projeto_dir: Path,
    asset_id: str = None,
    tipo: str = None,
    canal: str = None,
    tag: str = None,
    licenca: str = None,
) -> dict:
    """
    Busca assets no banco por ID ou filtros.

    Returns:
        Dict com lista de resultados.
    """
    db = AssetDB(projeto_dir)

    if asset_id:
        meta = db.buscar(asset_id)
        if meta:
            return {
                "status": "ok",
                "encontrado": True,
                "asset": {"id": asset_id, **meta},
                "ai_generated": True,
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }
        return {
            "status": "ok",
            "encontrado": False,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    resultados = db.listar(tipo=tipo, canal=canal, tag=tag, licenca=licenca)
    return {
        "status": "ok",
        "total": len(resultados),
        "assets": resultados,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def organizar_projeto(projeto_dir: Path, canal_config: dict) -> dict:
    """
    Cria estrutura de diretórios organizada para um projeto.

    Estrutura:
    projeto_dir/
    ├── assets/
    │   ├── imagem/
    │   ├── video/
    │   ├── audio/
    │   ├── fonte/
    │   └── legenda/
    ├── clips/
    ├── audio/
    ├── legenda/
    ├── thumbnail/
    └── export/

    Returns:
        Dict com diretórios criados.
    """
    projeto_dir = Path(projeto_dir)
    dirs = {
        "assets_imagem":  projeto_dir / "assets" / "imagem",
        "assets_video":   projeto_dir / "assets" / "video",
        "assets_audio":   projeto_dir / "assets" / "audio",
        "assets_fonte":   projeto_dir / "assets" / "fonte",
        "assets_legenda": projeto_dir / "assets" / "legenda",
        "clips":          projeto_dir / "clips",
        "audio":          projeto_dir / "audio",
        "legenda":        projeto_dir / "legenda",
        "thumbnail":      projeto_dir / "thumbnail",
        "export":         projeto_dir / "export",
        "motion":         projeto_dir / "motion",
    }
    criados = []
    for nome, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        criados.append(str(path))

    # Gera manifesto do projeto
    manifesto = {
        "canal": canal_config.get("id", "desconhecido"),
        "nome": canal_config.get("nome", ""),
        "nicho": canal_config.get("nicho", ""),
        "criado_em": _agora(),
        "estrutura": {k: str(v) for k, v in dirs.items()},
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
    manifesto_path = projeto_dir / "manifesto.json"
    manifesto_path.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return {
        "status": "ok",
        "projeto_dir": str(projeto_dir),
        "diretorios_criados": len(criados),
        "manifesto": str(manifesto_path),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def listar_assets_projeto(projeto_dir: Path) -> dict:
    """Lista todos os assets registrados com estatísticas."""
    db = AssetDB(projeto_dir)
    stats = db.estatisticas()
    todos = db.listar()
    return {
        "status": "ok",
        "estatisticas": stats,
        "assets": todos,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def varredura_assets(projeto_dir: Path, canal: str = "global") -> dict:
    """
    Faz varredura no diretório e registra automaticamente assets encontrados.

    Útil para importar uma pasta de mídia existente.
    """
    projeto_dir = Path(projeto_dir)
    db = AssetDB(projeto_dir)
    registrados = 0
    erros = 0

    todas_exts = set()
    for exts in ASSET_TYPES.values():
        todas_exts.update(exts)

    for arquivo in projeto_dir.rglob("*"):
        if not arquivo.is_file():
            continue
        if arquivo.suffix.lower() not in todas_exts:
            continue
        if arquivo.name.startswith("."):
            continue
        tipo = _detectar_tipo(arquivo)
        asset_id = _hash_arquivo(arquivo)
        if db.buscar(asset_id):
            continue  # já registrado
        meta = {
            "tipo": tipo,
            "nome": arquivo.name,
            "caminho": str(arquivo),
            "tamanho_bytes": arquivo.stat().st_size,
            "extensao": arquivo.suffix.lower(),
            "canal": canal,
            "tags": [tipo],
            "licenca": "MIT",
            "descricao": f"Auto-registrado por varredura",
            "registrado_em": _agora(),
            "ai_generated": True,
        }
        db.registrar(asset_id, meta)
        registrados += 1

    return {
        "status": "ok",
        "registrados": registrados,
        "erros": erros,
        "total_no_banco": len(db._db["assets"]),
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def validar_licenca(licenca: str) -> dict:
    """Valida se uma licença é reconhecida pelo DARK CREATIVE LAB."""
    valida = licenca in LICENCAS_VALIDAS
    uso_comercial = licenca not in ["CC-BY-NC", "GPL-3.0", "LGPL-2.1"]
    return {
        "status": "ok",
        "licenca": licenca,
        "valida": valida,
        "uso_comercial_permitido": uso_comercial if valida else None,
        "licencas_suportadas": LICENCAS_VALIDAS,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


# ─────────────────────────────────────────────────────────────────
#  HELPERS PRIVADOS
# ─────────────────────────────────────────────────────────────────

def _detectar_tipo(arquivo: Path) -> str:
    ext = arquivo.suffix.lower()
    for tipo, exts in ASSET_TYPES.items():
        if ext in exts:
            return tipo
    return "outro"


def _hash_arquivo(arquivo: Path) -> str:
    """Calcula MD5 dos primeiros 64KB para identificação rápida."""
    h = hashlib.md5()
    with open(arquivo, "rb") as f:
        h.update(f.read(65536))
    return h.hexdigest()


def _agora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────
#  DIAGNÓSTICO
# ─────────────────────────────────────────────────────────────────

def check_asset_manager() -> dict:
    return {
        "status": "ok",
        "tipos_suportados": list(ASSET_TYPES.keys()),
        "extensoes_suportadas": {k: v for k, v in ASSET_TYPES.items()},
        "licencas_suportadas": LICENCAS_VALIDAS,
        "funcoes": [
            "registrar_asset",
            "buscar_asset",
            "organizar_projeto",
            "listar_assets_projeto",
            "varredura_assets",
            "validar_licenca",
        ],
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
