# KB-PD — raw/ Protocol (v1.2)

Documento operacional do estágio `raw/` — landing zone imutável do pipeline.
Versionar no Git. Atualizar quando schema do sidecar mudar.

Introduzido em: 2026-04-22 (pipeline v1.2).

---

## 1. Propósito

`raw/` é a única porta de entrada do corpus no KB-PD. Todo documento jurídico
novo — normativa, acórdão, ISO, resolução, doutrina, peça processual — entra
primeiro em `raw/<tipo>/` no formato original em que foi obtido (HTML, PDF,
TXT, MD, JSON, XML), acompanhado de um sidecar `.source.yaml` com a
procedência.

Nenhum arquivo vai direto para `inbox/`, `corpus/` ou qualquer outro estágio
sem passar antes por `raw/`.

---

## 2. Propriedades de `raw/`

| Propriedade | Regra |
|---|---|
| Imutabilidade | Binários em `raw/` não são editados depois do depósito — só substituídos por novo depósito com novo SHA-256. |
| Cobertura | 8 subpastas espelhando o `source_type` (A–H). Sem mistura entre tipos. |
| Sidecar | Todo arquivo tem um `.source.yaml` irmão obrigatório (ver §4). |
| Auditabilidade | `ls raw/*/` audita cobertura do Critério 1 da Fase 1 em um comando. |
| Git LFS | `*.pdf` e `*.epub` vão para LFS via `.gitattributes`. Demais formatos ficam como texto. |

---

## 3. Layout

```
raw/
├── A-normativas/        # CP, CPP, leis, MPs, decretos, portarias
│   ├── <id>.<ext>
│   └── <id>.source.yaml
├── B-jurisprudencia/    # acórdãos STF/STJ/tribunais
├── C-iso/               # ISO/IEC, NIST SP-800
├── D-resolucoes/        # CNJ, CNMP, órgãos reguladores
├── E-doutrina/          # livros, artigos acadêmicos
├── F-operacional/       # manuais Cellebrite, runbooks
├── G-proprio/           # material do autor
└── H-pecas/             # peças processuais — modelos e casos
```

### 3.1 Naming convention

Nome do arquivo = ID canônico do documento (o mesmo que vai para `corpus/`).

| Exemplo | Fonte |
|---|---|
| `lei-12737-2012.html` | normativa Planalto |
| `lei-12737-2012.source.yaml` | sidecar obrigatório |
| `re-1037396-tema987-stf.pdf` | acórdão STF (PDF assinado) |
| `re-1037396-tema987-stf.source.yaml` | sidecar |
| `iso-iec-27037-2012.pdf` | norma técnica ISO |
| `res-cnj-615-2025.html` | resolução CNJ |

Regra: nome do sidecar = `<id>.source.yaml` (não `<id>.<ext>.source.yaml`).
Um sidecar descreve um documento lógico, mesmo que ele seja depositado em
múltiplos formatos simultaneamente (ver §5).

### 3.2 Casos pendentes de julgamento (Tipo B em tramitação)

Quando a fonte é um processo **em tramitação** no STF/STJ (sem acórdão
publicado, sem trânsito em julgado), o ativo em `raw/` é fundamentalmente
distinto de um PDF assinado:

- **Fonte**: HTML dinâmico multi-endpoint (portal + abas AJAX), não PDF.
- **Temporalidade**: o ativo muda ao longo do tempo — cada coleta é um
  *snapshot datado*, não uma cópia definitiva.
- **Sem assinatura**: não há ICP-Brasil nem equivalente institucional na
  origem (é apenas HTML renderizado pelo portal).
- **Não gera L0**: o conteúdo não entra em `corpus/` até trânsito em
  julgado — evita chunking de petições/decisões interlocutórias que
  podem ser superadas pela tese definitiva.

Layout adotado:

