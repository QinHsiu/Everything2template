"""Fetch a web page and extract readable text → CIR."""

from __future__ import annotations

import re
from urllib.parse import urlparse

import html2text
import httpx
from bs4 import BeautifulSoup

from e2t.cir import SourceKind
from e2t.ingest.draft import draft_cir_from_text


def _clean_html(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
        tag.decompose()
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    root = soup.find("article") or soup.find("main") or soup.body or soup
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    text = converter.handle(str(root)).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text


def ingest_url(url: str, *, timeout: float = 30.0):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; Everything2template/0.1; "
            "+https://github.com/QinHsiu/Everything2template)"
        )
    }
    with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text
    title, text = _clean_html(html)
    if not text:
        raise ValueError(f"No readable text extracted from {url}")
    host = urlparse(url).netloc
    cir = draft_cir_from_text(
        text, source_kind=SourceKind.url, source_ref=url, title=title or None
    )
    cir.meta["host"] = host
    label = host.split(".")[-2] if "." in host else host
    cir.tags = list({*cir.tags, label})
    return cir
