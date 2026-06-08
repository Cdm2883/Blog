def get_rss_created_date(meta):
    date = meta.get("date")
    if isinstance(date, dict):
        return date.get("created")
    return date


def get_rss_updated_date(meta):
    date = meta.get("date")
    if isinstance(date, dict):
        return date.get("updated")
    return None


def on_page_markdown(markdown, page, config, files, **kwargs):
    created = get_rss_created_date(page.meta)
    updated = get_rss_updated_date(page.meta)

    if created and not page.meta.get("rss_date_created"):
        page.meta["rss_date_created"] = created

    if updated and not page.meta.get("rss_date_updated"):
        page.meta["rss_date_updated"] = updated

    return markdown
