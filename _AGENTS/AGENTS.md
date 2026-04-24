# KB-PD AGENTS.md — Instruções para Cowork
# Este arquivo é carregado automaticamente em toda sessão Cowork nesta pasta.
# Não remover. Não renomear. Versionar no Git.
## IDENTIDADE DO PROJETO
Knowledge base especializada em prova digital e direito digital brasileiro.
Pipeline RAG com destilação hierárquica: L0 (atômico) → L1 → L2 → L3.
Rastreabilidade até fonte primária é requisito de primeira classe — não metadado opcional.
Vocabulário controlado em schema\vocabulario.yaml — carregar em toda sessão como contexto permanente.
## TIPOS DE FONTE (source_type)
A: normativas brasileiras — chunking por artigo/inciso/alínea, autoridade: vinculante
B: jurisprudência — **julgado transitado**: 3 L0s obrigatórios por acórdão (ementa + holding + ratio) + 1 opcional (voto divergente), autoridade: vinculante ou persuasivo. **Em tramitação**: snapshot temporal HTML, sem L0 até trânsito em julgado; governança em watchlist\README.md, schema em _AGENTS\raw-protocol.md §4.4.1
C: normas técnicas ISO/NIST — chunking por requisito prescritivo (shall/deve), autoridade: persuasivo
D: resoluções CNJ/CNMP/portarias — chunking por dispositivo, autoridade: vinculante no âmbito
E: doutrina — atribuição de autor obrigatória no L0, autoridade: persuasivo
F: operacional/ferramental — campos versao_ferramenta + data_verificacao + ciclo_revisao_meses obrigatórios, autoridade: exemplificativo
G: conhecimento próprio — confiança rebaixada para 'media' HARDCODED (não negociável), revisão humana obrigatória sem exceção
H: peças processuais — unidade de valor é padrão argumentativo, campos par_dialetico_id e polo obrigatórios
## PIPELINE DE INGESTÃO — 4 ESTÁGIOS (v1.2)
Todo documento atravessa: raw/ → (Etapa 0.5) → inbox/ → (Etapa 2) → corpus/.
- Etapa 0: depósito em raw\<tipo>\ com sidecar .source.yaml obrigatório (schema em _AGENTS\raw-protocol.md §4). Sidecar sem sha256 só para legado pré-v1.2.
- Etapa 0.5: validação bloqueante de encoding + hash + artefatos (detalhada abaixo).
- Etapa 1: conversão canônica conforme campo conversao_prevista do sidecar (HTML→MD via iconv CP1252, PDF→MD via pdftotext, JSON→MD via parser, etc.). Produto: inbox\<id>.md com front-matter completo (schema-reference.md §5).
- Etapa 2: chunking atômico por artigo/cláusula. Produto: corpus\<tipo>\<id>\<chunk>.md (L0 canônico).
Fluxo detalhado e exemplos: _AGENTS\raw-protocol.md §7.

## ETAPA 0.5 — PRÉ-CONDIÇÃO BLOQUEANTE (executa em TODO documento, sem exceção)
**Implementação de referência: `scripts/validate_raw_05.py`** (commit 2679d8b, 2026-04-23 — v1 A-normativas).
Python 3, stdlib-only. 4 checks obrigatórios por documento; qualquer `blocked` aborta a avanço para inbox/.

1. **Schema do sidecar** (`check_sidecar_schema`): valida presença dos 9 campos obrigatórios v1.2 (arquivo, tipo, url_origem, baixado_em, baixado_por, sha256, encoding_real_detectado, conversao_prevista, idioma). Extensões §4.4/§4.4.1/§4.5 são opcionais e não bloqueiam; validador atual v1 ainda não verifica §4.4 (Tipo B) — pendente.
2. **Conferência de integridade sha256** (`check_sha256`): recalcula em 3 modos com fallback cross-OS:
   - **modo=direto**: `sha256(bytes do arquivo)` — match esperado quando worktree preserva encoding original (CRLF do Planalto).
   - **modo=normalizado_lf**: `sha256(bytes com CRLF→LF)` — match esperado após reclone com `.gitattributes eol=lf` ativo.
   - **modo=normalizado_crlf**: `sha256(bytes com LF→CRLF)` — fallback inverso (worktree Unix após commit a partir de Windows).
   - Mismatch nos 3 modos → `blocked`.
3. **Mojibake score** (`check_mojibake`): regex binária detecta padrões UTF-8→Latin-1 sobre bytes brutos:
   - `\xc3[\x80-\xbf]` (Ã-til + byte), `\xc2[\x80-\xbf]` (Â-circ + byte), `\xe2\x80[\x80-\xbf]` (â€ + byte).
   - Score > 2% → `blocked` + quarantine\encoding-artifacts\ + encoding_validated: false.
   - Score 0.5–2% → `warning` + revisão manual recomendada.
   - Score < 0.5% → encoding_validated: true, prossegue.
4. **Artefatos de processo** (`check_artifacts`): regex textual sobre UTF-8 decodificado:
   - Padrões ativos: `((VERIFICAR))`, `[[...]]`, RASCUNHO, TODO, FIXME.
   - Padrões removidos por calibração empírica: **XXX** (ver §Calibrações empíricas do validador abaixo).
   - Qualquer match → `blocked` + lista de ocorrências no CSV.
5. Relatório: `_AGENTS/validation-reports/YYYY-MM-DD-etapa05.csv` (14 colunas; trilha de auditoria versionada).
6. Documento só avança com `status=ok` ou `status=warning` + revisão humana explícita.
7. PROIBIDO limpeza automatizada — risco de remoção de conteúdo legítimo em texto jurídico.
## REGRAS ABSOLUTAS
1. NUNCA sobrescrever L0: correções criam nova versão; anterior → superados\ + status: superado + valido_ate preenchido
2. NUNCA ingerir output da própria KB como Tipo G (loop de contaminação)
3. Tipo G: confiança_extracao NUNCA é 'alta' — sempre 'media', hardcoded, sem exceção
4. Tipo B: yield mínimo = 3 L0s por acórdão; se < 3 → Fila A com flag yield_incompleto: true
5. Vocabulário: verificar near-duplicates antes de propor termo novo; sim > 0.85 = substituição automática pelo existente
6. Toda saída com claim jurídico cita o L0 de suporte no formato [L0:id]
7. Tipo A com histórico legislativo inline: separar redações em chunks distintos antes de qualquer embedding
## FILAS DE REVISÃO (ordem obrigatória)
- Fila B (vocabulário) SEMPRE antes da Fila A (L0 candidatos)
- L0s com pendente_vocab não são commitados até Fila B ser resolvida
- Obrigatório para Fila A: confiança baixa | CONTRADIZ | source_type G | yield_incompleto
- Semi-automático permitido: confiança alta + status NOVO ou ATUALIZA
## AUTORIDADE EPISTÊMICA
vinculante > persuasivo > exemplificativo > proprio
Tensões entre autoridades incompatíveis: preencher campo tensoes no L2 — nunca silenciar.
## NOTAS TÉCNICAS DE OPERAÇÃO
### Escrita de arquivos grandes com acentuação (Windows)
A tool Write falha silenciosamente por truncagem de buffer em arquivos com:
- Tamanho > ~500 bytes, E
- Conteúdo com caracteres acentuados (UTF-8 multibyte: ã, ç, ê, etc.)
Sintoma: arquivo criado com 100–200 bytes em vez do tamanho esperado, cortado no meio de uma palavra acentuada.
Solução obrigatória para arquivos de conteúdo jurídico: usar bash com heredoc de aspas simples:
  cat << 'NOME_EOF' > caminho\arquivo.ext
  [conteúdo]
  NOME_EOF
