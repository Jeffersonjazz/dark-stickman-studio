"""
DARK ASSET MANAGER — Gestão de assets audiovisuais
FASE: Asset Management | DARK STUDIO AAA v1.4.0

Responsabilidades:
  - Banco SQLite de assets (imagens, vídeos, áudio, fontes, b-roll)
  - Índice por tipo, canal, licença e tags
  - Controle de aprovação para produção
  - Escanear pastas e registrar automaticamente
  - Exportar relatório de assets disponíveis

Licenças suportadas:
  - CC0: domínio público — uso livre sem atribuição
  - CC-BY: Creative Commons com atribuição
  - MIT: código e fontes
  - proprietary: uso restrito

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════
# EXTENSÕES POR TIPO DE ASSET
# ═══════════════════════════════════════════════════════
EXTENSOES_TIPO: Dict[str, List[str]] = {
    "image":  [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"],
    "video":  [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".m4v"],
    "audio":  [".mp3", ".wav", ".ogg", ".aac", ".flac", ".m4a", ".opus"],
    "font":   [".ttf", ".otf", ".woff", ".woff2"],
    "broll":  [],  # subconjunto de vídeo — classificado manualmente
}

_EXT_PARA_TIPO: Dict[str, str] = {}
for _tipo, _exts in EXTENSOES_TIPO.items():
    for _ext in _exts:
        _EXT_PARA_TIPO[_ext] = _tipo


# ═══════════════════════════════════════════════════════
# CLASSE PRINCIPAL
# ═══════════════════════════════════════════════════════
class DarkAssetManager:
    """
    Gerencia o banco de assets audiovisuais do DARK STUDIO AAA.

    Uso rápido:
        am = DarkAssetManager()
        am.escanear_pasta("producao/")
        am.escanear_pasta("assets/broll/", tipo_forcado="broll", licenca="CC0")
        print(am.estatisticas())
    """

    def __init__(self, db_path: str = "dados/assets.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._criar_schema()

    # ── Schema ──────────────────────────────────────────
    def _criar_schema(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nome        TEXT NOT NULL,
                tipo        TEXT NOT NULL,
                canal       TEXT DEFAULT '',
                nicho       TEXT DEFAULT '',
                tags        TEXT DEFAULT '[]',
                caminho     TEXT UNIQUE NOT NULL,
                tamanho_mb  REAL DEFAULT 0.0,
                licenca     TEXT DEFAULT 'CC0',
                criado_em   TEXT NOT NULL,
                usado_em    TEXT DEFAULT '[]',
                qualidade   INTEGER DEFAULT 3,
                aprovado    INTEGER DEFAULT 0
            )
        """)
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_tipo    ON assets(tipo)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_canal   ON assets(canal)"
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_licenca ON assets(licenca)"
        )
        self._conn.commit()

    # ── Registrar ────────────────────────────────────────
    def registrar(
        self,
        caminho: str,
        tipo: str,
        canal: str = "",
        nicho: str = "",
        tags: List[str] = None,
        licenca: str = "CC0",
        qualidade: int = 3,
    ) -> Dict[str, Any]:
        """Registra um asset. Se já existe (mesmo caminho), atualiza metadados."""
        p = Path(caminho)
        if not p.exists():
            return {"status": "erro", "motivo": f"Arquivo não encontrado: {caminho}"}

        tamanho_mb = round(p.stat().st_size / 1_048_576, 4)
        tags_json = json.dumps(tags or [], ensure_ascii=False)
        agora = datetime.now().isoformat()

        cur = self._conn.execute(
            "SELECT id FROM assets WHERE caminho = ?", (str(p),)
        )
        row = cur.fetchone()

        if row:
            self._conn.execute(
                """UPDATE assets SET tipo=?, canal=?, nicho=?, tags=?,
                   tamanho_mb=?, licenca=?, qualidade=?
                   WHERE caminho=?""",
                (tipo, canal, nicho, tags_json, tamanho_mb, licenca, qualidade, str(p)),
            )
            self._conn.commit()
            return {"status": "ok", "acao": "atualizado", "id": row["id"], "nome": p.name}

        self._conn.execute(
            """INSERT INTO assets
               (nome, tipo, canal, nicho, tags, caminho, tamanho_mb, licenca, criado_em, qualidade)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (p.name, tipo, canal, nicho, tags_json, str(p), tamanho_mb, licenca, agora, qualidade),
        )
        self._conn.commit()
        asset_id = self._conn.execute(
            "SELECT id FROM assets WHERE caminho=?", (str(p),)
        ).fetchone()["id"]
        return {"status": "ok", "acao": "registrado", "id": asset_id, "nome": p.name}

    # ── Buscar ───────────────────────────────────────────
    def buscar(
        self,
        tipo: Optional[str] = None,
        canal: Optional[str] = None,
        tags: List[str] = None,
        licenca: Optional[str] = None,
        aprovado: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Retorna lista de assets que correspondem aos filtros."""
        conds, params = [], []

        if tipo:
            conds.append("tipo = ?"); params.append(tipo)
        if canal:
            conds.append("canal = ?"); params.append(canal)
        if licenca:
            conds.append("licenca = ?"); params.append(licenca)
        if aprovado is not None:
            conds.append("aprovado = ?"); params.append(1 if aprovado else 0)

        where = ("WHERE " + " AND ".join(conds)) if conds else ""
        rows = self._conn.execute(
            f"SELECT * FROM assets {where} ORDER BY qualidade DESC, criado_em DESC",
            params,
        ).fetchall()

        resultado = [dict(r) for r in rows]

        # Filtro por tags (pós-query — mais simples que JSON em SQLite)
        if tags:
            filtrado = []
            for a in resultado:
                asset_tags = json.loads(a.get("tags", "[]"))
                if any(t in asset_tags for t in tags):
                    filtrado.append(a)
            resultado = filtrado

        return resultado

    # ── Aprovar ──────────────────────────────────────────
    def aprovar(self, asset_id: int) -> Dict[str, Any]:
        """Marca asset como aprovado para produção."""
        cur = self._conn.execute(
            "UPDATE assets SET aprovado=1 WHERE id=?", (asset_id,)
        )
        self._conn.commit()
        if cur.rowcount == 0:
            return {"status": "erro", "motivo": f"Asset id={asset_id} não encontrado"}
        return {"status": "ok", "aprovado": asset_id}

    # ── Estatísticas ─────────────────────────────────────
    def estatisticas(self) -> Dict[str, Any]:
        """Resumo do banco de assets."""
        total = self._conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        aprovados = self._conn.execute(
            "SELECT COUNT(*) FROM assets WHERE aprovado=1"
        ).fetchone()[0]
        total_mb = self._conn.execute(
            "SELECT COALESCE(SUM(tamanho_mb),0) FROM assets"
        ).fetchone()[0]

        por_tipo = {}
        for row in self._conn.execute(
            "SELECT tipo, COUNT(*) as n FROM assets GROUP BY tipo"
        ):
            por_tipo[row["tipo"]] = row["n"]

        por_canal = {}
        for row in self._conn.execute(
            "SELECT canal, COUNT(*) as n FROM assets WHERE canal != '' GROUP BY canal"
        ):
            por_canal[row["canal"]] = row["n"]

        por_licenca = {}
        for row in self._conn.execute(
            "SELECT licenca, COUNT(*) as n FROM assets GROUP BY licenca"
        ):
            por_licenca[row["licenca"]] = row["n"]

        return {
            "status": "ok",
            "total_assets": total,
            "aprovados": aprovados,
            "total_mb": round(total_mb, 2),
            "por_tipo": por_tipo,
            "por_canal": por_canal,
            "por_licenca": por_licenca,
        }

    # ── Escanear pasta ───────────────────────────────────
    def escanear_pasta(
        self,
        pasta: str,
        canal: str = "",
        licenca: str = "CC0",
        tipo_forcado: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Escaneia recursivamente a pasta e registra todos os arquivos de mídia.
        tipo_forcado: sobrescreve detecção automática (útil para 'broll').
        """
        p = Path(pasta)
        if not p.exists():
            return {"status": "erro", "motivo": f"Pasta não encontrada: {pasta}"}

        registrados = atualizados = erros = 0

        for arquivo in p.rglob("*"):
            if not arquivo.is_file():
                continue
            ext = arquivo.suffix.lower()
            tipo = tipo_forcado or _EXT_PARA_TIPO.get(ext)
            if not tipo:
                continue  # ignora extensões desconhecidas

            try:
                resultado = self.registrar(
                    caminho=str(arquivo),
                    tipo=tipo,
                    canal=canal,
                    licenca=licenca,
                )
                if resultado.get("acao") == "registrado":
                    registrados += 1
                elif resultado.get("acao") == "atualizado":
                    atualizados += 1
                else:
                    erros += 1
            except Exception:
                erros += 1

        return {
            "status": "ok",
            "pasta": str(p),
            "registrados": registrados,
            "atualizados": atualizados,
            "erros": erros,
            "total": registrados + atualizados,
        }

    # ── Exportar relatório ───────────────────────────────
    def exportar_relatorio(
        self, output_path: str = "dados/relatorio_assets.json"
    ) -> Dict[str, Any]:
        """Exporta JSON completo de todos os assets."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        assets = [dict(r) for r in self._conn.execute(
            "SELECT * FROM assets ORDER BY tipo, canal, nome"
        ).fetchall()]

        # Desserializar tags e usado_em para JSON real
        for a in assets:
            a["tags"] = json.loads(a.get("tags", "[]"))
            a["usado_em"] = json.loads(a.get("usado_em", "[]"))

        relatorio = {
            "gerado_em": datetime.now().isoformat(),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "estatisticas": self.estatisticas(),
            "assets": assets,
        }

        out.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))
        return {"status": "ok", "arquivo": str(out), "total": len(assets)}

    # ── Context manager ──────────────────────────────────
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._conn.close()


# ═══════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    print("=" * 60)
    print("DARK ASSET MANAGER — auto-teste")
    print("=" * 60)

    am = DarkAssetManager()

    # Escanear pasta de produção
    r = am.escanear_pasta("producao/")
    print(f"Scan producao/: {r}")

    # Escanear pasta de dados
    r2 = am.escanear_pasta("dados/")
    print(f"Scan dados/:    {r2}")

    stats = am.estatisticas()
    print(f"\nEstatísticas:")
    print(f"  Total assets : {stats['total_assets']}")
    print(f"  Total MB     : {stats['total_mb']}")
    print(f"  Por tipo     : {stats['por_tipo']}")
    print(f"  Por licença  : {stats['por_licenca']}")

    rel = am.exportar_relatorio()
    print(f"\nRelatório exportado: {rel['arquivo']} ({rel['total']} assets)")
    print("\n✅ DARK ASSET MANAGER — OK")
