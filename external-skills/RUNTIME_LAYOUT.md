# Runtime Layout (Cleaned)

This repo keeps only runtime-relevant files for imported skills.

## Kept
- `*/SKILL.md` (skill entry)
- `*/references/**` (when referenced by SKILL)
- `*/prompts/**` (runtime prompt assets)
- `LICENSE` and core `README*` for attribution/context

## Removed as non-runtime
- CI/CD (`.github/workflows/**`)
- Build/test/dev files (`src/**`, `tests/**`, `scripts/**`, `package*.json`, `tsconfig.json`)
- local tooling ignores (`.gitignore`, `.npmignore`)


## Entry Convention

- One skill = one root entry file: `SKILL.md`
- No nested duplicate entry points (e.g., `openclaw/SKILL.md`)
- Runtime assets stay under `references/` and `prompts/`
