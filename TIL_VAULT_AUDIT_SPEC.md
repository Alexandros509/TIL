---
title: TIL Vault — 옵시디언 활용도 진단 및 개선 명세서
doc_type: audit-spec
created: 2026-09-17
updated: 2026-09-18
author: 417now (with Claude / Claudian)
status: living-document
---

# TIL Vault 진단·개선 명세서

> 이 문서는 사람과 AI 모델(Claude 등) 양쪽이 별도 대화 맥락 없이도 읽고
> 이 저장소(TIL vault)의 현재 상태와 합의된 개선 방향을 파악할 수 있도록 작성한다.
> 새 결정이 생기면 "결정 로그"에 추가하고, 조치 항목의 상태를 갱신한다.

---

## 1. 대상 저장소 개요

- 성격: 개인 학습 기록(TIL, Today I Learned) Obsidian vault. Git으로 버전 관리, GitHub Actions로 일부 자동화.
- 시작일: 2026-08-03. 진단 시점(2026-09-17~18) 기준 약 7주차, 평일 커버리지 97%(32/33 평일 기록, 결측 1일: 2026-08-17).
- 규모: 정식 노트(`2026/**`) 34개, `AWS_Afterschool/**` 3개, 별도 제텔카스텐 폴더 `궁금증/**`(Q&A 42, 개념 5, 주제맵 4) — 총 100개 마크다운 노트.
- 핵심 파이프라인: **raw(초안) → 편집(Claude 프롬프트, `TIL_EDITOR_PROMPT.md`) → 정식본(`2026/MM/`) → GitHub Actions가 `TIL_INDEX.md` 자동 재생성**.
- 인덱스 스캔 범위(`scripts/build_til_index.py`): `TIL_GLOBS = ("20*/**/*.md", "AWS_Afterschool/**/*.md")`. **`raw/**`는 스캔 대상이 아님** — 이 사실이 아래 결정 D-2의 근거.

---

## 2. 현재 상태 진단 (2026-09-17 기준)

### 2.1 종합 점수: 73 / 100

| 항목 | 배점 | 점수 | 근거 |
|---|---|---|---|
| 꾸준함 | 20 | 18 | 평일 출석 97% |
| 구조/조직 | 20 | 17 | category 기반 폴더 분리 명확. raw/edited 이중 구조는 진단 시점엔 미정리 상태였음(→ D-1로 해결) |
| 메타데이터 일관성 | 15 | 10 | 정식본은 frontmatter 정돈됨. raw 캡처본은 title/category/tags가 항상 빈 채로 저장됨 |
| 링크·백링크·그래프 활용 | 20 | 6 | 정식 노트 34개 중 `[[ ]]` 사용 6개뿐. 날짜 간 연결, 궁금증 폴더와의 교차 링크 거의 없음. 그래프 뷰 색상 그룹 미설정 |
| 자동화 | 15 | 14 | GitHub Actions 기반 인덱스·이미지 경로 자동 갱신 파이프라인 우수 |
| PKM 확장(`궁금증` 제텔카스텐) | 10 | 8 | Q&A→개념→주제맵 구조와 상호 백링크는 훌륭하나 메인 TIL 로그와 완전히 단절 |

**총평**: 기록 습관·자동화 인프라는 상위권. 옵시디언 고유 강점인 "링크로 연결된 그래프"는 사실상 미활용 — 지금 구조는 노션/깃허브 블로그로 옮겨도 손실이 거의 없다.

### 2.2 구조 스냅샷

```
TIL/
├─ 2026/08~09/          # 정식(편집 완료) TIL — README가 명시한 정본 위치
├─ raw/2026/…            # 캡처 초안 (D-1 이후 폴더 분리 확정)
├─ AWS_Afterschool/       # 방과 후 트랙
├─ 궁금증/                 # 별도 git 리포(TIL-Vault)로 독립 관리되는 미니 제텔카스텐
│   ├─ 00_Inbox / 10_Q&A / 20_개념 / 30_주제맵 / 40_흐름(미사용) / 90_템플릿
├─ references/, scripts/, .github/workflows/
└─ TIL_INDEX.md           # GitHub Actions가 category·tag 기준 자동 생성하는 MOC
```

---

## 3. 결정 로그 (Decision Log)

