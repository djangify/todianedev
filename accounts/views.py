# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from allauth.account.models import EmailAddress
from shop.models import WishList

from .forms import SupportForm
from .models import MemberResource
from shop.models import OrderItem


@login_required
def dashboard_view(request):
    user = request.user

    # Check email verification via allauth
    is_verified = EmailAddress.objects.filter(
        user=user,
        verified=True,
    ).exists()

    if not is_verified:
        messages.warning(
            request, "Please verify your email address to access all features."
        )

    purchased_count = (
        OrderItem.objects.filter(order__user=user).values("product").distinct().count()
    )

    member_resources = MemberResource.objects.filter(is_active=True)

    # ✅ WISHLIST DATA (THIS WAS MISSING)
    wishlist_items = WishList.objects.filter(user=user).select_related("product")

    favourite_products = [item.product for item in wishlist_items]

    context = {
        "is_verified": is_verified,
        "purchased_count": purchased_count,
        "member_resources": member_resources,
        "favourite_products": favourite_products,  # ✅ REQUIRED
    }

    return render(request, "accounts/dashboard.html", context)


# -------------------------
# Support
# -------------------------
@login_required
def support(request):
    user = request.user

    if request.method == "POST":
        form = SupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = user
            support_request.save()
            messages.success(
                request,
                "Thanks — your message has been sent. We'll get back to you soon.",
            )
            return redirect("accounts:support")
    else:
        form = SupportForm()

    context = {
        "form": form,
        "user_name": user.get_full_name() or user.first_name or "Member",
        "user_email": user.email,
    }

    return render(request, "accounts/support.html", context)
