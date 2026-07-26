# Everything2template

**Any source → WeChat / Xiaohongshu / Zhihu / Weibo / Douyin → Markdown, WeChat HTML & PDF**

Apache-2.0 **open source**. Goal: the **strongest OSS** adapter in this category — multi-source ingest + platform-native rebuild at **publishable / commercial-grade effect** (not a thin prompt pack).

## Why this exists

Peers usually do one of: (a) cloud paste→rewrite, (b) prompt-only skill packs, (c) heavy auto-publish suites.  
We own the painful middle:

1. **Ingest everything** — URL, PDF, DOCX, Markdown, code, project tree  
2. **CIR once** — Canonical Intermediate Representation (facts stay grounded)  
3. **Rebuild per platform** — not the same essay in five skins  
4. **Humanize + compliance + validate** — kill AI filler, flag risky claims, catch truncated titles / template spam  
5. **Export** — Markdown, WeChat paste HTML, CJK PDF  
6. **Agent-native** — Cursor skill + CLI + MCP lite + local trial web  

Quality gate (open-source strongest):

```bash
python scripts/strongest_score.py
```

See [docs/competitive.md](docs/competitive.md) and `content/exp/e2t-oss-strongest-v4/`.

## Install

```bash
cd Everything2template
pip install -e ".[dev]"
e2t version
python scripts/strongest_score.py
```

### Cursor skill

See [docs/INSTALL.md](docs/INSTALL.md). Junction/copy:

```text
skill/everything2template  →  <workspace>/.cursor/skills/everything2template
```

Slash commands: `/e2t`, `/e2t_wechat`, `/e2t_xhs`, `/e2t_zhihu`, `/e2t_export`.

## Trial web UI

```bash
e2t web
# http://127.0.0.1:8767
```

Optional LLM polish (DeepSeek / Ollama): [docs/deepseek.md](docs/deepseek.md). Without a key, the **rules rewrite engine** still produces platform-native drafts.

## CLI

```bash
e2t ingest https://example.com/post
e2t adapt content/runs/<id>/cir.json -p wechat
e2t humanize content/runs/<id>/wechat/draft.md --in-place
e2t validate -p wechat content/runs/<id>/wechat/draft.md
e2t export content/runs/<id>/wechat/draft.md -f all
e2t run examples/sample_inputs/demo_article.md --no-llm
python -m e2t.mcp_server
```

## License & support

- **License:** Apache-2.0 (open core)  
- **Support / optional tips:** WeChat OA **Tecience** (reply `E2T`) — does not gate the open core  
- Changelog: [CHANGELOG.md](CHANGELOG.md) · Support: [SUPPORT.md](SUPPORT.md)