```
raw/B-jurisprudencia/<TRIBUNAL>/<CLASSE-NUMERO>/
└── <YYYY-MM-DDTHH-MM-SSZ>/            # snapshot datado UTC
    ├── portal-detalhe.html             # página principal (incidente)
    ├── aba-partes.html
    ├── aba-andamentos.html
    ├── aba-peticoes.html
    ├── aba-decisoes.html
    ├── aba-sessao-virtual.html
    ├── aba-pauta.html
    └── snapshot.source.yaml            # sidecar do snapshot
```

A governança do **quê** coletar, **quando** recoletar e **quando** promover
para L0 vive em `watchlist/` (ver `watchlist/README.md`). Aqui só se
define o formato do depósito.

---

## 4. Schema do sidecar `.source.yaml`

```yaml
# Campos OBRIGATÓRIOS
arquivo: <nome do arquivo principal em raw/>
tipo: <A|B|C|D|E|F|G|H>
url_origem: <URL pública ou identificador interno>
baixado_em: "<ISO-8601 com timezone>"
baixado_por: <identificação de quem depositou>
sha256: <hash do binário original | null se legado pré-v1.2>
encoding_declarado_http: <o que o servidor respondeu no Content-Type | null>
encoding_real_detectado: <resultado de file/chardet/enca | null para PDF>
conversao_prevista: <pipeline previsto: ex. html→md via iconv CP1252>

# Campos OPCIONAIS (contextuais)
observacoes: >
  <texto livre — peculiaridades, bugs do portal de origem, decisões>
formato_alternativo: <lista de outros formatos do mesmo doc depositados | null>
# ex: ["lei-12737-2012.pdf"] quando HTML + PDF coexistem
paginas: <int | null>                   # PDFs — número total de páginas
idioma: <ptBR|ptPT|en|es|...>
licenca: <domínio público | CC-BY | all rights reserved | ...>
versao_ferramenta_extracao: null        # preenchido na Etapa 1, não aqui
```

### 4.1 Campo `sha256`

Calcular sobre o binário no momento do depósito, antes de qualquer
transformação:

```bash
sha256sum raw/A-normativas/lei-12737-2012.html
```

O valor vai cru no sidecar, sem prefixo. Se o arquivo for substituído por
nova versão (nova data de baixa, novo conteúdo), o sidecar inteiro é
reescrito — novo `sha256`, novo `baixado_em`, e a versão antiga vai para
`raw/<tipo>/_archive/<id>.<timestamp>.<ext>` (preservação de histórico).

### 4.2 Exceção de legado — `sha256: null`

Permitido apenas para os 3 arquivos do `inbox/` que entraram pré-v1.2
(lei-12737-2012, lei-14155-2021, lei-12965-2014). O binário HTML original
não foi preservado no depósito da sessão anterior. O sidecar retroativo
registra URL de origem e data aproximada, com `observacoes:
"legado-pre-v1.2 — binário HTML original não preservado; reconstruir
sha256 sob demanda se a lei for contestada em peça processual"`.

Todo sidecar v1.2 em diante tem `sha256` não-nulo. Regra: se o pipeline
encontrar `sha256: null` em um sidecar não-legado, **bloqueia**.

### 4.3 Campo `conversao_prevista`

Texto livre descrevendo a etapa 1 prevista. Valores típicos:

- `html→md via iconv CP1252 + pandoc`
- `pdf→md via pdftotext -layout`
- `pdf→md via ocrmypdf (scan, sem camada de texto)`
- `json→md via parser-stj-brs-v1`
- `xml→md via xslt lexml-ato-normativo`
- `md (nativo) — sem conversão, só validação de front-matter`


### 4.4 Extensões por source_type

Alguns tipos de documento carregam campos de custódia que não fazem sentido
para outros. Esta seção define os campos **adicionais** (opcionais para A/C/E,
**obrigatórios** para B) que o sidecar deve conter para cada `source_type`.

#### Tipo B — Jurisprudência (PDF como fonte canônica)

Campos adicionais obrigatórios quando `tipo: B` e o formato é PDF:

