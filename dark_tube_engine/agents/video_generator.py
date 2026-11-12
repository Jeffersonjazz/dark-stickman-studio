"""
DARK TUBE ENGINE — AGENTE VIDEO GENERATOR v2.0
Fase 3: DARK VIDEO STUDIO — Wan 2.2 I2V + FFmpeg zoompan + pipeline B-roll
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

Hierarquia de backends (ordem de preferência / custo):
1. FFmpeg zoompan  — gratuito, local, sem GPU, instantâneo
2. Wan 2.2 I2V     — gratuito, HF Space, precisa de GPU no Space, 60-300s
3. Wan 2.2 T2V     — gratuito, HF Space, texto→vídeo (experimental)
4. Runway / Kling  — pagos, qualidade profissional (future)
"""
import sys
import uuid
import subprocess
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.video_composer import (
    verificar_ffmpeg,
    gerar_video_fundo_ffmpeg,
    pipeline_compose_short,
)

try:
    from core.wan_client import (
        imagem_para_video_wan,
        gerar_zoompan_ffmpeg,
        gerar_broll_de_thumbnail,
        gerar_pack_broll,
        concatenar_clips,
        status_wan_client,
        ZOOMPAN_EFFECTS,
        MOTION_PRESETS,
        CANAL_PARA_NICHO,
    )
    WAN_CLIENT_AVAILABLE = True
except ImportError:
    WAN_CLIENT_AVAILABLE = False


