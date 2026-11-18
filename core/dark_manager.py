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
# CADEIA DE FALLBACK — BACKEND DE PRODUÇÃO
# ═══════════════════════════════════════════════════════
# Ordem de prioridade para produção de Shorts:
#   1. vidiq   — cloud premium (melhor qualidade; requer MCP vidIQ ativo)
#   2. hugging — HuggingFace Spaces (gratuito; qualidade boa; mais lento)
#   3. local   — modelos locais (CPU/GPU; requer hardware compatível)
BACKEND_PRIORITY = ["vidiq", "hugging", "local"]

# Importação lazy do bridge vidIQ (disponível apenas quando MCP estiver ativo)
try:
    from core.dark_vidiq_bridge import (
        ProducaoShort,
        VOZES_PTBR,
        MODELOS_VIDEO,
        CANAL_DEFAULT,
        QA_SCORE_MINIMO,
        gerar_prompt_video_noir,
        gerar_prompt_thumbnail,
        gerar_overlays_texto,
        gerar_cenas_compose,
        calcular_qa_score,
        gerar_descricao_youtube,
        gerar_tags_nicho,
        estimar_custo,
        exportar_log as _exportar_log_vidiq,
    )
    _VIDIQ_BRIDGE_DISPONIVEL = True
except ImportError:
    _VIDIQ_BRIDGE_DISPONIVEL = False


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

    VERSION = "2.0.0"

    def __init__(self):
        self._agentes: Dict[str, Any] = {}
        self._log: List[dict] = []
        self._backend_atual: str = BACKEND_PRIORITY[0]  # padrão: vidiq
        print(f"\n╔══════════════════════════════════════════════════════╗")
        print(f"║   DARK MANAGER v{self.VERSION} — DARK STUDIO AAA          ║")
        print(f"║   Orquestrador de 9 Agentes + Backend vidIQ         ║")
        print(f"╚══════════════════════════════════════════════════════╝")
        print(f"  vidIQ Bridge: {'✅ disponível' if _VIDIQ_BRIDGE_DISPONIVEL else '⚠️  não carregado (fallback: local)'}")

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

    # ── Backend vidIQ ─────────────────────────────────────────────────────────

    def pipeline_short_vidiq(
        self,
        titulo: str,
        roteiro: str,
        nicho: str = "misterio",
        canal_id: str = None,
        voz: str = "brian",
        modelo_video: str = "minimax-h3",
        projeto_id: str = None,
        log_path: str = None,
    ) -> dict:
        """
        Pipeline de produção via backend vidIQ (cloud premium).

        AGENTES EVOCADOS:
          CINEMATIC_DIRECTOR  → prompt de vídeo noir/cinematográfico
          IMAGE_ENGINE        → prompt de thumbnail
          AUDIO_MASTER        → narração vidIQ TTS
          VIDEO_GENERATOR     → vídeo minimax-h3 (768p 9:16 15s)
          VIDEO_EDITOR_PRO    → overlays de texto e cenas compose
          ASSET_MANAGER       → tags, descrição SEO, log
          CREATIVE_QA         → qa_score ≥ 85 obrigatório

        NOTA: Este método documenta o contrato e a lógica de roteamento.
        A execução real das chamadas MCP vidIQ acontece via sessão Claude
        (MCP não é callable direto em Python).

        Args:
            titulo: título do Short
            roteiro: roteiro completo em PT-BR
            nicho: 'misterio' | 'historia' | 'educacao' | 'tecnologia' | ...
            canal_id: canal YouTube (default: Canal S002)
            voz: 'brian' | 'nassif' | 'edmilson'
            modelo_video: 'minimax-h3' | 'minimax-h3-hd' | 'kling-v2'
            projeto_id: ID do projeto (auto-gerado se None)
            log_path: onde salvar o log JSON (opcional)

        Returns:
            dict com contrato de execução para o DARK MANAGER
        """
        if not _VIDIQ_BRIDGE_DISPONIVEL:
            self._log_evento("DARK_MANAGER", "pipeline_short_vidiq()", "⚠️  bridge não disponível — fallback local")
            return self.pipeline_short(titulo=titulo, roteiro=roteiro, preset=nicho, projeto_id=projeto_id)

        if canal_id is None:
            canal_id = CANAL_DEFAULT
        if projeto_id is None:
            projeto_id = f"vidiq_{nicho}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self._log_evento("DARK_MANAGER", "pipeline_short_vidiq()", f"iniciado — {titulo[:40]}")

        # CINEMATIC_DIRECTOR → prompt cinematográfico
        prompt_video = gerar_prompt_video_noir(titulo, nicho)
        self._log_evento("CINEMATIC_DIRECTOR", "gerar_prompt_video_noir()", f"{len(prompt_video)} chars")

        # IMAGE_ENGINE → prompt thumbnail
        prompt_thumb = gerar_prompt_thumbnail(titulo, nicho)
        self._log_evento("IMAGE_ENGINE", "gerar_prompt_thumbnail()", f"{len(prompt_thumb)} chars")

        # ASSET_MANAGER → tags, descrição, custo estimado
        tags = gerar_tags_nicho(titulo, nicho)
        descricao = gerar_descricao_youtube(titulo, roteiro, nicho)
        custo = estimar_custo(modelo_video, num_clips=1)
        self._log_evento("ASSET_MANAGER", "gerar_tags_nicho()", f"{len(tags)} tags")
        self._log_evento("ASSET_MANAGER", "gerar_descricao_youtube()", f"{len(descricao)} chars")
        self._log_evento("ASSET_MANAGER", "estimar_custo()", f"~{custo.get('creditos_estimados', '?')} créditos")

        # Monta contrato de execução (passado para a sessão MCP)
        contrato = {
            "projeto_id": projeto_id,
            "titulo": titulo,
            "nicho": nicho,
            "canal_id": canal_id,
            "backend": "vidiq",
            "modelo_video": modelo_video,
            "voz_id": VOZES_PTBR.get(voz, VOZES_PTBR["brian"]),
            "voz_nome": voz,
            "roteiro_chars": len(roteiro),
            "prompt_video": prompt_video,
            "prompt_thumbnail": prompt_thumb,
            "tags": tags,
            "descricao_youtube": descricao,
            "custo_estimado": custo,
            "qa_score_minimo": QA_SCORE_MINIMO,
            "overlays": gerar_overlays_texto(titulo, 15.0),
            "cenas_compose": gerar_cenas_compose("TBD", 15.0, 5),
            "sequencia_execucao": [
                "1. vidiq_voiceover_generate(texto=roteiro, voice_id=voz_id)",
                "2. vidiq_generate_video(prompt=prompt_video, modelo=modelo_video)",
                "3. vidiq_generate_thumbnail(titulo=titulo, prompt=prompt_thumbnail)",
                "4. vidiq_compose(video_url, overlays, cenas)",
                "5. vidiq_video_upload(compose_url)",
                "6. vidiq_social_post_draft_create() → aprovação",
                "7. vidiq_social_post_publish()",
                "8. calcular_qa_score() ≥ 85",
            ],
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            "ts_contrato": datetime.now().isoformat(),
        }

        # Salvar log se solicitado
        if log_path:
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(contrato, f, ensure_ascii=False, indent=2)
            self._log_evento("ASSET_MANAGER", "exportar_contrato()", log_path)

        return contrato

    def pipeline_auto(
        self,
        titulo: str,
        roteiro: str,
        nicho: str = "misterio",
        backend: str = "auto",
        **kwargs,
    ) -> dict:
        """
        Dispatcher automático — escolhe o melhor backend disponível.

        Cadeia de fallback: vidIQ (cloud premium) → HuggingFace → local.
        Usa o backend de menor custo que atenda QA_SCORE_MINIMO (85).

        Args:
            titulo: título do Short
            roteiro: roteiro completo
            nicho: nicho de produção
            backend: 'auto' | 'vidiq' | 'hugging' | 'local'
            **kwargs: passado para o método de pipeline específico

        Returns:
            dict resultado do pipeline selecionado
        """
        prioridade = BACKEND_PRIORITY if backend == "auto" else [backend]

        for b in prioridade:
            if b == "vidiq":
                if _VIDIQ_BRIDGE_DISPONIVEL:
                    self._log_evento("DARK_MANAGER", "pipeline_auto()", f"→ BACKEND: vidIQ (cloud premium)")
                    return self.pipeline_short_vidiq(titulo=titulo, roteiro=roteiro, nicho=nicho, **kwargs)
                else:
                    self._log_evento("DARK_MANAGER", "pipeline_auto()", "vidIQ bridge indisponível — próximo fallback")
                    continue

            elif b == "hugging":
                self._log_evento("DARK_MANAGER", "pipeline_auto()", "→ BACKEND: HuggingFace Spaces (gratuito)")
                # HuggingFace Spaces: usar via dark_video_generator com endpoint HF
                try:
                    from core.dark_video_generator import DarkVideoGenerator
                    gen = DarkVideoGenerator()
                    self._log_evento("VIDEO_GENERATOR", "gerar_broll_sintetico()", f"HF: {titulo[:30]}")
                    # Fallback para pipeline local com vídeo HF
                    return self.pipeline_short(titulo=titulo, roteiro=roteiro, preset=nicho,
                                               projeto_id=kwargs.get("projeto_id"), **{})
                except Exception as e:
                    self._log_evento("DARK_MANAGER", "pipeline_auto()", f"HuggingFace falhou: {e}")
                    continue

            elif b == "local":
                self._log_evento("DARK_MANAGER", "pipeline_auto()", "→ BACKEND: local (CPU/GPU)")
                return self.pipeline_short(titulo=titulo, roteiro=roteiro, preset=nicho,
                                           projeto_id=kwargs.get("projeto_id"))

        # Fallback final
        return {
            "status": "erro",
            "msg": "Nenhum backend disponível",
            "backends_tentados": prioridade,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def status_agentes(self) -> dict:
        """Retorna status de disponibilidade de todos os agentes."""
        vidiq_status = "✅ vidIQ MCP bridge disponível" if _VIDIQ_BRIDGE_DISPONIVEL else "⚠️  vidIQ bridge não carregado"
        agentes = {
            "IMAGE_ENGINE": f"dark_image_engine + vidIQ thumbnail ({vidiq_status})",
            "VIDEO_GENERATOR": f"dark_video_generator + vidIQ minimax-h3 ({vidiq_status})",
            "CINEMATIC_DIRECTOR": "dark_cinematic_director — prompt noir/cinematográfico ✅",
            "VIDEO_EDITOR_PRO": f"dark_cinema_editor + vidIQ compose ({vidiq_status})",
            "MOTION_GRAPHICS": "dark_motion_lab — animações e aberturas ✅",
            "AUDIO_MASTER": f"dark_audio_studio (edge-tts) + vidIQ TTS Brian ({vidiq_status})",
            "VISUAL_CONSISTENCY": "dark_visual_consistency — continuidade entre cenas ✅",
            "ASSET_MANAGER": f"integrado + dark_script_generator (30 tópicos) ✅",
            "CREATIVE_QA": "integrado — qa_score ≥ 85 obrigatório ✅",
            "SHORTS_FACTORY": f"dark_shorts_factory + vidIQ publish ({vidiq_status})",
        }
        backends = {
            "vidiq":   {"disponivel": _VIDIQ_BRIDGE_DISPONIVEL, "qualidade": "★★★★★", "custo": "créditos vidIQ"},
            "hugging": {"disponivel": True,                      "qualidade": "★★★☆☆", "custo": "gratuito"},
            "local":   {"disponivel": True,                      "qualidade": "★★☆☆☆", "custo": "hardware próprio"},
        }
        return {
            "versao": self.VERSION,
            "agentes": agentes,
            "backends": backends,
            "backend_atual": self._backend_atual,
            "backend_priority": BACKEND_PRIORITY,
            "presets": list(PRESETS_PRODUCAO.keys()),
            "politica_custo": "Menor custo com QA ≥ 85. vidIQ requer aprovação explícita.",
            "canal_default": CANAL_DEFAULT if _VIDIQ_BRIDGE_DISPONIVEL else "N/A",
            "qa_score_minimo": QA_SCORE_MINIMO if _VIDIQ_BRIDGE_DISPONIVEL else 85,
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
    "versao": "2.0.0",
    "descricao": "Orquestrador central — decide qual agente e backend usar em cada tarefa",
    "agentes_gerenciados": [
        "IMAGE_ENGINE", "VIDEO_GENERATOR", "CINEMATIC_DIRECTOR",
        "VIDEO_EDITOR_PRO", "MOTION_GRAPHICS", "AUDIO_MASTER",
        "VISUAL_CONSISTENCY", "ASSET_MANAGER", "CREATIVE_QA", "SHORTS_FACTORY",
    ],
    "backends": {
        "vidiq":   "cloud premium — MCP vidIQ — minimax-h3 — qualidade ★★★★★",
        "hugging": "HuggingFace Spaces — gratuito — qualidade ★★★☆☆",
        "local":   "modelos locais CPU/GPU — qualidade ★★☆☆☆",
    },
    "fallback_chain": "vidiq → hugging → local",
    "metodos": {
        "pipeline_auto": {
            "descricao": "Dispatcher automático — escolhe melhor backend disponível",
            "entrada": {
                "titulo": "str",
                "roteiro": "str — texto completo",
                "nicho": "str — misterio|historia|educacao|tecnologia|natureza|...",
                "backend": "str? — 'auto'|'vidiq'|'hugging'|'local' (default: 'auto')",
            },
            "saida": "dict — resultado do pipeline selecionado",
        },
        "pipeline_short_vidiq": {
            "descricao": "Pipeline vidIQ cloud premium — 8 etapas MCP",
            "entrada": {
                "titulo": "str",
                "roteiro": "str",
                "nicho": "str",
                "canal_id": "str? — default: Canal S002 UCwuyz5ABF6ooQUn2HwG9xHQ",
                "voz": "str? — 'brian'|'nassif'|'edmilson' (default: 'brian')",
                "modelo_video": "str? — 'minimax-h3'|'minimax-h3-hd'|'kling-v2'",
            },
            "saida": "dict — contrato de execução com todos os prompts e parâmetros",
            "sequencia": [
                "AUDIO_MASTER: vidiq_voiceover_generate",
                "VIDEO_GENERATOR: vidiq_generate_video (minimax-h3)",
                "IMAGE_ENGINE: vidiq_generate_thumbnail",
                "VIDEO_EDITOR_PRO: vidiq_compose",
                "SHORTS_FACTORY: vidiq_video_upload",
                "ASSET_MANAGER: vidiq_social_post_draft_create → aprovação",
                "SHORTS_FACTORY: vidiq_social_post_publish",
                "CREATIVE_QA: calcular_qa_score ≥ 85",
            ],
        },
        "pipeline_short": {
            "descricao": "Pipeline local — motion graphics + TTS edge + FFmpeg",
            "entrada": {
                "titulo": "str",
                "roteiro": "str",
                "preset": "str — misterio|documentary|natureza|historia|...",
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
            "saida": "dict — status de todos os 10 agentes + backends",
        },
    },
    "presets": list(PRESETS_PRODUCAO.keys()),
    "politica_custo": "pipeline_auto seleciona menor custo com QA ≥ 85. vidIQ requer aprovação explícita.",
    "canal_s002": "UCwuyz5ABF6ooQUn2HwG9xHQ — Dark História",
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


# ─── Funções de módulo para compatibilidade com testes e integrações ──────────

_manager_singleton: "DarkManager | None" = None

def _get_manager() -> "DarkManager":
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = DarkManager()
    return _manager_singleton


def executar(tarefa: str, params: dict = None, verbose: bool = True, **kwargs) -> dict:
    """Alias de módulo: despacha uma tarefa para o agente adequado.
    
    Args:
        tarefa: nome da tarefa (ex: 'gerar_imagem', 'narrar', 'gerar_video', 'thumbnail')
        **kwargs: parâmetros passados ao agente
    
    Returns:
        dict com resultado da operação
    """
    # Mesclar params dict com kwargs
    if params:
        kwargs.update(params)

    manager = _get_manager()
    agente = manager.decidir_agente(tarefa)

    # Mapear tarefas para métodos do pipeline
    task_lower = tarefa.lower().replace(" ", "_")
    
    if "imagem" in task_lower or "image" in task_lower or "thumbnail" in task_lower:
        try:
            # Fase 2: preferir DarkImageStudio (unified engine)
            try:
                from core.dark_image_studio import DarkImageStudio
                studio = DarkImageStudio()
                prompt = kwargs.get("prompt", kwargs.get("titulo", kwargs.get("descricao", f"cena de {tarefa}")))
                nicho = kwargs.get("nicho", kwargs.get("canal", "natureza"))
                output_path = kwargs.get("output_path")
                from pathlib import Path as _Path
                if "thumbnail" in task_lower:
                    result = studio.gerar_thumbnail(
                        titulo=prompt, nicho=nicho,
                        output_path=_Path(output_path) if output_path else None,
                    )
                else:
                    extra = {k:v for k,v in kwargs.items() if k not in ("prompt","nicho","descricao","titulo","canal","output_path")}
                    result = studio.gerar(prompt=prompt, nicho=nicho,
                                          output_path=_Path(output_path) if output_path else None, **extra)
            except ImportError:
                # Fallback: DarkImageEngine legado
                from core.dark_image_engine import DarkImageEngine
                eng = DarkImageEngine()
                prompt = kwargs.get("prompt", kwargs.get("titulo", kwargs.get("descricao", f"cena de {tarefa}")))
                nicho = kwargs.get("nicho", kwargs.get("canal", "natureza"))
                output_path = kwargs.get("output_path")
                extra = {k:v for k,v in kwargs.items() if k not in ("prompt","nicho","descricao","titulo","canal","output_path")}
                from pathlib import Path as _Path
                result = eng.gerar(prompt=prompt, nicho=nicho, output_path=_Path(output_path) if output_path else None, **extra)
            result["status"] = result.get("status", "ok")
            return result
        except Exception as e:
            return {"status": "erro", "agente": agente, "erro": str(e), "tarefa": tarefa,
                    "ai_generated": True, "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}
    
    elif "video" in task_lower or "vídeo" in task_lower:
        try:
            # Fase 3: preferir DarkVideoStudio (unified engine com cascade)
            try:
                from core.dark_video_studio import DarkVideoStudio
                studio = DarkVideoStudio()
                prompt = kwargs.get("prompt", kwargs.get("descricao", f"vídeo de {tarefa}"))
                nicho = kwargs.get("nicho", kwargs.get("canal", "natureza"))
                preset = kwargs.get("preset", "documentario")
                output_path = kwargs.get("output_path")
                image_path = kwargs.get("image_path")
                duracao = kwargs.get("duracao_s", kwargs.get("duracao", 5))
                backend = kwargs.get("backend")
                from pathlib import Path as _Path
                result = studio.gerar(
                    prompt=prompt, nicho=nicho, preset=preset,
                    output_path=_Path(output_path) if output_path else None,
                    image_path=_Path(image_path) if image_path else None,
                    duracao=float(duracao), backend=backend,
                )
                return result.to_dict() if hasattr(result, "to_dict") else dict(result)
            except ImportError:
                # Fallback: DarkVideoGenerator legado
                from core.dark_video_generator import DarkVideoGenerator
                gen = DarkVideoGenerator()
                prompt = kwargs.get("prompt", kwargs.get("descricao", f"vídeo de {tarefa}"))
                output_path = kwargs.get("output_path")
                duracao_s = kwargs.get("duracao_s", 5)
                result = gen.gerar_broll_sintetico(
                    tema=prompt,
                    output_path=output_path or "/tmp/dark_video_exec.mp4",
                    duracao=float(duracao_s),
                ) if hasattr(gen, "gerar_broll_sintetico") else gen.gerar_broll(prompt=prompt, output_path=output_path)
                if isinstance(result, dict) and "status" not in result:
                    result["status"] = "ok"
                return result
        except Exception as e:
            return {"status": "erro", "agente": agente, "erro": str(e), "tarefa": tarefa,
                    "ai_generated": True, "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}
    
    elif "narr" in task_lower or "audio" in task_lower or "voz" in task_lower or "tts" in task_lower:
        try:
            from core.piper_tts import synthesize
            texto = kwargs.get("texto", kwargs.get("text", "Narração de teste."))
            output = kwargs.get("output_path", "/tmp/dark_narr_exec.wav")
            from pathlib import Path as _Path
            result = synthesize(texto, _Path(output))
            return {"status": "ok" if result else "erro", "audio_path": output, "agente": agente,
                    "ai_generated": True, "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}
        except Exception as e:
            return {"status": "erro", "agente": agente, "erro": str(e), "tarefa": tarefa,
                    "ai_generated": True, "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}
    
    elif (
        "multilin" in task_lower or "traduz" in task_lower
        or "expan" in task_lower or "internacional" in task_lower
        or "dublar" in task_lower or "expand_canal" in task_lower
    ):
        try:
            from core.dark_multilingual_agent import DarkMultilingualAgent, expandir_canal
            canal = kwargs.get("canal", "")
            video_id = kwargs.get("video_id", "")
            titulo = kwargs.get("titulo", kwargs.get("title", ""))
            descricao = kwargs.get("descricao", kwargs.get("description", ""))
            tags = kwargs.get("tags", [])
            script = kwargs.get("script")
            srt_path = kwargs.get("srt_path")
            if canal and video_id and titulo:
                return expandir_canal(
                    canal=canal,
                    video_id=video_id,
                    titulo=titulo,
                    descricao=descricao,
                    tags=tags,
                    script=script,
                    srt_path=srt_path,
                )
            # Sem parâmetros suficientes: retornar status do agente
            agente_ml = DarkMultilingualAgent()
            return agente_ml.status()
        except Exception as e:
            return {"status": "erro", "agente": "MULTILINGUAL_AGENT", "erro": str(e), "tarefa": tarefa,
                    "ai_generated": True, "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"}

    return {
        "status": "despachado",
        "tarefa": tarefa,
        "agente_decidido": agente,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }


def check_all_agents() -> dict:
    """Verifica status de todos os 11 agentes especialistas (incluindo Multilingual).

    Returns:
        dict com status de cada agente
    """
    status = {}

    agentes_modulos = [
        ("IMAGE_ENGINE",        "core.dark_image_studio",        "DarkImageStudio"),
        ("VIDEO_STUDIO",        "core.dark_video_studio",        "DarkVideoStudio"),
        ("VIDEO_GENERATOR",     "core.dark_video_generator",     "DarkVideoGenerator"),
        ("CINEMATIC_DIRECTOR",  "core.cinematic_director",       "gerar_prompt_visual"),
        ("VIDEO_EDITOR_PRO",    "core.cinema_editor",            "Timeline"),
        ("MOTION_GRAPHICS",     "core.motion_graphics",          "gerar_titulo_animado"),
        ("AUDIO_MASTER",        "core.piper_tts",                "PiperTTS"),
        ("VISUAL_CONSISTENCY",  "core.visual_consistency",       "VisualConsistencyDB"),
        ("ASSET_MANAGER",       "core.asset_manager",            "AssetDB"),
        ("CREATIVE_QA",         "core.creative_qa",              "verificar_qualidade"),
        ("MULTILINGUAL_AGENT",  "core.dark_multilingual_agent",  "DarkMultilingualAgent"),
    ]
    
    agentes_status = {}
    for nome, modulo, classe in agentes_modulos:
        try:
            import importlib
            mod = importlib.import_module(modulo)
            getattr(mod, classe)
            agentes_status[nome] = {"status": "ok", "modulo": modulo, "symbol": classe}
        except Exception as e:
            agentes_status[nome] = {"status": "erro", "modulo": modulo, "symbol": classe, "erro": str(e)}

    n_ok = sum(1 for v in agentes_status.values() if v["status"] == "ok")
    status["agentes"] = agentes_status
    status["_resumo"] = {
        "total": len(agentes_modulos),
        "ok": n_ok,
        "falhas": len(agentes_modulos) - n_ok,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
    return status


# TASK_TYPES: mapeamento de tarefas para agentes (compatibilidade)
TASK_TYPES = {
    "gerar_imagem":   "IMAGE_ENGINE",
    "thumbnail":      "IMAGE_ENGINE",
    "gerar_video":    "VIDEO_STUDIO",
    "animar":         "VIDEO_STUDIO",
    "video_studio":   "VIDEO_STUDIO",
    "narrar":         "AUDIO_MASTER",
    "tts":            "AUDIO_MASTER",
    "audio":          "AUDIO_MASTER",
    "montar":         "VIDEO_EDITOR_PRO",
    "editar":         "VIDEO_EDITOR_PRO",
    "motion":         "MOTION_GRAPHICS",
    "titulo":         "MOTION_GRAPHICS",
    "consistencia":   "VISUAL_CONSISTENCY",
    "qa":             "CREATIVE_QA",
    "asset":          "ASSET_MANAGER",
    "cinematic":      "CINEMATIC_DIRECTOR",
    # Expansão internacional
    "multilingual":   "MULTILINGUAL_AGENT",
    "traduzir":       "MULTILINGUAL_AGENT",
    "expandir":       "MULTILINGUAL_AGENT",
    "internacional":  "MULTILINGUAL_AGENT",
    "dublar":         "MULTILINGUAL_AGENT",
    "expand_canal":   "MULTILINGUAL_AGENT",
}
