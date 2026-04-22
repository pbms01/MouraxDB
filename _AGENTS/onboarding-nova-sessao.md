# PROMPT DE ONBOARDING — KB-PD (nova sessão)

> Cole este prompt inteiro na primeira mensagem da nova sessão Cowork.
> Última atualização: 2026-04-22 (após ingestão de Lei 12.737/2012, Lei 14.155/2021, Lei 12.965/2014).

---

## 1. Quem eu sou e o contexto operacional

Sou Pedro Mourão, Promotor de Justiça no MPRJ, especialista em crimes digitais, prova digital e IA aplicada ao direito. Desenvolvo o **KB-PD (Knowledge Base de Prova Digital)** — pipeline RAG jurídico com distilação hierárquica L0→L1→L2→L3, rodando em Windows 11, sandbox Linux para operações de bash/iconv/python.

Diretório-raiz do projeto: `C:\Users\Membro\MouraxDB` (bash path: `/sessions/<...>/mnt/MouraxDB/`).

Preferências de interação: denso, técnico-colaborativo, visual quando ajudar (SVG/tabela/diagrama sem pedir permissão), sempre confirmar fundamento normativo com precisão (artigo/inciso/lei/julgado), sempre pesquisar online quando precisão for crítica, apontar ambiguidade antes de responder.

---

## 2. Arquitetura atual do repositório (estado em 2026-04-22)

```
C:\Users\Membro\MouraxDB\
├── _AGENTS\
│   ├── AGENTS.md                      # 5.679 B / 74 L — convenções operacionais
│   ├── schema-reference.md            # 13.934 B / 260 L — schema canônico, 14 seções
│   ├── citacoes-canonicas.md          # formatos de citação por tipo
│   └── onboarding-nova-sessao.md      # ESTE arquivo
├── schema\
│   ├── vocabulario.yaml               # vocabulário ativo
│   └── golden_dataset.yaml
├── inbox\                             # arquivos prontos para ingestão no pipeline
│   ├── lei-12737-2012.md  (4.769 B)   # Carolina Dieckmann, 154-A/154-B CP originais
│   ├── lei-14155-2021.md  (6.008 B)   # altera 154-A, 155 §4º-B, 171, CPP 70
│   └── lei-12965-2014.md  (47.333 B)  # Marco Civil, 38 arts, art. 19 eficácia condicionada
└── (demais diretórios do pipeline L0/L1/L2/L3 quando existirem)
```

---

## 3. Taxonomia source_type (não alterar)

| Tipo | Escopo |
|---|---|
| A | Normativas (leis, MPs, decretos, CP, CPP) |
| B | Jurisprudência (STF, STJ, tribunais superiores e estaduais) |
| C | ISO/NIST (27037, 27041, 27042, SP 800-series) |
| D | Resoluções CNJ/CNMP (615/2025 etc.) |
| E | Doutrina (artigos acadêmicos, manuais) |
| F | Operacional (manuais Cellebrite UFED, runbooks forenses) |
| G | Próprio (material do autor — cursos, artigos) |
| H | Peças processuais (modelos, decisões marcantes) |

---

## 4. Regras operacionais inelutáveis

### 4.1 Encoding Planalto (crítico)
O portal planalto.gov.br serve HTML em **Windows-1252 (CP1252)**, NÃO ISO-8859-1. Diferença é real: bytes 0x80–0x9F existem no CP1252 mas não no Latin-1. Afetados: aspas tipográficas "" (0x93/0x94), en-dash – (0x96), elipse … (0x85). Com `-f ISO-8859-1` esses bytes são convertidos silenciosamente para símbolos incorretos sem flag de erro — perda invisível.
**Regra permanente:** sempre `iconv -f WINDOWS-1252 -t UTF-8` para qualquer ato do Planalto, independentemente do que o meta charset declare. Validado em 3 leis (12.737/2012, 14.155/2021, 12.965/2014).

### 4.2 Sandbox-Windows bridge (escrita com acentuação)
Write tool pode truncar arquivos >500 bytes com acentuação densa no Windows. Solução canônica: `cat << 'EOF' > destino` via bash. Para arquivos grandes já existentes, preferir split N-partes + cat (operação atômica, previsível, sem risco de truncagem silenciosa).

### 4.3 Etapa 0.5 — validação de encoding bloqueante
- corrupção > 2% → **bloqueia** pipeline
- corrupção 0.5–2% → warning
- corrupção < 0.5% → passa

Contar via Python (bytes inesperados / total) antes de marcar `encoding_validated: true` no front-matter.

### 4.4 Preservação de fidelidade ao texto original
Nunca "corrigir" o que parece bug (ex.: "200o" e "133o" em Lei 14.155/2021 — erro de digitação do próprio Planalto; art. 12 duplicado no Marco Civil por MP 1.068/2021 rejeitada). Fidelidade > limpeza.

---

## 5. Schema de front-matter canônico (source_type A — normativas)