```yaml
tribunal: <STF|STJ|TRF1|TRF2|TRF3|TRF4|TRF5|TJ-UF|TST|...>
# determina qual perfil de segmentação aplicar na Etapa 1
# (regex de EMENTA/ACÓRDÃO/RELATÓRIO/VOTO varia por tribunal)

instrumento: <acordao|decisao_monocratica|despacho|sumula|tema_repetitivo>
numero_processo: <número oficial com formatação do tribunal>
relator: <nome do relator/a>
orgao_julgador: <ex: "Sexta Turma", "Plenário", "Pleno">
data_julgamento: <YYYY-MM-DD | null se decisão monocrática>
data_publicacao: <YYYY-MM-DD | null>

assinatura_digital:
  presente: <true|false>           # detectado via `pdfsig`
  formato: <ICP-Brasil|Revista_Eletronica_STJ|outros|sem_assinatura>
  # "Revista_Eletronica_STJ" = PDF sem ICP-Brasil mas com cabeçalho
  # institucional do tribunal (caso do HC 315.220)
  certificados: <lista de signatários com emissor e validade | null>

paginacao_oficial_preservada: <true|false>
# true quando o PDF mantém numeração "fl. N" referenciável em peças;
# false quando é renderização sem paginação oficial

fonte_confiavel: <pbm_s|null>
# quando o PDF foi obtido diretamente pelo autor no portal oficial
# e a ausência de assinatura ICP-Brasil é compensada pela cadeia de
# custódia do próprio depositário (registrar em observacoes: data,
# hora, portal específico, tribunal, sistema de autenticação usado)
```

**Perfis de segmentação disponíveis na Etapa 1:**

Inicia com `STJ` (piloto HC 315.220). Novos perfis (STF, TRF2, TJ-UF
etc.) são adicionados conforme cada tipologia receber seu primeiro
depósito. A escolha do perfil é determinada pelo campo `tribunal` do
sidecar.

Justificativa dos campos:

- `tribunal` parametriza o segmentador. Sem este campo, a Etapa 1 não tem
  como escolher o regex correto (STF e STJ compartilham estrutura, mas
  TRFs variam muito entre si e entre relatores).
- `assinatura_digital` é **a** prova de custódia em PDF. Registrar no
  depósito evita ter de re-rodar `pdfsig` toda vez que alguém quiser
  verificar a custódia.
- `paginacao_oficial_preservada` determina se o MD pode citar `fl. N` ou
  se só pode citar offsets textuais.
- `fonte_confiavel: pbm_s` documenta que, para PDFs sem ICP-Brasil
  (ex: Revista Eletrônica STJ), a custódia é ancorada na coleta pelo
  próprio autor em portal autenticado. Não é equivalente a ICP-Brasil,
  mas é um grau de confiança documentado e auditável.

#### 4.4.1 Tipo B em tramitação (snapshot temporal, HTML)

Aplicável quando `tipo: B` e `instrumento: processo_em_tramitacao`. Schema
de custódia é **temporal** (por snapshot), não criptográfico — a garantia
vem da coleta datada pelo próprio autor no portal oficial, não de
assinatura ICP-Brasil (que inexiste na origem HTML).

Campos adicionais obrigatórios:

```yaml
tribunal: <STF|STJ|TJ-UF|...>

instrumento: processo_em_tramitacao

numero_processo: <número oficial do tribunal + CNJ único, se houver>
incidente: <número do incidente no portal | null>
classe_processual: <RE|AgR|HC|ADI|ADPF|...>
tema_rg: <número do Tema de Repercussão Geral | null>
ramo: <Criminal|Cível|Tributário|Constitucional|...>

relator: <relator/a conforme portal na data do snapshot>
orgao_julgador: <turma/plenário | null se ainda não distribuído>

estado_processual:
  <autuado
   | em_tramitacao
   | com_RG_reconhecida
   | sob_vista
   | em_sessao_virtual
   | suspenso
   | julgado_pendente_publicacao
   | redistribuicao_pendente>

data_autuacao: <YYYY-MM-DD | null>
data_ultima_movimentacao: <YYYY-MM-DD | null>

snapshot:
  datetime_iso: "<YYYY-MM-DDTHH:MM:SSZ>"   # UTC (sufixo Z obrigatório)
  user_agent: "<User-Agent usado na coleta>"
  abas_capturadas: <lista de HTMLs efetivamente baixados>
  anomalias_observadas: >
    <texto livre — ex: relator divergente de fato conhecido,
    data fora de padrão, campos ausentes, abas em 404>
  dinamico: true                        # marcador: ativo pode mudar

assinatura_digital:
  presente: false
  formato: sem_assinatura
  certificados: null

fonte_confiavel: pbm_s                  # coleta direta pelo autor
```

