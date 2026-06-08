import re

HEADERLINK_ANCHOR_PATTERN = re.compile(
    r'<a\b(?=[^>]*\bclass=["\'][^"\']*\bheaderlink\b[^"\']*["\'])'
    r'(?=[^>]*\bdata-preview\b)[^>]*>',
    re.IGNORECASE,
)
DATA_PREVIEW_ATTRIBUTE_PATTERN = re.compile(
    r'\sdata-preview(?:=(?:""|\'\'|[^\s>]+))?',
    re.IGNORECASE,
)

def strip_headerlink_preview(html: str) -> str:
    def strip_attribute(match: re.Match) -> str:
        return DATA_PREVIEW_ATTRIBUTE_PATTERN.sub("", match.group(0))

    return HEADERLINK_ANCHOR_PATTERN.sub(strip_attribute, html)

def on_page_content(html, page, config, files, **kwargs):
    return strip_headerlink_preview(html)
