"""
DARK ORCHESTRATOR — Pipeline Integrado
Orquestra todos os agentes do DARK CREATIVE LAB

Fluxo completo: Roteiro → Cenas → Imagens → Vídeo → Áudio → Legendas → Montagem final
Custo: R$0,00

Agentes disponíveis:
  - DarkImageEngine      (FLUX/Midjourney clone)
  - DarkVideoEngine      (Runway/Kling clone)
  - DarkCinemaEditor     (DaVinci Resolve clone)
  - DarkAudioStudio      (ElevenLabs clone)
  - DarkMotionLab        (After Effects clone)
  - DarkVisualConsistency (consistência entre cenas)
"""

import json
import time
from pathlib import Path
from typing import Optional

OUTPUT_DIR = Path("/tmp/dark-studio/projetos")


class DarkOrchestrator:
    """
    DARK MANAGER — Orquestrador central.
    Decide qual agente usar em cada tarefa e executa o pipeline completo.
    """

    def __init__(self):
        self._agentes = {}
        self._carregar_agentes()

    def _carregar_agentes(self):
        """Carrega agentes disponíveis (lazy loading)."""
        try:
            from core.dark_image_engine import DarkImageEngine
            self._agentes["image"] = DarkImageEngine()
        except Exception as e:
            self._agentes["image"] = None

        try:
            from core.dark_video_engine import DarkVideoEngine
            self._agentes["video"] = DarkVideoEngine()
        except Exception as e:
            self._agentes["video"] = None

        try:
            from core.dark_cinema_editor import DarkCinemaEditor
            self._agentes["editor"] = DarkCinemaEditor()
        except Exception as e:
            self._agentes["editor"] = None

        try:
            from core.dark_audio_studio import DarkAudioStudio
            self._agentes["audio"] = DarkAudioStudio()
        except Exception as e:
            self._agentes["audio"] = None

        try:
            from core.dark_motion_lab import DarkMotionLab
            self._agentes["motion"] = DarkMotionLab()
        except Exception as e:
            self._agentes["motion"] = None

        try:
            from core.dark_visual_consistency import DarkVisualConsistency
            self._agentes["consistency"] = DarkVisualConsistency()
        except Exception as e:
            self._agentes["consistency"] = None

    def status_agentes(self) -> dict:
        """Retorna status de todos os agentes."""
        resultado = {}
        for nome, agente in self._agentes.items():
            if agente:
                try:
                    resultado[nome] = agente.status()
                except Exception as e:
                    resultado[nome] = {"status": "erro", "mensagem": str(e)}
            else:
                resultado[nome] = {"status": "indisponivel"}
        return {
            "status": "ok",
            "agentes": resultado,
            "custo_total_mensal_brl": 0.00,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── Pipeline completo ─────────────────────────────────────────────────────

    def produzir_video_completo(
        self,
        roteiro: str,
        titulo: str,
        nicho: str = "geral",
        orientacao: str = "horizontal",  # horizontal | shorts
        canal_nome: str = "DARK STUDIO",
        projeto_id: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> dict:
        """
        Pipeline completo: roteiro → vídeo final.
        Orquestra todos os agentes em sequência.
        """
        log = []
        t_ini = time.time()

        if output_dir is None:
            output_dir = str(OUTPUT_DIR / "pipeline_output")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # ── Passo 1: Criar projeto de consistência ─────────────────────────
        if projeto_id is None and self._agentes.get("consistency"):
            res_proj = self._agentes["consistency"].criar_projeto(titulo, nicho)
            projeto_id = res_proj.get("projeto_id")
            log.append({"passo": 1, "acao": "criar_projeto", "projeto_id": projeto_id})

        # ── Passo 2: Dividir roteiro em cenas ─────────────────────────────
        cenas = self._dividir_cenas(roteiro)
        log.append({"passo": 2, "acao": "dividir_cenas", "total_cenas": len(cenas)})

        # ── Passo 3: Narração ──────────────────────────────────────────────
        audio_paths = []
        if self._agentes.get("audio"):
            textos = [{"texto": c["texto"], "nicho": nicho, "voz": "narrador"} for c in cenas]
            narrs = self._agentes["audio"].narrar_lote(
                textos,
                output_dir=str(Path(output_dir) / "audio")
            )
            audio_paths = [r.get("audio_path") for r in narrs if r.get("audio_path")]
            log.append({"passo": 3, "acao": "narração", "clips": len(audio_paths)})

        # ── Passo 4: Gerar imagens por cena ───────────────────────────────
        imagem_paths = []
        if self._agentes.get("image"):
            for i, cena in enumerate(cenas):
                prompt = cena.get("prompt_visual", cena["texto"][:80])

                # Enriquecer prompt com consistência do projeto
                if projeto_id and self._agentes.get("consistency"):
                    enr = self._agentes["consistency"].enriquecer_prompt(projeto_id, prompt)
                    prompt = enr.get("prompt_enriquecido", prompt)

                res_img = self._agentes["image"].gerar(
                    prompt,
                    nicho=nicho,
                    output_path=str(Path(output_dir) / f"cena_{i:03d}.png")
                )
                if res_img.get("path"):
                    imagem_paths.append(res_img["path"])

            log.append({"passo": 4, "acao": "gerar_imagens", "total": len(imagem_paths)})

        # ── Passo 5: Animar imagens (Ken Burns) ───────────────────────────
        clip_paths = []
        if imagem_paths and self._agentes.get("video"):
            anims = self._agentes["video"].animar_lote(
                imagem_paths, nicho=nicho,
                output_dir=str(Path(output_dir) / "clips")
            )
            clip_paths = [r.get("path") for r in anims if r.get("path")]
            log.append({"passo": 5, "acao": "animar_clips", "total": len(clip_paths)})

        # ── Passo 6: Montar abertura e encerramento ────────────────────────
        abertura_path = None
        enc_path = None
        if self._agentes.get("motion"):
            res_ab = self._agentes["motion"].abertura(
                canal_nome, titulo, nicho=nicho,
                output_path=str(Path(output_dir) / "abertura.mp4")
            )
            abertura_path = res_ab.get("path")

            res_enc = self._agentes["motion"].encerramento(
                canal_nome, nicho=nicho,
                output_path=str(Path(output_dir) / "encerramento.mp4")
            )
            enc_path = res_enc.get("path")
            log.append({"passo": 6, "acao": "motion_graphics"})

        # ── Passo 7: Montar vídeo completo ────────────────────────────────
        todos_clips = []
        if abertura_path:
            todos_clips.append(abertura_path)
        todos_clips.extend(clip_paths)
        if enc_path:
            todos_clips.append(enc_path)

        video_final = None
        if todos_clips and self._agentes.get("editor"):
            narr_final = audio_paths[0] if audio_paths else None
            res_mont = self._agentes["editor"].montar_video(
                todos_clips,
                audio_path=narr_final,
                nicho=nicho,
                output_path=str(Path(output_dir) / "video_final.mp4")
            )
            video_final = res_mont.get("path")
            log.append({"passo": 7, "acao": "montar_video", "path": video_final})

        # ── Passo 8: Exportar em formatos ─────────────────────────────────
        exports = []
        if video_final and self._agentes.get("editor"):
            resolucoes = ["1080p", "720p"]
            if orientacao == "shorts":
                resolucoes = ["shorts"]
            exports_res = self._agentes["editor"].exportar_lote(
                video_final,
                resolucoes=resolucoes,
                output_dir=str(Path(output_dir) / "exports")
            )
            exports = [e.get("output_path") for e in exports_res if e.get("output_path")]
            log.append({"passo": 8, "acao": "exportar", "formatos": resolucoes})

        t_total = round(time.time() - t_ini, 1)

        return {
            "status": "ok",
            "titulo": titulo,
            "nicho": nicho,
            "projeto_id": projeto_id,
            "video_final": video_final,
            "exports": exports,
            "total_cenas": len(cenas),
            "clips_gerados": len(clip_paths),
            "tempo_total_s": t_total,
            "custo_brl": 0.00,
            "log": log,
            "output_dir": output_dir,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ── Tarefas individuais ───────────────────────────────────────────────────

    def gerar_imagem(self, prompt: str, nicho: str = "geral", **kw) -> dict:
        """Delega ao IMAGE ENGINE."""
        ag = self._agentes.get("image")
        if not ag:
            return {"status": "erro", "mensagem": "IMAGE ENGINE indisponível"}
        return ag.gerar(prompt, nicho=nicho, **kw)

    def animar_imagem(self, imagem_path: str, nicho: str = "geral", **kw) -> dict:
        """Delega ao VIDEO ENGINE."""
        ag = self._agentes.get("video")
        if not ag:
            return {"status": "erro", "mensagem": "VIDEO ENGINE indisponível"}
        return ag.imagem_para_video(imagem_path, nicho=nicho, **kw)

    def narrar_texto(self, texto: str, nicho: str = "geral", **kw) -> dict:
        """Delega ao AUDIO MASTER."""
        ag = self._agentes.get("audio")
        if not ag:
            return {"status": "erro", "mensagem": "AUDIO STUDIO indisponível"}
        return ag.narrar(texto, nicho=nicho, **kw)

    def montar_video(self, clips: list, **kw) -> dict:
        """Delega ao CINEMA EDITOR."""
        ag = self._agentes.get("editor")
        if not ag:
            return {"status": "erro", "mensagem": "CINEMA EDITOR indisponível"}
        return ag.montar_video(clips, **kw)

    def criar_thumbnail(self, titulo: str, nicho: str = "geral", **kw) -> dict:
        """Delega ao IMAGE ENGINE para thumbnail."""
        ag = self._agentes.get("image")
        if not ag:
            return {"status": "erro", "mensagem": "IMAGE ENGINE indisponível"}
        return ag.gerar_thumbnail(titulo, nicho=nicho, **kw)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _dividir_cenas(self, roteiro: str) -> list[dict]:
        """Divide roteiro em cenas por parágrafo/marcador."""
        linhas = [l.strip() for l in roteiro.strip().split("\n") if l.strip()]
        cenas = []
        for i, linha in enumerate(linhas):
            if len(linha) > 20:  # ignorar linhas muito curtas
                cenas.append({
                    "numero": i + 1,
                    "texto": linha,
                    "prompt_visual": linha[:100],
                })
        return cenas or [{"numero": 1, "texto": roteiro[:200], "prompt_visual": roteiro[:100]}]


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    print("=== DARK ORCHESTRATOR — Status de Agentes ===")
    orch = DarkOrchestrator()
    st = orch.status_agentes()
    for nome, ag_st in st["agentes"].items():
        status = ag_st.get("status", "?")
        custo = ag_st.get("custo_mensal_brl", "?")
        print(f"  [{status.upper()}] {nome.upper():15s} custo=R${custo}")
    print(f"\nCusto total mensal: R${st['custo_total_mensal_brl']:.2f}")
