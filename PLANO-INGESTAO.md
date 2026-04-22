# PLANO-INGESTAO.md
# KB-PD — Plano de Ingestão v1.2
# Fonte: KB-PD-plano-v3.md + decisões de setup (abril 2026)
# Versionar no Git. Atualizar a cada fase concluída.
#
# Changelog v1.1 → v1.2 (2026-04-22):
# Introduzido estágio raw/ como landing zone imutável por tipo (8 subpastas).
# Formalizadas Etapas 0 (registro de procedência via .source.yaml) e 0.5
# (validação de encoding/corrupção) como pré-condições absolutas da entrada
# no inbox/. Critério 1 (cobertura dos 8 tipos no bootstrap) agora é
# auditável via `ls raw/*/`. Arquivos atuais do inbox/ marcados como
# legado pré-v1.2 com sidecar retroativo de sha256:null. Git LFS habilitado
# para raw/**/*.pdf e raw/**/*.epub. Schema completo do sidecar e pipeline
# de 4 estágios em _AGENTS/raw-protocol.md.
#
# Changelog v1.0 → v1.1:
# Adicionado Critério 3c — terceiro caso de Tipo A (mutação jurisprudencial sem
# alteração de texto). Adicionadas extensões de schema: tipo de relação
# eficacia_condicionada / condiciona_eficacia e tipo de tensão
# norma_com_eficacia_condicionada. Caso Marco Civil art. 19 + ADI 6.031
# documentado como par de referência obrigatório.

---

## Status geral

| Fase | Descrição | Status |
|------|-----------|--------|
| 0 | Infraestrutura e repositório Git | ✅ Concluído |
| 0.5 | Landing zone raw/ + sidecar .source.yaml + LFS | 🟡 Em andamento — estrutura criada em 2026-04-22; **A-normativas = 10 documentos com sidecar v1.2 completo** (CF/1988, CP/1940, CPP/1941 + leis 12.737/2012, 12.965/2014, 13.718/2018, 13.964/2019, 14.132/2021, 14.155/2021, 14.188/2021 — as 3 legadas retrofited; faltam B, C, D, E, F, G, H) |
| 1 | Bootstrap do vocabulário | ⏳ Pendente — bloqueado pelo Critério 1 (cobertura dos 8 tipos em raw/) |
| 2 | Prompts de extração por tipo | ⏳ Pendente |
| 3 | Golden dataset inicial | ⏳ Pendente |
| 4 | Configuração da busca híbrida | ⏳ Pendente |
| 5 | Primeira ingestão em lote + baseline RAGAS | ⏳ Pendente |

---

## Fase 0.5 — Landing zone raw/ e validação de encoding

### Objetivo

Formalizar `raw/` como única porta de entrada do corpus e garantir cadeia de
custódia do binário original (URL de origem, data de baixa, SHA-256, encoding
real detectado) antes de qualquer transformação. Separar landing zone
(imutável) de corpus processado é a única forma de garantir reprodutibilidade
do pipeline sob reprocessamento.

### Componentes

1. **Estrutura de pastas**: `raw/A-normativas/` … `raw/H-pecas/` (8 subpastas
   espelhando os 8 source_types).
2. **Sidecar obrigatório** `.source.yaml` por arquivo, schema documentado em
   `_AGENTS/raw-protocol.md` §4. Sidecar com `sha256: null` permitido apenas
   para legado pré-v1.2; em todos os demais casos o pipeline bloqueia.
3. **Git LFS** para `raw/**/*.pdf` e `raw/**/*.epub` (ver `.gitattributes`).
4. **Etapa 0.5 bloqueante**: validação de encoding + hash + detecção de
   artefatos antes da Etapa 1. Thresholds conforme AGENTS.md §ETAPA 0.5.

### Critério de conclusão desta fase

Não há critério binário de "conclusão" — a Fase 0.5 é contínua: toda
ingestão futura depende dela. O que é verificável é a estrutura:

- [x] 8 subpastas raw/ criadas com .gitkeep
- [x] .gitattributes com filtros LFS para pdf/epub
- [x] _AGENTS/raw-protocol.md documentando o sidecar
- [x] 3 sidecars retroativos para legado pré-v1.2 RETROFITED para v1.2 completo
      (lei-12737/2012, lei-12965/2014, lei-14155/2021 — agora com sha256, ETag,
      Last-Modified, encoding_real_detectado e diagnostico_aj2021)
