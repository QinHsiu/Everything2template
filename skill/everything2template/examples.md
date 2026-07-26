# Examples

## 1) URL → three platforms

```text
/e2t https://example.com/how-to-build-a-second-brain
```

Agent:

1. `e2t ingest <url>`
2. Rewrite with `templates/*.md`
3. Validate + export

## 2) Project → Xiaohongshu

```text
/e2t_xhs ./
```

Or point at any project directory relative to your workspace, e.g. `/e2t_xhs ./my-app`.

Expected: checklist note on what the repo does, 3–6 image plan, tags like `#AI工具 #效率 #创作者`.

## 3) PDF → WeChat

```text
/e2t_wechat ./whitepaper.pdf
```

If PDF is scanned/empty: stop and ask for OCR text or another file.

## 4) Export only

```text
/e2t_export path=content/runs/abc123/zhihu/draft.md format=both
```

## Sample local demo (no network)

```bash
e2t run examples/sample_inputs/demo_article.md --platforms wechat,xiaohongshu,zhihu
```
