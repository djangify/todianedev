from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, render
from .models import Portfolio, Technology


class JSONLDMixin:
    """Reusable mixin for injecting JSON-LD structured data."""

    def get_jsonld(self, context):
        return {}

    def render_jsonld(self, context):
        import json
        from django.utils.safestring import mark_safe

        data = self.get_jsonld(context)
        if not data:
            return ""
        return mark_safe(
            f'<script type="application/ld+json">{json.dumps(data, indent=2)}</script>'
        )


class PortfolioListView(ListView):
    model = Portfolio
    template_name = "portfolio/portfolio_list.html"
    context_object_name = "portfolios"

    def get_queryset(self):
        return Portfolio.objects.filter(status="published").order_by(
            "order", "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["technologies"] = Technology.objects.all()
        return context


class PortfolioDetailView(JSONLDMixin, DetailView):
    model = Portfolio
    template_name = "portfolio/portfolio_detail.html"
    context_object_name = "portfolio"

    def get_queryset(self):
        return Portfolio.objects.filter(status="published")

    def get_jsonld(self, context):
        """Generate CreativeWork schema for this project."""
        project = self.get_object()
        links = [
            url
            for url in [project.live_site_url, project.github_url, project.for_sale_url]
            if url
        ]
        return {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": project.title,
            "description": project.short_description,
            "url": self.request.build_absolute_uri(),
            "image": project.display_image,
            "author": {"@type": "Person", "name": "Diane Corriette"},
            "datePublished": project.created_at.isoformat(),
            "sameAs": links,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jsonld"] = self.render_jsonld(context)
        return context


def portfolio_by_technology(request, slug):
    technology = get_object_or_404(Technology, slug=slug)
    portfolios = Portfolio.objects.filter(
        technologies=technology, status="published"
    ).order_by("order", "-created_at")

    return render(
        request,
        "portfolio/portfolio_by_technology.html",
        {"technology": technology, "portfolios": portfolios},
    )