- [x] 7 sidecars v1.2 nativos (cf-1988-compilada, cp-2848-compilado,
      cpp-3689-compilado, lei-13718/2018, lei-13964/2019, lei-14132/2021,
      lei-14188/2021) — todos com cadeia de custódia HTTP completa
- [x] _AGENTS/hot-articles.yaml v0.2 — camada de priorização declarativa
      sobre L0, 43 artigos hot + 3 hot_laws + 10 pareamentos transversais
- [ ] git lfs install executado no Windows (Pedro — uma vez por máquina)
- [ ] Etapa 0.5 propriamente dita (validação bloqueante de mojibake score,
      sha256 match e ausência de artefatos) ainda não executada sobre os
      10 documentos em raw/A-normativas/ — destrava a Fase 1

---

## Fase 1 — Bootstrap do vocabulário

### Objetivo

Produzir o `schema/vocabulario.yaml` v0.1 estável o suficiente para não exigir
reestruturação significativa nas primeiras ingestões reais. Um vocabulário instável
no bootstrap é a falha mais cara do pipeline — propaga erro para todos os L0s da
primeira carga.

### Pré-condição obrigatória

**A partir da v1.2:** todo documento do corpus de bootstrap deve estar
depositado em `raw/<tipo>/` com sidecar `.source.yaml` válido (§4 de
`_AGENTS/raw-protocol.md`) ANTES de ser submetido à Etapa 0.5 de validação
de encoding, e esta ANTES da indução de vocabulário.

Pipeline de pré-condições em ordem:

```
raw/<tipo>/<id>.<ext>       ← depósito imutável
raw/<tipo>/<id>.source.yaml ← sidecar obrigatório (sha256, url, encoding)
            │
            ▼
Etapa 0.5 — validação bloqueante (AGENTS.md §ETAPA 0.5)
   - sha256 confere com sidecar
   - score de corrupção < 0.5%
   - sem artefatos de processo
            │
            ▼
Etapa 1 — conversão canônica → inbox/<id>.md
            │
            ▼
Indução de vocabulário (Fase 1 propriamente dita)
```

Documentos com encoding corrompido no bootstrap contaminam o vocabulário
induzido — os termos extraídos de texto corrompido produzem near-duplicates
espúrios que persistem como ruído no `vocabulario.yaml`.

Validar encoding antes de selecionar, não depois.

---

### Critérios de seleção do corpus de bootstrap

#### Critério 1 — Cobertura obrigatória de todos os 8 tipos

| Tipo | Mínimo | Máximo | Observação |
|------|--------|--------|------------|
| A — Normativas | 2 | 4 | Ver detalhamento abaixo |
| B — Jurisprudência | 3 | 5 | RE 1.055.941 obrigatório |
| C — ISO/NIST | 1 | 2 | ISO/IEC 27037 obrigatório |
| D — Resoluções | 1 | 2 | CNJ 615/2025 prioritário |
| E — Doutrina | 2 | 4 | Livro + artigo (dois formatos de citação) |
| F — Operacional | 1 | 2 | Com campo versao_ferramenta explícito |
| G — Próprio | 1 | 2 | Transcrição ou nota de pesquisa |
| H — Peças | 6 | 10 | Núcleo do bootstrap — ver Critério 2 |
| **Total** | **17** | **31** | **Faixa ideal: 20–25** |

O teto de 25 é mais importante que o piso de 17. Bootstrap com 30+ documentos
não melhora a qualidade do vocabulário e aumenta o tempo de revisão humana sem
ganho proporcional. Diversidade importa mais que volume.

**Auditoria de cobertura (v1.2):** verificável em um comando a partir da
landing zone `raw/`:

```bash
for tipo in raw/*/; do
  count=$(ls "$tipo" 2>/dev/null | grep -v '^\.gitkeep$' | grep -v '\.source\.yaml$' | wc -l)
  echo "$tipo: $count arquivos"
done
```

