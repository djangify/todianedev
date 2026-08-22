# accounts/views.py
# Customer account area for the shop (register/login are thin redirects to
# django-allauth; dashboard + wishlist are provided here).

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ProfileForm


# ---------------------------------------------------------------------------
# Auth entry points — the shop templates link to accounts:register / login /
# logout. We keep django-allauth as the single source of truth for the actual
# auth flow and simply forward to it, preserving any ?next= parameter.
# ---------------------------------------------------------------------------
def _with_next(target, request):
    nxt = request.GET.get("next")
    return f"{target}?next={nxt}" if nxt else target


def register_view(request):
    return redirect(_with_next(reverse("account_signup"), request))


def login_view(request):
    return redirect(_with_next(reverse("account_login"), request))


def logout_view(request):
    if request.method == "POST":
        auth_logout(request)
        return redirect("/")
    return redirect(reverse("account_logout"))


# ---------------------------------------------------------------------------
# Customer dashboard
# ---------------------------------------------------------------------------
@login_required
def dashboard_view(request):
    """Customer home: recent orders, purchased downloads and wishlist."""
    from shop.models import Order

    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created")
        .prefetch_related("items__product")[:10]
    )
    profile = getattr(request.user, "profile", None)
    favourites = (
        profile.favourite_products.all() if profile is not None else []
    )
    return render(
        request,
        "accounts/dashboard.html",
        {"orders": orders, "favourites": favourites},
    )


@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form, "user": user})


@login_required
@require_POST
def add_favourite_product(request, product_slug):
    """Toggle a product in the logged-in user's wishlist."""
    from shop.models import Product

    product = get_object_or_404(Product, slug=product_slug)
    profile = getattr(request.user, "profile", None)
    if profile is None:
        from .models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.favourite_products.filter(pk=product.pk).exists():
        profile.favourite_products.remove(product)
        messages.info(request, f"Removed “{product.title}” from your wishlist.")
    else:
        profile.favourite_products.add(product)
        messages.success(request, f"Saved “{product.title}” to your wishlist.")

    return redirect(request.META.get("HTTP_REFERER") or product.get_absolute_url())


@login_required
def delete_account_view(request):
    return redirect("/")


@login_required
def support(request):
    return redirect("/")
