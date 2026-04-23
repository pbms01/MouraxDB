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
1. Conferência de integridade: sha256 recalculado bate com sidecar .source.yaml (mismatch → aborta).
2. Verificar encoding: detectar padrões de corrupção UTF-8→Latin-1 (ex: "ÃÃ§Ã£o" em vez de "ação")
   - Score > 2% de tokens afetados → quarantine\encoding-artifacts\ + encoding_validated: false
   - Score 0.5–2% → warning + revisão manual recomendada
   - Score < 0.5% → encoding_validated: true, prossegue
3. Verificar artefatos de processo: ((VERIFICAR)), [[notas internas]], RASCUNHO, linhas com ??, (TIRAR DA
   - Qualquer match → quarantine\encoding-artifacts\ com lista de ocorrências
4. Documento só avança com encoding_validated: true no front-matter YAML.
5. PROIBIDO limpeza automatizada — risco de remoção de conteúdo legítimo em texto jurídico.
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
## REFERÊNCIAS INTERNAS
- Protocolo da landing zone raw/ (sidecar .source.yaml + pipeline): _AGENTS\raw-protocol.md
- Watchlist de casos pendentes de julgamento (governança B em tramitação): watchlist\README.md
- Schema canônico completo: _AGENTS\schema-reference.md
- Formatos de citação por tipo: _AGENTS\citacoes-canonicas.md
- Vocabulário ativo: schema\vocabulario.yaml
- Golden dataset: schema\golden_dataset.yaml
- Plano de ingestão e fases: PLANO-INGESTAO.md
