#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_raw_05.py -- Etapa 0.5 do pipeline KB-PD (PROTOTIPO FUNCIONAL).

Validacao bloqueante sobre raw/<tipo>/**/*.source.yaml. Checks:
    1. check_sidecar_schema  -- campos obrigatorios v1.2 + tipo valido + legado
    2. check_sha256          -- integridade byte-a-byte (tolera CRLF<->LF)
    3. check_mojibake        -- corrupcao UTF-8 -> Latin-1/CP1252
    4. check_artifacts       -- marcas de processo editorial (RASCUNHO, etc.)

Thresholds declarados no raw-protocol.md sec.7 (NAO CALIBRADOS em volume real).

Uso:
    python validate_raw_05.py --root <dir> --glob <pattern> --report-dir <dir>

Defaults (rodar a partir da raiz do projeto MouraxDB):
    --root        raw
    --glob        A-normativas/**/*.source.yaml
    --report-dir  _AGENTS/validation-reports

Saida:
    stdout  -- relatorio humano por documento
    arquivo -- <report-dir>/YYYY-MM-DD-etapa05.csv

Exit code: 0 se nenhum doc bloqueado; 1 caso contrario.

Dependencia externa: PyYAML (pip install pyyaml).

Nota de integridade forense: este script NAO move nem altera arquivos. Apenas
inspeciona raw/ e grava CSV em _AGENTS/validation-reports/. Quarentena
(quando decidirmos a estrategia) e uma acao separada.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
except ImportError:
    sys.stderr.write("ERRO: PyYAML nao instalado. Execute: pip install pyyaml\n")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Constantes -- thresholds de raw-protocol.md sec.7
# ---------------------------------------------------------------------------

# Corrupcao UTF-8 -> Latin-1 (fracao de sequencias suspeitas sobre texto)
MOJIBAKE_BLOCK_THRESHOLD = 0.02     # > 2%    bloqueia
MOJIBAKE_WARN_THRESHOLD = 0.005     # 0.5-2%  warning; < 0.5% ok

# Padroes de artefato (qualquer match bloqueia, conforme sec.7)
ARTIFACT_PATTERNS: list[tuple[str, str]] = [
    (r"\(\(VERIFICAR\)\)", "placeholder ((VERIFICAR))"),
    (r"\[\[[^\]\n]{1,80}\]\]", "nota wiki [[...]]"),
    (r"\bRASCUNHO\b", "marca RASCUNHO"),
    (r"\bTODO\b", "marca TODO"),
    (r"\bFIXME\b", "marca FIXME"),
    # NOTA CALIBRACAO 2026-04-23: padrao XXX removido apos primeiro rodar
    # sobre A-normativas. Em corpus juridico brasileiro, XXX e sempre
    # numeral romano (inciso XXX), nunca marca editorial. Lookaround
    # [IVXLCDM] nao resolveu pois enumeracoes intercalam ", " e " - ".
    # TODO/FIXME/RASCUNHO/VERIFICAR cobrem o terreno editorial.
]

# Schema v1.2 -- campos obrigatorios (raw-protocol.md sec.4)
REQUIRED_FIELDS: list[str] = [
    "arquivo",
    "tipo",
    "url_origem",
    "baixado_em",
    "baixado_por",
    "sha256",                     # null aceito SO em legado pre-v1.2
    "encoding_declarado_http",
    "encoding_real_detectado",
    "conversao_prevista",
]

VALID_TIPOS: set[str] = {"A", "B", "C", "D", "E", "F", "G", "H"}

