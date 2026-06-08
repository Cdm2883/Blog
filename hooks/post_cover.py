import posixpath
import re
from urllib.parse import urlparse

MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
HTML_IMAGE_PATTERN = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
LOCAL_SCHEMES = {"", None}

def is_local_image(url: str) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme not in LOCAL_SCHEMES or parsed.netloc:
        return False

    path = parsed.path.lower()
    return path.endswith((".apng", ".avif", ".gif", ".jpg", ".jpeg", ".png", ".webp"))

def find_first_local_image(markdown: str) -> str | None:
    matches = [
        *MARKDOWN_IMAGE_PATTERN.finditer(markdown),
        *HTML_IMAGE_PATTERN.finditer(markdown),
    ]
    for match in sorted(matches, key = lambda match: match.start()):
        url = match.group(1).strip()
        if is_local_image(url):
            return url

    return None

def resolve_site_url(url: str, page, files) -> str:
    parsed = urlparse(url.strip())
    if parsed.path.startswith("/"):
        path = parsed.path.lstrip("/")
    else:
        path = posixpath.normpath(posixpath.join(
            posixpath.dirname(page.file.src_uri),
            parsed.path,
        ))

    file = files.get_file_from_path(path)
    if file:
        return file.url

    return path

def on_page_markdown(markdown, page, config, files, **kwargs):
    if page.meta.get("cover"):
        return markdown

    cover = find_first_local_image(markdown)
    if cover:
        page.meta["cover"] = resolve_site_url(cover, page, files)

    return markdown
