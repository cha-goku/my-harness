# 역할 (R6)

## 에이전트와 편집 폴더

각 에이전트는 자기 폴더만 편집할 수 있다 (`harness/runs/<묶음>/` 안).

| 역할 | 하는 일 | 편집할 수 있는 폴더 | 쓰는 도구 |
|---|---|---|---|
| researcher | S1: 레퍼런스 수집·분석 | `research/` (`01-references.md`, `02-analysis.md`) | uibowl |
| spec-writer | S2: 화면 설계 문서 | `spec/` (`03-screen-spec.md`) | 없음 |
| concept-designer | S3: 키스크린 | `concept/` (`04-keyscreens.md`) | Figma |
| builder | S4: 토큰·컴포넌트·화면 | `build/` (`05-build.md`, `design-export.json`) | Figma |
| harness-judge (읽기 전용) | G1·G2·S5 판정 | 없음 | Read, Grep, 판정 스크립트 실행 |
| orchestrator (메인) | 순서 관리, `state.json` 기록 | `state.json`만 | 전체 |

- 판정자는 파일을 쓰지 못한다. 판정 스크립트(에이전트가 아님)가 `review/06-review.json`을 쓴다.
- `state.json`은 오케스트레이터만 고친다. G3 컨펌은 작업자가 "컨펌 났어"라고 말하면 오케스트레이터가 `g3_approved: true`를 기록한다. 에이전트가 스스로 컨펌을 기록하는 일은 없다.
- `harness-judge`는 새로 만든다. 기존 `design-token-auditor`는 코드의 하드코딩을 찾는 용도라 Figma 내보내기 JSON 판정에는 맞지 않는다.

## 자연어 트리거

| 말하면 | 실행되는 것 |
|---|---|
| "○○ 화면 시작해줘" | 새 묶음 폴더와 `state.json`을 만들고 researcher 실행 |
| "레퍼런스 모아줘" / "분석해줘" | researcher |
| "설계 문서 써줘" | spec-writer |
| "키스크린 그려줘" | concept-designer |
| "토큰이랑 컴포넌트 만들어줘" | builder |
| "검수해줘" / "위반 확인해줘" | harness-judge |
| "컨펌 났어" | orchestrator가 `state.json`에 `g3_approved: true` 기록 |
| "이어서 해줘" | `state.json`이 가리키는 단계부터 재개 |
