# 🎬 DARK STICKMAN STUDIO

**Pipeline de produção automatizada de vídeos stickman para 12 canais YouTube faceless.**

> Produzido com IA — DARK STUDIO AAA — DARK CREATIVE LAB  
> `ai_generated: True` | Licença: MIT

---

## O que é

DARK STICKMAN STUDIO é um sistema open-source que automatiza a produção de vídeos de 4 minutos com animações stickman para canais YouTube sem apresentador ("dark channels"). 

O pipeline completo vai do roteiro ao MP4 final com:
- **Narração PT-BR** via Piper TTS (100% local, offline)
- **Animação** via Manim CE (biblioteca matemática MIT)
- **Edição e efeitos** via FFmpeg (LGPL)
- **Legendas** via WhisperX/Whisper
- **Thumbnails** via Pillow
- **API REST** para integração com DARK STUDIO AAA (porta 7870)

**Stack 100% gratuita e open-source.** Zero assinaturas obrigatórias.

---

## Instalação (Windows)

```bat
# Clone o repositório
git clone https://github.com/Jeffersonjazz/dark-stickman-studio.git
cd dark-stickman-studio

# Execute o wizard de instalação
setup\setup_wizard.bat
```

### Instalação Manual

```bash
pip install -r requirements.txt
pip install manim
pip install piper-tts
# FFmpeg: winget install FFmpeg
```

---

## Uso rápido

```bash
# Verificar dependências
dark-stickman status

# Listar os 12 canais
dark-stickman canais

# Produzir um vídeo
dark-stickman produzir --canal psicologia --titulo "POR QUE PROCRASTINAMOS?"

# Produzir com roteiro personalizado
dark-stickman produzir --canal batalhas --titulo "A BATALHA DE STALINGRADO" \
  --roteiro meu_roteiro.json

# Produção em lote (5 vídeos)
dark-stickman lote --canal tecnologia --n 5

# Gerar thumbnail
dark-stickman thumbnail --canal psicologia --titulo "TÍTULO DO VÍDEO" --variacoes 3

# Iniciar API REST
dark-stickman api
```

---

## Os 12 canais

| # | Canal | Nicho | Cor |
|---|-------|-------|-----|
| 01 | Stickman Psicologia | Psicologia | 🟣 #6366F1 |
| 02 | Stickman Batalhas | Batalhas históricas | 🔴 #EF4444 |
| 03 | Stickman Tech | Tecnologia e IA | 🔵 #3B82F6 |
| 04 | Stickman STEM | Ciências exatas | 🟢 #22C55E |
| 05 | Stickman Filosofia | Filosofia | 🟣 #A855F7 |
| 06 | Stickman História | História mundial | 🟡 #F59E0B |
| 07 | Stickman Mistério | Mistérios e enigmas | 🟤 #8B5CF6 |
| 08 | Stickman Motivação | Desenvolvimento pessoal | 🔵 #60A5FA |
| 09 | Stickman Natureza | Natureza e ecologia | 🟢 #4ADE80 |
| 10 | Stickman Ciência | Descobertas científicas | 🟢 #34D399 |
| 11 | Stickman Finanças | Educação financeira | 🟡 #FCD34D |
| 12 | Stickman Saúde | Saúde e bem-estar | 🩷 #F472B6 |

---

## Pipeline F01 (15 etapas)

```
Roteiro JSON
    │
    ▼
[01] Inicializar job (SQLite)
[02] Gerar narração PT-BR (Piper TTS)
[03] Medir duração do áudio
[04] Gerar animação stickman (Manim CE)
[05] Renderizar intro hook
[06] Renderizar cenas
[07] Renderizar outro/CTA
[08] Concatenar vídeos (FFmpeg)
[09] Adicionar narração ao vídeo
[10] Gerar legenda SRT (WhisperX → Whisper → fallback)
[11] Burn-in de legendas
[12] Aplicar watermark de IA obrigatória ⚠️
[13] Aplicar color grade por nicho
[14] Gerar thumbnail 1280x720 (Pillow)
[15] Exportar MP4 final + QA check
```

### Marca d'água obrigatória

**Todos os vídeos incluem obrigatoriamente:**
```
"Produzido com IA — DARK STUDIO AAA"
```

Conforme as diretrizes do projeto DARK CREATIVE LAB: conteúdo produzido por IA deve ser identificado. O campo `ai_generated: true` está presente em todos os outputs da API.

---

## API REST (porta 7870)

Integração com DARK MANAGER via contrato JSON documentado.

```bash
# Iniciar servidor
dark-stickman api

# Documentação interativa
http://localhost:7870/docs
```

### Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status do sistema e dependências |
| POST | `/produzir` | Produzir vídeo (assíncrono) |
| POST | `/produzir/sincrono` | Produzir vídeo (síncrono, para testes) |
| POST | `/produzir/lote` | Produção em lote |
| GET | `/jobs/{job_id}` | Status de um job |
| GET | `/jobs` | Listar jobs com filtros |
| POST | `/thumbnail` | Gerar thumbnail(s) |
| GET | `/canais` | Listar 12 canais |
| GET | `/presets` | Listar presets cinematográficos |
| GET | `/stats` | Estatísticas de produção |

