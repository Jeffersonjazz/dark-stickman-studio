"""
DARK MULTILINGUAL AGENT — FASE 9 / EXPANSÃO INTERNACIONAL
Expande os 6 canais para múltiplos países via multilinguagem.

Estratégia baseada no vídeo YouTube: https://www.youtube.com/watch?v=2ORchxjfZRg
  - Adicionar faixas de áudio dublado por idioma (YouTube Studio > Languages)
  - Traduzir títulos, descrições e tags para cada idioma alvo
  - Gerar SRT (legendas) em cada idioma
  - Gerar plano de dublagem por idioma via tts_cascade()
  - Publicar com metadados multilíngues = +25% watch time internacional

Canais disponíveis:
  Esquina do Medo       → Horror/Mistério → EN, ES, DE, FR
  Projeto Secreto       → Mistério/Conspirações → EN, ES, DE, FR, IT
  Mente de Aço          → Motivação/Psicologia → EN, ES, DE, FR, IT, AR
  AquaZen Relax         → Relaxamento → EN, ES, FR, DE, JA, KO
  Intelligentia Nova    → Tecnologia/IA → EN, ES, DE, FR, IT, ZH
  Bastidores do Tempo   → História → EN, ES, DE, FR, IT, AR, PL

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DOS CANAIS E IDIOMAS ALVO
# ═══════════════════════════════════════════════════════

CANAIS_CONFIG: Dict[str, dict] = {
    "Esquina do Medo": {
        "id": "UCwuyz5ABF6ooQUn2HwG9xHQ",
        "nicho": "horror",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "DE", "FR"],
        "estilo_conteudo": "suspense, mistério, horror psicológico",
        "categoria_youtube": "22",  # People & Blogs / Entertainment
    },
    "Projeto Secreto": {
        "id": "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "nicho": "misterio",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "DE", "FR", "IT"],
        "estilo_conteudo": "conspirações, mistério, teoria",
        "categoria_youtube": "25",  # News & Politics
    },
    "Mente de Aço": {
        "id": "UCPRWgHoI85u-gmZmS9uVbqA",
        "nicho": "motivacional",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "ar"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "DE", "FR", "IT", "SA", "EG"],
        "estilo_conteudo": "motivação, psicologia, desenvolvimento pessoal",
        "categoria_youtube": "27",  # Education
    },
    "AquaZen Relax": {
        "id": "UC89YZqbZ02RTaT2FYepPHCQ",
        "nicho": "relaxamento",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "fr", "de", "ja", "ko"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "FR", "DE", "JP", "KR"],
        "estilo_conteudo": "relaxamento, meditação, natureza aquática",
        "categoria_youtube": "26",  # Howto & Style
    },
    "Intelligentia Nova": {
        "id": "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "nicho": "tecnologia",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "zh"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "DE", "FR", "IT", "CN", "TW"],
        "estilo_conteudo": "inteligência artificial, tecnologia, inovação",
        "categoria_youtube": "28",  # Science & Technology
    },
    "Bastidores do Tempo": {
        "id": "UCMinaADQVJ6QbbhOr_idVdA",
        "nicho": "historia",
        "idioma_original": "pt",
        "idiomas_alvo": ["en", "es", "de", "fr", "it", "ar", "pl"],
        "prioridade_paises": ["US", "GB", "MX", "ES", "DE", "FR", "IT", "PL", "SA"],
        "estilo_conteudo": "história, eventos históricos, documentário",
        "categoria_youtube": "27",  # Education
    },
}

# ═══════════════════════════════════════════════════════
# MAPA DE IDIOMAS
# ═══════════════════════════════════════════════════════

IDIOMAS: Dict[str, dict] = {
    "en": {
        "nome": "English",
        "code_youtube": "en",
        "code_tts": "en-US",
        "voz_edge": "en-US-AriaNeural",
        "voz_gtts": "en",
        "regiao": "Global",
    },
    "es": {
        "nome": "Español",
        "code_youtube": "es",
        "code_tts": "es-ES",
        "voz_edge": "es-ES-ElviraNeural",
        "voz_gtts": "es",
        "regiao": "América Latina + Espanha",
    },
    "de": {
        "nome": "Deutsch",
        "code_youtube": "de",
        "code_tts": "de-DE",
        "voz_edge": "de-DE-KatjaNeural",
        "voz_gtts": "de",
        "regiao": "Alemanha + Áustria + Suíça",
    },
    "fr": {
        "nome": "Français",
        "code_youtube": "fr",
        "code_tts": "fr-FR",
        "voz_edge": "fr-FR-DeniseNeural",
        "voz_gtts": "fr",
        "regiao": "França + Bélgica + Canadá",
    },
    "it": {
        "nome": "Italiano",
        "code_youtube": "it",
        "code_tts": "it-IT",
        "voz_edge": "it-IT-ElsaNeural",
        "voz_gtts": "it",
        "regiao": "Itália + Suíça",
    },
    "ar": {
        "nome": "العربية",
        "code_youtube": "ar",
        "code_tts": "ar-SA",
        "voz_edge": "ar-SA-ZariyahNeural",
        "voz_gtts": "ar",
        "regiao": "Oriente Médio + Norte da África",
    },
    "ja": {
        "nome": "日本語",
        "code_youtube": "ja",
        "code_tts": "ja-JP",
        "voz_edge": "ja-JP-NanamiNeural",
        "voz_gtts": "ja",
        "regiao": "Japão",
    },
    "ko": {
        "nome": "한국어",
        "code_youtube": "ko",
        "code_tts": "ko-KR",
        "voz_edge": "ko-KR-SunHiNeural",
        "voz_gtts": "ko",
        "regiao": "Coreia do Sul",
    },
    "zh": {
        "nome": "中文",
        "code_youtube": "zh-Hans",
        "code_tts": "zh-CN",
        "voz_edge": "zh-CN-XiaoxiaoNeural",
        "voz_gtts": "zh-cn",
        "regiao": "China + Taiwan + Hong Kong",
    },
    "pl": {
        "nome": "Polski",
        "code_youtube": "pl",
        "code_tts": "pl-PL",
        "voz_edge": "pl-PL-ZofiaNeural",
        "voz_gtts": "pl",
        "regiao": "Polônia",
    },
}


# ═══════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════

@dataclass
class MetadadosIdioma:
    """Metadados traduzidos para um idioma."""
    idioma: str
    titulo: str
    descricao: str
    tags: List[str]
    srt_path: Optional[str] = None
    audio_path: Optional[str] = None
    audio_status: str = "pendente"  # pendente | pronto | erro
    youtube_instrucoes: Optional[dict] = None


@dataclass
class PlanoExpansaoCanal:
    """Plano completo de expansão de um canal."""
    canal: str
    canal_id: str
    nicho: str
    video_id: str
    titulo_original: str
    descricao_original: str
    tags_originais: List[str]
    idiomas: List[MetadadosIdioma] = field(default_factory=list)
    gerado_em: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pendente"
    custo_estimado_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "canal": self.canal,
            "canal_id": self.canal_id,
            "nicho": self.nicho,
            "video_id": self.video_id,
            "titulo_original": self.titulo_original,
            "idiomas": [
                {
                    "idioma": m.idioma,
                    "titulo": m.titulo,
                    "descricao": m.descricao,
                    "tags": m.tags,
                    "audio_status": m.audio_status,
                    "youtube_instrucoes": m.youtube_instrucoes,
                }
                for m in self.idiomas
            ],
            "gerado_em": self.gerado_em,
            "status": self.status,
            "custo_estimado_usd": self.custo_estimado_usd,
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# ═══════════════════════════════════════════════════════
# CLASSE PRINCIPAL
# ═══════════════════════════════════════════════════════

class DarkMultilingualAgent:
    """
    Agente de expansão internacional do DARK STUDIO AAA.

    Estratégia:
      1. Traduz títulos/descrições/tags para cada idioma alvo do canal
      2. Gera plano de dublagem (tts_cascade ou vidIQ MCP)
      3. Gera arquivo SRT traduzido
      4. Produz instruções para YouTube Studio

    Não usa APIs pagas por padrão — usa deep-translator (gratuito).
    Para áudio dublado, usa cascata: Edge TTS → gTTS → Piper → vidIQ.
    """

    def __init__(self, output_dir: str = "outputs/multilingual"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ───────────────────────────────────────────────────
    # TRADUÇÃO VIA DEEP-TRANSLATOR
    # ───────────────────────────────────────────────────

    def _traduzir(self, texto: str, idioma_destino: str, idioma_origem: str = "pt") -> str:
        """Traduz texto usando deep-translator (GoogleTranslator, gratuito)."""
        if not texto or not texto.strip():
            return texto

        # Mapeia código de idioma para deep-translator
        CODIGO_MAP = {
            "zh": "zh-CN",
            "ar": "ar",
            "ja": "ja",
            "ko": "ko",
            "pl": "pl",
            "it": "it",
            "fr": "fr",
            "de": "de",
            "es": "es",
            "en": "en",
            "pt": "pt",
        }
        dest = CODIGO_MAP.get(idioma_destino, idioma_destino)
        orig = CODIGO_MAP.get(idioma_origem, idioma_origem)

        # Tier 1: GoogleTranslator (produção — requer acesso à internet)
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source=orig, target=dest)
            if len(texto) <= 4900:
                result = translator.translate(texto)
            else:
                partes = [texto[i:i+4900] for i in range(0, len(texto), 4900)]
                result = " ".join(translator.translate(p) for p in partes)
            if result and "[erro" not in str(result):
                return result
        except ImportError:
            pass
        except Exception:
            pass

        # Tier 2: MyMemoryTranslator (endpoint alternativo, sem API key)
        try:
            from deep_translator import MyMemoryTranslator
            MYMEMORY_LANG = {
                "pt": "pt-BR", "en": "en-US", "es": "es-ES",
                "de": "de-DE", "fr": "fr-FR", "it": "it-IT",
                "ar": "ar-SA", "ja": "ja-JP", "ko": "ko-KR",
                "zh-CN": "zh-CN", "pl": "pl-PL",
            }
            orig_mm = MYMEMORY_LANG.get(orig, orig)
            dest_mm = MYMEMORY_LANG.get(dest, dest)
            if len(texto) <= 490:
                result = MyMemoryTranslator(source=orig_mm, target=dest_mm).translate(texto)
            else:
                partes = [texto[i:i+490] for i in range(0, len(texto), 490)]
                result = " ".join(
                    MyMemoryTranslator(source=orig_mm, target=dest_mm).translate(p)
                    for p in partes
                )
            if result:
                return result
        except Exception:
            pass

        # Tier 3: Marcação de pendência (tradução offline não disponível neste ambiente)
        # Em produção (máquina do usuário), Tier 1 e 2 funcionam normalmente.
        return f"[TRADUÇÃO_PENDENTE_{idioma_destino.upper()}] {texto}"

    def traduzir_titulo(self, titulo: str, idioma: str, nicho: str = "") -> str:
        """Traduz título com contexto de nicho."""
        traduzido = self._traduzir(titulo, idioma)
        return traduzido

    def traduzir_descricao(self, descricao: str, idioma: str) -> str:
        """Traduz descrição completa."""
        # Remove links (preservar) e traduz o resto
        import re

        # Separa linhas com links das outras
        linhas = descricao.split("\n")
        linhas_traduzidas = []
        for linha in linhas:
            if re.search(r"https?://", linha) or linha.strip().startswith("#"):
                linhas_traduzidas.append(linha)  # preserva links e hashtags
            elif linha.strip():
                linhas_traduzidas.append(self._traduzir(linha, idioma))
            else:
                linhas_traduzidas.append(linha)

        return "\n".join(linhas_traduzidas)

    def traduzir_tags(self, tags: List[str], idioma: str) -> List[str]:
        """Traduz e adapta tags para o idioma."""
        tags_traduzidas = []
        for tag in tags[:30]:  # YouTube: máx 30 tags
            tag_limpa = tag.strip().lstrip("#")
            traduzida = self._traduzir(tag_limpa, idioma)
            if traduzida and len(traduzida) < 50:
                tags_traduzidas.append(traduzida)
        return tags_traduzidas

    # ───────────────────────────────────────────────────
    # GERAÇÃO DE LEGENDAS SRT TRADUZIDAS
    # ───────────────────────────────────────────────────

    def gerar_srt_traduzido(
        self,
        srt_original_path: str,
        idioma_destino: str,
        output_path: Optional[str] = None,
    ) -> dict:
        """Traduz arquivo SRT para idioma destino."""
        srt_path = Path(srt_original_path)
        if not srt_path.exists():
            return {"status": "erro", "msg": f"SRT não encontrado: {srt_original_path}"}

        conteudo = srt_path.read_text(encoding="utf-8")

        # Parse SRT: separa blocos (número, timecode, texto)
        import re
        blocos = re.split(r"\n\n+", conteudo.strip())
        blocos_traduzidos = []

        for bloco in blocos:
            linhas = bloco.strip().split("\n")
            if len(linhas) < 3:
                blocos_traduzidos.append(bloco)
                continue

            num = linhas[0]
            timecode = linhas[1]
            texto = "\n".join(linhas[2:])
            texto_traduzido = self._traduzir(texto, idioma_destino)

            blocos_traduzidos.append(f"{num}\n{timecode}\n{texto_traduzido}")

        srt_traduzido = "\n\n".join(blocos_traduzidos)

        if not output_path:
            output_path = str(self.output_dir / f"{srt_path.stem}_{idioma_destino}.srt")

        Path(output_path).write_text(srt_traduzido, encoding="utf-8")
        return {"status": "OK", "arquivo": output_path, "idioma": idioma_destino}

    # ───────────────────────────────────────────────────
    # PLANO DE DUBLAGEM (TTS CASCADE)
    # ───────────────────────────────────────────────────

    def planejar_dublagem(
        self,
        script_pt: str,
        idioma: str,
        nome_base: str,
    ) -> dict:
        """
        Gera plano de dublagem para um idioma.
        Usa tts_cascade do DarkAudioStudio quando disponível,
        ou retorna instruções para sessão interativa.
        """
        # Traduz script
        script_traduzido = self._traduzir(script_pt, idioma)

        cfg_idioma = IDIOMAS.get(idioma, {})
        voz_edge = cfg_idioma.get("voz_edge", "en-US-AriaNeural")
        code_tts = cfg_idioma.get("code_tts", idioma)

        output_audio = str(self.output_dir / f"{nome_base}_{idioma}_narracao.mp3")

        # Tenta TTS local
        try:
            from core.dark_audio_studio import DarkAudioStudio
            studio = DarkAudioStudio()
            resultado = studio.tts_cascade(
                texto=script_traduzido,
                output_path=output_audio,
                voz_edge=voz_edge,
            )
            if resultado.get("status") == "OK":
                return {
                    "status": "OK",
                    "arquivo": output_audio,
                    "idioma": idioma,
                    "script_traduzido": script_traduzido,
                    "motor": resultado.get("motor", "tts_cascade"),
                    "custo": "GRATUITO",
                }
            # Se retornou plano para sessão interativa (vidIQ)
            if resultado.get("status") == "pendente_mcp":
                return {
                    "status": "pendente_sessao_interativa",
                    "idioma": idioma,
                    "script_traduzido": script_traduzido,
                    "instrucao": resultado.get("instrucao"),
                    "ferramenta_mcp": resultado.get("ferramenta"),
                    "params_mcp": {
                        "script": script_traduzido,
                        "voice": voz_edge,
                        "title": nome_base,
                    },
                }
        except ImportError:
            pass
        except Exception as e:
            pass

        # Fallback: plano de instrução manual
        return {
            "status": "pendente_sessao_interativa",
            "idioma": idioma,
            "script_traduzido": script_traduzido,
            "instrucao": (
                f"Gerar dublagem em {cfg_idioma.get('nome', idioma)} via vidIQ "
                f"ou ElevenLabs em sessão interativa."
            ),
            "ferramenta_mcp": "mcp__vidIQ__vidiq_voiceover_generate",
            "params_mcp": {
                "script": script_traduzido,
                "voice": voz_edge,
                "title": f"{nome_base}_{idioma}",
            },
            "alternativa_elevenlabs": {
                "ferramenta": "mcp__ElevenLabs__text_to_speech",
                "voice_id": "auto",
                "text": script_traduzido,
                "language": code_tts,
            },
        }

    # ───────────────────────────────────────────────────
    # INSTRUÇÕES PARA YOUTUBE STUDIO
    # ───────────────────────────────────────────────────

    def gerar_instrucoes_youtube_studio(
        self,
        video_id: str,
        canal: str,
        titulo_idioma: str,
        descricao_idioma: str,
        tags_idioma: List[str],
        idioma: str,
        audio_path: Optional[str] = None,
        srt_path: Optional[str] = None,
    ) -> dict:
        """Gera guia passo-a-passo para adicionar idioma no YouTube Studio."""
        cfg = IDIOMAS.get(idioma, {})
        nome_idioma = cfg.get("nome", idioma.upper())
        code_yt = cfg.get("code_youtube", idioma)

        url_studio = f"https://studio.youtube.com/video/{video_id}/translations"

        passos = [
            f"1. Abrir YouTube Studio: {url_studio}",
            f"2. Clicar em 'Adicionar idioma' → selecionar '{nome_idioma}'",
            f"3. Título ({nome_idioma}): {titulo_idioma[:100]}",
            f"4. Descrição ({nome_idioma}): [colar texto abaixo]",
            f"5. Tags ({nome_idioma}): {', '.join(tags_idioma[:10])}",
        ]

        if audio_path and Path(audio_path).exists():
            passos.append(f"6. Faixa de áudio: Upload de '{audio_path}'")
            passos.append(f"   → YouTube Studio > Editor > Áudio > Adicionar faixa de idioma")
        else:
            passos.append(f"6. Faixa de áudio: Gerar dublagem em '{nome_idioma}' (ver plano de dublagem)")

        if srt_path and Path(srt_path).exists():
            passos.append(f"7. Legendas: Upload de '{srt_path}' em '{nome_idioma}'")
        else:
            passos.append(f"7. Legendas: Gerar SRT em '{nome_idioma}' via tts_cascade + WhisperX")

        passos.append(f"8. Salvar e publicar")

        return {
            "canal": canal,
            "video_id": video_id,
            "idioma": idioma,
            "nome_idioma": nome_idioma,
            "code_youtube": code_yt,
            "url_studio": url_studio,
            "titulo": titulo_idioma,
            "descricao": descricao_idioma,
            "tags": tags_idioma,
            "passos": passos,
            "audio_pronto": audio_path and Path(audio_path).exists(),
            "srt_pronto": srt_path and Path(srt_path).exists(),
        }

    # ───────────────────────────────────────────────────
    # EXPANDIR VÍDEO PARA MÚLTIPLOS IDIOMAS
    # ───────────────────────────────────────────────────

    def expandir_video(
        self,
        canal: str,
        video_id: str,
        titulo: str,
        descricao: str,
        tags: List[str],
        script_narracao: Optional[str] = None,
        srt_original_path: Optional[str] = None,
        idiomas_override: Optional[List[str]] = None,
    ) -> PlanoExpansaoCanal:
        """
        Expande um vídeo para todos os idiomas alvo do canal.

        Args:
            canal: Nome do canal (chave em CANAIS_CONFIG)
            video_id: ID do vídeo no YouTube
            titulo: Título original em português
            descricao: Descrição original em português
            tags: Tags originais
            script_narracao: Script de narração para dublagem (opcional)
            srt_original_path: Caminho para o SRT original (opcional)
            idiomas_override: Substituir idiomas padrão do canal (opcional)

        Returns:
            PlanoExpansaoCanal com todos os metadados traduzidos e planos de dublagem
        """
        cfg_canal = CANAIS_CONFIG.get(canal, {})
        canal_id = cfg_canal.get("id", "")
        nicho = cfg_canal.get("nicho", "geral")
        idiomas_alvo = idiomas_override or cfg_canal.get("idiomas_alvo", ["en", "es"])

        plano = PlanoExpansaoCanal(
            canal=canal,
            canal_id=canal_id,
            nicho=nicho,
            video_id=video_id,
            titulo_original=titulo,
            descricao_original=descricao,
            tags_originais=tags,
        )

        print(f"\n[MULTILINGUAL] Expandindo '{titulo[:50]}...' → {len(idiomas_alvo)} idiomas")

        for idioma in idiomas_alvo:
            cfg_idioma = IDIOMAS.get(idioma, {})
            nome_idioma = cfg_idioma.get("nome", idioma.upper())
            print(f"  → {nome_idioma} ({idioma})...")

            # 1. Traduzir metadados
            titulo_trad = self.traduzir_titulo(titulo, idioma, nicho)
            descricao_trad = self.traduzir_descricao(descricao, idioma)
            tags_trad = self.traduzir_tags(tags, idioma)

            # 2. Plano de dublagem
            audio_path = None
            audio_status = "sem_script"
            dublagem = None
            if script_narracao:
                nome_base = f"{canal.replace(' ', '_')}_{video_id}"
                dublagem = self.planejar_dublagem(script_narracao, idioma, nome_base)
                audio_path = dublagem.get("arquivo")
                audio_status = dublagem.get("status", "pendente")

            # 3. SRT traduzido
            srt_trad_path = None
            if srt_original_path:
                srt_nome = f"{canal.replace(' ', '_')}_{video_id}_{idioma}.srt"
                srt_trad_path = str(self.output_dir / srt_nome)
                self.gerar_srt_traduzido(srt_original_path, idioma, srt_trad_path)

            # 4. Instruções YouTube Studio
            instrucoes_yt = self.gerar_instrucoes_youtube_studio(
                video_id=video_id,
                canal=canal,
                titulo_idioma=titulo_trad,
                descricao_idioma=descricao_trad,
                tags_idioma=tags_trad,
                idioma=idioma,
                audio_path=audio_path,
                srt_path=srt_trad_path,
            )

            meta = MetadadosIdioma(
                idioma=idioma,
                titulo=titulo_trad,
                descricao=descricao_trad,
                tags=tags_trad,
                srt_path=srt_trad_path,
                audio_path=audio_path,
                audio_status=audio_status,
                youtube_instrucoes=instrucoes_yt,
            )
            plano.idiomas.append(meta)

        plano.status = "pronto"
        plano.custo_estimado_usd = 0.0  # deep-translator é gratuito

        return plano

    # ───────────────────────────────────────────────────
    # EXPANDIR TODOS OS CANAIS
    # ───────────────────────────────────────────────────

    def expandir_todos_canais(
        self,
        videos_por_canal: Dict[str, List[dict]],
    ) -> Dict[str, List[PlanoExpansaoCanal]]:
        """
        Expande múltiplos vídeos de múltiplos canais.

        Args:
            videos_por_canal: {
                "Nome Canal": [
                    {"video_id": "...", "titulo": "...", "descricao": "...", "tags": [...]}
                ]
            }

        Returns:
            {canal_nome: [PlanoExpansaoCanal, ...]}
        """
        resultados = {}

        for canal, videos in videos_por_canal.items():
            if canal not in CANAIS_CONFIG:
                print(f"  ⚠ Canal '{canal}' não configurado — pulando")
                continue

            planos = []
            print(f"\n[MULTILINGUAL] Canal: {canal} → {len(videos)} vídeo(s)")

            for video in videos:
                plano = self.expandir_video(
                    canal=canal,
                    video_id=video["video_id"],
                    titulo=video.get("titulo", video.get("title", "")),
                    descricao=video.get("descricao", video.get("description", "")),
                    tags=video.get("tags", []),
                    script_narracao=video.get("script"),
                    srt_original_path=video.get("srt_path"),
                )
                planos.append(plano)

            resultados[canal] = planos

        return resultados

    # ───────────────────────────────────────────────────
    # EXPORTAR PLANO COMO JSON
    # ───────────────────────────────────────────────────

    def exportar_plano_json(
        self,
        plano: PlanoExpansaoCanal,
        output_path: Optional[str] = None,
    ) -> str:
        """Salva plano de expansão como JSON."""
        if not output_path:
            nome = f"plano_{plano.canal.replace(' ', '_')}_{plano.video_id}.json"
            output_path = str(self.output_dir / nome)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(plano.to_dict(), f, ensure_ascii=False, indent=2)

        return output_path

    def exportar_guia_youtube_studio(
        self,
        plano: PlanoExpansaoCanal,
        output_path: Optional[str] = None,
    ) -> str:
        """Exporta guia de ações para YouTube Studio em Markdown."""
        if not output_path:
            nome = f"guia_youtube_{plano.canal.replace(' ', '_')}_{plano.video_id}.md"
            output_path = str(self.output_dir / nome)

        linhas = [
            f"# Guia YouTube Studio — {plano.canal}",
            f"**Vídeo ID:** {plano.video_id}",
            f"**Título original:** {plano.titulo_original}",
            f"**URL:** https://studio.youtube.com/video/{plano.video_id}/translations",
            f"**Gerado em:** {plano.gerado_em}",
            "",
            "---",
            "",
            "## Como adicionar idiomas no YouTube Studio",
            "",
            "1. Acesse YouTube Studio > Vídeos > selecione o vídeo",
            "2. Clique em **Legendas** (menu lateral)",
            "3. Clique em **Adicionar idioma**",
            "4. Adicione título e descrição traduzidos",
            "5. Para dublagem: **Editor** > **Áudio** > **Adicionar faixa de idioma**",
            "",
            "---",
            "",
        ]

        for meta in plano.idiomas:
            cfg = IDIOMAS.get(meta.idioma, {})
            nome_idioma = cfg.get("nome", meta.idioma.upper())
            linhas.extend([
                f"## {nome_idioma} (`{meta.idioma}`)",
                "",
                f"**Título:** {meta.titulo}",
                "",
                "**Descrição:**",
                "```",
                meta.descricao[:800] + ("..." if len(meta.descricao) > 800 else ""),
                "```",
                "",
                f"**Tags:** {', '.join(meta.tags[:10])}",
                "",
                f"**Áudio dublado:** {'✅ ' + (meta.audio_path or '') if meta.audio_status == 'OK' else '⏳ Pendente — ver plano de dublagem'}",
                f"**Legendas SRT:** {'✅ ' + (meta.srt_path or '') if meta.srt_path else '⏳ Pendente'}",
                "",
            ])

            if meta.youtube_instrucoes:
                linhas.append("**Passos no YouTube Studio:**")
                for passo in meta.youtube_instrucoes.get("passos", []):
                    linhas.append(f"- {passo}")
                linhas.append("")

            linhas.append("---")
            linhas.append("")

        Path(output_path).write_text("\n".join(linhas), encoding="utf-8")
        return output_path

    # ───────────────────────────────────────────────────
    # STATUS E DIAGNÓSTICO
    # ───────────────────────────────────────────────────

    def status(self) -> dict:
        """Retorna status do agente e capacidades."""
        tts_disponivel = False
        tradutor_disponivel = False

        try:
            from deep_translator import GoogleTranslator
            tradutor_disponivel = True
        except ImportError:
            pass

        try:
            from core.dark_audio_studio import DarkAudioStudio
            tts_disponivel = True
        except ImportError:
            pass

        total_idiomas = sum(
            len(c.get("idiomas_alvo", [])) for c in CANAIS_CONFIG.values()
        )

        return {
            "agente": "MULTILINGUAL_AGENT",
            "versao": "1.0.0",
            "canais_configurados": len(CANAIS_CONFIG),
            "total_combinacoes_idioma": total_idiomas,
            "tradutor_disponivel": tradutor_disponivel,
            "tts_disponivel": tts_disponivel,
            "custo_traducao": "GRATUITO (deep-translator)",
            "custo_tts": "GRATUITO (Edge TTS / gTTS / Piper)",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# ═══════════════════════════════════════════════════════
# WRAPPERS FUNCIONAIS
# ═══════════════════════════════════════════════════════

def expandir_canal(
    canal: str,
    video_id: str,
    titulo: str,
    descricao: str,
    tags: Optional[List[str]] = None,
    script: Optional[str] = None,
    srt_path: Optional[str] = None,
    output_dir: str = "outputs/multilingual",
) -> dict:
    """Wrapper funcional para expandir um vídeo."""
    agente = DarkMultilingualAgent(output_dir=output_dir)
    plano = agente.expandir_video(
        canal=canal,
        video_id=video_id,
        titulo=titulo,
        descricao=descricao,
        tags=tags or [],
        script_narracao=script,
        srt_original_path=srt_path,
    )
    json_path = agente.exportar_plano_json(plano)
    guia_path = agente.exportar_guia_youtube_studio(plano)

    resultado = plano.to_dict()
    resultado["json_plano"] = json_path
    resultado["guia_youtube"] = guia_path
    return resultado


def check_multilingual_agent() -> dict:
    """Verifica status do MULTILINGUAL_AGENT."""
    agente = DarkMultilingualAgent()
    return agente.status()


# ═══════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════

CONTRACT = {
    "agente": "MULTILINGUAL_AGENT",
    "versao": "1.0.0",
    "descricao": "Expansão internacional via tradução e dublagem multilíngue",
    "entrada": {
        "canal": "str — nome do canal (chave em CANAIS_CONFIG)",
        "video_id": "str — ID YouTube do vídeo",
        "titulo": "str — título em português",
        "descricao": "str — descrição em português",
        "tags": "list[str]? — tags em português",
        "script": "str? — script de narração para dublagem",
        "srt_path": "str? — caminho do SRT original",
        "output_dir": "str? — diretório de saída",
    },
    "saida": {
        "status": "pronto|erro",
        "canal": "str",
        "video_id": "str",
        "idiomas": "list[dict] — metadados por idioma",
        "json_plano": "str — path do JSON de plano",
        "guia_youtube": "str — path do guia Markdown",
        "custo_estimado_usd": "float",
        "ai_generated": True,
        "ai_disclosure": "str",
    },
    "canais_suportados": list(CANAIS_CONFIG.keys()),
    "idiomas_suportados": list(IDIOMAS.keys()),
    "dependencias": ["deep-translator", "core.dark_audio_studio"],
    "custo": "GRATUITO (deep-translator + Edge TTS / gTTS)",
}


# ═══════════════════════════════════════════════════════
# MAIN — TESTE E DEMONSTRAÇÃO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK MULTILINGUAL AGENT — EXPANSÃO INTERNACIONAL   ║")
    print("║   Fase 9 — DARK CREATIVE LAB                         ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    agente = DarkMultilingualAgent()
    st = agente.status()

    print(f"Canais configurados: {st['canais_configurados']}")
    print(f"Total idioma-canal: {st['total_combinacoes_idioma']}")
    print(f"Tradutor: {'✅' if st['tradutor_disponivel'] else '❌ pip install deep-translator'}")
    print(f"TTS: {'✅' if st['tts_disponivel'] else '⚠ DarkAudioStudio não acessível'}")

    print("\nCONFIGURAÇÃO DOS CANAIS:")
    for nome, cfg in CANAIS_CONFIG.items():
        idiomas_str = ", ".join(cfg["idiomas_alvo"])
        print(f"  {nome:25} → {idiomas_str}")

    # Teste com vídeo exemplo
    print("\n--- TESTE: Expandindo vídeo exemplo para Mente de Aço ---\n")
    plano = agente.expandir_video(
        canal="Mente de Aço",
        video_id="HXDngAAmUbo",
        titulo="A Mente Mais Poderosa do Mundo — Disciplina Absoluta",
        descricao=(
            "Descubra os segredos da disciplina mental que separa os campeões "
            "dos mediocres. Neste episódio, exploramos as técnicas usadas pelos "
            "atletas de elite para desenvolver uma mente de aço.\n\n"
            "#mentedeaco #disciplina #motivacao #psicologia"
        ),
        tags=["mente de aço", "disciplina", "motivação", "psicologia", "mentalidade"],
        script_narracao=(
            "A disciplina não é um dom. É uma escolha feita todos os dias, "
            "em cada momento de fraqueza. Os campeões não sentem menos dor. "
            "Eles simplesmente decidiram que a dor não os define."
        ),
    )

    print(f"\nStatus: {plano.status}")
    print(f"Idiomas gerados: {len(plano.idiomas)}")
    for m in plano.idiomas:
        cfg = IDIOMAS.get(m.idioma, {})
        print(f"  {cfg.get('nome', m.idioma):15} — Título: {m.titulo[:60]}")

    # Exportar guia
    guia = agente.exportar_guia_youtube_studio(plano)
    print(f"\n✅ Guia YouTube Studio: {guia}")

    json_plano = agente.exportar_plano_json(plano)
    print(f"✅ Plano JSON: {json_plano}")

    # Salvar contrato
    Path("core").mkdir(exist_ok=True)
    with open("core/dark_multilingual_agent_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Contrato: core/dark_multilingual_agent_contract.json")