**Notas operacionais:**

- `datetime_iso` sempre em **UTC** (sufixo `Z`), independente do fuso
  local. Evita ambiguidade em auditoria cruzada.
- `anomalias_observadas` preserva o que o portal disse na data do
  snapshot, mesmo quando o valor é factualmente questionável (ex:
  relator já aposentado constando como relator ativo). A cadeia de
  custódia documenta a **coleta**, não a correção do dado de origem.
- `abas_capturadas` lista apenas os arquivos efetivamente salvos — aba
  que retornou 404 ou veio vazia vai para `anomalias_observadas`, não
  para a lista.
- Nenhum snapshot Tipo B em tramitação gera L0 até promoção formal via
  `watchlist/` (gate: trânsito em julgado + acórdão publicado com
  assinatura institucional — então o caso recai no schema §4.4
  canônico, PDF como fonte).

#### Tipos A, C, D, E, F, G, H

Por enquanto seguem só com o schema de §4. Extensões específicas serão
incorporadas quando cada tipo receber seu primeiro depósito.

### 4.5 Rastreabilidade dupla no front-matter do MD (inbox/)

Para documentos Tipo B (e quaisquer outros convertidos de PDF), o MD em
`inbox/<id>.md` carrega **duas** camadas de rastreabilidade no front-matter:

**Camada 1 — artefato original** (replicada do sidecar, para o MD ser
autossuficiente):

```yaml
raw_arquivo: <nome do PDF em raw/>
raw_sha256: <hash do PDF>
raw_bytes: <tamanho em bytes>
raw_url: <URL do portal oficial>
raw_baixado_em: <ISO-8601>
raw_assinatura_icp: <true|false>
```

**Camada 2 — conversão reproduzível** (nova para Tipo B):

```yaml
conversor: "pdftotext"
conversor_versao: <output de `pdftotext -v` truncado>
# ex: "poppler 23.04.0"
conversor_flags: "-layout -enc UTF-8"
segmentador_script: "scripts/segmenta_acordao.py"
segmentador_sha: <git commit hash curto | null durante bootstrap>
conversao_rodada_em: <ISO-8601 do momento da conversão>
md_sha256: <hash do próprio MD, calculado após escrita>
```

**Nota bootstrap:** `segmentador_sha: null` é aceito enquanto o script
`segmenta_acordao.py` ainda não existir. Quando o script for criado,
documentos Tipo B convertidos na fase de bootstrap devem ser
reconvertidos e ter o campo preenchido.

Justificativa: `pdftotext` **não é determinístico entre versões do
Poppler**. Um upgrade pode mudar a saída. Sem registro da versão, a
promessa de reproduzibilidade da conversão falha se alguém contestar uma
citação anos depois. Registrar `conversor_versao` + `segmentador_sha`
permite reconstruir exatamente o mesmo MD a partir do mesmo PDF a
qualquer momento.

`md_sha256` permite detectar edição manual não autorizada do MD em
`inbox/` (princípio de fidelidade: se o MD foi editado após a conversão,
o hash diverge e a Etapa 2 bloqueia).

---

## 5. Múltiplos formatos do mesmo documento

Ocorre em dois cenários:

### 5.1 Backup de segurança

Você baixa o HTML do Planalto (fonte canônica) mas também quer preservar o
PDF do DOU para o caso de o Planalto alterar o HTML silenciosamente:

