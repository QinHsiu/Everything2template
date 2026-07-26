"""Optional LLM polish — default provider: DeepSeek (OpenAI-compatible).

Env (priority high → low for API key):
  E2T_LLM_API_KEY
  DEEPSEEK_API_KEY
  OPENAI_API_KEY

Other:
  E2T_LLM_PROVIDER=deepseek|openai|ollama|custom   (default deepseek)
  E2T_LLM_BASE_URL / OPENAI_BASE_URL / DEEPSEEK_BASE_URL
  E2T_LLM_MODEL / DEEPSEEK_MODEL / OLLAMA_MODEL
  OLLAMA_HOST (default http://127.0.0.1:11434)

Loads `.env` from cwd and package repo root if present (no extra dependency).
Ollama needs no API key; auto-selected when provider=ollama or DeepSeek unset and Ollama is up.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import httpx

from e2t.adapt import load_template
from e2t.cir import CIR

_ENV_LOADED = False

PROVIDERS = {
    "deepseek": {
        "base": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_envs": ("E2T_LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"),
        "needs_key": True,
    },
    "openai": {
        "base": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_envs": ("E2T_LLM_API_KEY", "OPENAI_API_KEY"),
        "needs_key": True,
    },
    "ollama": {
        "base": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
        "key_envs": ("E2T_LLM_API_KEY", "OLLAMA_API_KEY"),
        "needs_key": False,
    },
    "custom": {
        "base": "http://127.0.0.1:8000/v1",
        "model": "default",
        "key_envs": ("E2T_LLM_API_KEY", "OPENAI_API_KEY"),
        "needs_key": False,
    },
}


def _load_dotenv() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            k, v = k.strip(), v.strip().strip("'").strip('"')
            if k and k not in os.environ:
                os.environ[k] = v


def llm_configured() -> bool:
    _load_dotenv()
    return _client_settings() is not None


def _ollama_host() -> str:
    return (os.environ.get("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")


def ollama_available() -> bool:
    try:
        with httpx.Client(timeout=1.5) as client:
            r = client.get(f"{_ollama_host()}/api/tags")
            return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


def llm_info() -> dict[str, Any]:
    _load_dotenv()
    cfg = _client_settings()
    if not cfg:
        hint = "在项目根目录 .env 写入 DEEPSEEK_API_KEY=sk-...，或安装并启动 Ollama 后设 E2T_LLM_PROVIDER=ollama"
        return {
            "configured": False,
            "provider": os.environ.get("E2T_LLM_PROVIDER", "deepseek"),
            "ollama_up": ollama_available(),
            "hint": hint,
        }
    preview = "***"
    if cfg.get("key") and cfg["key"] not in ("ollama", "no-key"):
        preview = cfg["key"][:7] + "…" if len(cfg["key"]) > 8 else "***"
    return {
        "configured": True,
        "provider": cfg["provider"],
        "base": cfg["base"],
        "model": cfg["model"],
        "key_preview": preview,
        "ollama_up": ollama_available(),
    }


def _looks_like_real_key(key: str) -> bool:
    k = key.strip()
    if len(k) < 20:
        return False
    if "请替换" in k or "your" in k.lower() or "xxx" in k.lower():
        return False
    return k.startswith("sk-") or len(k) >= 24


def _client_settings() -> dict[str, str] | None:
    _load_dotenv()
    provider = (os.environ.get("E2T_LLM_PROVIDER") or "").lower().strip()

    # Auto: prefer configured DeepSeek/OpenAI; else live Ollama
    if not provider or provider == "auto":
        for cand in ("deepseek", "openai"):
            probe = _settings_for(cand)
            if probe:
                return probe
        if ollama_available():
            return _settings_for("ollama")
        return None

    if provider not in PROVIDERS:
        provider = "deepseek"
    return _settings_for(provider)


def _settings_for(provider: str) -> dict[str, str] | None:
    preset = PROVIDERS[provider]
    key = ""
    for env_name in preset["key_envs"]:
        if os.environ.get(env_name):
            key = os.environ[env_name].strip()
            break
    if not key and provider == "deepseek":
        key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()

    needs_key = bool(preset.get("needs_key", True))
    if needs_key:
        if not key or not _looks_like_real_key(key):
            return None
    else:
        if provider == "ollama" and not ollama_available():
            # still allow explicit base override attempts
            if not (os.environ.get("E2T_LLM_BASE_URL") or os.environ.get("OLLAMA_HOST")):
                return None
        key = key or ("ollama" if provider == "ollama" else "no-key")

    if provider == "ollama":
        base = (
            os.environ.get("E2T_LLM_BASE_URL")
            or f"{_ollama_host()}/v1"
        ).rstrip("/")
        model = (
            os.environ.get("E2T_LLM_MODEL")
            or os.environ.get("OLLAMA_MODEL")
            or preset["model"]
        )
    else:
        base = (
            os.environ.get("E2T_LLM_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or preset["base"]
        ).rstrip("/")
        model = (
            os.environ.get("E2T_LLM_MODEL")
            or os.environ.get("DEEPSEEK_MODEL")
            or preset["model"]
        )
    return {"key": key, "base": base, "model": model, "provider": provider}


def maybe_llm_polish(cir: CIR, platform: str, draft: str) -> str | None:
    cfg = _client_settings()
    if not cfg:
        return None
    template = load_template(platform)
    system = (
        "你是资深新媒体主编。目标：在信息不编造的前提下，把草稿改成更有钩子、有话题、"
        "能停留与转发的平台成稿。必须遵守：\n"
        "1) 只用 CIR/草稿里已有事实，禁止虚构数据、经历、引用\n"
        "2) 不确定就删或标「待核实」\n"
        "3) 结构必须平台原生，拒绝同文换皮\n"
        "4) 语言真人、具体、有冲突感与获得感，去掉套话\n"
        "5) 只输出最终 Markdown 正文（可含备选标题与元数据），不要解释过程"
    )
    user = (
        f"平台: {platform}\n\n"
        f"## 平台模板\n{template}\n\n"
        f"## CIR\n{cir.to_brief(max_chars=5000)}\n\n"
        f"## 当前草稿（请大幅改写增强传播力，但保真）\n{draft}\n"
    )
    payload: dict[str, Any] = {
        "model": cfg["model"],
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
    }
    # DeepSeek OpenAI-compatible endpoint
    url = f"{cfg['base']}/chat/completions"
    if cfg["base"].endswith("/v1"):
        url = f"{cfg['base']}/chat/completions"
    else:
        # https://api.deepseek.com/chat/completions also works; also try /v1
        url = f"{cfg['base']}/chat/completions"

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code == 404 and not cfg["base"].endswith("/v1"):
            resp = client.post(
                f"{cfg['base']}/v1/chat/completions", headers=headers, json=payload
            )
        resp.raise_for_status()
        data = resp.json()
    content = data["choices"][0]["message"]["content"]
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:markdown|md)?\n", "", content)
        content = re.sub(r"\n```$", "", content)
    return content
