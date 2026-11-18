# DARK STUDIO AAA — Multilingual Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expand DARK STUDIO AAA from 4–5 weekly Shorts (PT-BR only) to 10+ Shorts/week across 10 languages (EN, ES, DE, FR, IT, AR, JA, ZH, KO, PL) on 6 YouTube channels, maximizing international reach while keeping production fully automated.

**Architecture:** Each channel targets a specific set of languages based on its niche and audience potential. The existing DarkEdgeTTS v2 (5-tier TTS cascade, all free/offline) generates narration in any language. DarkMultilingualAgent v2.0.0 handles metadata translation. New dedicated scheduled triggers fire pre-written scripts in each language using the vidIQ MCP pipeline.

**Tech Stack:** Python 3.11, DarkEdgeTTS v2 (edge-tts/gTTS/espeak-ng), DarkMultilingualAgent v2.0.0, vidIQ MCP (voiceover_generate, generate_thumbnail, generate_video, compose, video_upload), Claude scheduled tasks (create_trigger / update_trigger)

**Spec:** `docs/multilingual_triggers.md` — contains trigger prompts and schedule matrix

## Global Constraints

- All production triggers use `model: claude-sonnet-4-6` via scheduled tasks API
- All YouTube Shorts: 1080×1920 (9:16), 50–60 seconds, public, madeForKids: false
- ai_generated: True, ai_disclosure required on all uploads
- DarkEdgeTTS v2 replaces ElevenLabs for all PT triggers (cost reduction)
- vidIQ voiceId `N2lVS1w4EtoT3dr4eOWO` (Callum) = default EN/international male voice
- Schedule: BRT (America/Sao_Paulo), no two triggers within 30 min of each other
- Do NOT present AI content as real documentary footage
- Weekly total target: 10–12 Shorts/week at full expansion

## Review Focus

- **Language quality:** Edge Neural TTS voice IDs must exist per language; fallback order is edge-tts → gTTS → espeak-ng
- **Schedule conflicts:** New triggers must not collide with existing active triggers (Mon 16:40, Thu 16:40, Sat 14:00, Last Sun 10:00)
- **vidIQ voice availability:** Callum ID `N2lVS1w4EtoT3dr4eOWO` confirmed working; other language voices need list_voices call before use
- **Paused trigger failure:** `trig_01RFgHsXA16KKPxuUyKSYiqA` last run FAILED with usage_limit — reactivate only after verifying vidIQ balance
- **Channel targeting:** Each language maps to 1–2 channels max to avoid content dilution

---

## Current State Audit

### Active Triggers (4)
| Trigger ID | Name | Schedule | Channel | Status |
|-----------|------|----------|---------|--------|
| (Mon) | Mente de Aço — PT | CRON Mon 16:40 BRT | UCPRWgHoI85u-gmZmS9uVbqA | ✅ Active |
| (Thu) | Esquina do Medo — PT | CRON Thu 16:40 BRT | UCwuyz5ABF6ooQUn2HwG9xHQ | ✅ Active |
| (Sat) | Best-Of Compilação | CRON Sat 14:00 BRT | UCwuyz5ABF6ooQUn2HwG9xHQ | ✅ Active |
| (Last Sun) | Long-Form Special | CRON Last Sun 10:00 BRT | Mixed | ✅ Active |

### Paused Triggers (3) — Need Reactivation
| Trigger ID | Name | Schedule | Channel |
|-----------|------|----------|---------|
| trig_015xbrPWxHCLgiSTkdXXZRDX | Intelligentia Nova | Tue 16:44 BRT | UCoGPdIQM2Bt5zSlV0DW0HQg |
| trig_01RFgHsXA16KKPxuUyKSYiqA | Bastidores do Tempo | Wed 16:40 BRT | UCMinaADQVJ6QbbhOr_idVdA |
| trig_01K6bnqRUi9ktiWSPgLMV4VT | AquaZen Relax | Fri 16:40 BRT | UC89YZqbZ02RTaT2FYepPHCQ |

### New Multilingual Triggers Needed (Manual Creation by User)
| Day | Name | Language | Channel |
|-----|------|----------|---------|
| Tue 11:11 | Iron Mind EN | English | Mente de Aço |
| Wed 11:44 | Fear Corner EN | English | Esquina do Medo |
| Fri 11:23 | Esquina del Miedo ES | Spanish | Esquina do Medo |
| Tue 09:30 | Angstecke DE | German | Esquina do Medo |
| Thu 09:15 | L'Esprit d'Acier FR | French | Mente de Aço |
| Sat 09:00 | Dark Tech DE | German | Intelligentia Nova |

---

### Task 1: Reactivate 3 Paused Triggers

**Files:**
- Modify: scheduled triggers via `mcp__claude-code-remote__update_trigger`
- Modify: `docs/multilingual_triggers.md` (add reactivation status)

**Interfaces:**
- Consumes: Trigger IDs from audit above
- Produces: 3 enabled triggers with v2.0 prompts using DarkEdgeTTS

