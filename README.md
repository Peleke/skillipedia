<div align="center">

# Skillipedia

**Another encyclopedia nobody asked for.**

*A browsable index of agent skills, patterns, and learnings.*

[Live site](https://skillipedia.vercel.app) · [About](https://skillipedia.vercel.app/about) · [brunnr](https://github.com/Peleke/brunnr)

</div>

---

## What this is

Agents forget everything between sessions. Skillipedia writes down what they needed to know, in a format agents and people can both read.

It has 42 entries, each with a claim, a confidence score, and provenance:

| Type | Entries | What it is |
|------|---------|------------|
| **Skill** | 40 | A repeatable capability an agent can execute |
| **Pattern** | 1 | A structural solution that shows up across codebases |
| **Learning** | 1 | Something we got wrong, then got right, then wrote down |

You can search the entries, filter them by skill set, or browse by domain.

---

## How entries get here

Skills come from [brunnr](https://github.com/Peleke/brunnr), a security scanner and skills marketplace for Claude Code.

1. brunnr pushes a skill update and sends a `brunnr-skills-updated` dispatch.
2. `scripts/sync-from-brunnr.py` converts each `SKILL.md` into an entry in `src/content/entries/`.
3. GitHub Actions commits the changed entries and builds the site.

---

## Run it locally

Requires [Bun](https://bun.sh).

```bash
bun install
bun run dev
```

Build the site:

```bash
bun run build
```

Sync entries from a local brunnr checkout:

```bash
python scripts/sync-from-brunnr.py --brunnr-dir ../brunnr --output-dir src/content/entries
```

---

## Stack

[Astro](https://astro.build) · Tailwind CSS · Python (standard library) for the sync script · [Vercel](https://vercel.com)
