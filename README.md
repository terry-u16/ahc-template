# {{project-name}}

共通ライブラリは `src/library/` に配置し、`src/library.rs` で各モジュールを公開しています。
`src/main.rs` などからは `crate::library::grid::Map2d` のように参照してください。

- `annealing.rs`: 焼きなまし
- `beam.rs`・`beam/`: ビームサーチ
- `diagnostics.rs`: 診断・計測
- `graph.rs`: グラフ
- `grid.rs`: 2次元グリッド
- `random.rs`: 乱数
- `util.rs`: 共通処理

`neighbors!` マクロは `#[macro_export]` によりクレート直下に公開されるため、`crate::neighbors!` で呼び出します。
