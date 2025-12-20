from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from blog.models import Post, Category
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import Http404
from studio.models import Gallery
from shop.models import Product


def home(request):
    homepage_gallery = (
        Gallery.objects.filter(published=True).prefetch_related("images").first()
    )

    homepage_images = (
        homepage_gallery.images.filter(published=True).order_by("order", "id")[:6]
        if homepage_gallery
        else None
    )

    featured_products = Product.objects.filter(
        is_active=True, featured=True, status__in=["publish", "soon", "full"]
    ).order_by("order", "-created")[:4]

    return render(
        request,
        "core/home.html",
        {
            "homepage_gallery": homepage_gallery,
            "homepage_images": homepage_images,
            "featured_products": featured_products,
        },
    )


def handler500(request):
    return render(request, "error/500.html", status=500)


def handler403(request, exception):
    return render(request, "error/403.html", status=403)


def handler404(request, exception):
    # Define which category to show (by slug)
    category_slug = "reflections"  # Change this to your desired category slug

    try:
        # Try to get the category
        category = get_object_or_404(Category, slug=category_slug)

        # Get posts from the category
        category_posts = Post.objects.filter(
            category=category, status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:4]

    except Http404:
        # Fallback to recent posts if category doesn't exist
        category_posts = Post.objects.filter(
            status="published", publish_date__lte=timezone.now()
        ).order_by("-publish_date")[:6]
        category = None

    context = {"category_posts": category_posts, "selected_category": category}

    return render(request, "error/404.html", context, status=404)


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
        "Disallow: /checkout/",
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
        "# todiane.com - portfolio projects by Django developer and creator of mini-ecommerce site builder - Diane Corriette.",
        "# It demonstrates best practices in ecommerce,offline-first,AI-search-ready design and ethical tech visibility.",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
