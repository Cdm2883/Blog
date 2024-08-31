CATEGORIES = {
    '技术': 'technical',
    '绘画': 'drawing',
    '日常': 'daily',
}

def _make_slug(text, _sep):
    return CATEGORIES[text]
def slugify():
    return _make_slug
