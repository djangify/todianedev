import json
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_GET
from blog.models import Post, Category
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404


def home(request):
    return render(request, "core/home.html")


def handler500(request):
    return render(request, "error/500.html", status=500)


def handler403(request, exception):
    return render(request, "error/403.html", status=403)


def handler404(request, exception):
    category_slug = "reflections"

    try:
        category = get_object_or_404(Category, slug=category_slug)
        category_posts = Post.objects.filter(
            category=category, status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:4]
    except Http404:
        category_posts = Post.objects.filter(
            status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:6]
        category = None

    context = {"category_posts": category_posts, "selected_category": category}
    return render(request, "error/404.html", context, status=404)


@require_GET
def service_worker(request):
    """Serve the PWA service worker from the site root (required for full scope).

    The latest published posts are injected so they are cached at install time and
    can be read offline even if the visitor never opened them.
    """
    latest = (
        Post.objects.filter(status="published", publish_date__lte=timezone.now())
        .order_by("-publish_date")
        .values_list("slug", flat=True)[:10]
    )
    precache_pages = [reverse("blog:detail", args=[slug]) for slug in latest]

    return render(
        request,
        "pwa/sw.js",
        {"precache_pages": json.dumps(precache_pages)},
        content_type="application/javascript",
    )


@require_GET
def robots_txt(request):
    """Robots.txt for search + AI visibility."""
    site_url = request.build_absolute_uri("/").rstrip("/")
    sitemap_url = f"{site_url}/sitemap.xml"

    lines = [
        "# robots.txt for todiane.com",
        "# Enables modern search and AI engines to crawl public sections.",
        "",
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /media/private/",
        "",
        "# AI & Answer Engine Bots",
        "User-agent: GPTBot",
        "User-agent: ChatGPT-User",
        "User-agent: Google-Extended",
        "User-agent: ClaudeBot",
        "User-agent: PerplexityBot",
        "User-agent: anthropic-ai",
        "User-agent: Bingbot",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
        "",
        "# --- Brand Context ---",
        "# todiane.com - portfolio and writing by Django developer Diane Corriette.",
        "# Specialising in self-hosted, offline-first software and ecommerce tools.",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
