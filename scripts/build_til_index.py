#!/usr/bin/env python3
"""설정된 TIL_GLOBS Front Matter를 읽어 루트 TIL_INDEX.md를 다시 쓴다.

목차 구조
1. 대분류(category) — 교안 합본 과목 기준 CATEGORIES 순서, 별칭은 CATEGORY_ALIASES로 정규화
2. 태그(tags)

Front Matter 점검(허용 밖 키, tags 4개 초과, date 누락, 허용 밖 category)은
경고로만 출력하고 목차 생성은 계속한다.

전환일은 category 리스트라 두 대분류 섹션에 같은 글이 들어간다.
date가 없으면 파일명 YYYYMMDD를 쓴다.
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
# 일과는 연도 폴더, 방과 후는 *_Afterschool.
TIL_GLOBS = (
    "20*/**/*.md",
    "AWS_Afterschool/**/*.md",
    "Python_Afterschool/**/*.md",
)
SKIP_NAMES = {"README.md", "TIL.md", "TIL_INDEX.md"}
INDEX_PATH = ROOT / "TIL_INDEX.md"
FILENAME_DATE = re.compile(r"^(\d{8})")

# 대분류(category) 정의 — 교안 합본(2026-11-16) 과목 순서 + 교안 밖 트랙.
# (category 값, 교안 폴더, 교안 과목명)
CATEGORIES = [
    ("Git", "01-git", "Git & Github"),
    ("AI Literacy", "02-ai-literacy", "AI Literacy"),
    ("Machine Learning", "03-ml", "머신러닝 기초"),
    ("Python", "04-python", "Python 기초"),
    ("SQL", "05-sql", "SQL & 데이터베이스"),
    ("Database & AI", "06-db-ai", "데이터베이스 & AI 활용"),
    ("Frontend", "07-frontend", "프론트엔드 개발"),
    ("TypeScript", "08-typescript", "프론트엔드 심화 (TypeScript)"),
    ("React & Next.js", "09-react", "프론트엔드 응용 (React/Next.js)"),
    ("Backend", "10-backend", "백엔드 아키텍처 & API 설계"),
    ("LLM", "11-llm", "LLM 프롬프트 엔지니어링"),
    ("RAG", "12-rag", "RAG 파이프라인 설계"),
    ("Workflow", "13-workflow", "워크플로우 오케스트레이션"),
    ("LLMOps", "14-llmops", "LLMOps"),
    # 특강은 단독으로 쓰지 않는다. 항상 해당 트랙과 함께 [트랙, 특강].
    ("특강", "특강", "특강 (정규식·PostgreSQL 함수·NumPy/Pandas·Streamlit·Tailwind·Supabase·node:test 등, 트랙과 함께)"),
    ("Linux", "-", "교안 밖 (방과 후·자습)"),
    ("AWS", "-", "교안 밖 (AWS 방과 후)"),
]
CATEGORY_ORDER = [c[0] for c in CATEGORIES]

# 별칭·옛 표기 → 정식 category. 대소문자·앞뒤 공백 무시.
# Front Matter를 고치기 전에도 목차가 깨지지 않게 하는 안전망이다.
# "Frontend"는 07 과목의 정식 값이라 그대로 둔다(TS/React 날을 자동으로 옮기지 않음).
CATEGORY_ALIASES = {
    "git": "Git", "github": "Git", "git & github": "Git",
    "ail": "AI Literacy", "ai 리터러시": "AI Literacy", "ai literacy": "AI Literacy",
    "생성형 ai": "AI Literacy", "프롬프트 리터러시": "AI Literacy",
    "ml": "Machine Learning", "머신러닝": "Machine Learning", "머신러닝 기초": "Machine Learning",
    "딥러닝": "Machine Learning",
    "py": "Python", "python": "Python", "파이썬": "Python", "python 기초": "Python",
    "sql": "SQL", "database": "SQL", "데이터베이스": "SQL", "sql & 데이터베이스": "SQL",
    "dbai": "Database & AI", "db-ai": "Database & AI", "db & ai": "Database & AI",
    "database & ai": "Database & AI", "데이터베이스 & ai 활용": "Database & AI",
    "데이터베이스와 ai 활용": "Database & AI", "supabase": "Database & AI",
    "fe": "Frontend", "frontend": "Frontend", "프론트엔드": "Frontend", "프론트엔드 개발": "Frontend",
    "ts": "TypeScript", "typescript": "TypeScript", "프론트엔드 심화": "TypeScript",
    "rn": "React & Next.js", "react": "React & Next.js", "next.js": "React & Next.js",
    "nextjs": "React & Next.js", "react/next.js": "React & Next.js", "react & next.js": "React & Next.js",
    "프론트엔드 응용": "React & Next.js",
    "be": "Backend", "backend": "Backend", "백엔드": "Backend", "api 설계": "Backend",
    "백엔드 아키텍처 & api 설계": "Backend",
    "llm": "LLM", "프롬프트 엔지니어링": "LLM", "llm 프롬프트 엔지니어링": "LLM",
    "prompt engineering": "LLM",
    "rag": "RAG", "rag 파이프라인 설계": "RAG",
    "wf": "Workflow", "workflow": "Workflow", "워크플로우": "Workflow",
    "워크플로우 오케스트레이션": "Workflow",
    "ops": "LLMOps", "llmops": "LLMOps", "llm ops": "LLMOps",
    "특강": "특강", "special lecture": "특강",
    "linux": "Linux", "리눅스": "Linux",
    "aws": "AWS", "amazon web services": "AWS",
}
ALLOWED_FM_KEYS = {"title", "date", "tags", "category"}
MAX_TAGS = 4


def canonical_category(value: str) -> str:
    key = re.sub(r"\s+", " ", str(value)).strip()
    if key in CATEGORY_ORDER:
        return key
    return CATEGORY_ALIASES.get(key.lower(), key)


def escape_markdown_text(text: str) -> str:
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def sanitize_heading(text: str) -> str:
    cleaned = re.sub(r"[\r\n]+", " ", str(text)).strip()
    cleaned = cleaned.lstrip("#").strip()
    return cleaned or "Untitled"


def parse_front_matter(text: str, notes: list[str] | None = None) -> dict:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        if notes is not None:
            notes.append("Front Matter 없음")
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        if notes is not None:
            notes.append("Front Matter 닫는 --- 없음")
        return {}
    raw = parts[1]
    try:
        import yaml

        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        if notes is not None:
            notes.append("YAML 파싱 실패 → 느슨한 파서로 읽음")
        return parse_front_matter_loose(raw)


def parse_front_matter_loose(raw: str) -> dict:
    data: dict = {}
    key = None
    list_keys = {"tags", "category"}
    for line in raw.splitlines():
        if re.match(r"^-\s+", line) and key in list_keys:
            data.setdefault(key, [])
            data[key].append(re.sub(r"^-\s+", "", line).strip().strip("\"'"))
            continue
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in list_keys:
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                data[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
            elif value:
                data[key] = [value.strip("\"'")]
            else:
                data[key] = []
        else:
            data[key] = value.strip("\"'")
    return data


def normalize_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    if isinstance(value, list):
        out = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                out.append(text)
        return out
    return [str(value).strip()]


def parse_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def date_from_filename(name: str) -> date | None:
    m = FILENAME_DATE.match(name)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None


def collect_entries() -> tuple[list[dict], list[str]]:
    entries: list[dict] = []
    warnings: list[str] = []

    paths: list[Path] = []
    for pattern in TIL_GLOBS:
        paths.extend(ROOT.glob(pattern))
    if not paths:
        warnings.append("20YY/MM/*.md TIL이 없습니다")
        return entries, warnings

    for path in sorted(set(paths)):
        if path.name in SKIP_NAMES:
            continue
        if path.resolve() == INDEX_PATH.resolve():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        notes: list[str] = []
        meta = parse_front_matter(text, notes)
        tags = [sanitize_heading(t) for t in normalize_list(meta.get("tags"))]
        categories: list[str] = []
        for raw_cat in normalize_list(meta.get("category")):
            cat = canonical_category(sanitize_heading(raw_cat))
            if cat != sanitize_heading(raw_cat):
                notes.append(f"category 별칭 {raw_cat!r} → {cat!r}")
            if cat not in CATEGORY_ORDER:
                notes.append(f"허용 목록 밖 category {cat!r}")
            if cat not in categories:
                categories.append(cat)
        if meta and not categories:
            notes.append("category 없음")
        if categories == ["특강"]:
            notes.append("특강 단독 category — 해당 트랙과 함께 [트랙, 특강]으로 쓴다")
        extra_keys = sorted(str(k) for k in meta if k not in ALLOWED_FM_KEYS)
        if extra_keys:
            notes.append("허용 밖 키: " + ", ".join(extra_keys))
        if len(tags) > MAX_TAGS:
            notes.append(f"tags {len(tags)}개 (최대 {MAX_TAGS})")
        if meta and not parse_date(meta.get("date")):
            notes.append("date 없음/형식 오류 → 파일명 날짜 사용")
        fn_date = date_from_filename(path.name)
        fm_date = parse_date(meta.get("date"))
        if fn_date and fm_date and fn_date != fm_date:
            notes.append(f"date {fm_date} ≠ 파일명 {fn_date}")
        for note in notes:
            warnings.append(f"{rel}: {note}")
        title = sanitize_heading(str(meta.get("title") or "").strip() or path.stem)
        sort_date = parse_date(meta.get("date")) or date_from_filename(path.name)
        if sort_date is None:
            warnings.append(f"{rel}: 날짜 없음, 건너뜀")
            continue
        entries.append(
            {
                "title": title,
                "date": sort_date,
                # 파일명이 #로 시작하면 마크다운이 제목 앵커로 오해하므로 인코딩한다.
            "path": "./" + quote(path.relative_to(ROOT).as_posix(), safe="/"),
                "tags": tags,
                "categories": categories,
            }
        )
    return entries, warnings


def _render_group(lines: list[str], heading: str, items: list[dict], level: str = "##") -> None:
    heading = sanitize_heading(heading)
    lines.append(f"{level} {heading}")
    items = sorted(items, key=lambda x: (x["date"], x["title"]), reverse=True)
    seen = set()
    for item in items:
        key = (item["path"], item["title"], item["date"])
        if key in seen:
            continue
        seen.add(key)
        label = escape_markdown_text(f"{item['date'].isoformat()} {item['title']}")
        lines.append(f"- [{label}]({item['path']})")
    lines.append("")


def render_index(entries: list[dict]) -> str:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    by_tag: dict[str, list[dict]] = defaultdict(list)

    for item in entries:
        if item["categories"]:
            for cat in item["categories"]:
                by_cat[cat].append(item)
        else:
            by_cat["Uncategorized"].append(item)
        if item["tags"]:
            for tag in item["tags"]:
                by_tag[tag].append(item)
        else:
            by_tag["Untagged"].append(item)

    lines = [
        "# TIL Index",
        "",
        "> 이 파일은 GitHub Actions가 `20*/**/*.md`, `AWS_Afterschool/**/*.md`, `Python_Afterschool/**/*.md` Front Matter를 읽어 자동 생성한다.",
        "> 손으로 고치지 않는다.",
        "",
        "## 대분류",
        "",
        "허용 값: " + ", ".join(CATEGORY_ORDER) + ".",
        "순서는 교안 합본 과목 순서(01~14, 특강)이고, 교안 밖 트랙(Linux, AWS)은 뒤에 둔다.",
        "전환일은 해당 대분류에 모두 나타난다. 글이 없는 대분류는 목차에 나타나지 않는다.",
        "",
        "| category | 교안 폴더 | 교안 과목 | 글 수 |",
        "|---|---|---|---|",
    ]
    for name, folder, subject in CATEGORIES:
        count = len({i["path"] for i in by_cat.get(name, [])})
        lines.append(f"| {name} | {folder} | {subject} | {count} |")
    lines.append("")

    cat_keys = [c for c in CATEGORY_ORDER if c in by_cat]
    extra_cats = sorted(k for k in by_cat if k not in CATEGORY_ORDER and k != "Uncategorized")
    if "Uncategorized" in by_cat:
        extra_cats.append("Uncategorized")
    for cat in cat_keys + extra_cats:
        _render_group(lines, cat, by_cat[cat], level="###")

    lines += [
        "## 태그",
        "",
    ]
    tag_keys = sorted(k for k in by_tag if k != "Untagged")
    if "Untagged" in by_tag:
        tag_keys.append("Untagged")
    for tag in tag_keys:
        _render_group(lines, tag, by_tag[tag], level="###")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    entries, warnings = collect_entries()
    INDEX_PATH.write_text(render_index(entries), encoding="utf-8")
    print(f"wrote {INDEX_PATH.relative_to(ROOT)} ({len(entries)} entries)")
    for line in warnings:
        # GitHub Actions 로그에 경고 주석으로 보이게 한다. 빌드는 실패시키지 않는다.
        prefix = "::warning::" if os.environ.get("GITHUB_ACTIONS") == "true" else "warning: "
        print(f"{prefix}{line}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
