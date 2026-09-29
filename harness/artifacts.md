# 산출물 (R4)

## 폴더 구조

화면 묶음마다 `harness/runs/<묶음이름>/` 폴더를 만들고 그 안에 둔다. 에이전트마다 편집 폴더가 하나씩 있다 (`roles.md` 참고).

| 단계 | 파일 (`harness/runs/<묶음이름>/` 안) |
|---|---|
| S1 리서치 | `research/01-references.md` (앱·화면·uibowl 링크), `research/02-analysis.md` |
| S2 설계 | `spec/03-screen-spec.md` |
| S3 시안 | `concept/04-keyscreens.md` (Figma 링크와 프레임 이름 목록) |
| S4 제작 | `build/05-build.md` (Figma에 만든 토큰·컴포넌트·화면 목록), `build/design-export.json` |
| S5 검수 | `review/06-review.json` (위반 목록, 판정 스크립트가 씀) |
| 공통 | `state.json` (오케스트레이터만 씀) |

## 규칙 SSOT

- 파일: `harness/rules.json` (묶음 폴더 밖, 전체 공통)
- 담는 것: 토큰 값(색, 모서리, 굵기, 간격)과 세어야 하는 규칙. `on-primary` 값도 여기서 확정한다.
- 판정 스크립트는 이 파일과 `design-export.json`만 읽는다.
- `design.md`는 사람이 읽는 설명 문서로 남긴다. 숫자 값의 기준은 `rules.json`이다.

## Figma 결과를 스크립트에 넘기는 방법

S4가 Figma 노드의 값(색, 모서리, 굵기, 그림자, 간격)을 `design-export.json`으로 내보낸다. 판정 스크립트는 이 JSON과 `rules.json`만 비교한다.

## 재개

- 각 묶음 폴더의 `state.json`에 현재 단계, 게이트 통과 여부, 실패 횟수를 기록한다.
- 중간에 끊기면 `state.json`이 가리키는 단계부터 다시 시작한다.