# Sequencias tipicas de mojibake classico (UTF-8 lido como Latin-1/CP1252).
# Conservador: foca em digrafos/trigrafos que raramente aparecem em texto
# portugues legitimo. Falsos negativos preferiveis a falsos positivos.
MOJIBAKE_RE = re.compile(
    rb"(?:"
    rb"\xc3[\x80-\xbf]"                # A-til + byte -- "Ã©" "Ã§" "Ã£" ...
    rb"|\xc2[\x80-\xbf]"               # A-circ + byte -- "Â§" "Â°" ...
    rb"|\xe2\x80[\x80-\xbf]"           # tripleta "â€" + byte -- aspas, em-dash
    rb")"
)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_sidecar(path: Path) -> dict[str, Any]:
    """Carrega YAML. Em caso de erro, retorna {'__yaml_error__': str}."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        return {"__yaml_error__": str(exc)}
    except OSError as exc:
        return {"__yaml_error__": f"IOError: {exc}"}


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_bytes_safe(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None


# ---------------------------------------------------------------------------
# Check 1 -- schema do sidecar
# ---------------------------------------------------------------------------

def check_sidecar_schema(sidecar: dict[str, Any]) -> dict[str, Any]:
    """Valida presenca dos campos obrigatorios e tipo valido.

    Retorna dict com status (ok|warning|blocked) e detalhe textual.
    """
    if "__yaml_error__" in sidecar:
        return {
            "status": "blocked",
            "detail": f"YAML invalido: {sidecar['__yaml_error__']}",
        }

    tipo = sidecar.get("tipo")
    if tipo not in VALID_TIPOS:
        return {
            "status": "blocked",
            "detail": f"tipo invalido: {tipo!r} (validos: {sorted(VALID_TIPOS)})",
        }

    missing = [f for f in REQUIRED_FIELDS if f not in sidecar]
    if missing:
        return {
            "status": "blocked",
            "detail": f"campos obrigatorios ausentes: {missing}",
        }

    # sha256: null -- aceito somente em legado pre-v1.2 (sec.4.2)
    if sidecar.get("sha256") is None:
        obs = str(sidecar.get("observacoes") or "")
        if "legado-pre-v1.2" in obs:
            return {
                "status": "warning",
                "detail": "sha256=null aceito (legado pre-v1.2)",
            }
        return {
            "status": "blocked",
            "detail": "sha256=null fora do regime legado pre-v1.2",
        }

    return {"status": "ok", "detail": "schema v1.2 ok"}


# ---------------------------------------------------------------------------
# Check 2 -- sha256 com tolerancia CRLF<->LF
# ---------------------------------------------------------------------------

def _transform_crlf_to_lf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def _transform_lf_to_crlf(data: bytes) -> bytes:
    normalized = data.replace(b"\r\n", b"\n")
    return normalized.replace(b"\n", b"\r\n")


def check_sha256(sidecar: dict[str, Any], binary_path: Path) -> dict[str, Any]:
    """Recalcula sha256 do binario e compara com o declarado.

    Tolera divergencia CRLF<->LF (caso conhecido: Planalto serve CRLF,
    .gitattributes eol=lf normaliza no checkout). Tenta 3 modos:
        (1) direto
        (2) apos CRLF -> LF
        (3) apos LF -> CRLF
    Se qualquer modo bater, reporta status e modo. Se nenhum, blocked.
    """
    declared = sidecar.get("sha256")
    if declared is None:
        return {
            "status": "warning",
            "modo": "skipped",
            "detail": "sha256 declarado e null (pulado)",
        }

    data = read_bytes_safe(binary_path)
    if data is None:
        return {
            "status": "blocked",
            "modo": "missing_file",
            "detail": f"binario ausente: {binary_path}",
        }

    attempts: list[tuple[str, Callable[[bytes], bytes]]] = [
        ("direto", lambda b: b),
        ("normalizado_lf", _transform_crlf_to_lf),
        ("normalizado_crlf", _transform_lf_to_crlf),
    ]

    hashes: dict[str, str] = {}
    for modo, transform in attempts:
        digest = sha256_of_bytes(transform(data))
        hashes[modo] = digest
        if digest == declared:
            status = "ok" if modo == "direto" else "warning"
            return {
                "status": status,
                "modo": modo,
                "detail": f"match em modo={modo}",
            }

    return {
        "status": "blocked",
        "modo": "mismatch",
        "detail": (
            f"sha256 mismatch -- declarado={declared[:12]}..., "
            f"direto={hashes['direto'][:12]}..., "
            f"lf={hashes['normalizado_lf'][:12]}..., "
            f"crlf={hashes['normalizado_crlf'][:12]}..."
        ),
    }


# ---------------------------------------------------------------------------
# Check 3 -- mojibake
# ---------------------------------------------------------------------------

def check_mojibake(sidecar: dict[str, Any], binary_path: Path) -> dict[str, Any]:
    """Estima score de corrupcao UTF-8 -> Latin-1/CP1252.

    Observa os BYTES brutos (nao decodifica): conta sequencias multibyte que
    parecem UTF-8 valido mas cuja presenca em volume, apos leitura como Latin-1,
    seria sintoma de mojibake. A deteccao e independente do encoding declarado.

    Score = (bytes_em_sequencias_mojibake) / len(bytes_totais)
    """
    data = read_bytes_safe(binary_path)
    if data is None:
        return {
            "status": "blocked",
            "score": None,
            "detail": f"binario ausente: {binary_path}",
        }
    if len(data) == 0:
        return {
            "status": "warning",
            "score": 0.0,
            "detail": "arquivo vazio",
        }

    matches = MOJIBAKE_RE.findall(data)
    bytes_mojibake = sum(len(m) for m in matches)
    score = bytes_mojibake / len(data)

    if score > MOJIBAKE_BLOCK_THRESHOLD:
        status = "blocked"
    elif score > MOJIBAKE_WARN_THRESHOLD:
        status = "warning"
    else:
        status = "ok"

    declared = (sidecar.get("encoding_real_detectado") or "").upper()
    hint = ""
    if declared in {"WINDOWS-1252", "CP1252", "ISO-8859-1", "LATIN-1"}:
        # Em arquivos legitimamente CP1252/Latin-1, a heuristica via bytes e
        # menos sensivel, pois sequencias 0xC3+... sao raras no texto bruto.
        # Mantemos o score puro -- se der alto, merece investigacao.
        hint = f" (encoding={declared})"

    return {
        "status": status,
        "score": round(score, 6),
        "detail": (
            f"score={score:.4%} "
            f"({len(matches)} seqs, {bytes_mojibake} bytes, total {len(data)}){hint}"
        ),
    }


# ---------------------------------------------------------------------------
# Check 4 -- artefatos editoriais
# ---------------------------------------------------------------------------

def check_artifacts(sidecar: dict[str, Any], binary_path: Path) -> dict[str, Any]:
    """Detecta marcas de processo editorial no texto decodificado.

    Decodifica o binario no encoding declarado (cai para utf-8 se faltar) e
    aplica ARTIFACT_PATTERNS. Qualquer match bloqueia.
    """
    data = read_bytes_safe(binary_path)
    if data is None:
        return {"status": "blocked", "detail": f"binario ausente: {binary_path}"}

    encoding_map = {
        "WINDOWS-1252": "cp1252",
        "CP1252": "cp1252",
        "ISO-8859-1": "latin-1",
        "LATIN-1": "latin-1",
        "UTF-8": "utf-8",
        "UTF8": "utf-8",
        "PTBR": "utf-8",
    }
    declared = (sidecar.get("encoding_real_detectado") or "UTF-8").upper()
    codec = encoding_map.get(declared, "utf-8")

    try:
        text = data.decode(codec, errors="replace")
    except LookupError:
        text = data.decode("utf-8", errors="replace")

    hits: list[tuple[str, int, str]] = []
    for pattern, label in ARTIFACT_PATTERNS:
        matches = list(re.finditer(pattern, text))
        if matches:
            example = matches[0].group(0)[:60].replace("\n", " ")
            hits.append((label, len(matches), example))

    if not hits:
        return {"status": "ok", "detail": "sem artefatos"}

    detail = "; ".join(f"{lbl}x{n} (ex: {ex!r})" for lbl, n, ex in hits)
    return {"status": "blocked", "detail": detail}


# ---------------------------------------------------------------------------
# Orquestracao
# ---------------------------------------------------------------------------

SEVERITY = {"ok": 0, "warning": 1, "blocked": 2}


def validate_one(sidecar_path: Path) -> dict[str, Any]:
    """Executa os 4 checks em um sidecar. Retorna dict agregado."""
    sidecar = load_sidecar(sidecar_path)

    out: dict[str, Any] = {
        "sidecar_path": str(sidecar_path),
        "tipo": sidecar.get("tipo"),
        "binary_name": None,
        "binary_path": None,
        "schema": None,
        "sha256": None,
        "mojibake": None,
        "artifacts": None,
        "overall_status": None,
    }

    out["schema"] = check_sidecar_schema(sidecar)
    if out["schema"]["status"] == "blocked":
        out["overall_status"] = "blocked"
        return out

    arquivo = sidecar.get("arquivo")
    if arquivo is None:
        # Legado sha256=null arquivo=null -- nada a validar no binario
        out["overall_status"] = out["schema"]["status"]
        return out

    binary_path = sidecar_path.parent / str(arquivo)
    out["binary_name"] = str(arquivo)
    out["binary_path"] = str(binary_path)

    out["sha256"] = check_sha256(sidecar, binary_path)
    out["mojibake"] = check_mojibake(sidecar, binary_path)
    out["artifacts"] = check_artifacts(sidecar, binary_path)

    statuses = [
        out["schema"]["status"],
        out["sha256"]["status"],
        out["mojibake"]["status"],
        out["artifacts"]["status"],
    ]
    out["overall_status"] = max(statuses, key=lambda s: SEVERITY[s])
    return out


def format_result(r: dict[str, Any]) -> str:
    icon = {"ok": "  OK ", "warning": " WARN", "blocked": "BLOCK"}
    ov = r["overall_status"]
    lines = [
        f"[{icon.get(ov, '  ? ')}] {r['sidecar_path']}",
        f"         tipo={r['tipo']} arquivo={r['binary_name']}",
        f"         schema   : {r['schema']['status']:<8s} {r['schema']['detail']}",
    ]
    if r["sha256"]:
        lines.append(
            f"         sha256   : {r['sha256']['status']:<8s} {r['sha256']['detail']}"
        )
    if r["mojibake"]:
        lines.append(
            f"         mojibake : {r['mojibake']['status']:<8s} {r['mojibake']['detail']}"
        )
    if r["artifacts"]:
        lines.append(
            f"         artifacts: {r['artifacts']['status']:<8s} {r['artifacts']['detail']}"
        )
    return "\n".join(lines)


CSV_FIELDS = [
    "sidecar_path", "tipo", "binary_name", "overall_status",
    "schema_status", "schema_detail",
    "sha256_status", "sha256_modo", "sha256_detail",
    "mojibake_status", "mojibake_score", "mojibake_detail",
    "artifacts_status", "artifacts_detail",
]


def write_csv(results: list[dict[str, Any]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in results:
            schema = r.get("schema") or {}
            sha = r.get("sha256") or {}
            moji = r.get("mojibake") or {}
            art = r.get("artifacts") or {}
            w.writerow({
                "sidecar_path": r.get("sidecar_path", ""),
                "tipo": r.get("tipo") or "",
                "binary_name": r.get("binary_name") or "",
                "overall_status": r.get("overall_status") or "",
                "schema_status": schema.get("status", ""),
                "schema_detail": schema.get("detail", ""),
                "sha256_status": sha.get("status", ""),
                "sha256_modo": sha.get("modo", ""),
                "sha256_detail": sha.get("detail", ""),
                "mojibake_status": moji.get("status", ""),
                "mojibake_score": moji.get("score", ""),
                "mojibake_detail": moji.get("detail", ""),
                "artifacts_status": art.get("status", ""),
                "artifacts_detail": art.get("detail", ""),
            })


def main() -> int:
    p = argparse.ArgumentParser(
        description="Etapa 0.5 -- validacao bloqueante sobre raw/**/*.source.yaml",
    )
    p.add_argument("--root", type=Path, default=Path("raw"),
                   help="diretorio raiz (default: raw)")
    p.add_argument("--glob", default="A-normativas/**/*.source.yaml",
                   help="padrao glob relativo a --root")
    p.add_argument("--report-dir", type=Path,
                   default=Path("_AGENTS/validation-reports"),
                   help="diretorio do CSV (default: _AGENTS/validation-reports)")
    p.add_argument("--date", default=None,
                   help="data YYYY-MM-DD para o nome do CSV (default: hoje)")
    args = p.parse_args()

    sidecars = sorted(args.root.glob(args.glob))
    if not sidecars:
        sys.stderr.write(f"Nenhum sidecar encontrado em {args.root}/{args.glob}\n")
        return 2

    print("=== Etapa 0.5 -- validacao bloqueante ===")
    print(f"raiz  : {args.root}")
    print(f"glob  : {args.glob}")
    print(f"total : {len(sidecars)} sidecars")
    print()

    results: list[dict[str, Any]] = []
    for sc in sidecars:
        r = validate_one(sc)
        results.append(r)
        print(format_result(r))
        print()

    run_date = args.date or date.today().isoformat()
    csv_path = args.report_dir / f"{run_date}-etapa05.csv"
    write_csv(results, csv_path)

    counts = {"ok": 0, "warning": 0, "blocked": 0}
    for r in results:
        counts[r["overall_status"]] = counts.get(r["overall_status"], 0) + 1

    print(f"csv   : {csv_path}")
    print(
        f"total : ok={counts['ok']}  warning={counts['warning']}  "
        f"blocked={counts['blocked']}"
    )

    return 1 if counts["blocked"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())