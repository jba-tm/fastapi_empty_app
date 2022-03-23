# server/sitemap.py
import asgi_sitemaps
from app.conf.config import settings


class Sitemap(asgi_sitemaps.Sitemap):
    def items(self):
        return ["/"]

    def location(self, item: str):
        return item

    def changefreq(self, item: str):
        return "monthly"


sitemap = asgi_sitemaps.SitemapApp(Sitemap(), domain=settings.DOMAIN)
