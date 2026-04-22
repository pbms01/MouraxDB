# STATUS.md — KB-PD (Knowledge Base de Prova Digital)

**Última atualização:** 2026-04-22
**Próxima revisão sugerida:** ao iniciar a próxima sessão, ou ao concluir a Etapa 0.5 propriamente dita

> Painel de bordo do projeto. Lê em 2 minutos, orienta a retomada do trabalho após qualquer pausa. Não substitui `PLANO-INGESTAO.md` (plano completo) nem `_AGENTS/AGENTS.md` (contrato operacional) — consolida o estado atual deles.

---

## 1. Onde estamos

| Fase | Estado | Bloqueador |
|---|---|---|
| 0 — Infra + Git | ✅ concluída | — |
| 0.5 — Landing zone `raw/` + sidecar | 🟡 estrutura pronta; **validação bloqueante ainda não rodada** sobre os 11 docs já depositados (10 A + 1 B piloto) | precisa rodar mojibake + sha256 match + detecção de artefatos sobre `raw/A-normativas/`; para `raw/B-jurisprudencia/` adicional: schema §4.4 + verificação ICP |
| 1 — Bootstrap do vocabulário | ⏳ pendente | bloqueada pelo Critério 1 (cobertura dos 8 tipos) — só A está populado |
| 2–5 | ⏳ pendentes | dependem da Fase 1 |

**Um único gesto destrava a Fase 1 parcialmente:** rodar a Etapa 0.5 sobre os 10 documentos de A. Isso libera a indução de vocabulário inicial restrita ao corpus normativo, enquanto B–H seguem sendo coletados em paralelo.

---

## 2. Inventário atual de `raw/`

### A-normativas (10 documentos com sidecar v1.2 completo)

| # | Documento | Sanção | sha256 | Bug ordinal |
|---|---|---|---|---|
| 1 | CF/1988 compilada | Sarney/AJ-compilação atual | `09adfadd…` | 0% (limpo) |
| 2 | CP 2848/1940 compilado | Vargas/AJ-compilação atual | `224467a3…` | ~6,5% |
| 3 | CPP 3689/1941 compilado | Vargas/AJ-compilação atual | `0c8db263…` | ~30,4% |
| 4 | Lei 12.737/2012 (Carolina Dieckmann) | Dilma | retrofited | 0% |
| 5 | Lei 12.965/2014 (Marco Civil) | Dilma | retrofited | 0% |
| 6 | Lei 13.718/2018 (importunação sexual) | Toffoli interino | v1.2 nativo | 0% |
| 7 | Lei 13.964/2019 (Pacote Anticrime) | Bolsonaro/Moro | v1.2 nativo | bug presente |
| 8 | Lei 14.132/2021 (stalking) | Bolsonaro | retrofited | bug presente |
| 9 | Lei 14.155/2021 (furto/fraude eletrônica) | Bolsonaro | retrofited | bug presente |
| 10 | Lei 14.188/2021 (violência psicológica) | Bolsonaro | retrofited | bug presente |

### B-jurisprudencia (1 documento piloto com sidecar v1.2 + extensão §4.4)

| # | Documento | Órgão | Relatora | sha256 | Observações |
|---|---|---|---|---|---|
| 1 | HC 315.220/RS — acórdão | STJ 6ª Turma | Maria Thereza de Assis Moura | `e85bd95c…` | Revista Eletrônica STJ; sem ICP; `fonte_confiavel: pbm_s`; via Git LFS; 58 pp |

### C–H (vazios)

`raw/C-iso/`, `raw/D-resolucoes/`, `raw/E-doutrina/`, `raw/F-operacional/`, `raw/G-proprio/`, `raw/H-pecas/` — todos com `.gitkeep` apenas. Nenhum documento ainda.

**Próximas coletas prioritárias** (cobrem o caminho crítico do bootstrap):
- B: RE 1.055.941/SP (STF), HC 841.778/RS (STJ), ADI 6.031/RE 1.037.396 (STF) — caso de validação Critério 3c
- C: ISO/IEC 27037:2012
- D: Resolução CNJ 615/2025
- H: ≥ 2 pares dialéticos completos (inicial + contestação)

---

## 3. Hipóteses ativas

### Hipótese v3 do bug ordinal Planalto

**Estado epistêmico:** ATIVA (v1 e v2 refutadas em 2026-04-22).

**Enunciado:** a presença do `<u><sup>o</sup></u>` no lugar do U+00BA (`º`) é estratificada por bloco editorial dentro do documento. Cada inserção/alteração legislativa carrega o template em uso no momento da incorporação. Documentos compilados são fósseis estratigráficos de templates editoriais sucessivos.

