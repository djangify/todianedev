from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Post
from portfolio.models import Portfolio
from shop.models import Product, Category as ShopCategory
from infopages.models import InfoPage


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:ai_search",
            "core:independent_software",
        ]

    def location(self, item):
        return reverse(item)


class StudioSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return [
            "studio:index",
            "studio:products_index",
            "studio:bookkeeping",
            "studio:ecommerce_builder",
            "studio:invoice_generator",
            "studio:pdf_products",
            "studio:creative_coding",
            "studio:sites_index",
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


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


class ShopCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ShopCategory.objects.all()


class InfoPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return InfoPage.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated if hasattr(obj, "updated") else None


sitemaps = {
    "static": StaticSitemap,
    "studio": StudioSitemap,
    "blog": BlogSitemap,
    "portfolio": PortfolioSitemap,
    "products": ProductSitemap,
    "shop_categories": ShopCategorySitemap,
    "infopages": InfoPageSitemap,
}
