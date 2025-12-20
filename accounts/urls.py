# accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("support/", views.support, name="support"),
]
