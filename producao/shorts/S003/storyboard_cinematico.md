# STORYBOARD CINEMATOGRÁFICO — SHORT S003
## AGENTE CINEMATIC DIRECTOR — DARK SHORTS FACTORY
## Canal: Dark Tech · Nicho: tecnologia

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

---

## IDENTIDADE VISUAL DO SHORT
- **Plano principal:** POV + tela de dados em foreground
- **Movimento de câmera:** Push in digital, glitch effect
- **Iluminação:** Backlight azul neon, reflexos holográficos
- **Color grade:** tech_blue_clinical
- **Proporção:** 9:16 (1080×1920)
- **Frame rate:** 30fps
- **Duração alvo:** 55s

---

## STORYBOARD — CENA A CENA

### ⏱ 0:00–0:05 — HOOK
- **Enquadramento:** POV + tela de dados em foreground, composição vertical, sujeito no terço superior
- **Ação visual:** Fade in de preto, texto aparece com typewriter effect
- **Texto:** "Uma IA previu a morte de pacientes com 90% de precisão."
- **Movimento:** Push in digital, glitch effect acelerado (×1.5)
- **Audio:** Música começa piano+sutil, TTS inicia

### ⏱ 0:05–0:20 — DESENVOLVIMENTO A
- **Enquadramento:** B-roll relacionado ao tema, cortes a cada 3s
- **Ação visual:** Série de imagens com Ken Burns alternando direção
- **Overlays:** Palavras-chave em destaque ao ritmo da narração
- **Movimento:** Push in digital, glitch effect
- **Iluminação target:** Backlight azul neon, reflexos holográficos

### ⏱ 0:20–0:40 — DESENVOLVIMENTO B (pico de tensão)
- **Enquadramento:** Close em elemento visual do nicho
- **Ação visual:** Cortes mais rápidos (1.5–2s por imagem)
- **Overlays:** Estatísticas ou citações animadas
- **Movimento:** Zoom in progressivo (1.0× → 1.3×)
- **Transição:** Corte seco + flash branco sutil

### ⏱ 0:40–55s — CTA + ENCERRAMENTO
- **Enquadramento:** Plano geral ou close final impactante
- **Ação visual:** Texto CTA entra de baixo (slide up)
- **Overlays:** Hashtags + ícone de like/seguir
- **Movimento:** Zoom out lento (1.1× → 1.0×)
- **Audio:** Música vai crescendo, TTS conclui, fade out

---

## PALETA DE CORES DO SHORT
- **Primária:** tech blue clinical
- **Texto:** JetBrains Mono, ciano neon em fundo escuro
- **Música mood:** eletrônico frio, synthwave, 110 BPM

---

## FFMPEG KEN BURNS — SHORT VERTICAL
```bash
# Ken Burns vertical adaptado para 9:16
zoompan=z='min(zoom+0.0006,1.3)':d=90:x='iw/2-(iw/zoom/2)':y='ih/4-(ih/zoom/4)':s=1080x1920
```

## TRANSIÇÕES RECOMENDADAS
1. Fade to black (0.3s) entre cenas principais
2. Cross dissolve (0.2s) entre B-roll
3. Flash branco (1 frame) no momento de revelação
4. Slide up para texto CTA