As aspas simples em 'NOME_EOF' suprimem expansão de variáveis — obrigatório quando o conteúdo
contém $, \, backticks ou qualquer marcação que bash interprete como expansão.
Após escrita: verificar tamanho com wc -c e confirmar que bate com o esperado antes de prosseguir.
Aplicável a: todos os arquivos .md, .yaml e .txt do pipeline com conteúdo jurídico em português.
### Warnings do Git em scripts PowerShell com ErrorActionPreference = Stop
**Política aplicada em todos os scripts .ps1 do pipeline KB-PD.**
Em PowerShell 5.1 com `$ErrorActionPreference = 'Stop'`, mensagens informativas do Git emitidas em stderr (não-fatais por natureza — ex.: "warning: in the working copy of 'X', CRLF will be replaced by LF the next time Git touches it") são promovidas a exceção bloqueante quando capturadas via o pipeline redirect padrão:

```powershell
git add $f 2>&1 | Out-Null    # ← PADRÃO BUGADO
```

O mecanismo: `2>&1` mistura stderr com stdout; PowerShell então inspeciona cada objeto do stream e, ao encontrar um ErrorRecord derivado de uma linha em stderr, dispara terminating error sob Stop. O warning do core.autocrlf vira RuntimeException e o script aborta sem ter executado a operação pretendida (ou tendo executado só parcialmente).

Sintoma observado: `commit-rodada-cf-lei13964.ps1` (2026-04-22) abortou após stagar apenas 1 dos 24 paths previstos. Erro reportado como "git: The term 'add' is not recognized..." ou "ParameterBindingException" — mensagens enganosas que sugerem git ausente do PATH ou argumento malformado, quando a causa real é o warning de CRLF sendo promovido a erro terminal.

Regra permanente (padrão canônico para qualquer invocação de git em .ps1 sob Stop):

```powershell
$null = & git add $f 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "git add $f falhou (exit $LASTEXITCODE)"
    exit $LASTEXITCODE
}
```

Três componentes essenciais e não substituíveis:
1. **`& git ...`** (call operator) em vez de `git ...` direto — isola o invocation do parser PowerShell, impedindo que um ErrorRecord de stderr seja promovido antes do redirect tomar efeito.
2. **`$null = ... 2>&1`** em vez de `... 2>&1 | Out-Null` — a atribuição a `$null` consome o stream inteiro como um array de objetos silenciosos; o pipe para Out-Null mantém o stream "vivo" e é justamente nesse trânsito que Stop intercepta o ErrorRecord.
3. **Check explícito de `$LASTEXITCODE`** — o único sinal confiável de falha real do Git. Warnings legítimos (CRLF, trailing whitespace, filename case) têm exit 0; erros reais têm exit != 0.

Validado empiricamente no retrofit de `commit-rodada-cf-lei13964.ps1` (2026-04-22): com o padrão canônico aplicado a todos os 24 `git add`, o staging completou sem aborto e os warnings de CRLF passaram a ser ignorados como ruído informativo esperado (o repositório KB-PD armazena com autocrlf=true em Windows, portanto CRLF→LF no objeto é comportamento correto, não falha).

Aplicável a: todos os scripts .ps1 que invocam git add/commit/push/rm no pipeline (commit-rodada-*.ps1, reingest-*.ps1, retrofit-*.ps1). NUNCA usar `git ... 2>&1 | Out-Null` em PS 5.1 com Stop — mesmo que pareça funcionar no primeiro arquivo, quebrará no primeiro warning.
### Mensagens de commit em PowerShell 5.1 -- argument splitting com `git commit -m`
**Política aplicada em todos os scripts .ps1 do pipeline KB-PD.**

Em PowerShell 5.1, passar mensagem estruturada diretamente via `-m $msg` é instável quando a mensagem contém hífen (`-`), parênteses (`(` `)`), setas (`->`) ou travessão. Esses caracteres são interpretados pelo parser de comandos nativos do PS como separadores de argumento, fragmentando a string antes de chegar ao git.

```powershell
git commit -m $msg    # PADRÃO BUGADO quando $msg tem -, (, ), ->, travessão
```

Sintoma observado em 2026-04-22 no commit da Fase 1 do fix de `raw-protocol.md` item 8.2: mensagem contendo `HC-315220`, `(pbm_s)` e travessão quebrou com erro enganoso:

```
fatal: pathspec '15' did not match any file(s) known to git
```

O número 15 veio de fragmento de `HC-315220` interpretado como pathspec posicional. Pior: o `throw` dentro do script não abortou a pipeline e o script imprimiu `[OK] Fase 1 commitada` enquanto o commit nunca entrou no histórico -- confirmado via `git log` subsequente.

Regra permanente (padrão canônico para qualquer `git commit` estruturado em .ps1):

```powershell
# 1. Escreve mensagem em arquivo temporário -- UTF-8 SEM BOM
$msgFile = Join-Path $env:TEMP "gitmsg-$(Get-Random).txt"
[System.IO.File]::WriteAllText($msgFile, $msg, [System.Text.UTF8Encoding]::new($false))

# 2. Commit por arquivo -- imune a argument splitting
$null = & git commit -F $msgFile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "git commit falhou (exit $LASTEXITCODE)"
    exit $LASTEXITCODE
}

# 3. Limpa temp
Remove-Item $msgFile -Force
```

