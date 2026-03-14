"""Tests for sync-from-brunnr.py skill ingestion pipeline."""

from __future__ import annotations

import importlib.util
import sys
import pytest
from pathlib import Path

# Import the sync module by loading the script directly
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location(
    "sync_from_brunnr", SCRIPTS_DIR / "sync-from-brunnr.py"
)
sync_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_mod)

parse_frontmatter = sync_mod.parse_frontmatter
detect_domain = sync_mod.detect_domain
extract_tags = sync_mod.extract_tags
build_mdx = sync_mod.build_mdx
_escape_mdx_body = sync_mod._escape_mdx_body
sync = sync_mod.sync


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_basic_frontmatter(self):
        text = "---\nname: test\ndescription: A test skill\n---\n# Body"
        fm, body = parse_frontmatter(text)
        assert fm["name"] == "test"
        assert fm["description"] == "A test skill"
        assert body.strip() == "# Body"

    def test_quoted_description(self):
        text = '---\nname: test\ndescription: "A quoted description"\n---\n# Body'
        fm, body = parse_frontmatter(text)
        assert fm["description"] == "A quoted description"

    def test_single_quoted_description(self):
        text = "---\nname: test\ndescription: 'Single quoted'\n---\n# Body"
        fm, body = parse_frontmatter(text)
        assert fm["description"] == "Single quoted"

    def test_no_frontmatter(self):
        text = "# Just a heading\nSome content"
        fm, body = parse_frontmatter(text)
        assert fm == {}
        assert body == text

    def test_empty_frontmatter(self):
        text = "---\n---\n# Body"
        fm, body = parse_frontmatter(text)
        assert fm == {}

    def test_nested_metadata_ignored(self):
        """Nested YAML keys (metadata:) are not parsed by the simple regex."""
        text = "---\nname: test\nmetadata:\n  context: fork\n---\n# Body"
        fm, body = parse_frontmatter(text)
        assert "name" in fm
        assert "metadata" not in fm

    def test_preserves_body_content(self):
        text = "---\nname: test\n---\n\n# Body\n\nParagraph\n"
        fm, body = parse_frontmatter(text)
        assert "# Body" in body
        assert "Paragraph" in body

    def test_description_with_colon(self):
        text = '---\nname: test\ndescription: "Has: a colon"\n---\n# Body'
        fm, body = parse_frontmatter(text)
        assert fm["description"] == "Has: a colon"


# ---------------------------------------------------------------------------
# detect_domain
# ---------------------------------------------------------------------------


class TestDetectDomain:
    def test_product_discovery_from_conventions(self):
        body = "## Step 0\nRead ${SKILLS_DIR}/_conventions.md\n# Rest of skill"
        assert detect_domain("signal-scan", body, {}) == "product-discovery"

    def test_education_from_conventions(self):
        body = "## Step 0\nRead _educational-suite-conventions.md\n# Rest"
        assert detect_domain("lesson-gen", body, {}) == "education"

    def test_utility_fallback(self):
        body = "# A standalone skill\nNo convention references."
        assert detect_domain("standalone", body, {}) == "utility"

    def test_product_discovery_wins_over_education(self):
        """If both markers present, product-discovery wins (dict iteration order)."""
        body = "_conventions.md\n_educational-suite-conventions.md"
        result = detect_domain("both", body, {})
        assert result == "product-discovery"

    def test_marker_in_frontmatter_area_also_detected(self):
        """detect_domain receives the full raw text, including frontmatter."""
        raw = "---\nname: test\n---\nRead _conventions.md"
        assert detect_domain("test", raw, {}) == "product-discovery"


# ---------------------------------------------------------------------------
# extract_tags
# ---------------------------------------------------------------------------


