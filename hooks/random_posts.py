import json
import re
from pathlib import Path
from typing import Optional, Tuple

import yaml
from dateutil.parser import parse as parse_date
from mkdocs.config import config_options
from mkdocs.structure.files import File, Files

OUTPUT_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>博客漫游中…</title>
<style>
    body {{ background: #1e2129 }}
    @media (prefers-color-scheme: light) {{
        body {{ background: unset }}
    }}
</style>
</head>
<body>
<script>
    var posts = {posts};
    var post = posts[Math.floor(Math.random() * posts.length)];
    var base = window.location.pathname.replace(/\/random(?:\/index\.html)?\/?$/, '');
    window.location.href = base + '/' + post + '/';
</script>
</body>
</html>"""

is_serving = False
def on_startup(command: str, **kwargs):
    global is_serving
    is_serving = command == 'serve'

def on_files(files: Files, *, config: config_options.Config) -> Optional[Files]:
    posts = [get_post_url(f, config) for f in files.documentation_pages()]
    posts = [p for p in posts if p]

    project_root = Path(config.config_file_path).parent
    output_path = project_root / '.cache' / 'random-posts' / 'random' / 'index.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(OUTPUT_TEMPLATE.format(posts=json.dumps(posts)), encoding='utf-8')

    files.append(File(
        path=output_path.name,
        src_dir=output_path.parent,
        dest_dir=Path(config['site_dir']) / output_path.parent.name,
        use_directory_urls=config['use_directory_urls']
    ))
    return files

def get_post_url(file: File, config: config_options.Config) -> Optional[str]:
    if not file.url.startswith("posts/"):
        return None
    
    docs_root = Path(config['docs_dir'])
    date, is_draft = get_post_meta(docs_root / file.src_path)
    if date is None:
        raise ValueError(f"Date is not found at post '{file.src_path}'.")
    if is_draft and not is_serving:
        return None

    return date + "/" + file.name

def get_post_meta(file_path: Path) -> Tuple[Optional[str], bool]:
    text = file_path.read_text(encoding='utf-8-sig')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if not match:
        return None, False

    meta = yaml.safe_load(match.group(1)) or {}
    date = meta.get('date')
    if isinstance(date, dict):
        date = date.get('created')

    if date:
        date = parse_date(str(date)).strftime("%Y/%m/%d")

    is_draft = bool(meta.get('draft'))
    return date, is_draft
