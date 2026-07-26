# Support

## Channels

1. **微信公众号 Tecience** — 付费 / Pro 交付 / 安装协助（回复 `E2T` 或 `已付`）  
2. **GitHub Issues** — bugs, feature requests, Pro waitlist  
   https://github.com/QinHsiu/Everything2template/issues
3. **Discussions** (when enabled) — usage questions, template sharing
4. **Security** — email maintainer privately; do not file public issues for secrets

## Response targets (best-effort for open core)

| Severity | Target |
|----------|--------|
| Install / crash blocker | 72h |
| Template quality bug | 1 week |
| Pro / Tecience 付款确认 | 24h |
| Pro waitlist ack | 48h |

## Before you ask

```bash
python -m e2t version
python -m pytest -q
python scripts/closed_loop_verify.py
```

Attach OS, Python version, and the `content/runs/<id>/` path when possible.