```yaml
---
id: lei-NNNNN-YYYY
source_type: A
dominio: <domínio>
conversion_quality: alto
encoding_validated: true
autoridade_epistemica: vinculante
confianca_extracao: alta
chunking_regime: normativo
vigencia: "YYYY-MM-DD"
valido_desde: "YYYY-MM-DD"
valido_ate: "presente" | "YYYY-MM-DD"
versao_anterior: null
versao_posterior: null
status: ativo | superado | revogado
derivado_por: []
converted_at: "YYYY-MM-DD"
converted_from: html
citacao_canonica: "Lei N.º NNNNN/YYYY"
lei: "NNNNN/YYYY"
ementa: "..."
artigos_incluidos: todos
observacoes: "..."
observacoes_chunking: "..."   # quando houver MP rejeitada, eficácia condicionada etc.
---
```

### Extensões recentes do schema (já em schema-reference.md)
- **Relações L2:** `eficacia_condicionada`, `condiciona_eficacia`
- **Tipo de tensão L3:** `norma_com_eficacia_condicionada`
- **Caso padrão:** Marco Civil art. 19 ↔ ADI 6.031 / RE 1.037.396

---

## 6. Inbox\ — itens depositados e prontos para pipeline

| Arquivo | Conteúdo | Peculiaridades |
|---|---|---|
| `lei-12737-2012.md` | Carolina Dieckmann: arts. 154-A/154-B CP originais | — |
| `lei-14155-2021.md` | altera 154-A, 155 §4º-B (furto eletrônico), 171 §2º-A (estelionato eletrônico), CPP art. 70 §4º | preserva bugs "200o"/"133o" do Planalto |
| `lei-12965-2014.md` | Marco Civil: 38 arts, 6 capítulos, 6 seções | art. 12 e incisos VII/VIII do art. 5º duplicados (MP 1.068/2021 rejeitada); arts. 8º-A/B/C/D e 28-A como status: superado com valido_ate: 2021-10-27; art. 19 eficácia condicionada |

---

## 7. O que foi feito na sessão anterior (resumo)

1. Verificada extensão de `schema-reference.md` com `eficacia_condicionada`/`condiciona_eficacia` e `norma_com_eficacia_condicionada` (230 → 260 linhas)
2. Extraídas e convertidas três leis do Planalto HTML → MD com YAML front-matter
3. Descoberto empiricamente que Planalto usa CP1252 (não ISO-8859-1) — após perda silenciosa de 0x93/0x94 na Lei 12.737
4. Adicionada subseção "### Encoding de atos normativos do Planalto (planalto.gov.br)" ao AGENTS.md (4.695 → 5.679 B)
5. Adicionado campo `observacoes_chunking` ao front-matter do Marco Civil (46.717 → 47.333 B) via split 3-partes + cat

---

## 8. Próximos passos sugeridos (escolher um)

**A. Processar inbox\ → L0**
Gerar chunks atômicos por artigo das três leis, rodar Etapa 0.5 em cada, popular L0 com metadata herdada do front-matter. Tratar duplicatas do Marco Civil (MP 1.068/2021) com `status: superado` e `valido_ate: 2021-10-27`.

**B. Ingerir jurisprudência condicionante (source_type B)**
ADI 6.031 e RE 1.037.396 (Tema 987 de Repercussão Geral) como normas condicionantes do art. 19 do Marco Civil. Criar par dialético L2.

**C. Completar a trilha normativa de crimes digitais**
Próximos alvos: arts. 147-A (stalking), 147-B (violência psicológica), 218-C (pornografia não consensual) CP; Leis 14.478/2022 (criptoativos), 15.123/2025 (supostamente a mais recente — confirmar por busca).

**D. Ingerir CPP completo (arts. relevantes a prova digital)**
Arts. 6º, 7º, 13-A, 13-B, 158 e seguintes, 240, 241 (busca e apreensão), 282 (cadeia de custódia pós-Lei 13.964/2019).

**E. Ingerir Resolução CNJ 615/2025 (source_type D)**
Marco regulatório de IA no Judiciário brasileiro — relevante para o eixo APOIA/TRF2.

---

## 9. Forma de trabalho

- **Nunca resumir ou truncar** texto legal em operações cirúrgicas — preservar byte a byte
- Usar `TaskCreate`/`TaskUpdate` para workflows multi-passos
- Heredoc via bash quando risco de truncagem do Write tool
- `wc -c` antes e depois de qualquer edição destrutiva — arquivos devem crescer (ou manter), nunca encolher sem intenção explícita
- Reportar tamanho antes/depois em cada operação
- Confirmar fundamento normativo com precisão em análises jurídicas
- Pesquisar online antes de afirmar vigência/revogação

---

## 10. Comando de verificação inicial (rodar na nova sessão)

```bash
# Confirmar estrutura básica do projeto
wc -c /sessions/<SID>/mnt/MouraxDB/_AGENTS/AGENTS.md
wc -c /sessions/<SID>/mnt/MouraxDB/_AGENTS/schema-reference.md
ls -la /sessions/<SID>/mnt/MouraxDB/inbox/
```

Esperado:
- AGENTS.md ≥ 5.679 B
- schema-reference.md ≥ 13.934 B
- inbox/ com 3 arquivos (12737, 14155, 12965)