class TestExtractTags:
    def test_context_fork(self):
        body = "metadata:\n  context: fork\n# Rest"
        tags = extract_tags({}, body)
        assert "context:fork" in tags

    def test_context_inline(self):
        body = "metadata:\n  context: inline\n# Rest"
        tags = extract_tags({}, body)
        assert "context:inline" in tags

    def test_pipeline_tag(self):
        body = "## Pipeline Position\nsignal-scan -> decision-log"
        tags = extract_tags({}, body)
        assert "pipeline" in tags

    def test_web_search_tag_explicit(self):
        body = "### What to research (via web search):\n- Search for competitors"
        tags = extract_tags({}, body)
        assert "web-search" in tags

    def test_web_search_tag_from_context_fork(self):
        body = "metadata:\n  context: fork\nSome content"
        tags = extract_tags({}, body)
        assert "web-search" in tags

    def test_no_tags(self):
        body = "# Simple skill\nJust does things."
        tags = extract_tags({}, body)
        assert tags == []

    def test_multiple_tags(self):
        body = "metadata:\n  context: fork\n## Pipeline Position\nsome -> pipeline"
        tags = extract_tags({}, body)
        assert "context:fork" in tags
        assert "pipeline" in tags
        assert "web-search" in tags


# ---------------------------------------------------------------------------
# build_mdx
# ---------------------------------------------------------------------------


class TestEscapeMdxBody:
    def test_escapes_angle_bracket_before_digit(self):
        assert _escape_mdx_body("(<300 words)") == "(&lt;300 words)"

    def test_preserves_html_tags(self):
        assert _escape_mdx_body("<div>hello</div>") == "<div>hello</div>"

    def test_preserves_code_blocks(self):
        body = "before\n```\n<300\n```\nafter <3"
        result = _escape_mdx_body(body)
        assert "<300" in result  # inside code block, untouched
        assert "&lt;3" in result  # outside code block, escaped

    def test_escapes_angle_bracket_before_space(self):
        assert _escape_mdx_body("a < b") == "a &lt; b"

    def test_no_escape_needed(self):
        assert _escape_mdx_body("just normal text") == "just normal text"


class TestBuildMdx:
    def test_basic_output(self):
        mdx = build_mdx("test", "A test skill", "# Body", "abc123")
        assert 'id: "skill:test"' in mdx
        assert "type: skill" in mdx
        assert 'claim: "A test skill"' in mdx
        assert 'domain: "utility"' in mdx
        assert "# Body" in mdx

    def test_custom_domain(self):
        mdx = build_mdx("test", "Desc", "# Body", "abc", domain="product-discovery")
        assert 'domain: "product-discovery"' in mdx
        assert 'category: "product-discovery"' in mdx

    def test_tags_rendered(self):
        mdx = build_mdx("test", "Desc", "# Body", "abc", tags=["pipeline", "web-search"])
        assert '"pipeline"' in mdx
        assert '"web-search"' in mdx

    def test_empty_tags(self):
        mdx = build_mdx("test", "Desc", "# Body", "abc", tags=[])
        assert "tags: []" in mdx

    def test_description_with_quotes(self):
        mdx = build_mdx("test", 'Has "quotes" inside', "# Body", "abc")
        assert 'Has \\"quotes\\" inside' in mdx

    def test_frontmatter_boundaries(self):
        mdx = build_mdx("test", "Desc", "# Body", "abc")
        assert mdx.startswith("---\n")
        assert "\n---\n" in mdx

    def test_source_id_includes_hash(self):
        mdx = build_mdx("test", "Desc", "# Body", "abc123")
        assert "skill_md:test:abc123" in mdx

    def test_body_stripped(self):
        mdx = build_mdx("test", "Desc", "\n\n# Body\n\n", "abc")
        assert mdx.endswith("# Body\n")


# ---------------------------------------------------------------------------
# sync (integration)
# ---------------------------------------------------------------------------


