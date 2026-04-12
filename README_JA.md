# Immort

`nuwa-skill` を中核に整理し、3つの外部 skill を取り込んだ、ランタイム優先構成の集約 Skill リポジトリです。

## リポジトリ方針

- `nuwa-skill` の中核機能を維持（`SKILL.md` + `references/` + `examples/`）
- 外部 skill は `external-skills/` に集約
- 1 skill 1 エントリ（ルート `SKILL.md`）を統一
- 実行に不要な CI/テスト/ビルド資産は除去

## 構成

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

## 統合済み外部 Skill

1. `dull-bird/diamond-sutra-skill`
2. `jinchenma94/bazi-skill`
3. `cantian-ai/bazi-persona-skill`

詳細は `external-skills/SOURCES.md` を参照してください。

## 使い方

- Nuwa 本体: ルートの `SKILL.md` を使用
- 統合 skill: 各サブフォルダの `SKILL.md` と実行資産（`references/` / `prompts/`）を使用

## 運用ルール

- 1 skill = 1 ルート `SKILL.md`
- 実行資産は `references/` / `prompts/` に配置
- 集約リポジトリに CI/テスト/ビルド資産を残さない
- 新規取り込み時は `external-skills/SOURCES.md` を更新