Três componentes essenciais:
1. **`git commit -F <path>`** em vez de `-m $msg` -- o path é string ASCII segura (do `$env:TEMP`), não sofre splitting. O conteúdo da mensagem fica blindado dentro do arquivo.
2. **`[System.IO.File]::WriteAllText(..., [System.Text.UTF8Encoding]::new($false))`** -- garante UTF-8 **sem BOM**. `Set-Content -Encoding UTF8` do PS 5.1 emite BOM, e git interpreta BOM como parte da mensagem (caracteres invisíveis no `git log`).
3. **Check explícito de `$LASTEXITCODE`** -- o `throw` pode não propagar corretamente sob `ErrorActionPreference = Stop` combinado com subshell via `& git`. O check é a única forma confiável de detectar falha real.

Profilaxia adicional: evitar caracteres tipográficos (seção, seta, travessão, aspas curvas) em mensagens de commit sempre que possível -- trocar por ASCII equivalentes. Reduz superfície de problema mesmo com `-F` aplicado e preserva legibilidade em terminais sem UTF-8 completo.

Validado empiricamente na recuperação do commit `6927e9a` em 2026-04-22: após migrar para o padrão `-F tempfile`, a mensagem estruturada completou sem fragmentação.

Aplicável a: todos os scripts .ps1 que invocam `git commit` com mensagem contendo os caracteres problemáticos listados. NUNCA usar `git commit -m $msg` em PS 5.1 quando `$msg` pode conter esses caracteres.

### Git LFS como camada forense em git 2.53.0.windows.1
**Política aplicada em `raw/B-jurisprudencia/**/*.html` (Tipo B em tramitação).**

Snapshots HTML de tribunais brasileiros declaram `sha256(bytes_HTTP_originais)` no sidecar §4.4.1 — invariante byte-a-byte sobre o que o portal serviu no instante da coleta. Armazená-los como blob git textual expõe a cadeia de custódia à normalização CRLF↔LF do `core.autocrlf`, que corrompe silenciosamente o hash em clone cross-OS. A solução canônica é migrá-los para Git LFS:

```
# .gitattributes
raw/B-jurisprudencia/**/*.html  filter=lfs diff=lfs merge=lfs -text
```

Quatro propriedades críticas: (1) `filter=lfs` — o OID LFS coincide com o SHA-256 dos bytes originais (alinha com a declaração do sidecar §4.4.1); (2) `diff=lfs` + `merge=lfs` — elimina ruído textual em operações git; (3) `-text` — desliga a text conversion CRLF↔LF; (4) pattern específico — não afeta outros HTMLs do repo (A-normativas, documentação, exemplos).

**Descoberta secundária — `text:set` cosmético em git 2.53.0.windows.1:** `git check-attr text <path>` reporta `text: set` mesmo com `-text` declarado no `.gitattributes`, desde que coexista com `binary: set`. Isso é **cosmético** quando `filter=lfs` está ativo. Ordem canônica dos filtros git:

```
working-tree --[clean filter (LFS)]--> blob --[text conversion (checkin)]--> pack
```

O LFS intercepta o conteúdo **antes** do estágio de text conversion, e o blob que chega à text conversion já é um pointer de ~130 bytes ASCII puro (imune a CRLF↔LF por construção). Ao auditar a cadeia forense, ignorar o valor de `text` em `check-attr`; o único teste que importa é a invariante:

```
sha256(disco) == OID(LFS_local) == OID(LFS_origin) == sha256(arquivo_pós-smudge_em_clone_fresh)
```

Validação empírica em 2026-04-23 no piloto RE 1.301.250 (BLOCO G.6): 7/7 HTMLs com `$H0` idêntico em 6 posições da travessia (coleta HTTP → disco origem → LFS local clean → push → origin → pull/clone fresh + smudge). Nenhuma divergência.

Aplicável a qualquer tipo text-like cujo formato carregue invariante byte-a-byte declarada em sidecar (XML de listas de autuações, JSON de DataLake Codex do CNJ em cenários forenses). Decisão LFS vs. text guiada por: *"a cadeia declara hash sobre bytes específicos que o git poderia reescrever sem aviso?"* — se sim, LFS + `-text`; se não, text stream normal.

Detalhes completos e checklist em `_AGENTS/raw-protocol.md` §8.5.

### Encoding de atos normativos do Planalto (planalto.gov.br)
**Política aplicada na Etapa 1 do pipeline** (conversão raw/ → inbox/).
O portal Planalto serve HTML em Windows-1252 (CP1252), não ISO-8859-1.
A diferença é crítica: bytes 0x80–0x9F existem no CP1252 mas não no Latin-1.
Caracteres afetados: aspas tipográficas "" (0x93/0x94), en-dash – (0x96),
elipse … (0x85). Com -f ISO-8859-1 esses bytes são convertidos silenciosamente
para símbolos incorretos sem abortar — perda invisível e sem flag de erro.
Regra permanente: usar SEMPRE iconv -f WINDOWS-1252 -t UTF-8 para qualquer
ato do Planalto, independentemente do que o meta charset declare.
Registrar no sidecar .source.yaml: encoding_declarado_http: "ISO-8859-1"
(o que o HTTP/meta diz) e encoding_real_detectado: "WINDOWS-1252" (o que
file/chardet confirma). A divergência dos dois campos é parte da cadeia
de custódia da conversão.
Validado empiricamente em 6 leis com lastro byte-a-byte pelo pipeline v1.2 (o retrofit de 2026-04-22 fechou a cadeia de custódia das 3 legadas 12.737/2012, 14.155/2021 e 12.965/2014 — antes com sha256:null — e as integrou ao padrão v1.2 das 3 já nativas):

| Lei | Gestão (sanção) | Tamanho (B) | Bytes 0x80–0x9F | Distribuição |
|---|---|---|---|---|
| 12.737/2012 (Carolina Dieckmann) | Dilma | 11.916 | 8 | 0x93×4 + 0x94×4 (aspas tipográficas) |
| 12.965/2014 (Marco Civil) | Dilma | 119.976 | 0 | — (file(1) classifica como ISO-8859 text) |
| 13.718/2018 (importunação sexual) | Toffoli interino | 21.142 | 0 | — |
| 14.132/2021 (stalking) | Bolsonaro | 14.333 | 6 | aspas tipográficas |
| 14.155/2021 (furto/fraude eletrônica) | Bolsonaro | 20.916 | 12 | 0x93×4 + 0x94×4 + 0x96×4 (inclui en-dash) |
| 14.188/2021 (violência psicológica) | Bolsonaro | 18.263 | registrado no sidecar | — |