A Fase 1 só destrava quando cada um dos 8 tipos tiver ≥ mínimo da tabela
acima. Estado atual (2026-04-22, pós-rodada Trindade Normativa):
**A=10 (já ultrapassa o teto de 4 — ver nota abaixo)**, B=0, C=0, D=0, E=0,
F=0, G=0, H=0 — insuficiente para bootstrap por falta dos 7 outros tipos.

**Nota sobre A=10 vs. teto=4:** o teto de 4 do Critério 1 é orientativo para
o **bootstrap inicial do vocabulário**. A coleta agressiva de A foi decisão
deliberada para (a) cobrir os 3 diplomas-base do domínio penal (CF, CP, CPP)
+ todas as leis especiais que tipificam crimes digitais ou alteram CP/CPP;
(b) testar empiricamente as hipóteses de encoding e ordinal Planalto sob
diversidade de origem editorial; (c) construir o índice de hot-articles v0.2
com lastro nos textos integrais. Para o bootstrap propriamente dito (Fase 1),
basta selecionar 4 dos 10 — provavelmente CP+CPP+CF+Lei 14.155/2021 (ou
13.964/2019) para cobrir os três casos do Critério 3 (alteração inline,
estável e mutação jurisprudencial).

---

#### Critério 2 — Tipo H é o núcleo do bootstrap

Os vocabulários mais instáveis — `problema_juridico` e `teses_principais` — emergem
quase exclusivamente do Tipo H. Um bootstrap com poucos ou homogêneos documentos
Tipo H produz vocabulário raso que vai explodir em propostas de termos novos nas
primeiras ingestões reais.

Requisitos específicos para os documentos Tipo H selecionados:

**a) Mínimo de 2 pares dialéticos completos**
Inicial + contestação do mesmo processo ou do mesmo tipo de problema.
Sem isso, os campos `polo` e `par_dialetico_id` não são cobertos na indução
e o vocabulário não aprende a distinguir argumento de acusação de argumento
de defesa.

**b) Variedade de `problema_juridico`**
Ao menos 3 problemas jurídicos distintos entre os documentos selecionados.
Exemplos: espelhamento de WhatsApp, negativa de perícia, cadeia de custódia.
Não selecionar 6 contestações do mesmo tipo de caso.

**c) Variedade de `subtipo`**
Ao menos 3 subtipos diferentes: contestação, inicial, recurso, laudo.
Um corpus só de contestações não induz os padrões de outros subtipos.

**d) Ao menos 1 `resultado` conhecido**
Para que o campo `resultado` apareça com valor real (não só `desconhecido`)
na indução.

---

#### Critério 3 — Âncoras temporais e mutação jurisprudencial

Ao menos 2 documentos com marcos temporais claros e distintos — para que os
campos `valido_desde`/`valido_ate` sejam exercitados na indução. O bootstrap
deve cobrir os três casos distintos de Tipo A: alteração de texto com histórico
inline, normativo estável sem histórico, e mutação jurisprudencial sem alteração
de texto.

##### Critério 3a — Caso de referência obrigatório:

**Par Lei 12.737/2012 + Lei 14.155/2021 (art. 154-A CP)**

Este par é o exemplo canônico de histórico legislativo inline no domínio.

A Lei 12.737/2012 criou o art. 154-A com pena de detenção de 3 meses a 1 ano.
A Lei 14.155/2021 alterou a redação elevando a pena para 1 a 4 anos.

Quando convertido para .md a partir do Planalto, o texto frequentemente
inclui ambas as redações inline:

```
Art. 154-A. Invadir dispositivo informático de uso alheio...
Pena — detenção, de 1 (um) a 4 (quatro) anos, e multa.
(Redação dada pela Lei nº 14.155, de 2021)

Redação anterior:
Pena — detenção, de 3 (três) meses a 1 (um) ano, e multa.
(Incluído pela Lei nº 12.737, de 2012)
```

Este bloco inline é o problema central: um embedding que mistura as duas
redações responde "3 meses a 1 ano" para queries sobre a pena atual.

**Tratamento correto no pipeline:**

