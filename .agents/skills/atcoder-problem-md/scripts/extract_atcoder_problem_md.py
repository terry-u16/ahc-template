#!/usr/bin/env python3
"""AtCoderの日本語本文を、コード・公式指示を保持してMarkdown化する。"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)
    start: int = 0
    raw: str = ''

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get('class', '').split()


class Document(HTMLParser):
    """属性順序や保存時の追加属性に依存せず、要素の終端で範囲を決める。"""
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.root = Node('document')
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict((key, value or '') for key, value in attrs))
        line, column = self.getpos()
        node.start = self.offsets[line - 1] + column
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                line, column = self.getpos()
                end = self.source.find('>', self.offsets[line - 1] + column) + 1
                self.stack[index].raw = self.source[self.stack[index].start:end]
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def plain(node: Node | str) -> str:
    if isinstance(node, str):
        return node
    if node.tag in {'script', 'style', 'button'}:
        return ''
    if node.has_class('katex') or node.has_class('katex-display'):
        value = next((plain(n) for n in node.walk() if n.tag == 'annotation'
                      and n.attrs.get('encoding') == 'application/x-tex'), None)
        if value is None:
            raise ValueError('KaTeXの元TeX annotationがありません')
        return value
    if node.tag == 'br':
        return '\n'
    return ''.join(plain(child) for child in node.children)


def compact(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def delimiter(text: str, minimum: int) -> str:
    return '`' * max(minimum, max((len(m[0]) + 1 for m in re.finditer(r'`+', text)), default=0))


class MarkdownConverter:
    def __init__(self, base_url: str = '', assets: dict[str, str] | None = None, asset_dir: str = 'problem.assets'):
        self.base_url = base_url
        self.assets = assets
        self.asset_dir = asset_dir

    def children(self, node: Node) -> str:
        return ''.join(self.render(child) for child in node.children)

    def render(self, node: Node | str) -> str:
        if isinstance(node, str):
            text = re.sub(r'\s+', ' ', node)
            text = re.sub(r'\\\[(.*?)\\\]', lambda m: '\n\n$$\n' + m[1].strip() + '\n$$\n\n', text)
            return re.sub(r'\\\((.*?)\\\)', lambda m: '$' + m[1].strip() + '$', text)
        tag = node.tag
        if tag in {'script', 'style', 'button'}:
            return ''
        if tag == 'svg':
            if self.assets is None:
                return '\n\n' + node.raw + '\n\n'
            name = f'figure-{len(self.assets) + 1}.svg'
            self.assets[name] = node.raw
            return f'\n\n![](<{self.asset_dir}/{name}>)\n\n'
        if tag == 'pre':
            value = plain(node)
            marker = delimiter(value, 3)
            return '\n\n' + marker + 'text\n' + value + ('' if value.endswith('\n') else '\n') + marker + '\n\n'
        if tag == 'var' or node.has_class('katex') or node.has_class('katex-display'):
            value = compact(plain(node))
            if node.has_class('katex-display'):
                return '\n\n$$\n' + value + '\n$$\n\n'
            return '$' + value + '$'
        if tag == 'code':
            value = plain(node)
            marker = delimiter(value, 1)
            pad = ' ' if value.startswith(('`', ' ')) or value.endswith(('`', ' ')) else ''
            return marker + pad + value + pad + marker
        if tag in {'ul', 'ol'}:
            items = []
            number = int(node.attrs.get('start', '1'))
            for child in node.children:
                if not isinstance(child, Node) or child.tag != 'li':
                    continue
                if tag == 'ol':
                    number = int(child.attrs.get('value', str(number)))
                marker = f'{number}. ' if tag == 'ol' else '- '
                lines = self.children(child).strip().split('\n')
                items.append(marker + lines[0] + ''.join('\n' + (' ' * len(marker) + line if line else '') for line in lines[1:]))
                number += 1
            return '\n\n' + '\n\n'.join(items) + '\n\n'
        if tag == 'img':
            src = node.attrs.get('src', '')
            alt = node.attrs.get('alt', '').replace('[', r'\[').replace(']', r'\]')
            return f'![{alt}](<{urljoin(self.base_url, src)}>)' if src else ''
        body = self.children(node)
        if tag == 'a':
            href = node.attrs.get('href')
            return f'[{body.strip()}](<{urljoin(self.base_url, href)}>)' if href else body
        if tag in {'strong', 'b', 'em', 'i'}:
            marker = '**' if tag in {'strong', 'b'} else '*'
            return (' ' if body[:1].isspace() else '') + marker + body.strip() + marker + (' ' if body[-1:].isspace() else '')
        if re.fullmatch(r'h[1-6]', tag):
            return '\n\n' + '#' * max(2, int(tag[1]) - 1) + ' ' + body.strip() + '\n\n'
        if tag == 'blockquote':
            return '\n\n' + '\n'.join('> ' + line for line in body.strip().split('\n')) + '\n\n'
        if tag == 'br':
            return '  \n'
        if tag == 'hr':
            return '\n\n---\n\n'
        if tag in {'p', 'div', 'section', 'details', 'summary'}:
            return '\n\n' + body.strip() + '\n\n'
        return body


def japanese_statement(root: Node) -> Node:
    task = next((n for n in root.walk() if n.attrs.get('id') == 'task-statement'), None)
    if task is None:
        raise ValueError('#task-statement が見つかりません')
    statement = next((n for n in task.walk() if n.tag == 'span' and n.has_class('lang-ja')), None)
    if statement is None:
        raise ValueError('#task-statement span.lang-ja が見つかりません')
    return statement


def convert(source: str, base_url: str = '', *, assets: dict[str, str] | None = None, asset_dir: str = 'problem.assets') -> str:
    root = Document(source).root
    statement = japanese_statement(root)
    if not base_url:
        base_url = next((n.attrs.get('href', '') for n in root.walk() if n.tag == 'link' and n.attrs.get('rel') == 'canonical'), '')
    if not base_url:
        base_url = next((n.attrs.get('content', '') for n in root.walk() if n.tag == 'meta' and n.attrs.get('property') == 'og:url'), '')
    parts = []
    title = next((compact(plain(n)) for n in root.walk() if n.tag == 'title'), '')
    if title:
        parts.append('# ' + title)
    limits = next((compact(plain(n)) for n in root.walk() if n.tag == 'p' and '実行時間制限' in plain(n) and 'メモリ制限' in plain(n)), '')
    if limits:
        parts.append(limits)
    body = MarkdownConverter(base_url, assets, asset_dir).children(statement).strip()
    # コード内の空白には触れず、ブロック境界の空行だけを正規化する。
    chunks = re.split(r'(^[ \t]*(`{3,})text\n.*?^[ \t]*\2[ \t]*$)', body, flags=re.M | re.S)
    # splitのキャプチャにはフェンス文字列も入る。
    normalized = []
    for i in range(0, len(chunks), 3):
        normalized.append(re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', chunks[i]))
        if i + 1 < len(chunks):
            normalized.append(chunks[i + 1])
    parts.append(''.join(normalized))
    return '\n\n'.join(parts) + '\n'


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit('usage: extract_atcoder_problem_md.py <problem.html> <problem.md>')
    src, dst = map(Path, sys.argv[1:])
    assets: dict[str, str] = {}
    asset_dir = dst.with_suffix('.assets')
    try:
        result = convert(src.read_text(encoding='utf-8'), assets=assets, asset_dir=asset_dir.name)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    if assets:
        asset_dir.mkdir(parents=True, exist_ok=True)
        for name, content in assets.items():
            (asset_dir / name).write_text(content, encoding='utf-8')
    dst.write_text(result, encoding='utf-8')


if __name__ == '__main__':
    main()