Observação operacional: 12.965/2014 e 13.718/2018 têm ZERO bytes 0x80–0x9F — decodificariam sem corrupção sob iconv Latin-1. Mesmo assim a política v1.2 é sempre `iconv -f WINDOWS-1252`, por consistência de procedimento (elimina classe inteira de regressões quando um arquivo ambíguo aparecer no futuro).
Aplicável a: CP, CPP, leis ordinárias, medidas provisórias, decretos do Planalto.
Se o arquivo inteiro precisar ser reescrito via heredoc por causa do risco de
truncagem, reescrever preservando todas as seções existentes. Verificar com
wc -c antes e depois — o arquivo deve crescer, nunca diminuir.
### Fidelidade a artefatos do Planalto (ordinais, duplicações, erros de digitação)
O Planalto apresenta ordinais do fecho de lei de duas formas distintas.
Inicialmente hipotetizou-se que a variação correlacionasse com a gestão
administrativa da Subchefia para Assuntos Jurídicos (AJ) em cada período.
- Forma correta (caractere U+00BA masculine ordinal indicator): "197º", "130º"
- Forma com bug (HTML `<u><sup>o</sup></u>` sem o caractere º real): "200o", "133o"

**Hipótese v1 (formulada 2026-04-22, REFUTADA 2026-04-22):**
"Bug introduzido no template do Planalto em 2021 (AJ-2021, gestão Bolsonaro)".
Base empírica inicial: 6/6 data points consistentes (12.737/2012 Dilma, 12.965/2014 Dilma, 13.718/2018 Toffoli interino — os três sem bug; 14.132/2021, 14.155/2021, 14.188/2021 Bolsonaro — os três com bug). A correlação ano≥2021 ⇔ bug-presente parecia limpa.

**Refutação da v1 (rodada CF + Lei 13.964/2019, 2026-04-22):**
A rodada de ingestão que adicionou a CF/1988 compilada e a Lei 13.964/2019 (Pacote Anticrime, sanção Bolsonaro via Moro, 24/12/2019) produziu dois contraexemplos, um deles decisivo:

- **Lei 13.964/2019** — sanção em 2019 (Bolsonaro PRÉ-AJ-2021), bug PRESENTE no HTML do Planalto. Isso falseia diretamente a v1, que previa bug ausente em qualquer lei pré-2021.
- **CF/1988 compilada** — artefato cuja última atualização no Planalto se deu em gestão posterior a 2021 (portanto sob suposta AJ-2021), bug AUSENTE. Isso falseia v1 pela direção oposta: a gestão AJ-2021 produz artefato limpo quando opera sobre compilação de texto constitucional.

Tabela empírica consolidada (10 data points, 2026-04-22 pós-rodada Trindade Normativa):

| Artefato | Gestão (sanção/compilação) | Ano sanção | Ratio bugados / corretos | Taxa bug |
|---|---|---|---|---|
| 12.737/2012 (Carolina Dieckmann) | Dilma | 2012 | 0 / poucos | 0% |
| 12.965/2014 (Marco Civil) | Dilma | 2014 | 0 / poucos | 0% |
| 13.718/2018 (importunação sexual) | Toffoli interino | 2018 | 0 / poucos | 0% |
| 13.964/2019 (Pacote Anticrime) | Bolsonaro/Moro | 2019 | bug presente em fecho | — |
| CF/1988 compilada | Planalto AJ (compilação pós-2021) | 1988/atual | 0 / muitos | 0% |
| 14.132/2021 (stalking) | Bolsonaro | 2021 | bug presente | — |
| 14.155/2021 (furto/fraude eletrônica) | Bolsonaro | 2021 | bug presente | — |
| 14.188/2021 (violência psicológica) | Bolsonaro | 2021 | bug presente | — |
| **CP 2848/1940 compilado** | **Vargas/AJ-compilação atual** | **1940/atual** | **105 / 1500** | **~6,5%** |
| **CPP 3689/1941 compilado** | **Vargas/AJ-compilação atual** | **1941/atual** | **510 / 1165** | **~30,4%** |

CP e CPP são contraexemplos DECISIVOS contra a v2: são compilações editadas pela própria Subchefia AJ (mesma origem editorial atribuída à CF/1988 limpa) e ainda assim apresentam o bug — mais que isso, **coexistem** as duas formas dentro do MESMO documento, em ratios não-triviais (6,5% e 30,4% respectivamente).

**Hipótese v2 (formulada e REFUTADA em 2026-04-22):**
"A variável determinante é `origem_do_dispositivo` (ramo editorial) — atos sancionados em gabinete presidencial de período Bolsonaro têm template bugado; compilações AJ têm template limpo."

**Refutação da v2 (rodada Trindade Normativa, 2026-04-22):**
A coleta de CP, CPP e CF na mesma rodada produziu três data points que falseiam a v2 simultaneamente:
- **CP/1940 compilado**: editoração AJ atual, mas tem ~6,5% de ordinais bugados.
- **CPP/1941 compilado**: editoração AJ atual, mas tem ~30,4% de ordinais bugados.
- **CF/1988 compilado**: editoração AJ atual, sem bug.

Se `ramo_editorial = AJ-compilação` determinasse `template = limpo`, os três deveriam estar limpos. A coexistência interna no CP e no CPP refuta a predição de que cada artefato tem UM template — há dois templates convivendo no mesmo arquivo.

**Hipótese v3 (formulada 2026-04-22):**
A presença do bug NÃO é binária por documento — é **estratificada por bloco editorial dentro do documento**. Cada inserção/alteração legislativa subsequente carrega o template em uso no momento da sua incorporação ao texto consolidado. O documento compilado é, portanto, um "fóssil estratigráfico" de templates editoriais sucessivos.

A taxa de bug em um documento compilado seria função aproximada de:

  taxa_bug ≈ f(idade_do_diploma_base × densidade_de_alteracoes_acumuladas)

Predições da v3:
1. Documentos compilados antigos com muitas alterações pulverizadas devem ter alta heterogeneidade interna (CPP confirma: 1941, alterado dezenas de vezes desde Lei 13.964/2019, 30,4% bug).
2. Documentos compilados antigos com alterações mais episódicas e estruturadas devem ter heterogeneidade média (CP confirma: 1940, mas com Reforma da Parte Geral 1984 como bloco coeso, 6,5% bug).
3. Documentos compilados modernos cujas alterações se dão por instrumentos editorialmente uniformes (Emendas Constitucionais sequenciadas e processadas em bloco) devem ter heterogeneidade baixa ou nula (CF confirma: 1988 + ECs numeradas, 0%).
4. Leis curtas autônomas (não compiladas, sem incorporação de alterações posteriores) devem refletir homogeneamente o template do momento da sanção (Dilma 2012/2014, Toffoli 2018, Bolsonaro 2019/2021 — todas confirmam dentro da sua época).

