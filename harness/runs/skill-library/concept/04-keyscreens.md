# 키스크린: 스킬 라이브러리

Figma 파일: Huddling MVP (https://www.figma.com/design/VrYuOr2eV4aYb5bP7uAjfl/Huddling-MVP)
근거: `spec/03-screen-spec.md`, `design.md`, `rules.json`. 프레임은 모두 390×844.

## 폰트 주의

Figma 파일에서 Pretendard를 불러올 수 없어(설치되지 않음) 임시로 Inter(Light/Regular/Bold, 굵기 300/400/700 대응)로 그렸다. 폰트를 설치한 뒤 텍스트 폰트를 Pretendard로 바꿔야 한다.

## 프레임 1. 스킬 라이브러리 / 유료 회원 목록

- 검색창(field 채움, 16px 모서리), 태그 필터 칩 줄(가로 스크롤, 오른쪽 칩이 잘려 스크롤을 암시), 드롭다운형 필터(난이도, 권한).
- 카드 목록: 스킬명, 카테고리 태그, 난이도 태그, 권한 배지(유료/무료/코호트)만 올렸다.
- 코호트 전용 카드는 이 유료 회원이 해당 코호트가 아니므로 잠금 표시(자물쇠 + 회색 채움)로 보인다.
- 반영한 분석: A1(카드 목록), A2(검색, 칩 + 드롭다운), A3(난이도 작은 태그).

## 프레임 2. 스킬 라이브러리 / 무료 회원 목록(잠금)

- 같은 상단(검색, 칩, 필터) 아래에 유료 전환 안내 배너: accent 색 "유료 전환" 배지 1곳, 잉크 pill 버튼 "유료 전환 안내 보기".
- 무료 카드는 그대로, 유료/코호트 카드는 숨기지 않고 자물쇠 + "유료로 전환하면 열 수 있어요." 안내를 붙였다. 스킬명, 카테고리, 난이도, 권한 배지는 그대로 보인다.
- 반영한 분석: A1, A2, A3, 잠금 카드 + 유료 전환 안내(설계 §5-1). accent 사용은 이 화면에서 1곳.

## 프레임 3. 스킬 상세

- 뒤로 가기 pill, 스킬명, 카테고리·난이도·권한 태그, 추천 대상·사용 도구·업데이트 날짜(상세에만 둔 항목).
- 탭(사용 정보 / 프롬프트·파일 / 예시 결과) 중 "예시 결과" 탭을 활성 상태로 보여주고 예시 결과 블록을 채웠다.
- 관련 미션 카드형 링크(누르면 미션 화면으로 이동).
- 하단 고정 버튼 영역: 잉크 pill "복사", 아웃라인 pill "파일 다운로드".
- 반영한 분석: A4(복사·다운로드 하단 고정), A5(탭 구획, 예시 결과), A6(관련 미션 링크). 이 화면에는 accent를 쓰지 않았다.

## 반영하지 않은 것

- A7(결과 없음 빈 화면)은 PRD에 없는 제안이라 G2에서 채택 여부가 정해지지 않아 키스크린에 그리지 않았다.
- 잠금 카드를 눌렀을 때의 이동은 설계에 없어 그리지 않았다.

## 프레임 목록

```json
{
  "frames": [
    {
      "name": "스킬 라이브러리 / 유료 회원 목록",
      "width": 390,
      "height": 844,
      "figma_url": "https://www.figma.com/design/VrYuOr2eV4aYb5bP7uAjfl/Huddling-MVP?node-id=2-57"
    },
    {
      "name": "스킬 라이브러리 / 무료 회원 목록(잠금)",
      "width": 390,
      "height": 844,
      "figma_url": "https://www.figma.com/design/VrYuOr2eV4aYb5bP7uAjfl/Huddling-MVP?node-id=2-127"
    },
    {
      "name": "스킬 상세",
      "width": 390,
      "height": 844,
      "figma_url": "https://www.figma.com/design/VrYuOr2eV4aYb5bP7uAjfl/Huddling-MVP?node-id=2-197"
    }
  ]
}
```
