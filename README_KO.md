# Immort

`nuwa-skill`을 중심으로 정리하고, 3개의 외부 skill을 병합한 런타임 우선 구조의 통합 Skill 저장소입니다.

## 저장소 목적

- `nuwa-skill` 핵심 유지 (`SKILL.md` + `references/` + `examples/`)
- 외부 skill을 `external-skills/` 아래로 통합
- 스킬별 단일 진입점: 루트 `SKILL.md`
- CI/테스트/빌드 소스 등 비실행 파일 제거

## 구조

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

## 통합된 외부 Skill

1. `dull-bird/diamond-sutra-skill`
2. `jinchenma94/bazi-skill`
3. `cantian-ai/bazi-persona-skill`

출처 상세는 `external-skills/SOURCES.md`를 참고하세요.

## 사용 방법

- Nuwa 본체: 루트 `SKILL.md` 사용
- 통합 skill: 각 하위 폴더의 `SKILL.md`와 런타임 자산(`references/`, `prompts/`) 사용

## 유지보수 규칙

- 1 skill = 1 루트 `SKILL.md`
- 런타임 자산은 `references/`, `prompts/`에 유지
- 이 통합 저장소에 CI/테스트/빌드 자산을 두지 않음
- 새 외부 skill 추가 시 `external-skills/SOURCES.md` 갱신