**Alvos de falseamento da v3 (rodadas futuras):**
1. Lei 13.105/2015 (CPC) compilado — diploma intermediário, várias alterações desde 2015. v3 prevê heterogeneidade ENTRE 0% e 6,5% (provavelmente 1–3%). Se aparecer sem bug ou com bug muito alto (>10%), v3 enfraquece.
2. CLT compilada (1943, com milhares de alterações ao longo de oito décadas) — v3 prevê heterogeneidade ALTA, possivelmente acima do CPP. Se vier sem bug ou com taxa muito baixa, refuta.
3. Decreto compilado pré-2000 que tenha sofrido apenas uma ou duas atualizações — v3 prevê heterogeneidade muito baixa. Se vier alta, refuta.
4. Republicação integral de qualquer diploma após 2024 (DOU re-edição completa, não emenda incremental) — v3 prevê homogeneização para o template AJ corrente. Se a heterogeneidade persistir, refuta.
5. Comparação intra-CP por época de inserção do dispositivo — se a Reforma 1984 (Parte Geral) tiver taxa diferente dos artigos de 2021 (147-A, 147-B), v3 ganha resolução estratigráfica direta. Análise pendente.

**Status epistêmico atual (2026-04-22):**
- v1 (ano≥2021 ⇔ bug) — REFUTADA.
- v2 (ramo editorial determina template) — REFUTADA.
- v3 (estratificação por bloco editorial; ratio cresce com idade × alterações) — ATIVA, com 10 data points consistentes mas pendente de testes adversariais (alvos 1–5 acima).

A v3 é mais frágil que v1/v2 no sentido de ser uma predição contínua (taxa esperada) ao invés de binária (bug presente/ausente), o que torna o falseamento mais delicado — uma rodada futura precisa medir a taxa exata e comparar com a faixa prevista, não só "tem bug ou não".

Regra do pipeline (inalterada por todas as refutações): o extrator NUNCA "corrige" a forma ordinal — preserva exatamente como veio do HTML. Duplicações de artigo (ex: Marco Civil art. 12 duplicado por MP 1.068/2021 rejeitada), erros de digitação oficiais e qualquer outra "anomalia" do Planalto também são preservados byte a byte na Etapa 1. A política de fidelidade está acima da política de limpeza: qualquer correção é decisão humana editorial a ser feita em etapa posterior, nunca no pipeline automatizado. A hipótese explicativa pode mudar — e mudou três vezes em uma única semana; a regra de preservação, não.

### Calibrações empíricas do validador (Etapa 0.5)
**Política aplicada em `scripts/validate_raw_05.py`**. Registro imutável das decisões de calibração feitas a partir de dados da população real — cada calibração nasce de uma rodada do validador sobre `raw/` e responde à pergunta "este padrão distingue artefato de processo de conteúdo legítimo neste corpus?". Se a resposta for não, o padrão sai; se o threshold não for robusto, o threshold muda. Calibrações não são opiniões do analista — são epistemologia aplicada ao detector.

**Calibração #1 — Remoção do padrão `XXX` (2026-04-23, commit 2679d8b).**

Primeira corrida de `validate_raw_05.py` sobre `raw/A-normativas/` em 2026-04-23 bloqueou `cf-1988-compilada.html` com 5 ocorrências de "marca XXX". Inspeção manual das linhas ofensoras:

```
Art. 5º, inciso XXX - é assegurado o direito de herança
Art. 7º, inciso XXX - proibição de diferença de salários
Art. 37, inciso XXX - (revogado)
(e 2 outras ocorrências em incisos constitucionais)
```

Todas as 5 ocorrências eram numerais romanos legítimos — nunca marcas editoriais. Em corpus jurídico brasileiro, o contexto de `XXX` é estruturalmente diferente do contexto em código-fonte/documentação técnica anglófona (onde `XXX` é marca pejorativa de código problemático). Aqui, `XXX = 30` no sistema romano, e aparece como inciso em leis longas.

Tentativa intermediária descartada: lookbehind/lookahead `(?<![IVXLCDM])XXX(?![IVXLCDM])` para exigir que XXX NÃO esteja cercado de outros caracteres romanos. Falhou empiricamente — em textos normativos, incisos vêm cercados de vírgulas, hífens, espaços e parênteses, não de outros algarismos romanos. O lookaround estava errado sobre o ambiente morfológico do corpus.

Decisão adotada: remoção integral do padrão `XXX` do detector de artefatos, com comentário inline no código explicitando o motivo (para que futuros editores do validador não o reintroduzam "ingenuamente"). Trade-off aceito: se no futuro algum documento vier com marca editorial "XXX" literal (analista que esqueceu de substituir), o validador não captura — mas esse é um falso-negativo tolerável dado o custo do falso-positivo sistêmico em cada lei/código constitucional que contenha incisos numerados até 30+.

**Regra metódica que emergiu desta calibração:** antes de adicionar qualquer padrão de artefato editorial que pareça "óbvio" (FIXME, TODO, TBD, RASCUNHO, XXX, HACK, NOTE), testá-lo contra a população real de `raw/` ANTES de aceitar o threshold. A semântica do corpus é o filtro definitivo, não a intuição do analista treinado em outro domínio. Padrões importados de code review, QA de software ou revisão editorial anglófona precisam de validação cruzada contra o gênero textual brasileiro-jurídico.

**Calibração #2 — sha256 `modo=direto` em 10/10 na primeira rodada Windows-nativa (2026-04-23, commit 2679d8b, observação empírica).**

Não é remoção de regra, é confirmação de predição arquitetural. A rede de segurança tri-modo (`direto` → `normalizado_lf` → `normalizado_crlf`) foi projetada antecipando divergência CRLF↔LF em rodadas cross-OS. Na primeira rodada, 10/10 sidecars bateram em `modo=direto`, indicando que o worktree Windows-nativo preservou o CRLF original do download Planalto mesmo com `.gitattributes eol=lf` ativo — porque os arquivos nunca foram re-checkoutados após a regra entrar em vigor.

Predição testável: em futuro `git clone` fresco da máquina, o checkout produzirá LF e o sha256 direto divergirá. O fallback `modo=normalizado_lf` entrará em ação e será essa a corrida que valida empiricamente a arquitetura tri-modo. Se 10/10 caírem em `normalizado_lf` após reclone, a rede de segurança está confirmada; se qualquer um cair em `normalizado_crlf` ou falhar nos três, há hipótese não coberta.

Registro como lastro: a arquitetura atual funciona em Windows-origem sem precisar do fallback. Não é evidência de que o fallback é desnecessário — é evidência de que a primeira máquina não exercitou a hipótese que o fallback existe para cobrir. Validar em próxima máquina antes de declarar o desenho completo.

**Calibração #3 — `eol=lf + text=auto` suspende fidelidade byte-a-byte em qualquer rebuild; rede tri-modo não recupera bytes originalmente mixed-CRLF (2026-04-23, pós-experimento `lfs-migrate-a-normativas-essay`).**

