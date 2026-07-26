# Quality checklist (pre-delivery)

## Universal

- [ ] No invented metrics / quotes / affiliations
- [ ] Uncertain claims marked `待核实` or removed
- [ ] AI-flavor phrases purged（综上所述 / 赋能 / delve into …）
- [ ] 3 alternative titles provided
- [ ] Export paths reported (md, and pdf if requested)

## WeChat

- [ ] Title ≤30 chars; abstract ≤54
- [ ] Hook in first screen
- [ ] H2 sections; short paragraphs
- [ ] End CTA present
- [ ] Image placeholders every ~300–500 chars (optional but preferred)

## Xiaohongshu

- [ ] Title ≤20 chars, keyword-first
- [ ] Conclusion up front
- [ ] Numbered points; short lines
- [ ] 3–6 #tags
- [ ] Cover + inner image plan listed

## Zhihu

- [ ] Conclusion in opening
- [ ] Evidence vs opinion separated
- [ ] Boundary /反例 section present when claims are strong
- [ ] Discussion invite (not hard sell)

## Validate CLI

```bash
e2t validate -p wechat path/to/draft.md
e2t validate -p xiaohongshu path/to/draft.md
e2t validate -p zhihu path/to/draft.md
```

Ship only when `ok=true` or user explicitly accepts remaining warnings.