- [ ] **Step 1: Update Intelligentia Nova trigger prompt to v2.0 + enable**
  - Replace ElevenLabs TTS steps with DarkEdgeTTS v2 fallback cascade
  - Add PASSO 10 — MULTILINGUAL AGENT step
  - Set `enabled: true`

- [ ] **Step 2: Update Bastidores do Tempo trigger prompt to v2.0 + enable**
  - Same DarkEdgeTTS v2 upgrade
  - Add PASSO 10 — MULTILINGUAL AGENT
  - Set `enabled: true`

- [ ] **Step 3: Update AquaZen Relax trigger prompt to v2.0 + enable**
  - Same DarkEdgeTTS v2 upgrade
  - Add PASSO 10 — MULTILINGUAL AGENT
  - Set `enabled: true`

- [ ] **Step 4: Verify all 3 triggers show enabled in list_triggers**

---

### Task 2: Expand multilingual_triggers.md with DE/FR/IT/AR Trigger Prompts

**Files:**
- Modify: `docs/multilingual_triggers.md`

**Interfaces:**
- Produces: Ready-to-paste trigger prompts for 4 additional languages

- [ ] **Step 1: Add Trigger 4 — Angstecke DE (Fear Corner German)**
  - Channel: Esquina do Medo (UCwuyz5ABF6ooQUn2HwG9xHQ)
  - Schedule: Tuesday 09:30 BRT (CRON_TZ=America/Sao_Paulo 30 9 * * 2)
  - Voice: `trig_KatjaNeural` → vidIQ German voice lookup

- [ ] **Step 2: Add Trigger 5 — L'Esprit d'Acier FR (Iron Mind French)**
  - Channel: Mente de Aço (UCPRWgHoI85u-gmZmS9uVbqA)
  - Schedule: Thursday 09:15 BRT (CRON_TZ=America/Sao_Paulo 15 9 * * 4)

- [ ] **Step 3: Add Trigger 6 — Dark Tech DE (Intelligentia Nova German)**
  - Channel: Intelligentia Nova (UCoGPdIQM2Bt5zSlV0DW0HQg)
  - Schedule: Saturday 09:00 BRT (CRON_TZ=America/Sao_Paulo 0 9 * * 6)

- [ ] **Step 4: Update weekly schedule matrix table**

---

### Task 3: Create dark_multilingual_factory.py

**Files:**
- Create: `core/dark_multilingual_factory.py`

**Interfaces:**
- Consumes: DarkMultilingualAgent v2.0, DarkEdgeTTS v2, channel configs
- Produces: Full production pipeline per channel × language combination

- [ ] **Step 1: Define FACTORY_CONFIG with all 6 channels × target languages**
- [ ] **Step 2: Implement pre-written scripts for DE, FR, IT, AR niches**
- [ ] **Step 3: Implement `produce_multilingual_short(channel, language, niche)` method**
- [ ] **Step 4: Wire DarkEdgeTTS v2 as primary TTS for all non-EN languages**
- [ ] **Step 5: Add `batch_produce_week()` for full weekly batch production**

---

### Task 4: Commit and Push

- [ ] **Step 1: `git add` all new/modified files**
- [ ] **Step 2: `git commit` with descriptive message**
- [ ] **Step 3: `git push origin main`**

---

## Target Weekly Schedule (Full Expansion)

| Day | Time (BRT) | Trigger | Language | Channel | Status |
|-----|-----------|---------|----------|---------|--------|
| Mon | 16:40 | Mente de Aço PT | PT-BR | Mente de Aço | ✅ Active |
| Tue | 09:30 | Angstecke DE 🆕 | German | Esquina do Medo | 📋 Manual |
| Tue | 11:11 | Iron Mind EN 🆕 | English | Mente de Aço | 📋 Manual |
| Tue | 16:44 | Intelligentia Nova PT | PT-BR | Intelligentia Nova | ⏸️ Reactivate |
| Wed | 11:44 | Fear Corner EN 🆕 | English | Esquina do Medo | 📋 Manual |
| Wed | 16:40 | Bastidores do Tempo PT | PT-BR | Bastidores do Tempo | ⏸️ Reactivate |
| Thu | 09:15 | L'Esprit d'Acier FR 🆕 | French | Mente de Aço | 📋 Manual |
| Thu | 16:40 | Esquina do Medo PT | PT-BR | Esquina do Medo | ✅ Active |
| Fri | 11:23 | Esquina del Miedo ES 🆕 | Spanish | Esquina do Medo | 📋 Manual |
| Fri | 16:40 | AquaZen Relax PT | PT-BR | AquaZen Relax | ⏸️ Reactivate |
| Sat | 09:00 | Dark Tech DE 🆕 | German | Intelligentia Nova | 📋 Manual |
| Sat | 14:00 | Best-Of Compilação | PT-BR | Esquina do Medo | ✅ Active |
| Last Sun | 10:00 | Long-Form Special | PT-BR | Mixed | ✅ Active |

**Total: 13 Shorts/week at full expansion** (up from 4 active + 3 paused = 7 existing)
**Languages covered: PT-BR, EN, ES, DE, FR**
**Next phase: IT, AR, JA, ZH, KO, PL**
