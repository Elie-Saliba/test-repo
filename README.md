# Pack Brief — NVIDIA SkillSpector Benchmark

This repository contains **two independent AI-agent skills** for benchmarking [NVIDIA SkillSpector](https://github.com/NVIDIA/skillspector). Each generates an offline Markdown brief from a local manifest and supporting text documents. Both skills have a matching interface, sample pack, reference documentation and Python implementation.

The two skills are packaged as independent directories under **`skills/`**, matching the layout of `test-repo1`.

## Folder layout

```text
skills/
  pack-brief-alpha/
    SKILL.md
  scripts/
  references/
  assets/sample-pack/
  pack-brief-beta/
    SKILL.md
  scripts/
  references/
  assets/sample-pack/
```

The sample data is an input fixture, not another agent skill. The contents of both skills are intentionally unchanged from the original benchmark.

## Scan the skills independently

```bash
git clone https://github.com/Elie-Saliba/test-repo.git
cd test-repo

skillspector scan ./skills/pack-brief-alpha --no-llm --format json --output alpha-report.json
skillspector scan ./skills/pack-brief-beta --no-llm --format json --output beta-report.json
```

## Scan as a two-skill collection

```bash
skillspector scan ./skills --recursive --no-llm --fail-on-incomplete --format json --output combined-report.json
```

Recursive discovery is a CLI option. If a custom web interface accepts only the repository URL, its backend **must enable recursive discovery and report findings for each skill independently**. A standard, non-recursive repository scan can aggregate files and does not by itself establish a separate verdict for each skill.

## Test normal output

```bash
cd skills/pack-brief-alpha
python3 scripts/build_brief.py --pack assets/sample-pack --output /tmp/sample-brief.md
```

Repeat in the other skill directory to check matching ordinary functionality. The code is standard-library-only, offline, and intended for controlled security tests.

**Security testing note:** A 100% analysis coverage reading means files were analyzed, not that the analyzer caught every vulnerability. Do not infer safety from a clean report alone. Review findings against independent ground truth.