Esta calibração refuta a Calibração #2. O que lá era "confirmação de predição arquitetural" (rede de segurança tri-modo projetada para cobrir divergência CRLF↔LF em rodadas cross-OS) se revelou artefato do working tree local pré-rebuild, não propriedade do repo. O baseline 10/10 OK em `modo=direto` nunca foi uma propriedade estável — foi um fotograma do estado transitório de bytes que o git ainda não havia reescrito.

**Evidência empírica (2026-04-23, pós-rollback do branch essay).** Sequência de três observações em cadeia:

1. Experimento em branch de trabalho `lfs-migrate-a-normativas-essay`: após `.gitattributes` receber o pattern `raw/A-normativas/**/*.html filter=lfs diff=lfs merge=lfs -text` e `git lfs migrate import --include="raw/A-normativas/*.html" --include-ref=refs/heads/lfs-migrate-a-normativas-essay` reescrever as commits históricas, validador rodou sobre `raw/A-normativas/` e retornou **8/10 BLOCK**. Os únicos OK foram `lei-12737-2012.html` e `lei-13718-2018.html` — precisamente os dois arquivos que `git ls-files --eol` reportava como `w/lf` já no download original (sidecar declarava sha256 de bytes LF-puros).
2. Rollback executado: `git checkout main && git reset --hard origin/main && git tag -d backup-pre-lfs-a-normativas && git branch -D lfs-migrate-a-normativas-essay`. Repo voltou ao estado pré-experimento, zero operação LFS ativa em `main`.
3. Validador rodado em `main` pós-rollback **sem nenhuma alteração de `.gitattributes` ou LFS**: reproduziu o mesmo 8/10 BLOCK, com `direto == lf` para cada um dos oito. Os bytes em disco já estavam LF-puros.

O vetor de reescrita foi o próprio `git reset --hard origin/main`. A regra `* text=auto eol=lf` em `.gitattributes` (linha 9) dispara o smudge filter em qualquer operação que reconstrua o working tree a partir dos objetos git. O smudge aplica `eol=lf` e substitui no disco os bytes mixed-CRLF pelos bytes LF-puros correspondentes. Isso acontece em `checkout`, `reset --hard`, `switch`, `restore`, `clone` — qualquer reconstrução do working tree.

**Quantificação da perda.** Comparação de byte-size entre download original (preservado em sidecar via `bytes_declarados`) e arquivo em disco pós-reset:

| arquivo | bytes sidecar | bytes pós-reset | delta | interpretação |
|---|---|---|---|---|
| cf-1988-compilada.html | 1 944 732 | 1 922 369 | −22 363 | 22 363 CRLFs colapsados em LF |
| cp-2848-compilado.html | 562 448 | 555 891 | −6 557 | idem |
| cpp-3689-compilado.html | 798 611 | 788 933 | −9 678 | idem |
| lei-12965-2014.html | 45 712 | 45 198 | −514 | idem |
| lei-13964-2019.html | 187 329 | 185 102 | −2 227 | idem |
| lei-14132-2021.html | 19 446 | 19 229 | −217 | idem |
| lei-14155-2021.html | 34 812 | 34 394 | −418 | idem |
| lei-14188-2021.html | 18 902 | 18 695 | −207 | idem |
| lei-12737-2012.html | 15 088 | 15 088 | 0 | era `w/lf` no download; imune |
| lei-13718-2018.html | 19 744 | 19 744 | 0 | era `w/lf` no download; imune |

O delta exato em bytes iguala a contagem de CRLFs que foram normalizados para LF. Cada `\r\n` colapsa em `\n` — um byte perdido por quebra de linha afetada.

**Distinção analítica: regime prospectivo vs regime retroativo.** A comparação com B-jurisprudencia deixa visível por que lá o LFS funcionou e aqui não:

- Regime prospectivo (B-jurisprudencia, fluxo de 2026-04-23): o pattern `raw/B-jurisprudencia/**/*.html filter=lfs diff=lfs merge=lfs -text` entrou no `.gitattributes` antes do primeiro `git add` dos HTMLs STF. O `lfs clean` rodou sobre os bytes HTTP originais, capturando o OID correto. Working tree e objeto git convergem byte-a-byte porque LFS intercepta o conteúdo antes da text conversion.
- Regime retroativo (A-normativas, tentado em 2026-04-23): o pattern foi adicionado depois que as blobs dos HTMLs já haviam sido gravadas nos objetos git pela Etapa 0.5 inicial (com `* text=auto eol=lf` ativo). `git lfs migrate import` opera sobre blobs no histórico, não sobre bytes no working tree — ele captura a versão que o git já tem, que é a versão LF-normalizada. O bug que se pretendia resolver já havia sido consumado meses antes; o migrate só rebatizou a tubulação.

**Descoberta lateral (a grave).** A falha retroativa do LFS migrate é irrelevante comparada à descoberta operacional que o experimento revelou: o smudge filter reescreve o working tree em qualquer rebuild, com ou sem LFS. A cadeia de custódia byte-a-byte declarada em sidecar v1.2 §4.4.1 para os oito arquivos mixed-CRLF nunca viveu no repositório git — viveu apenas no working tree local do Pedro, imune porque o repo nunca havia reescrito aqueles arquivos depois do `.gitattributes` entrar em vigor. Qualquer clone fresco em Linux, qualquer reset hard em Windows com `core.autocrlf=false`, qualquer checkout que troque branch, produz 8/10 BLOCK imediatamente. O baseline 10/10 OK celebrado em 2026-04-23 (commit 2679d8b) era propriedade transitória da máquina do Pedro, não propriedade do repositório.

**Trade-off aceito (calibração de convicção, não calibração de código).** A rede de segurança tri-modo (`direto` → `normalizado_lf` → `normalizado_crlf`) permanece no validador porque continua sendo útil: ela agora é diagnóstica, não corretiva. Quando `modo=normalizado_lf` faz o hash bater, o validador está informando "os bytes originais tinham este conteúdo em codepoints, mas em CRLF". Isso sustenta o registro histórico — o sidecar continua verdadeiro quanto ao conteúdo editorial, mesmo que o repositório não mantenha mais a representação byte exata. A rede NÃO recupera bytes; ela sinaliza que a representação byte original foi perdida e documenta qual era o conteúdo em nível de codepoints.

**Regra metódica generalizada que emerge.** Fidelidade byte-a-byte em git exige uma de três abordagens, todas necessariamente prospectivas (antes do primeiro `git add` do arquivo):

