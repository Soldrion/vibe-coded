def filter_items(items, query):
    query = query.lower()
    return [item for item in items if query in item.name.lower() or any(query in tag.lower() for tag in item.tags)]
