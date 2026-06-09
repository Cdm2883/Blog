import posixpath
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

IMAGE_EXTENSIONS = (".apng", ".avif", ".gif", ".jpg", ".jpeg", ".png", ".webp")
SKIP_IMAGE_CLASSES = {"twemoji", "md-author", "md-post__cover"}

def is_supported_image_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    if is_remote_url(url):
        return True
    if parsed.scheme:
        return False
    return parsed.path.lower().endswith(IMAGE_EXTENSIONS)

def is_remote_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

def resolve_rendered_path(src: str, page_url: str) -> str:
    parsed = urlparse(src.strip())
    if parsed.path.startswith("/"):
        return parsed.path.lstrip("/")

    base = page_url if page_url.endswith("/") else posixpath.dirname(page_url)
    return posixpath.normpath(posixpath.join(base, parsed.path))

class PhotoSwipeTransformer(HTMLParser):
    def __init__(self, page_url: str, image_info: dict[str, tuple[int, int, str]]):
        super().__init__(convert_charrefs=False)
        self.page_url = page_url
        self.image_info = image_info
        self.parts = []
        self.anchor_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.anchor_depth += 1

        if tag != "img" or self.anchor_depth:
            self.parts.append(self.get_starttag_text())
            return

        attrs_dict = dict(attrs)
        src = attrs_dict.get("src", "")
        classes = set(attrs_dict.get("class", "").split())
        if not src or classes & SKIP_IMAGE_CLASSES or not is_supported_image_url(src):
            self.parts.append(self.get_starttag_text())
            return

        attrs_dict["data-pswp-src"] = src
        attrs_dict["data-pswp-gallery"] = "content"

        if not is_remote_url(src):
            rendered_path = resolve_rendered_path(src, self.page_url)
            if rendered_path not in self.image_info:
                self.parts.append(self.get_starttag_text())
                return

            width, height, _ = self.image_info[rendered_path]
            attrs_dict["data-pswp-width"] = str(width)
            attrs_dict["data-pswp-height"] = str(height)

        classes = attrs_dict.get("class", "").split()
        if "pswp-image" not in classes:
            classes.append("pswp-image")
        attrs_dict["class"] = " ".join(classes).strip()
        self.parts.append(render_starttag(tag, attrs_dict, self.get_starttag_text()))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor_depth:
            self.anchor_depth -= 1
        self.parts.append(f"</{tag}>")

    def handle_data(self, data):
        self.parts.append(data)

    def handle_entityref(self, name):
        self.parts.append(f"&{name};")

    def handle_charref(self, name):
        self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.parts.append(f"<!{decl}>")

    def output(self) -> str:
        return "".join(self.parts)

def transform_html(html: str, page_url: str, image_info: dict[str, tuple[int, int, str]]) -> str:
    transformer = PhotoSwipeTransformer(page_url, image_info)
    transformer.feed(html)
    transformer.close()
    return transformer.output()

def render_starttag(tag: str, attrs: dict[str, str], original: str) -> str:
    suffix = " /" if original.rstrip().endswith("/>") else ""
    rendered = " ".join(
        f'{name}="{escape(value, quote=True)}"'
        for name, value in attrs.items()
        if value is not None
    )
    if rendered:
        return f"<{tag} {rendered}{suffix}>"
    return f"<{tag}{suffix}>"

def build_image_info(files, config) -> dict[str, tuple[int, int, str]]:
    docs_dir = Path(config["docs_dir"])
    info = {}
    for file in files.media_files():
        if not file.src_uri.lower().endswith(IMAGE_EXTENSIONS):
            continue

        path = docs_dir / file.src_path
        if not path.is_file():
            continue

        try:
            with Image.open(path) as image:
                size = (*image.size, file.url)
                info[file.src_uri] = size
                info[file.url.lstrip("/")] = size
        except Exception:
            continue

    return info

def is_blog_post_page(page) -> bool:
    return bool(page and page.meta and page.meta.get("template") == "blog-post.html")

def on_page_content(html, page, config, files, **kwargs):
    if not is_blog_post_page(page):
        return html

    return transform_html(html, page.url, build_image_info(files, config))