1. LFS regime ativo desde o commit inaugural — `lfs clean` captura bytes originais e `smudge` não reescreve (apenas materializa o OID).
2. Atributo `binary` (`-text`) no `.gitattributes` antes do primeiro `git add` — suprime text conversion integralmente.
3. Pattern-specific `-text` ou `eol=crlf` antes do primeiro `git add` — preserva line endings de origem.

Retroativamente, nenhuma ferramenta de history rewrite (`lfs migrate import`, BFG, `git filter-repo`) recupera os bytes originais. Os bytes foram consumidos pela conversão do text filter antes de virarem objeto git — não existem mais em nenhum lugar do repositório. Recuperação exige nova coleta da fonte original (HTTP re-download), não remediação interna ao repo.

**Corolário para sidecar v1.2 §4.4.1.** A declaração de `sha256` dos bytes HTTP originais continua sendo registro histórico verdadeiro — `data_coleta`, `etag`, `last_modified` são factuais, não dependem do estado do repo. Mas a verificação desse sha256 via validador só recupera o invariante `sha256(disco) == sha256(sidecar)` para arquivos que nasceram LFS, binary ou `-text`. Para o resto, o validador passa a atestar conteúdo (codepoints via fallback tri-modo), não byte-representação. O campo de sidecar `bytes_declarados` ganha peso probatório maior — é o único registro imutável da representação byte original.

**Implicação imediata para o projeto.** Reingest prospectivo dos 10 HTMLs de A-normativas com pattern LFS ativo *antes* do `git add` é operação urgente, não opcional. Cada dia que o repo permanece no estado atual é mais um dia de "cadeia de custódia ilusória" para eventual auditoria externa ou para onboarding de nova máquina. Plano operacional em `PLANO-INGESTAO.md §Reingest-2026-04-23`.

**Protocolo adicional ao sidecar v1.3 (proposta para escopo futuro).** Registrar em cada `.source.yaml` um campo novo `regime_git: lfs | binary | text_unset | text_auto` indicando sob que regime o arquivo foi comitado pela primeira vez. Isso torna o escopo da fidelidade byte-a-byte auditável no próprio sidecar, sem depender de inspeção de `.gitattributes` em momento desconhecido. Arquivos comitados sob `regime_git: text_auto` ganham marca explícita de "sha256 é histórico, não verificável no repo atual".

**Protocolo de registro de calibrações futuras:** cada nova calibração (adição/remoção de padrão, ajuste de threshold, nova rede de segurança) deve ser registrada nesta subseção com (a) data, (b) commit, (c) evidência empírica que motivou a decisão, (d) trade-off aceito, (e) regra metódica geral que emerge (se houver). Esta subseção funciona como cadeia de custódia epistemológica do validador — parte integrante da disciplina de fidelidade do pipeline.

**Calibração #4 — FASE 2 reingest prospectivo LFS valida a recomendação da Calibração #3; schema v1.2 tolera heterogeneidade rica/simplificada; sentinela `"nao-capturado"` passa por teste de campo; anomalia material lei-14188-2021 isolada (2026-04-24, commit 3081647).**

Três observações simultâneas encerram a Fase 0.5 para A-normativas, com consequências operacionais distintas.

**(a) Regime LFS prospectivo funciona integralmente — `sha256(disco) == OID(LFS) == sidecar` em 10/10.**

