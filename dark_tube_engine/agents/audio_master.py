"""
DARK TUBE ENGINE — AGENTE AUDIO MASTER
Narração, mixagem, tratamento e masterização
Clone funcional: vidiq_voiceover_generate (GRATUITO via edge-tts)
ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.tts_engine import gerar_voiceover, listar_vozes, VOZES_PTBR, gerar_voiceover_sync


class AudioMasterAgent:
    """
    AGENTE AUDIO MASTER — Narração e pós-produção de áudio
    Stack: edge-tts (Microsoft Neural TTS) — GRATUITO, ilimitado, PT-BR excelente
    Alternativa: gTTS (Google TTS) como fallback
    Clone: vidiq_voiceover_generate sem custo de créditos
    """

    AGENT_ID = "audio_master"
    VERSION = "1.0.0"

    def executar(self, contrato: dict) -> dict:
        tarefa = contrato.get("tarefa", "")
        payload = contrato.get("payload", {})

        if "narrar" in tarefa or "voiceover" in tarefa or "tts" in tarefa:
            return self.gerar_narração(payload)
        elif "vozes" in tarefa or "listar" in tarefa:
            return asyncio.run(self.listar_vozes_disponiveis())
        else:
            return {"status": "erro", "mensagem": f"Tarefa não reconhecida: {tarefa}"}

    def gerar_narração(self, payload: dict) -> dict:
        script = payload.get("script", "")
        canal = payload.get("canal", "")
        voice_id = payload.get("voice_id", "pt-BR-AntonioNeural")
        rate = payload.get("rate", "+0%")

        # Selecionar voz automática pelo canal/nicho
        nicho_voz_map = {
            "Mente de Aço": "narrativa",
            "Esquina do Medo": "terror",
            "Intelligentia Nova": "tech_ia",
            "Projeto Secreto": "conspiracao",
            "AquaZen Relax": "relaxamento",
            "Dark Nature": "documentario",
            "Historia Sombria": "documentario",
        }
        if canal in nicho_voz_map:
            nicho = nicho_voz_map[canal]
            if nicho in VOZES_PTBR:
                voice_id = VOZES_PTBR[nicho]["voz"]

        resultado = gerar_voiceover_sync(
            script=script,
            voice_id=voice_id,
            output_dir="outputs/audio"
        )
        resultado["agente"] = self.AGENT_ID
        resultado["custo"] = "GRATUITO — edge-tts Microsoft Neural TTS"
        resultado["ai_disclosure"] = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        return resultado

    async def listar_vozes_disponiveis(self) -> dict:
        vozes = await listar_vozes()
        return {
            "agente": self.AGENT_ID,
            "total_vozes": len(vozes),
            "vozes": vozes,
            "vozes_por_nicho": VOZES_PTBR,
            "backend": "edge-tts (GRATUITO)",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }

    def status(self) -> dict:
        try:
            import edge_tts
            tts_ok = True
            backend = "edge-tts"
        except ImportError:
            try:
                import gtts
                tts_ok = True
                backend = "gtts (fallback)"
            except ImportError:
                tts_ok = False
                backend = "indisponível"

        return {
            "agente": self.AGENT_ID,
            "versao": self.VERSION,
            "tts_disponivel": tts_ok,
            "backend": backend,
            "vozes_configuradas": len(VOZES_PTBR),
            "custo": "GRATUITO — edge-tts ilimitado",
            "clone_de": "vidiq_voiceover_generate",
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }
