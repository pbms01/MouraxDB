---
# schema-reference.md
# Referência canônica de front-matter YAML por source_type — KB-PD v3.0
# Carregado como contexto permanente em toda sessão do pipeline.
# Fonte: KB-PD-plano-v3.md, Seção 4.
# Não editar manualmente — alterações requerem atualização do plano-mestre e git commit.
---
## BASE COMPARTILHADA (todos os documentos, todos os tipos)
```yaml
id:                      # slug único gerado na ingestão (ex: cp-art154a-caput)
source_type:             # A | B | C | D | E | F | G | H
dominio:                 # vocabulário controlado induzido — ver schema\vocabulario.yaml
conversion_quality:      # nativo | alto | medio | baixo
encoding_validated:      # true | false — resultado da Etapa 0.5 (OBRIGATÓRIO)
                         # false = documento em quarentena, nenhum chunk gerado
autoridade_epistemica:   # vinculante | persuasivo | exemplificativo | proprio
confianca_extracao:      # alta | media | baixa
                         # Tipo G: nunca 'alta' — hardcoded para 'media'
chunking_regime:         # normativo | jurisprudencial | tecnico |
                         # doutrinario | argumentativo | proposicional | tecnico_quesito
# ── Temporalidade ──────────────────────────────────────────────────────────
vigencia:                # "YYYY-MM-DD" ou "indeterminado"
valido_desde:            # "YYYY-MM-DD" — início de validade desta versão
valido_ate:              # "YYYY-MM-DD" | "presente"
                         # queries sem âncora temporal filtram valido_ate == "presente"
versao_anterior:         # ID do L0 que esta versão substitui (null se primeira versão)
versao_posterior:        # ID do L0 que substitui esta versão (null se versão atual)
# ── Status e derivação ────────────────────────────────────────────────────
status:                  # ativo | revogado | superado | revisando
derivado_por:            # lista de IDs de L1/L2/L3 que dependem deste L0
# ── Proveniência ──────────────────────────────────────────────────────────
converted_at:            # "YYYY-MM-DD"
converted_from:          # pdf | docx | pptx | xlsx | audio | video | imagem | nativo
citacao_canonica:        # string formatada — ver _AGENTS\citacoes-canonicas.md
```
---
## TIPO A — Normativas primárias brasileiras
Pasta: corpus\A-normativas\
Chunking: por artigo/parágrafo/inciso como unidade atômica
Autoridade: vinculante
ATENÇÃO: histórico legislativo inline deve ser separado em chunks distintos antes de qualquer
embedding — redação vigente em corpus\, redações anteriores em superados\ com valido_ate preenchido.
```yaml
# Extensão Tipo A (adicionar ao base)
lei:
artigo:
paragrafo:
inciso:
alinea:
redacao_vigente_desde:   # "YYYY-MM-DD"
alterado_por:            # lista de leis
relacoes:
  - tipo:                # revoga | especializa | fundamenta | aplica | contradiz
                         # eficacia_condicionada | condiciona_eficacia
    id:                  # ID do L0 relacionado
    nota:                # max 100 tokens — contexto da relação (obrigatório para
                         # eficacia_condicionada e condiciona_eficacia)
```
> **Tipos de relação para mutação jurisprudencial (sem alteração de texto):**
>
> `eficacia_condicionada` (L0 normativo → L0 jurisprudencial): norma textualmente
> vigente cujo âmbito de aplicação foi condicionado/redefinido por decisão judicial.
> O L0 normativo permanece ativo — NÃO vai para superados/.
> Exemplo: Marco Civil art. 19 → ADI 6.031 (STF condicionou responsabilidade civil
> de plataformas ao descumprimento de ordem judicial prévia de remoção).
>
> `condiciona_eficacia` (L0 jurisprudencial → L0 normativo): decisão que redefine
> o âmbito de aplicação de uma norma. Link reverso obrigatório ao
> eficacia_condicionada correspondente.
>
> **Distinção crítica:** mutação jurisprudencial ≠ revogação.
> Se o pipeline encontrar um L0 normativo com relacao eficacia_condicionada
> durante a harmonização, NÃO propor status: superado — o texto da norma
> continua vigente. A eficácia é que foi condicionada.
Yield mínimo: 1 L0 por unidade normativa independente (artigo/inciso/alínea).
---
## TIPO B — Jurisprudência
Pasta: corpus\B-jurisprudencia\
Chunking: 4 partes obrigatórias — ementa, holding, ratio decidendi, voto divergente (quando presente)
Autoridade: vinculante (repetitivo/vinculante STF/STJ) | persuasivo
YIELD MÍNIMO OBRIGATÓRIO: 3 L0s por acórdão (ementa + holding + ratio).
Se < 3 → Fila A com flag yield_incompleto: true. NÃO é erro fatal, mas exige revisão humana.
4º L0 (voto divergente): opcional, autoridade_epistemica: persuasivo, tipo_decisao: voto_divergente.
```yaml
# Extensão Tipo B (adicionar ao base)
tribunal:
numero:
ano:
relator:
tipo_decisao:            # acordao | decisao_monocratica | sumula | tese_repetitiva
                         # | voto_divergente
vinculante:              # true | false
tema_repetitivo:         # número, se aplicável
holding:                 # texto do holding (max 200 tokens)
ratio_decidendi_resumo:  # texto da ratio (max 300 tokens)
votos_divergentes:
  - ministro:
    posicao_resumo:      # max 150 tokens
    l0_id:               # ID do L0 do voto divergente
```
Caso de referência obrigatório para validação do prompt Tipo B: RE 1.055.941/SP (STF).
Contém os 4 componentes: ementa, holding, ratio, voto divergente Min. Marco Aurélio.
---
## TIPO C — Normas técnicas ISO/NIST
Pasta: corpus\C-iso\
Chunking: por requisito prescritivo (shall/deve). Notas explicativas são contexto (P3), não L0.
Autoridade: persuasivo
```yaml
# Extensão Tipo C (adicionar ao base)
norma:                   # ex: "ISO/IEC 27037:2012"
secao:
subsecao:
tipo_requisito:          # prescritivo | recomendatorio | definitorio
```
---
## TIPO D — Resoluções e atos administrativos
Pasta: corpus\D-resolucoes\
Chunking: por dispositivo relevante
Autoridade: vinculante no âmbito institucional correspondente
```yaml
# Extensão Tipo D — mesma estrutura do Tipo A
# (usar campos lei/artigo/paragrafo/inciso com nome do órgão no campo lei)
```
---
## TIPO E — Doutrina especializada
Pasta: corpus\E-doutrina\
Chunking: por argumento desenvolvido. Parágrafos com conectivos de desenvolvimento
("Portanto", "Assim", "Nesse sentido") são agregados ao parágrafo anterior no mesmo chunk.
Autoridade: persuasivo
ATENÇÃO: artefatos de processo frequentes (anotações de revisor, bullets incompletos).
Etapa 0.5 obrigatória antes de qualquer processamento.
```yaml
# Extensão Tipo E (adicionar ao base)
autor:
obra:
edicao:
paginas:
posicao_doutrinaria:     # majoritaria | minoritaria | isolada | indeterminada
```
---
## TIPO F — Operacional/ferramental
Pasta: corpus\F-operacional\
Chunking: por procedimento. L0 no formato "protocolo + limitação conhecida".
Autoridade: exemplificativo
RISCO ATIVO: versões de ferramentas mudam capacidades substancialmente.
Orientação baseada em versão desatualizada pode ser ativamente incorreta, não apenas imprecisa.
```yaml
# Extensão Tipo F (adicionar ao base) — campos obrigatórios sem exceção
ferramenta:
versao_ferramenta:
sistema_alvo:              # iOS | Android | Windows | Linux | cloud | generico
limitacao_conhecida:
data_verificacao:          # "YYYY-MM-DD" — última verificação de atualidade
ciclo_revisao_meses:       # 6 | 12 | 18
# Cowork monitora data_verificacao + ciclo_revisao_meses e gera staleness_alert
# quando vencimento se aproxima (30 dias). Reportado em schema\CORPUS_HEALTH.md.
```
---
## TIPO G — Conhecimento próprio
Pasta: corpus\G-proprio\
Chunking: por tópico coeso (segmentação LLM-assistida)
Autoridade: proprio
REGRA ABSOLUTA: confianca_extracao NUNCA é 'alta' — hardcoded para 'media'. Sem exceção.
REGRA DO LOOP: nenhum output do próprio sistema entra como Tipo G sem verificação
contra fonte primária. Outputs da KB são referências para busca, nunca fontes para ingestão.
ATENÇÃO: transcrições Claude contêm artefatos de processo ("aguarde, reformulando...",
prompts intermediários). Etapa 0.5 obrigatória.
```yaml
# Extensão Tipo G (adicionar ao base)
origem:                          # transcript | curso | slide | nota | analise_caso
sessao_id:
verificacao_fonte_primaria:      # true | false — obrigatório antes de commit
```
---
## TIPO H — Peças processuais
Pasta: corpus\H-pecas\
Chunking: regime argumentativo — teses como P1, argumentos de suporte como P2
Autoridade: proprio (peça própria) | persuasivo (peça de terceiro)
DISTINÇÃO EPISTÊMICA: peças não são fontes de proposições — são demonstrações de método.
O valor a extrair é o padrão argumentativo, não o claim de verdade.
Dois índices vetoriais distintos: índice de peças + índice de padrões.
```yaml
# Extensão Tipo H (adicionar ao base)
subtipo:               # contestacao | inicial | recurso | parecer | laudo |
                       # manifestacao | embargos | agravo | outro
area:                  # vocabulário controlado induzido
problema_juridico:     # vocabulário controlado induzido
resultado:             # favoravel | desfavoravel | parcial | desconhecido
                       # quando atualizado de 'desconhecido': dispara re-indexação
instancia:             # primeira | segunda | stj | stf | arbitral
data_producao:         # "YYYY-MM"
metodologia:           # ARPC | SCARF | convencional | outro
teses_principais:      # lista — vocabulário controlado induzido
l0s_utilizados:        # lista de IDs de L0s aplicados na peça
l0s_gerados:           # lista de IDs de L0s novos introduzidos pela peça
par_dialetico_id:      # ID da peça H do polo oposto (null se par indisponível)
polo:                  # acusacao | defesa | autor | reu | neutro
```
Subtipos e regimes de chunking:
- contestacao / inicial: regime argumentativo — P1=tese, P2=argumento de suporte
- laudo pericial: regime tecnico_quesito — P1=par pergunta/resposta, P2=fundamento técnico
- parecer jurídico: regime proposicional — P1=proposição sustentada, P2=argumento
- recurso / embargos: regime argumentativo — P1=ponto de insurgência, P2=argumento
Yield mínimo:
- contestacao/inicial: ao menos 1 tese identificada
- laudo: ao menos 1 par pergunta/resposta
Threshold de ativação do índice de padrões: ≥5 peças com resultado conhecido (não 'desconhecido')
por problema_juridico. Abaixo disso: degradação graciosa com fallback para índice normativo-doutrinário.
---
## CAMPO tensoes — extensão de L2 (sínteses temáticas)
Quando um subdomínio contém L0s em posições incompatíveis, o campo tensoes é OBRIGATÓRIO.
Tensões não são anotações opcionais — são parte constitutiva da síntese L2.
```yaml
# Campos adicionais no front-matter de L2
tensoes:
  - claim_a:            # ID do L0 de autoridade superior
    claim_b:            # ID do L0 divergente
    tipo_tensao:        # holding_vs_doutrina | tribunais_conflitantes | norma_vs_pratica
                        # | holding_vs_voto_divergente | norma_com_eficacia_condicionada
    status_resolucao:   # resolvido_pelo_leading_case | questao_aberta |
                        # divergencia_doutrinaria
    nota:               # max 100 tokens — descrição em linguagem natural
```
> **Tipo de tensão norma_com_eficacia_condicionada:**
> Usar quando uma norma textualmente vigente tem seu âmbito de aplicação
> condicionado por leading case — o texto permanece intacto mas a eficácia
> foi redefinida pelo STF/STJ.
>
> Diferente de norma_vs_pratica (conflito não resolvido entre norma e aplicação
> real) — aqui há resolução pelo leading case com status_resolucao:
> resolvido_pelo_leading_case.
>
> Exemplo canônico: Marco Civil art. 19 + ADI 6.031 (STF).
> O campo nota do tensoes deve identificar o leading case e resumir a condição.
---
## REGRAS TRANSVERSAIS DE TEMPORALIDADE
- valido_desde / valido_ate habilitam point-in-time retrieval determinístico
- Queries sem âncora temporal: filtro automático valido_ate == "presente"
- Queries com âncora: valido_desde <= data_query AND valido_ate >= data_query
- L0 corrigido NUNCA é deletado: versão anterior → superados\ com status: superado,
  valido_ate = data da correção, link bidirecional via versao_posterior
