from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from portfolio.models import Portfolio
from infopages.models import InfoPage


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:diane-corriette",
            "core:independent_software",
            "core:owning_your_platform",
        ]

    def location(self, item):
        return reverse(item)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else obj.created


class PortfolioSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Portfolio.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


class InfoPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return InfoPage.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


sitemaps = {
    "static": StaticSitemap,
    "blog": BlogSitemap,
    "portfolio": PortfolioSitemap,
    "infopages": InfoPageSitemap,
}