**Predição operacional:** `taxa_bug ≈ f(idade_do_diploma_base × densidade_de_alteracoes_acumuladas)`.

**Lastro empírico (10 data points, 2026-04-22):**
- CPP/1941 (muitas alterações pulverizadas): 30,4% bug → confirma alta heterogeneidade.
- CP/1940 (alterações episódicas + Reforma 1984 coesa): 6,5% bug → confirma média heterogeneidade.
- CF/1988 (ECs sequenciadas e processadas em bloco): 0% bug → confirma baixa heterogeneidade.
- Leis curtas autônomas: refletem o template do momento da sanção (consistente com v3).

**Próximos testes adversariais** (qualquer um pode falsear a v3):
1. CPC compilado (Lei 13.105/2015) — predição: 1–3% bug.
2. CLT compilada (1943) — predição: > CPP (mais alta).
3. Decreto pré-2000 com poucas atualizações — predição: < 1%.
4. Diploma re-editado por DOU completo após 2024 — predição: homogeneização para template AJ atual.
5. Análise intra-CP por época de inserção (Reforma 1984 vs. arts. 2021) — predição: gradiente observável.

**Regra inalterada por todas as refutações:** o pipeline NUNCA "corrige" o ordinal — preserva byte a byte. A hipótese explicativa pode mudar (e mudou três vezes em uma semana); a regra de fidelidade, não. Detalhes em `_AGENTS/AGENTS.md` §155-200.

---

## 4. Camada de priorização declarativa

`_AGENTS/hot-articles.yaml` v0.2 (aprovada 2026-04-22) — índice de **43 artigos hot** sobre o L0 (CP 13 + CPP 19 + CF 11) + **3 hot_laws** com artigos próprios (Marco Civil 12.965/2014, Anticrime 13.964/2019, Cibernéticos 14.155/2021) + **10 pareamentos transversais** para query expansion.

**Princípio arquitetural:** L0 permanece agnóstico de domínio. Múltiplas lentes de priorização podem coexistir sem reescrita do corpus. Esta é a primeira lente — `prova_digital_e_direito_penal_digital`.

**Critério de inclusão:** A (estrito, diferencial PD) com escape válvula. Artigos meramente "frequentes" sem dimensão qualitativamente diferente em PD ficam de fora (ex: CP art. 59 dosimetria — entra no L0 por coleta integral, mas não na priorização).

---

## 5. Próximas ações concretas

### Caminho A — destravar Fase 1 parcial sobre A-normativas
1. Implementar script de Etapa 0.5 (Python ou bash):
   - Recalcular sha256 de cada `.html` e comparar com `.source.yaml`.
   - Calcular mojibake score (% de tokens com padrão UTF-8→Latin-1 corrompido).
   - Detectar artefatos de processo (`((VERIFICAR))`, `[[notas]]`, `RASCUNHO`).
   - Emitir `inbox/<id>.md` com `encoding_validated: true` para os que passarem.
2. Rodar sobre os 10 documentos de A.
3. Iniciar indução de vocabulário sobre `inbox/` validado (subset normativo).

### Caminho B — coletar B, C, D, H em paralelo
1. Baixar RE 1.055.941/SP, HC 841.778/RS e ADI 6.031 — criar sidecars manualmente (Tipo B não tem URL canônica única; cada tribunal tem layout próprio).
2. Baixar ISO/IEC 27037:2012 (acesso institucional).
3. Baixar Resolução CNJ 615/2025.
4. Selecionar 2 pares dialéticos H do acervo MPRJ (Pedro escolhe).

### Caminho C — piloto Tipo B (HC 315.220/STJ) — PARCIALMENTE CONCLUÍDO
Desbloqueado pelo `raw-protocol.md` v2 (commit 66c150f; fix cosmético do exemplo §8.2 em 6927e9a).

**Etapas concluídas em 2026-04-22 (commits 6927e9a + 3632faa):**
1. ✅ PDF depositado em `raw/B-jurisprudencia/STJ/HC-315220/hc-315220-stj.pdf` via Git LFS (58 pp, 317.856 B, sha256 `e85bd95c…`).
2. ✅ `.source.yaml` v1.2 estendido conforme §4.4 (Revista Eletrônica STJ; ICP ausente; `fonte_confiavel: pbm_s`; incerteza da URL registrada em `observacoes`).

