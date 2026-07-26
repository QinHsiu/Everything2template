# Experiment: e2t-oss-loop-v1

## Goal

Close open-source competitor gaps for Everything2template until **commercializable** under a stricter parity bar.

## target_score

```yaml
task: e2t_commercial_parity
eval_set: local_benchmark (demo_article + project self-ingest + validate suite)
metric: commercial_ready
threshold:
  commercializable: true          # scripts/commercial_score.py
  competitive_parity: >= 0.85     # scripts/competitive_parity.py
  tests_pass: true
secondary:
  - wechat_html_export: true
  - humanize_pass: true
  - mcp_server: true
  - platforms_count: >= 5
  - compliance_gate: true
```

## tool/function

- local Python 3.10+
- git shallow clones under `competitors/`
- pytest + e2t CLI
- no paid publish APIs; auto-login publish is **out of scope** (account risk)

## Stop

Stop when `target_score` met OR plans exhausted with documented deferrals.
