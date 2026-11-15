"""
DARK TUBE ENGINE — AGENTE VIDEO EDITOR PRO v2.0
Montagem automática, color grading, transições, silence removal e renderização
Clone funcional: DaVinci Resolve + vidiq_compose + vidiq_generate_video
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Fase 5 — DARK CINEMA EDITOR integrado
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_composer import pipeline_compose_short, verificar_ffmpeg, gerar_srt_do_script
from core.script_engine import criar_job_script
from core.cinema_editor import (
    pipeline_cinema_editor,
    renderizar_em_lote,
    aplicar_color_grade,
    adicionar_transicao,
    remover_silencio,
    listar_presets,
    COLOR_GRADE_FILTERS,
    TRANSITION_TYPES,
)


class VideoEditorProAgent:
    """
    AGENTE VIDEO EDITOR PRO v2.0 — Montagem, color grading e renderização
    Stack: FFmpeg (gratuito, local, profissional)
    Integra: DARK CINEMA EDITOR (Fase 5)
    Clone: vidiq_compose + DaVinci Resolve + Premiere Pro sem custo
    """

    AGENT_ID = "video_editor_pro"
    VERSION = "2.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        # ── Listar presets (ANTES de color_grade — evita substring collision) ─
        if "listar" in tarefa or "templates" in tarefa or tarefa == "presets":
            return self.listar_presets_disponiveis(payload)

        # ── Color grading ─────────────────────────────────────────────────
        if "color_grade" in tarefa or "color grade" in tarefa or "grading" in tarefa:
            return self.aplicar_color_grade(payload)

        # ── Pipeline cinema completo ──────────────────────────────────────
        if "pipeline_cinema" in tarefa or "cinema_editor" in tarefa:
            return self.pipeline_cinema(payload)

        # ── Renderização em lote (ANTES de renderizar solo) ───────────────
        if "lote" in tarefa or "batch" in tarefa or "renderizar_lote" in tarefa:
            return self.renderizar_lote(payload)

        # ── Transição ─────────────────────────────────────────────────────
        if "xfade" in tarefa or "adicionar_transicao" in tarefa:
            return self.adicionar_transicao(payload)

        # ── Remover silêncio ──────────────────────────────────────────────
        if "silencio" in tarefa or "silence" in tarefa or "remover_silencio" in tarefa:
            return self.remover_silencio(payload)

        # ── Compose/Montar/Renderizar (v1 — mantido para compatibilidade) ─
        if "compose" in tarefa or "montar" in tarefa or "renderizar" in tarefa:
            return self.compor_video(payload)

        # ── Script/Roteiro ────────────────────────────────────────────────
        if "script" in tarefa or "roteiro" in tarefa:
            return self.criar_script(payload)

        # ── SRT/Legenda ───────────────────────────────────────────────────
        if "srt" in tarefa or "legenda" in tarefa:
            return self.gerar_srt(payload)

        return {"status": "erro", "mensagem": f"Tarefa não reconhecida: {tarefa}"}

    # ── Métodos v2.0 — DARK CINEMA EDITOR ─────────────────────────────────

    def aplicar_color_grade(self, payload: dict) -> dict:
        """Aplica color grading a um vídeo com preset cinematográfico."""
        video_path = payload.get("video_path", "")
        if not video_path or not os.path.exists(video_path):
            return {"status": "erro", "mensagem": f"Vídeo não encontrado: {video_path}"}

        preset = payload.get("preset_nome", payload.get("preset", "storytelling_dark"))
        output_path = payload.get("output_path") or video_path.replace(".mp4", f"_graded_{preset}.mp4")

        resultado = aplicar_color_grade(video_path, preset, output_path, crf=payload.get("crf"))
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def pipeline_cinema(self, payload: dict) -> dict:
        """
        Pipeline cinema completo: color grade + transições + áudio.
        Payload: {clips, preset_nome, audio_path, titulo, tipo_transicao,
                  output_dir, remover_silencio_audio}
        """
        clips = payload.get("clips", [])
        if not clips:
            return {"status": "erro", "mensagem": "Lista de clipes não fornecida"}

        resultado = pipeline_cinema_editor(
            clips=clips,
            preset_nome=payload.get("preset_nome", "storytelling_dark"),
            audio_path=payload.get("audio_path"),
            output_dir=payload.get("output_dir", "outputs/video"),
            tipo_transicao=payload.get("tipo_transicao"),
            resolucao=payload.get("resolucao", "1920x1080"),
            remover_silencio_audio=payload.get("remover_silencio_audio", False),
            titulo=payload.get("titulo", ""),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def renderizar_lote(self, payload: dict) -> dict:
        """
        Renderiza múltiplos projetos em lote.
        Payload: {projetos: [{clips, preset_nome, audio_path, titulo}, ...], output_dir}
        """
        projetos = payload.get("projetos", [])
        if not projetos:
            return {"status": "erro", "mensagem": "Lista de projetos não fornecida"}

        resultado = renderizar_em_lote(
            projetos=projetos,
            output_dir=payload.get("output_dir", "outputs/video/batch"),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def adicionar_transicao(self, payload: dict) -> dict:
        """
        Adiciona transição entre dois clipes.
        Payload: {clip1_path, clip2_path, output_path, tipo, duracao}
        """
        clip1 = payload.get("clip1_path", "")
        clip2 = payload.get("clip2_path", "")
        output = payload.get("output_path", "outputs/video/trans_out.mp4")

        if not clip1 or not clip2:
            return {"status": "erro", "mensagem": "clip1_path e clip2_path são obrigatórios"}

        resultado = adicionar_transicao(
            clip1_path=clip1,
            clip2_path=clip2,
            output_path=output,
            tipo=payload.get("tipo", "dissolve"),
            duracao=payload.get("duracao"),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def remover_silencio(self, payload: dict) -> dict:
        """
        Remove silêncios do áudio.
        Payload: {audio_path, output_path, threshold_db, min_silence_duration, padding_ms}
        """
        audio_path = payload.get("audio_path", "")
        if not audio_path or not os.path.exists(audio_path):
            return {"status": "erro", "mensagem": f"Áudio não encontrado: {audio_path}"}

        output_path = payload.get("output_path") or audio_path.replace(".wav", "_clean.wav").replace(".mp3", "_clean.mp3")

        resultado = remover_silencio(
            audio_path=audio_path,
            output_path=output_path,
            threshold_db=payload.get("threshold_db", -35.0),
            min_silence_duration=payload.get("min_silence_duration", 0.5),
            padding_ms=payload.get("padding_ms", 200),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def listar_presets_disponiveis(self, payload: dict) -> dict:
        """Lista todos os presets de color grade e transições."""
        resultado = listar_presets()
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ── Métodos v1.0 — mantidos para compatibilidade ───────────────────────

    def compor_video(self, payload: dict) -> dict:
        """Composição de Short vertical com áudio e legenda (v1 — compat)."""
        import os
        audio_path = payload.get("audio_path", "")
        if not audio_path or not os.path.exists(audio_path):
            return {"status": "erro", "mensagem": f"Áudio não encontrado: {audio_path}"}

        resultado = pipeline_compose_short(
            titulo=payload.get("titulo", "Sem título"),
            canal=payload.get("canal", ""),
            script=payload.get("script", ""),
            audio_path=audio_path,
            resolucao=payload.get("resolucao", "1080x1920"),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["custo"] = "GRATUITO — FFmpeg local"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def criar_script(self, payload: dict) -> dict:
        """Cria job de script para vídeo."""
        job = criar_job_script(
            titulo=payload.get("titulo", ""),
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            duracao_alvo=payload.get("duracao_alvo", 60),
            palavras_chave=payload.get("palavras_chave", []),
        )
        job["agente"] = self.AGENT_ID
        return job

    def gerar_srt(self, payload: dict) -> dict:
        """Gera arquivo SRT de legenda a partir do script."""
        script = payload.get("script", "")
        duracao_total = payload.get("duracao_total", payload.get("duracao_total_s", 60.0))
        output_path = payload.get("output_path", "outputs/video/legenda.srt")

        Path(os.path.dirname(output_path) or ".").mkdir(parents=True, exist_ok=True)
        srt_path = gerar_srt_do_script(
            script=script,
            duracao_total_s=duracao_total,
            output_path=output_path,
        )
        return {
            "agente": self.AGENT_ID,
            "srt_path": srt_path,
            "status": "completed",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    def status(self) -> dict:
        ffmpeg = verificar_ffmpeg()
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "ffmpeg": ffmpeg,
            "capacidades": [
                "color_grade_8_presets",
                "transicoes_xfade",
                "silence_removal",
                "pipeline_cinema_completo",
                "renderizacao_lote",
                "compose_short",
                "compose_horizontal",
                "srt_legendas",
                "h264_aac",
            ],
            "presets_color_grade": list(COLOR_GRADE_FILTERS.keys()),
            "tipos_transicao": list(TRANSITION_TYPES.keys()),
            "resolucoes": ["1080x1920 (Shorts)", "1920x1080 (Horizontal)", "1080x1080 (Square)"],
            "custo": "GRATUITO — FFmpeg local (DaVinci Resolve clone)",
            "clone_de": "DaVinci Resolve + Adobe Premiere Pro + Descript",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }
