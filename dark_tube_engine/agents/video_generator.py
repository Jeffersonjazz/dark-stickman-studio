"""
DARK TUBE ENGINE — AGENTE VIDEO GENERATOR
Geração de vídeos, animação e movimento
Clone funcional: vidiq_generate_video (via FFmpeg + modelos HF gratuitos)
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import uuid
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_composer import verificar_ffmpeg, gerar_video_fundo_ffmpeg


class VideoGeneratorAgent:
    """
    AGENTE VIDEO GENERATOR — Geração e animação de vídeos
    Stack: FFmpeg (local gratuito) + Modelos HF (opcionais)
    Alternativas: CogVideoX, HunyuanVideo, Wan via HuggingFace
    NOTA: Modelos de geração IA requerem GPU/VRAM — diagnóstico antes de instalar
    """

    AGENT_ID = "video_generator"
    VERSION = "1.0.0"

    # Backends disponíveis em ordem de custo (mais barato primeiro)
    BACKENDS = {
        "ffmpeg_gradient": {"custo": "GRATUITO", "gpu": False, "qualidade": "básica"},
        "cogvideox_hf": {"custo": "GRATUITO (HF API)", "gpu": True, "qualidade": "boa"},
        "hunyuanvideo": {"custo": "GRATUITO (local)", "gpu": True, "vram_min": "16GB"},
        "wan_hf": {"custo": "GRATUITO (HF API)", "gpu": True, "qualidade": "excelente"},
        "runway_api": {"custo": "PAGO", "gpu": False, "qualidade": "profissional"},
        "kling_api": {"custo": "PAGO", "gpu": False, "qualidade": "profissional"},
    }

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "broll" in tarefa or "fundo" in tarefa or "background" in tarefa:
            return self.gerar_fundo_video(payload)
        elif "animar" in tarefa or "motion" in tarefa:
            return self.gerar_video_motion(payload)
        else:
            return self.gerar_fundo_video(payload)  # default

    def gerar_fundo_video(self, payload: dict) -> dict:
        """Gera vídeo de fundo via FFmpeg (gratuito, sem GPU)."""
        audio_path = payload.get("audio_path", "")
        if not audio_path:
            # Sem áudio: retornar configuração para uso posterior
            return {
                "agente": self.AGENT_ID,
                "status": "configurado",
                "mensagem": "Forneça audio_path para gerar o vídeo. Ex: payload={'audio_path': 'outputs/audio/narr.mp3'}",
                "resolucao": payload.get("resolucao", "1080x1920"),
                "backend": "ffmpeg_gradient",
                "custo": "GRATUITO — FFmpeg local",
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
            }

        # Construir output_path completo (arquivo, não diretório)
        output_dir = payload.get("output_dir", "outputs/video")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        video_id = f"vid_{uuid.uuid4().hex[:8]}"
        output_path = str(Path(output_dir) / f"{video_id}.mp4")

        resultado = gerar_video_fundo_ffmpeg(
            audio_path=audio_path,
            output_path=output_path,
            cor_bg=payload.get("cor_bg", "0x0A0A1E"),
            resolucao=payload.get("resolucao", "1080x1920"),
            fps=payload.get("fps", 30)
        )
        resultado["agente"] = self.AGENT_ID
        resultado["backend"] = "ffmpeg_gradient"
        resultado["custo"] = "GRATUITO — FFmpeg local"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    def gerar_video_motion(self, payload: dict) -> dict:
        """
        Gera vídeo com movimento de câmera (pan, zoom, travelling).
        Implementação via FFmpeg zoompan filter.
        Para IA real: usar CogVideoX ou Wan via HuggingFace Inference API.
        """
        job_id = f"vid_{uuid.uuid4().hex[:12]}"

        # FFmpeg zoompan como alternativa gratuita
        resultado = {
            "job_id": job_id,
            "agente": self.AGENT_ID,
            "status": "pending_implementation",
            "backend_recomendado": "ffmpeg_zoompan",
            "alternativas_ia": {
                "CogVideoX": "https://huggingface.co/THUDM/CogVideoX-5b — requer GPU 24GB+",
                "Wan": "https://huggingface.co/Wan-AI/Wan2.1-T2V-14B — requer GPU 40GB+",
                "HunyuanVideo": "https://huggingface.co/tencent/HunyuanVideo — requer GPU 80GB+",
            },
            "nota": "Modelos de geração IA requerem diagnóstico de hardware antes da instalação",
            "custo": "GRATUITO via FFmpeg | API paga para qualidade profissional",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
        return resultado

    def status(self) -> dict:
        ffmpeg = verificar_ffmpeg()

        # Verificar GPU disponível
        try:
            import subprocess
            gpu_info = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                                       "--format=csv,noheader"], capture_output=True, text=True)
            gpu_disponivel = gpu_info.returncode == 0
            gpu_detalhes = gpu_info.stdout.strip() if gpu_disponivel else "GPU não detectada"
        except Exception:
            gpu_disponivel = False
            gpu_detalhes = "nvidia-smi não encontrado"

        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "ffmpeg": ffmpeg,
            "gpu_disponivel": gpu_disponivel,
            "gpu_detalhes": gpu_detalhes,
            "backends": self.BACKENDS,
            "backend_ativo": "ffmpeg_gradient",
            "nota": "Modelos IA de geração de vídeo requerem GPU dedicada com VRAM mínima de 16GB",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
