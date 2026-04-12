# Immort

A consolidated Skill repository based on `nuwa-skill`, with 3 external skills integrated under a runtime-first layout.

## Repository Purpose

- Keep the core `nuwa-skill` capability (`SKILL.md` + `references/` + `examples/`)
- Aggregate external skills under `external-skills/`
- Enforce one entry per skill: root-level `SKILL.md`
- Remove non-runtime files (CI, tests, build source, etc.)

## Structure

```text
Immort/
├── SKILL.md
├── references/
├── examples/
├── external-skills/
│   ├── RUNTIME_LAYOUT.md
│   ├── SOURCES.md
│   ├── diamond-sutra-skill/
│   ├── bazi-skill/
│   └── bazi-persona-skill/
└── README.md
```

## Integrated External Skills

1. `dull-bird/diamond-sutra-skill`
2. `jinchenma94/bazi-skill`
3. `cantian-ai/bazi-persona-skill`

See `external-skills/SOURCES.md` for source details.

## Usage

- For Nuwa core: use root `SKILL.md`.
- For integrated skills: open each subfolder and use its root `SKILL.md` plus runtime assets (`references/`, `prompts/`).

## Maintenance Rules

- One skill = one root `SKILL.md`
- Runtime assets stay in `references/` / `prompts/`
- No CI/test/build artifacts in this aggregate repo
- Any newly imported skill must update `external-skills/SOURCES.md`
