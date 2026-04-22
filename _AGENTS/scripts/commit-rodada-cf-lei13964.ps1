# -----------------------------------------------------------------------------
# commit-rodada-cf-lei13964.ps1
# Gerado por Claude — rodada KB-PD: ingestão CF/1988 + Lei 13.964/2019 (v1.2)
# Data geração: 2026-04-22
#
# O que este script faz (NA ORDEM, com fail-fast):
#   1. Valida que está rodando em C:\Users\Membro\MouraxDB
#   2. Remove .git/index.lock stale (9P não permitiu remover da sandbox)
#   3. Remove órfãos (.wtest, .gitk fantasma)
#   4. git reset HEAD (desfaz TODO o staging atual — incluindo as deleções perigosas)
#   5. Verifica que os 4 arquivos críticos de schema/ estão no disco
#   6. git add cirúrgico dos arquivos desta rodada + dos schema re-adicionados
#   7. Mostra git diff --cached --stat + git status
#   8. Pede CONFIRMAÇÃO humana
#   9. git commit com mensagem estruturada
#  10. Opcional: git push (COMENTADO — descomente se desejar)
#
# PRÉ-REQUISITO: executar a partir de PowerShell 5.1+ com cwd = C:\Users\Membro\MouraxDB
#   > cd C:\Users\Membro\MouraxDB
#   > powershell -ExecutionPolicy Bypass -File _AGENTS\scripts\commit-rodada-cf-lei13964.ps1
# -----------------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ---- 0. cabeçalho ----
Write-Host ""
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "  commit-rodada-cf-lei13964.ps1  (KB-PD pipeline v1.2)" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# ---- 1. validação do PWD ----
$expectedRoot = 'C:\Users\Membro\MouraxDB'
if ((Resolve-Path -LiteralPath '.').Path -ne $expectedRoot) {
    Write-Host "[FATAL] cwd atual: $((Resolve-Path .).Path)" -ForegroundColor Red
    Write-Host "[FATAL] cwd esperado: $expectedRoot" -ForegroundColor Red
    Write-Host "        Execute: cd $expectedRoot" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK]   cwd = $expectedRoot" -ForegroundColor Green

# ---- 2. remover .git\index.lock stale ----
if (Test-Path '.git\index.lock') {
    $lockInfo = Get-Item '.git\index.lock'
    $ageMin = [math]::Round(((Get-Date) - $lockInfo.LastWriteTime).TotalMinutes, 1)
    Write-Host "[INFO] .git\index.lock existe (idade: ${ageMin} min)" -ForegroundColor Yellow
    Remove-Item -Force '.git\index.lock'
    Write-Host "[OK]   .git\index.lock removido" -ForegroundColor Green
} else {
    Write-Host "[OK]   .git\index.lock ausente" -ForegroundColor Green
}

# ---- 3. remover órfãos ----
$orphans = @(
    'raw\A-normativas\.wtest',
    'inbox\.wtest',
    'raw\B-jurisprudencia\.gitk'
)
foreach ($o in $orphans) {
    if (Test-Path $o) {
        Remove-Item -Force $o
        Write-Host "[OK]   removido órfão: $o" -ForegroundColor Green
    }
}

# ---- 4. git reset HEAD (desfaz staging perigoso) ----
Write-Host ""
Write-Host "--- git reset HEAD ---" -ForegroundColor Cyan
git reset HEAD 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FATAL] git reset falhou" -ForegroundColor Red
    exit 1
}
Write-Host "[OK]   staging desfeito (schema/* não será mais commitado como deletado)" -ForegroundColor Green

