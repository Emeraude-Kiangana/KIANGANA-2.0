#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md", "GOVERNANCE.md", "SECURITY.md", ".gitignore",
    ".github/CODEOWNERS", ".github/pull_request_template.md",
    ".github/workflows/gate-zero.yml",
    "governance/permission-matrix.yaml", "governance/plugin-registry.yaml",
    "governance/decision-log.md", "templates/mission-contract.yaml",
    "templates/evidence-record.yaml", "templates/closure-report.md",
    "schemas/mission-contract.schema.json", "docs/architecture.md",
    "missions/KIA-2026-001.yaml", "evidence/EVD-2026-001.yaml",
    "reports/KIA-2026-001-status.md",
    "governance/project-registry.yaml", "templates/project-status.yaml",
    "dashboard/COMMAND-CENTER.md", "missions/KIA-2026-002.yaml",
    "evidence/EVD-2026-002.yaml",
    "reports/KIA-2026-002-closure.md",
]

def validate():
    errors = [f"missing: {item}" for item in REQUIRED if not (ROOT / item).is_file()]
    schema_path = ROOT / "schemas/mission-contract.schema.json"
    if schema_path.is_file():
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            if "required" not in schema:
                errors.append("schema has no required fields")
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON schema: {exc}")
    matrix = (ROOT / "governance/permission-matrix.yaml").read_text(encoding="utf-8")
    for level in ("P0", "P1", "P2", "P3", "P4", "P5"):
        if f"  {level}:" not in matrix:
            errors.append(f"missing permission level: {level}")
    registry_path = ROOT / "governance/project-registry.yaml"
    if registry_path.is_file():
        registry = registry_path.read_text(encoding="utf-8")
        for project in ("eCDF", "AGRICHAIN DAO", "Open Technologies Portfolio"):
            if project not in registry:
                errors.append(f"missing project in registry: {project}")
    forbidden = ["PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY", "ghp_", "sk-"]
    for path in ROOT.rglob("*"):
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.is_file() and ".git" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                if token in text:
                    errors.append(f"possible secret marker in {path.relative_to(ROOT)}")
    return errors

if __name__ == "__main__":
    failures = validate()
    if failures:
        print("GATE ZERO: FAILED")
        print("\n".join(f"- {item}" for item in failures))
        sys.exit(1)
    print("GATE ZERO: PASSED")
    print(f"Validated {len(REQUIRED)} required governance artifacts and levels P0-P5.")