class TestSync:
    @pytest.fixture
    def brunnr_tree(self, tmp_path):
        """Create a mock brunnr skills directory."""
        brunnr = tmp_path / "brunnr"
        skills = brunnr / "skills"
        skills.mkdir(parents=True)

        # Product discovery skill
        s1 = skills / "signal-scan"
        s1.mkdir()
        (s1 / "SKILL.md").write_text(
            "---\nname: signal-scan\ndescription: Scan for market signals\n---\n"
            "## Step 0\nRead ${SKILLS_DIR}/_conventions.md\n"
            "## Pipeline Position\nsignal-scan -> decision-log\n# Signal Scan"
        )

        # Skill with references (references should be ignored by sync)
        s2 = skills / "pitch"
        s2.mkdir()
        (s2 / "SKILL.md").write_text(
            "---\nname: pitch\ndescription: Go-to-market launch engine\n---\n"
            "## Step 0\nRead ${SKILLS_DIR}/_conventions.md\n# Pitch"
        )
        refs = s2 / "references"
        refs.mkdir()
        (refs / "template.md").write_text("# Template")

        # Education skill
        s3 = skills / "lesson-generator"
        s3.mkdir()
        (s3 / "SKILL.md").write_text(
            "---\nname: lesson-generator\ndescription: Generate lessons\n---\n"
            "Read _educational-suite-conventions.md\n# Lesson Gen"
        )

        # Utility skill (no convention reference)
        s4 = skills / "sketches"
        s4.mkdir()
        (s4 / "SKILL.md").write_text(
            "---\nname: sketches\ndescription: Draw SVG sketches\n---\n# Sketches"
        )

        # Convention files (should be skipped)
        (skills / "_conventions.md").write_text("# Conventions")
        (skills / "_educational-suite-conventions.md").write_text("# Educational")

        # Empty directory (no SKILL.md, should be skipped)
        (skills / "empty-dir").mkdir()

        return brunnr

    def test_creates_mdx_entries(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        assert (output / "signal-scan.mdx").exists()
        assert (output / "pitch.mdx").exists()
        assert (output / "lesson-generator.mdx").exists()
        assert (output / "sketches.mdx").exists()

    def test_skips_convention_files(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        assert not (output / "_conventions.mdx").exists()
        assert not (output / "_educational-suite-conventions.mdx").exists()

    def test_skips_empty_directories(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        assert not (output / "empty-dir.mdx").exists()

    def test_product_discovery_domain(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        content = (output / "signal-scan.mdx").read_text()
        assert 'domain: "product-discovery"' in content

    def test_education_domain(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        content = (output / "lesson-generator.mdx").read_text()
        assert 'domain: "education"' in content

    def test_utility_domain(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        content = (output / "sketches.mdx").read_text()
        assert 'domain: "utility"' in content

    def test_tags_extracted(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        content = (output / "signal-scan.mdx").read_text()
        assert '"pipeline"' in content

    def test_idempotent_sync(self, brunnr_tree, tmp_path, capsys):
        output = tmp_path / "output"

        # First sync
        sync(brunnr_tree, output)
        first = capsys.readouterr()
        assert "created" in first.out

        # Second sync (no changes)
        sync(brunnr_tree, output)
        second = capsys.readouterr()
        assert "unchanged" in second.out
        assert "created" not in second.out

    def test_updated_skill(self, brunnr_tree, tmp_path, capsys):
        output = tmp_path / "output"

        # First sync
        sync(brunnr_tree, output)
        capsys.readouterr()

        # Modify skill
        skill_md = brunnr_tree / "skills" / "signal-scan" / "SKILL.md"
        skill_md.write_text(
            "---\nname: signal-scan\ndescription: UPDATED description\n---\n# Updated"
        )

        # Second sync
        sync(brunnr_tree, output)
        second = capsys.readouterr()
        assert "updated" in second.out
        assert "signal-scan" in second.out

    def test_total_entry_count(self, brunnr_tree, tmp_path):
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        mdx_files = list(output.glob("*.mdx"))
        assert len(mdx_files) == 4  # signal-scan, pitch, lesson-generator, sketches

    def test_references_not_synced_as_entries(self, brunnr_tree, tmp_path):
        """References dir content should NOT become separate entries."""
        output = tmp_path / "output"
        sync(brunnr_tree, output)

        assert not (output / "template.mdx").exists()
        assert not (output / "references.mdx").exists()

    def test_skipped_reported(self, brunnr_tree, tmp_path, capsys):
        output = tmp_path / "output"
        sync(brunnr_tree, output)
        out = capsys.readouterr().out
        assert "skipped" in out
        assert "_conventions.md" in out
