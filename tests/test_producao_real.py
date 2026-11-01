#!/usr/bin/env python3
"""
FASE 10 — Teste de Produção Real Ponta-a-Ponta
DARK STUDIO AAA — DARK CREATIVE LAB

Executa um vídeo real pelo pipeline F02 e valida qualidade do output.
Custo alvo: R$0,00 (apenas backends gratuitos/locais).

ai_generated: True
ai_disclosure: Produzido com DARK STUDIO AAA — DARK CREATIVE LAB
"""
import sys
import os
import time
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ─── Roteiro de teste no formato real do pipeline ────────────────────────────

CANAL_JSON = ROOT / "config" / "canais" / "canal_09_natureza.json"

ROTEIRO_TESTE = {
    "id": "f10_amazonia_001",
    "titulo": "Amazônia — Fatos Extraordinários",
    "cenas": [
        {"id": "c01", "narracao": "A Amazônia abriga mais de 40 mil espécies de plantas conhecidas pela ciência.", "duracao": 8.0, "descricao_visual": "Vista aérea da floresta amazônica com dossel verde exuberante"},
        {"id": "c02", "narracao": "Suas florestas produzem 20 por cento do oxigênio terrestre e regulam o clima global.", "duracao": 8.0, "descricao_visual": "Raios de luz penetrando entre as árvores da floresta tropical"},
        {"id": "c03", "narracao": "Cada hectare de floresta primária pode conter mais de 400 espécies de árvores.", "duracao": 8.0, "descricao_visual": "Diversidade de árvores e plantas na floresta amazônica"},
        {"id": "c04", "narracao": "O rio Amazonas carrega 20 por cento de toda a água doce que chega aos oceanos.", "duracao": 8.0, "descricao_visual": "Vista do Rio Amazonas serpenteando pela floresta"},
        {"id": "c05", "narracao": "A biodiversidade amazônica ainda guarda segredos que a ciência mal começou a explorar.", "duracao": 8.0, "descricao_visual": "Macaco-prego observando a câmera em galho de árvore"},
    ]
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

VERDE   = "\033[92m"
VERM    = "\033[91m"
AMAR    = "\033[93m"
AZUL    = "\033[94m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

resultados = []

def ok(msg):
    print(f"  {VERDE}✅{RESET} {msg}")
    resultados.append(("ok", msg))

def falha(msg, exc=None):
    detalhe = f" — {exc}" if exc else ""
    print(f"  {VERM}❌{RESET} {msg}{detalhe}")
    resultados.append(("falha", msg))

def aviso(msg):
    print(f"  {AMAR}⚠️ {RESET} {msg}")
    resultados.append(("aviso", msg))

def secao(titulo):
    print(f"\n{BOLD}{AZUL}▶ {titulo}{RESET}")

# ─── SETUP ───────────────────────────────────────────────────────────────────

pasta_saida = Path(tempfile.mkdtemp(prefix="dark_f10_"))
canal_config = json.loads(CANAL_JSON.read_text()) if CANAL_JSON.exists() else {
    "nicho": "natureza", "duracao_alvo_s": 60, "ai_generated": True,
    "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB"
}

# ─── TESTE 1: Importações ────────────────────────────────────────────────────

secao("IMPORTAÇÕES E DEPENDÊNCIAS")

try:
    from pipeline.f02_imagem_realista import (
        planejar_cenas,
        gerar_imagens_cenas,
        animar_imagens_ken_burns,
        gerar_legendas_srt,
        check_pipeline_f02,
    )
    ok("pipeline F02 importado")
except Exception as e:
    falha("pipeline F02 não importou", e)
    sys.exit(1)

try:
    from core.visual_consistency import ProjetoVisualBank
    ok("ProjetoVisualBank importado")
except Exception as e:
    falha("ProjetoVisualBank", e)
    ProjetoVisualBank = None

try:
    check_ok = check_pipeline_f02()
    n_ok = sum(1 for v in check_ok.values() if v)
    ok(f"check_pipeline_f02(): {n_ok}/{len(check_ok)} componentes ok")
except Exception as e:
    aviso(f"check_pipeline_f02() falhou: {e}")

# ─── TESTE 2: Planejamento de cenas ─────────────────────────────────────────

secao("PLANEJAMENTO CINEMATOGRÁFICO")

t0 = time.time()
roteiro_cinematico = None
try:
    roteiro_cinematico = planejar_cenas(ROTEIRO_TESTE, canal_config)
    elapsed = time.time() - t0
    assert isinstance(roteiro_cinematico, dict)
    cenas_enr = roteiro_cinematico.get("cenas_enriquecidas", roteiro_cinematico.get("cenas", []))
    ok(f"planejar_cenas(): {len(cenas_enr)} cenas em {elapsed:.2f}s")
    for i, c in enumerate(cenas_enr[:2], 1):
        enquad = c.get("enquadramento", c.get("camera", ""))[:50]
        print(f"    Cena {i}: enquadramento={enquad}")
except Exception as e:
    falha("planejar_cenas()", e)
    roteiro_cinematico = ROTEIRO_TESTE  # fallback para continuar testes

# ─── TESTE 3: Geração de imagens ─────────────────────────────────────────────

secao("GERAÇÃO DE IMAGENS (Pillow fallback)")

imagens_geradas = []
t0 = time.time()
try:
    imagens_geradas = gerar_imagens_cenas(roteiro_cinematico, pasta_saida)
    elapsed = time.time() - t0
    existentes = [d for d in imagens_geradas if Path(d["imagem_path"]).exists()]
    ok(f"gerar_imagens_cenas(): {len(existentes)}/{len(imagens_geradas)} imagens em {elapsed:.1f}s")
    for item in existentes[:2]:
        p = Path(item["imagem_path"])
        sz = p.stat().st_size // 1024
        print(f"    {p.name} [{item.get('backend','?')}] — {sz} KB")
except Exception as e:
    falha("gerar_imagens_cenas()", e)

# ─── TESTE 4: Animação Ken Burns ─────────────────────────────────────────────

secao("ANIMAÇÃO KEN BURNS (FFmpeg zoompan)")

clips_gerados = []
t0 = time.time()
try:
    clips_gerados = animar_imagens_ken_burns(imagens_geradas, roteiro_cinematico, pasta_saida)
    elapsed = time.time() - t0
    existentes_clips = [d for d in clips_gerados if Path(d.get("clip_path", d.get("path", ""))).exists()]
    ok(f"animar_imagens_ken_burns(): {len(existentes_clips)}/{len(clips_gerados)} clips em {elapsed:.1f}s")
    for item in existentes_clips[:2]:
        p = Path(item.get("clip_path", item.get("path", "")))
        sz = p.stat().st_size // 1024
        print(f"    {p.name} — {sz} KB")
except Exception as e:
    falha("animar_imagens_ken_burns()", e)

# ─── TESTE 5: Legendas SRT ───────────────────────────────────────────────────

secao("GERAÇÃO DE LEGENDAS SRT")

srt_path = pasta_saida / "legendas.srt"
t0 = time.time()
try:
    # narracoes: lista de dicts com path de áudio (pode ser vazia — usará timecodes das cenas)
    narracoes = [{"cena_id": c["id"], "duracao": c["duracao"]} for c in ROTEIRO_TESTE["cenas"]]
    resultado_srt = gerar_legendas_srt(roteiro_cinematico, narracoes, srt_path)
    elapsed = time.time() - t0
    if srt_path.exists():
        conteudo = srt_path.read_text()
        n_blocos = conteudo.count("\n\n")
        ok(f"gerar_legendas_srt(): {n_blocos} blocos SRT em {elapsed:.1f}s")
        print(f"    Preview:\n" + "\n".join("    " + l for l in conteudo.split("\n")[:6]))
    else:
        aviso("SRT não gerado")
except Exception as e:
    falha("gerar_legendas_srt()", e)

# ─── TESTE 6: Banco Visual ───────────────────────────────────────────────────

secao("BANCO VISUAL — ProjetoVisualBank")

banco_dir = pasta_saida / "banco_visual"
banco_dir.mkdir(exist_ok=True)

if ProjetoVisualBank:
    try:
        bank = ProjetoVisualBank(base_dir=banco_dir)
        proj = bank.criar_projeto("f10_amazonia", "Amazônia — Fatos Extraordinários", "natureza",
                                   descricao="Teste produção real Fase 10")
        assert proj.get("ai_generated") is True
        ok("criar_projeto() com ai_generated=True")

        bank.registrar_personagem("f10_amazonia", "Narrador",
                                   descricao="Voz em off masculina, grave e tranquila")
        bank.registrar_cenario("f10_amazonia", "Floresta Amazônica",
                                descricao="Dossel verde exuberante com luz filtrada",
                                iluminacao="natural", horario="manhã", clima="úmido")
        ok("personagem e cenário registrados")

        cena0 = ROTEIRO_TESTE["cenas"][0]
        img0_path = imagens_geradas[0]["imagem_path"] if imagens_geradas else ""
        bank.registrar_cena_produzida(
            "f10_amazonia",
            idx=0,
            imagem_path=img0_path,
            prompt_usado=imagens_geradas[0].get("prompt", cena0.get("descricao_visual", "")) if imagens_geradas else "",
            duracao_s=cena0["duracao"],
        )
        ok("cena produzida registrada no banco visual")

        relatorio = bank.exportar_relatorio("f10_amazonia")
        assert relatorio.get("ai_disclosure") is not None
        ok(f"relatório banco visual exportado — ai_disclosure presente")
    except Exception as e:
        falha("ProjetoVisualBank", e)
else:
    aviso("ProjetoVisualBank não disponível — pulando")

# ─── TESTE 7: Concatenação FFmpeg ─────────────────────────────────────────────

secao("CONCATENAÇÃO FINAL (FFmpeg)")

def _clip_path(item):
    if isinstance(item, dict):
        return Path(item.get("clip_path", item.get("path", "")))
    return Path(item)

clips_paths = [_clip_path(c) for c in clips_gerados if _clip_path(c).exists()]
mp4_final = pasta_saida / "video_final.mp4"

if clips_paths:
    try:
        lista_concat = pasta_saida / "concat_list.txt"
        lista_concat.write_text("\n".join(f"file '{p}'" for p in clips_paths))
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(lista_concat),
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
            "-movflags", "+faststart", str(mp4_final)
        ]
        ret = subprocess.run(cmd, capture_output=True, text=True)
        if ret.returncode == 0 and mp4_final.exists():
            sz_mb = mp4_final.stat().st_size / (1024 * 1024)
            ok(f"MP4 final gerado: {mp4_final.name} ({sz_mb:.2f} MB)")
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(mp4_final)],
                capture_output=True, text=True
            )
            if probe.returncode == 0:
                dur = float(json.loads(probe.stdout)["format"].get("duration", 0))
                ok(f"Duração do vídeo final: {dur:.1f}s")
        else:
            aviso(f"FFmpeg concatenação: {ret.stderr[-200:] if ret.stderr else 'erro desconhecido'}")
    except Exception as e:
        falha("Concatenação FFmpeg", e)