---
## PIRÂMIDE DE DESTILAÇÃO (referência rápida)
L0 → nota atômica canônica. Um claim verificável. Imutável após commit. Unidade mínima de citação.
L1 → claim estruturado: [sujeito][predicado normativo][objeto][condição][fonte]. ~50 tokens.
     Campo obrigatório: l0_origem (ID do L0 de origem).
L2 → síntese temática. 300–500 tokens. Unidade de busca RAG padrão.
     Campos obrigatórios: l0s_origem (lista de IDs) + tensoes (quando aplicável).
L3 → context-injection snippet. 500–1.200 tokens. Vai no system prompt.
     Piso: domínio precisa de ≥10 L0s únicos para gerar L3.
     Teto: 1.200 tokens — se exceder, subdividir o domínio.
     Campo obrigatório: l0s_representativos (lista de IDs mais representativos).
---
## HIERARQUIA DE CHUNKS (referência rápida)
P0 → documento inteiro (contexto máximo, raramente recuperado diretamente)
P1 → seção / tese / ponto (unidade de argumento)
P2 → parágrafo / argumento (nível de busca — similaridade calculada aqui)
     LIMITE: máximo 800 tokens. Acima disso: subdivisão por janela deslizante, overlap 15%.
     Overlap preserva continuidade de frases com conectivos de desenvolvimento.
L0 → claim atômico (nível canônico — unidade de commit, versionamento e citação)
