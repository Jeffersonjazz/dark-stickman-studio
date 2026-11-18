"""
DARK EDGE TTS — Motor de Narração Gratuito (Edge TTS + Cascata)
================================================================
Motor TTS primário do DARK STUDIO AAA após bloqueio do ElevenLabs.

Engines disponíveis (em ordem de prioridade):
  Tier 1: Edge TTS (Microsoft Neural, cloud gratuito, sem API key)
  Tier 2: gTTS (Google Text-to-Speech, cloud gratuito)
  Tier 3: espeak-ng (offline, via espeakng_loader)
  Tier 4: Piper TTS (local, precisa de modelos instalados)
  Tier 5: Silêncio (fallback final, nunca falha)

Vozes PT-BR disponíveis:
  - pt-BR-FranciscaNeural  : feminina, suave, natural
  - pt-BR-AntonioNeural    : masculino, profissional
  - pt-BR-ThalitaNeural    : feminina, jovem, animada (Edge TTS v1.5+)

Mapeamento por canal DARK STUDIO:
  Mente de Aço / documentário / história → AntonioNeural (masculino)
  AquaZen / relaxamento / meditação      → FranciscaNeural (feminina)
  Universo Misterioso / suspense         → AntonioNeural
  Corte Brasil / notícias                → AntonioNeural
  Shorts verticais                       → FranciscaNeural (padrão)

Uso rápido:
    from core.dark_edge_tts import DarkEdgeTTS
    tts = DarkEdgeTTS()
    path = tts.narrar("Bem-vindo ao canal.", "audio.mp3", canal="mente_de_aco")
    path = tts.narrar_roteiro(["Cena 1.", "Cena 2."], "outputs/audio/")

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
Licença: MIT
"""

import asyncio
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE VOZES
# ═══════════════════════════════════════════════════════════════════════

# Mapeamento de voz por idioma + gênero
VOZES_EDGE_TTS: Dict[str, Dict[str, str]] = {
    "pt-BR": {
        "masculino":  "pt-BR-AntonioNeural",
        "feminino":   "pt-BR-FranciscaNeural",
        "jovem":      "pt-BR-ThalitaNeural",
        "padrao":     "pt-BR-FranciscaNeural",
    },
    "pt-PT": {
        "masculino":  "pt-PT-DuarteNeural",
        "feminino":   "pt-PT-RaquelNeural",
        "padrao":     "pt-PT-RaquelNeural",
    },
    "en-US": {
        "masculino":  "en-US-GuyNeural",
        "feminino":   "en-US-JennyNeural",
        "jovem":      "en-US-AriaNeural",
        "padrao":     "en-US-JennyNeural",
    },
    "en-GB": {
        "masculino":  "en-GB-RyanNeural",
        "feminino":   "en-GB-SoniaNeural",
        "padrao":     "en-GB-SoniaNeural",
    },
    "es-ES": {
        "masculino":  "es-ES-AlvaroNeural",
        "feminino":   "es-ES-ElviraNeural",
        "padrao":     "es-ES-ElviraNeural",
    },
    "es-MX": {
        "masculino":  "es-MX-JorgeNeural",
        "feminino":   "es-MX-DaliaNeural",
        "padrao":     "es-MX-DaliaNeural",
    },
    "fr-FR": {
        "masculino":  "fr-FR-HenriNeural",
        "feminino":   "fr-FR-DeniseNeural",
        "padrao":     "fr-FR-DeniseNeural",
    },
    "de-DE": {
        "masculino":  "de-DE-ConradNeural",
        "feminino":   "de-DE-KatjaNeural",
        "padrao":     "de-DE-KatjaNeural",
    },
    "it-IT": {
        "masculino":  "it-IT-DiegoNeural",
        "feminino":   "it-IT-ElsaNeural",
        "padrao":     "it-IT-ElsaNeural",
    },
    "ja-JP": {
        "masculino":  "ja-JP-KeitaNeural",
        "feminino":   "ja-JP-NanamiNeural",
        "padrao":     "ja-JP-NanamiNeural",
    },
    "zh-CN": {
        "masculino":  "zh-CN-YunxiNeural",
        "feminino":   "zh-CN-XiaoxiaoNeural",
        "padrao":     "zh-CN-XiaoxiaoNeural",
    },
}