```
raw/A-normativas/
├── lei-12737-2012.html           ← canônico
├── lei-12737-2012.pdf            ← backup
└── lei-12737-2012.source.yaml
```

```yaml
arquivo: lei-12737-2012.html
formato_alternativo: ["lei-12737-2012.pdf"]
sha256: 9c8a...<hash do html>
observacoes: >
  PDF do DOU preservado como backup. SHA-256 do PDF:
  a12b3c4d... (calculado em 2026-04-22). Fonte canônica = HTML.
```

### 5.2 Fonte canônica é PDF

Para ISO/NIST e peças assinadas digitalmente, o PDF é a fonte canônica
(tem a assinatura, a paginação oficial, etc.). Não há backup — só o PDF.

---

## 6. Hierarquia de preferência de formato (fonte canônica)

Quando um documento está disponível em múltiplos formatos, a ordem de
preferência para **fonte canônica** é:

| Prioridade | Formato | Justificativa |
|---|---|---|
| 1 | `.html` com encoding explícito | diffável, parse robusto, encoding detectável |
| 2 | `.txt` com encoding explícito | simples, diffável |
| 3 | `.md` nativo (autor) | quando a fonte original já é Markdown |
| 4 | `.json` estruturado (API) | ótimo para schemas fechados (STJ BRS, DataJud) |
| 5 | `.xml` estruturado (LexML) | quando há DTD/schema |
| 6 | `.pdf` (último recurso) | só quando é a única forma disponível ou paginação/assinatura é semanticamente relevante (ISO, peças assinadas) |

Regra: HTML com encoding explícito **sempre** vence PDF quando ambos
existem. PDF introduz custo de extração (OCR, pdftotext, controle de
layout) sem ganho informacional.

---

## 7. Fluxo de entrada no pipeline

```
 ┌─────────────────────────────────────────────────────────┐
 │ Etapa 0 — depósito em raw/                              │
 │                                                         │
 │   1. Baixar o arquivo (manualmente ou via script)       │
 │   2. Salvar em raw/<tipo>/<id>.<ext>                    │
 │   3. Calcular sha256sum                                 │
 │   4. Criar raw/<tipo>/<id>.source.yaml                  │
 │   5. git add + commit (sidecar + binário juntos)        │
 └─────────────────────────────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Etapa 0.5 — validação bloqueante                        │
 │                                                         │
 │   1. Recalcular sha256 e comparar com sidecar           │
 │      (mismatch = aborta)                                │
 │   2. Detectar encoding real                             │
 │      (conflito com declarado no sidecar = warning)      │
 │   3. Score de corrupção UTF-8→Latin-1                   │
 │      > 2%  → quarantine/ + bloqueia                     │
 │      0.5–2% → warning + revisão manual                  │
 │      < 0.5% → prossegue                                 │
 │   4. Detectar artefatos de processo                     │
 │      ((VERIFICAR)), [[notas]], RASCUNHO, ??             │
 │      qualquer match → quarantine/                       │
 └─────────────────────────────────────────────────────────┘
                           │ encoding_validated: true
                           ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Etapa 1 — conversão canônica                            │
 │                                                         │
 │   Aplica conversao_prevista do sidecar:                 │
 │     - HTML Planalto: iconv -f WINDOWS-1252 -t UTF-8     │
 │     - PDF: pdftotext -layout ou ocrmypdf                │
 │     - JSON API: parser dedicado                         │
 │     - XML LexML: xslt                                   │
 │                                                         │
 │   Produto: inbox/<id>.md com front-matter canônico      │
 │   (source_type, citacao_canonica, encoding_validated:   │
 │   true, campos da seção §5 de schema-reference.md)      │
 └─────────────────────────────────────────────────────────┘
                           │
                           ▼
 ┌─────────────────────────────────────────────────────────┐
 │ Etapa 2 — chunking atômico                              │
 │                                                         │
 │   inbox/<id>.md → corpus/<tipo>/<id>/<chunk>.md         │
 │   (L0 canônico)                                         │
 └─────────────────────────────────────────────────────────┘
```