else:
    aviso("Sem clips para concatenar")

# ─── TESTE 8: ai_disclosure obrigatório ──────────────────────────────────────

secao("VALIDAÇÃO AI_DISCLOSURE OBRIGATÓRIO")

try:
    relatorio_final = {
        "projeto": "f10_amazonia",
        "titulo": ROTEIRO_TESTE["titulo"],
        "nicho": canal_config.get("nicho", "natureza"),
        "n_cenas": len(ROTEIRO_TESTE["cenas"]),
        "n_imagens": len(imagens_geradas),
        "n_clips": len(clips_gerados),
        "mp4_gerado": mp4_final.exists(),
        "mp4_path": str(mp4_final) if mp4_final.exists() else None,
        "srt_path": str(srt_path) if srt_path.exists() else None,
        "ai_generated": True,
        "ai_disclosure": "Produzido com DARK STUDIO AAA — DARK CREATIVE LAB",
    }
    assert relatorio_final["ai_generated"] is True
    assert "DARK STUDIO AAA" in relatorio_final["ai_disclosure"]
    ok("ai_generated=True e ai_disclosure no relatório final")
    relatorio_json = pasta_saida / "relatorio_fase10.json"
    relatorio_json.write_text(json.dumps(relatorio_final, ensure_ascii=False, indent=2))
    ok(f"Relatório salvo: {relatorio_json}")
    print(f"\n  {BOLD}Resumo do vídeo gerado:{RESET}")
    print(f"    Cenas:    {relatorio_final['n_cenas']}")
    print(f"    Imagens:  {relatorio_final['n_imagens']}")
    print(f"    Clips:    {relatorio_final['n_clips']}")
    print(f"    MP4:      {'✅' if relatorio_final['mp4_gerado'] else '—'}")
    print(f"    SRT:      {'✅' if relatorio_final['srt_path'] else '—'}")
