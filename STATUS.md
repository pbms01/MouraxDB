# STATUS.md — KB-PD (Knowledge Base de Prova Digital)

**Última atualização:** 2026-04-22
**Próxima revisão sugerida:** ao iniciar a próxima sessão, ou ao concluir a Etapa 0.5 propriamente dita

> Painel de bordo do projeto. Lê em 2 minutos, orienta a retomada do trabalho após qualquer pausa. Não substitui `PLANO-INGESTAO.md` (plano completo) nem `_AGENTS/AGENTS.md` (contrato operacional) — consolida o estado atual deles.

---

## 1. Onde estamos

| Fase | Estado | Bloqueador |
|---|---|---|
| 0 — Infra + Git | ✅ concluída | — |
| 0.5 — Landing zone `raw/` + sidecar | 🟡 estrutura pronta; **validação bloqueante ainda não rodada** sobre os 10 docs já depositados | precisa rodar mojibake score + sha256 match + detecção de artefatos sobre `raw/A-normativas/` |
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

### B–H (vazios)

`raw/B-jurisprudencia/`, `raw/C-iso/`, `raw/D-resolucoes/`, `raw/E-doutrina/`, `raw/F-operacional/`, `raw/G-proprio/`, `raw/H-pecas/` — todos com `.gitkeep` apenas. Nenhum documento ainda.

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

### Decisão pendente do Pedro
Qual caminho atacar primeiro? A é estritamente necessário para o bootstrap; B é o **núcleo** do bootstrap segundo o `PLANO-INGESTAO.md` (Critério 2 — Tipo H + Tipo B carregam o vocabulário mais instável).

---

## 6. Mapa de documentos de governança

| Arquivo | Função | Última atualização |
|---|---|---|
| `_AGENTS/AGENTS.md` | Contrato operacional do pipeline; carregado em toda sessão Cowork | 2026-04-22 (v3 do bug ordinal) |
| `_AGENTS/raw-protocol.md` | Schema do sidecar `.source.yaml` + fluxo de 4 etapas | (estável) |
| `_AGENTS/schema-reference.md` | Schema canônico completo (L0, L1, L2, L3) | (estável) |
| `_AGENTS/citacoes-canonicas.md` | Formatos de citação por source_type | (estável) |
| `_AGENTS/hot-articles.yaml` | Camada de priorização declarativa por domínio | 2026-04-22 (v0.2) |
| `PLANO-INGESTAO.md` | Plano completo de 5 fases | 2026-04-22 (Fase 0.5 = 10 docs) |
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

---

*Quando este STATUS.md ficar mais de uma semana sem atualização ou divergir do estado real do `raw/` e do `_AGENTS/`, regenerar.*
