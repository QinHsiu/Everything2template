# e2t-closed-loop-v3 — Tecience 商业化闭环

目标：产品侧完成「试用 → Tecience 关注 → 关键词 → 付费 → Pro 交付」可验证闭环。

## 命令

```bash
python scripts/closed_loop_verify.py
python -m e2t llm-info
python -m e2t web --port 8767
```

## 产物

- `docs/tecience_funnel.md` / `docs/pay_tecience.md` / `docs/closed_loop.json`
- `content/publish/tecience/*`（首发文、自动回复、OPS）
- `metrics/closed_loop.json`
