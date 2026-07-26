# Competitive analysis (2026-07) — open-source strongest track

## Category map

| Competitor | Type | Strength | Gap vs Everything2template |
|------------|------|----------|----------------------------|
| 侯斯特内容转换 | SaaS paste→rewrite | Fast multi-platform copy | Weak on PDF/code/project ingest; cloud; limited export |
| MCP Content Styles | MCP prompt pack | 12 platforms, Cursor/Claude | Markdown-in only; no CIR; no PDF; thin quality gates |
| oh-my-writing-skill | Agent skill pipeline | Deep converters + humanizer | Research→write focus; weaker everything-ingest + export pack |
| AIWriteX / 简媒 / ALQQ | Matrix ops suites | Hot topics, publish automation | Heavy; account risk; not agent-skill portable |
| Single skills (wechat-article etc.) | Agent skill | Deep one-platform craft | No multi-platform + no everything-ingest |
| 壹伴等编辑器 | In-editor layout | WeChat typesetting | Not multi-source rewrite |

## Wedge (OSS lead)

1. **Everything ingest** — URL / PDF / DOCX / MD / code / project → CIR  
2. **Agent-native** — `SKILL.md` + CLI + MCP lite + trial web  
3. **Platform rebuild** — 5 templates + rewrite engine + validate (anti-filler / anti-truncation)  
4. **Delivery** — Markdown + WeChat HTML + CJK PDF  
5. **Measurable quality** — `scripts/strongest_score.py` (avg validate ≥85, no spam, parity ≥0.85)

## Open-source strongest checklist

- [x] End-to-end CLI: ingest → rewrite → validate → export  
- [x] 5 platforms + humanize + compliance + WeChat HTML + MCP  
- [x] Rewrite engine without template spam / truncated H1  
- [x] `strongest_score` gate  
- [ ] Beat prompt-packs on **more platforms** only if quality holds (prefer depth > 12 shallow skins)  
- [ ] Public before/after gallery continuously refreshed  
- [ ] Optional LLM polish docs for DeepSeek / Ollama  

**Verdict:** compete on **publishable draft quality + ingest breadth**, not on auto-login matrix suites.