# Mapeamento de canal para voz preferida
VOZES_CANAL: Dict[str, str] = {
    # Canais DARK STUDIO AAA
    "mente_de_aco":           "pt-BR-AntonioNeural",
    "universo_misterioso":    "pt-BR-AntonioNeural",
    "esquina_do_medo":        "pt-BR-AntonioNeural",
    "corte_brasil":           "pt-BR-AntonioNeural",
    "aquazen":                "pt-BR-FranciscaNeural",
    "aquazen_relax":          "pt-BR-FranciscaNeural",
    "shorts_dark":            "pt-BR-FranciscaNeural",
    # Tipos de conteúdo
    "documentario":           "pt-BR-AntonioNeural",
    "historia":               "pt-BR-AntonioNeural",
    "suspense":               "pt-BR-AntonioNeural",
    "misterio":               "pt-BR-AntonioNeural",
    "motivacional":           "pt-BR-AntonioNeural",
    "relaxamento":            "pt-BR-FranciscaNeural",
    "meditacao":              "pt-BR-FranciscaNeural",
    "natureza":               "pt-BR-FranciscaNeural",
    "educacao":               "pt-BR-FranciscaNeural",
    "shorts":                 "pt-BR-FranciscaNeural",
    # Default
    "padrao":                 "pt-BR-FranciscaNeural",
}

# Taxa de fala por estilo (SSML rate)
TAXA_FALA: Dict[str, str] = {
    "normal":      "+0%",
    "lento":       "-10%",
    "rapido":      "+10%",
    "muito_rapido": "+20%",
    "muito_lento": "-20%",
    "suspense":    "-8%",
    "relaxamento": "-15%",
    "shorts":      "+5%",
}


# ═══════════════════════════════════════════════════════════════════════
# ENGINES INTERNOS
# ═══════════════════════════════════════════════════════════════════════

