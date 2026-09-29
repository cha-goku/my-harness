# 화면 설계

```json
{
  "screens": [
    {
      "screen": "스킬 라이브러리",
      "kind": "library",
      "roles": [
        "free",
        "paid",
        "seller",
        "admin"
      ]
    },
    {
      "screen": "내 자산 등록",
      "variant": "paid",
      "kind": "asset_form",
      "roles": [
        "paid"
      ],
      "visibility": {
        "options": [
          "private",
          "member_only"
        ],
        "default": "private"
      }
    },
    {
      "screen": "내 자산 등록",
      "variant": "seller",
      "kind": "asset_form",
      "roles": [
        "seller"
      ],
      "visibility": {
        "options": [
          "private",
          "member_only",
          "sale_request"
        ],
        "default": "private"
      }
    },
    {
      "screen": "운영자 검수",
      "kind": "admin_review",
      "roles": [
        "admin"
      ],
      "review_checklist": [
        "실제 업무에 써본 것",
        "결과 예시가 있는 것",
        "사용 방법이 명확한 것",
        "초보자가 따라할 수 있는 것",
        "특정 툴/버전/환경 조건이 적혀 있는 것",
        "개인정보/고객정보/회사기밀이 없는 것",
        "저작권 문제가 없는 것",
        "구매자가 바로 써볼 수 있는 것"
      ],
      "approve_enabled_before_checklist_complete": false,
      "transitions": [
        {
          "from": "pending",
          "to": "approved",
          "via_review": true
        },
        {
          "from": "pending",
          "to": "revision_requested",
          "via_review": true
        },
        {
          "from": "pending",
          "to": "rejected",
          "via_review": true
        }
      ]
    }
  ]
}
```
