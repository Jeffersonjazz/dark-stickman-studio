# MOTION GRAPHICS — SHORT S003
## AGENTE MOTION GRAPHICS — DARK SHORTS FACTORY
## Canal: Dark Tech · Estilo: tech blue clinical, hologramas médicos, UI futurista

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB

---

## ELEMENTOS VISUAIS ANIMADOS

### 1. TEXTO HOOK (0:00–0:05)
```
Conteúdo: "Uma IA previu a morte de pacientes com 90% de precisão."
Fonte: JetBrains Mono, ciano neon em fundo escuro
Posição: Centro vertical superior (y=15% da altura)
Animação: typewriter effect — 1 char/40ms
Duração: 3s
Fundo: Gradiente escuro na parte superior (overlay 60% opacidade)
```

### 2. LEGENDAS AUTOMÁTICAS (0:05–45s)
```
Fonte: Inter Bold, 38px
Cor: Branco com borda preta 3px
Posição: 80% da altura (terço inferior)
Máximo 2 linhas · 8 palavras por linha
Timing: sincronizado com TTS
Fundo: Caixa semi-transparente preta (70% opacidade)
```

### 3. PALAVRAS-CHAVE EM DESTAQUE
```
Trigger: substantivos e números impactantes
Cor destaque: tech blue clinical — cor de acento
Animação: scale 1.0→1.15 (0.1s) + volta
Duração highlight: 0.5s
```

### 4. PROGRESS BAR (opcional)
```
Posição: Topo da tela (y=0)
Altura: 4px
Cor: Acento do nicho
Animação: fill linear da esquerda para a direita
Duração: 55s total
```

### 5. CTA FINAL (0:43s em diante)
```
Ícone like: ❤️  tamanho 80px, pulsa a cada 1s
Texto: "Comenta: você deixaria a IA decidir seu tratamento?"
Posição: y=75% · centralizado
Animação: slide from bottom (0.4s ease-out)
Fundo: Gradiente escuro 80% nos últimos 15% da tela
```

### 6. HASHTAGS
```
Texto: #IA #InteligênciaArtificial #Tecnologia #Saúde #Shorts
Posição: y=90%
Fonte: Inter Regular 24px
Cor: Branco 70% opacidade
Animação: fade in (0.5s) no início do CTA
```

### 7. WATERMARK / BRANDING
```
Canal: Dark Tech
Posição: Canto superior direito
Tamanho: Inter Bold 22px
Cor: Acento 80% opacidade
Aparece: Sempre visível (from 0:02)
```

---

## FFMPEG DRAWTEXT (referência)
```bash
# Hook text
drawtext=text='Uma IA previu a morte de pacientes com 9...':fontsize=42:fontcolor=white:
x=(w-text_w)/2:y=h*0.15:shadowcolor=black:shadowx=2:shadowy=2:
enable='between(t,0,5)'

# Branding watermark
drawtext=text='Dark Tech':fontsize=22:fontcolor=white@0.8:
x=w-tw-20:y=20:shadowcolor=black:shadowx=1:shadowy=1:
enable='gte(t,2)'
```

---

## LEGENDAS SRT (template)
```srt
1
00:00:00,000 --> 00:00:05,000
Uma IA previu a morte de pacientes com 90% de precisão.

2
00:00:05,000 --> 00:00:20,000
O algoritmo do DeepMind analisou 700 mil registros médicos. Identificou insuficiência renal antes dos médicos. Salvou vidas — mas também...

3
00:00:45,000 --> 00:00:55,000
Comenta: você deixaria a IA decidir seu tratamento?
```
