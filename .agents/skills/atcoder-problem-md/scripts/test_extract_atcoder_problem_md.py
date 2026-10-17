"""合成HTMLの回帰テストと、任意指定した公式HTML 10回分の照合。"""
import html
import os
from pathlib import Path
import re
import unittest

from extract_atcoder_problem_md import convert


def page(body, english=True):
    return ('<title>A - Test</title><span class="lang-ja">OUTSIDE</span>'
            '<p>実行時間制限: 2 sec / メモリ制限: 1024 MiB</p>'
            '<div id="task-statement"><span class="lang">'
            '<span style="display:inline" class="extra lang-ja">' + body + '</span>'
            + ('<span class="lang-en">ENGLISH_SENTINEL</span>' if english else '')
            + '</span></div><p>FOOTER_SENTINEL</p>')


class RegressionTests(unittest.TestCase):
    def test_scope_and_attributes(self):
        for english in (True, False):
            result = convert(page('<p>本文<span>内部</span>続き</p>', english))
            self.assertIn('本文内部続き', result)
            for token in ('OUTSIDE', 'ENGLISH_SENTINEL', 'FOOTER_SENTINEL'):
                self.assertNotIn(token, result)

    def test_missing_statement(self):
        for source in ('<span class="lang-ja">x</span>', '<div id="task-statement">x</div>'):
            with self.assertRaises(ValueError):
                convert(source)

    def test_pre_whitespace_entities_and_fences(self):
        code = '\nif a < b:\n    print("&lt;", "$x$")  \n\n\n# ```\n'
        result = convert(page('<pre>' + html.escape(code) + '</pre>'))
        self.assertIn('````text\n' + code + '````', result)

    def test_inline_spaces_and_code(self):
        result = convert(page('<p><var>N</var> <var>M</var> <code>`x`</code></p>'))
        self.assertIn('$N$ $M$ `` `x` ``', result)

    def test_numbered_nested_list_and_paragraph(self):
        result = convert(page('<ol><li><p>一</p><p>続き</p><ol><li>内側</li></ol></li><li>二</li></ol>'))
        self.assertIn('1. 一\n\n   続き', result)
        self.assertIn('   1. 内側', result)
        self.assertIn('\n\n2. 二', result)

    def test_math_and_katex(self):
        katex = '<span class="katex"><math><annotation encoding="application/x-tex">x &lt; y</annotation></math><span>xVISIBLE_DUPLICATEy</span></span>'
        result = convert(page('<p>\\[ a+b \\]</p><var>' + katex + '</var><pre>' + katex + '</pre>'))
        self.assertIn('$$\na+b\n$$', result)
        self.assertIn('$x < y$', result)
        self.assertIn('```text\nx < y\n```', result)
        self.assertNotIn('VISIBLE_DUPLICATE', result)
        with self.assertRaises(ValueError):
            convert(page('<span class="katex">no annotation</span>'))

    def test_instructions_are_not_ui(self):
        instruction = '\nEnglish official instructions.\n\n\nKeep every line.\n'
        result = convert(page('<div class="div-btn-copy"><button>Copy</button><pre class="prettyprint">' + instruction + '</pre></div>'))
        self.assertIn('```text\n' + instruction + '```', result)
        self.assertNotIn('Copy', result)

    def test_links_images_quote_and_svg(self):
        svg = '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M0 0L10 10"/></svg>'
        assets = {}
        result = convert(page('<blockquote><p>引用</p></blockquote><a href="/tools">道具</a><img src="//img.atcoder.jp/a.png" alt="図">' + svg), 'https://atcoder.jp/tasks/a', assets=assets, asset_dir='out.assets')
        self.assertIn('> 引用', result)
        self.assertIn('https://atcoder.jp/tools', result)
        self.assertIn('https://img.atcoder.jp/a.png', result)
        self.assertIn('![](<out.assets/figure-1.svg>)', result)
        self.assertEqual(assets, {'figure-1.svg': svg})


@unittest.skipUnless(os.environ.get('AHC_HTML_DIR'), 'AHC_HTML_DIR未指定（公式HTML照合は省略）')
class OfficialCorpusTests(unittest.TestCase):
    def test_ahc063_through_072(self):
        for number in range(63, 73):
            with self.subTest(contest=number):
                source = (Path(os.environ['AHC_HTML_DIR']) / f'ahc{number:03}.html').read_text()
                # 実装のDOM抽出に依存しない、公式生HTML用の照合範囲。
                fragment = source.split('<span class="lang-ja">', 1)[1].split('<span class="lang-en">', 1)[0]
                assets = {}
                result = convert(source, assets=assets)
                # コードと公式必須指示は、HTMLタグ除去・実体参照復号以外変更しない。
                pres = re.findall(r'<pre\b[^>]*>(.*?)</pre>', fragment, re.S)
                for pre in pres:
                    expected = html.unescape(re.sub(r'<[^>]+>', '', pre))
                    self.assertIn('```text\n' + expected + ('' if expected.endswith('\n') else '\n') + '```', result)
                # 見出し・本文中のテキスト片・数式を元の順で照合。
                content = re.sub(r'<svg\b.*?</svg>', '', fragment, flags=re.S)
                content = re.sub(r'<pre\b.*?</pre>', '', content, flags=re.S)
                position = 0
                flat = re.sub(r'\s+', '', result)
                for piece in re.split(r'<[^>]+>', content):
                    text = re.sub(r'\s+', '', html.unescape(piece))
                    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
                    if text:
                        found = flat.find(text, position)
                        self.assertGreaterEqual(found, 0, text)
                        position = found + len(text)
                for target in re.findall(r'(?:href|src)="([^"]+)"', content):
                    self.assertIn(html.unescape(target), result)
                svg = re.findall(r'<svg\b.*?</svg>', fragment, re.S)
                self.assertEqual(list(assets.values()), svg)
                for ui in ('<span', 'Problem Statement', 'Input Generation', 'ENGLISH_SENTINEL'):
                    self.assertNotIn(ui, result)
                print(f'AHC{number:03}: {len(pres)} code blocks, {len(svg)} SVGs OK')


if __name__ == '__main__':
    unittest.main()
