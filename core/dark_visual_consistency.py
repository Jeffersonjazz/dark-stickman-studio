"""
DARK VISUAL CONSISTENCY — Fase 8
Sistema de continuidade audiovisual entre cenas
Clone funcional de: Adobe Sensei (consistency), Midjourney style reference

Mantém por projeto:
  - Paleta de cores dominante (extração via Pillow/colorthief)
  - Perfil de personagens (descrição + imagem de referência)
  - Ambientes e cenários registrados
  - Estilo de fotografia (lighting, angle, mood)
  - Diretrizes de color grade

Integra com:
  - DarkImageEngine: prompts enriquecidos com referências do projeto
  - DarkCinemaEditor: color grade consistente entre cenas
  - DarkVideoEngine: parâmetros de câmera consistentes

ai_generated: True — OBRIGATÓRIO
"""

import json
import hashlib
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

PROJETOS_DIR = Path("/tmp/dark-studio/projetos")


class DarkVisualConsistency:
    """
    Banco de referências visuais por projeto.
    Garante continuidade entre todas as cenas de um vídeo.
    """

    def __init__(self):
        PROJETOS_DIR.mkdir(parents=True, exist_ok=True)

    # ── CRUD de projetos ──────────────────────────────────────────────────────

    def criar_projeto(
        self,
        nome: str,
        nicho: str = "geral",
        estilo_cinematico: str = "cinematico",
        paleta_descricao: str = "",
        resolucao: str = "1080p",
    ) -> dict:
        """Cria banco de referências para um novo projeto."""
        projeto_id = hashlib.md5(f"{nome}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        projeto_dir = PROJETOS_DIR / projeto_id
        projeto_dir.mkdir(parents=True, exist_ok=True)
        (projeto_dir / "refs").mkdir(exist_ok=True)
        (projeto_dir / "personagens").mkdir(exist_ok=True)
        (projeto_dir / "cenarios").mkdir(exist_ok=True)

        dados = {
            "id": projeto_id,
            "nome": nome,
            "nicho": nicho,
            "estilo_cinematico": estilo_cinematico,
            "resolucao": resolucao,
            "criado_em": datetime.now().isoformat(),
            "paleta": {
                "descricao": paleta_descricao or f"Paleta {nicho} cinematográfica",
                "cores_dominantes": [],
                "color_grade_preset": self._nicho_para_preset(nicho),
            },
            "camera": {
                "angulos_aprovados": ["eye_level", "slight_low"],
                "lentes": ["wide", "standard"],
                "profundidade_campo": "raso",
                "movimento": "suave",
            },
            "iluminacao": {
                "estilo": "natural" if nicho in ("natureza", "historia") else "cinematica",
                "temperatura": "quente" if nicho in ("historia", "misterio") else "neutra",
                "contraste": "alto" if nicho in ("misterio", "tecnologia") else "médio",
            },
            "personagens": {},
            "cenarios": {},
            "estilos_aprovados": [],
            "prompt_sufixo": self._gerar_sufixo_prompt(nicho, estilo_cinematico),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

        self._salvar(projeto_id, dados)
        return {"status": "ok", "projeto_id": projeto_id, "dados": dados}

    def carregar_projeto(self, projeto_id: str) -> dict:
        """Carrega banco de referências do projeto."""
        dados = self._carregar(projeto_id)
        if dados is None:
            return {"status": "erro", "mensagem": f"Projeto {projeto_id} não encontrado"}
        return {"status": "ok", "projeto_id": projeto_id, "dados": dados}

    def listar_projetos(self) -> dict:
        """Lista todos os projetos com resumo."""
        projetos = []
        for d in PROJETOS_DIR.iterdir():
            if d.is_dir():
                dados = self._carregar(d.name)
                if dados:
                    projetos.append({
                        "id": d.name,
                        "nome": dados.get("nome", "—"),
                        "nicho": dados.get("nicho", "—"),
                        "personagens": len(dados.get("personagens", {})),
                        "cenarios": len(dados.get("cenarios", {})),
                    })
        return {"status": "ok", "projetos": projetos, "total": len(projetos)}

    # ── Personagens ───────────────────────────────────────────────────────────

    def registrar_personagem(
        self,
        projeto_id: str,
        nome: str,
        descricao: str,
        aparencia: str,
        vestuario: str = "",
        imagem_ref: Optional[str] = None,
    ) -> dict:
        """Registra um personagem com referências visuais aprovadas."""
        dados = self._carregar(projeto_id)
        if dados is None:
            return {"status": "erro", "mensagem": "Projeto não encontrado"}

        char_id = nome.lower().replace(" ", "_")
        char_dir = PROJETOS_DIR / projeto_id / "personagens" / char_id
        char_dir.mkdir(parents=True, exist_ok=True)

        # Copiar imagem de referência se fornecida
        ref_path = None
        if imagem_ref and Path(imagem_ref).exists():
            dest = char_dir / f"ref_{Path(imagem_ref).name}"
            shutil.copy2(imagem_ref, dest)
            ref_path = str(dest)

        dados["personagens"][char_id] = {
            "nome": nome,
            "descricao": descricao,
            "aparencia": aparencia,
            "vestuario": vestuario,
            "imagem_ref": ref_path,
            "prompt_descricao": self._gerar_prompt_personagem(nome, aparencia, vestuario),
            "cenas_participadas": 0,
        }

        self._salvar(projeto_id, dados)
        return {
            "status": "ok",
            "char_id": char_id,
            "prompt_descricao": dados["personagens"][char_id]["prompt_descricao"],
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── Cenários ──────────────────────────────────────────────────────────────

    def registrar_cenario(
        self,
        projeto_id: str,
        nome: str,
        descricao: str,
        iluminacao: str = "",
        horario: str = "dia",
        clima: str = "claro",
        imagem_ref: Optional[str] = None,
    ) -> dict:
        """Registra um cenário/ambiente visual aprovado."""
        dados = self._carregar(projeto_id)
        if dados is None:
            return {"status": "erro", "mensagem": "Projeto não encontrado"}

        cen_id = nome.lower().replace(" ", "_")
        cen_dir = PROJETOS_DIR / projeto_id / "cenarios" / cen_id
        cen_dir.mkdir(parents=True, exist_ok=True)

        ref_path = None
        if imagem_ref and Path(imagem_ref).exists():
            dest = cen_dir / f"ref_{Path(imagem_ref).name}"
            shutil.copy2(imagem_ref, dest)
            ref_path = str(dest)

        dados["cenarios"][cen_id] = {
            "nome": nome,
            "descricao": descricao,
            "iluminacao": iluminacao,
            "horario": horario,
            "clima": clima,
            "imagem_ref": ref_path,
            "prompt_descricao": self._gerar_prompt_cenario(descricao, iluminacao, horario, clima),
        }

        self._salvar(projeto_id, dados)
        return {
            "status": "ok",
            "cen_id": cen_id,
            "prompt_descricao": dados["cenarios"][cen_id]["prompt_descricao"],
            "ai_generated": True,
        }

    # ── Enriquecimento de prompt ──────────────────────────────────────────────

    def enriquecer_prompt(
        self,
        projeto_id: str,
        prompt_base: str,
        personagens: list[str] = None,
        cenario: str = None,
        cena_numero: int = 0,
    ) -> dict:
        """
        Enriquece prompt de geração de imagem/vídeo com referências do projeto.
        Garante consistência visual entre cenas.
        """
        dados = self._carregar(projeto_id)
        if dados is None:
            return {
                "status": "ok",
                "prompt_enriquecido": prompt_base,
                "aviso": "Projeto não encontrado, prompt sem enriquecimento",
                "ai_generated": True,
            }

        partes = [prompt_base]

        # Adicionar descrição de personagens
        if personagens:
            for char_id in personagens:
                char = dados["personagens"].get(char_id)
                if char:
                    partes.append(char["prompt_descricao"])

        # Adicionar cenário
        if cenario:
            cen = dados["cenarios"].get(cenario)
            if cen:
                partes.append(cen["prompt_descricao"])

        # Adicionar sufixo de estilo do projeto
        sufixo = dados.get("prompt_sufixo", "")
        if sufixo:
            partes.append(sufixo)

        # Adicionar diretriz de câmera
        cam = dados.get("camera", {})
        angulo = cam.get("angulos_aprovados", ["eye_level"])[0]
        profundidade = cam.get("profundidade_campo", "raso")
        partes.append(f"{angulo} shot, {profundidade} depth of field")

        # Adicionar diretrizes de iluminação
        ilu = dados.get("iluminacao", {})
        estilo_ilu = ilu.get("estilo", "cinematica")
        temperatura = ilu.get("temperatura", "neutra")
        partes.append(f"{estilo_ilu} lighting, {temperatura} color temperature")

        prompt_final = ", ".join(p.strip() for p in partes if p.strip())

        return {
            "status": "ok",
            "prompt_original": prompt_base,
            "prompt_enriquecido": prompt_final,
            "projeto_nome": dados.get("nome"),
            "color_grade_preset": dados["paleta"]["color_grade_preset"],
            "personagens_usados": personagens or [],
            "cenario_usado": cenario,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def verificar_consistencia(self, projeto_id: str, cena_atual: dict, cena_anterior: dict) -> dict:
        """
        Verifica se uma cena é consistente com a anterior.
        Retorna score de consistência e alertas.
        """
        alertas = []
        score = 100

        # Verificar nicho (basic)
        if cena_atual.get("nicho") != cena_anterior.get("nicho"):
            alertas.append("Nicho diferente entre cenas")
            score -= 20

        # Verificar personagens
        chars_ant = set(cena_anterior.get("personagens", []))
        chars_atu = set(cena_atual.get("personagens", []))
        novos = chars_atu - chars_ant
        if novos:
            alertas.append(f"Personagens novos sem introdução: {novos}")
            score -= 10

        # Verificar cenário
        if cena_atual.get("cenario") != cena_anterior.get("cenario"):
            alertas.append("Mudança de cenário — verificar corte")
            score -= 5

        return {
            "status": "ok",
            "score_consistencia": max(0, score),
            "alertas": alertas,
            "aprovado": score >= 70,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _gerar_prompt_personagem(self, nome: str, aparencia: str, vestuario: str) -> str:
        partes = [aparencia]
        if vestuario:
            partes.append(f"wearing {vestuario}")
        return ", ".join(partes)

    def _gerar_prompt_cenario(self, descricao: str, iluminacao: str, horario: str, clima: str) -> str:
        partes = [descricao]
        if horario:
            partes.append(f"{horario} time")
        if clima:
            partes.append(clima)
        if iluminacao:
            partes.append(iluminacao)
        return ", ".join(partes)

    def _gerar_sufixo_prompt(self, nicho: str, estilo: str) -> str:
        SUFIXOS = {
            "natureza": "photorealistic, nature photography, 8K, sharp details, natural colors",
            "historia": "historical documentary style, cinematic, sepia tones, film grain",
            "tecnologia": "futuristic, high-tech, blue tones, sharp, professional photography",
            "misterio": "dark atmosphere, dramatic shadows, mysterious, cinematic noir",
            "motivacao": "vibrant, energetic, warm tones, inspiring, bright",
            "geral": "cinematic, professional photography, 4K, sharp",
        }
        return SUFIXOS.get(nicho, SUFIXOS["geral"])

    def _nicho_para_preset(self, nicho: str) -> str:
        MAP = {
            "natureza": "natureza",
            "historia": "historia",
            "tecnologia": "tecnologia",
            "misterio": "misterio",
            "motivacao": "motivacao",
            "psicologia": "cinematico",
            "filosofia": "historia",
            "ciencia": "tecnologia",
            "financas": "motivacao",
            "saude": "natureza",
            "geral": "cinematico",
        }
        return MAP.get(nicho, "cinematico")

    def _salvar(self, projeto_id: str, dados: dict):
        path = PROJETOS_DIR / projeto_id / "projeto.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def _carregar(self, projeto_id: str) -> Optional[dict]:
        path = PROJETOS_DIR / projeto_id / "projeto.json"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def status(self) -> dict:
        projetos = self.listar_projetos()
        return {
            "status": "ok",
            "total_projetos": projetos["total"],
            "projetos_dir": str(PROJETOS_DIR),
            "funcionalidades": [
                "criar_projeto",
                "registrar_personagem",
                "registrar_cenario",
                "enriquecer_prompt",
                "verificar_consistencia",
            ],
            "custo_mensal_brl": 0.00,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


if __name__ == "__main__":
    import json
    print("=== DARK VISUAL CONSISTENCY — Diagnóstico ===")
    vc = DarkVisualConsistency()
    print(json.dumps(vc.status(), indent=2, ensure_ascii=False))

    # Teste básico
    res = vc.criar_projeto("Série Mistérios da História", "historia", "cinematico")
    pid = res["projeto_id"]
    print(f"\nProjeto criado: {pid}")

    res2 = vc.registrar_personagem(pid, "Narrador", "narrador off", "voz grave e misteriosa")
    print(f"Personagem: {res2['prompt_descricao']}")

    res3 = vc.enriquecer_prompt(pid, "ancient Roman ruins at sunset")
    print(f"Prompt enriquecido: {res3['prompt_enriquecido'][:120]}...")
