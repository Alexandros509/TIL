#!/usr/bin/env python3
"""TIL/*.md Front Matter를 읽어 루트 TIL_INDEX.md를 다시 쓴다.

목차 구조
1. 대분류(category)
2. 태그(tags)

전환일은 category 리스트라 두 대분류 섹션에 같은 글이 들어간다.
date가 없으면 파일명 YYYYMMDD를 쓴다.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
# 연/월 폴더에 있는 TIL만 읽는다. 루트 README.md, TIL.md(프롬프트)는 제외.
TIL_GLOBS = ("20*/**/*.md",)
SKIP_NAMES = {"README.md", "TIL.md", "TIL_INDEX.md"}
INDEX_PATH = ROOT / "TIL_INDEX.md"
FILENAME_DATE = re.compile(r"^(\d{8})")

CATEGORY_ORDER = ["Git", "Python", "AI Literacy", "Machine Learning"]


def parse_front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    raw = parts[1]
    try:
        import yaml

        data = yaml.safe_load(raw) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
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
        meta = parse_front_matter(text)
        tags = normalize_list(meta.get("tags"))
        categories = normalize_list(meta.get("category"))
        title = str(meta.get("title") or "").strip() or path.stem
        sort_date = parse_date(meta.get("date")) or date_from_filename(path.name)
        if sort_date is None:
            warnings.append(f"날짜 없음, 건너뜀: {path.name}")
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
    lines.append(f"{level} {heading}")
    items = sorted(items, key=lambda x: (x["date"], x["title"]), reverse=True)
    seen = set()
    for item in items:
        key = (item["path"], item["title"], item["date"])
        if key in seen:
            continue
        seen.add(key)
        label = f"{item['date'].isoformat()} {item['title']}"
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
        "> 이 파일은 GitHub Actions가 `TIL/*.md`의 Front Matter를 읽어 자동 생성한다.",
        "> 손으로 고치지 않는다.",
        "",
        "## 대분류",
        "",
        "허용 값: Git, Python, AI Literacy, Machine Learning.",
        "전환일은 해당 대분류에 모두 나타난다.",
        "",
    ]

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
    print(f"wrote {INDEX_PATH.relative_to(ROOT)}")
    for line in warnings:
        print(f"warning: {line}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
