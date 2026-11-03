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

    # ═══════════════════════════════════════════════════
    # MOVIMENTO DE CÂMERA — FFmpeg nativo (zero custo)
    # ═══════════════════════════════════════════════════

    def _ffprobe_duracao(self, path: str) -> float:
        """Retorna duração em segundos via ffprobe."""
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_streams", str(path)],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(r.stdout)
            for s in data.get("streams", []):
                if s.get("duration"):
                    return float(s["duration"])
        except Exception:
            pass
        return 5.0

    def zoom_cinematico(self, input_path: str, output_path: str,
                        tipo: str = "zoom_in", duracao: float = None,
                        intensidade: float = 1.5) -> dict:
        """
        Aplica movimento de câmera cinematográfico via FFmpeg zoompan.

        tipo: "zoom_in" | "zoom_out" | "ken_burns" | "parallax"
        intensidade: fator máximo de zoom (1.0 = sem zoom, 1.5 = 50% mais próximo)
        """
        inp = Path(input_path)
        if not inp.exists():
            return {"status": "erro", "msg": f"Arquivo não encontrado: {input_path}"}

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        dur = duracao or self._ffprobe_duracao(str(inp))
        fps = 25
        total_frames = int(dur * fps)
        z = intensidade

        if tipo == "zoom_in":
            # Começa em 1.0, termina em intensidade
            zoom_expr = f"1+({z}-1)*on/{total_frames}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif tipo == "zoom_out":
            # Começa em intensidade, termina em 1.0
            zoom_expr = f"{z}+({1}-{z})*on/{total_frames}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif tipo == "ken_burns":
            # Zoom diagonal + pan: canto superior-esquerdo → centro
            zoom_expr = f"1+({z}-1)*on/{total_frames}"
            x_expr = f"(iw/4)*(1-on/{total_frames})"
            y_expr = f"(ih/4)*(1-on/{total_frames})"
        else:  # parallax — zoom assimétrico simulando profundidade
            zoom_expr = f"1+({z*0.8}-1)*on/{total_frames}"
            x_expr = f"(iw/6)*sin(on*PI/{total_frames})"
            y_expr = "ih/2-(ih/zoom/2)"

        vf = (
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}'"
            f":d={total_frames}:s=1920x1080:fps={fps}"
        )

        cmd = [
            "ffmpeg", "-y", "-i", str(inp),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            str(out)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and out.exists():
                return {
                    "status": "ok", "output": str(out),
                    "tipo": tipo, "duracao": dur,
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
                }
            return {"status": "erro", "msg": result.stderr[-400:]}
        except subprocess.TimeoutExpired:
            return {"status": "erro", "msg": "FFmpeg timeout (>120s)"}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

    def pan_horizontal(self, input_path: str, output_path: str,
                       direcao: str = "esquerda", duracao: float = None) -> dict:
        """
        Travelling horizontal via FFmpeg crop animado.
        direcao: "esquerda" | "direita"
        """
        inp = Path(input_path)
        if not inp.exists():
            return {"status": "erro", "msg": f"Arquivo não encontrado: {input_path}"}

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        dur = duracao or self._ffprobe_duracao(str(inp))
        fps = 25
        total_frames = int(dur * fps)

        # Pan: move o ponto de crop de um lado ao outro
        # Usa `t` (segundos) no filtro crop, não `on` (só disponível em zoompan)
        if direcao == "esquerda":
            # x avança de 0 até 480 ao longo de `dur` segundos
            x_expr = f"480*t/{dur}"
        else:
            # x recua de 480 até 0
            x_expr = f"480*(1-t/{dur})"

        # Escala para 2400px de largura, depois crop 1920 com x animado
        vf = (
            f"scale=2400:1080,"
            f"crop=1920:1080:x='{x_expr}':y=0"
        )

        cmd = [
            "ffmpeg", "-y", "-i", str(inp),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy",
            str(out)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and out.exists():
                return {
                    "status": "ok", "output": str(out),
                    "direcao": direcao, "duracao": dur
                }
            return {"status": "erro", "msg": result.stderr[-400:]}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

    def estabilizar(self, input_path: str, output_path: str) -> dict:
        """
        Estabilização via libvidstab. Fallback gracioso se não disponível.
        """
        inp = Path(input_path)
        if not inp.exists():
            return {"status": "erro", "msg": f"Arquivo não encontrado: {input_path}"}

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        transforms = out.parent / "vidstab_transforms.trf"

        # Passo 1: detecção de movimento
        cmd1 = [
            "ffmpeg", "-y", "-i", str(inp),
            "-vf", f"vidstabdetect=shakiness=10:accuracy=15:result={transforms}",
            "-f", "null", "-"
        ]
        # Passo 2: aplicar estabilização
        cmd2 = [
            "ffmpeg", "-y", "-i", str(inp),
            "-vf", f"vidstabtransform=input={transforms}:zoom=5:smoothing=30",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy", str(out)
        ]

        try:
            r1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=120)
            if r1.returncode != 0:
                # libvidstab não disponível — copia sem modificar
                import shutil
                shutil.copy2(str(inp), str(out))
                return {
                    "status": "aviso",
                    "msg": "libvidstab não disponível. Arquivo copiado sem estabilização.",
                    "output": str(out)
                }
            r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)
            if transforms.exists():
                transforms.unlink()
            if r2.returncode == 0 and out.exists():
                return {"status": "ok", "output": str(out)}
            return {"status": "erro", "msg": r2.stderr[-400:]}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

    def animar_foto(self, input_path: str, output_path: str,
                    duracao: float = 6.0, efeito: str = "ken_burns") -> dict:
        """
        Transforma imagem estática em vídeo animado com movimento de câmera.
        Perfeito para criar B-roll a partir de fotos.
        """
        inp = Path(input_path)
        if not inp.exists():
            return {"status": "erro", "msg": f"Imagem não encontrada: {input_path}"}

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        fps = 25
        total_frames = int(duracao * fps)
        z = 1.4  # zoom padrão para foto

        if efeito == "ken_burns":
            zoom_expr = f"1+({z}-1)*on/{total_frames}"
            x_expr = f"(iw/5)*(1-on/{total_frames})"
            y_expr = f"(ih/5)*(1-on/{total_frames})"
        elif efeito == "zoom_in":
            zoom_expr = f"1+({z}-1)*on/{total_frames}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        else:  # zoom_out
            zoom_expr = f"{z}+(1-{z})*on/{total_frames}"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"

        vf = (
            f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}'"
            f":d={total_frames}:s=1920x1080:fps={fps},"
            f"format=yuv420p"
        )

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(inp),
            "-t", str(duracao),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode == 0 and out.exists():
                return {
                    "status": "ok", "output": str(out),
                    "efeito": efeito, "duracao": duracao,
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
                }
            return {"status": "erro", "msg": result.stderr[-400:]}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

    def gerar_broll_sintetico(self, tema: str, output_path: str,
                              duracao: float = 5.0,
                              resolucao: tuple = (1920, 1080)) -> dict:
        """
        Gera B-roll sintético 100% via FFmpeg lavfi — sem assets externos.

        tema: "natureza_verde" | "cidade_noite" | "espaco_estrelas" |
              "oceano_azul" | "floresta_densa"
        """
        TEMAS = {
            "natureza_verde": {
                "cor_base": "0x2d5a27",
                "cor2": "0x4a8c3f",
                "noise": "alls=30:allf=t+u",
                "descricao": "Verde floresta com variação orgânica"
            },
            "cidade_noite": {
                "cor_base": "0x0a0a1a",
                "cor2": "0x1a1a3a",
                "noise": "alls=15:allf=t",
                "descricao": "Azul escuro urbano noturno"
            },
            "espaco_estrelas": {
                "cor_base": "0x000010",
                "cor2": "0x050520",
                "noise": "alls=40:allf=t+u",
                "descricao": "Preto profundo com pontos de luz"
            },
            "oceano_azul": {
                "cor_base": "0x0d3b6e",
                "cor2": "0x1a5c9e",
                "noise": "alls=20:allf=t",
                "descricao": "Azul oceano com movimento de ondas"
            },
            "floresta_densa": {
                "cor_base": "0x1a3a0d",
                "cor2": "0x2d5c1a",
                "noise": "alls=35:allf=t+u",
                "descricao": "Verde escuro de floresta densa"
            },
        }

        t = TEMAS.get(tema, TEMAS["espaco_estrelas"])
        w, h = resolucao
        fps = 25
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Gradiente animado + noise + zoompan suave
        total_frames = int(duracao * fps)
        vf = (
            f"color=c={t['cor_base']}:s={w}x{h}:r={fps},"
            f"noise=c0s=30:c0f=t+u:allf=t+u,"
            f"zoompan=z='1+0.3*sin(on*PI/{total_frames})'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={w}x{h}:fps={fps},"
            f"format=yuv420p"
        )

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={t['cor_base']}:s={w}x{h}:r={fps}",
            "-t", str(duracao),
            "-vf", (
                f"noise=c0s=30:c0f=t+u:allf=t+u,"
                f"zoompan=z='1+0.2*sin(2*PI*on/{total_frames})'"
                f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={total_frames}:s={w}x{h}:fps={fps},"
                f"format=yuv420p"
            ),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            str(out)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and out.exists():
                return {
                    "status": "ok",
                    "output": str(out),
                    "tema": tema,
                    "descricao": t["descricao"],
                    "duracao": duracao,
                    "resolucao": f"{w}x{h}",
                    "custo": "R$0 (FFmpeg lavfi)",
                    "ai_generated": True,
                    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
                }
            return {"status": "erro", "msg": result.stderr[-500:]}
        except Exception as e:
            return {"status": "erro", "msg": str(e)}

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