### Exemplo de request

```json
POST /produzir
{
  "roteiro": {
    "titulo": "POR QUE VOCÊ PROCRASTINA?",
    "hook": "E se a procrastinação fosse um mecanismo de defesa do cérebro?",
    "cenas": [
      {
        "num": 1, "tipo": "normal", "duracao_s": 8,
        "stickman_acao": "pensando",
        "narracao": "Hoje vamos entender por que adiamos tarefas importantes.",
        "fundo": "branco_minimalista"
      }
    ],
    "cta": "Inscreva-se para mais conteúdo!"
  },
  "canal": {
    "nome": "Stickman Psicologia",
    "nicho": "psicologia",
    "stickman_color": "#6366F1",
    "stickman_seed": 42,
    "modelo_tts": "faber-medium",
    "velocidade_fala": 1.05,
    "watermark": true
  }
}
```

---

## Estrutura do projeto

```
dark-stickman-studio/
├── core/
│   ├── stickman_svg.py      # Gerador SVG de stickman (20 poses)
│   ├── ffmpeg_utils.py      # Edição de vídeo via FFmpeg
│   ├── piper_tts.py         # Narração PT-BR via Piper TTS
│   ├── manim_scene.py       # Animação via Manim CE
│   ├── legenda.py           # Legendas via WhisperX/Whisper
│   └── thumbnail.py         # Thumbnails 1280x720 via Pillow
├── pipeline/
│   └── f01_producao.py      # Pipeline completo (15 etapas)
├── api/
│   ├── main.py              # FastAPI — 12 endpoints — porta 7870
│   └── models.py            # Modelos Pydantic (contratos JSON)
├── cli/
│   └── dark_stickman.py     # CLI Typer (6 comandos)
├── config/
│   ├── presets.json         # 9 presets cinematográficos
│   └── canais/              # 12 configs de canal (JSON)
├── db/
│   └── schema.sql           # Schema SQLite
├── replica/                 # Documentação de engenharia reversa
│   ├── recon.md
│   ├── architecture.md
│   ├── features.csv
│   └── build-log.md
├── setup/
│   └── setup_wizard.bat     # Instalador Windows
├── output/                  # Saída dos vídeos (gerado automaticamente)
├── requirements.txt
└── README.md
```

---

## Presets cinematográficos

| Preset | Estilo | Uso |
|--------|--------|-----|
| `documentario` | Frio, cinematográfico | Documentários, história |
| `natureza` | Verde orgânico, calmo | Natureza, vida selvagem |
| `historia` | Sépia quente, solene | História, acontecimentos |
| `tecnologia` | Azul neon, dinâmico | Tech, IA, inovação |
| `misterio` | Roxo sombrio, pausado | Mistério, suspense |
| `educacao` | Claro, didático | Educação, ciência |
| `relaxamento` | Pastel, sereno | Meditação, bem-estar |
| `musical` | Vibrante, energético | Música, entretenimento |
| `storytelling_dark` | Dramático, faceless | Canal dark sem apresentador |

---

## Dependências e licenças

| Ferramenta | Licença | Uso |
|------------|---------|-----|
| Manim CE | MIT | Animação matemática |
| FFmpeg | LGPL v2.1+ | Edição de vídeo |
| Piper TTS | MIT | Síntese de voz PT-BR |
| OpenAI Whisper | MIT | Transcrição / legendas |
| WhisperX | BSD | Transcrição word-level |
| Pillow | HPND | Geração de thumbnails |
| FastAPI | MIT | API REST |
| Typer | MIT | CLI |
| Rich | MIT | Terminal UI |
| SQLite | Domínio Público | Banco de dados local |

---

## Integração com DARK STUDIO AAA

O DARK STICKMAN STUDIO integra com o DARK MANAGER na porta 7870:

```python
# Exemplo de dispatch do DARK MANAGER
import requests

response = requests.post("http://localhost:7870/produzir", json={
    "roteiro": roteiro,
    "canal": canal_config
})
job_id = response.json()["job_id"]

# Acompanhar progresso
status = requests.get(f"http://localhost:7870/jobs/{job_id}").json()
```

---

## Diretrizes éticas

- **Transparência**: todos os vídeos incluem marca d'água de IA obrigatória
- **Licenças**: apenas ferramentas open-source com licenças compatíveis
- **Sem plágio**: zero cópia de código proprietário ou assets de terceiros
- **"Dark" = faceless**: o termo refere-se ao formato sem apresentador, não a conteúdo enganoso
- **Consentimento**: narração sintética identificada; sem uso de vozes reais sem autorização

---

## Contribuição

Issues e PRs bem-vindos em [github.com/Jeffersonjazz/dark-stickman-studio](https://github.com/Jeffersonjazz/dark-stickman-studio).

---

*DARK STICKMAN STUDIO faz parte do ecossistema DARK STUDIO AAA — DARK CREATIVE LAB.*  
*Produzido com IA — Claude Sonnet 4.6 — Anthropic.*
