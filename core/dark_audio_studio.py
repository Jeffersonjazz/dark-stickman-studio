"""
DARK AUDIO STUDIO — FASE 6 do DARK CREATIVE LAB
Agente de narração, mixagem e masterização de áudio.

Motores TTS suportados (gratuitos):
  - ElevenLabs (via MCP — free tier)
  - Piper TTS (local, offline)
  - XTTS-v2 (local, alta qualidade)
  - Edge TTS (Microsoft, gratuito via API)
  - gTTS (Google, fallback)

Pós-produção:
  - FFmpeg: normalização, EQ, compressão, noise gate
  - Pydub: mixagem de trilhas
  - Whisper: transcrição e geração de legendas

Política: SEMPRE gratuito. ElevenLabs pago só com aprovação.

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import subprocess
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════
# FICHAS TÉCNICAS DOS MOTORES TTS
# ═══════════════════════════════════════════════════════
MOTORES_TTS = {
    "elevenlabs_free": {
        "nome": "ElevenLabs (Free Tier)",
        "tipo": "cloud_api",
        "custo": "Gratuito até 10.000 chars/mês",
        "qualidade": "★★★★★",
        "vozes_ptbr": True,
        "latencia": "2-5s",
        "emocoes": True,
        "modelo": "eleven_multilingual_v2",
        "acesso": "MCP Tool: mcp__ElevenLabs__creative_generate_speech",
        "vozes_recomendadas": {
            "dark_narrator": {"id": "acdKA5HckGxoxxvy40dA", "nome": "Nassif"},
            "motivacional": {"id": "9luRA11KwacKAVmLyqUs", "nome": "Edmilson"},
            "relaxamento": {"id": "NFmEzNOony1UsEJGXLth", "nome": "Voz Suave"},
        }
    },
    "piper": {
        "nome": "Piper TTS",
        "tipo": "local_offline",
        "custo": "GRATUITO (open source)",
        "qualidade": "★★★☆☆",
        "vozes_ptbr": True,
        "latencia": "<1s (CPU local)",
        "emocoes": False,
        "install": "pip install piper-tts --break-system-packages",
        "modelos_ptbr": ["pt_BR-faber-medium", "pt_BR-edresson-low"],
        "uso": "echo 'Texto' | piper --model pt_BR-faber-medium.onnx --output_file out.wav"
    },
    "xtts": {
        "nome": "XTTS-v2 (Coqui)",
        "tipo": "local_gpu",
        "custo": "GRATUITO (open source)",
        "qualidade": "★★★★☆",
        "vozes_ptbr": True,
        "latencia": "5-30s (GPU recomendada)",
        "emocoes": True,
        "install": "pip install TTS --break-system-packages",
        "vram_minima": "4GB",
        "nota": "Coqui descontinuado mas XTTS-v2 ainda funciona via TTS library"
    },
    "edge_tts": {
        "nome": "Edge TTS (Microsoft)",
        "tipo": "cloud_gratuito",
        "custo": "GRATUITO (sem limite prático)",
        "qualidade": "★★★★☆",
        "vozes_ptbr": True,
        "latencia": "1-3s",
        "emocoes": False,
        "install": "pip install edge-tts --break-system-packages",
        "vozes_ptbr_ids": ["pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"],
        "uso": "edge-tts --voice pt-BR-AntonioNeural --text 'Texto' --write-media out.mp3"
    },
    "gtts": {
        "nome": "gTTS (Google Text-to-Speech)",
        "tipo": "cloud_gratuito",
        "custo": "GRATUITO",
        "qualidade": "★★★☆☆",
        "vozes_ptbr": True,
        "latencia": "2-4s",
        "emocoes": False,
        "install": "pip install gtts --break-system-packages",
        "uso": "gtts-cli 'Texto' --lang pt --output out.mp3"
    }
}


class DarkAudioStudio:
    """
    Agente de pós-produção de áudio do DARK STUDIO AAA.
    """

    def __init__(self, output_dir: str = "outputs/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def verificar_ffmpeg(self) -> bool:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True)
        return r.returncode == 0

    def normalizar_audio(self, input_path: str, output_path: str = None,
                         loudness: float = -16.0) -> dict:
        """
        Normaliza volume para broadcast (-16 LUFS padrão YouTube).
        """
        if not output_path:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_norm{p.suffix}")

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-af", f"loudnorm=I={loudness}:TP=-1.5:LRA=11",
            "-ar", "44100", "-ac", "2",
            output_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            return {"status": "OK", "arquivo": output_path, "loudness_target": loudness}
        return {"status": "erro", "log": r.stderr[-200:]}

    def reduzir_ruido(self, input_path: str, output_path: str = None) -> dict:
        """
        Reduz ruído de fundo usando filtro anlmdn do FFmpeg.
        """
        if not output_path:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_denoise{p.suffix}")

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-af", "anlmdn=s=7:p=0.002:r=0.002:m=5:b=0.001",
            output_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            return {"status": "OK", "arquivo": output_path}
        return {"status": "erro", "log": r.stderr[-200:]}

    def masterizar(self, input_path: str, output_path: str = None,
                   preset: str = "narration") -> dict:
        """
        Masteriza áudio com presets por tipo de conteúdo.
        Presets: narration | podcast | music | relaxation | documentary
        """
        presets = {
            "narration": {
                "filters": [
                    "highpass=f=80",          # Remove rumble
                    "equalizer=f=3000:t=h:width=1000:g=2",  # Presença vocal
                    "compand=attacks=0.1:decays=0.5:points=-70/-70|-20/-15|-5/-3|0/-1",
                    "loudnorm=I=-16:TP=-1.5:LRA=7",
                ],
                "desc": "Narração clara e presente"
            },
            "documentary": {
                "filters": [
                    "highpass=f=60",
                    "equalizer=f=200:t=h:width=200:g=-3",  # Reduz boom
                    "equalizer=f=4000:t=h:width=2000:g=3", # Clareza
                    "compand=attacks=0.2:decays=1:points=-70/-70|-25/-18|-5/-2|0/-1",
                    "loudnorm=I=-16:TP=-1:LRA=9",
                ],
                "desc": "Tom de documentário profissional"
            },
            "relaxation": {
                "filters": [
                    "lowpass=f=8000",          # Corta agudos duros
                    "equalizer=f=300:t=h:width=200:g=2",   # Warmth
                    "compand=attacks=0.5:decays=2:points=-70/-70|-20/-17|-3/-2|0/-1",
                    "loudnorm=I=-18:TP=-2:LRA=12",
                ],
                "desc": "Som suave e relaxante"
            },
            "podcast": {
                "filters": [
                    "highpass=f=100",
                    "equalizer=f=1000:t=h:width=500:g=1",
                    "equalizer=f=5000:t=h:width=2000:g=2",
                    "compand=attacks=0.05:decays=0.3:points=-70/-70|-15/-10|-5/-2|0/-1",
                    "loudnorm=I=-16:TP=-1.5:LRA=7",
                ],
                "desc": "Tom podcast profissional"
            }
        }

        cfg = presets.get(preset, presets["narration"])
        af_chain = ",".join(cfg["filters"])

        if not output_path:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}_master_{preset}{p.suffix}")

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-af", af_chain,
            "-ar", "44100", "-ac", "2",
            "-b:a", "192k",
            output_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            return {"status": "OK", "arquivo": output_path,
                    "preset": preset, "descricao": cfg["desc"]}
        return {"status": "erro", "log": r.stderr[-200:]}

    def mixar_trilha(self, voz_path: str, musica_path: str,
                     output_path: str = None,
                     musica_vol: float = 0.12) -> dict:
        """
        Mixa narração com trilha sonora.
        musica_vol: volume da música (0.0-1.0, default 0.12 = -18dB)
        """
        if not Path(voz_path).exists():
            return {"status": "erro", "msg": f"Voz não encontrada: {voz_path}"}
        if not Path(musica_path).exists():
            return {"status": "erro", "msg": f"Música não encontrada: {musica_path}"}

        if not output_path:
            p = Path(voz_path)
            output_path = str(p.parent / f"{p.stem}_mix{p.suffix}")

        # Detectar duração da voz
        dur_result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", voz_path
        ], capture_output=True, text=True)
        dur = float(dur_result.stdout.strip() or "60")

        # Mixar: música em loop cortada na duração da voz, com fade out
        cmd = [
            "ffmpeg", "-y",
            "-i", voz_path,
            "-stream_loop", "-1", "-i", musica_path,
            "-t", str(dur),
            "-filter_complex",
            f"[1:a]volume={musica_vol},afade=t=out:st={max(0,dur-3)}:d=3[bg];"
            f"[0:a][bg]amix=inputs=2:duration=first[mix]",
            "-map", "[mix]",
            "-ar", "44100", "-b:a", "192k",
            output_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            return {"status": "OK", "arquivo": output_path,
                    "duracao": dur, "vol_musica": musica_vol}
        return {"status": "erro", "log": r.stderr[-200:]}

    def gerar_legendas_whisper(self, audio_path: str,
                                idioma: str = "pt",
                                output_dir: str = None) -> dict:
        """
        Gera legendas SRT via Whisper (gratuito, local).
        Requer: pip install openai-whisper --break-system-packages
        """
        try:
            import whisper
        except ImportError:
            return {
                "status": "erro_install",
                "msg": "Whisper não instalado",
                "install": "pip install openai-whisper --break-system-packages",
                "alternativa": "Use WhisperX para timestamps mais precisos: pip install whisperx"
            }

        if not output_dir:
            output_dir = str(Path(audio_path).parent)

        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=idioma, task="transcribe")

        # Gerar SRT
        srt_path = Path(output_dir) / (Path(audio_path).stem + ".srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(result["segments"], 1):
                start = seg["start"]
                end = seg["end"]
                text = seg["text"].strip()

                def fmt_time(t):
                    h = int(t // 3600)
                    m = int((t % 3600) // 60)
                    s = int(t % 60)
                    ms = int((t % 1) * 1000)
                    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

                f.write(f"{i}\n{fmt_time(start)} --> {fmt_time(end)}\n{text}\n\n")

        return {
            "status": "OK",
            "srt": str(srt_path),
            "texto_completo": result["text"],
            "segmentos": len(result["segments"]),
            "idioma": result.get("language", "?")
        }

    def tts_edge(self, texto: str, output_path: str,
                 voz: str = "pt-BR-AntonioNeural") -> dict:
        """
        Narração via Edge TTS (Microsoft, gratuito).
        """
        try:
            r = subprocess.run([
                "edge-tts", "--voice", voz,
                "--text", texto,
                "--write-media", output_path
            ], capture_output=True, text=True, timeout=60)
            if r.returncode == 0 and Path(output_path).exists():
                return {"status": "OK", "arquivo": output_path,
                        "voz": voz, "custo": "GRATUITO"}
            return {"status": "erro", "log": r.stderr[-200:],
                    "install": "pip install edge-tts --break-system-packages"}
        except FileNotFoundError:
            return {"status": "erro", "msg": "edge-tts não instalado",
                    "install": "pip install edge-tts --break-system-packages"}

    def pipeline_completo(self, texto: str, nome: str,
                          estilo: str = "documentary",
                          musica: Optional[str] = None) -> dict:
        """
        Pipeline completo: TTS → normalização → masterização → mix (opcional)
        """
        print(f"\n[AUDIO_MASTER] Pipeline: {nome} ({estilo})")

        # 1. TTS via Edge (gratuito, sem install extra)
        raw = str(self.output_dir / f"{nome}_raw.mp3")
        tts = self.tts_edge(texto, raw)
        if tts["status"] != "OK":
            print(f"  ⚠ Edge TTS falhou: {tts.get('msg','?')}")
            return tts

        print(f"  ✅ TTS gerado: {raw}")

        # 2. Masterizar
        master = self.masterizar(raw, preset=estilo)
        if master["status"] != "OK":
            print(f"  ⚠ Masterização falhou")
            master["arquivo"] = raw  # Usar bruto

        master_path = master.get("arquivo", raw)
        print(f"  ✅ Masterizado: {master_path}")

        # 3. Mixar com música (opcional)
        final_path = master_path
        if musica and Path(musica).exists():
            mix = self.mixar_trilha(master_path, musica)
            if mix["status"] == "OK":
                final_path = mix["arquivo"]
                print(f"  ✅ Mixado com trilha: {final_path}")

        return {
            "status": "OK",
            "arquivo_final": final_path,
            "nome": nome,
            "estilo": estilo,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }


# ═══════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════
CONTRACT = {
    "agente": "AUDIO_MASTER",
    "versao": "1.0.0",
    "descricao": "Narração, mixagem e masterização de áudio",
    "entrada": {
        "texto": "str — script para narração",
        "nome": "str — identificador do arquivo",
        "estilo": "str? — narration|documentary|relaxation|podcast",
        "musica": "str? — path da trilha sonora (opcional)",
        "motor_tts": "str? — elevenlabs|edge_tts|piper|xtts"
    },
    "saida": {
        "status": "OK|erro",
        "arquivo_final": "str — path do MP3 masterizado",
        "ai_generated": True,
        "ai_disclosure": "str"
    },
    "motores_tts": list(MOTORES_TTS.keys()),
    "politica_custo": "SEMPRE gratuito. ElevenLabs pago só com aprovação."
}


if __name__ == "__main__":
    studio = DarkAudioStudio()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK AUDIO STUDIO — FASE 6                         ║")
    print("║   Narração + Pós-produção de Áudio                   ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    print("MOTORES TTS DISPONÍVEIS:")
    for nome, m in MOTORES_TTS.items():
        print(f"\n  [{nome.upper()}]")
        print(f"    Custo: {m['custo']}")
        print(f"    Qualidade: {m['qualidade']}")
        print(f"    Vozes PT-BR: {'✅' if m['vozes_ptbr'] else '❌'}")
        print(f"    Latência: {m['latencia']}")

    print("\nVERIFICANDO FFMPEG:")
    if studio.verificar_ffmpeg():
        print("  ✅ FFmpeg disponível")
    else:
        print("  ✗ FFmpeg não encontrado")

    # Salvar contrato
    with open("core/dark_audio_studio_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print("\n  Contrato: core/dark_audio_studio_contract.json")
    print("\n  Para narração offline: instale edge-tts")
    print("  pip install edge-tts --break-system-packages\n")
