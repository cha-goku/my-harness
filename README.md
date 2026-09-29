# 허들링 디자인 하네스

허들링 앱(AI 실무 학습 플랫폼)의 화면을 **리서치 → 설계 → 시안 → 제작 → 검수** 순서로 만드는 Claude Code 하네스입니다.
사람이 손으로 하던 디자인 작업을 작업 에이전트, 게이트, 판정 스크립트로 옮겼습니다.

## 구조

| 경로 | 내용 |
|---|---|
| `prd.md` | 서비스 PRD (판정 기준) |
| `design.md` | 디자인 시스템 문서 (판정 기준). 숫자 값의 기준은 `harness/rules.json` |
| `story-service.md` | "무엇을 위한 일인지": 유저스토리 5개와 어기면 안 되는 것 2개 |
| `story-work.md` | "어떻게 일했는지": 작업 7단계, 산출물, 게이트, 에이전트 경계 |
| `harness/CLAUDE.md` | 오케스트레이터 진입점 |
| `harness/*.md` | 목적, 파이프라인, 산출물, 게이트, 역할, 검증 (인터뷰 R0~R8 결과) |
| `harness/rules.json` | 규칙 SSOT (토큰 값, 게이트 기준, 서비스 규칙) |
| `harness/check/` | 판정 스크립트 `check.py`, 픽스처 테스트 `run_fixtures.py` |
| `harness/fixtures/` | 판정 스크립트 시험용 입력 (정상 1세트 + 위반 케이스) |
| `harness/.claude/agents/` | researcher, spec-writer, concept-designer, builder, harness-judge |
| `harness/runs/` | 실행 결과 (`skill-library`, `asset-review` 두 묶음) |

## 파이프라인

```
S1 리서치 → G1 → S2 설계 → G2 → S3 시안 → G3(사람 컨펌) → S4 제작 → S5 검수(위반 0건)
```

- G1, G2, S5는 스크립트가 판정합니다. 사람이 승인하는 곳은 G3 한 곳입니다.
- 같은 단계에서 3번 실패하면 자동 반복을 멈추고 사람에게 넘깁니다.
- 서비스 규칙(`story-service.md`)은 G2에서 설계 문서로, S5에서 설계 문서와 Figma 프레임으로 확인합니다.
  - 자료는 기본 비공개, 판매 신청은 판매 승인 회원만
  - 판매 자산은 검수를 거쳐야 하고 체크리스트 8개를 모두 채운 뒤에만 승인 가능

## 사용법

`harness/` 폴더에서 Claude Code 세션을 시작합니다. 에이전트는 세션을 시작할 때 등록됩니다.

필요한 것:
- Claude Code
- Python 3 (판정 스크립트, 외부 패키지 없음)
- Figma MCP (S3, S4), uibowl MCP (S1)
- 폰트 Pretendard. Figma 도구 환경은 설치된 폰트를 불러오지 못해서, 에이전트는 Inter로 그리고 작업자가 Figma에서 텍스트 스타일을 Pretendard로 바꿉니다.

시작 문구: `"○○ 화면 시작해줘"` (전체 트리거는 `harness/roles.md`)

## 판정 스크립트

```bash
cd harness
python3 check/run_fixtures.py                       # 픽스처 테스트 (46개)
python3 check/check.py docs-sync                    # rules.json과 design.md 값 비교
python3 check/check.py g1 --run runs/skill-library  # g1, g2, g3, s5
```

## 실행 결과

| 묶음 | 화면 | 결과 |
|---|---|---|
| `skill-library` | 스킬 라이브러리 | G1, G2, G3, S5 통과 |
| `asset-review` | 내 자산 등록, 운영자 검수 | G1, G2, S5 통과 (S3는 skill-library의 컨셉 재사용) |

## 알려진 한계

- `design-export.json`은 빌더 에이전트가 Figma 노드에서 읽어 파일로 옮긴 값입니다. 스크립트는 이 파일과 규칙만 비교하므로 옮기는 과정의 오류는 잡지 못합니다.
- 프레임에서 확인하지 못하는 규칙: "검수 없이 승인됨으로 가는 전환"은 설계 문서의 전환 목록으로만 검사합니다. 체크가 모두 된 상태의 화면은 Figma에 없어서, 그 경로는 픽스처로만 확인합니다.
- 폴더 제한(에이전트별 편집 폴더)은 에이전트 지시문으로만 걸려 있고 도구 수준에서 강제하지 않습니다.
- 두 번의 실행은 에이전트가 등록되기 전이라 `general-purpose` 에이전트가 각 에이전트 정의를 읽고 대신 수행했습니다.
- 체크리스트 행의 터치 영역이 32~38px로 44px보다 작습니다. 한 화면에 8개 행과 가격 입력을 넣기 위해 유지하기로 했습니다.
