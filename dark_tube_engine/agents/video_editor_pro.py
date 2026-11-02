"""
DARK TUBE ENGINE — AGENTE VIDEO EDITOR PRO
Montagem automática, linha do tempo, transições e renderização
Clone funcional: vidiq_compose + vidiq_generate_video
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_composer import pipeline_compose_short, verificar_ffmpeg, gerar_srt_do_script
from core.script_engine import criar_job_script, salvar_script


class VideoEditorProAgent:
    """
    AGENTE VIDEO EDITOR PRO — Montagem e renderização
    Stack: FFmpeg (gratuito, local, profissional)
    Clone: vidiq_compose sem custo de créditos
    """

    AGENT_ID = "video_editor_pro"
    VERSION = "1.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "compose" in tarefa or "montar" in tarefa or "renderizar" in tarefa:
            return self.compor_video(payload)
        elif "script" in tarefa or "roteiro" in tarefa:
            return self.criar_script(payload)
        elif "srt" in tarefa or "legenda" in tarefa:
            return self.gerar_srt(payload)
        else:
            return {"status": "erro", "mensagem": f"Tarefa não reconhecida: {tarefa}"}

    def compor_video(self, payload: dict) -> dict:
        import os
        audio_path = payload.get("audio_path", "")
        if not audio_path or not os.path.exists(audio_path):
            return {"status": "erro", "mensagem": f"Áudio não encontrado: {audio_path}"}

        resultado = pipeline_compose_short(
            titulo=payload.get("titulo", "Sem título"),
            canal=payload.get("canal", ""),
            script=payload.get("script", ""),
            audio_path=audio_path,
            resolucao=payload.get("resolucao", "1080x1920")
        )
        resultado["agente"] = self.AGENT_ID
        resultado["custo"] = "GRATUITO — FFmpeg local"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def criar_script(self, payload: dict) -> dict:
        job = criar_job_script(
            titulo=payload.get("titulo", ""),
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            duracao_alvo=payload.get("duracao_alvo", 60),
            palavras_chave=payload.get("palavras_chave", [])
        )
        job["agente"] = self.AGENT_ID
        return job

    def gerar_srt(self, payload: dict) -> dict:
        srt = gerar_srt_do_script(
            script=payload.get("script", ""),
            duracao_total=payload.get("duracao_total", 60.0)
        )
        return {
            "agente": self.AGENT_ID,
            "srt": srt,
            "status": "completed",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        ffmpeg = verificar_ffmpeg()
        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "ffmpeg": ffmpeg,
            "capacidades": ["compose_short", "compose_horizontal", "srt_legendas", "h264_aac"],
            "resolucoes": ["1080x1920 (Shorts)", "1920x1080 (Horizontal)", "1080x1080 (Square)"],
            "custo": "GRATUITO — FFmpeg local",
            "clone_de": "vidiq_compose + vidiq_generate_video",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
