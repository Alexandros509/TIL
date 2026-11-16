# 📝 TIL (Today I Learned)

> **"매일 조금씩 꾸준히 배우고 기록합니다."**

매일 학습한 내용, 문제 해결 과정, 깨달은 점을 마크다운으로 남기는 저장소입니다.

- [TIL 목차](./TIL_INDEX.md) ← 대분류·태그·글 링크는 여기
- 일과 글: `2026/08/`, `2026/09/` …
- 방과 후: `AWS_Afterschool/`, `Python_Afterschool/`
- 그림: `images/`
- `TIL_INDEX.md`는 GitHub Actions가 자동 갱신합니다. 손으로 고치지 않습니다.

---

## 🗂️ Categories

분류는 폴더가 아니라 각 글 Front Matter의 `category`입니다.
`AWS_Afterschool`은 폴더 이름일 뿐, 대분류가 아닙니다.
목차에서 바로 이동할 수 있습니다.

순서는 교안 합본(2026-11-16) 과목 순서입니다. Linux·AWS는 교안 밖 트랙입니다.

* [🌿 Git](./TIL_INDEX.md#git) — 버전 관리, 명령어, 워크플로우 (교안 01)
* [🧠 AI Literacy](./TIL_INDEX.md#ai-literacy) — 생성형 AI 이해, 안전한 활용 (교안 02)
* [🤖 Machine Learning](./TIL_INDEX.md#machine-learning) — 회귀, 신경망, PyTorch (교안 03)
* [🐍 Python](./TIL_INDEX.md#python) — 문법, 자료구조, 비동기 (교안 04)
* [🗄️ SQL](./TIL_INDEX.md#sql) — SQL & 데이터베이스 (교안 05)
* [🧩 Database & AI](./TIL_INDEX.md#database--ai) — PostgreSQL·Supabase, 트랜잭션, RLS (교안 06)
* [🖥️ Frontend](./TIL_INDEX.md#frontend) — HTML/CSS, JavaScript, DOM (교안 07)
* [🔷 TypeScript](./TIL_INDEX.md#typescript) — 프론트엔드 심화 (교안 08)
* [⚛️ React & Next.js](./TIL_INDEX.md#react--nextjs) — 프론트엔드 응용 (교안 09)
* [⚙️ Backend](./TIL_INDEX.md#backend) — 백엔드 아키텍처 & API 설계 (교안 10)
* [💬 LLM](./TIL_INDEX.md#llm) — LLM 프롬프트 엔지니어링 (교안 11)
* [🔎 RAG](./TIL_INDEX.md#rag) — RAG 파이프라인 설계 (교안 12)
* [🔀 Workflow](./TIL_INDEX.md#workflow) — 워크플로우 오케스트레이션 (교안 13)
* [📈 LLMOps](./TIL_INDEX.md#llmops) — LLMOps (교안 14)
* [🎤 특강](./TIL_INDEX.md#특강) — 정규식, NumPy/Pandas, Streamlit, Supabase 등 (교안 특강 · 단독으로 쓰지 않고 해당 트랙과 함께)
* [🐧 Linux](./TIL_INDEX.md#linux) — 셸, 권한, 프로세스
* [☁️ AWS](./TIL_INDEX.md#aws) — EC2, IAM, VPC, 서버리스

하루가 두 트랙을 넘나들면 목차 두 곳에 같은 글이 올라갑니다.

---

## 📌 룰 및 작성 규칙

1. **매일 작성하기:** 작은 개념이라도 학습한 날에는 기록을 남긴다.
2. **나만의 언어로 정리하기:** 복사하지 않고, 내가 이해한 방식과 인사이트를 적는다.
3. **문제와 해결 과정 포함하기:** 에러와 시행착오, 해결을 남긴다.
4. **미래의 나를 위해 쓰기:** 다시 읽었을 때 복습되게 구조화한다.
5. **분류는 Front Matter에:** `category`는 위 목록(Git / AI Literacy / Machine Learning / Python / SQL / Database & AI / Frontend / TypeScript / React & Next.js / Backend / LLM / RAG / Workflow / LLMOps / 특강 / Linux / AWS)만 쓴다. 목록·별칭의 기준은 `scripts/build_til_index.py`의 `CATEGORIES`·`CATEGORY_ALIASES`다.
