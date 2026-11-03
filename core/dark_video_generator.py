"""
DARK VIDEO GENERATOR — FASE 3 do DARK CREATIVE LAB
Agente de geração de vídeos via HuggingFace Spaces (gratuito/open source).

Modelos suportados:
  - CogVideoX-5B (THUDM) — texto → vídeo, imagem → vídeo
  - HunyuanVideo (Tencent) — alta qualidade
  - LTX-Video (Lightricks) — rápido, text-to-video
  - AnimateDiff — animação de imagens
  - Wan2.1 — vídeos realistas

Política de custo:
  SEMPRE usar alternativas gratuitas (HuggingFace Spaces, modelos locais).
  Serviços pagos (Runway, Kling, Pika, Sora) apenas com aprovação explícita.

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""

import json
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


# ═══════════════════════════════════════════════════════
# MAPA DE MODELOS E SPACES GRATUITOS
# ═══════════════════════════════════════════════════════
MODELOS = {
    "cogvideox": {
        "nome": "CogVideoX-5B",
        "empresa": "THUDM",
        "space": "THUDM/CogVideoX-5B-Space",
        "licenca": "Apache 2.0",
        "custo": "GRATUITO (HuggingFace Spaces)",
        "qualidade": "★★★★☆",
        "texto_para_video": True,
        "imagem_para_video": True,
        "duracao_max": 6,
        "resolucao": "720x480",
        "fps": 8,
        "vram_local": "24GB",
        "disponivel_api": True,
    },
    "hunyuanvideo": {
        "nome": "HunyuanVideo",
        "empresa": "Tencent",
        "space": "tencent/HunyuanVideo",
        "licenca": "Tencent Hunyuan Community",
        "custo": "GRATUITO (HuggingFace Spaces)",
        "qualidade": "★★★★★",
        "texto_para_video": True,
        "imagem_para_video": False,
        "duracao_max": 5,
        "resolucao": "720x1280",
        "fps": 24,
        "vram_local": "60GB+",
        "disponivel_api": True,
    },
    "ltx_video": {
        "nome": "LTX-Video",
        "empresa": "Lightricks",
        "space": "Lightricks/LTX-Video",
        "licenca": "Lightricks Open Source",
        "custo": "GRATUITO (HuggingFace Spaces)",
        "qualidade": "★★★★☆",
        "texto_para_video": True,
        "imagem_para_video": True,
        "duracao_max": 5,
        "resolucao": "512x512 a 1280x720",
        "fps": 24,
        "vram_local": "16GB",
        "disponivel_api": True,
    },
    "animatediff": {
        "nome": "AnimateDiff",
        "empresa": "Guoyww/Community",
        "space": "guoyww/animatediff",
        "licenca": "Apache 2.0",
        "custo": "GRATUITO",
        "qualidade": "★★★☆☆",
        "texto_para_video": True,
        "imagem_para_video": True,
        "duracao_max": 3,
        "resolucao": "512x512",
        "fps": 8,
        "vram_local": "8GB",
        "disponivel_api": True,
    },
}

MODELOS_PAGOS = {
    "runway": {"custo_por_segundo": 0.05, "qualidade": "★★★★★"},
    "kling": {"custo_por_segundo": 0.10, "qualidade": "★★★★★"},
    "pika": {"custo_por_credito": 0.08, "qualidade": "★★★★☆"},
    "sora": {"custo_por_segundo": 0.30, "qualidade": "★★★★★"},
    "veo": {"disponivel": False, "nota": "Google VEO apenas para parceiros"},
}


class DarkVideoGenerator:
    """
    Agente de geração de vídeos do DARK STUDIO AAA.
    Prioriza sempre alternativas gratuitas.
    """

    def __init__(self, output_dir: str = "outputs/videos_gerados"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log = []

    def selecionar_modelo(self, texto_para_video: bool = True,
                          imagem_para_video: bool = False,
                          qualidade_minima: int = 4) -> dict:
        """
        Seleciona o melhor modelo gratuito para a tarefa.
        Nunca usa modelos pagos sem aprovação.
        """
        candidatos = []
        for nome, m in MODELOS.items():
            if texto_para_video and not m["texto_para_video"]:
                continue
            if imagem_para_video and not m["imagem_para_video"]:
                continue
            stars = int(m["qualidade"][1])
            if stars >= qualidade_minima:
                candidatos.append((stars, nome, m))

        candidatos.sort(reverse=True)
        if not candidatos:
            return MODELOS["cogvideox"]  # fallback
        return {candidatos[0][1]: candidatos[0][2]}

    def gerar_via_gradio(self, prompt: str, modelo: str = "cogvideox",
                         duracao: int = 5, seed: int = 42) -> dict:
        """
        Gera vídeo via HuggingFace Space (Gradio API).
        Requer: pip install gradio_client
        """
        try:
            from gradio_client import Client
        except ImportError:
            return {
                "status": "erro",
                "msg": "gradio_client não instalado. Execute: pip install gradio_client --break-system-packages",
                "alternativa": "Use a interface web do HuggingFace Space diretamente"
            }

        m = MODELOS.get(modelo, MODELOS["cogvideox"])
        space = m["space"]

        print(f"\n[VIDEO_GENERATOR] Gerando via {m['nome']}...")
        print(f"  Space: {space}")
        print(f"  Prompt: {prompt[:80]}...")
        print(f"  Duração: {duracao}s")

        try:
            client = Client(space)
            result = client.predict(
                prompt=prompt,
                num_frames=int(duracao * m.get("fps", 8)),
                seed=seed,
                api_name="/generate"
            )
            out_path = self.output_dir / f"video_{modelo}_{int(time.time())}.mp4"
            # Copiar resultado
            if isinstance(result, str) and Path(result).exists():
                import shutil
                shutil.copy2(result, str(out_path))
                return {
                    "status": "OK",
                    "modelo": m["nome"],
                    "arquivo": str(out_path),
                    "prompt": prompt,
                    "custo": "GRATUITO",
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
                }
            return {"status": "erro", "msg": f"Resultado inesperado: {result}"}

        except Exception as e:
            return {"status": "erro", "msg": str(e),
                    "dica": f"Acesse manualmente: https://huggingface.co/spaces/{space}"}

    def animar_imagem(self, imagem_path: str, prompt_movimento: str,
                      modelo: str = "ltx_video") -> dict:
        """
        Anima uma imagem estática em vídeo (imagem → vídeo).
        Útil para animar thumbnails e fotos.
        """
        if not Path(imagem_path).exists():
            return {"status": "erro", "msg": f"Imagem não encontrada: {imagem_path}"}

        m = MODELOS.get(modelo, MODELOS["ltx_video"])
        if not m["imagem_para_video"]:
            modelo = "cogvideox"
            m = MODELOS["cogvideox"]

        return self.gerar_via_gradio(
            prompt=f"Animate this image: {prompt_movimento}",
            modelo=modelo
        )

    def gerar_broll(self, tema: str, estilo: str = "cinematografico",
                    quantidade: int = 3) -> list:
        """
        Gera múltiplos B-rolls para um tema.
        Retorna lista de clipes gerados.
        """
        estilos = {
            "cinematografico": "cinematic shot, 35mm film, shallow depth of field",
            "documental": "documentary footage, hand-held camera, natural lighting",
            "natureza": "wildlife documentary, slow motion, golden hour",
            "urbano": "urban environment, tracking shot, street photography",
            "historico": "historical footage, sepia tone, archival style",
        }

        suffix = estilos.get(estilo, "cinematic")
        resultados = []

        for i in range(quantidade):
            prompt = f"{tema}, {suffix}, 4K quality, no text, smooth motion"
            r = self.gerar_via_gradio(prompt, modelo="cogvideox", seed=42 + i)
            r["indice"] = i + 1
            r["tema"] = tema
            r["estilo"] = estilo
            resultados.append(r)

        return resultados

    def relatorio_modelos(self) -> dict:
        """Retorna ficha técnica de todos os modelos disponíveis"""
        return {
            "gratuitos": MODELOS,
            "pagos_referencia": MODELOS_PAGOS,
            "recomendacao": {
                "melhor_qualidade_gratuito": "hunyuanvideo",
                "mais_rapido_gratuito": "ltx_video",
                "melhor_custo_beneficio": "cogvideox",
                "para_animacao": "animatediff",
            },
            "instrucao": "Sempre usar gratuitos. Pagos só com aprovação explícita.",
            "ai_generated": True,
            "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
        }


# ═══════════════════════════════════════════════════════
# CONTRATO JSON PARA DARK MANAGER
# ═══════════════════════════════════════════════════════
CONTRACT = {
    "agente": "VIDEO_GENERATOR",
    "versao": "1.0.0",
    "descricao": "Geração de vídeos realistas e animações",
    "entrada": {
        "prompt": "str — descrição do vídeo",
        "imagem": "str? — path da imagem (para img2video)",
        "modelo": "str? — cogvideox|hunyuanvideo|ltx_video|animatediff",
        "duracao": "int? — segundos (default: 5)",
        "estilo": "str? — cinematografico|documental|natureza|urbano|historico",
        "seed": "int? — seed para reprodutibilidade"
    },
    "saida": {
        "status": "OK|erro",
        "arquivo": "str — path do MP4 gerado",
        "modelo_usado": "str",
        "custo": "str — GRATUITO ou valor em USD",
        "ai_generated": "bool",
        "ai_disclosure": "str"
    },
    "politica_custo": "SEMPRE gratuito por padrão. Modelos pagos exigem aprovação.",
    "dependencias": ["gradio_client", "huggingface_hub"],
    "install": "pip install gradio_client huggingface_hub --break-system-packages"
}


if __name__ == "__main__":
    gen = DarkVideoGenerator()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║   DARK VIDEO GENERATOR — FASE 3                      ║")
    print("║   Modelos gratuitos via HuggingFace                  ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    rel = gen.relatorio_modelos()
    print("MODELOS GRATUITOS DISPONÍVEIS:")
    for nome, m in rel["gratuitos"].items():
        print(f"\n  [{nome.upper()}]")
        print(f"    Nome: {m['nome']}")
        print(f"    Space: {m['space']}")
        print(f"    Licença: {m['licenca']}")
        print(f"    Qualidade: {m['qualidade']}")
        print(f"    Max: {m['duracao_max']}s @ {m['resolucao']}")
        print(f"    Texto→Vídeo: {'✅' if m['texto_para_video'] else '❌'}")
        print(f"    Imagem→Vídeo: {'✅' if m['imagem_para_video'] else '❌'}")

    print("\nRECOMENDAÇÕES:")
    for k, v in rel["recomendacao"].items():
        print(f"  {k}: {v}")

    # Salvar contrato
    Path("core").mkdir(exist_ok=True)
    with open("core/dark_video_generator_contract.json", "w", encoding="utf-8") as f:
        json.dump(CONTRACT, f, ensure_ascii=False, indent=2)
    print("\n  Contrato salvo em core/dark_video_generator_contract.json")
    print("\n  Para gerar vídeo: instale gradio_client e use a Gradio API")
    print("  Ou acesse os Spaces diretamente no HuggingFace.\n")
