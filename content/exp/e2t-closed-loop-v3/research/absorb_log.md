# Competitors / OSS template absorb log (closed-loop v3)

## Sources used

1. **Local clone**: `competitors/oh-my-writing-skill/skills/{wechat,xiaohongshu,zhihu}-converter/SKILL.md`
2. **OpenAlex** (Paper_Rec-style polite API): `content/exp/e2t-closed-loop-v3/research/openalex_hits.json`
3. **Product** templates updated: `skill/everything2template/templates/wechat.md`, `xiaohongshu.md`

## Absorbed patterns

| Source | Pattern | Landed in |
|--------|---------|-----------|
| wechat-converter | 引子式开头、正式深度、排版感 | wechat.md |
| xiaohongshu-converter | 共鸣开头、收藏步骤、Emoji 节制 | xiaohongshu.md |
| OpenAlex | Prompt/链式可控 → 首发文论据 | launch_wechat.md + source_brief.md |

## Not used

- Remote GitHub raw SKILL fetch (policy-blocked in agent; local clone sufficient)
- Cookie-based auto-publish
