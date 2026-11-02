"""
DARK YOUTUBE PUBLISHER — Batch Publisher
Publica múltiplos vídeos em múltiplos canais automaticamente.
Integrado com o pipeline DARK STUDIO AAA.
"""

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

from dark_youtube_publisher.auth.oauth_manager import load_credentials, authorize_channel
from dark_youtube_publisher.core.youtube_uploader import DarkYouTubeUploader

RESULTS_DIR = Path.home() / ".dark_studio" / "publish_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento canais Jefferson — nichos oficiais confirmados 02/11/2026
DARK_CHANNELS = {
    "intelligentia_nova": {
        "label": "Intelligentia Nova",
        "handle": "@intelligentianova",
        "channelId": "UCoGPdIQM2Bt5zSlV0DW0HQg",
        "niche": "tech",
        "tags_base": ["inteligência artificial", "tecnologia", "IA", "futuro", "dark channel"],
    },
    "esquina_do_medo": {
        "label": "Esquina do Medo",
        "handle": "@esquinadomedo-k3s",
        "channelId": "UCwuyz5ABF6ooQUn2HwG9xHQ",
        "niche": "terror",
        "tags_base": ["terror", "mistério", "histórias de terror", "dark", "assustador"],
    },
    "projeto_secreto": {
        "label": "Projeto Secreto",
        "handle": "@projetosecreto-y9e",
        "channelId": "UCOfXd8Hf_83Y2VHWmj3f3Vg",
        "niche": "conspiracao",
        "tags_base": ["conspirações", "área 51", "segredos", "curiosidades", "arquivos secretos"],
    },
    "aquazen_relax": {
        "label": "AquaZen Relax",
        "handle": "@aquazenrelaxbr",
        "channelId": "UC89YZqbZ02RTaT2FYepPHCQ",
        "niche": "natureza",
        "tags_base": ["natureza", "relaxamento", "sons da natureza", "cachoeira", "meditação", "ASMR"],
    },
    "mente_de_aco": {
        "label": "Mente de Aço",
        "handle": "@mentedeaco-o7u",
        "channelId": "UCPRWgHoI85u-gmZmS9uVbqA",
        "niche": "motivacao",
        "tags_base": ["mentalidade", "motivação", "disciplina", "foco", "desenvolvimento pessoal"],
    },
    "bastidores_do_tempo": {
        "label": "Bastidores do Tempo",
        "handle": "@bastidoresdotempo-l6p",
        "channelId": "UCMinaADQVJ6QbbhOr_idVdA",
        "niche": "historia",
        "tags_base": ["história", "fatos históricos", "documentário", "passado", "curiosidades históricas"],
    },
    "horizonte_cosmico": {
        "label": "Horizonte Cósmico",
        "handle": "@horizontecósmico-v8i",
        "niche": "espaco",
        "tags_base": ["espaço", "astronomia", "universo", "ciência", "NASA"],
    },
    "mente_de_investidor": {
        "label": "Mente de Investidor",
        "handle": "@mentedeinvestidor-g9i",
        "niche": "investimentos",
        "tags_base": ["investimentos", "finanças", "dinheiro", "bolsa", "renda passiva"],
    },
    "mestre_do_oculto": {
        "label": "Mestre do Oculto",
        "handle": "@mestrédooculto",
        "niche": "ocultismo",
        "tags_base": ["ocultismo", "esoterismo", "mistério", "magia", "oculto"],
    },
    "bussola_virtual": {
        "label": "Bússola Virtual",
        "handle": "@bússolavirtual",
        "niche": "viagens",
        "tags_base": ["viagens", "turismo", "lugares incríveis", "mundo", "destinos"],
    },
    "linha_de_investigacao": {
        "label": "Linha de Investigação",
        "handle": "@linhadainvestigação-o9k",
        "niche": "crimes",
        "tags_base": ["crimes", "investigação", "casos reais", "true crime", "mistério criminal"],
    },
    "mente_curiosa": {
        "label": "Mente Curiosa",
        "handle": "@mentecuriosa-v6z",
        "niche": "curiosidades",
        "tags_base": ["curiosidades", "ciência", "educação", "você sabia", "fatos incríveis"],
    },
    "mentes_que_mudaram": {
        "label": "Mentes que Mudaram o Mundo",
        "handle": "@mentesquemudararamoMundo-o3v",
        "niche": "historia",
        "tags_base": ["biografias", "grandes pensadores", "história", "personalidades", "legado"],
    },
    "caminho_do_meio": {
        "label": "O Caminho do Meio",
        "handle": "@ocaminhodoMeio-b4r",
        "niche": "filosofia",
        "tags_base": ["filosofia", "filósofos", "estoicismo", "sabedoria", "reflexão"],
    },
    "profeta_do_vale": {
        "label": "Profeta do Vale de Jeová",
        "handle": "@profetadovaledejová",
        "niche": "biblica",
        "tags_base": ["bíblia", "histórias bíblicas", "JW", "estudos bíblicos", "fé"],
    },
    "atlantic_dnb": {
        "label": "ATLANTIC DNB",
        "handle": "@basssyndicatebr",
        "niche": "musica",
        "tags_base": ["drum and bass", "jungle", "música eletrônica", "DNB", "bass"],
    },
}


