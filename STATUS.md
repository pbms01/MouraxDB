# STATUS.md — KB-PD (Knowledge Base de Prova Digital)

**Última atualização:** 2026-04-23 (pós-commit 2679d8b — validate_raw_05.py em produção)
**Próxima revisão sugerida:** ao estender o validador para B-jurisprudencia (schema §4.4/§4.4.1) ou ao iniciar Fase 1

> Painel de bordo do projeto. Lê em 2 minutos, orienta a retomada do trabalho após qualquer pausa. Não substitui `PLANO-INGESTAO.md` (plano completo) nem `_AGENTS/AGENTS.md` (contrato operacional) — consolida o estado atual deles.

---

## 1. Onde estamos

| Fase | Estado | Bloqueador |
|---|---|---|
| 0 — Infra + Git | ✅ concluída | — |
| 0.5 — Landing zone `raw/` + sidecar | 🟡 **em remediação (Calibração #3, 2026-04-23)** — A-normativas (10 docs): 8/10 precisam de reingest com regime LFS prospectivo (smudge filter `eol=lf` corrompeu byte-representação durante Etapa 0.5 inicial; cadeia de custódia §4.4.1 era ilusória — descoberta em 2026-04-23 pós-experimento LFS retroativo). B-jurisprudencia (2 pilotos): íntegros desde o primeiro commit (regime LFS prospectivo desde design). Validador `scripts/validate_raw_05.py` permanece em produção; rede tri-modo reinterpretada como diagnóstica (sinaliza perda de byte-representação) em vez de corretiva. | reingest A-normativas (ver `PLANO-INGESTAO.md §Reingest-2026-04-23`); depois estender validador para schema §4.4/§4.4.1 e rodar sobre `raw/B-jurisprudencia/` (2 pilotos) |
| 1 — Bootstrap do vocabulário | ⏳ pendente | desbloqueada parcialmente para A-normativas (inbox/ pode ser populado); para cobertura total (Critério 1), depende de coleta B–H |
| 2–5 | ⏳ pendentes | dependem da Fase 1 |

**Inflexão arquitetural de 2026-04-23:** a transição "protocolo declarado → protocolo aplicado" se consumou. A Etapa 0.5 saiu do plano e entrou no repositório como componente executável. O caminho crítico agora bifurca entre (a) adensar a cobertura de tipos em `raw/` para estressar o validador contra heterogeneidade, ou (b) subir para a Fase 1 (chunker + embeddings) sobre a base A já validada.

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

> **⚠ Nota (Calibração #3, 2026-04-23):** 8 dos 10 HTMLs de A-normativas tiveram byte-representação perdida pelo smudge filter (`eol=lf + text=auto`) durante a Etapa 0.5 inicial. Reingest com LFS prospectivo é operação urgente (ver §7 item 9 e `PLANO-INGESTAO.md §Reingest-2026-04-23`). `lei-12737-2012.html` e `lei-13718-2018.html` são imunes — eram LF-puros no download original.

### B-jurisprudencia (2 documentos piloto com sidecar v1.2 + extensões §4.4/§4.4.1)

| # | Documento | Órgão | Relator(a) | sha256 | Observações |
|---|---|---|---|---|---|
| 1 | HC 315.220/RS — acórdão (julgado) | STJ 6ª Turma | Maria Thereza de Assis Moura | `e85bd95c…` | Revista Eletrônica STJ; sem ICP; `fonte_confiavel: pbm_s`; via Git LFS; 58 pp |
| 2 | RE 1.301.250/RJ (Tema RG 1148) — snapshot de tramitação | STF Pleno | Edson Fachin (rel.) | `4e8b1e9a…` | Caso Google × Marielle; 7 HTMLs (pesquisa + detalhe + andamento + aba sessão + partes + recursos + despachos); coleta 2026-04-23T18-23-06Z; schema §4.4.1; via Git LFS; watchlist ativa até trânsito |

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
1. ✅ **Implementado (2026-04-23, commit 2679d8b)** — `scripts/validate_raw_05.py`:
   - Recalcula sha256 com rede de segurança tri-modo (direto → normalizado_lf → normalizado_crlf) para tolerar rodadas cross-OS.
   - Calcula mojibake score sobre bytes brutos (padrão UTF-8→Latin-1: `\xc3[\x80-\xbf]`, `\xc2[\x80-\xbf]`, `\xe2\x80[\x80-\xbf]`) com thresholds 2%/0.5%.
   - Detecta artefatos de processo (`((VERIFICAR))`, `[[notas]]`, RASCUNHO, TODO, FIXME). **XXX removido após primeira calibração empírica** — em corpus jurídico BR é sempre numeral romano (inciso XXX).
   - Emite CSV em `_AGENTS/validation-reports/YYYY-MM-DD-etapa05.csv` com status por arquivo.
2. ✅ **Rodado sobre os 10 documentos de A** — resultado: `ok=10 warning=0 blocked=0`. Todos os sha256 bateram em `modo=direto` (worktree ainda com CRLF original; `.gitattributes eol=lf` só ativará divergência em futuro reclone — fallback `normalizado_lf` validado em desenho, não em execução).
3. ⏳ **Pendente** — emitir `inbox/<id>.md` com `encoding_validated: true` (requer Etapa 1: conversão HTML→MD via iconv CP1252 + strip HTML) para então iniciar indução de vocabulário.

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

### Próxima decisão do Pedro (pós-2026-04-23)
Três caminhos abertos, por ordem de ROI estratégico:

1. **Estender `validate_raw_05.py` para Tipo B** (schema §4.4/§4.4.1 + verificação ICP + snapshot temporal) e rodar sobre os 2 pilotos já em `raw/B-jurisprudencia/`. Estresse do validador contra heterogeneidade real (PDF STJ + HTMLs STF) — primeiro bug do validador aparece aqui.
2. **Adensar raw/ com novos source_types** (C: ISO 27037; D: Res. CNJ 615; H: 2 pares dialéticos) para diversificar antes do chunker. Preserva o princípio de fidelidade: coletar largo antes de embedir.
3. **Subir para Fase 1 (chunker + embeddings)** sobre A-normativas já validado — corre o risco de re-escrever o chunker quando B-H chegarem com semânticas estruturais distintas.

Meu voto implícito: **(1) primeiro**, porque é o teste adversarial mais barato que o validador pode receber agora, e porque destravar o validador para Tipo B elimina o único bloqueador atual do piloto HC 315.220.

---

## 6. Mapa de documentos de governança

| Arquivo | Função | Última atualização |
|---|---|---|
| `_AGENTS/AGENTS.md` | Contrato operacional do pipeline; carregado em toda sessão Cowork | 2026-04-23 (+ Calibração #3: `eol=lf + text=auto` suspende fidelidade byte-a-byte em qualquer rebuild) |
| `_AGENTS/raw-protocol.md` | Schema do sidecar `.source.yaml` + fluxo de 4 etapas; extensões Tipo B em §4.4/§4.4.1/§4.5, exemplo canônico §8.2, piloto RE 1.301.250 em §8.4, lições BLOCO F-G em §8.5 | 2026-04-23 (v2.2 — §8.5 LFS para Tipo B em tramitação) |
| `_AGENTS/schema-reference.md` | Schema canônico completo (L0, L1, L2, L3) | (estável) |
| `_AGENTS/citacoes-canonicas.md` | Formatos de citação por source_type | (estável) |
| `_AGENTS/hot-articles.yaml` | Camada de priorização declarativa por domínio | 2026-04-22 (v0.2) |
| `PLANO-INGESTAO.md` | Plano completo de 5 fases | 2026-04-22 (v1.3 — extensões Tipo B) |
| `STATUS.md` | **este arquivo** — painel de bordo | 2026-04-23 (Calibração #3, item 9 refutado) |
| `scripts/validate_raw_05.py` | **Validador bloqueante da Etapa 0.5** (Python 3, stdlib-only: schema + sha256 tri-modo + mojibake + artefatos) | 2026-04-23 (commit 2679d8b — v1 A-normativas) |
| `_AGENTS/validation-reports/` | Trilha de auditoria do validador (CSV por corrida, YYYY-MM-DD-etapa05.csv) | 2026-04-23 (primeira corrida) |
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
7. **Git 2.53.0.windows.1 mantém `text:set` cosmético em check-attr mesmo com `filter=lfs ... -text`** → `git check-attr text <path>` reporta `text: set` quando deveria reportar `text: unset`, porém `binary: set` coexiste e LFS intercepta o conteúdo ANTES da text conversion. Ordem canônica de filtros: `clean filter (LFS)` → `text conversion (checkin)`. Se o OID LFS local == SHA256 disco, a cadeia forense está íntegra apesar do ruído cosmético. Regra permanente: para Tipo B em tramitação (HTMLs), forçar `filter=lfs diff=lfs merge=lfs -text` no `.gitattributes`; ignorar `text: set` em check-attr; auditar invariante `sha256(disco) == OID(LFS) == OID(origin) == re-hash(smudge clone)`. Documentado em `_AGENTS/raw-protocol.md` §8.5 e `_AGENTS/AGENTS.md` §Git LFS como camada forense.
8. **Padrões editoriais que colidem com notação jurídica (calibração empírica do validador)** → o detector de artefatos do `validate_raw_05.py` foi calibrado em 2026-04-23 removendo o padrão `XXX` após falso-positivo em `cf-1988-compilada.html` (5 ocorrências — todas incisos romanos). Em corpus jurídico brasileiro, `XXX` é sempre numeral romano (inciso XXX), nunca marca editorial. Regra metódica: antes de adicionar qualquer padrão que pareça "óbvio" (FIXME, TODO, TBD, RASCUNHO, XXX), testar contra a população real antes de aceitar o threshold — a semântica do corpus é a filtro definitivo, não a intuição do analista. Documentado em `_AGENTS/AGENTS.md` §Calibrações empíricas do validador.
9. **Fidelidade byte-a-byte em raw/A-normativas — REFUTADA em 2026-04-23 (ver Calibração #3 em `_AGENTS/AGENTS.md`)** → a predição arquitetural de que a rede tri-modo cobriria divergência cross-OS foi empiricamente refutada. O experimento `lfs-migrate-a-normativas-essay` disparou o smudge filter (`* text=auto eol=lf`, linha 9 do `.gitattributes`) que reescreveu o working tree de 8 dos 10 HTMLs, substituindo bytes mixed-CRLF originais por LF-puros. Mesmo após rollback completo do experimento (`git reset --hard origin/main`, sem LFS ativo), o validador reproduz 8/10 BLOCK com `direto == lf` — porque o próprio reset reaplica o smudge. Consequência: o baseline 10/10 OK de 2026-04-23 (commit 2679d8b) era artefato transitório do worktree local pré-rebuild, não propriedade do repositório. Qualquer clone fresco em Linux (ou em Windows com `core.autocrlf=false`) produz 8/10 BLOCK imediatamente. **A cadeia de custódia byte-a-byte declarada em sidecar v1.2 §4.4.1 para esses oito nunca viveu no repo — viveu apenas no worktree local do Pedro.** Os dois OK (`lei-12737-2012.html`, `lei-13718-2018.html`) são imunes porque eram `w/lf` já no download original. **Próxima operação:** reingest dos 10 HTMLs com pattern LFS prospectivo (ver `PLANO-INGESTAO.md §Reingest-2026-04-23`) — urgente, não opcional. Reingest é a única remediação possível; nenhuma ferramenta de history rewrite recupera bytes já consumidos pela text conversion.
10. **Fidelidade byte-a-byte em git exige abordagem prospectiva** → retroativamente nenhuma ferramenta (`lfs migrate import`, BFG, `git filter-repo`) recupera bytes originais consumidos pelo `text=auto`. Três regimes prospectivos possíveis, todos aplicados *antes* do primeiro `git add` do arquivo: (a) LFS regime via `filter=lfs ... -text`; (b) atributo `binary`; (c) `-text` ou `eol=crlf` pattern-specific. Qualquer arquivo comitado sob `* text=auto eol=lf` tem byte-representação perdida no momento do `git add` inaugural — o sidecar v1.2 §4.4.1 passa a atestar conteúdo (codepoints via fallback tri-modo) em vez de byte-representação. Regra para novas coletas: verificar `.gitattributes` antes do primeiro `git add`, confirmar que o pattern LFS/binary/`-text` está ativo para o source_type em questão. Documentado em Calibração #3.

---

*Quando este STATUS.md ficar mais de uma semana sem atualização ou divergir do estado real do `raw/` e do `_AGENTS/`, regenerar.*
