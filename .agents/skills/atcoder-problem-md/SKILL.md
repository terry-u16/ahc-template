---
name: atcoder-problem-md
description: Convert downloaded AtCoder problem statement HTML pages into faithful Japanese Markdown. Use when Codex is asked to create or refresh problem.md from problem.html, strip AtCoder page chrome, keep only the Japanese task statement, preserve math/code/lists/links/images, and avoid summarizing or translating.
---

# AtCoder Problem Markdown

## Workflow

1. Read the local `problem.html` or the user-specified AtCoder task HTML file.
2. Extract only the Japanese statement under `#task-statement span.lang-ja`.
3. Preserve the original content as much as Markdown allows:
   - keep section headings, paragraphs, lists, nested lists, preformatted input/output blocks, links, and images;
   - convert `<var>...</var>` math to `$...$`;
   - convert `<code>...</code>` to inline code;
   - convert AtCoder labels such as WA/TLE to plain text;
   - do not summarize, translate, reorder, or add solver commentary.
4. Include the task title and time/memory limit when present in the page.
5. Write the result to `problem.md` unless the user specifies another destination.
6. Review the output against the source HTML range before finishing, especially around nested lists, examples, and tool links.

## Script

Use the bundled script for the standard AtCoder HTML layout:

```bash
uv run python .agents/skills/atcoder-problem-md/scripts/extract_atcoder_problem_md.py problem.html problem.md
```

If `uv run python` is unavailable, use any available Python 3 runner. The script has no third-party dependencies.

After running it, inspect the generated Markdown rather than assuming the conversion is perfect. If the source has unusual tables, figures, or statement-specific formatting, patch the Markdown manually while preserving the Japanese text.

## Validation

Check that:

- `problem.md` contains no English statement sections such as `Problem Statement`, `Input Generation`, or `Scoring`;
- page UI text, submit forms, navigation, language selectors, and login menus are absent;
- Japanese sections from the source are present;
- code blocks and operation formats remain readable;
- formulas are still visible in Markdown math form.