class VideoGeneratorAgent:
    """
    AGENTE VIDEO GENERATOR v2.0 — DARK VIDEO STUDIO
    Capacidades Fase 3:
    - Imagem → vídeo animado (Wan 2.2 I2V ou FFmpeg zoompan)
    - B-roll automático a partir de thumbnails FLUX
    - Pack de clipes para Shorts (múltiplas imagens → vídeo final)
    - Concatenação de clips em vídeo único
    - Presets de movimento por nicho (zoom, pan, kenburns, travelling)
    - Fundo animado FFmpeg para Shorts (sem imagem de entrada)
    """

    AGENT_ID = "video_generator"
    VERSION = "2.0.0"

    BACKENDS = {
        "ffmpeg_zoompan":  {"custo": "GRATUITO", "gpu": False, "qualidade": "boa", "latencia": "5s"},
        "ffmpeg_gradient": {"custo": "GRATUITO", "gpu": False, "qualidade": "básica", "latencia": "5s"},
        "wan_i2v":         {"custo": "GRATUITO (HF Space)", "gpu": True, "qualidade": "excelente", "latencia": "60-300s"},
        "wan_t2v":         {"custo": "GRATUITO (HF Space)", "gpu": True, "qualidade": "excelente", "latencia": "120-360s"},
        "runway_api":      {"custo": "PAGO", "gpu": False, "qualidade": "profissional", "latencia": "30-60s"},
        "kling_api":       {"custo": "PAGO", "gpu": False, "qualidade": "profissional", "latencia": "30-60s"},
    }

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        roteamento = {
            "broll":        self.gerar_broll,
            "thumbnail_animada": self.gerar_broll,
            "zoompan":      self.gerar_zoompan,
            "motion":       self.gerar_zoompan,
            "wan_i2v":      self.gerar_video_wan,
            "imagem_para_video": self.gerar_video_wan,
            "pack_broll":   self.gerar_pack_broll,
            "concatenar":   self.concatenar,
            "fundo":        self.gerar_fundo,
            "background":   self.gerar_fundo,
            "short_completo": self.montar_short_completo,
            "status":       lambda p: self.status(),
        }

        for chave, func in roteamento.items():
            if chave in tarefa:
                return func(payload)

        # Default: fundo animado (retrocompatibilidade v1)
        return self.gerar_fundo(payload)

    # ------------------------------------------------------------------
    # B-roll: thumbnail → vídeo animado (Wan ou zoompan)
    # ------------------------------------------------------------------

    def gerar_broll(self, payload: dict) -> dict:
        """
        Converte thumbnail/imagem em clipe animado para B-roll.
        Usa preset de movimento automático pelo canal/nicho.
        """
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        imagem = payload.get("imagem") or payload.get("imagem_path") or payload.get("path")
        if not imagem:
            return {"status": "erro", "mensagem": "payload.imagem é obrigatório"}

        resultado = gerar_broll_de_thumbnail(
            imagem_path=imagem,
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            output_dir=payload.get("output_dir", "outputs/video"),
            usar_wan=payload.get("usar_wan", False),  # FFmpeg por padrão (rápido)
            hf_token=payload.get("hf_token"),
            duracao_s=payload.get("duracao_s", 7.0),
            resolucao_short=payload.get("resolucao", "1080x1920"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # FFmpeg zoompan direto (controle total do efeito)
    # ------------------------------------------------------------------

    def gerar_zoompan(self, payload: dict) -> dict:
        """
        Anima imagem com efeito de câmera específico via FFmpeg zoompan.
        Efeitos disponíveis: zoom_in, zoom_out, pan_left, pan_right,
                             pan_up, pan_down, travelling, kenburns
        """
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        imagem = payload.get("imagem") or payload.get("path")
        if not imagem:
            return {"status": "erro", "mensagem": "payload.imagem é obrigatório"}

        resultado = gerar_zoompan_ffmpeg(
            imagem_path=imagem,
            efeito=payload.get("efeito", "zoom_in"),
            duracao_s=payload.get("duracao_s", 7.0),
            fps=payload.get("fps", 25),
            resolucao=payload.get("resolucao", "1080x1920"),
            output_dir=payload.get("output_dir", "outputs/video"),
            audio_path=payload.get("audio_path"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Wan 2.2 I2V (imagem → vídeo IA)
    # ------------------------------------------------------------------

    def gerar_video_wan(self, payload: dict) -> dict:
        """
        Converte imagem em vídeo via Wan 2.2 I2V (HF Space).
        Mais lento mas melhor qualidade — requer GPU no Space.
        """
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        imagem = payload.get("imagem") or payload.get("imagem_path") or payload.get("path")
        if not imagem:
            return {"status": "erro", "mensagem": "payload.imagem é obrigatório"}

        resultado = imagem_para_video_wan(
            imagem_path=imagem,
            prompt=payload.get("prompt", "cinematic camera movement, smooth motion, high quality"),
            duracao_frames=payload.get("frames", 81),
            resolucao=payload.get("resolucao_wan", "720p"),
            output_dir=payload.get("output_dir", "outputs/video"),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Pack de B-roll (múltiplas imagens)
    # ------------------------------------------------------------------

    def gerar_pack_broll(self, payload: dict) -> dict:
        """
        Gera pack de clipes B-roll a partir de lista de imagens.
        Alterna efeitos (zoom, pan, kenburns, travelling) entre imagens.
        """
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        imagens = payload.get("imagens", [])
        if not imagens:
            return {"status": "erro", "mensagem": "payload.imagens (lista) é obrigatório"}

        resultado = gerar_pack_broll(
            imagens=imagens,
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            output_dir=payload.get("output_dir", "outputs/video"),
            usar_wan=payload.get("usar_wan", False),
            hf_token=payload.get("hf_token"),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Concatenação de clips
    # ------------------------------------------------------------------

    def concatenar(self, payload: dict) -> dict:
        """Concatena lista de vídeos MP4 em um único arquivo."""
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        clips = payload.get("clips") or payload.get("clips_paths", [])
        if not clips:
            return {"status": "erro", "mensagem": "payload.clips (lista de paths) é obrigatório"}

        output = payload.get("output_path") or (
            f"outputs/video/final_{str(uuid.uuid4())[:8]}.mp4"
        )
        resultado = concatenar_clips(
            clips_paths=clips,
            output_path=output,
            adicionar_fade=payload.get("fade", True),
        )
        resultado["agente"] = self.AGENT_ID
        return resultado

    # ------------------------------------------------------------------
    # Fundo animado FFmpeg (retrocompatibilidade v1)
    # ------------------------------------------------------------------

    def gerar_fundo(self, payload: dict) -> dict:
        """Gera vídeo de fundo sólido via FFmpeg (retrocompatível com v1)."""
        audio_path = payload.get("audio_path", "")
        if not audio_path:
            return {
                "agente": self.AGENT_ID,
                "status": "configurado",
                "mensagem": "Forneça audio_path para gerar. Ou use gerar_broll para animar uma imagem.",
                "resolucao": payload.get("resolucao", "1080x1920"),
                "backend": "ffmpeg_gradient",
                "custo": "GRATUITO — FFmpeg local",
                "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
            }

        output_dir = payload.get("output_dir", "outputs/video")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        vid_id = f"vid_{uuid.uuid4().hex[:8]}"
        output_path = str(Path(output_dir) / f"{vid_id}.mp4")

        resultado = gerar_video_fundo_ffmpeg(
            audio_path=audio_path,
            output_path=output_path,
            cor_bg=payload.get("cor_bg", "0x0A0A1E"),
            resolucao=payload.get("resolucao", "1080x1920"),
            fps=payload.get("fps", 30),
        )
        resultado["agente"] = self.AGENT_ID
        resultado["backend"] = "ffmpeg_gradient"
        resultado["custo"] = "GRATUITO — FFmpeg local"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    # ------------------------------------------------------------------
    # Pipeline Short completo com B-roll
    # ------------------------------------------------------------------

    def montar_short_completo(self, payload: dict) -> dict:
        """
        Pipeline completo: imagens → clipes B-roll → Short montado com áudio.
        Encadeia gerar_pack_broll → concatenar → adicionar áudio.
        """
        if not WAN_CLIENT_AVAILABLE:
            return {"status": "erro", "mensagem": "wan_client não disponível"}

        imagens = payload.get("imagens", [])
        audio_path = payload.get("audio_path")
        output_dir = payload.get("output_dir", "outputs/video")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if not imagens:
            return {"status": "erro", "mensagem": "payload.imagens (lista) é obrigatório"}

        # Passo 1: Gera clipes individuais
        pack = gerar_pack_broll(
            imagens=imagens,
            canal=payload.get("canal", ""),
            nicho=payload.get("nicho"),
            output_dir=output_dir,
            usar_wan=payload.get("usar_wan", False),
        )

        clips_ok = [c["path"] for c in pack["clips"] if c.get("status") == "completed" and c.get("path")]
        if not clips_ok:
            return {"status": "failed", "erro": "Nenhum clip gerado com sucesso", "pack": pack}

        # Passo 2: Concatena clipes
        vid_id = str(uuid.uuid4())[:8]
        concat_path = os.path.join(output_dir, f"concat_{vid_id}.mp4")
        concat = concatenar_clips(clips_ok, concat_path)

        if concat.get("status") != "completed":
            return {"status": "failed", "erro": concat.get("error"), "pack": pack}

        # Passo 3: Adiciona áudio se fornecido
        if audio_path and os.path.exists(audio_path):
            final_path = os.path.join(output_dir, f"short_{vid_id}.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-i", concat_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                final_path
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            video_final = final_path if r.returncode == 0 else concat_path
        else:
            video_final = concat_path

        return {
            "status": "completed",
            "path": video_final,
            "clips": clips_ok,
            "total_clips": len(clips_ok),
            "canal": payload.get("canal", ""),
            "agente": self.AGENT_ID,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        ffmpeg = verificar_ffmpeg()
        wan_st = status_wan_client() if WAN_CLIENT_AVAILABLE else {"gradio_client": False}

        try:
            r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                                 "--format=csv,noheader"], capture_output=True, text=True, timeout=5)
            gpu_ok = r.returncode == 0
            gpu_det = r.stdout.strip() if gpu_ok else "GPU não detectada"
        except Exception:
            gpu_ok = False
            gpu_det = "nvidia-smi não encontrado"

        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "fase": "3 — DARK VIDEO STUDIO",
            "ffmpeg": ffmpeg,
            "wan_client": WAN_CLIENT_AVAILABLE,
            "gradio_client": wan_st.get("gradio_client", False),
            "gpu_local": gpu_ok,
            "gpu_detalhes": gpu_det,
            "backends": self.BACKENDS,
            "backend_padrao": "ffmpeg_zoompan (gratuito, sem GPU)",
            "efeitos_zoompan": list(ZOOMPAN_EFFECTS.keys()) if WAN_CLIENT_AVAILABLE else [],
            "motion_presets": list(MOTION_PRESETS.keys()) if WAN_CLIENT_AVAILABLE else [],
            "capacidades": [
                "broll (thumbnail → vídeo animado)",
                "zoompan (zoom_in/out, pan, kenburns, travelling)",
                "wan_i2v (imagem → vídeo IA — HF Space)",
                "pack_broll (múltiplas imagens → pack de clips)",
                "concatenar (clips → vídeo único)",
                "short_completo (pipeline imagens + áudio → Short)",
                "fundo (background gradient FFmpeg — v1 compat)",
            ],
            "custo": "GRATUITO — FFmpeg local + HF Space (Wan I2V)",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# Fix: import os necessário aqui
import os
