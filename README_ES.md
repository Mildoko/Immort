# Immort

Repositorio agregado de Skills, organizado alrededor de `nuwa-skill`, con 3 skills externos incorporados y una estructura unificada orientada a ejecución.

## Objetivo del repositorio

- Mantener el núcleo de `nuwa-skill` (`SKILL.md` + `references/` + `examples/`)
- Agregar skills externos en `external-skills/`
- Unificar una sola entrada por skill: `SKILL.md` en raíz
- Eliminar archivos no esenciales para ejecución (CI, tests, build, etc.)

## Estructura

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

## Skills externos integrados

1. `dull-bird/diamond-sutra-skill`
2. `jinchenma94/bazi-skill`
3. `cantian-ai/bazi-persona-skill`

Ver `external-skills/SOURCES.md` para detalles de origen.

## Uso

- Núcleo Nuwa: usar `SKILL.md` en la raíz.
- Skills integrados: usar `SKILL.md` de cada subcarpeta y sus recursos de runtime (`references/`, `prompts/`).

## Reglas de mantenimiento

- Un skill = un `SKILL.md` en raíz
- Recursos de runtime en `references/` / `prompts/`
- Sin artefactos de CI/test/build en este repositorio agregado
- Al agregar nuevos skills externos, actualizar `external-skills/SOURCES.md`
