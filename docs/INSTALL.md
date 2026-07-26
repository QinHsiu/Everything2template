# Install across agents

## Python CLI

```bash
cd Everything2template   # or: git clone … && cd Everything2template
pip install -e ".[dev]"
python -m e2t version
```

## Cursor

Copy or symlink the skill folder:

```text
skill/everything2template  →  <workspace>/.cursor/skills/everything2template
```

PowerShell example (replace `<repo>` / `<workspace>` with your paths):

```powershell
New-Item -ItemType Junction `
  -Path "<workspace>\.cursor\skills\everything2template" `
  -Target "<repo>\skill\everything2template"
```

Then use `/e2t`, `/e2t_wechat`, `/e2t_xhs`, `/e2t_zhihu`, `/e2t_export`.

## Claude / other agents

1. Add `skill/everything2template/SKILL.md` to the agent's skill path or project instructions.
2. Ensure `e2t` is importable in the same environment the agent can shell into.
3. Prefer CLI for ingest/export; let the model do platform rewrite from `writer_brief.md`.

## Verify

```bash
python -m pytest -q
python scripts/commercial_score.py
e2t run examples/sample_inputs/demo_article.md
```
