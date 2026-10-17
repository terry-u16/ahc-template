# AHC063～AHC072 変換検証

検証日: 2026-10-17。対象は各コンテストの `tasks/ahcNNN_a?lang=ja` の公式生HTML。

合成HTMLの回帰テスト8件と、公式HTML10件を照合するテスト1件が成功。本文中のテキスト片の順序、全コードブロック（空白込み）、リンク・画像URL、埋め込みSVGの原文一致を確認した。解答プログラムの実行・得点評価は行っていない。

主な修正は、日本語範囲の構造的な抽出、コード空白の保持、番号付きリストの入れ子、表示数式、引用、SVG別ファイル出力。保存済みHTML向けのKaTeX・追加属性・Copyボタン処理は合成HTMLで検証した。

| 問題 | HTMLのSHA-256（UTF-8・改行LF） |
|---|---|
| [AHC063](https://atcoder.jp/contests/ahc063/tasks/ahc063_a?lang=ja) | `d54f778e11dcc7e1e1c8e66b1b68951ae12047622e39945015dd87342be07d2f` |
| [AHC064](https://atcoder.jp/contests/ahc064/tasks/ahc064_a?lang=ja) | `31fbd4d66a825d7678b8ba08d9a63cd05ca00f82919c2ca5afdde184047904ec` |
| [AHC065](https://atcoder.jp/contests/ahc065/tasks/ahc065_a?lang=ja) | `e23fbe7724ecaa0580a07364b16a288fa466945bcf2c6143c2d7ab95afa4b640` |
| [AHC066](https://atcoder.jp/contests/ahc066/tasks/ahc066_a?lang=ja) | `939d8f48786062671893679f0645bd0a323a22cc21525542298ae2402fa5f432` |
| [AHC067](https://atcoder.jp/contests/ahc067/tasks/ahc067_a?lang=ja) | `48bc68ed46f6e6526b12c1586d1055ee47b228b5bfbf60ee68e2cb20555c7813` |
| [AHC068](https://atcoder.jp/contests/ahc068/tasks/ahc068_a?lang=ja) | `9ed6fdacdb1c82e91580a5fd54c208d28f8d25e1c8640ce3351beef311cd0333` |
| [AHC069](https://atcoder.jp/contests/ahc069/tasks/ahc069_a?lang=ja) | `1be8864072cce0cc4f5542999a5b6e56173dd08ff6507d212fd44715ad9904c7` |
| [AHC070](https://atcoder.jp/contests/ahc070/tasks/ahc070_a?lang=ja) | `bb573e32b8ede77b1d9ad983ade095e5636ed1f2d4563994797149dcc57e3aaa` |
| [AHC071](https://atcoder.jp/contests/ahc071/tasks/ahc071_a?lang=ja) | `9cddfbca92231a4702ce3b7132bdb6faa2e56781454313d676af4369c975f77e` |
| [AHC072](https://atcoder.jp/contests/ahc072/tasks/ahc072_a?lang=ja) | `e444240114e93dc745d0895017e0118a16bdf01a64460fe8b7c4936833464f63` |

AHC070のSVGは別ファイルとして保存する。SVG自体は原文と完全一致を確認したが、各Markdownビューアでの見た目は未検証。ブラウザ保存時にローカル化された画像や、この10回分に存在しない表などは個別確認が必要。

HTMLと生成Markdownは一時ディレクトリで検証し、リポジトリには追加していない。再検証手順はSKILL.mdを参照。
