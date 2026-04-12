# Immort

道生一，一生二，二生三，三生万物，此immort之道也。

## 当前仓库定位

- 保留 `nuwa-skill` 主体能力（根目录 `SKILL.md` + `references/` + `examples/`）
- 聚合外部 skill 到 `external-skills/`
- 统一规范：每个 skill 仅保留一个根级入口 `SKILL.md`
- 清理非运行必需内容（CI、测试、构建源码等）

## 目录结构

```text
Immort/
├── SKILL.md                       # 主技能入口（Nuwa）
├── references/                    # 主技能参考资料
├── examples/                      # 主技能示例
├── external-skills/
│   ├── RUNTIME_LAYOUT.md          # 运行目录规范
│   ├── SOURCES.md                 # 外部来源记录
│   ├── diamond-sutra-skill/
│   │   ├── SKILL.md
│   │   └── ...
│   ├── bazi-skill/
│   │   ├── SKILL.md
│   │   └── references/
│   └── bazi-persona-skill/
│       ├── SKILL.md
│       └── prompts/
└── README.md
```

## 已并入的外部 Skill

1. `dull-bird/diamond-sutra-skill`
2. `jinchenma94/bazi-skill`
3. `cantian-ai/bazi-persona-skill`

> 详细来源与说明见：`external-skills/SOURCES.md`

## 运行方式（本仓库）

你可以把本仓库作为 Skill 集合使用，按需读取各目录下的 `SKILL.md`。

若仅使用主技能（Nuwa），直接以根目录 `SKILL.md` 作为入口。
若使用并入技能，进入对应子目录读取其 `SKILL.md` 与依赖资源（`references/` / `prompts/`）。

## 维护约定

- 一个 skill 一个入口：根级 `SKILL.md`
- 运行资源只放在 `references/`、`prompts/`（或等价运行目录）
- 不在聚合仓库保留 CI/测试/构建脚本
- 任何新增外部 skill 需先更新 `external-skills/SOURCES.md`
