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
B: jurisprudência — 3 L0s obrigatórios por acórdão (ementa + holding + ratio) + 1 opcional (voto divergente), autoridade: vinculante ou persuasivo
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
### Encoding de atos normativos do Planalto (planalto.gov.br)
**Política aplicada na Etapa 1 do pipeline** (conversão raw/ → inbox/).
O portal Planalto serve HTML em Windows-1252 (CP1252), não ISO-8859-1.
A diferença é crítica: bytes 0x80–0x9F existem no CP1252 mas não no Latin-1.
Caracteres afetados: aspas tipográficas “” (0x93/0x94), en-dash – (0x96),
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
O Planalto apresenta ordinais do fecho de lei de duas formas distintas,
e essa variação NÃO é universal do portal — correlaciona com a gestão da
Subchefia para Assuntos Jurídicos em cada período.
- Forma correta (caractere U+00BA masculine ordinal indicator): "197º", "130º"
- Forma com bug (HTML `<u><sup>o</sup></u>` sem o caractere º real): "200o", "133o"
Confirmado empiricamente (base ampliada pelo retrofit v1.2 de 2026-04-22 — 2 data points novos + 1 confirmação byte-a-byte):
- Bug presente: Lei 14.132/2021, Lei 14.155/2021, Lei 14.188/2021 (leis 2021, assinatura Bolsonaro). Na 14.155/2021 o fecho literal é "Brasília,  27  de maio de 2021; 200<u><sup>o</sup></u> da Independência e 133<u><sup>o</sup></u> da República" — 2 ocorrências verificadas byte-a-byte em 2026-04-22 (sha256 1a6be934…2d73).
- Bug ausente: Lei 13.718/2018 (assinatura Dias Toffoli em exercício da Presidência, 24/09/2018); Lei 12.737/2012 (assinatura Dilma, 30/11/2012 — data point novo do retrofit 2026-04-22); Lei 12.965/2014 (assinatura Dilma, 23/04/2014 — data point novo do retrofit 2026-04-22). Nas três, ordinais aparecem como 'º' UTF-8 real.

Hipótese em teste: o bug correlaciona com período/gestão, não com o portal como sistema. 6/6 data points atuais são consistentes com "bug introduzido no template do Planalto em 2021 (AJ-2021, gestão Bolsonaro)". Nenhum contraexemplo até o momento. Alvos para falsear: leis sancionadas em 2019–2020 (Bolsonaro pré-AJ-2021) e em 2015–2017 (Temer).
Regra do pipeline: o extrator NUNCA "corrige" a forma ordinal — preserva
exatamente como veio do HTML. Duplicações de artigo (ex: Marco Civil art. 12
duplicado por MP 1.068/2021 rejeitada), erros de digitação oficiais e qualquer
outra "anomalia" do Planalto também são preservados byte a byte na Etapa 1.
A política de fidelidade está acima da política de limpeza: qualquer
correção é decisão humana editorial a ser feita em etapa posterior,
nunca no pipeline automatizado.
## REFERÊNCIAS INTERNAS
- Protocolo da landing zone raw/ (sidecar .source.yaml + pipeline): _AGENTS\raw-protocol.md
- Schema canônico completo: _AGENTS\schema-reference.md
- Formatos de citação por tipo: _AGENTS\citacoes-canonicas.md
- Vocabulário ativo: schema\vocabulario.yaml
- Golden dataset: schema\golden_dataset.yaml
- Plano de ingestão e fases: PLANO-INGESTAO.md
