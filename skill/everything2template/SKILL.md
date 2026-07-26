---
name: everything2template
version: 0.4.0
description: >-
  Rewrites webpages, PDFs, docs, code, and projects into traffic-ready WeChat /
  Xiaohongshu / Zhihu / Weibo / Douyin articles that stay fact-faithful with hooks
  and platform-native structure. Markdown/HTML/PDF export, humanize, compliance,
  optional LLM polish. Activated by /e2t, /e2t_wechat, /e2t_xhs, /e2t_zhihu,
  /e2t_export. Use for 爆款改写, 一稿多发, 去AI味, 公众号小红书知乎.
---

# Everything2template / 万物转模板

Agent-native pipeline: **Ingest → CIR → Adapt → Validate → Export**.

Works with any agent that can follow this skill. Prefer the `e2t` CLI for deterministic ingest/export; the agent owns high-quality platform rewriting.

**Root**: this skill directory (`skill/everything2template/`) plus package `e2t` under `src/`.

---

## Quick Start

```
Task Progress:
- [ ] Parse slash command + source (url|file|dir|paste)
- [ ] e2t ingest → CIR JSON + brief.md
- [ ] Load platform template(s); write platform-native article(s)
- [ ] e2t validate each draft
- [ ] Export Markdown (+ PDF if requested)
- [ ] Report paths + 3 title options + risks
```

### Activation

| Command | Behavior |
|---------|----------|
| `/e2t` | Full run: default five platforms |
| `/e2t_wechat` | WeChat official-account article only |
| `/e2t_xhs` | Xiaohongshu note only |
| `/e2t_zhihu` | Zhihu article/answer only |
| `/e2t_export` | Export existing draft(s) to MD/PDF/HTML |

```text
/e2t https://example.com/blog/post
/e2t_wechat ./paper.pdf
/e2t_xhs D:/code/my-project
/e2t_zhihu 粘贴长文…
/e2t_export path=content/runs/<id>/wechat/draft.md format=both
```

Strip the slash command; remaining text is the source or options.

If the user asks to convert content **without** a slash command but clearly wants platform templates, suggest `/e2t` or apply this skill when already mid-pipeline.

---

## Non-negotiables

1. **No invented facts** — metrics, quotes, affiliations, and results must come from the source/CIR. Otherwise label `待核实` or omit.
2. **Publish-quality rewrite, not skeleton** — rebuild with hooks, conflict, concrete steps, platform CTA. Never ship thin outlines to customers.
3. **Platform-native voice** — do not paste the same essay into three skins.
4. **Validate before delivery** — run quality gates; fix errors; warn on AI-flavor phrases.
5. **Always offer exports** — at least Markdown; PDF/HTML when asked.

When CLI/web runs, it uses `e2t.rewrite` (rules) and optional LLM polish (`E2T_LLM_API_KEY` / `OPENAI_API_KEY`). Agent should still improve drafts further when chatting.
---

## Module A — Ingest

Detect source kind: `url | pdf | docx | markdown | text | code | project`.

```bash
python -m e2t ingest "<source>" -o content/runs/<id>/cir.json
# or
e2t ingest "<source>"
```

Read `brief.md` / CIR. If CIR is thin (scanned PDF, empty page), tell the user and stop or ask for another source.

Refine CIR lightly when needed: better title, audience, 5–9 key points, risks. Save updates back to `cir.json`.

---

## Module B — Adapt

For each target platform, read the template:

- [templates/wechat.md](templates/wechat.md)
- [templates/xiaohongshu.md](templates/xiaohongshu.md)
- [templates/zhihu.md](templates/zhihu.md)
- [templates/weibo.md](templates/weibo.md)
- [templates/douyin.md](templates/douyin.md)

Optional CLI scaffold (skeleton only — **you** must rewrite for publish quality):

```bash
e2t adapt content/runs/<id>/cir.json -p wechat
e2t run "<source>" --platforms wechat,xiaohongshu,zhihu,weibo,douyin
e2t humanize path/to/draft.md --in-place
```

After drafting, run humanize + compliance (CLI does this in `e2t run` by default).

| Mode | When |
|------|------|
| `rewrite` (default) | Rebuild for platform virality / native structure |
| `format` | Keep argument order; only adjust length, headings, CTA, density |

Also produce: **3 titles**, metadata (tags/cover/CTA), short **risks** list.

Style depth: [references/platforms.md](references/platforms.md).  
Converter depth: [references/converter-depth.md](references/converter-depth.md).  
Quality bar: [references/quality-checklist.md](references/quality-checklist.md).

Optional enrich:

```bash
e2t research "你的选题关键词"
e2t run "<source>" --research
e2t batch examples/sample_inputs/batch_list.txt
e2t titles "主题" -p xiaohongshu
```

---

## Module C — Validate

```bash
e2t validate -p wechat content/runs/<id>/wechat/draft.md
```

Fix all `errors`. Treat `warnings` seriously (AI套话, length, missing CTA).

---

## Module D — Export

```bash
e2t export content/runs/<id>/wechat/draft.md -f all
```

Deliver paths for `.md`, `.pdf`, and `.wechat.html`. If PDF fails (missing CJK font), still deliver Markdown/HTML and explain the font requirement.

---

## Output layout

```text
content/runs/<cir_id>/
  cir.json
  brief.md
  wechat/draft.md
  xiaohongshu/draft.md
  zhihu/draft.md
  */export/draft.md
  */export/draft.pdf
```

---

## Commercial boundary (agent)

- Free skill path: 3 platforms + MD/PDF + CIR pipeline + built-in voices (`tech_builder`, `knowledge_operator`).
- Do not claim auto-publishing to WeChat/XHS/Zhihu APIs unless the user has a separate publisher integration.
- Do not scrape paywalled content the user cannot access.

Voice profiles:

```bash
e2t voices
e2t run "<source>" --voice tech_builder
```

See [examples.md](examples.md) for end-to-end demos.
