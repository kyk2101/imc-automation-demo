# IMC Automation Demo

AI 튜터 4회차 강의 데모 리포지토리.
구글시트 데이터를 매일 자동으로 가져와 대시보드 데이터로 변환하고,
주간 알림을 Teams DM으로 발송합니다.

## 구조

```
[Google Sheets]  ← 일정 입력
       ↓ (sync.yml: 매일 09:00 KST 자동 실행)
[data.json] ← GitHub 리포에 자동 커밋
       ↓ (notify.yml: 매주 월요일 09:00 KST 자동 실행)
[Teams DM 알림] ← Adaptive Card
```

## 대시보드 (`dashboard.html`)

`data.json`을 Gantt 차트 형태로 시각화하는 단일 HTML 파일입니다.

- **브랜드별 그룹** 트리(접기/펼치기) + 채널 · 상태 컬럼
- **월/주 타임라인** 바 (상태별 색상: 🟢 진행중 · 🔴 예정 · ⚪ 종료)
- **오늘 기준선**, 호버 툴팁, 브랜드/채널/상태 필터 + 프로모션 검색
- 상단 요약 카드(전체/진행중/예정/종료, 브랜드·채널 수)

보는 방법:

- 라이브 데이터로 보기: 폴더에서 `python -m http.server` 실행 → `http://localhost:8000/dashboard.html`
- 그냥 파일을 더블클릭해도 동작(내장 스냅샷으로 폴백)

## 셋업 (5분)

### 1. 이 리포 fork

우상단 Fork 버튼 → 본인 계정으로 복제.

### 2. GitHub Secrets 3개 등록

리포 → Settings → Secrets and variables → Actions → New repository secret

| Name | Value |
|---|---|
| `GOOGLE_JSON_KEY` | Google Cloud 서비스 계정 JSON 파일 내용 전체 (그대로 붙여넣기) |
| `SHEET_ID` | 본인 구글시트 URL의 `/d/` 와 `/edit` 사이 문자열 |
| `TEAMS_WEBHOOK_URL` | Teams Workflows에서 받은 Webhook URL |

### 3. 시트에 서비스 계정 이메일 공유

구글시트 우상단 "공유" → 서비스 계정 이메일(`...@...iam.gserviceaccount.com`) 추가 → **뷰어** 권한.

### 4. 동작 확인

1. Actions 탭 → **"시트 → data.json 동기화"** → "Run workflow"
2. 성공하면 `data.json`이 자동 커밋됨
3. 이어서 **"Teams DM 알림 발송"** → "Run workflow"
   - `dry_run=true`로 먼저 시뮬레이션 권장
   - `dry_run=false`로 실제 발송 → Teams로 알림 도착

## 시트 스키마

첫 번째 워크시트(sheet1)에 아래 컬럼을 **1행**에 배치:

| 컬럼 | 설명 | 예시 |
|---|---|---|
| BRAND | 브랜드명 | MLB |
| CHANNEL | 판매 채널 | 자사몰 |
| PROMO_NAME | 프로모션명 | 봄맞이 할인전 |
| START_DATE | 시작일 (YYYY-MM-DD) | 2026-05-01 |
| END_DATE | 종료일 (YYYY-MM-DD) | 2026-05-15 |
| STATUS | 상태 | 진행중 / 종료 / 예정 |

## cron 스케줄 (KST 기준)

| 워크플로 | 한국시간 | UTC cron |
|---|---|---|
| `sync.yml` | 매일 09:00 | `0 0 * * *` |
| `notify.yml` | 매주 월요일 09:00 | `0 0 * * 1` |

## 알림 조건

`notify_teams.py`가 (BRAND, CHANNEL)별 마지막 `END_DATE`를 보고:

- **🚨 이미 종료**: `END_DATE < 오늘` → 재등록 필요
- **⚠️ 7일 이내 종료 예정**: `0 ≤ END_DATE - 오늘 ≤ 7`
- 둘 다 없으면 발송 스킵
