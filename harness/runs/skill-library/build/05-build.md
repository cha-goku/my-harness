# 제작: 스킬 라이브러리

Figma 파일: Huddling MVP (https://www.figma.com/design/VrYuOr2eV4aYb5bP7uAjfl/Huddling-MVP), 페이지 "Build" (node 5:2). S3 시안이 있는 "Page 1"은 건드리지 않았다.

## 진행 상태 (중단 시 여기서 이어서)

- [x] 시작 전 파일 상태 확인
- [x] 1단계 토큰: 변수 3개 컬렉션 24개, 텍스트 스타일 12개
- [x] 2단계 컴포넌트: Components 섹션(6:34)에 컴포넌트 13개 (변형 세트 5개 포함)
- [x] 3단계 화면: 프레임 3개(7:10, 7:97, 7:194), 스크린샷 확인 후 프레임 2의 잘린 카드 1장 제거
- [x] design-export.json: 프레임 3개, 노드 130개(52 + 43 + 35)

## 남아 있던 요소 처리

이전 중단 시도의 흔적을 확인했다. 변수 컬렉션 0개, 텍스트 스타일 0개, 페이지는 "Page 1"(S3 시안 프레임 3개)뿐이었고 "Build" 페이지와 컴포넌트는 없었다. 정리할 것이 없어 처음부터 만들었다. 작업 중 스크립트 오류가 두 번 났지만(벡터 경로 문법) 실패한 호출은 아무 노드도 남기지 않았음을 확인했고, 중복은 없다.

## 폰트 진단

`figma.listAvailableFontsAsync()` 결과 Pretendard는 0건(사용 불가). Inter(Light, Regular, Bold)로 대체했다. 이 Build 페이지의 모든 텍스트와 텍스트 스타일 12개가 Inter다(숨긴 대체 없음). 굵기 대응: Light=300, Regular=400, Bold=700. Pretendard 설치 후 텍스트 스타일 12개의 폰트만 바꾸면 된다. design-export.json의 font_weight는 Inter 스타일 이름을 300/400/700으로 옮긴 값이다.

## 토큰

- 변수 컬렉션 Color (12): `color/` primary, ink, ink-soft, canvas, canvas-soft, field, hairline-soft, hairline, text-muted, text-faint, accent, on-primary. rules.json 값 그대로.
- 변수 컬렉션 Radius (4): `radius/` none 0, sm 16, md 24, full 9999
- 변수 컬렉션 Spacing (8): `spacing/` xxs 4, xs 8, sm 12, md 16, lg 24, xl 32, section 48, section-lg 64
- 텍스트 스타일 12개 (`typography/…`): display 32/700, heading-1 28/700, heading-2 24/700, heading-3 20/700, heading-4 18/700, title 17/700, body-lg 17/300, body 15/400, body-sm 13/400, link 15/700, label 12/700, caption 12/400. 글자 간격 0. design.md 표에 600은 없다.
- 변수 범위(scope)와 WEB 코드 문법을 모두 지정했다.

## 컴포넌트 (Build 페이지의 Components 섹션)

색, 모서리, 좌우 패딩, 간격은 변수에 바인딩했다. 텍스트는 텍스트 스타일에 연결했다.

1. button-primary (primary 채움, on-primary 글자, 9999, 높이 48)
2. button-outline (canvas 채움, hairline 1px, 9999)
3. button-pill-soft (canvas-soft, 9999, 뒤로 가기 화살표 포함)
4. chip (변형 State=Active/Default)
5. badge-permission (변형 Kind=paid/free/cohort)
6. badge-category (변형 Surface=default/on-soft)
7. badge-difficulty (hairline 테두리)
8. badge-accent ("유료 전환", accent 채움)
9. text-input (검색창, field 채움, 16, 아이콘 + 플레이스홀더)
10. dropdown-pill (hairline 테두리, 9999, chevron)
11. tab (변형 State=Active/Inactive)
12. skill-card (변형 State=Default/Locked, 잠금은 canvas-soft 채움 + 자물쇠 + 안내 문구)
13. banner-upgrade (유료 전환 배너: badge-accent + 문구 + button-primary)

세는 방법에 따라 13개(변형 세트 6개, 단일 컴포넌트 7개)다. 컴포넌트 속성(TEXT prop)은 만들지 않고 인스턴스 안의 텍스트를 직접 덮어썼다.

## 화면 (Build 페이지, 390×844, 좌우 여백 16)

- 스킬 라이브러리 / 유료 회원 목록 (7:10): 검색창, 칩 6개(오른쪽 잘림은 가로 스크롤 표현), 드롭다운 2개, 카드 4장(코호트 잠금 카드 1장)
- 스킬 라이브러리 / 무료 회원 목록(잠금) (7:97): 같은 상단 + 유료 전환 배너(accent 1곳) + 카드 2장(무료, 유료 잠금)
- 스킬 라이브러리 / 스킬 상세 (7:194): 뒤로 가기, 제목, 태그 3개, 메타 3줄, 탭(예시 결과 활성), 예시 결과 블록, 관련 미션 카드, 하단 고정 버튼(복사 primary, 파일 다운로드 outline)

## 임의로 정한 부분 (S3 시안과 달라진 것)

- 버튼 높이는 44/48이 섞여 있던 것을 48로 통일했다.
- 카드 패딩은 20 대신 16(spacing/md), 드롭다운 간격은 6 대신 8로 바꿨다. 4의 배수이면서 rules.json 간격 값에 맞추기 위해서다.
- 화면 위쪽 여백은 60 대신 64(spacing/section-lg)로 했다.
- 무료 회원 목록(잠금) 화면에서 코호트 잠금 카드는 마지막 카드가 프레임 아래에서 잘려 빼고, 배너 + 카드 2장만 남겼다. 코호트 잠금은 유료 회원 화면에서 보인다.
- 스킬 상세 프레임 이름은 "스킬 라이브러리 / 스킬 상세"로 했다. spec의 screens에는 "스킬 라이브러리" 하나뿐이라 design-export.json의 세 프레임 screen 값은 모두 "스킬 라이브러리"다.
- 탭 활성 항목은 그림자 없이 흰색 pill로만 표현했다. 그림자는 어디에도 쓰지 않았다.
- design-export.json에는 채움·테두리·모서리가 있는 프레임/인스턴스와 모든 텍스트 노드를 담았고, 값이 없는 배치용 프레임과 벡터 아이콘, spacer는 뺐다. 프레임마다 확인용으로 `figma_node`(프레임 노드 ID)를 추가했다.
- 추출값 점검: 굵기 400/700, 모서리 0/16/24/9999, 그림자 0, 패딩·간격 0/4/8/12/16/32.
