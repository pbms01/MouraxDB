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

## 8. Três exemplos anotados

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

### 8.2 PDF assinado de acórdão STF (Tipo B, PDF canônico)

```yaml
# raw/B-jurisprudencia/re-1037396-tema987-stf.source.yaml
arquivo: re-1037396-tema987-stf.pdf
tipo: B
url_origem: https://portal.stf.jus.br/processos/downloadPeca.asp?id=...
baixado_em: "2026-04-22T14:12:00-03:00"
baixado_por: pedro.mourao
sha256: a12b3c4d5e6f7081a2b3c4d5e6f70819a0b1c2d3e4f5061728394a5b6c7d8e9f
encoding_declarado_http: null
encoding_real_detectado: null       # PDF não aplica
conversao_prevista: "pdf→md via pdftotext -layout"
paginas: 487
idioma: ptBR
licenca: "domínio público (decisão judicial pública)"
observacoes: >
  PDF assinado digitalmente pelo STF — paginação oficial preservada.
  Fonte canônica = PDF (HTML do portal é renderização parcial).
  Verificar assinatura digital com `pdfsig` antes da Etapa 1.
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
- Critérios de cobertura — `PLANO-INGESTAO.md` §Fase 1 / Critério 1

