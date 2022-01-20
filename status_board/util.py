def chunks(it, chunk_size):
    lst = list(it)
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def pager(client, name, item_key, **kwargs):
    paginator = client.get_paginator(name)
    for page in paginator.paginate(**kwargs):
        for item in page[item_key]:
            yield item
