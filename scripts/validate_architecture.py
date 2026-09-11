#!/usr/bin/env python3
"""Validate the repository's architecture-as-code artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def fail(message: str) -> None:
    raise ValueError(message)


def walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "$ref":
                yield child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def validate_json() -> int:
    files = sorted(DOCS.rglob("*.json"))
    for path in files:
        with path.open(encoding="utf-8") as stream:
            json.load(stream)
    return len(files)


def validate_yaml() -> tuple[int, dict[str, Any]]:
    files = [DOCS / "openapi.yaml", ROOT / ".github/workflows/validate-architecture.yml"]
    documents: dict[Path, Any] = {}
    for path in files:
        with path.open(encoding="utf-8") as stream:
            documents[path] = yaml.safe_load(stream)

    spec = documents[DOCS / "openapi.yaml"]
    if spec.get("openapi") != "3.1.0":
        fail("docs/openapi.yaml must use OpenAPI 3.1.0")

    expected_operations = {
        "listProducts",
        "createProduct",
        "getProduct",
        "updateProduct",
        "listProductMovements",
        "createStockMovement",
    }
    found_operations = {
        operation.get("operationId")
        for path_item in spec.get("paths", {}).values()
        for method, operation in path_item.items()
        if method.lower() in {"get", "post", "put", "patch", "delete"}
    }
    missing = expected_operations - found_operations
    if missing:
        fail(f"OpenAPI operations missing: {sorted(missing)}")

    for ref in walk_values(spec):
        if isinstance(ref, str) and ref.startswith("./"):
            target = (DOCS / ref.split("#", 1)[0]).resolve()
            if not target.is_file() or ROOT not in target.parents:
                fail(f"Broken or unsafe OpenAPI reference: {ref}")

    return len(files), spec


def validate_markdown_links() -> int:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if ROOT not in resolved.parents and resolved != ROOT:
                fail(f"Link escapes repository in {path.relative_to(ROOT)}: {raw_target}")
            if not resolved.exists():
                fail(f"Broken link in {path.relative_to(ROOT)}: {raw_target}")
            checked += 1
    return checked


def mermaid_blocks(markdown: str) -> list[str]:
    return [block.strip() for block in re.findall(r"```mermaid\n(.*?)\n```", markdown, re.DOTALL)]


def validate_mermaid() -> int:
    source_paths = [
        DOCS / "diagrams/containers.mmd",
        DOCS / "diagrams/stock-exit-sequence.mmd",
    ]
    readme_blocks = mermaid_blocks((ROOT / "README.md").read_text(encoding="utf-8"))
    if len(readme_blocks) != len(source_paths):
        fail("README must contain the two required Mermaid diagrams")

    for source_path, embedded in zip(source_paths, readme_blocks, strict=True):
        source = source_path.read_text(encoding="utf-8").strip()
        if source != embedded:
            fail(f"README diagram is out of sync with {source_path.relative_to(ROOT)}")

    for path in sorted((DOCS / "diagrams").glob("*.mmd")):
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines or not (lines[0].startswith("flowchart ") or lines[0] == "sequenceDiagram"):
            fail(f"Unsupported Mermaid diagram header: {path.relative_to(ROOT)}")
    return len(list((DOCS / "diagrams").glob("*.mmd")))


def validate_adrs() -> int:
    paths = sorted((DOCS / "decisions").glob("ADR-*.md"))
    if len(paths) < 4:
        fail("At least four proposed ADRs are expected")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "**Status:** Proposto" not in text:
            fail(f"ADR without proposed status: {path.relative_to(ROOT)}")
    return len(paths)


def main() -> int:
    json_count = validate_json()
    yaml_count, _ = validate_yaml()
    link_count = validate_markdown_links()
    diagram_count = validate_mermaid()
    adr_count = validate_adrs()
    print(
        "Architecture validation passed: "
        f"{json_count} JSON, {yaml_count} YAML, {link_count} local links, "
        f"{diagram_count} Mermaid diagrams and {adr_count} ADRs."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"Architecture validation failed: {error}", file=sys.stderr)
        sys.exit(1)