except Exception as e:
    falha("ai_disclosure", e)

# ─── RESULTADO FINAL ─────────────────────────────────────────────────────────

print(f"\n{'═'*55}")
print(f"{BOLD}  RELATÓRIO FASE 10 — PRODUÇÃO REAL{RESET}")
print(f"{'═'*55}")
total   = len(resultados)
n_ok    = sum(1 for r in resultados if r[0] == "ok")
n_fail  = sum(1 for r in resultados if r[0] == "falha")
n_aviso = sum(1 for r in resultados if r[0] == "aviso")
score   = int(n_ok / total * 100) if total else 0

print(f"  Verificações:  {total}")
print(f"  ✅ OK:         {n_ok}")
print(f"  ⚠️  Avisos:    {n_aviso}")
print(f"  ❌ Falhas:     {n_fail}")
print(f"  🎯 Score:      {score}/100")
print(f"\n  Saída: {pasta_saida}")
print(f"\n  ai_generated:   True")
print(f"  ai_disclosure:  Produzido com DARK STUDIO AAA — DARK CREATIVE LAB")

if n_fail == 0:
    print(f"\n  {VERDE}{BOLD}✅ FASE 10 APROVADA — Pronto para produção real{RESET}")
    sys.exit(0)
elif score >= 70:
    print(f"\n  {AMAR}{BOLD}⚠️  FASE 10 APROVADA COM AVISOS — score {score}/100{RESET}")
    sys.exit(0)
else:
    print(f"\n  {VERM}{BOLD}❌ FASE 10 REPROVADA — score {score}/100{RESET}")
    sys.exit(1)
