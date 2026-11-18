"""
DARK PRODUCTION PIPELINE — PIPELINE INTEGRADO COM EXPANSÃO MULTILÍNGUE
Orquestra a produção completa: Short → Publicação → Expansão Internacional.

Fluxo:
  1. Recebe roteiro + nicho + canal
  2. Gera narração (TTS cascade)
  3. Gera vídeo (cascade: vidIQ → Higgsfield → FFmpeg)
  4. Aplica color grading (Cinema Editor)
  5. Monta Short final
  6. Gera metadados multilíngues (MULTILINGUAL_AGENT)
  7. Publica no YouTube (vidIQ MCP — sessão interativa)
  8. Retorna plano de dublagem por idioma

Usado pelos triggers dos 6 canais para produção automática de Shorts
com expansão internacional via faixas de áudio e legendas traduzidas.

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.dark_multilingual_agent import DarkMultilingualAgent, CANAIS_CONFIG


# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO DOS CANAIS (integração pipeline + multilíngue)
# ═══════════════════════════════════════════════════════

PIPELINE_CONFIG = {
    "Esquina do Medo": {
        "canal_id": "UCwuyz5ABF6ooQUn2HwG9xHQ",
        "nicho": "horror",
        "color_preset": "dark_thriller",
        "voz_padrao": "pt-BR-FranciscaNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#EsquinaDoMedo", "#Horror", "#Misterio", "#HorrorBrasileiro"],
        "playlist_id": None,
    },
    "Projeto Secreto": {
        "canal_id": "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "nicho": "misterio",
        "color_preset": "dark_thriller",
        "voz_padrao": "pt-BR-FranciscaNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#ProjetoSecreto", "#Misterio", "#Conspiracao", "#Verdade"],
        "playlist_id": None,
    },
    "Mente de Aço": {
        "canal_id": "UCPRWgHoI85u-gmZmS9uVbqA",
        "nicho": "motivacional",
        "color_preset": "sci_tech",
        "voz_padrao": "pt-BR-AntonioNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#MenteDeAço", "#Disciplina", "#Motivacao", "#Psicologia"],
        "playlist_id": None,
    },
    "AquaZen Relax": {
        "canal_id": "UC89YZqbZ02RTaT2FYepPHCQ",
        "nicho": "relaxamento",
        "color_preset": "relaxation",
        "voz_padrao": "pt-BR-FranciscaNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#AquaZen", "#Relaxamento", "#Meditacao", "#Sons"],
        "playlist_id": None,
    },
    "Intelligentia Nova": {
        "canal_id": "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "nicho": "tecnologia",
        "color_preset": "sci_tech",
        "voz_padrao": "pt-BR-AntonioNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#IntellectiaNova", "#InteligenciaArtificial", "#Tecnologia", "#IA"],
        "playlist_id": None,
    },
    "Bastidores do Tempo": {
        "canal_id": "UCMinaADQVJ6QbbhOr_idVdA",
        "nicho": "historia",
        "color_preset": "history",
        "voz_padrao": "pt-BR-FranciscaNeural",
        "duracao_target_s": 55,
        "hashtags_pt": ["#BastidoresDoTempo", "#Historia", "#Documentario", "#Passado"],
        "playlist_id": None,
    },
}


@dataclass
class ResultadoPipeline:
    """Resultado completo do pipeline de produção."""
    canal: str
    titulo: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    video_id_youtube: Optional[str] = None
    metadados_pt: Optional[dict] = None
    plano_multilingual: Optional[dict] = None
    status: str = "pendente"
    etapas: List[dict] = field(default_factory=list)
    gerado_em: str = field(default_factory=lambda: datetime.now().isoformat())
    custo_total_usd: float = 0.0
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"

    def to_dict(self) -> dict:
        return {
            "canal": self.canal,
            "titulo": self.titulo,
            "video_path": self.video_path,
            "audio_path": self.audio_path,
            "thumbnail_path": self.thumbnail_path,
            "video_id_youtube": self.video_id_youtube,
            "metadados_pt": self.metadados_pt,
            "plano_multilingual": self.plano_multilingual,
            "status": self.status,
            "etapas": self.etapas,
            "gerado_em": self.gerado_em,
            "custo_total_usd": self.custo_total_usd,
            "ai_generated": self.ai_generated,
            "ai_disclosure": self.ai_disclosure,
        }


class DarkProductionPipeline:
    """
    Pipeline de produção integrado com expansão multilíngue.

    Uso típico (nos triggers dos canais):
        pipeline = DarkProductionPipeline()
        resultado = pipeline.produzir_e_expandir(
            canal="Mente de Aço",
            titulo="A Disciplina que Muda Vidas",
            script="Narração aqui...",
            descricao="Descrição do vídeo...",
            tags=["disciplina", "motivação"],
        )
    """

    def __init__(self, output_dir: str = "outputs/pipeline"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ml_agente = DarkMultilingualAgent(output_dir=str(self.output_dir / "multilingual"))

    def _log_etapa(self, resultado: ResultadoPipeline, etapa: str, status: str, detalhe: dict = None):
        """Registra etapa do pipeline."""
        entrada = {
            "etapa": etapa,
            "status": status,
            "ts": datetime.now().isoformat(),
        }
        if detalhe:
            entrada.update(detalhe)
        resultado.etapas.append(entrada)

    def gerar_descricao_completa(
        self,
        canal: str,
        titulo: str,
        descricao_base: str,
        tags: List[str],
    ) -> str:
        """Gera descrição completa com hashtags e identidade do canal."""
        cfg = PIPELINE_CONFIG.get(canal, {})
        hashtags = cfg.get("hashtags_pt", [])

        hashtags_str = " ".join(hashtags)
        tags_str = " ".join(f"#{t.replace(' ', '')}" for t in tags[:5])

        return (
            f"{descricao_base}\n\n"
            f"🎬 DARK STUDIO AAA — Conteúdo produzido com IA\n\n"
            f"{hashtags_str} {tags_str}\n\n"
            f"⚡ Ative o sininho para não perder nenhum vídeo!\n"
            f"🌍 Legendas disponíveis em vários idiomas."
        )

    def expandir_internacionalmente(
        self,
        canal: str,
        video_id: str,
        titulo: str,
        descricao: str,
        tags: List[str],
        script: Optional[str] = None,
        srt_path: Optional[str] = None,
    ) -> dict:
        """
        Expande o vídeo publicado para múltiplos idiomas.

        Returns:
            dict com plano de expansão por idioma (títulos, descrições, instruções YT Studio)
        """
        plano = self._ml_agente.expandir_video(
            canal=canal,
            video_id=video_id,
            titulo=titulo,
            descricao=descricao,
            tags=tags,
            script_narracao=script,
            srt_original_path=srt_path,
        )

        # Exportar guia para o usuário
        guia_path = self._ml_agente.exportar_guia_youtube_studio(plano)
        json_path = self._ml_agente.exportar_plano_json(plano)

        resultado = plano.to_dict()
        resultado["guia_youtube_studio"] = guia_path
        resultado["json_plano"] = json_path
        return resultado

    def produzir_e_expandir(
        self,
        canal: str,
        titulo: str,
        script: str,
        descricao: str,
        tags: List[str],
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        video_id_youtube: Optional[str] = None,
        gerar_audio: bool = True,
        gerar_video: bool = False,  # Requer backend ativo (vidIQ/Higgsfield)
    ) -> ResultadoPipeline:
        """
        Pipeline completo: produção + expansão multilíngue.

        Para triggers de produção automática, passe os assets já gerados
        (video_path, audio_path) e o video_id após publicação.

        Args:
            canal: Nome do canal
            titulo: Título em português
            script: Script de narração em português
            descricao: Descrição em português
            tags: Tags em português
            video_path: Path do vídeo já produzido (opcional)
            audio_path: Path do áudio já gerado (opcional)
            thumbnail_path: Path da thumbnail (opcional)
            video_id_youtube: ID do vídeo após publicação (para expansão)
            gerar_audio: Se True, tenta gerar áudio via TTS cascade
            gerar_video: Se True, tenta gerar vídeo (requer MCP ativo)

        Returns:
            ResultadoPipeline com todos os assets e plano multilíngue
        """
        cfg = PIPELINE_CONFIG.get(canal, PIPELINE_CONFIG.get("Mente de Aço"))
        resultado = ResultadoPipeline(canal=canal, titulo=titulo)

        print(f"\n[PIPELINE] Canal: {canal}")
        print(f"[PIPELINE] Título: {titulo[:60]}")

        # ── Etapa 1: Áudio (TTS) ─────────────────────────────────────────
        if gerar_audio and not audio_path:
            self._log_etapa(resultado, "TTS", "iniciando")
            try:
                from core.dark_audio_studio import DarkAudioStudio
                studio = DarkAudioStudio()
                nome_base = titulo.replace(" ", "_")[:30]
                audio_out = str(self.output_dir / f"{nome_base}_narracao.mp3")
                tts_result = studio.tts_cascade(
                    texto=script,
                    output_path=audio_out,
                    voz_edge=cfg.get("voz_padrao", "pt-BR-FranciscaNeural"),
                )
                if tts_result.get("status") == "OK":
                    audio_path = audio_out
                    resultado.audio_path = audio_path
                    self._log_etapa(resultado, "TTS", "ok", {"motor": tts_result.get("motor")})
                    print(f"  ✅ Áudio: {audio_path}")
                else:
                    self._log_etapa(resultado, "TTS", "pendente_mcp", tts_result)
                    resultado.audio_path = None
                    print(f"  ⏳ TTS pendente — {tts_result.get('instrucao', 'usar vidIQ em sessão interativa')}")
            except Exception as e:
                self._log_etapa(resultado, "TTS", "erro", {"erro": str(e)})
                print(f"  ⚠ TTS erro: {e}")

        elif audio_path:
            resultado.audio_path = audio_path
            self._log_etapa(resultado, "TTS", "fornecido_externamente")
            print(f"  ✅ Áudio fornecido: {audio_path}")

        # ── Etapa 2: Vídeo ───────────────────────────────────────────────
        if video_path:
            resultado.video_path = video_path
            self._log_etapa(resultado, "VIDEO", "fornecido_externamente")
            print(f"  ✅ Vídeo fornecido: {video_path}")
        elif gerar_video:
            self._log_etapa(resultado, "VIDEO", "pendente_mcp", {
                "instrucao": "Gerar via vidIQ/Higgsfield em sessão interativa",
                "nicho": cfg.get("nicho"),
                "preset": cfg.get("color_preset"),
            })
            print(f"  ⏳ Vídeo: requer MCP em sessão interativa")
        else:
            self._log_etapa(resultado, "VIDEO", "pulado")

        # ── Etapa 3: Metadados em português ──────────────────────────────
        descricao_completa = self.gerar_descricao_completa(canal, titulo, descricao, tags)
        resultado.metadados_pt = {
            "titulo": titulo,
            "descricao": descricao_completa,
            "tags": tags,
            "canal_id": cfg.get("canal_id"),
            "nicho": cfg.get("nicho"),
        }
        self._log_etapa(resultado, "METADADOS_PT", "ok")
        print(f"  ✅ Metadados PT gerados")

        # ── Etapa 4: Expansão multilíngue ────────────────────────────────
        if video_id_youtube:
            self._log_etapa(resultado, "MULTILINGUAL", "iniciando")
            print(f"  → Expandindo para múltiplos idiomas...")
            try:
                plano_ml = self.expandir_internacionalmente(
                    canal=canal,
                    video_id=video_id_youtube,
                    titulo=titulo,
                    descricao=descricao_completa,
                    tags=tags,
                    script=script,
                )
                resultado.plano_multilingual = {
                    "total_idiomas": len(plano_ml.get("idiomas", [])),
                    "guia_youtube_studio": plano_ml.get("guia_youtube_studio"),
                    "json_plano": plano_ml.get("json_plano"),
                    "custo": "GRATUITO (deep-translator)",
                    "idiomas": [
                        {
                            "idioma": m["idioma"],
                            "titulo": m["titulo"][:80],
                            "audio_status": m.get("audio_status", "pendente"),
                        }
                        for m in plano_ml.get("idiomas", [])
                    ],
                }
                self._log_etapa(resultado, "MULTILINGUAL", "ok", {
                    "idiomas": resultado.plano_multilingual["total_idiomas"],
                    "guia": plano_ml.get("guia_youtube_studio"),
                })
                print(f"  ✅ Plano multilíngue: {resultado.plano_multilingual['total_idiomas']} idiomas")
            except Exception as e:
                self._log_etapa(resultado, "MULTILINGUAL", "erro", {"erro": str(e)})
                print(f"  ⚠ Multilíngue erro: {e}")
        else:
            resultado.plano_multilingual = {
                "status": "aguardando_video_id",
                "instrucao": (
                    "Após publicar o vídeo no YouTube, chame "
                    "pipeline.expandir_internacionalmente(canal, video_id, titulo, descricao, tags)"
                ),
            }
            self._log_etapa(resultado, "MULTILINGUAL", "aguardando_video_id")
            print(f"  ⏳ Multilíngue: aguardando video_id após publicação")

        resultado.status = "pronto"

        # Salvar resultado
        out_json = str(self.output_dir / f"pipeline_{canal.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(resultado.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"  ✅ Pipeline salvo: {out_json}")

        return resultado

    def status(self) -> dict:
        """Retorna status do pipeline e todos os canais configurados."""
        return {
            "agente": "PRODUCTION_PIPELINE",
            "versao": "1.0.0",
            "canais": list(PIPELINE_CONFIG.keys()),
            "total_canais": len(PIPELINE_CONFIG),
            "total_idiomas_cobertura": sum(
                len(CANAIS_CONFIG.get(c, {}).get("idiomas_alvo", []))
                for c in PIPELINE_CONFIG
            ),
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
        }


# ═══════════════════════════════════════════════════════
# WRAPPERS PARA USO NOS TRIGGERS DOS CANAIS
# ═══════════════════════════════════════════════════════

def produzir_short_e_expandir(
    canal: str,
    titulo: str,
    script: str,
    descricao: str,
    tags: List[str],
    video_id_youtube: Optional[str] = None,
    **kwargs,
) -> dict:
    """
    Wrapper funcional para triggers dos canais.
    Produz Short + expande internacionalmente.
    """
    pipeline = DarkProductionPipeline()
    resultado = pipeline.produzir_e_expandir(
        canal=canal,
        titulo=titulo,
        script=script,
        descricao=descricao,
        tags=tags,
        video_id_youtube=video_id_youtube,
        **kwargs,
    )
    return resultado.to_dict()


def expandir_video_publicado(
    canal: str,
    video_id: str,
    titulo: str,
    descricao: str,
    tags: List[str],
    script: Optional[str] = None,
) -> dict:
    """
    Wrapper para expandir um vídeo já publicado.
    Use após publicar um novo Short para gerar metadados multilíngues.
    """
    pipeline = DarkProductionPipeline()
    return pipeline.expandir_internacionalmente(
        canal=canal,
        video_id=video_id,
        titulo=titulo,
        descricao=descricao,
        tags=tags,
        script=script,
    )


# ═══════════════════════════════════════════════════════
# MAIN — DEMONSTRAÇÃO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK PRODUCTION PIPELINE — INTEGRADO              ║")
    print("║   Produção + Expansão Internacional                  ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    pipeline = DarkProductionPipeline()
    st = pipeline.status()
    print(f"Canais: {st['total_canais']}")
    print(f"Cobertura de idiomas: {st['total_idiomas_cobertura']} combinações canal×idioma\n")

    # Simular produção de um Short para Mente de Aço
    resultado = pipeline.produzir_e_expandir(
        canal="Mente de Aço",
        titulo="O Segredo da Disciplina Mental — Sua Vida vai Mudar",
        script=(
            "A maioria das pessoas falha porque espera motivação. "
            "Os campeões não esperam sentir vontade. Eles agem. "
            "Disciplina não é uma emoção. É uma escolha repetida."
        ),
        descricao=(
            "Aprenda a desenvolver uma mente inabalável com as técnicas "
            "usadas pelos maiores atletas e líderes do mundo."
        ),
        tags=["disciplina", "mente de aço", "motivação", "psicologia", "mentalidade"],
        video_id_youtube="HXDngAAmUbo",  # vídeo existente para demonstração
    )

    print(f"\nStatus pipeline: {resultado.status}")
    print(f"Etapas: {len(resultado.etapas)}")
    if resultado.plano_multilingual:
        n = resultado.plano_multilingual.get("total_idiomas", 0)
        guia = resultado.plano_multilingual.get("guia_youtube_studio", "")
        print(f"Multilíngue: {n} idiomas → {guia}")
