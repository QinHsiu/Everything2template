# e2t-oss-strongest-v4

Goal: **开源同类最强** — commercializable *effect*, Apache-2.0 core.

## Loop

1. Fix rewrite defects (truncation, filler spam, duplication)  
2. Harden `validate` anti-regression  
3. `python scripts/strongest_score.py` until `strongest_ready=true`  
4. Refresh polished samples + competitive doc  

## Commands

```bash
python scripts/strongest_score.py
python -m pytest -q
e2t run examples/sample_inputs/demo_article.md --no-llm --out-dir content/exp/e2t-oss-strongest-v4/metrics/demo
```
