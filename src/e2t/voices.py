"""Optional brand voice profiles (Pro-oriented extension point)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from e2t.paths import display_path


class VoiceProfile(BaseModel):
    id: str
    display_name: str
    platforms: list[str] = Field(
        default_factory=lambda: ["wechat", "xiaohongshu", "zhihu", "weibo", "douyin"]
    )
    persona: str = ""
    do: list[str] = Field(default_factory=list)
    dont: list[str] = Field(default_factory=list)
    signature_cta: dict[str, str] = Field(default_factory=dict)
    banned_phrases: list[str] = Field(default_factory=list)

    def as_prompt_block(self) -> str:
        lines = [
            f"Voice profile: {self.display_name} ({self.id})",
            f"Persona: {self.persona}",
            "Do:",
            *[f"- {x}" for x in self.do],
            "Don't:",
            *[f"- {x}" for x in self.dont],
        ]
        if self.signature_cta:
            lines.append("CTA overrides:")
            for k, v in self.signature_cta.items():
                lines.append(f"- {k}: {v}")
        if self.banned_phrases:
            lines.append("Banned phrases: " + ", ".join(self.banned_phrases))
        return "\n".join(lines)


DEFAULT_VOICES: dict[str, VoiceProfile] = {
    "tech_builder": VoiceProfile(
        id="tech_builder",
        display_name="Tech Builder",
        persona="务实的构建者：先演示，再讲原理，诚实说局限",
        do=["给可复现步骤", "用具体数字（仅来自源）", "对比取舍"],
        dont=["假装测评过未出现的产品", "绝对化承诺", "空泛励志"],
        signature_cta={
            "wechat": "如果这篇对你有用，点个在看，我继续拆可落地的方法。",
            "xiaohongshu": "你们还想看我拆哪个工具？评论区扣1",
            "zhihu": "欢迎贴反例；有更好的做法我会更新到文首。",
        },
        banned_phrases=["赋能", "闭环", "颠覆式"],
    ),
    "knowledge_operator": VoiceProfile(
        id="knowledge_operator",
        display_name="Knowledge Operator",
        persona="知识工作者：强调流程、清单、可迁移方法",
        do=["清单化", "给模板字段", "标注适用边界"],
        dont=["鸡汤开头", "恐吓式标题"],
        signature_cta={
            "wechat": "把清单收藏后，今天先执行第 1 步。",
            "xiaohongshu": "保存这页，下周回来打卡进度",
            "zhihu": "你的流程里哪一步最容易断？评论区交流。",
        },
    ),
}


def _voice_dirs(custom_dir: str | Path | None = None) -> list[Path]:
    dirs: list[Path] = []
    if custom_dir:
        dirs.append(Path(custom_dir))
    env = os.environ.get("E2T_VOICE_DIR")
    if env:
        dirs.append(Path(env))
    # bundled Pro pack in repo (buyers copy here or set env)
    repo_pro = Path(__file__).resolve().parents[2] / "packaging" / "pro" / "voices"
    dirs.append(repo_pro)
    return dirs


def load_voice(voice_id: str, *, custom_dir: str | Path | None = None) -> VoiceProfile:
    for d in _voice_dirs(custom_dir):
        path = d / f"{voice_id}.json"
        if path.exists():
            return VoiceProfile.model_validate_json(path.read_text(encoding="utf-8"))
    if voice_id in DEFAULT_VOICES:
        return DEFAULT_VOICES[voice_id]
    raise KeyError(f"Unknown voice profile: {voice_id}")


def list_voices() -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {
        v.id: {"id": v.id, "display_name": v.display_name, "platforms": v.platforms}
        for v in DEFAULT_VOICES.values()
    }
    for d in _voice_dirs():
        if not d.exists():
            continue
        for path in d.glob("*.json"):
            try:
                v = VoiceProfile.model_validate_json(path.read_text(encoding="utf-8"))
                found[v.id] = {
                    "id": v.id,
                    "display_name": v.display_name,
                    "platforms": v.platforms,
                    "source": display_path(path),
                }
            except Exception:  # noqa: BLE001
                continue
    return list(found.values())