# ---- 5. pré-voo: schema/ intacto no disco? ----
$critical = @(
    'schema\vocabulario.yaml',
    'schema\CORPUS_HEALTH.md',
    'schema\VOCAB_HEALTH.md',
    'schema\golden_dataset.yaml'
)
$missing = @()
foreach ($f in $critical) {
    if (-not (Test-Path $f)) {
        $missing += $f
    } else {
        $sz = (Get-Item $f).Length
        if ($sz -eq 0) { $missing += "$f (ZERO bytes)" }
    }
}
if ($missing.Count -gt 0) {
    Write-Host "[FATAL] Arquivos críticos ausentes ou vazios no disco:" -ForegroundColor Red
    foreach ($m in $missing) { Write-Host "         - $m" -ForegroundColor Red }
    Write-Host "        ABORTANDO antes de qualquer git add." -ForegroundColor Red
    exit 1
}
Write-Host "[OK]   4 arquivos schema/ críticos presentes e não-vazios" -ForegroundColor Green

# ---- 6. git add cirúrgico ----
Write-Host ""
Write-Host "--- git add cirúrgico ---" -ForegroundColor Cyan

$toAdd = @(
    # Rodada desta sessão — CF/1988
    'raw\A-normativas\cf-1988-compilada.html',
    'raw\A-normativas\cf-1988-compilada.source.yaml',
    'inbox\cf-1988-compilada.md',

    # Rodada desta sessão — Lei 13.964/2019
    'raw\A-normativas\lei-13964-2019.html',
    'raw\A-normativas\lei-13964-2019.source.yaml',
    'inbox\lei-13964-2019.md',

    # Schema/ re-adicionados (reverter deleções perigosas do índice)
    'schema\vocabulario.yaml',
    'schema\CORPUS_HEALTH.md',
    'schema\VOCAB_HEALTH.md',
    'schema\golden_dataset.yaml',
    'schema\eval_results\.gitkeep',

    # review-queue/ re-adicionada
    'review-queue\.gitkeep',
    'review-queue\fila-A-l0-candidatos\.gitkeep',
    'review-queue\fila-B-vocab-propostas\.gitkeep',
    'review-queue\pendente-vocab\.gitkeep',

    # superados/
    'superados\.gitkeep',

    # raw/ subdiretórios (garantir que todos os .gitkeep estão versionados)
    'raw\A-normativas\.gitkeep',
    'raw\B-jurisprudencia\.gitkeep',
    'raw\C-iso\.gitkeep',
    'raw\D-resolucoes\.gitkeep',
    'raw\E-doutrina\.gitkeep',
    'raw\F-operacional\.gitkeep',
    'raw\G-proprio\.gitkeep',
    'raw\H-pecas\.gitkeep'
)

foreach ($f in $toAdd) {
    if (Test-Path $f) {
        git add $f 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  + $f" -ForegroundColor Green
        } else {
            Write-Host "  ! falha ao adicionar: $f" -ForegroundColor Red
        }
    } else {
        Write-Host "  - ausente no disco (skip): $f" -ForegroundColor Yellow
    }
}

# PLANO-INGESTAO.md fica UNSTAGED por decisão explícita — NÃO adicionamos.
# _AGENTS/AGENTS.md.pre-retrofit.bak fica como untracked — o usuário decide depois
# se move para superados/ ou mantém fora do git.

# ---- 7. relatório pré-commit ----
Write-Host ""
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "  DIFF --CACHED --STAT (o que SERÁ commitado)" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
git diff --cached --stat
Write-Host ""

Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "  git status" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
git status --short
Write-Host ""

# ---- 8. confirmação humana ----
Write-Host "Itens que permanecerão UNSTAGED (intencional):" -ForegroundColor Yellow
Write-Host "  - PLANO-INGESTAO.md  (fora de escopo nesta rodada)" -ForegroundColor Yellow
Write-Host "  - _AGENTS\AGENTS.md.pre-retrofit.bak  (decidir mover p/ superados\ separadamente)" -ForegroundColor Yellow
Write-Host ""
$resp = Read-Host "Prosseguir com o commit? (digite SIM para confirmar)"
if ($resp -ne 'SIM') {
    Write-Host "[ABORT] commit cancelado pelo usuário." -ForegroundColor Red
    Write-Host "        Estado do índice preservado. Revise git status e re-execute o script." -ForegroundColor Yellow
    exit 2
}

