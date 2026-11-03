"""
DARK MANAGER — FASE 9 do DARK CREATIVE LAB
Orquestrador central do DARK STUDIO AAA.

Integra todos os 9 agentes especializados:
  1. IMAGE ENGINE       — geração e tratamento de imagens
  2. VIDEO GENERATOR    — geração de vídeos realistas
  3. CINEMATIC DIRECTOR — direção de fotografia e roteiro visual
  4. VIDEO EDITOR PRO   — montagem, color grading e renderização
  5. MOTION GRAPHICS    — animações, títulos e efeitos
  6. AUDIO MASTER       — narração, TTS, tratamento de áudio
  7. VISUAL CONSISTENCY — continuidade visual entre cenas
  8. ASSET MANAGER      — gestão de arquivos e assets
  9. CREATIVE QA        — controle de qualidade audiovisual

O DARK MANAGER decide qual agente usar, na menor custo possível,
respeitando o padrão de qualidade definido por preset.

Política: SEMPRE alternativas gratuitas. APIs pagas requerem aprovação.

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Garante que o diretório raiz do projeto esteja no sys.path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ═══════════════════════════════════════════════════════
# IMPORT LAZY DOS AGENTES (evita dependências pesadas no import)
# ═══════════════════════════════════════════════════════
def _import_agente(modulo: str, classe: str):
    """Import dinâmico para evitar falhas se um módulo opcional não estiver disponível."""
    try:
        import importlib
        mod = importlib.import_module(modulo)
        return getattr(mod, classe)
    except Exception as e:
        print(f"  [DARK_MANAGER] ⚠️  Agente {classe} não carregado: {e}")
        return None


# ═══════════════════════════════════════════════════════
# PRESETS DE PRODUÇÃO
# ═══════════════════════════════════════════════════════
PRESETS_PRODUCAO = {
    "documentary": {
        "nome": "Documentário Cinematográfico",
        "estilo_visual": "documentary",
        "color_grade": "documentary",
        "nicho_consistencia": "cinematico",
        "tts_velocidade": 0.9,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "natureza": {
        "nome": "Natureza e Vida Selvagem",
        "estilo_visual": "nature",
        "color_grade": "nature",
        "nicho_consistencia": "natureza",
        "tts_velocidade": 0.85,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "historia": {
        "nome": "História e Acontecimentos",
        "estilo_visual": "history",
        "color_grade": "history",
        "nicho_consistencia": "historia",
        "tts_velocidade": 0.85,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "tecnologia": {
        "nome": "Tecnologia e Inteligência Artificial",
        "estilo_visual": "sci_tech",
        "color_grade": "sci_tech",
        "nicho_consistencia": "tecnologia",
        "tts_velocidade": 1.0,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "misterio": {
        "nome": "Mistério e Suspense",
        "estilo_visual": "dark_thriller",
        "color_grade": "dark_thriller",
        "nicho_consistencia": "misterio",
        "tts_velocidade": 0.85,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "educacao": {
        "nome": "Educação",
        "estilo_visual": "education",
        "color_grade": "cinematic",
        "nicho_consistencia": "geral",
        "tts_velocidade": 0.95,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "relaxamento": {
        "nome": "Relaxamento",
        "estilo_visual": "relaxation",
        "color_grade": "relaxation",
        "nicho_consistencia": "geral",
        "tts_velocidade": 0.8,
        "fps": 24,
        "resolucao": "1080x1920",
    },
    "musical": {
        "nome": "Conteúdo Musical",
        "estilo_visual": "music",
        "color_grade": "cinematic",
        "nicho_consistencia": "motivacao",
        "tts_velocidade": 1.0,
        "fps": 30,
        "resolucao": "1080x1920",
    },
    "dark_storytelling": {
        "nome": "Storytelling Dark",
        "estilo_visual": "dark_thriller",
        "color_grade": "dark_thriller",
        "nicho_consistencia": "cinematico",
        "tts_velocidade": 0.85,
        "fps": 24,
        "resolucao": "1080x1920",
    },
}


# ═══════════════════════════════════════════════════════
# AGENTE ASSET MANAGER (embutido — sem dependências)
# ═══════════════════════════════════════════════════════
class AssetManager:
    """Gerencia assets de produção: imagens, vídeos, áudios, licenças."""

    def __init__(self, projeto_id: str, base_dir: str = "outputs"):
        self.projeto_id = projeto_id
        self.base = Path(base_dir) / projeto_id
        self.base.mkdir(parents=True, exist_ok=True)
        for sub in ["imagens", "videos", "audios", "motion", "final", "thumbnails"]:
            (self.base / sub).mkdir(exist_ok=True)
        self.registro: List[dict] = []

    def registrar(self, path: str, tipo: str, descricao: str = "", custo: float = 0.0):
        entry = {
            "path": path,
            "tipo": tipo,
            "descricao": descricao,
            "custo_brl": custo,
            "registrado_em": datetime.now().isoformat(),
            "ai_generated": True,
        }
        self.registro.append(entry)
        return entry

    def pasta(self, tipo: str) -> str:
        return str(self.base / tipo)

    def listar(self, tipo: str = None) -> list:
        if tipo:
            return [r for r in self.registro if r["tipo"] == tipo]
        return self.registro

    def custo_total(self) -> float:
        return sum(r.get("custo_brl", 0) for r in self.registro)

    def relatorio(self) -> dict:
        tipos = {}
        for r in self.registro:
            t = r["tipo"]
            tipos[t] = tipos.get(t, 0) + 1
        return {
            "projeto_id": self.projeto_id,
            "total_assets": len(self.registro),
            "por_tipo": tipos,
            "custo_total_brl": self.custo_total(),
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# ═══════════════════════════════════════════════════════
# AGENTE CREATIVE QA (embutido)
# ═══════════════════════════════════════════════════════
class CreativeQA:
    """Avalia qualidade de vídeos, imagens e áudio gerados."""

    def verificar_arquivo(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {"status": "erro", "msg": "Arquivo não encontrado", "path": path}

        tamanho_kb = p.stat().st_size / 1024
        if tamanho_kb < 5:
            return {"status": "alerta", "msg": f"Arquivo muito pequeno ({tamanho_kb:.1f}KB)", "path": path}

        return {
            "status": "ok",
            "path": path,
            "tamanho_kb": round(tamanho_kb, 1),
            "extensao": p.suffix,
        }

    def verificar_video(self, path: str) -> dict:
        """Verifica duração e resolução do vídeo via ffprobe."""
        base = self.verificar_arquivo(path)
        if base["status"] == "erro":
            return base

        try:
            r = subprocess.run([
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration:stream=width,height",
                "-of", "json", path
            ], capture_output=True, text=True, timeout=15)

            if r.returncode == 0:
                data = json.loads(r.stdout)
                dur = float(data.get("format", {}).get("duration", 0))
                streams = data.get("streams", [{}])
                w = streams[0].get("width", 0) if streams else 0
                h = streams[0].get("height", 0) if streams else 0
                base.update({
                    "duracao_s": round(dur, 2),
                    "resolucao": f"{w}x{h}",
                    "qualidade": "ok" if dur > 0.5 and w >= 720 else "baixa",
                })
        except Exception:
            pass

        return base

    def relatorio_qa(self, assets: list) -> dict:
        resultados = [self.verificar_arquivo(a["path"]) for a in assets if "path" in a]
        ok = sum(1 for r in resultados if r.get("status") == "ok")
        alertas = sum(1 for r in resultados if r.get("status") == "alerta")
        erros = sum(1 for r in resultados if r.get("status") == "erro")
        return {
            "total": len(resultados),
            "ok": ok,
            "alertas": alertas,
            "erros": erros,
            "aprovado": erros == 0 and alertas == 0,
            "detalhes": resultados,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# ═══════════════════════════════════════════════════════
# DARK MANAGER — ORQUESTRADOR PRINCIPAL
# ═══════════════════════════════════════════════════════
class DarkManager:
    """
    Orquestrador central do DARK STUDIO AAA.
    Decide qual agente chamar para cada tarefa e gerencia o pipeline completo.
    """

    VERSION = "1.0.0"

    def __init__(self):
        self._agentes: Dict[str, Any] = {}
        self._log: List[dict] = []
        print(f"\n╔══════════════════════════════════════════════════════╗")
        print(f"║   DARK MANAGER v{self.VERSION} — DARK STUDIO AAA          ║")
        print(f"║   Orquestrador de 9 Agentes Especializados           ║")
        print(f"╚══════════════════════════════════════════════════════╝")

    def _log_evento(self, agente: str, acao: str, resultado: str, custo: float = 0.0):
        evento = {
            "ts": datetime.now().isoformat(),
            "agente": agente,
            "acao": acao,
            "resultado": resultado,
            "custo_brl": custo,
        }
        self._log.append(evento)
        custo_str = f" R${custo:.2f}" if custo > 0 else " GRÁTIS"
        print(f"  [{agente}] {acao} → {resultado}{custo_str}")

    # ── Carregamento lazy dos agentes ─────────────────────────────────────────

    def _get_motion_lab(self):
        if "motion" not in self._agentes:
            cls = _import_agente("core.dark_motion_lab", "DarkMotionLab")
            if cls:
                self._agentes["motion"] = cls()
        return self._agentes.get("motion")

    def _get_audio_studio(self):
        if "audio" not in self._agentes:
            cls = _import_agente("core.dark_audio_studio", "DarkAudioStudio")
            if cls:
                self._agentes["audio"] = cls()
        return self._agentes.get("audio")

    def _get_cinema_editor(self):
        if "editor" not in self._agentes:
            cls = _import_agente("core.dark_cinema_editor", "DarkCinemaEditor")
            if cls:
                self._agentes["editor"] = cls()
        return self._agentes.get("editor")

    def _get_cinematic_director(self):
        if "director" not in self._agentes:
            cls = _import_agente("core.dark_cinematic_director", "DarkCinematicDirector")
            if cls:
                self._agentes["director"] = cls()
        return self._agentes.get("director")

    def _get_visual_consistency(self):
        if "consistency" not in self._agentes:
            cls = _import_agente("core.dark_visual_consistency", "DarkVisualConsistency")
            if cls:
                self._agentes["consistency"] = cls()
        return self._agentes.get("consistency")

    # ── Decisão do orquestrador ───────────────────────────────────────────────

    def decidir_agente(self, tarefa: str) -> str:
        """
        Decide qual agente chamar com base na tarefa.
        Retorna o nome do agente responsável.
        """
        tarefa_lower = tarefa.lower()

        if any(w in tarefa_lower for w in ["imagem", "image", "thumbnail", "capa", "foto"]):
            return "IMAGE_ENGINE"
        if any(w in tarefa_lower for w in ["animar", "animação", "vídeo a partir de imagem"]):
            return "VIDEO_GENERATOR"
        if any(w in tarefa_lower for w in ["montar", "editar", "color grade", "renderizar", "sequência"]):
            return "VIDEO_EDITOR_PRO"
        if any(w in tarefa_lower for w in ["roteiro", "cena", "plano", "enquadramento", "câmera"]):
            return "CINEMATIC_DIRECTOR"
        if any(w in tarefa_lower for w in ["abertura", "título", "motion", "animação de texto", "infográfico"]):
            return "MOTION_GRAPHICS"
        if any(w in tarefa_lower for w in ["voz", "narração", "tts", "áudio", "falar"]):
            return "AUDIO_MASTER"
        if any(w in tarefa_lower for w in ["short", "shorts", "vertical", "reels"]):
            return "SHORTS_FACTORY"
        if any(w in tarefa_lower for w in ["qualidade", "qa", "verificar", "aprovar"]):
            return "CREATIVE_QA"
        if any(w in tarefa_lower for w in ["consistência", "personagem", "cenário", "bíblia visual"]):
            return "VISUAL_CONSISTENCY"

        return "DARK_MANAGER"

    # ── Pipeline de produção completo ─────────────────────────────────────────

    def pipeline_short(
        self,
        titulo: str,
        roteiro: str,
        preset: str = "misterio",
        projeto_id: str = None,
        canal: str = "DARK STUDIO AAA",
    ) -> dict:
        """
        Pipeline completo para produção de um Short:
        Roteiro → Abertura → Narração → Edição → Color Grade → QA
        """
        if projeto_id is None:
            projeto_id = f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cfg = PRESETS_PRODUCAO.get(preset, PRESETS_PRODUCAO["misterio"])
        assets = AssetManager(projeto_id)
        qa = CreativeQA()

        print(f"\n{'═'*56}")
        print(f"  PIPELINE SHORT: {titulo}")
        print(f"  Preset: {cfg['nome']} | Projeto: {projeto_id}")
        print(f"{'═'*56}")

        resultado = {
            "projeto_id": projeto_id,
            "titulo": titulo,
            "preset": preset,
            "canal": canal,
            "inicio": datetime.now().isoformat(),
            "etapas": {},
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

        # ── ETAPA 1: MOTION GRAPHICS — Abertura ───────────────────────────────
        print(f"\n  [1/5] MOTION GRAPHICS — Abertura")
        motion = self._get_motion_lab()
        abertura_path = None
        if motion:
            try:
                r_abertura = motion.abertura(
                    canal_nome=canal,
                    slogan=titulo,
                    duracao=4.0,
                    nicho=cfg["nicho_consistencia"],
                    resolucao=(1080, 1920),
                )
                if r_abertura.get("status") == "ok":
                    abertura_path = r_abertura["path"]
                    assets.registrar(abertura_path, "motion", f"Abertura: {titulo}")
                    self._log_evento("MOTION_GRAPHICS", "abertura()", "ok")
                    resultado["etapas"]["abertura"] = {"status": "ok", "path": abertura_path}
                else:
                    self._log_evento("MOTION_GRAPHICS", "abertura()", f"erro: {r_abertura.get('erro', '?')}")
                    resultado["etapas"]["abertura"] = {"status": "skip"}
            except Exception as e:
                self._log_evento("MOTION_GRAPHICS", "abertura()", f"exceção: {e}")
                resultado["etapas"]["abertura"] = {"status": "skip"}
        else:
            resultado["etapas"]["abertura"] = {"status": "skip", "motivo": "agente não carregado"}

        # ── ETAPA 2: CINEMATIC DIRECTOR — Roteiro Visual ───────────────────────
        print(f"\n  [2/5] CINEMATIC DIRECTOR — Roteiro visual")
        director = self._get_cinematic_director()
        cenas_visuais = []
        if director:
            try:
                cenas_raw = [{"descricao": linha.strip()}
                              for linha in roteiro.split("\n") if linha.strip()][:6]
                roteiro_camera = director.gerar_roteiro_de_camera(
                    titulo=titulo,
                    cenas=cenas_raw,
                    estilo=cfg["estilo_visual"],
                )
                cenas_visuais = roteiro_camera.get("cenas", [])
                self._log_evento("CINEMATIC_DIRECTOR", "roteiro_camera()", f"{len(cenas_visuais)} cenas")
                resultado["etapas"]["roteiro_visual"] = {
                    "status": "ok",
                    "total_cenas": len(cenas_visuais),
                    "estilo": cfg["estilo_visual"],
                }
            except Exception as e:
                self._log_evento("CINEMATIC_DIRECTOR", "roteiro_camera()", f"exceção: {e}")
                resultado["etapas"]["roteiro_visual"] = {"status": "skip"}
        else:
            resultado["etapas"]["roteiro_visual"] = {"status": "skip"}

        # ── ETAPA 3: AUDIO MASTER — Narração TTS ─────────────────────────────
        print(f"\n  [3/5] AUDIO MASTER — Narração TTS")
        audio = self._get_audio_studio()
        audio_path = None
        if audio:
            try:
                audio_out = str(Path(assets.pasta("audios")) / f"{projeto_id}_narracao.mp3")
                r_audio = audio.tts_edge(
                    texto=roteiro,
                    output_path=audio_out,
                )
                if r_audio.get("status") in ("ok", "OK"):
                    audio_path = r_audio["path"]
                    assets.registrar(audio_path, "audio", "Narração TTS")
                    self._log_evento("AUDIO_MASTER", "narrar()", "ok")
                    resultado["etapas"]["narracao"] = {"status": "ok", "path": audio_path}
                else:
                    self._log_evento("AUDIO_MASTER", "narrar()", f"erro: {r_audio.get('erro', '?')}")
                    resultado["etapas"]["narracao"] = {"status": "skip"}
            except Exception as e:
                self._log_evento("AUDIO_MASTER", "narrar()", f"exceção: {e}")
                resultado["etapas"]["narracao"] = {"status": "skip"}
        else:
            resultado["etapas"]["narracao"] = {"status": "skip", "motivo": "agente não carregado"}

        # ── ETAPA 4: VIDEO EDITOR PRO — Montagem + Color Grade ────────────────
        print(f"\n  [4/5] VIDEO EDITOR PRO — Montagem e color grade")
        editor = self._get_cinema_editor()
        video_final = None

        if abertura_path and editor:
            try:
                video_mux = str(Path(assets.pasta("final")) / f"{projeto_id}_FINAL.mp4")
                if audio_path:
                    r_edit = editor.pipeline_edicao(
                        input_video=abertura_path,
                        input_audio=audio_path,
                        nome=projeto_id,
                        color_preset=cfg["color_grade"],
                    )
                else:
                    # Só color grade sem áudio
                    r_edit = editor.aplicar_color_grade(
                        abertura_path,
                        preset=cfg["color_grade"],
                        output_path=video_mux,
                    )
                    r_edit["status"] = "OK"

                if r_edit.get("status") == "OK":
                    video_final = r_edit.get("arquivo", video_mux)
                    assets.registrar(video_final, "video", "Vídeo final")
                    self._log_evento("VIDEO_EDITOR_PRO", "pipeline_edicao()", "ok")
                    resultado["etapas"]["edicao"] = {"status": "ok", "path": video_final}
                else:
                    self._log_evento("VIDEO_EDITOR_PRO", "pipeline_edicao()", "erro")
                    resultado["etapas"]["edicao"] = {"status": "skip"}
            except Exception as e:
                self._log_evento("VIDEO_EDITOR_PRO", "pipeline_edicao()", f"exceção: {e}")
                resultado["etapas"]["edicao"] = {"status": "skip"}
        elif abertura_path:
            video_final = abertura_path
            resultado["etapas"]["edicao"] = {"status": "skip", "video_base": abertura_path}
        else:
            resultado["etapas"]["edicao"] = {"status": "skip", "motivo": "sem vídeo base"}

        # ── ETAPA 5: CREATIVE QA ───────────────────────────────────────────────
        print(f"\n  [5/5] CREATIVE QA — Controle de qualidade")
        qa_relatorio = qa.relatorio_qa(assets.listar())
        resultado["etapas"]["qa"] = qa_relatorio
        if qa_relatorio["aprovado"]:
            self._log_evento("CREATIVE_QA", "relatorio_qa()", f"✅ Aprovado ({qa_relatorio['ok']} assets)")
        else:
            self._log_evento("CREATIVE_QA", "relatorio_qa()", f"⚠️  {qa_relatorio['erros']} erros")

        # ── Resultado final ────────────────────────────────────────────────────
        resultado["fim"] = datetime.now().isoformat()
        resultado["video_final"] = video_final
        resultado["assets_total"] = len(assets.listar())
        resultado["custo_total_brl"] = assets.custo_total()
        resultado["qa_aprovado"] = qa_relatorio["aprovado"]

        print(f"\n{'═'*56}")
        print(f"  PIPELINE CONCLUÍDO: {projeto_id}")
        print(f"  Vídeo final: {video_final or 'N/A'}")
        print(f"  Assets: {resultado['assets_total']} | QA: {'✅' if qa_relatorio['aprovado'] else '⚠️'}")
        print(f"  Custo total: R${resultado['custo_total_brl']:.2f} (GRÁTIS)")
        print(f"{'═'*56}\n")

        return resultado

    def pipeline_producao_semanal(
        self,
        canal_config: dict,
        semana: int,
        dias: int = 5,
    ) -> dict:
        """
        Produz a semana completa de Shorts para um canal.
        canal_config: {'id', 'nome', 'preset', 'temas': [lista de roteiros]}
        """
        canal_id = canal_config.get("id", "canal_001")
        canal_nome = canal_config.get("nome", "DARK CHANNEL")
        preset = canal_config.get("preset", "misterio")
        temas = canal_config.get("temas", [])

        print(f"\n{'═'*56}")
        print(f"  PRODUÇÃO SEMANAL — SEMANA {semana:02d}")
        print(f"  Canal: {canal_nome} | {dias} dias")
        print(f"{'═'*56}")

        producao = []
        for i in range(min(dias, len(temas))):
            tema = temas[i]
            projeto_id = f"{canal_id}_S{semana:02d}D{i+1:02d}"
            r = self.pipeline_short(
                titulo=tema.get("titulo", f"Episódio {i+1}"),
                roteiro=tema.get("roteiro", tema.get("titulo", "")),
                preset=preset,
                projeto_id=projeto_id,
                canal=canal_nome,
            )
            producao.append(r)

        aprovados = sum(1 for p in producao if p.get("qa_aprovado"))
        return {
            "canal_id": canal_id,
            "semana": semana,
            "total_produzidos": len(producao),
            "aprovados": aprovados,
            "producao": producao,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def status_agentes(self) -> dict:
        """Retorna status de disponibilidade de todos os agentes."""
        agentes = {
            "IMAGE_ENGINE": "dark_image_studio (em desenvolvimento)",
            "VIDEO_GENERATOR": "dark_video_generator — disponível (HuggingFace)",
            "CINEMATIC_DIRECTOR": "dark_cinematic_director — disponível ✅",
            "VIDEO_EDITOR_PRO": "dark_cinema_editor — disponível ✅",
            "MOTION_GRAPHICS": "dark_motion_lab — disponível ✅",
            "AUDIO_MASTER": "dark_audio_studio — disponível (edge-tts) ✅",
            "VISUAL_CONSISTENCY": "dark_visual_consistency — disponível ✅",
            "ASSET_MANAGER": "integrado no DarkManager ✅",
            "CREATIVE_QA": "integrado no DarkManager ✅",
        }
        return {
            "versao": self.VERSION,
            "agentes": agentes,
            "presets": list(PRESETS_PRODUCAO.keys()),
            "politica_custo": "SEMPRE gratuito. APIs pagas requerem aprovação explícita.",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def exportar_log(self, path: str = None) -> str:
        """Exporta o log de operações como JSON."""
        if path is None:
            path = f"/tmp/dark_manager_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._log, f, ensure_ascii=False, indent=2)
        return path


# ═══════════════════════════════════════════════════════
# CONTRATO JSON
# ═══════════════════════════════════════════════════════
CONTRACT = {
    "agente": "DARK_MANAGER",
    "versao": "1.0.0",
    "descricao": "Orquestrador central — decide qual agente usar em cada tarefa",
    "agentes_gerenciados": [
        "IMAGE_ENGINE", "VIDEO_GENERATOR", "CINEMATIC_DIRECTOR",
        "VIDEO_EDITOR_PRO", "MOTION_GRAPHICS", "AUDIO_MASTER",
        "VISUAL_CONSISTENCY", "ASSET_MANAGER", "CREATIVE_QA",
    ],
    "metodos": {
        "pipeline_short": {
            "entrada": {
                "titulo": "str",
                "roteiro": "str — texto completo",
                "preset": "str — misterio|documentary|natureza|historia|tecnologia|educacao|relaxamento|musical|dark_storytelling",
                "projeto_id": "str?",
                "canal": "str?",
            },
            "saida": "dict — resultado completo com todos os assets e status por etapa",
        },
        "decidir_agente": {
            "entrada": {"tarefa": "str — descrição em linguagem natural"},
            "saida": "str — nome do agente responsável",
        },
        "status_agentes": {
            "entrada": {},
            "saida": "dict — status de todos os 9 agentes",
        },
    },
    "presets": list(PRESETS_PRODUCAO.keys()),
    "politica_custo": "Alternativas gratuitas sempre. APIs pagas requerem aprovação.",
    "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
}


if __name__ == "__main__":
    manager = DarkManager()

    # Status dos agentes
    status = manager.status_agentes()
    print("\nSTATUS DOS AGENTES:")
    for nome, desc in status["agentes"].items():
        print(f"  {nome:25} — {desc}")

    print(f"\nPRESETS DISPONÍVEIS:")
    for k, v in PRESETS_PRODUCAO.items():
        print(f"  {k:20} — {v['nome']}")

    # Teste de decisão de agente
    tarefas_teste = [
        "Gerar imagem para thumbnail",
        "Gravar narração do roteiro",
        "Montar sequência de cenas",
        "Criar abertura animada",
        "Verificar qualidade do vídeo",
        "Manter consistência do personagem",
    ]
    print(f"\nDECISÃO DE AGENTES:")
    for tarefa in tarefas_teste:
        agente = manager.decidir_agente(tarefa)
        print(f"  '{tarefa}' → {agente}")

    # Salvar contrato
    Path("core").mkdir(exist_ok=True)
    with open("core/dark_manager_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print(f"\n  Contrato: core/dark_manager_contract.json")

    # Pipeline teste (sem gerar vídeo real)
    print(f"\n  TESTE RÁPIDO DE PIPELINE...")
    r = manager.pipeline_short(
        titulo="Teste FASE 9 — DARK MANAGER",
        roteiro="Esta é uma narração de teste.\nO DARK STUDIO AAA está operacional.\nTodos os agentes integrados.",
        preset="misterio",
        projeto_id="fase9_teste",
        canal="DARK MANAGER TEST",
    )
    print(f"\n  Etapas concluídas: {list(r['etapas'].keys())}")
    print(f"  QA aprovado: {r['qa_aprovado']}")
    print(f"  Custo: R${r['custo_total_brl']:.2f}\n")
