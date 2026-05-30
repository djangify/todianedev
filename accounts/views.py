# accounts/views.py
# Public account views removed — this site is a showcase only.
# Django admin login is handled via /admin/. No public registration.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from allauth.account.models import EmailAddress

from .forms import ProfileForm
from .models import MemberResource


@login_required
def dashboard_view(request):
    return redirect("/admin/")


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
def delete_account_view(request):
    return redirect("/")


@login_required
def support(request):
    return redirect("/")
