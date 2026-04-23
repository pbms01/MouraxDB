# watchlist/ — Casos pendentes de julgamento

Camada de **governança** para processos em tramitação no STF/STJ (ou
qualquer tribunal cujo acompanhamento pré-trânsito faça sentido para o
KB-PD). Complementa `raw/B-jurisprudencia/` sem contaminá-lo com
material que pode ser superado pela tese definitiva.

## Por que existe

Casos pendentes têm propriedades que os distinguem de acórdãos
transitados em julgado (schema em `_AGENTS/raw-protocol.md` §4.4.1):

1. **Fonte é HTML dinâmico**, não PDF assinado.
2. **Ativo é alvo móvel** — a página muda ao longo do tempo.
3. **Sem assinatura criptográfica** na origem.
4. **Não geram L0** — não entram em `corpus/` até trânsito em julgado.

Separação de responsabilidades:

| Diretório | Função |
|---|---|
| `raw/B-jurisprudencia/<TRIBUNAL>/<CLASSE-NUM>/<YYYY-MM-DDTHH-MM-SSZ>/` | **depósito** dos snapshots (dado) |
| `watchlist/` | **governança** — quais casos, quando recoletar, quando promover |

## Quando adicionar uma entry

Incluir um caso em `watchlist/index.yaml` sempre que:

- Há interesse do KB-PD em acompanhar a definição da tese (ex: tema
  recente em prova digital, direito penal digital, compliance).
- O caso ainda não teve acórdão publicado com trânsito em julgado.
- A autoridade epistêmica esperada justifica rastreamento contínuo:
  STF com RG reconhecida, STJ em repetitivo, ADI/ADPF, casos com
  efeito vinculante projetado.

Casos sem acórdão mas sem interesse de acompanhamento NÃO vão para
watchlist — ficam fora do escopo do KB-PD.

## Política de recoleta

Um snapshot representa o estado do processo em um momento T.
Recoletar novo snapshot quando qualquer uma das condições se
verifica:

- **Mudança de `estado_processual`** (autuado → com_RG_reconhecida →
  sob_vista → em_sessao_virtual → julgado_pendente_publicacao etc.).
- **Movimentação significativa** documentada em `aba-andamentos`
  (decisão monocrática, voto, pedido de vista, redistribuição,
  suspensão).
- **Último snapshot com mais de 6 meses** (cap de *stale*).

Cada recoleta cria um **novo diretório** `<YYYY-MM-DDTHH-MM-SSZ>/`
dentro da pasta do processo. Snapshots antigos NÃO são apagados —
preservam a trajetória e permitem comparação diacrônica.

## Gate de promoção para L0

Um caso sai do watchlist e entra em `corpus/` quando TODAS as
condições abaixo forem atendidas:

1. Acórdão publicado com assinatura institucional (ICP-Brasil ou
   equivalente auditável — ex: Revista Eletrônica STJ + coleta
   autenticada).
2. Trânsito em julgado confirmado (ou caso de eficácia imediata
   tipo ADI com modulação, documentar exceção em `observacoes`).
3. PDF canônico depositado em
   `raw/B-jurisprudencia/<TRIBUNAL>/<CLASSE-NUM>/<id>.pdf` com
   sidecar schema §4.4 (não mais §4.4.1).
4. Etapa 0.5 + Etapa 1 + Etapa 2 rodadas conforme pipeline canônico
   (`_AGENTS/raw-protocol.md` §7).

A entry em `watchlist/index.yaml` ganha `status: promovido` e o
campo `acordao_em` apontando para o PDF definitivo. O histórico
de snapshots permanece preservado por auditoria — não se apaga
nada de `raw/`.

## Schema de `watchlist/index.yaml`

```yaml
schema_version: "0.1"
atualizado_em: "<YYYY-MM-DD>"
entries:
  - id: <slug estável — ex: STF-RE-1301250>
    tribunal: <STF|STJ|TJ-UF|...>
    numero_processo: <número oficial>
    incidente: <número do portal | null>
    ramo: <Criminal|Cível|Tributário|Constitucional|...>
    tema_rg: <número do Tema de Repercussão Geral | null>
    assunto: <descrição curta do motivo de rastreamento>
    primeiro_snapshot: "<YYYY-MM-DDTHH:MM:SSZ>"
    ultimo_snapshot: "<YYYY-MM-DDTHH:MM:SSZ>"
    estado_processual: <enum §4.4.1>
    status: <observando|suspenso|promovido>
    revisar_em: "<YYYY-MM-DD>"        # próxima janela sugerida
    acordao_em: <path | null>          # preenchido só em status: promovido
    observacoes: >
      <por que está sob observação, notas de relevância para o KB-PD,
      anomalias conhecidas do portal>
```

**Campos obrigatórios:** `id`, `tribunal`, `numero_processo`,
`primeiro_snapshot`, `estado_processual`, `status`.

**Campos opcionais:** `incidente`, `ramo`, `tema_rg`, `assunto`,
`ultimo_snapshot`, `revisar_em`, `acordao_em`, `observacoes`.

## Referências cruzadas

- Schema do depósito (sidecar do snapshot): `_AGENTS/raw-protocol.md`
  §3.2 (layout) + §4.4.1 (campos do sidecar) + §8.4 (exemplo canônico).
- Contrato operacional do pipeline: `_AGENTS/AGENTS.md`.
- Enum de `estado_processual` (8 valores): `_AGENTS/raw-protocol.md`
  §4.4.1.

## Política de fidelidade

`anomalias_observadas` no snapshot preserva o que o portal disse na
data da coleta, mesmo quando o valor é factualmente questionável (ex:
relator já aposentado constando como relator ativo). A cadeia de
custódia documenta a **coleta**, não a correção do dado de origem.
Mesma política que governa a preservação de bugs tipográficos do
Planalto (AGENTS.md §Fidelidade a artefatos).
