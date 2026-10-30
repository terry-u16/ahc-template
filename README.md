# {{project-name}}

共通ライブラリは `src/library/` に配置し、`src/library.rs` で各モジュールを公開しています。
`src/main.rs` などからは `crate::library::grid::Map2d` のように参照してください。

- `annealing.rs`: 焼きなまし
- `beam.rs`・`beam/`: ビームサーチ
- `data_structures.rs`・`data_structures/`: 固定容量配列、整数集合、世代管理配列、Link-Cut Treeなど
- `diagnostics.rs`: 診断・計測
- `geometry.rs`・`geometry/`: 整数座標の静的2次元KD-tree・Delaunay分割
- `graph.rs`: グラフ
- `grid.rs`: 2次元グリッド
- `modint.rs`: modintを使った組合せ・順列
- `numerics.rs`: 最大公約数・最小公倍数・素因数分解など
- `random.rs`: 乱数
- `util.rs`: 共通処理

`neighbors!` マクロは `#[macro_export]` によりクレート直下に公開されるため、`crate::neighbors!` で呼び出します。
