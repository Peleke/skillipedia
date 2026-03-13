#!/usr/bin/env python3
"""Sync brunnr skill definitions into skillipedia MDX entries.

Walks brunnr's skills/*/SKILL.md files, parses frontmatter, and generates
MDX entries matching the skillipedia content schema.  Zero external deps
(stdlib only).

Usage:
    python scripts/sync-from-brunnr.py --brunnr-dir ../brunnr --output-dir src/content/entries
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body) from a markdown file with YAML front matter."""
    fm: dict[str, str] = {}
    body = text

    match = re.match(r"^---\s*\n(.*?\n)---\s*\n", text, re.DOTALL)
    if not match:
        return fm, body

    raw = match.group(1)
    body = text[match.end() :]

    for line in raw.splitlines():
        m = re.match(r"^([a-z_]+)\s*:\s*(.+)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")

    return fm, body


def build_mdx(slug: str, description: str, body: str, content_hash: str) -> str:
    """Build the MDX string for a single skill entry."""
    now = datetime.now(timezone.utc).isoformat()
    source_id = f"skill_md:{slug}:{content_hash}"

    # Escape double quotes in description for YAML
    desc_escaped = description.replace('"', '\\"')

    lines = [
        "---",
        f'id: "skill:{slug}"',
        "type: skill",
        f'claim: "{desc_escaped}"',
        "confidence: 0.75",
        f'domain: "skill:{slug}"',
        "derivation: literal",
        "tags: []",
        f'category: "skill:{slug}"',
        "source_concepts:",
        f'  - "skill:{slug}"',
        "provenance:",
        f'  id: "skill:{slug}"',
        f'  domain: "skill:{slug}"',
        "  derivation: literal",
        "  source_concepts:",
        f'    - "skill:{slug}"',
        "  confidence: 0.75",
        f'  source_id: "{source_id}"',
        "metadata:",
        f'  source_id: "{source_id}"',
        "  skill_format: canonical",
        f'generated_at: "{now}"',
        "---",
        "",
        body.strip(),
        "",
    ]
    return "\n".join(lines)


def sync(brunnr_dir: Path, output_dir: Path) -> None:
    skills_root = brunnr_dir / "skills"
    if not skills_root.is_dir():
        print(f"error: skills directory not found at {skills_root}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    created = []
    updated = []
    unchanged = []

    for skill_dir in sorted(skills_root.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        slug = skill_dir.name
        raw = skill_md.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:6]

        fm, body = parse_frontmatter(raw)
        description = fm.get("description", fm.get("name", slug))

        mdx = build_mdx(slug, description, body, content_hash)

        out_path = output_dir / f"{slug}.mdx"
        if out_path.exists():
            existing = out_path.read_text(encoding="utf-8")

            # Compare body content only (skip generated_at which changes each run)
            def strip_generated_at(s: str) -> str:
                return re.sub(r"^generated_at:.*$", "", s, flags=re.MULTILINE)

            if strip_generated_at(existing) == strip_generated_at(mdx):
                unchanged.append(slug)
                continue
            else:
                updated.append(slug)
        else:
            created.append(slug)

        out_path.write_text(mdx, encoding="utf-8")

    if created:
        print(f"created: {', '.join(created)}")
    if updated:
        print(f"updated: {', '.join(updated)}")
    if unchanged:
        print(f"unchanged: {', '.join(unchanged)}")
    if not created and not updated and not unchanged:
        print("no skills found")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync brunnr skills to skillipedia entries")
    parser.add_argument(
        "--brunnr-dir",
        type=Path,
        default=Path("../brunnr"),
        help="Path to brunnr checkout (default: ../brunnr)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("src/content/entries"),
        help="Output directory for MDX entries (default: src/content/entries)",
    )
    args = parser.parse_args()
    sync(args.brunnr_dir, args.output_dir)


if __name__ == "__main__":
    main()
