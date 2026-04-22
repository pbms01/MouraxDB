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
## ETAPA 0.5 — PRÉ-CONDIÇÃO BLOQUEANTE (executa em TODO documento, sem exceção)
1. Verificar encoding: detectar padrões de corrupção UTF-8→Latin-1 (ex: "ÃÃ§Ã£o" em vez de "ação")
   - Score > 2% de tokens afetados → quarantine\encoding-artifacts\ + encoding_validated: false
   - Score 0.5–2% → warning + revisão manual recomendada
   - Score < 0.5% → encoding_validated: true, prossegue
2. Verificar artefatos de processo: ((VERIFICAR)), [[notas internas]], RASCUNHO, linhas com ??, (TIRAR DA
   - Qualquer match → quarantine\encoding-artifacts\ com lista de ocorrências
3. Documento só avança com encoding_validated: true no front-matter YAML.
4. PROIBIDO limpeza automatizada — risco de remoção de conteúdo legítimo em texto jurídico.
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
O portal Planalto serve HTML em Windows-1252 (CP1252), não ISO-8859-1.
A diferença é crítica: bytes 0x80–0x9F existem no CP1252 mas não no Latin-1.
Caracteres afetados: aspas tipográficas “” (0x93/0x94), en-dash – (0x96),
elipse … (0x85). Com -f ISO-8859-1 esses bytes são convertidos silenciosamente
para símbolos incorretos sem abortar — perda invisível e sem flag de erro.
Regra permanente: usar SEMPRE iconv -f WINDOWS-1252 -t UTF-8 para qualquer
ato do Planalto, independentemente do que o meta charset declare.
Validado empiricamente em: Lei 12.737/2012, Lei 14.155/2021, Lei 12.965/2014.
Aplicável a: CP, CPP, leis ordinárias, medidas provisórias, decretos do Planalto.
Se o arquivo inteiro precisar ser reescrito via heredoc por causa do risco de
truncagem, reescrever preservando todas as seções existentes. Verificar com
wc -c antes e depois — o arquivo deve crescer, nunca diminuir.
## REFERÊNCIAS INTERNAS
- Schema canônico completo: _AGENTS\schema-reference.md
- Formatos de citação por tipo: _AGENTS\citacoes-canonicas.md
- Vocabulário ativo: schema\vocabulario.yaml
- Golden dataset: schema\golden_dataset.yaml