O experimento de regime retroativo (`git lfs migrate import`, Calibração #3) havia refutado a tentativa de remediação do bug `eol=lf + text=auto` sobre blobs já gravados. A FASE 2 (commit 3081647) aplicou o regime prospectivo canônico: (i) commit de remoção dos HTMLs textuais (68353a7) para limpar o tracking; (ii) `.gitattributes` com `raw/**/*.html filter=lfs diff=lfs merge=lfs -text` ativo antes do re-`git add`; (iii) coleta fresca de 10 HTMLs via `Invoke-WebRequest` com `$r.RawContentStream.ToArray()` para snapshot byte-a-byte; (iv) sidecares atualizados com o sha256 dos bytes coletados; (v) `git add` inaugural roteando o conteúdo pelo `lfs clean` antes de qualquer text conversion.

Resultado empírico: `validate_raw_05.py` rodou sobre os 10 e emitiu `ok=10 warning=0 blocked=0`, com `sha256_modo=direto` em todos — ou seja, o sha256 declarado em sidecar bate com o sha256 dos bytes em disco pós-smudge em um clone fresh Windows-nativo. O OID LFS (pointer em `.git/lfs/objects/`) é idêntico ao sha256 do sidecar — como `filter=lfs` usa sha256 como esquema de ID, isso verifica automaticamente a integridade em toda travessia (coleta HTTP → disco origem → `lfs clean` → push → origin → pull/clone fresh + smudge).

Trade-off aceito: qualquer nova source_type com invariante byte-a-byte declarada em sidecar (HTMLs de tribunais, XMLs estruturados do CNJ DataLake em contexto forense, JSONs de peritagem digital) DEVE ter seu pattern adicionado a `.gitattributes` com `filter=lfs diff=lfs merge=lfs -text` ANTES do primeiro `git add` do primeiro arquivo desse tipo. Retroatividade é refutada por construção (Calibração #3). A disciplina recai sobre o analista: auditar `.gitattributes` antes de coletar, nunca depois.

Regra metódica que se consolida: **"auditoria de tubulação antes de auditoria de conteúdo"**. O estado do `.gitattributes` é pré-condição forense da cadeia de custódia, não detalhe de implementação. O reviewer que recebe um PR de nova source_type deve checar primeiro o patch do `.gitattributes`, só depois o conteúdo.

**(b) Schema v1.2 tolera heterogeneidade rica/simplificada + sentinela sem carve-out técnico.**

Observação não planejada: dos 10 sidecares atualizados em FASE 2, nove usam a forma simplificada (`etag_http` e `last_modified_http` como chaves na raiz) e um usa a forma rica (`http_response.etag`, `http_response.last_modified` sob bloco `http_response:`). Ambos passaram o validador sem qualquer ajuste de código. Heterogeneidade convive. Além disso, um dos sidecares usa a sentinela `"nao-capturado-2026-04-24"` em vez de valor HTTP real — o validador aceita como string opcional, não bloqueia.

A interpretação correta disso não é "o validador está tolerante demais, precisa apertar". É: **o schema v1.2 foi desenhado com campos extensíveis por tipo (§4.4 / §4.4.1 / §4.5) e com degradação graciosa de captura HTTP — e estas duas propriedades sustentam a operação do agente MP em campo sem quebra de compatibilidade do pipeline**. Se a próxima coleta usar headers HTTP indisponíveis (proxy institucional que suprime cabeçalhos, servidor que não responde ETag), a sentinela mantém o sidecar schema-válido e o analista não precisa decidir se "pula o campo" ou "inventa valor" — a política está embutida no schema.

Formalização como v1.2-a (proposta): documentar em `_AGENTS/raw-protocol.md` que (i) a forma rica é preferida quando disponível, (ii) a forma simplificada é aceita em legado, (iii) a sentinela `"nao-capturado-YYYY-MM-DD"` é o protocolo canônico para campos HTTP que o servidor não forneceu na coleta. Isso é ato documental, não técnico — o validador já aceita todos os três formatos sem alteração.

Trade-off aceito: com sentinela aceita, perde-se validação estrutural de formato ISO-8601 / RFC-7232 em timestamps HTTP. O custo é registrar como "ruído controlado" em auditoria externa — se um `nao-capturado-*` aparece, o auditor sabe que o agente MP deliberadamente escolheu essa string em vez de inventar valor, o que é preferível forensicamente.

Regra metódica: **"robustez operacional > pureza sintática em campos não-fundamentais"**. Aplicável a todo campo de sidecar que dependa de terceiros (ETag/Last-Modified do servidor, relator do acórdão em sistema legado que não expõe, número de processo em peça escaneada sem metadado). Fundamentais (`sha256`, `baixado_em`, `baixado_por`, `arquivo`, `tipo`, `url_origem`) permanecem sem sentinela — falha obrigatória, não degradação.

**(c) Anomalia material isolada em `lei-14188-2021.html`: delta_bytes −1.559 (−8,53%).**

9 dos 10 HTMLs tiveram `delta_bytes == 0` entre coleta anterior (2026-04-23) e coleta FASE 2 (2026-04-24), com `sha256` divergente. Isso valida a decisão arquitetural de 2026-04-24: rotação F5 WAF/CSPM por request reescreve nonce e token sem alterar o conteúdo editorial — invariante byte-a-byte com a fonte é impossível, mas o delta de tamanho é zero.

A exceção — lei-14188-2021 — é o único caso com delta não trivial. Redução de 1.559 bytes é grande demais para ser atribuída a rotação F5 (faixa observada: 128–1.233 B em injeções, e sempre adição, não remoção). Hipótese operacional registrada no sidecar: recompilação editorial do Planalto entre coletas. Esse arquivo já era o "caso de injeção assimétrica" no diagnóstico original (backup continha bloco CSPM de 1.233 B, fresh não continha) — provavelmente a gestão AJ homogeneizou o template CSPM nesta lei entre datas de coleta.

**Importa para a Hipótese v3 (bug ordinal)?** Em princípio, não: a anomalia é no envelope de template CSPM / script F5, não na redação normativa. Mas o diff só pode ser conclusivo após conversão HTML→MD canônica de ambas as versões, via `iconv -f WINDOWS-1252` + strip de scripts. **Plano de investigação** (registrado no sidecar `reingest_2026_04_24.anomalia_recompilacao.investigar_em_etapa_1: true` e em `PLANO-INGESTAO.md §Reingest-2026-04-23 Fase 2`):

1. Quando Etapa 1 for acionada, converter ambas as versões para `inbox/<id>.md`.
2. Executar `diff` semântico sobre o markdown canônico.
3. Se delta textual ≈ 0 (apenas remoção de template/script CSPM), consolida o modelo "F5 como causa única da divergência byte-a-byte".
4. Se delta textual > 0, é o primeiro data point de alteração material sem publicação de ato normativo alterador — exige checagem no DOU e, se confirmado, virar entrada na Hipótese v3 como "rebaseline editorial não sinalizada".

Regra metódica: **"toda anomalia numérica registrada em sidecar passa o bastão para Etapa 1 via campo flag, não fica em limbo"**. O protocolo `anomalia_recompilacao` + `investigar_em_etapa_1: true` é o canal canônico para esse handoff. A investigação é acionada pela Etapa 1, nunca pela Etapa 0.5 (que é apenas validação bloqueante de integridade, não análise editorial).

**Ganho lateral para Hipótese v3 (bug ordinal).** A FASE 2 coletou CF/1988 e CPP/1941 em versão fresca. Comparar o `taxa_bug` medido em 2026-04-22 com o medido sobre os novos arquivos (quando Etapa 1 produzir o markdown canônico) pode dar um novo tipo de data point: **"o mesmo artefato ingerido em datas diferentes mantém a mesma estratificação editorial ou há homogeneização silenciosa?"**. Se as taxas baterem (CF=0%, CPP≈30,4%, CP≈6,5%), v3 ganha suporte adicional — estratificação é propriedade persistente do documento compilado, não artefato do instante de coleta. Se divergirem significativamente, há recompilação em massa (alvo de falseamento #4 da v3) e v3 precisa ajustar. Acionar esta comparação quando Etapa 1 rodar.

## CADEIA DE CUSTÓDIA — Decisão arquitetural 2026-04-24

**Contexto**: diagnóstico da Fase 1 Reingest identificou F5 Advanced WAF/CSPM
no Planalto, injetando nonce `f5avr<timestamp>` + token 128 B por request.
Reprodutibilidade byte-a-byte com a fonte é impossível enquanto o F5 estiver
ativo.

**Decisão**: a cadeia de custódia de `raw/` ancora-se no ato de coleta
documentado por agente público do MP, não em reprodutibilidade perpétua.
Sidecar v1.2 (`sha256` + `etag_http` + `last_modified_http` + `baixado_em`
+ `baixado_por`) é a unidade atestada de captura.

**Fundamento**: CPP 158-A (Lei 13.964/19); LC 75/93 art. 8º II; Lei 8.625/93
art. 26 I; CNJ Res. 615/2025; Lei 9.610/98 art. 8º IV.

**Implicação sobre Hipótese v3 (bug ordinal)**: comparações editoriais
entre coletas em datas diferentes devem operar sobre `inbox/` (markdown
canônico) ou diff semântico, não sobre `raw/` HTML bruto — o sinal F5
contamina a métrica byte-a-byte.

**Detalhamento completo**: `PLANO-INGESTAO.md §Reingest-2026-04-23`.

## REFERÊNCIAS INTERNAS
- Protocolo da landing zone raw/ (sidecar .source.yaml + pipeline): _AGENTS\raw-protocol.md
- Watchlist de casos pendentes de julgamento (governança B em tramitação): watchlist\README.md
- Schema canônico completo: _AGENTS\schema-reference.md
- Formatos de citação por tipo: _AGENTS\citacoes-canonicas.md
- Vocabulário ativo: schema\vocabulario.yaml
- Golden dataset: schema\golden_dataset.yaml
- Plano de ingestão e fases: PLANO-INGESTAO.md
