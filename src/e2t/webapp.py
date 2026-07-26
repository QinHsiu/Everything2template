"""Local trial web UI for commercial-effect inspection."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from e2t import __version__
from e2t.adapt import PLATFORMS
from e2t.pipeline import PLATFORM_LABELS, convert_source
from e2t.rewrite_llm import llm_configured, llm_info
from e2t.voices import list_voices

STATIC_DIR = Path(__file__).resolve().parent / "web_static"


def create_app() -> FastAPI:
    app = FastAPI(title="Everything2template Trial", version=__version__)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "version": __version__, "platforms": list(PLATFORMS)}

    @app.get("/api/meta")
    def meta() -> dict:
        return {
            "version": __version__,
            "platforms": [
                {"id": p, "label": PLATFORM_LABELS.get(p, p)} for p in PLATFORMS
            ],
            "voices": list_voices(),
            "llm_enabled": llm_configured(),
            "llm": llm_info(),
        }

    @app.post("/api/convert")
    async def convert(
        source_text: Annotated[str, Form()] = "",
        source_url: Annotated[str, Form()] = "",
        platforms: Annotated[str, Form()] = "wechat,xiaohongshu,zhihu,weibo,douyin",
        voice: Annotated[str, Form()] = "",
        humanize: Annotated[str, Form()] = "1",
        use_llm: Annotated[str, Form()] = "1",
        upload: UploadFile | None = File(None),
    ) -> JSONResponse:
        try:
            selected = [p.strip() for p in platforms.split(",") if p.strip()]
            src = ""
            hint = None
            tmp_path: Path | None = None
            if upload is not None and upload.filename:
                suffix = Path(upload.filename).suffix or ".txt"
                fd, name = tempfile.mkstemp(prefix="e2t_", suffix=suffix)
                tmp_path = Path(name)
                data = await upload.read()
                tmp_path.write_bytes(data)
                src = str(tmp_path)
                hint = None
            elif source_url.strip():
                src = source_url.strip()
                hint = "url" if src.startswith("http") else None
            elif source_text.strip():
                src = source_text.strip()
                hint = "text"
            else:
                return JSONResponse(
                    {"ok": False, "error": "请提供文本、URL 或上传文件"}, status_code=400
                )

            result = convert_source(
                src,
                platforms=selected,
                hint=hint,
                voice=voice or None,
                do_humanize=humanize not in {"0", "false", "False"},
                use_llm=use_llm not in {"0", "false", "False"},
            )
            return JSONResponse({"ok": True, **result})
        except Exception as exc:  # noqa: BLE001
            return JSONResponse({"ok": False, "error": str(exc)}, status_code=500)

    return app


app = create_app()


def main(host: str = "127.0.0.1", port: int = 8767) -> None:
    import uvicorn

    uvicorn.run("e2t.webapp:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