def _run_async_safe(coro):
    """Executa coroutine de forma segura em qualquer contexto."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Dentro de contexto async (FastAPI, Jupyter, etc)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result(timeout=90)
    else:
        return asyncio.run(coro)


def _engine_edge_tts(texto: str, output_mp3: Path, voz: str) -> bool:
    """
    Tier 1: Edge TTS via Python library (import edge_tts).
    100% gratuito, sem API key, qualidade neural excelente.
    """
    try:
        import edge_tts

        async def _generate():
            communicate = edge_tts.Communicate(texto, voz)
            await communicate.save(str(output_mp3))

        _run_async_safe(_generate())

        ok = output_mp3.exists() and output_mp3.stat().st_size > 500
        if ok:
            print(f"[EDGE-TTS] ✅ {voz} → {output_mp3.name} ({output_mp3.stat().st_size // 1024}KB)")
        return ok

    except Exception as e:
        print(f"[EDGE-TTS] ✗ Falhou: {e}")
        return False


def _engine_gtts(texto: str, output_mp3: Path, lang: str = "pt") -> bool:
    """
    Tier 2: gTTS (Google Text-to-Speech, cloud gratuito).
    Qualidade: boa mas monótona vs edge-tts.
    """
    try:
        from gtts import gTTS
        tts = gTTS(text=texto, lang=lang, tld="com.br", slow=False)
        tts.save(str(output_mp3))
        ok = output_mp3.exists() and output_mp3.stat().st_size > 500
        if ok:
            print(f"[gTTS] ✅ → {output_mp3.name}")
        return ok
    except Exception as e:
        print(f"[gTTS] ✗ Falhou: {e}")
        return False


def _engine_espeak(texto: str, output_path: Path) -> bool:
    """
    Tier 3: espeak-ng via espeakng_loader (totalmente offline).
    Qualidade: robótica mas inteligível.
    """
    try:
        import espeakng_loader, ctypes, wave, struct
        lib = ctypes.CDLL(str(espeakng_loader.get_library_path()))
        data_path = str(espeakng_loader.get_data_path())
        AUDIO_OUTPUT_SYNCHRONOUS = 0x02
        ESPEAKNG_ENCODING_UTF8 = 1
        sample_rate = lib.espeak_Initialize(AUDIO_OUTPUT_SYNCHRONOUS, 500, data_path.encode(), 0)
        if sample_rate <= 0:
            return False
        lib.espeak_SetVoiceByName(b"pt-br")
        audio_data = []
        SYNTH_CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p)
        def _cb(wav, numsamples, events):
            if wav and numsamples > 0:
                samples = (ctypes.c_short * numsamples).from_address(wav)
                audio_data.extend(list(samples))
            return 0
        cb = SYNTH_CB(_cb)
        lib.espeak_SetSynthCallback(cb)
        enc = texto.encode("utf-8")
        lib.espeak_Synth(enc, len(enc)+1, 0, 0, 0, ESPEAKNG_ENCODING_UTF8,
                         ctypes.c_void_p(0), ctypes.c_void_p(0))
        lib.espeak_Synchronize()
        if not audio_data:
            return False
        wav_path = output_path.with_suffix(".wav")
        with wave.open(str(wav_path), "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f"<{len(audio_data)}h", *audio_data))
        # Converte WAV → MP3
        if output_path.suffix == ".mp3":
            ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
            r = subprocess.run([ffmpeg, "-y", "-i", str(wav_path), str(output_path)],
                               capture_output=True, check=False)
            wav_path.unlink(missing_ok=True)
            ok = r.returncode == 0 and output_path.exists()
        else:
            wav_path.rename(output_path)
            ok = output_path.exists()
        if ok:
            print(f"[ESPEAK-NG] ✅ → {output_path.name}")
        return ok
    except Exception as e:
        print(f"[ESPEAK-NG] ✗ Falhou: {e}")
        return False


def _engine_piper(texto: str, output_path: Path, modelo: str = "pt_BR-faber-medium") -> bool:
    """
    Tier 4: Piper TTS (local, precisa de modelos instalados).
    Alta qualidade quando disponível.
    """
    try:
        piper_bin = shutil.which("piper") or os.environ.get("PIPER_PATH", "piper")
        models_dir = Path(__file__).parent.parent / "assets" / "models" / "piper"
        model_file = models_dir / f"{modelo}.onnx"
        if not model_file.exists():
            return False
        wav_path = output_path.with_suffix(".wav")
        cmd = [piper_bin, "--model", str(model_file), "--output_file", str(wav_path)]
        config = model_file.with_suffix(".onnx.json")
        if config.exists():
            cmd += ["--config", str(config)]
        r = subprocess.run(cmd, input=texto, capture_output=True, text=True, timeout=60, check=False)
        if r.returncode != 0 or not wav_path.exists():
            return False
        if output_path.suffix == ".mp3":
            ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
            r2 = subprocess.run([ffmpeg, "-y", "-i", str(wav_path), str(output_path)],
                                capture_output=True, check=False)
            wav_path.unlink(missing_ok=True)
            ok = r2.returncode == 0 and output_path.exists()
        else:
            wav_path.rename(output_path)
            ok = output_path.exists()
        if ok:
            print(f"[PIPER] ✅ → {output_path.name}")
        return ok
    except Exception as e:
        print(f"[PIPER] ✗ Falhou: {e}")
        return False


def _engine_silencio(output_path: Path, texto: str) -> bool:
    """Tier 5: gera silêncio proporcional ao texto (nunca falha)."""
    try:
        words = len(texto.split())
        dur = max(3.0, words * 0.42)
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        r = subprocess.run(
            [ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono",
             "-t", str(dur), str(output_path)],
            capture_output=True, check=False, timeout=30
        )
        ok = r.returncode == 0 and output_path.exists()
        if ok:
            print(f"[SILÊNCIO] ⚠️ fallback {dur:.0f}s → {output_path.name}")
        return ok
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class DarkEdgeTTS:
    """
    Motor TTS primário do DARK STUDIO AAA.
    Substitui ElevenLabs com cascata 100% gratuita.

    Cascata: Edge-TTS → gTTS → espeak-ng → Piper → Silêncio

    Uso:
        tts = DarkEdgeTTS()
        # Por nome de canal:
        path = tts.narrar("Texto.", "saida.mp3", canal="mente_de_aco")
        # Por idioma:
        path = tts.narrar("Text.", "out.mp3", idioma="en-US", genero="masculino")
        # Por voz específica:
        path = tts.narrar("Texto.", "saida.mp3", voz="pt-BR-AntonioNeural")
    """

    def __init__(self, output_dir: str = "outputs/audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._status_cache: Optional[Dict] = None

    # ─────────────────────────────────────────────────────────
    # SELEÇÃO DE VOZ
    # ─────────────────────────────────────────────────────────

    def selecionar_voz(
        self,
        canal: Optional[str] = None,
        idioma: str = "pt-BR",
        genero: str = "padrao",
        voz: Optional[str] = None,
    ) -> str:
        """Retorna o ID de voz mais adequado para o contexto."""
        if voz:
            return voz

        if canal:
            canal_key = canal.lower().replace(" ", "_").replace("-", "_")
            if canal_key in VOZES_CANAL:
                return VOZES_CANAL[canal_key]

        idioma_vozes = VOZES_EDGE_TTS.get(idioma, VOZES_EDGE_TTS["pt-BR"])
        return idioma_vozes.get(genero, idioma_vozes["padrao"])

    def listar_vozes_disponiveis(self, idioma: str = "pt-BR") -> List[str]:
        """Lista vozes disponíveis para um idioma."""
        vozes = VOZES_EDGE_TTS.get(idioma, {})
        return list(set(vozes.values()))

    # ─────────────────────────────────────────────────────────
    # NARRAÇÃO PRINCIPAL
    # ─────────────────────────────────────────────────────────

    def narrar(
        self,
        texto: str,
        output_path: str,
        canal: Optional[str] = None,
        idioma: str = "pt-BR",
        genero: str = "padrao",
        voz: Optional[str] = None,
        velocidade: str = "normal",
    ) -> Dict[str, Any]:
        """
        Narra texto com cascata automática de TTS.

        Args:
            texto: Texto a narrar.
            output_path: Caminho do arquivo de saída (.mp3 ou .wav).
            canal: Nome do canal DARK STUDIO (ex: "mente_de_aco").
            idioma: Código ISO 639-1 (ex: "pt-BR", "en-US").
            genero: "masculino", "feminino", "jovem" ou "padrao".
            voz: ID direto de voz edge-tts (sobrescreve canal/idioma/genero).
            velocidade: "normal", "lento", "rapido", "suspense", "relaxamento".

        Returns:
            Dict com status, arquivo, motor, voz, custo.
        """
        if not texto.strip():
            return {"status": "erro", "msg": "Texto vazio"}

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        voz_id = self.selecionar_voz(canal, idioma, genero, voz)
        lang_gtts = idioma.split("-")[0] if "-" in idioma else idioma

        print(f"\n[DARK-TTS] Narrando: {output_path.name}")
        print(f"           Voz: {voz_id} | Canal: {canal or 'padrão'} | {len(texto)} chars")

        # ── Tier 1: Edge TTS ──────────────────────────────────
        if _engine_edge_tts(texto, output_path, voz_id):
            return {
                "status": "OK", "arquivo": str(output_path),
                "motor": "edge_tts", "tier": 1,
                "voz": voz_id, "custo": "GRATUITO",
                "qualidade": "★★★★☆",
                "ai_generated": True,
            }

        # ── Tier 2: gTTS ──────────────────────────────────────
        print("[DARK-TTS] Edge-TTS falhou → tentando gTTS...")
        if _engine_gtts(texto, output_path, lang=lang_gtts):
            return {
                "status": "OK", "arquivo": str(output_path),
                "motor": "gtts", "tier": 2,
                "voz": f"gTTS-{lang_gtts}", "custo": "GRATUITO",
                "qualidade": "★★★☆☆",
                "ai_generated": True,
            }

        # ── Tier 3: espeak-ng ─────────────────────────────────
        print("[DARK-TTS] gTTS falhou → tentando espeak-ng...")
        if _engine_espeak(texto, output_path):
            return {
                "status": "OK", "arquivo": str(output_path),
                "motor": "espeakng", "tier": 3,
                "voz": "pt-br (espeak)", "custo": "GRATUITO",
                "qualidade": "★★☆☆☆",
                "ai_generated": True,
            }

        # ── Tier 4: Piper ─────────────────────────────────────
        print("[DARK-TTS] espeak-ng falhou → tentando Piper...")
        if _engine_piper(texto, output_path):
            return {
                "status": "OK", "arquivo": str(output_path),
                "motor": "piper", "tier": 4,
                "voz": "pt_BR-faber-medium", "custo": "GRATUITO",
                "qualidade": "★★★☆☆",
                "ai_generated": True,
            }

        # ── Tier 5: Silêncio ──────────────────────────────────
        print("[DARK-TTS] ⚠️ Todos os engines falharam → gerando silêncio")
        _engine_silencio(output_path, texto)
        return {
            "status": "fallback_silencio", "arquivo": str(output_path),
            "motor": "silencio", "tier": 5,
            "voz": None, "custo": "GRATUITO",
            "qualidade": "☆☆☆☆☆",
            "aviso": "Todos os motores TTS falharam. Verifique conexão e dependências.",
            "ai_generated": True,
        }

    def narrar_roteiro(
        self,
        cenas: List[str],
        output_dir: str,
        prefixo: str = "cena",
        canal: Optional[str] = None,
        idioma: str = "pt-BR",
        genero: str = "padrao",
    ) -> List[Dict[str, Any]]:
        """
        Narra uma lista de cenas/textos.

        Args:
            cenas: Lista de textos para narrar.
            output_dir: Diretório de saída.
            prefixo: Prefixo dos arquivos (cena_01.mp3, cena_02.mp3...).
            canal, idioma, genero: Configuração de voz.

        Returns:
            Lista de resultados por cena.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        resultados = []

        for i, texto in enumerate(cenas, 1):
            if not texto or not texto.strip():
                resultados.append({"status": "skip", "cena": i, "msg": "Texto vazio"})
                continue

            output_path = output_dir / f"{prefixo}_{i:02d}.mp3"
            resultado = self.narrar(texto, str(output_path), canal=canal,
                                   idioma=idioma, genero=genero)
            resultado["cena"] = i
            resultados.append(resultado)

        ok = sum(1 for r in resultados if r["status"] == "OK")
        print(f"\n[DARK-TTS] Roteiro concluído: {ok}/{len(cenas)} cenas narradas")
        return resultados

    # ─────────────────────────────────────────────────────────
    # STATUS E DIAGNÓSTICO
    # ─────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Verifica engines disponíveis e retorna status completo."""
        engines = {}

        # Edge TTS
        try:
            import edge_tts
            engines["edge_tts"] = {
                "disponivel": True, "tipo": "cloud_gratuito",
                "vozes_ptbr": ["pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"],
                "qualidade": "★★★★☆", "custo": "GRATUITO",
                "nota": "Microsoft Neural — melhor qualidade gratuita",
            }
        except ImportError:
            engines["edge_tts"] = {
                "disponivel": False,
                "install": "pip install edge-tts --break-system-packages",
            }

        # gTTS
        try:
            from gtts import gTTS
            engines["gtts"] = {
                "disponivel": True, "tipo": "cloud_gratuito",
                "qualidade": "★★★☆☆", "custo": "GRATUITO",
            }
        except ImportError:
            engines["gtts"] = {
                "disponivel": False,
                "install": "pip install gtts --break-system-packages",
            }

        # espeak-ng
        try:
            import espeakng_loader
            lib_ok = Path(str(espeakng_loader.get_library_path())).exists()
            engines["espeakng"] = {
                "disponivel": lib_ok, "tipo": "offline",
                "qualidade": "★★☆☆☆", "custo": "GRATUITO",
            }
        except Exception:
            engines["espeakng"] = {"disponivel": False}

        # Piper
        piper_bin = shutil.which("piper")
        models_dir = Path(__file__).parent.parent / "assets" / "models" / "piper"
        modelos = list(models_dir.glob("*.onnx")) if models_dir.exists() else []
        engines["piper"] = {
            "disponivel": piper_bin is not None and len(modelos) > 0,
            "tipo": "local_offline",
            "modelos_instalados": [m.name for m in modelos],
            "qualidade": "★★★☆☆", "custo": "GRATUITO",
        }

        # Motor ativo
        motor_ativo = "silencio"
        for m in ["edge_tts", "gtts", "espeakng", "piper"]:
            if engines.get(m, {}).get("disponivel"):
                motor_ativo = m
                break

        self._status_cache = {
            "engines": engines,
            "motor_primario": motor_ativo,
            "vozes_ptbr": VOZES_CANAL,
            "elevenlabs_status": "BLOQUEADO (reconectar em connector settings)",
            "alternativa": "edge-tts ativo — qualidade equivalente a ElevenLabs tier gratuito",
            "custo_total": "R$0,00",
            "timestamp": datetime.now().isoformat(),
        }
        return self._status_cache

    def testar(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Testa narração PT-BR com cada engine disponível.
        Gera arquivo de áudio de teste.
        """
        texto_teste = (
            "DARK STUDIO AAA — sistema de narração autônomo ativo. "
            "ElevenLabs substituído por Edge TTS. Qualidade garantida."
        )
        output = output_path or str(self.output_dir / "teste_tts.mp3")
        resultado = self.narrar(texto_teste, output, canal="mente_de_aco")

        status = self.status()
        resultado["status_engines"] = status["engines"]
        resultado["motor_primario"] = status["motor_primario"]

        return resultado


# ═══════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CONVENIÊNCIA (retrocompatibilidade)
# ═══════════════════════════════════════════════════════════════════════

_tts_instance: Optional[DarkEdgeTTS] = None

def _get_instance() -> DarkEdgeTTS:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = DarkEdgeTTS()
    return _tts_instance


def gerar_audio(texto: str, output_path: str,
                canal: Optional[str] = None,
                idioma: str = "pt-BR",
                genero: str = "padrao") -> Dict[str, Any]:
    """Gera áudio com cascata automática. Função de conveniência."""
    return _get_instance().narrar(texto, output_path, canal=canal,
                                  idioma=idioma, genero=genero)


def narrar_cenas(cenas: List[str], output_dir: str,
                 canal: Optional[str] = None) -> List[Dict[str, Any]]:
    """Narra lista de cenas. Função de conveniência."""
    return _get_instance().narrar_roteiro(cenas, output_dir, canal=canal)


def status_tts() -> Dict[str, Any]:
    """Status dos engines TTS. Função de conveniência."""
    return _get_instance().status()


def voz_por_canal(canal: str) -> str:
    """Retorna a voz edge-tts recomendada para um canal."""
    canal_key = canal.lower().replace(" ", "_").replace("-", "_")
    return VOZES_CANAL.get(canal_key, VOZES_CANAL["padrao"])


# ═══════════════════════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════════════════════

CONTRACT = {
    "agente": "DARK_EDGE_TTS",
    "versao": "2.0.0",
    "descricao": "Motor TTS primário gratuito — substitui ElevenLabs",
    "status": "ATIVO",
    "custo": "R$0,00",
    "engines": ["edge_tts", "gtts", "espeakng", "piper", "silencio"],
    "idiomas": list(VOZES_EDGE_TTS.keys()),
    "canais_suportados": list(VOZES_CANAL.keys()),
    "entrada": {
        "texto": "str — script para narrar",
        "output_path": "str — caminho do arquivo MP3/WAV de saída",
        "canal": "str? — nome do canal DARK STUDIO",
        "idioma": "str? — código ISO ex: pt-BR",
        "genero": "str? — masculino|feminino|jovem|padrao",
        "voz": "str? — ID direto da voz edge-tts",
    },
    "saida": {
        "status": "OK|fallback_silencio|erro",
        "arquivo": "str — path do áudio gerado",
        "motor": "str — engine utilizado",
        "tier": "int — 1=edge_tts, 2=gtts, 3=espeak, 4=piper, 5=silencio",
        "voz": "str — voz utilizada",
        "custo": "GRATUITO",
        "ai_generated": True,
    },
    "elevenlabs": {
        "status": "BLOQUEADO",
        "motivo": "Falta de pagamento — reconectar em connector settings",
        "alternativa": "edge-tts (Tier 1) substitui com qualidade equivalente ao free tier",
    },
    "nota": "ElevenLabs bloqueado — sistema 100% gratuito ativo",
}


# ═══════════════════════════════════════════════════════════════════════
# DIAGNÓSTICO RÁPIDO
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    tts = DarkEdgeTTS()

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║   DARK EDGE TTS v2.0 — Motor de Narração Gratuito           ║")
    print("║   Substitui ElevenLabs (bloqueado) com cascata gratuita     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Status dos engines
    s = tts.status()
    print("ENGINES DISPONÍVEIS:")
    for eng, info in s["engines"].items():
        icon = "✅" if info.get("disponivel") else "❌"
        qual = info.get("qualidade", "")
        print(f"  {icon} {eng:<15} {qual}")

    print(f"\n  Motor primário: {s['motor_primario']}")
    print(f"  ElevenLabs: {s['elevenlabs_status']}")
    print(f"  Custo: {s['custo_total']}")

    # Testar narração
    if "--teste" in sys.argv or len(sys.argv) > 1:
        print("\nGERANDO TESTE DE ÁUDIO PT-BR...")
        texto = sys.argv[1] if len(sys.argv) > 1 and "--" not in sys.argv[1] else \
            "DARK STUDIO AAA. Sistema de narração ativo. ElevenLabs substituído com sucesso."
        resultado = tts.narrar(texto, "/tmp/dark_tts_teste.mp3", canal="mente_de_aco")
        print(f"\n  Status: {resultado['status']}")
        print(f"  Motor:  {resultado.get('motor', '?')}")
        print(f"  Voz:    {resultado.get('voz', '?')}")
        print(f"  Arquivo: {resultado.get('arquivo', '?')}")

    # Salvar contrato
    contract_path = Path(__file__).parent / "dark_edge_tts_contract.json"
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print(f"\n  Contrato: {contract_path}")
