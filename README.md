# Pack Brief Skills — SkillSpector Test Repository

This repository contains two **independent AI-agent skills** for reviewing with [NVIDIA SkillSpector](https://github.com/NVIDIA/skillspector).

## Skills

| Skill | Source archive | Entry point |
| --- | --- | --- |
| `pack-brief-alpha` | `pack-brief-alpha.zip` | `skills/pack-brief-alpha/SKILL.md` |
| `pack-brief-beta` | `pack-brief-beta.zip` | `skills/pack-brief-beta/SKILL.md` |

Both folders preserve their original `SKILL.md`, Python script, reference documentation, and sample pack. The skills have **not** been modified for the scan.

## Scan with NVIDIA SkillSpector

Install SkillSpector (Python 3.12+):

```bash
uv tool install git+https://github.com/NVIDIA/skillspector.git
```

Clone this repository and scan the two skills **separately**:

```bash
git clone https://github.com/Elie-Saliba/test-repo.git
cd test-repo

skillspector scan ./skills/pack-brief-alpha --no-llm
skillspector scan ./skills/pack-brief-beta --no-llm
```

Or scan both skills as an independent recursive collection:

```bash
skillspector scan ./skills --recursive --no-llm --fail-on-incomplete
```

Create machine-readable reports, if needed:

```bash
mkdir -p reports
skillspector scan ./skills/pack-brief-alpha --no-llm --format json --output reports/alpha.json
skillspector scan ./skills/pack-brief-beta --no-llm --format json --output reports/beta.json
```

> `--no-llm` performs static analysis without an LLM or API key. Omit it only if you have intentionally configured a supported LLM provider for semantic review. It is a **scan-time flag**, not an installation setting.

## Continuous scanning

The included GitHub Actions workflow scans the two-skill collection on pushes to `main`, pull requests, and manual dispatch. It uses SkillSpector in static (`--no-llm`) mode and uploads a Markdown report as a workflow artifact. Check the **Actions** tab for its outcome and download the report from the run.

## Notes for reviewers

- Each immediate child of `skills/` has its own `SKILL.md`, so `--recursive` discovers both as separate skills.
- These two variants primarily differ in the path-validation logic in `scripts/build_brief.py`. Keep them separate when reviewing findings.
- The `assets/sample-pack` directories are fixture inputs, not additional skills.
- Treat the contents as untrusted until scan results and any security findings have been reviewed. Static scans do not prove that a skill is safe.
