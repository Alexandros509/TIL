#!/usr/bin/env python3
"""마크다운의 로컬 이미지 경로를 실제 파일 위치로 맞춘다.

파일명으로 저장소 안 이미지를 찾고, 그 md 기준 상대경로로 다시 쓴다.
http(s) 링크, README.md / TIL.md / TIL_INDEX.md 는 건드리지 않는다.
"""

from __future__ import annotations

import os
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_MD_NAMES = {"README.md", "TIL.md", "TIL_INDEX.md"}
SKIP_DIRS = {".git", ".github", ".venv", "node_modules"}
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
IMAGE_PATTERN = re.compile(r"!\[(.*?)\]\((.*?)\)")


def build_image_dictionary(repo_root: Path) -> dict[str, Path]:
    image_dict: dict[str, Path] = {}
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.parts):
            continue
        if path.suffix.lower() not in VALID_EXTENSIONS:
            continue
        name = path.name
        if name in image_dict:
            print(f"[경고] 같은 파일명: {name}")
            print(f"  - 유지: {image_dict[name].relative_to(repo_root)}")
            print(f"  - 무시: {path.relative_to(repo_root)}")
            continue
        image_dict[name] = path
    return image_dict


def update_markdown_files(repo_root: Path, image_dict: dict[str, Path]) -> list[Path]:
    changed: list[Path] = []
    for path in repo_root.rglob("*.md"):
        if path.name in SKIP_MD_NAMES:
            continue
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8")

        def replacer(match: re.Match[str]) -> str:
            alt_text = match.group(1)
            old_url = match.group(2).strip()
            if old_url.startswith(("http://", "https://", "data:")):
                return match.group(0)
            old_filename = urllib.parse.unquote(os.path.basename(old_url))
            actual = image_dict.get(old_filename)
            if actual is None:
                return match.group(0)
            relative = os.path.relpath(actual, start=path.parent)
            relative = relative.replace("\\", "/")
            encoded = urllib.parse.quote(relative, safe="/")
            return f"![{alt_text}]({encoded})"

        updated = IMAGE_PATTERN.sub(replacer, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path)
            print(f"[완료] {path.relative_to(repo_root)}")
    return changed


def main() -> int:
    print("=== 이미지 링크 업데이트 ===")
    image_dict = build_image_dictionary(ROOT)
    print(f"이미지 {len(image_dict)}개")
    changed = update_markdown_files(ROOT, image_dict)
    print(f"수정한 md {len(changed)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