---

## 8. Quatro exemplos anotados

### 8.1 HTML do Planalto (caso canônico de Tipo A)

```yaml
# raw/A-normativas/lei-12737-2012.source.yaml
arquivo: lei-12737-2012.html
tipo: A
url_origem: https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12737.htm
baixado_em: "2026-04-22T13:47:00-03:00"
baixado_por: pedro.mourao
sha256: 9c8a4e1f7b3d2c8a5f1e9d0c3b4a7f2e1d8c5b6a9e7f3d2c1b4a5e8d7c6b3a2f
encoding_declarado_http: "ISO-8859-1"
encoding_real_detectado: "WINDOWS-1252"
conversao_prevista: "html→md via iconv -f WINDOWS-1252 + pandoc"
idioma: ptBR
licenca: "domínio público (Lei 9.610/98 art. 8º IV — textos de lei)"
observacoes: >
  Planalto declara ISO-8859-1 no meta mas bytes 0x93/0x94 (aspas
  tipográficas) estão presentes no HTML — confirma CP1252. Regra
  permanente AGENTS.md §Encoding.
```

### 8.2 PDF de acórdão STJ — Revista Eletrônica (Tipo B, PDF canônico)

```yaml
# raw/B-jurisprudencia/STJ/HC-315220/hc-315220-stj.source.yaml
arquivo: hc-315220-stj.pdf
tipo: B
url_origem: https://processo.stj.jus.br/...
baixado_em: "2026-04-22T14:12:00-03:00"
baixado_por: pedro.mourao
sha256: e85bd95c...<hash completo>
encoding_declarado_http: null
encoding_real_detectado: null          # PDF — não aplica
conversao_prevista: "pdf→md via pdftotext -layout + segmenta_acordao.py (perfil STJ)"
paginas: 58
idioma: ptBR
licenca: "domínio público (decisão judicial pública — Lei 9.610/98 art. 8º IV)"

# Extensões §4.4 — Tipo B
tribunal: STJ
instrumento: acordao
numero_processo: "HC 315.220/RS (2015/0019757-0)"
relator: "Ministra Maria Thereza de Assis Moura"
orgao_julgador: "Sexta Turma"
data_julgamento: "2015-09-15"
data_publicacao: "2015-10-09"

assinatura_digital:
  presente: false
  formato: Revista_Eletronica_STJ
  certificados: null

paginacao_oficial_preservada: true     # "fl. 3" etc. citáveis

fonte_confiavel: pbm_s

observacoes: >
  PDF obtido via Revista Eletrônica de Jurisprudência do STJ — produtor
  wPDF, autor "Superior Tribunal de Justiça". Não carrega ICP-Brasil
  (diferente de inteiro-teor via e-STJ). Custódia ancorada em coleta
  pelo próprio autor no portal oficial do STJ em 2026-04-22. Rodapé
  institucional "Documento: 1406511 - Inteiro Teor do Acórdão" em
  todas as 58 páginas — remover na Etapa 1 via regex. Ementa aparece
  duas vezes no PDF (p.1 e p.5) — propriedade do documento, não
  artefato do conversor; preservar no MD.
```

### 8.3 Legado pré-v1.2 (exceção com sha256: null)

```yaml
# raw/A-normativas/lei-12737-2012.source.yaml (versão LEGADO, se aplicável)
arquivo: null                     # binário original não preservado
tipo: A
url_origem: https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12737.htm
baixado_em: "2026-04-22"          # data aproximada da sessão anterior
baixado_por: pedro.mourao
sha256: null                      # perdido no depósito pré-v1.2
encoding_declarado_http: null
encoding_real_detectado: "WINDOWS-1252"  # inferido retroativamente
conversao_prevista: "já convertido — ver inbox/lei-12737-2012.md"
observacoes: >
  legado-pre-v1.2 — binário HTML original não preservado na sessão
  de 2026-04-22 que converteu a lei para MD. MD intermediário está
  em inbox/lei-12737-2012.md com encoding já validado. Reconstruir
  sha256 sob demanda se a lei for contestada em peça processual
  (re-download do Planalto + comparação byte a byte com MD atual
  via conversão reversa).
```

