from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.PortfolioListView.as_view(), name="list"),
    path("<slug:slug>/", views.PortfolioDetailView.as_view(), name="detail"),
    path(
        "technology/<slug:slug>/", views.portfolio_by_technology, name="by_technology"
    ),
]