**Etapas pendentes — bloqueadas por scripts ainda não existentes:**
3. ⏳ Rodar Etapa 0.5 (schema + SHA + verificação ICP) — bloqueada pela ausência de `scripts/validate_raw_05.py` ou equivalente. Precisa estender o validador com o schema §4.4 antes de rodar.
4. ⏳ `pdftotext -layout` + `segmenta_acordao.py` → MD em `inbox/B-jurisprudencia/STJ-HC-315220.md` com front-matter dual-layer (§4.5) — bloqueada pela ausência de `scripts/segmenta_acordao.py` (perfil STJ). Sidecar aceita `segmentador_sha: null` como bootstrap.

O piloto já validou empiricamente: (a) schema §4.4 aplicável na prática; (b) padrão hierárquico `raw/B-jurisprudencia/{TRIBUNAL}/{INSTRUMENTO-NUM}/` funciona; (c) coleta via Revista Eletrônica com `pbm_s` como âncora de confiança é viável quando ICP está ausente.

### Próxima decisão do Pedro
Dois caminhos abertos: (A) destravar Etapa 0.5 sobre A-normativas escrevendo `validate_raw_05.py`; (B) ampliar o acervo Tipo B com próximo julgado jurisprudencial (RE 1.055.941/SP, HC 841.778/RS, ou ADI 6.031). Caminho A desbloqueia a Fase 1 parcial; Caminho B adensa o corpus antes do vocabulário ser induzido.

---

## 6. Mapa de documentos de governança

| Arquivo | Função | Última atualização |
|---|---|---|
| `_AGENTS/AGENTS.md` | Contrato operacional do pipeline; carregado em toda sessão Cowork | 2026-04-22 (v3 bug ordinal + subseção PS 5.1 `git commit -m` splitting) |
| `_AGENTS/raw-protocol.md` | Schema do sidecar `.source.yaml` + fluxo de 4 etapas; extensões Tipo B em §4.4/§4.5, exemplo canônico §8.2 | 2026-04-22 (v2.1 — commits 66c150f + 6927e9a fix metadados §8.2) |
| `_AGENTS/schema-reference.md` | Schema canônico completo (L0, L1, L2, L3) | (estável) |
| `_AGENTS/citacoes-canonicas.md` | Formatos de citação por source_type | (estável) |
| `_AGENTS/hot-articles.yaml` | Camada de priorização declarativa por domínio | 2026-04-22 (v0.2) |
| `PLANO-INGESTAO.md` | Plano completo de 5 fases | 2026-04-22 (v1.3 — extensões Tipo B) |
| `STATUS.md` | **este arquivo** — painel de bordo | 2026-04-22 |
| `schema/vocabulario.yaml` | Vocabulário controlado | aguardando Fase 1 |
| `schema/golden_dataset.yaml` | Pares query-resposta para RAGAS | aguardando Fase 3 |

---

## 7. Limitações operacionais conhecidas (cookbook)

Salvar tempo na próxima sessão evitando armadilhas já mapeadas:

1. **Write/Edit truncam arquivos > ~500B com acentuação** → usar `cat << 'EOF'` em bash. Verificar com `wc -c` após escrita.
2. **Git no sandbox via mount Linux mostra estado falso** → todos os comandos `git status/add/commit` rodam no PowerShell nativo, não no `mcp__workspace__bash`.
3. **PowerShell 5.1 + `$ErrorActionPreference = 'Stop'` promove warnings de Git a erros fatais** → padrão canônico `$null = & git ... 2>&1` + check de `$LASTEXITCODE`. Documentado em `_AGENTS/AGENTS.md`.
4. **Encoding Planalto é WINDOWS-1252, não ISO-8859-1** → sempre `iconv -f WINDOWS-1252` na Etapa 1, mesmo quando o meta diz outra coisa. Validado empiricamente em 10 documentos.
5. **User-Agent matters para o Planalto** — historicamente requeria Mozilla; a coleta de CP/CPP em 2026-04-22 confirmou que User-Agent não-browser também é aceito (atualização registrada nos sidecars). Documentar como flutuação operacional.
6. **`git commit -m $msg` no PowerShell 5.1 fragmenta mensagens com `-`, `(`, `)`, `->` ou travessão** → parser de comandos nativos interpreta esses caracteres como separadores de argumento; erro típico enganoso `fatal: pathspec '15' did not match...`. Padrão canônico: `git commit -F <tempfile>` com `[System.IO.File]::WriteAllText(..., UTF8Encoding $false)`. Documentado em `_AGENTS/AGENTS.md` §Warnings Git.

---

*Quando este STATUS.md ficar mais de uma semana sem atualização ou divergir do estado real do `raw/` e do `_AGENTS/`, regenerar.*
