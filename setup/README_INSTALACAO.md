# DARK STICKMAN STUDIO — Guia de Instalação

**DARK CREATIVE LAB — Plataforma Audiovisual de Custo Zero**

> ai_generated: True  
> ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB  
> Custo: **R$0,00/mês**

---

## Requisitos Mínimos

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| SO | Windows 10 64-bit | Windows 11 |
| Python | 3.10+ | 3.12+ |
| RAM | 4 GB | 8 GB+ |
| Armazenamento | 5 GB | 20 GB+ |
| GPU | Opcional | NVIDIA (CUDA) |
| Internet | Para edge-tts | Banda larga |

---

## Instalação Rápida (Windows)

### Opção 1 — Setup Automático (Recomendado)

1. Baixe e extraia o ZIP do projeto
2. Clique duas vezes em **`setup\setup_wizard.bat`**
3. Siga as instruções na tela
4. Quando finalizar, clique em **`launcher.bat`**
5. Acesse: **http://localhost:8000/panel**

### Opção 2 — Instalação Manual

```batch
:: 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

:: 2. Instalar dependências
pip install -r requirements.txt

:: 3. Instalar FFmpeg
winget install Gyan.FFmpeg

:: 4. Iniciar servidor
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Instalação no Linux / Mac

```bash
# 1. Clonar o repositório
git clone https://github.com/Jeffersonjazz/dark-stickman-studio.git
cd dark-stickman-studio

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Instalar FFmpeg
sudo apt install ffmpeg        # Ubuntu/Debian
brew install ffmpeg            # macOS

# 5. Iniciar
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Motores Disponíveis (Custo Zero)

| Motor | Função | Backend Local | Backend Online |
|-------|--------|---------------|----------------|
| DarkImageEngine | Geração de imagens | Pillow (cinematográfico) | HuggingFace* |
| DarkVideoEngine | Geração de vídeos | FFmpeg Ken Burns | — |
| DarkCinemaEditor | Edição de vídeo | FFmpeg | — |
| DarkAudioStudio | Narração TTS | Piper (offline) | edge-tts |
| DarkMotionLab | Motion graphics | Pillow + FFmpeg | — |
| DarkVisualConsistency | Consistência visual | Local | — |

*HuggingFace requer internet e pode estar bloqueado em alguns ambientes

---

## TTS — Narração em Português

### edge-tts (padrão, requer internet)
Instalado automaticamente. Vozes disponíveis:
- `pt-BR-FranciscaNeural` — Feminina (padrão)
- `pt-BR-AntonioNeural` — Masculina

### Piper TTS (offline, sem internet)
Baixado durante setup ou manualmente:
1. Acesse: https://huggingface.co/rhasspy/piper-voices/tree/main/pt/pt_BR/faber/medium
2. Baixe `pt_BR-faber-medium.onnx` e `pt_BR-faber-medium.onnx.json`
3. Salve em `%USERPROFILE%\DarkStudioAAA\modelos\piper\`

---

## Estrutura de Pastas

```
dark-stickman-studio/
├── api/              # FastAPI — servidor REST
├── core/             # 6 motores DARK CREATIVE LAB
│   ├── dark_image_engine.py
│   ├── dark_video_engine.py
│   ├── dark_cinema_editor.py
│   ├── dark_audio_studio.py
│   ├── dark_motion_lab.py
│   ├── dark_visual_consistency.py
│   └── dark_orchestrator.py   ← DARK MANAGER
├── pipeline/         # Fluxos de produção completos
├── config/           # Presets e configurações
├── panel/            # Interface web
├── setup/            # Instaladores
├── requirements.txt
└── launcher.bat      # Inicializador Windows
```

---

## Produção de Vídeo — Exemplo Rápido

```python
from core.dark_orchestrator import DarkOrchestrator

orch = DarkOrchestrator()
resultado = orch.produzir_video_completo(
    roteiro="""
    Cena 1: Floresta misteriosa ao amanhecer.
    Cena 2: Personagem caminha pela trilha.
    Cena 3: Descoberta de um objeto antigo.
    """,
    nicho="mistério",
    preset="storytelling_dark"
)

print(f"Vídeo: {resultado['video_final']}")
print(f"Custo: R${resultado['custo_brl']:.2f}")
# Custo: R$0.00
```

---

## Resolução de Problemas

### FFmpeg não encontrado
```batch
winget install Gyan.FFmpeg
:: Feche e reabra o terminal após instalar
```

### edge-tts falha (sem internet)
```bash
# O sistema usará fallback silencioso automaticamente
# Para TTS local, instale Piper (ver seção TTS acima)
```

### Erro "CUDA out of memory"
- Use o modo CPU (padrão, sem GPU necessária)
- Reduza o tamanho das imagens geradas

### Porta 8000 ocupada
```batch
python -m uvicorn api.main:app --port 8001
:: Acesse: http://localhost:8001/panel
```

---

## Compliance e Licenças

- Todo código é original, sem cópia de código proprietário
- Modelos open source usados conforme suas respectivas licenças
- edge-tts usa a API pública do Microsoft Edge (uso pessoal)
- Piper TTS: MIT License
- FFmpeg: LGPL/GPL (uso como processo externo)
- `ai_generated: True` incluído em todos os outputs
- Conteúdo sintético identificado como produzido por IA

---

*DARK CREATIVE LAB — Parte do ecossistema DARK STUDIO AAA*  
*GitHub: https://github.com/Jeffersonjazz/dark-stickman-studio*
