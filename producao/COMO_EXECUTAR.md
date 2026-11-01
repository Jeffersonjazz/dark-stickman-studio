# 🎬 DARK STUDIO AAA — GUIA DE EXECUÇÃO LOCAL

**ai_generated: True | ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB**

---

## ⚡ INÍCIO RÁPIDO (Execução no seu computador)

### 1. Instalar dependências

```bash
pip install edge-tts gtts
```

### 2. Gerar narração de todos os vídeos

```bash
# V001 — Psicologia
python producao/v001_psicologia_vazio/gerar_narracao.py

# V002 — História
python producao/v002_historia_stonehouse/gerar_narracao.py

# V003 — Tecnologia
python producao/v003_tecnologia_ia_morte/gerar_narracao.py

# V004 — Mistério
python producao/v004_misterio_arquivo/gerar_narracao.py

# V005 — Natureza
python producao/v005_natureza_floresta/gerar_narracao.py
```

### 3. Executar orquestrador completo (todos os vídeos)

```bash
python producao/orquestrador_dark_manager.py
```

---

## 🎙️ MOTORES TTS DISPONÍVEIS

| Motor | Qualidade | Requer Internet | Idioma | Voz |
|-------|-----------|-----------------|--------|-----|
| **edge_tts** (primário) | ⭐⭐⭐⭐⭐ | ✅ Sim | pt-BR | pt-BR-AntonioNeural |
| **gTTS** (fallback) | ⭐⭐⭐ | ✅ Sim | pt-BR | Google TTS |
| **Piper** (local) | ⭐⭐⭐⭐ | ❌ Não | pt-BR | Leia-HFG (ver abaixo) |

### 🔇 Usar Piper TTS (100% offline)

```bash
# Download do modelo pt-BR (Leia)
pip install huggingface_hub
python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download('rhasspy/piper-voices', 'pt/pt_BR/leia/medium/pt_BR-leia-medium.onnx', local_dir='modelos_piper')
hf_hub_download('rhasspy/piper-voices', 'pt/pt_BR/leia/medium/pt_BR-leia-medium.onnx.json', local_dir='modelos_piper')
print('Modelo baixado em modelos_piper/')
"

# Gerar áudio com piper
echo "Texto de teste" | piper \
  --model modelos_piper/pt_BR-leia-medium.onnx \
  --output_file teste.wav
```

---

## 🎬 PIPELINE COMPLETO DE PRODUÇÃO

```
roteiro → gerar_narracao.py → audio/*.mp3
         → prompts_visuais_sd.md → IMAGE ENGINE → imagens/*.png
         → montar_video.py → output/V00X_final.mp4
```

### Gerar imagens (requer Stable Diffusion)

Instalar [ComfyUI](https://github.com/comfyanonymous/ComfyUI) ou [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

Usar os prompts em: `producao/vXXX/prompts_visuais_sd.md`

**Parâmetros recomendados:**
- Modelo: Realistic Vision V6 ou Deliberate v3
- Steps: 30 | CFG: 7.5 | Sampler: DPM++ 2M Karras
- Resolução: 1920×1080

### Montar vídeo (requer FFmpeg)

```bash
# Após gerar áudios e imagens:
python producao/v001_psicologia_vazio/montar_video.py
# Saída: producao/v001_psicologia_vazio/output/V001_final.mp4
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
producao/
├── orquestrador_dark_manager.py    # Orchestrador principal
├── v001_psicologia_vazio/
│   ├── gerar_narracao.py           # AUDIO MASTER
│   ├── pacote_producao.json        # Specs completas
│   ├── prompts_visuais_sd.md       # IMAGE ENGINE
│   ├── roteiro_naracao_completo.txt # Roteiro completo
│   ├── audio/                      # MP3 gerados
│   └── output/                     # MP4 final
├── v002_historia_stonehouse/       # John Stonehouse
├── v003_tecnologia_ia_morte/       # IA hospitalar
├── v004_misterio_arquivo/          # Arquivo secreto
└── v005_natureza_floresta/         # Rede micelial
```

---

## 💰 ESTIMATIVA DE GANHOS YOUTUBE

| Canal | Nicho | Views/mês estimado | RPM | Receita/mês |
|-------|-------|-------------------|-----|-------------|
| V001 | Psicologia | 50k | R$8 | R$400 |
| V002 | História | 80k | R$6 | R$480 |
| V003 | Tecnologia | 60k | R$12 | R$720 |
| V004 | Mistério | 100k | R$5 | R$500 |
| V005 | Natureza | 40k | R$7 | R$280 |
| **TOTAL** | | **330k** | | **R$2.380/mês** |

*Estimativas após 3-6 meses de canal monetizado com 1.000 inscritos*

---

## 🔧 REQUISITOS DE HARDWARE

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| RAM | 8GB | 16GB |
| GPU | Não necessária (TTS) | 8GB VRAM (SD) |
| Disco | 10GB | 50GB |
| OS | Windows 10 / Linux | Windows 11 / Ubuntu 22 |
| Python | 3.9+ | 3.11+ |

---

## ❓ TROUBLESHOOTING

**edge_tts falha:** Verifique conexão com internet. Execute `pip install edge-tts --upgrade`

**gTTS falha:** Verifique se `speech.google.com` está acessível

**Piper sem voz pt-BR:** Execute o download do modelo (ver seção Piper acima)

**FFmpeg não encontrado:** `apt install ffmpeg` (Linux) ou baixe em ffmpeg.org

---

*DARK STUDIO AAA v1.3.0 — 2024*
*ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB*
