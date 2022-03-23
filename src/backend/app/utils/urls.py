from urllib.parse import urlsplit, parse_qs, urlencode
from starlette.datastructures import URL


def include_query_params(url: URL, query: dict) -> URL:
    # _url = urlsplit(url)
    # _query = parse_qs(_url.query)
    # _query.update(query)
    # querystr = urlencode(_query, doseq=True)
    return url.include_query_params(**query)


def prepare_url(params: str, redirect_url: str) -> str:
    """Add params to redirect url."""
    split_url = urlsplit(redirect_url)
    split_url = split_url._replace(query=params)
    return split_url.geturl()
