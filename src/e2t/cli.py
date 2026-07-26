"""CLI: e2t ingest | adapt | validate | export | humanize | run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.panel import Panel

from e2t import __version__
from e2t.adapt import PLATFORMS, build_writer_brief, skeleton_article
from e2t.cir import CIR
from e2t.compliance import check_compliance
from e2t.export import export_markdown, export_pdf, export_wechat_html
from e2t.humanize import humanize
from e2t.images import build_image_plan, try_fetch_images
from e2t.ingest import ingest
from e2t.research import research
from e2t.rewrite import rewrite_article
from e2t.rewrite_llm import llm_configured, llm_info
from e2t.titles import title_variants
from e2t.validate import validate_article
from e2t.voices import list_voices

app = typer.Typer(
    name="e2t",
    help="Everything2template — ingest → CIR → platform templates → MD/PDF/HTML",
    add_completion=False,
    no_args_is_help=True,
)


def _default_run_dir(cir_id: str) -> Path:
    root = Path.cwd() / "content" / "runs" / cir_id
    root.mkdir(parents=True, exist_ok=True)
    return root


@app.command()
def version() -> None:
    rprint(__version__)


@app.command("ingest")
def ingest_cmd(
    source: str = typer.Argument(...),
    out: Optional[Path] = typer.Option(None, "--out", "-o"),
    hint: Optional[str] = typer.Option(None, "--hint"),
) -> None:
    cir = ingest(source, hint=hint)
    out_path = out or (_default_run_dir(cir.id) / "cir.json")
    cir.save(out_path)
    brief_path = out_path.with_name("brief.md")
    brief_path.write_text(cir.to_brief(), encoding="utf-8")
    rprint(
        Panel.fit(
            f"[bold]CIR[/bold] {cir.id}\nkind={cir.source_kind.value}\n"
            f"title={cir.title}\nsaved={out_path}\nbrief={brief_path}",
            title="ingest ok",
        )
    )


@app.command("voices")
def voices_cmd() -> None:
    rprint(json.dumps(list_voices(), ensure_ascii=False, indent=2))


@app.command("humanize")
def humanize_cmd(
    file: Path = typer.Argument(..., help="Markdown draft"),
    in_place: bool = typer.Option(False, "--in-place"),
    out: Optional[Path] = typer.Option(None, "--out", "-o"),
) -> None:
    """Strip common Chinese AI-flavor phrases."""
    text = file.read_text(encoding="utf-8")
    result = humanize(text)
    dest = file if in_place else (out or file.with_name(file.stem + ".humanized.md"))
    dest.write_text(result.text, encoding="utf-8")
    rprint(
        Panel.fit(
            f"saved={dest}\nreplacements={len(result.replacements)}\n"
            f"removed={len(result.removed)}",
            title="humanize",
        )
    )


@app.command("adapt")
def adapt_cmd(
    cir_path: Path = typer.Argument(...),
    platform: str = typer.Option(..., "--platform", "-p"),
    mode: str = typer.Option("rewrite", "--mode"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v"),
    out_dir: Optional[Path] = typer.Option(None, "--out-dir"),
    skeleton: bool = typer.Option(True, "--skeleton/--no-skeleton"),
) -> None:
    cir = CIR.load(cir_path)
    dest = out_dir or cir_path.parent / platform
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "writer_brief.md").write_text(
        build_writer_brief(cir, platform, mode=mode, voice=voice), encoding="utf-8"
    )
    article_path = None
    if skeleton:
        article_path = dest / "draft.md"
        article_path.write_text(
            rewrite_article(cir, platform, use_llm=True), encoding="utf-8"
        )
    rprint(
        Panel.fit(
            f"platform={platform}\nvoice={voice or '-'}\n"
            f"draft={article_path or '(skipped)'}",
            title="adapt ok",
        )
    )


@app.command("validate")
def validate_cmd(
    platform: str = typer.Option(..., "--platform", "-p"),
    file: Path = typer.Argument(...),
    compliance: bool = typer.Option(True, "--compliance/--no-compliance"),
) -> None:
    text = file.read_text(encoding="utf-8")
    result = validate_article(platform, text)
    payload = result.to_dict()
    if compliance:
        payload["compliance"] = check_compliance(text, platform=platform).to_dict()
        if not payload["compliance"]["ok"]:
            result.ok = False
    rprint(json.dumps(payload, ensure_ascii=False, indent=2))
    raise typer.Exit(code=0 if result.ok else 1)


@app.command("export")
def export_cmd(
    file: Path = typer.Argument(...),
    fmt: str = typer.Option("both", "--format", "-f", help="md|pdf|html|both|all"),
    out_dir: Optional[Path] = typer.Option(None, "--out-dir"),
    title: Optional[str] = typer.Option(None, "--title"),
    humanize_first: bool = typer.Option(False, "--humanize"),
) -> None:
    text = file.read_text(encoding="utf-8")
    if humanize_first:
        text = humanize(text).text
    dest = out_dir or file.parent / "export"
    dest.mkdir(parents=True, exist_ok=True)
    stem = file.stem
    outputs: list[str] = []
    want_md = fmt in {"md", "both", "all"}
    want_pdf = fmt in {"pdf", "both", "all"}
    want_html = fmt in {"html", "all"} or (fmt == "both" and False)
    # html on 'all' or explicit html; also when --format both we keep md+pdf
    if fmt == "html":
        want_md = False
        want_pdf = False
        want_html = True
    if want_md:
        outputs.append(str(export_markdown(text, dest / f"{stem}.md")))
    if want_pdf:
        try:
            outputs.append(str(export_pdf(text, dest / f"{stem}.pdf", title=title)))
        except Exception as exc:  # noqa: BLE001
            rprint(f"[yellow]PDF skipped:[/yellow] {exc}")
    if want_html or fmt == "all":
        outputs.append(str(export_wechat_html(text, dest / f"{stem}.wechat.html", title=title)))
    rprint(Panel.fit("\n".join(outputs) or "(nothing)", title="export"))


@app.command("llm-info")
def llm_info_cmd() -> None:
    """Show LLM provider status (default: DeepSeek)."""
    rprint(json.dumps(llm_info(), ensure_ascii=False, indent=2))


@app.command("web")
def web_cmd(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8767, "--port"),
) -> None:
    """Launch local trial web UI for commercial-effect inspection."""
    import uvicorn

    rprint(Panel.fit(f"http://{host}:{port}\n试用检验台", title="e2t web"))
    uvicorn.run("e2t.webapp:app", host=host, port=port, reload=False)


@app.command("research")
def research_cmd(
    query: str = typer.Argument(...),
    out: Optional[Path] = typer.Option(None, "--out", "-o"),
    max_results: int = typer.Option(8, "--max"),
) -> None:
    """Optional web research (requires ddgs)."""
    result = research(query, max_results=max_results)
    dest = out or Path("content/runs/research") / "research.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(result.to_markdown(), encoding="utf-8")
    (dest.with_suffix(".json")).write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rprint(Panel.fit(f"backend={result.backend}\nhits={len(result.hits)}\n{dest}", title="research"))


@app.command("titles")
def titles_cmd(
    title: str = typer.Argument(...),
    platform: str = typer.Option("wechat", "--platform", "-p"),
    summary: str = typer.Option("", "--summary"),
) -> None:
    rprint(json.dumps(title_variants(title, platform, summary=summary), ensure_ascii=False, indent=2))


@app.command("batch")
def batch_cmd(
    list_file: Path = typer.Argument(..., help="Text file with one source path/URL per line"),
    platforms: str = typer.Option("wechat,xiaohongshu,zhihu", "--platforms"),
    out_dir: Path = typer.Option(Path("content/runs/batch"), "--out-dir"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v"),
) -> None:
    """Batch-convert many sources (agency workflow)."""
    lines = [
        ln.strip()
        for ln in list_file.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: list[dict] = []
    for i, src in enumerate(lines, 1):
        dest = out_dir / f"{i:02d}"
        try:
            # reuse run logic via ingest+loop inline
            cir = ingest(src)
            dest.mkdir(parents=True, exist_ok=True)
            cir.save(dest / "cir.json")
            for p in [x.strip() for x in platforms.split(",") if x.strip()]:
                pdir = dest / p
                pdir.mkdir(parents=True, exist_ok=True)
                draft = humanize(rewrite_article(cir, p, use_llm=True)).text
                (pdir / "draft.md").write_text(draft, encoding="utf-8")
                (pdir / "titles.json").write_text(
                    json.dumps(
                        title_variants(cir.title, p, summary=cir.summary),
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                if voice:
                    (pdir / "writer_brief.md").write_text(
                        build_writer_brief(cir, p, voice=voice), encoding="utf-8"
                    )
            summary.append({"source": src, "ok": True, "out": str(dest)})
        except Exception as exc:  # noqa: BLE001
            summary.append({"source": src, "ok": False, "error": str(exc)})
    (out_dir / "batch_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rprint(Panel.fit(f"batch n={len(lines)} → {out_dir}", title="batch"))


@app.command("run")
def run_cmd(
    source: str = typer.Argument(...),
    platforms: str = typer.Option(
        "wechat,xiaohongshu,zhihu,weibo,douyin",
        "--platforms",
    ),
    out_dir: Optional[Path] = typer.Option(None, "--out-dir"),
    hint: Optional[str] = typer.Option(None, "--hint"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v"),
    export_pdf_flag: bool = typer.Option(True, "--pdf/--no-pdf"),
    do_humanize: bool = typer.Option(True, "--humanize/--no-humanize"),
    wechat_html: bool = typer.Option(True, "--wechat-html/--no-wechat-html"),
    do_research: bool = typer.Option(False, "--research/--no-research"),
    fetch_images: bool = typer.Option(False, "--fetch-images/--no-fetch-images"),
    use_llm: bool = typer.Option(True, "--llm/--no-llm", help="Use LLM polish when API key set"),
) -> None:
    cir = ingest(source, hint=hint)
    root = out_dir or _default_run_dir(cir.id)
    root.mkdir(parents=True, exist_ok=True)
    if do_research:
        rq = cir.title or source[:80]
        rr = research(rq)
        (root / "research.md").write_text(rr.to_markdown(), encoding="utf-8")
        cir.meta["research_backend"] = rr.backend
        cir.meta["research_hits"] = len(rr.hits)
    cir.save(root / "cir.json")
    (root / "brief.md").write_text(cir.to_brief(), encoding="utf-8")
    (root / "llm_status.txt").write_text(
        "enabled" if (use_llm and llm_configured()) else "rules-only",
        encoding="utf-8",
    )

    selected = [p.strip() for p in platforms.split(",") if p.strip()]
    for p in selected:
        if p not in PLATFORMS:
            raise typer.BadParameter(f"Unknown platform {p}; choose from {PLATFORMS}")
        pdir = root / p
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "writer_brief.md").write_text(
            build_writer_brief(cir, p, voice=voice), encoding="utf-8"
        )
        draft = rewrite_article(cir, p, use_llm=use_llm)
        if do_humanize:
            draft = humanize(draft).text
        (pdir / "draft.md").write_text(draft, encoding="utf-8")
        (pdir / "titles.json").write_text(
            json.dumps(
                title_variants(cir.title, p, summary=cir.summary),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        plan = build_image_plan(cir.title, cir.key_points, platform=p)
        if fetch_images:
            plan = try_fetch_images(plan, pdir / "images")
        (pdir / "image_plan.md").write_text(plan.to_markdown(), encoding="utf-8")
        result = validate_article(p, draft)
        compliance = check_compliance(draft, platform=p)
        (pdir / "validate.json").write_text(
            json.dumps(
                {**result.to_dict(), "compliance": compliance.to_dict()},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        export_markdown(draft, pdir / "export" / "draft.md")
        if export_pdf_flag:
            try:
                export_pdf(draft, pdir / "export" / "draft.pdf", title=cir.title)
            except Exception as exc:  # noqa: BLE001
                (pdir / "export" / "pdf_error.txt").write_text(str(exc), encoding="utf-8")
        if wechat_html and p == "wechat":
            export_wechat_html(draft, pdir / "export" / "draft.wechat.html", title=cir.title)

    mode = "llm+rules" if (use_llm and llm_configured()) else "rules-rewrite"
    rprint(Panel.fit(f"run complete → {root}\nmode={mode}", title="e2t"))


if __name__ == "__main__":
    app()
