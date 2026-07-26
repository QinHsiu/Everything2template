#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e ".[dev,research]"
python -m e2t version
python -m pytest -q
echo "OK — try: e2t run examples/sample_inputs/demo_article.md"
