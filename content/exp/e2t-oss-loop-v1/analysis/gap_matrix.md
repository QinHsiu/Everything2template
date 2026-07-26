# Competitor gap analysis — 2026-07-26

Sources: local clone `oh-my-writing-skill`; web READMEs for mcp-content-styles / excellent-typesetter / yuntype / multi-platform-publisher / xhs viral skill.

## Feature matrix

| Capability | mcp-content-styles | oh-my-writing | excellent-typesetter | yuntype | E2T before | E2T target |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Multi-platform rewrite | 12 | 3+pipeline | layout focus | WeChat/XHS layout | 3 | ≥5 |
| format/rewrite modes | ✓ | ✓ | — | — | partial | ✓ |
| Everything ingest (PDF/code/project) | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| CIR intermediate | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Humanizer / 去AI味 | ✗ | ✓ deep | --humanize | — | warn only | ✓ rewrite |
| WeChat paste HTML | ✗ | style tips | ✓ strong | ✓ | ✗ | ✓ |
| MD/PDF export | ✗ | md | html | zip/images | ✓ | ✓ |
| MCP server | ✓ | plugin | skill | ✓ | ✗ | ✓ |
| Compliance gate | ✗ | soft | — | — | ✗ | ✓ |
| Auto publish login | ✗ | ✗ | ✗ | ✗ | out | out (defer) |

## Our disadvantages (P0)

1. No deterministic **humanize** pass (oh-my-writing wins)
2. No **WeChat inline HTML** for editor paste (typesetter/yuntype win)
3. Only **3 platforms** vs 12 in mcp-content-styles
4. No **MCP** surface for agent tool calling
5. No **compliance** lexicon gate
6. commercial score ignored **competitive_parity**

## Intentional non-goals

- Cookie login / auto-publish (account ban risk; leave to separate tools)
- Full image-search pipeline (optional later; not core wedge)

## Chosen plan (Top-1 of 10)

**P1 — Commercial parity pack**: humanize + compliance + wechat HTML + weibo/douyin templates + MCP thin server + competitive_parity scorer + wire into run/export/eval.