| ID | 날짜 | 결정 | 근거 |
|---|---|---|---|
| D-1 | 2026-09-17 | raw(초안)와 edited(정식본) 폴더를 물리적으로 분리한다(`raw/**` vs `2026/**`). | 초안과 완성본이 섞여 있으면 인덱스·검색·링크가 혼란스러워짐. |
| D-2 | 2026-09-18 | **raw 파일은 frontmatter를 두지 않는다.** edited 파일에만 정돈된 frontmatter를 쓰고, edited → raw로 원본 링크 1개만 건다. | `build_til_index.py`의 `TIL_GLOBS`가 `raw/**`를 스캔하지 않으므로, raw의 frontmatter는 어떤 자동화·검색에도 기여하지 않음. 캡처 단계의 타이핑 부담(frontmatter 채우기)만 없앤다. 날짜는 파일명(`YYYYMMDD TIL.md`)이 이미 담고 있어 중복. |

### D-2 실행 스펙

**raw 파일** (`raw/2026/MM/YYYYMMDD TIL.md`)
- frontmatter 없음. 파일은 `# 오늘의 TIL` 본문부터 바로 시작.
- 기존에 이미 만들어진 raw 파일들(`title:`/`date:`/`category:`/`tags:` 빈 블록)은 편집 시점에 자동으로 잘려나가므로 소급 수정은 불필요(선택 사항).

**edited 파일** (`2026/MM/YYYYMMDD TIL.md`)
- frontmatter에 원본 raw 노트를 가리키는 필드를 추가:
  ```yaml
  ---
  title: <제목>
  date: 2026-09-18
  category: <카테고리>
  tags: [...]
  source_raw: "[[raw/2026/09/20260918 TIL]]"
  ---
  ```
- `source_raw`는 Obsidian이 위키링크로 인식해 백링크·그래프에도 반영됨(별도 body 링크 불필요).
- `TIL_EDITOR_PROMPT.md`의 "Front Matter 정리" 규칙에 `source_raw` 필드 추가를 반영해야 함(→ 조치 항목 OBS-02).

---

## 4. 열린 조치 항목 (Open Action Items)

우선순위 High → Low. 상태는 각자 진행하면서 갱신.

| ID | 우선순위 | 항목 | 완료 기준(Acceptance Criteria) | 상태 |
|---|---|---|---|---|
| OBS-01 | High | raw 캡처 템플릿에서 frontmatter 블록 제거 | `.obsidian/templates.json` 혹은 raw 전용 템플릿 파일이 frontmatter 없이 `# 오늘의 TIL` 골격만 생성 | Open |
| OBS-02 | High | `TIL_EDITOR_PROMPT.md`에 `source_raw` frontmatter 필드 규칙 추가 | 프롬프트 실행 시 매번 자동으로 원본 raw 경로를 `source_raw`에 채움 | Open |
| OBS-03 | High | 날짜 간 실제 링크 연결 | "어제의 복습" 섹션 또는 본문 상단에 전날 노트를 `[[2026/MM/YYYYMMDD TIL]]` 위키링크로 연결 | Open |
| OBS-04 | Medium | 태그 통제 어휘집 도입 | `references/tags.md`(가칭)에 재사용 가능한 태그 목록 유지, 신규 노트는 여기서만 선택 | Open |
| OBS-05 | Medium | `궁금증` 제텔카스텐 ↔ TIL 로그 교차 링크 | 같은 주제를 다룬 TIL 노트와 `궁금증/20_개념`·`10_Q&A` 노트가 최소 1개씩 상호 링크됨 | Open |
| OBS-06 | Medium | Daily Notes 플러그인에 raw 폴더/템플릿 연결 | `.obsidian/daily-notes.json`에 folder=`raw/2026/MM`, template=OBS-01 결과물 지정 | Open |
| OBS-07 | Low | 그래프 뷰 색상 그룹 설정 | `.obsidian/graph.json`의 `colorGroups`에 category별 그룹 최소 1개 이상 정의 | Open |
| OBS-08 | Low | 위키링크 스타일 통일 | 내부 링크가 `[[ ]]`와 `](<...>)`로 혼재된 것을 하나로 통일(`useMarkdownLinks` 설정과 일치시킴) | Open |

---

## 5. 이 문서의 유지 방법

- 새 진단/결정이 있을 때마다 §3 결정 로그에 D-n으로 추가.
- 조치 항목 완료 시 §4 상태를 `Open → Done`으로 바꾸고, 필요하면 완료일을 붙인다.
- 이 파일은 vault 루트에 위치하며 `TIL_INDEX.md` 자동 빌드 대상(`20*/**/*.md`)에 포함되지 않으므로, 카테고리 인덱스에는 나타나지 않는다(의도된 동작).