### 8.4 HTML em snapshot — STF em tramitação (Tipo B em tramitação)

```yaml
# raw/B-jurisprudencia/STF/RE-1301250/2026-04-23T15-00-00Z/snapshot.source.yaml
arquivo: portal-detalhe.html
tipo: B
url_origem: https://portal.stf.jus.br/processos/detalhe.asp?incidente=6059876
baixado_em: "2026-04-23T15:00:00Z"
baixado_por: pedro.mourao
sha256: <a calcular após coleta do portal-detalhe.html>
encoding_declarado_http: null
encoding_real_detectado: "UTF-8"
conversao_prevista: "sem conversão — snapshot de acompanhamento, não gera L0"
idioma: ptBR
licenca: "domínio público (informação processual pública — Lei 9.610/98 art. 8º IV)"

# Extensões §4.4.1 — Tipo B em tramitação
tribunal: STF
instrumento: processo_em_tramitacao
numero_processo: "RE 1.301.250/RJ (0072968-96.2018.8.19.0000)"
incidente: "6059876"
classe_processual: RE
tema_rg: "1148"
ramo: Criminal

relator: "Min. Rosa Weber"
orgao_julgador: null

estado_processual: com_RG_reconhecida

data_autuacao: "2021-02-05"
data_ultima_movimentacao: null

snapshot:
  datetime_iso: "2026-04-23T15:00:00Z"
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
  abas_capturadas:
    - portal-detalhe.html
    - aba-partes.html
    - aba-andamentos.html
    - aba-peticoes.html
    - aba-decisoes.html
    - aba-sessao-virtual.html
    - aba-pauta.html
  anomalias_observadas: >
    Portal consta Min. Rosa Weber como relatora apesar da aposentadoria
    formal em outubro/2023. O snapshot preserva o que o portal disse na
    data da coleta; redistribuição provável a ser capturada em snapshot
    posterior. `orgao_julgador` nulo porque ainda não há composição
    definida para julgamento de mérito.
  dinamico: true

assinatura_digital:
  presente: false
  formato: sem_assinatura
  certificados: null

fonte_confiavel: pbm_s

observacoes: >
  Primeiro piloto B-pendente do KB-PD. Tema de Repercussão Geral 1148
  (Criminal). Snapshot coletado via curl com UA Mozilla/5.0 em
  2026-04-23T15:00:00Z. Nenhum L0 será gerado enquanto não houver
  acórdão publicado e trânsito em julgado — registro em
  watchlist/index.yaml governa recoleta. Abas AJAX baixadas
  individualmente como HTMLs irmãos; ver watchlist/README.md para
  política de recoleta e promoção.
```

---

## 9. Checklist de depósito (operação manual)

Ao depositar um documento novo em `raw/`:

```
[ ] 1. Arquivo binário salvo em raw/<tipo>/<id>.<ext>
[ ] 2. sha256sum calculado
[ ] 3. <id>.source.yaml criado com todos os campos obrigatórios
[ ] 4. encoding detectado (file, chardet ou enca) — conferir com declarado
[ ] 5. git status mostra binário + sidecar juntos
[ ] 6. Se PDF/EPUB: confirmar git lfs track funcionando (git check-attr filter)
[ ] 7. Commit único: "feat(raw): <id> — <descrição breve>"
```

---

## 10. Relações com outros documentos

- Etapa 0.5 (validação) — detalhada em `_AGENTS/AGENTS.md` §ETAPA 0.5
- Regra de encoding Planalto — `_AGENTS/AGENTS.md` §Encoding de atos normativos
- Schema canônico do front-matter de `inbox/` — `_AGENTS/schema-reference.md`
- Critérios de cobertura — `PLANO-INGESTAO.md` §Fase 1 /