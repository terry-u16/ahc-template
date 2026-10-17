---
name: atcoder-problem-md
description: Convert downloaded AtCoder problem statement HTML pages into faithful Japanese Markdown. Use when Codex is asked to create or refresh problem.md from problem.html, strip AtCoder page chrome, keep only the Japanese task statement, preserve math/code/lists/links/images, and avoid summarizing or translating.
---

# AtCoder Problem Markdown

## 手順

1. ローカルの `problem.html` または指定されたAtCoder問題HTMLを読む。
2. `#task-statement span.lang-ja` の内部だけを抽出する。属性順序・追加class・style属性に依存せず、要素の閉じタグまでを対象にする。英語版が存在しなくても抽出できる。
3. 原文をMarkdownで可能な限り忠実に保持する。
   - 見出し、段落、引用、順序付き・順序なしリストとその入れ子、リンク、画像を保持する。
   - `<var>` は `$...$`、表示数式の `\[...\]` は `$$` に変換する。描画済みKaTeXは `application/x-tex` annotationから元のTeXを復元する。復元できない場合は停止する。
   - `<pre>` 内の改行、連続空行、インデント、末尾空白、文字列を保持する。HTMLタグの除去と実体参照の1回の復号以外の書き換えをしない。数式のTeXもそのまま残す。
   - `<code>` はインラインコードに、WA/TLEなどのラベルは普通の文字にする。
   - 日本語本文内にある英語の公式必須指示・サンプルコードも原文のまま保持する。`prettyprint` や `div-btn-copy` の内容をまとめて削除しない。Copyボタン、script、styleは除去する。
   - 要約、翻訳、並べ替え、解法の補足をしない。
4. ページの問題タイトルと実行時間・メモリ制限も出力する。
5. 指定がなければ `problem.md` に書き出す。埋め込みSVGがある場合は `problem.assets/figure-1.svg` なども生成する。出力が `foo.md` なら `foo.assets/` となる。Markdownと画像ディレクトリは一緒に扱う。
6. 原文と変換結果を照合し、特にリストの入れ子、数式、サンプルコード、公式指示、図、ツールへのリンクを確認する。

## スクリプト

```bash
uv run --no-project python .agents/skills/atcoder-problem-md/scripts/extract_atcoder_problem_md.py problem.html problem.md
```

標準ライブラリのみを使用する。`--no-project` は未展開のテンプレートの `pyproject.toml` に依存せず実行するために指定する。`uv` が使えない場合に限り、利用可能なPython 3で実行してよい。

相対リンクはページのcanonical URLまたは `og:url` を基準に解決する。ブラウザ保存時の `*_files/` などのローカル画像は公式URLを推測せず、保存画像の存在と出力からの相対位置を確認してコピーするか、原文の情報から参照先を修正する。

表などの未検証の形式が含まれる場合は、出力を原文と照合して修正する。埋め込みSVGは元のSVGを保持するため、確認時にはSVG対応ビューアを使用する。

## 検証

- 英語版の本文とページUI（提出フォーム、ナビゲーション、言語切替、ログインメニュー）が混入していない。
- 日本語範囲の全見出し・本文・公式必須指示が順序どおりに含まれる。英語文字列の有無だけで判定しない。
- コードと入出力形式は原文の空白を保持している。
- 数式がMarkdown数式として残り、KaTeXの表示文字列が重複しない。
- ネストした番号付きリスト、引用、図、リンクが保持されている。

回帰テスト（ネットワーク不要）:

```bash
uv run --no-project python -m unittest discover -s .agents/skills/atcoder-problem-md/scripts -p 'test_*.py' -v
```

AHC063～AHC072の公式HTMLも照合する場合は、各問題ページを `ahc063.html` ～ `ahc072.html` として保存したディレクトリを `AHC_HTML_DIR` に指定する。未指定時は公式HTMLのテストのみskipする。全10ファイルが必要。

```bash
AHC_HTML_DIR=/tmp/ahc-md-check uv run --no-project python -m unittest discover -s .agents/skills/atcoder-problem-md/scripts -p 'test_*.py' -v
```

2026-10-17の検証対象と結果は [references/validation.md](references/validation.md) を参照。