# ---- 9. commit ----
$commitMsg = @'
KB-PD v1.2: ingestao CF/1988 + Lei 13.964/2019 (Pacote Anticrime)

Rodada de ingestao de 2 normativas Tipo A com cadeia de custodia completa:

CF/1988 (Constituicao compilada)
  - raw/A-normativas/cf-1988-compilada.html
    sha256: 09adfaddecb8b3411141228307cc51b48d2343b3ae8639ca60df47b74b7a26e6
    bytes: 1.501.025 | bytes 0x80-0x9F: 0 | bug <u><sup>o</sup></u>: 0
  - raw/A-normativas/cf-1988-compilada.source.yaml (sidecar v1.2)
  - inbox/cf-1988-compilada.md (810KB)
    Politica editorial Onda 1: 8 dispositivos prioritarios para chunking
    (art. 5 caput/X/XII/LVI; art. 129 caput/VI; art. 145 caput/par 1)
    registrados em front-matter artigos_priorizados_onda1.

Lei 13.964/2019 (Pacote Anticrime, alteracao multipla)
  - raw/A-normativas/lei-13964-2019.html
    sha256: c3330bddf2c74c8a957745d17b45caf2f42141227d2e820a7efdd3820bd94d31
    bytes: 219.503 | bytes 0x80-0x9F: 213 (smart quotes Word)
    bug <u><sup>o</sup></u>: 3 linhas, 4 ocorrencias
  - raw/A-normativas/lei-13964-2019.source.yaml (sidecar v1.2)
  - inbox/lei-13964-2019.md (134KB)
    Last-Modified HTTP: 2021-08-06 (gestao AJ-Bolsonaro).
    Lei altera CP, CPP, LEP, L.11.340, L.12.850, L.9.296, L.12.037.

Descoberta cientifica sobre hipotese AJ-2021 (registrada em sidecar e
front-matter): bug ordinal aparece 4x no texto SANCIONADO em 24/12/2019
(gestao Moro) mas ZERO vezes no decreto de promulgacao das partes vetadas
de 29/04/2021 (gestao AJ). Isso REFUTA parcialmente a hipotese v1 que
correlacionava bug com gestao administrativa 2021, e sugere hipotese v2
centrada em processo de digitacao/origem do texto (Congresso vs Subchefia
de Assuntos Juridicos). Recomendacao registrada para Fase 1: separar
origem_do_dispositivo de ano_compilacao_html em reanalise dos 6 legados.

Etapa 0.5 (validacao blocante) aprovada em ambos:
  - sha256 match
  - iconv CP1252 -> UTF-8 sem erros
  - mojibake score 0.0000%
  - zero clusters de '?' (sem artefatos de conversao)

Re-adicionados tambem arquivos schema/, review-queue/ e superados/ que
estavam acidentalmente staged como DELETED no indice anterior (heranca
de rename fantasma .gitkeep -> .gitk em raw/B-jurisprudencia).

Proxima etapa: vocabulario v0.1 (Fase 1) antes de qualquer chunking.
'@

Write-Host ""
Write-Host "--- git commit ---" -ForegroundColor Cyan
git commit -m $commitMsg
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FATAL] git commit falhou" -ForegroundColor Red
    exit 3
}
Write-Host "[OK]   commit realizado" -ForegroundColor Green
git log -1 --oneline
Write-Host ""

# ---- 10. push opcional ----
# Descomente se quiser push automatico:
# Write-Host "--- git push ---" -ForegroundColor Cyan
# git push
# if ($LASTEXITCODE -ne 0) {
#     Write-Host "[WARN] push falhou (rede? auth?) — commit local OK" -ForegroundColor Yellow
# } else {
#     Write-Host "[OK]   push concluido" -ForegroundColor Green
# }

Write-Host ""
Write-Host "=============================================================" -ForegroundColor Green
Write-Host "  RODADA COMMITADA. Proxima etapa: vocabulario v0.1 (Fase 1)" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Green
