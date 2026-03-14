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


# Domain detection keywords in SKILL.md body
_DOMAIN_MARKERS = {
    "product-discovery": "_conventions.md",
    "education": "_educational-suite-conventions.md",
}


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


def detect_domain(slug: str, body: str, fm: dict[str, str]) -> str:
    """Detect the skill's domain from its body content and frontmatter.

    Priority:
    1. Check body for convention file references (_conventions.md etc.)
    2. Fall back to 'utility'
    """
    for domain, marker in _DOMAIN_MARKERS.items():
        if marker in body:
            return domain
    return "utility"


def extract_tags(fm: dict[str, str], body: str) -> list[str]:
    """Extract meaningful tags from frontmatter and body content."""
    tags = []

    # Extract context from metadata line if present
    context_match = re.search(r"context:\s*(fork|inline)", body[:500])
    if context_match:
        tags.append(f"context:{context_match.group(1)}")

    # Check for pipeline position indicator
    if "Pipeline Position" in body:
        tags.append("pipeline")

    # Check for web search requirement
    if "web search" in body.lower() or "context: fork" in body.lower():
        tags.append("web-search")

    return tags


def _escape_mdx_body(body: str) -> str:
    """Escape characters in markdown body that break MDX compilation.

    MDX treats bare < as JSX tag openers. Escape < that appear outside of
    fenced code blocks (``` ... ```) to prevent build failures.
    """
    parts = re.split(r"(```[\s\S]*?```)", body)
    escaped = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Inside a code fence — leave untouched
            escaped.append(part)
        else:
            # Outside code fence — escape bare < that aren't HTML tags
            # Replace < followed by a digit, space, =, or end-of-line
            part = re.sub(r"<(?=[\d\s=])", r"&lt;", part)
            escaped.append(part)
    return "".join(escaped)


def build_mdx(slug: str, description: str, body: str, content_hash: str,
              domain: str = "utility", tags: list[str] | None = None) -> str:
    """Build the MDX string for a single skill entry."""
    now = datetime.now(timezone.utc).isoformat()
    source_id = f"skill_md:{slug}:{content_hash}"
    tags = tags or []

    # Escape MDX-breaking characters in body
    body = _escape_mdx_body(body)

    # Escape double quotes in description for YAML
    desc_escaped = description.replace('"', '\\"')

    # Format tags
    if tags:
        tags_yaml = "\n".join(f'  - "{t}"' for t in tags)
        tags_block = f"tags:\n{tags_yaml}"
    else:
        tags_block = "tags: []"

    lines = [
        "---",
        f'id: "skill:{slug}"',
        "type: skill",
        f'claim: "{desc_escaped}"',
        "confidence: 0.75",
        f'domain: "{domain}"',
        "derivation: literal",
        tags_block,
        f'category: "{domain}"',
        "source_concepts:",
        f'  - "skill:{slug}"',
        "provenance:",
        f'  id: "skill:{slug}"',
        f'  domain: "{domain}"',
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
    skipped = []

    for skill_dir in sorted(skills_root.iterdir()):
        # Skip non-directories and _-prefixed convention files
        if not skill_dir.is_dir():
            if skill_dir.name.startswith("_"):
                skipped.append(skill_dir.name)
            continue
        if skill_dir.name.startswith("_"):
            skipped.append(skill_dir.name)
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue

        slug = skill_dir.name
        raw = skill_md.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:6]

        fm, body = parse_frontmatter(raw)
        description = fm.get("description", fm.get("name", slug))

        # Detect domain and tags
        domain = detect_domain(slug, raw, fm)
        tags = extract_tags(fm, raw)

        mdx = build_mdx(slug, description, body, content_hash, domain=domain, tags=tags)

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
    if skipped:
        print(f"skipped: {', '.join(skipped)}")
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