Redação vigente — entra em `corpus/A-normativas/`:
```yaml
id: cp-art154a-caput-redacao-2021
source_type: A
lei: "14.155/2021"
artigo: "154-A"
valido_desde: "2021-05-27"
valido_ate: "presente"
status: ativo
versao_anterior: cp-art154a-caput-redacao-2012
```

Redação anterior — vai para `superados/`:
```yaml
id: cp-art154a-caput-redacao-2012
source_type: A
lei: "12.737/2012"
artigo: "154-A"
valido_desde: "2012-11-30"
valido_ate: "2021-05-26"
status: superado
versao_posterior: cp-art154a-caput-redacao-2021
```

**Por que este par é ideal para o bootstrap:**
1. Testa a detecção automática dos marcadores "Redação dada pela Lei" e
   "Redação anterior:" na Etapa 1
2. Testa point-in-time retrieval: query com âncora 2019 deve retornar pena
   de 3 meses a 1 ano; query sem âncora deve retornar pena de 1 a 4 anos
3. Testa o link bidirecional `versao_anterior`/`versao_posterior`

##### Critério 3b — Normativo estável sem histórico legislativo inline:

Lei 12.965/2014 (Marco Civil da Internet) — sem alterações de redação inline
no corpo dos artigos. Calibra o pipeline para distinguir documentos que
precisam de separação de redações dos que não precisam, evitando falsos
positivos na detecção automática da Etapa 1.

ATENÇÃO: o Marco Civil não é um normativo "sem história" — ele é um normativo
com mutação jurisprudencial (ver Critério 3c abaixo). O que está ausente é
apenas o histórico legislativo inline no texto. A ingestão correta exige o
par com os L0s Tipo B condicionantes.

##### Critério 3c — Mutação jurisprudencial sem alteração de texto (terceiro caso):

Lei 12.965/2014 (Marco Civil), art. 19 — texto intacto desde 2014, eficácia
condicionada pelo STF. Este caso é estruturalmente diferente dos dois anteriores:

```
Lei 12.737/2012 → Lei 14.155/2021   = alteração de texto (redação inline)
  Solução: separação física de chunks + valido_ate no L0 superado

Marco Civil art. 19 → ADI 6.031 / RE 1.037.396
  = mutação jurisprudencial (texto intacto, eficácia alterada)
  Solução: campo relacoes com tipo eficacia_condicionada
           (o L0 normativo NÃO vai para superados/)
```

**Modelagem correta do L0 normativo:**

```yaml
id: mci-art19-caput
source_type: A
lei: "12.965/2014"
artigo: "19"
valido_desde: "2014-04-23"
valido_ate: "presente"
status: ativo
relacoes:
  - tipo: eficacia_condicionada
    id: stf-adi6031-holding
    nota: "STF condicionou responsabilidade civil de plataformas ao
           descumprimento de ordem judicial prévia de remoção"
  - tipo: eficacia_condicionada
    id: stf-re1037396-holding
    nota: "Tese de repercussão geral: plataformas respondem civilmente
           por conteúdo de terceiro quando descumprirem ordem judicial"
```

**Modelagem do L0 jurisprudencial condicionante (Tipo B):**

```yaml
id: stf-adi6031-holding
source_type: B
tribunal: STF
relacoes:
  - tipo: condiciona_eficacia
    id: mci-art19-caput
```

**Consequência para o L2 de síntese:**
O L2 do domínio `responsabilidade_plataformas` deve usar o tipo de tensão
`norma_com_eficacia_condicionada` — não `norma_vs_pratica` (que implica
conflito) nem ausência de tensão (que omite a condicionante):

```yaml
tensoes:
  - claim_a: mci-art19-caput
    claim_b: stf-adi6031-holding
    tipo_tensao: norma_com_eficacia_condicionada
    status_resolucao: resolvido_pelo_leading_case
    nota: "Art. 19 MCI não revogado — eficácia condicionada pelo STF:
           responsabilidade civil exige descumprimento de ordem judicial
           prévia de remoção (ADI 6.031 + RE 1.037.396)"
```

**Por que este caso é necessário no bootstrap:**
Sem ele, o pipeline não aprende a distinguir mutação jurisprudencial de
revogação — e vai propor incorretamente mover o L0 do art. 19 para
`superados/` quando encontrar a ADI 6.031 na harmonização.

