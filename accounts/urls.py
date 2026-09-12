# accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Auth entry points used by the shop templates (forward to allauth).
    path("register/", views.register_view, name="register"),
    path("signin/", views.login_view, name="login"),
    path("signout/", views.logout_view, name="logout"),
    # Customer area
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "wishlist/<slug:product_slug>/",
        views.add_favourite_product,
        name="add_to_wishlist",
    ),
    path("delete-account/", views.delete_account_view, name="delete_account"),
    path("support/", views.support, name="support"),
    # Saved tool results
    path("saved-results/<int:pk>/", views.saved_result_detail, name="saved_result_detail"),
    path("saved-results/<int:pk>/rename/", views.saved_result_rename, name="saved_result_rename"),
    path("saved-results/<int:pk>/delete/", views.saved_result_delete, name="saved_result_delete"),
]
