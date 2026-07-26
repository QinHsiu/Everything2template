# Experiment: e2t-profit-loop-v2

Successor to e2t-oss-loop-v1. v1 only proved **engineering parity**.  
v2 stops only when **profit-ready** (sellable skill product) OR plans are exhausted.

## target_score (profit_ready)

```yaml
task: e2t_profit_ready
threshold:
  commercializable: true              # v1 gate
  competitive_parity: >= 0.85
  tests_pass: true
  profit_ready_score: >= 0.90         # scripts/profit_ready.py
  required_assets:
    - Gumroad/Lemon-ready release zip (Hobby + Pro packs)
    - Sales page with explicit price & value math
    - Case study before/after (multi-platform)
    - Claude Code plugin manifest
    - Research enrichment (optional DDGS / URL notes)
    - Image plan + optional image fetch
    - One-command install for buyers
    - Batch convert CLI
stop_when:
  - profit_ready_score >= 0.90 AND release zip builds, OR
  - no remaining positive-EV plan (document exhaustion)
```

## Why v1 was NOT enough for monetization

- No priced offer / checkout packaging
- Weaker than oh-my on research + images + plugin UX
- Skeletons only — buyers need case-study proof
- No Pro SKU differentiation