**Par obrigatório:** se o Marco Civil art. 19 entrar no bootstrap como Tipo A,
a ADI 6.031 (ou o RE 1.037.396) deve entrar como Tipo B. Ingerir o art. 19
sem o L0 condicionante cria um L0 correto mas perigosamente incompleto.

---

#### Critério 4 — Cobertura das duas autoridades epistêmicas principais

O bootstrap precisa de documentos `vinculante` e `persuasivo` em proporção
que reflita o corpus real.

Proporção orientativa: 60% vinculante / 40% persuasivo.

Vinculante: Tipos A, D, B (repetitivo/vinculante STF/STJ)
Persuasivo: Tipos C, E, B (não-repetitivo)

---

#### Critério 5 — Diversidade de domínios, não profundidade

O bootstrap mapeia a variedade do espaço — não cobre um domínio exaustivamente.

Regra prática: se dois documentos candidatos cobrem o mesmo `problema_juridico`
com as mesmas `teses_principais`, selecionar apenas um para o bootstrap.
O segundo entra na primeira ingestão em lote.

---

### Documentos de referência obrigatória no bootstrap

Os documentos abaixo são obrigatórios por cobrirem casos de validação
específicos do pipeline. Sem eles, partes do vocabulário e do prompt de
extração não podem ser validadas antes da ingestão em lote.

| Documento | Tipo | Obrigatoriedade | O que valida |
|-----------|------|-----------------|--------------|
| Art. 154-A CP — redação Lei 14.155/2021 | A | Obrigatório | Redação vigente + valido_ate: "presente" |
| Art. 154-A CP — redação Lei 12.737/2012 | A | Obrigatório | Redação superada + separação de histórico inline |
| Lei 12.965/2014 art. 19 (Marco Civil) | A | Obrigatório | Mutação jurisprudencial + relacoes: eficacia_condicionada |
| RE 1.055.941/SP (STF) | B | Obrigatório | Yield mínimo B: ementa + holding + ratio + voto divergente Min. Marco Aurélio |
| HC 841.778/RS (STJ) | B | Obrigatório | Cadeia de custódia digital — leading case |
| ADI 6.031 ou RE 1.037.396 (STF) | B | Obrigatório (par com Marco Civil art. 19) | relacoes: condiciona_eficacia — mutação jurisprudencial |
| ISO/IEC 27037:2012 | C | Obrigatório | Requisitos prescritivos (shall/deve) vs. recomendatórios |
| CNJ Resolução 615/2025 | D | Prioritário | Resolução mais recente do escopo |
| 2 pares dialéticos completos (inicial + contestação) | H | Obrigatório | polo, par_dialetico_id, problema_juridico |

---

### Sequência de execução da Fase 1

```
1. Depositar corpus de bootstrap em raw/<tipo>/ (20–25 documentos, cobertura
   dos 8 tipos, um sidecar .source.yaml por arquivo)
2. Executar Etapa 0.5 em cada arquivo de raw/ (validação de encoding,
   conferência de sha256 com sidecar, detecção de artefatos)
3. Executar Etapa 1 de conversão canônica (raw/ → inbox/<id>.md com
   front-matter completo)
4. Executar prompt de indução de vocabulário (Cowork) sobre inbox/ validado
5. Revisar vocabulario.yaml candidato:
   - Ao menos 3 sinonimos_informais por termo
   - Nenhum termo que aparece em apenas 1 documento
   - Verificar near-duplicates na própria proposta
   - Cobrir problema_juridico, teses_principais, dominios, tipo_decisao, posicao_doutrinaria
6. Aprovar vocabulario.yaml v0.1
7. git add schema/vocabulario.yaml && git commit -m "feat: vocabulario.yaml v0.1 — bootstrap aprovado"
```

Somente após o commit do vocabulario.yaml v0.1 aprovado o pipeline de
extração de L0 é liberado. Nenhum L0 é extraído antes desta etapa.

---

## Fase 2 — Prompts de extração por tipo

### Sequência de desenvolvimento (por prioridade)

**Prioridade 1 — Tipo B (validar antes de qualquer uso em lote)**

