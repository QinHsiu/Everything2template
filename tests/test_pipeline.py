from pathlib import Path
import re

from e2t.adapt import PLATFORMS, skeleton_article
from e2t.cir import CIR, SourceKind
from e2t.compliance import check_compliance
from e2t.export import export_markdown, export_wechat_html
from e2t.humanize import humanize
from e2t.ingest import ingest
from e2t.validate import validate_article

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "sample_inputs" / "demo_article.md"


def test_ingest_markdown():
    cir = ingest(str(DEMO), hint="markdown")
    assert cir.source_kind == SourceKind.markdown
    assert cir.title
    assert cir.key_points or cir.sections


def test_platforms_ge_5():
    assert len(PLATFORMS) >= 5
    assert "weibo" in PLATFORMS and "douyin" in PLATFORMS


def test_humanize_and_compliance():
    dirty = "综上所述，这标志着具有里程碑意义的赋能，未来可期。"
    cleaned = humanize(dirty)
    assert "综上所述" not in cleaned.text
    assert cleaned.changed
    assert check_compliance("普通内容分享").ok
    assert not check_compliance("稳赚不赔的内幕消息").ok


def test_wechat_html(tmp_path: Path):
    md = "# Title\n\nThis is **important** text.\n\n> quote line\n\n## End\n\nBody."
    path = export_wechat_html(md, tmp_path / "a.wechat.html", title="Test")
    html = path.read_text(encoding="utf-8")
    assert "section" in html
    assert "<strong>important</strong>" in html
    assert "07c160" in html


def test_skeleton_and_validate_wechat(tmp_path: Path):
    cir = ingest(str(DEMO))
    draft = skeleton_article(cir, "wechat")
    draft = draft + "\n\n" + ("这是补充段落，用于保证可读长度。" * 20)
    path = tmp_path / "wechat.md"
    export_markdown(draft, path)
    result = validate_article("wechat", path.read_text(encoding="utf-8"))
    assert not result.errors
    assert result.score >= 60


def test_weibo_douyin_validate():
    cir = CIR(
        source_kind=SourceKind.text,
        source_ref="inline",
        title="测试主题",
        summary="这是结论摘要",
        key_points=["要点A", "要点B", "要点C"],
        tags=["效率"],
    )
    wb = skeleton_article(cir, "weibo")
    dy = skeleton_article(cir, "douyin")
    assert validate_article("weibo", wb).ok or validate_article("weibo", wb).score >= 50
    assert "钩子" in dy or "镜头" in dy


def test_titles_and_image_plan():
    from e2t.images import build_image_plan
    from e2t.titles import title_variants

    titles = title_variants("效率工具", "xiaohongshu", summary="先说结论")
    assert len(titles) >= 3
    plan = build_image_plan("效率工具", ["步骤一", "步骤二"], platform="xiaohongshu")
    assert plan.slots and plan.slots[0].role == "cover"


def test_pro_voice_loads():
    from e2t.voices import load_voice

    v = load_voice("pro_operator")
    assert v.id == "pro_operator"


def test_rewrite_has_hook_and_length():
    from e2t.rewrite import rewrite_article
    from e2t.validate import FILLER_SPAM, validate_article

    cir = ingest(str(DEMO))
    wechat = rewrite_article(cir, "wechat", use_llm=False)
    assert "别再" in wechat or "先说" in wechat
    assert len(wechat) > 400
    assert not any(s in wechat for s in FILLER_SPAM)
    h1 = next(ln[2:].strip() for ln in wechat.splitlines() if ln.startswith("# "))
    assert not h1.endswith(("：", "我用", "的", "了"))
    assert validate_article("wechat", wechat).ok
    xhs = rewrite_article(cir, "xiaohongshu", use_llm=False)
    assert "#" in xhs
    assert "先说结论" in xhs or "结论" in xhs
    assert validate_article("xiaohongshu", xhs).ok


def test_cir_roundtrip(tmp_path: Path):
    cir = ingest(str(DEMO))
    path = tmp_path / "cir.json"
    cir.save(path)
    loaded = CIR.load(path)
    assert loaded.id == cir.id
    assert loaded.title == cir.title


def test_source_ref_is_portable():
    """Ingested CIR must not store machine-local absolute paths."""
    cir = ingest(str(DEMO))
    assert "PycharmProjects" not in cir.source_ref
    assert not re.match(r"^[A-Za-z]:[/]", cir.source_ref)
    assert "examples/sample_inputs/demo_article.md" in cir.source_ref.replace("/", "/")
    brief = cir.to_brief()
    assert "PycharmProjects" not in brief
    assert not re.search(r"[A-Za-z]:[/].*Everything2template", brief)
