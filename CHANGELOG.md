# Changelog

## 0.4.2 — 2026-07-26

- Portable paths: CIR `source_ref` / briefs / score JSON use repo-relative paths (no machine abs paths)
- Docs install examples no longer hardcode local disks
- `scripts/scrub_local_paths.py` + `scripts/check_no_local_paths.py`

## 0.4.1 — 2026-07-26

- **Open-source strongest track**: rewrite engine removes filler spam / truncated H1 / wrong section fallback
- Stronger `validate` anti-regression (FILLER_SPAM, title truncation)
- `scripts/strongest_score.py` gate (avg ≥85 + parity + tests)
- README repositioned: Apache-2.0 core first; Tecience optional support only

## 0.4.0 — 2026-07-26

- **Breaking product intent**: default output is publish-oriented rewrite (hooks/traffic), not thin skeletons
- New `e2t.rewrite` engine + optional LLM polish (`E2T_LLM_API_KEY` / `OPENAI_API_KEY`)
- Stronger CIR extraction; trial web shows rewrite mode + effect score
- Fix markdown title taken from H1 instead of filename

## 0.3.0 — 2026-07-26

- Profit-loop v2: sales page, Pro SKU zip, installers, Claude plugin manifest
- Research (optional ddgs) + image plan/fetch + title variants + batch CLI
- Converter depth notes; stricter `scripts/profit_ready.py` gate

## 0.2.0 — 2026-07-26

- exp_loop P1 parity pack vs OSS rivals
- Platforms: +weibo, +douyin (now 5)
- Humanize pass + compliance lexicon
- WeChat paste HTML export
- Lightweight MCP JSON-RPC server (`python -m e2t.mcp_server`)
- `scripts/competitive_parity.py` gated into commercial score

## 0.1.0 — 2026-07-25

- Initial commercializable core: CIR ingest, 3 platform templates, validate, MD/PDF export
- Cursor skill with `/e2t` family commands
- Competitive analysis + GTM docs
- Demo article + CLI one-shot `e2t run`