O RE 1.055.941/SP é o caso de referência obrigatório. Produzir manualmente
os 4 L0s esperados como ground truth antes de escrever o prompt:
- L0-1: ementa
- L0-2: holding
- L0-3: ratio decidendi
- L0-4: voto divergente Min. Marco Aurélio (delimita o que NÃO foi decidido
  sobre dados cadastrais — informação crítica para fundamentação)

O prompt de Tipo B só é liberado para uso em lote após gerar os 4 L0s
corretos para este caso de referência.

**Prioridade 2 — Tipo A**
Foco: extração de `valido_desde` a partir do histórico de alterações e
separação de redações anteriores inline.

**Prioridade 3 — Tipo H**
Foco: identificação de teses como P1, extração de padrão argumentativo,
preenchimento de `polo` e `par_dialetico_id`.

**Prioridade 4 — Tipos C, D, E, F, G**
Em sequência, após validação dos três tipos prioritários.

---

## Fase 3 — Golden dataset inicial

### Meta: ~65 pares anotados

| Tipo de query | Pares | O que avalia |
|---------------|-------|--------------|
| normativa_simples | 15 | Precision Tipo A/D, BM25 em identificadores |
| multi_hop_juridico | 10 | Raciocínio cruzado A+B, context recall |
| temporal | 10 | Point-in-time retrieval, valido_desde/valido_ate |
| contrastante_autoridade | 10 | Distinção vinculante/persuasivo, campo tensoes L2 |
| padrao_argumentativo | 10 | Índice de padrões, query routing, Tipo H |
| expansao_vocabulario | 5 | Linguagem informal → vocabulário controlado |
| dialetico | 5 | par_dialetico_id, polo, view dialética |
| sem_resposta | 5 | Lacuna de cobertura, retrieval_confidence baixo |

Prioridade de preenchimento: temporal > contrastante_autoridade >
dialetico > sem_resposta (os quatro tipos que testam diferenciais
arquiteturais específicos da v3).

Preenchimento manual pelo especialista de domínio após primeira ingestão.
Não preencher com exemplos sintéticos — invalida a avaliação.

---

## Fase 4 — Configuração da busca híbrida

Componentes a integrar ao script de embedding existente:

- `rank-bm25` (Python) — busca esparsa, preservação de identificadores legais
- Fusão RRF (k=60) — combinação BM25 + semântico
- `bge-reranker-large` (BAAI) — cross-encoder sobre top-80, retorna top-10
- Pré-filtro de metadata: `valido_ate = "presente"`, `status = "ativo"`,
  `encoding_validated = true`

Validação obrigatória: confirmar que números de lei, processos e artigos
são capturados pelo BM25 mesmo quando o embedding os trata como tokens opacos.

---

## Fase 5 — Primeira ingestão em lote + baseline RAGAS

Executar sobre o corpus de bootstrap já processado na Fase 1 para validar
o pipeline completo antes de expandir para o corpus total.

Verificações obrigatórias ao final:
- Baseline RAGAS sobre o golden dataset inicial (Fase 3)
- Yield médio por source_type (queda sinaliza regressão no prompt)
- Status de ativação do índice de padrões por problema_juridico
- Documentos com flag yield_incompleto: true pendentes de revisão

---

## Extensões de schema identificadas durante o planejamento

Decisões de modelagem tomadas durante a seleção do corpus de bootstrap que
requerem atualização do `_AGENTS/schema-reference.md` antes da primeira ingestão.

### Extensão 1 — Dois novos tipos de relação (campo `relacoes` do Tipo A)

O enum `tipo` no campo `relacoes` do schema base cobre:
`revoga | especializa | fundamenta | aplica | contradiz`

Adicionar:

| Tipo novo | Direção | Quando usar |
|-----------|---------|-------------|
| `eficacia_condicionada` | L0 normativo → L0 jurisprudencial | Norma cujo âmbito de aplicação foi condicionado/redefinido por decisão judicial. O L0 normativo permanece ativo — não vai para superados/. |
| `condiciona_eficacia` | L0 jurisprudencial → L0 normativo | Decisão que redefine o âmbito de aplicação de uma norma. Link reverso obrigatório ao eficacia_condicionada correspondente. |