@dataclass
class PublishJob:
    channel_key: str
    video_url: str
    title: str
    description: str
    extra_tags: list
    thumbnail_url: Optional[str] = None
    is_short: bool = True
    privacy: str = "public"


@dataclass
class PublishResult:
    channel_key: str
    channel_label: str
    title: str
    video_id: Optional[str]
    youtube_url: Optional[str]
    success: bool
    error: Optional[str]
    ai_generated: bool = True
    ai_disclosure: str = "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"


class DarkBatchPublisher:
    """Publica batch de vídeos em múltiplos canais DARK STUDIO AAA."""

    def __init__(self, client_secrets_path: str):
        self.client_secrets_path = client_secrets_path
        self.results: list[PublishResult] = []

    def _get_uploader(self, channel_key: str) -> DarkYouTubeUploader | None:
        ch = DARK_CHANNELS.get(channel_key)
        if not ch:
            print(f"[BATCH] Canal desconhecido: {channel_key}")
            return None

        creds = load_credentials(ch["label"])
        if not creds:
            print(f"[BATCH] Sem token para {ch['label']}. Iniciando autorização...")
            try:
                creds = authorize_channel(ch["label"], self.client_secrets_path)
            except Exception as e:
                print(f"[BATCH] Falha na autorização: {e}")
                return None

        return DarkYouTubeUploader(creds)

    def publish_batch(self, jobs: list[PublishJob], delay_between: int = 10) -> list[PublishResult]:
        """Executa todos os jobs de publicação em sequência."""
        print(f"\n[BATCH] 🚀 Iniciando batch de {len(jobs)} vídeos...")

        for i, job in enumerate(jobs, 1):
            ch = DARK_CHANNELS.get(job.channel_key, {})
            label = ch.get("label", job.channel_key)
            niche = ch.get("niche", "tech")
            base_tags = ch.get("tags_base", [])
            all_tags = base_tags + job.extra_tags

            print(f"\n[BATCH] [{i}/{len(jobs)}] {label}: {job.title}")

            uploader = self._get_uploader(job.channel_key)
            if not uploader:
                self.results.append(PublishResult(
                    channel_key=job.channel_key,
                    channel_label=label,
                    title=job.title,
                    video_id=None,
                    youtube_url=None,
                    success=False,
                    error="Sem credenciais OAuth",
                ))
                continue

            try:
                result = uploader.upload_from_url(
                    video_url=job.video_url,
                    title=job.title,
                    description=job.description,
                    tags=all_tags,
                    category_key=niche,
                    privacy=job.privacy,
                    is_short=job.is_short,
                )

                # Thumbnail opcional
                if job.thumbnail_url:
                    uploader.set_thumbnail(result["videoId"], job.thumbnail_url)

                self.results.append(PublishResult(
                    channel_key=job.channel_key,
                    channel_label=label,
                    title=job.title,
                    video_id=result["videoId"],
                    youtube_url=result["url"],
                    success=True,
                    error=None,
                ))
                print(f"[BATCH] ✅ {label}: {result['url']}")

            except Exception as e:
                self.results.append(PublishResult(
                    channel_key=job.channel_key,
                    channel_label=label,
                    title=job.title,
                    video_id=None,
                    youtube_url=None,
                    success=False,
                    error=str(e),
                ))
                print(f"[BATCH] ❌ Erro em {label}: {e}")

            if i < len(jobs):
                print(f"[BATCH] Aguardando {delay_between}s antes do próximo...")
                time.sleep(delay_between)

        self._save_results()
        return self.results

    def _save_results(self):
        ts = int(time.time())
        result_file = RESULTS_DIR / f"batch_{ts}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.results], f, ensure_ascii=False, indent=2)
        print(f"\n[BATCH] Resultados salvos: {result_file}")

    def summary(self) -> str:
        ok = [r for r in self.results if r.success]
        fail = [r for r in self.results if not r.success]
        lines = [f"✅ {r.channel_label}: {r.youtube_url}" for r in ok]
        lines += [f"❌ {r.channel_label}: {r.error}" for r in fail]
        return "\n".join(lines)
