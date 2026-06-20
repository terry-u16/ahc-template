#!/usr/bin/env python3
"""Extract the Japanese AtCoder task statement from a downloaded HTML page."""

from __future__ import annotations

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class MarkdownConverter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.out: list[str] = []
        self.heading_level: int | None = None
        self.list_stack: list[str] = []
        self.in_pre = False
        self.in_code = False
        self.link_stack: list[tuple[str, int]] = []
        self.skip_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key: value or "" for key, value in attrs}

        if tag in {"section", "div", "span"}:
            return
        if tag in {"script", "style"}:
            self.skip_stack.append(tag)
            return
        if self.skip_stack:
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = max(1, int(tag[1]) - 1)
            self._blank()
            self.out.append("#" * self.heading_level + " ")
        elif tag == "p":
            self._blank()
        elif tag == "br":
            self.out.append("\n")
        elif tag == "hr":
            self._blank()
        elif tag == "ul":
            self._blank()
            self.list_stack.append("ul")
        elif tag == "ol":
            self._blank()
            self.list_stack.append("ol")
        elif tag == "li":
            self._line_start()
            indent = "  " * max(0, len(self.list_stack) - 1)
            bullet = "1. " if self.list_stack and self.list_stack[-1] == "ol" else "- "
            self.out.append(indent + bullet)
        elif tag == "pre":
            self._blank()
            self.out.append("```text\n")
            self.in_pre = True
        elif tag == "var":
            if not self.in_pre:
                self.out.append("$")
        elif tag == "strong":
            self.out.append("**")
        elif tag == "code":
            if not self.in_pre:
                self.out.append("`")
                self.in_code = True
        elif tag == "a":
            self.out.append("[")
            self.link_stack.append((attrs_dict.get("href", ""), len(self.out)))
        elif tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "") or image_alt(src)
            if src:
                self.out.append(f"![{alt}]({src})")

    def handle_endtag(self, tag: str) -> None:
        if self.skip_stack:
            if self.skip_stack[-1] == tag:
                self.skip_stack.pop()
            return

        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_level = None
            self._blank()
        elif tag == "p":
            self._blank()
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                self.list_stack.pop()
            self._blank()
        elif tag == "li":
            self.out.append("\n")
        elif tag == "pre":
            if self.out and not self.out[-1].endswith("\n"):
                self.out.append("\n")
            self.out.append("```\n")
            self.in_pre = False
            self._blank()
        elif tag == "var":
            if not self.in_pre:
                self.out.append("$")
        elif tag == "strong":
            self.out.append("**")
        elif tag == "code":
            if self.in_code:
                self.out.append("`")
                self.in_code = False
        elif tag == "a":
            href, _ = self.link_stack.pop() if self.link_stack else ("", 0)
            self.out.append(f"]({href})" if href else "]")

    def handle_data(self, data: str) -> None:
        if self.skip_stack:
            return
        text = html.unescape(data)
        if self.in_pre:
            text = strip_var_markup(text)
            self.out.append(text)
            return
        if self.in_code:
            self.out.append(text)
            return
        if not data.strip():
            return
        text = re.sub(r"\s+", " ", text)
        if text:
            self.out.append(text)

    def handle_entityref(self, name: str) -> None:
        self.handle_data(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.handle_data(f"&#{name};")

    def markdown(self) -> str:
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"\$([^$\n]+)\$", lambda m: "$" + normalize_math(m.group(1)) + "$", text)
        return text.strip() + "\n"

    def _blank(self) -> None:
        current = "".join(self.out)
        if not current:
            return
        if current.endswith("\n\n"):
            return
        if current.endswith("\n"):
            self.out.append("\n")
        else:
            self.out.append("\n\n")

    def _line_start(self) -> None:
        current = "".join(self.out)
        if not current or current.endswith("\n"):
            return
        self.out.append("\n")


def image_alt(src: str) -> str:
    if "oni" in src:
        return "鬼"
    if "fuku" in src:
        return "福"
    return ""


def strip_var_markup(text: str) -> str:
    text = re.sub(r"</?var>", "", text)
    return html.unescape(text)


def normalize_math(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text.strip())
    return text


def extract_title(source: str) -> str | None:
    match = re.search(r"<title>\s*(.*?)\s*</title>", source, flags=re.I | re.S)
    if not match:
        return None
    title = html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())
    return title or None


def extract_limits(source: str) -> str | None:
    match = re.search(
        r"実行時間制限\s*:\s*.*?メモリ制限\s*:\s*[^<\n]+",
        html.unescape(source),
        flags=re.S,
    )
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(0)).strip()


def extract_lang_ja(source: str) -> str:
    start = source.find('<span class="lang-ja">')
    if start == -1:
        raise SystemExit("span.lang-ja が見つかりません")
    start = source.find(">", start) + 1
    end = source.find('<span class="lang-en">', start)
    if end == -1:
        raise SystemExit("span.lang-en が見つからず、日本語範囲の終端を特定できません")
    fragment = source[start:end]
    return re.sub(r"</span>\s*$", "", fragment.strip())


def convert(source: str) -> str:
    parts: list[str] = []
    title = extract_title(source)
    if title:
        parts.append(f"# {title}")
    limits = extract_limits(source)
    if limits:
        parts.append(limits)

    parser = MarkdownConverter()
    parser.feed(extract_lang_ja(source))
    parts.append(parser.markdown().strip())
    return "\n\n".join(part for part in parts if part).strip() + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_atcoder_problem_md.py <problem.html> <problem.md>")
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    dst.write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