Sem esses dois tipos, o pipeline não consegue distinguir mutação jurisprudencial
de revogação — e pode propor incorretamente mover o L0 normativo para superados/.

### Extensão 2 — Novo tipo de tensão (campo `tensoes` do L2)

O enum `tipo_tensao` do schema L2 cobre:
`holding_vs_doutrina | tribunais_conflitantes | norma_vs_pratica | holding_vs_voto_divergente`

Adicionar:

| Tipo novo | Quando usar |
|-----------|-------------|
| `norma_com_eficacia_condicionada` | Norma textualmente vigente com âmbito de aplicação condicionado por leading case. Diferente de norma_vs_pratica (que implica conflito não resolvido) — aqui há resolução pelo leading case mas o texto permanece intacto. |

Sem esse tipo, o L2 de síntese vai classificar incorretamente como
`norma_vs_pratica` o que é uma relação de condicionamento resolvida.

---

## Notas operacionais do ambiente

### Limitações do sandbox Cowork (Windows bridge)

Três falhas confirmadas empiricamente durante o setup (abril 2026):

| Operação | Sintoma | Contramedida |
|----------|---------|--------------|
| `Write` de arquivo > ~500 bytes com acentuação | Truncagem em ~200 bytes no meio de palavra multibyte | `cat << 'EOF'` em bash |
| `Edit` de arquivo > ~500 bytes com acentuação | Mesma truncagem | `cat << 'EOF'` em bash (reescrita total) |
| `git init` / operações Git em path Windows montado | Escrita como NULs + lock preso + unlink bloqueado | Executar Git nativo no terminal Windows |

**Regra permanente:** toda operação Git deve ser executada em terminal
Windows nativo (cmd ou PowerShell), nunca no sandbox do Cowork.

**Regra permanente:** arquivos .md, .yaml e .txt de conteúdo jurídico em
português devem ser escritos via `cat << 'NOME_EOF'` em bash com aspas
simples no delimitador. Verificar tamanho com `wc -c` após escrita.

---

## Histórico de commits

| SHA-1 | Mensagem | Data |
|-------|----------|------|
| 34af1cb | chore: estrutura inicial KB-PD v3.0 | 2026-04-22 |
| f6a1686 | chore: forçar LF em todos os arquivos de texto (eol=lf) | 2026-04-22 |
| 458ef3a | docs: plano de ingestão v1.1 + extensões de schema (eficacia_condicionada, norma_com_eficacia_condicionada) | 2026-04-22 |
| 2f4083a | feat: ingestão Tipo A — leis 12.737/2012, 14.155/2021, 12.965/2014 + regra encoding Planalto (Windows-1252) | 2026-04-22 |
| (push e920512) | refactor: pipeline v1.2 — raw/ landing zone + sidecar source.yaml + etapas 0/0.5 formalizadas | 2026-04-22 |
| (push e920512) | feat: rodada CF/1988 + Lei 13.964/2019 — refutação da hipótese AJ-2021 v1 do bug ordinal | 2026-04-22 |
| (push e920512) | retrofit: 3 sidecars legados → v1.2 completo (sha256, ETag, Last-Modified, encoding_real) | 2026-04-22 |
| (push e920512) | raw(A): CP 2848/1940 compilado + sidecar (Etapa 0) — coexistência de templates ~6,5% bug | 2026-04-22 |
| (push e920512) | raw(A): CPP 3689/1941 compilado + sidecar (Etapa 0) — coexistência de templates ~30,4% bug | 2026-04-22 |
| (push e920512) | _AGENTS: hot-articles v0.2 — 14 mudanças aprovadas, 43 artigos hot + 3 hot_laws | 2026-04-22 |
| pendente | docs: AGENTS.md §155-170 — promove hipótese v3 (estratificação por bloco editorial) | 2026-04-22 |
| pendente | docs: PLANO-INGESTAO.md — Fase 0.5 com 10 documentos em A-normativas | 2026-04-22 |
| pendente | docs: STATUS.md — painel de bordo do projeto (consolidação) | 2026-04-22 |

---

*Documento gerado em 2026-04-22. Atualizado para v1.2 em 2026-04-22.*
*Atualizar status das fases a cada conclusão.*