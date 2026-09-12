from django.urls import path

from . import views

app_name = "tools"

urlpatterns = [
    path("", views.tool_list, name="list"),
    # Specific suffixes must come before the generic slug so they resolve first.
    path("<slug:slug>/raw/", views.tool_raw, name="raw"),
    path("<slug:slug>/email-results/", views.email_results, name="email_results"),
    path("<slug:slug>/save/", views.save_result, name="save_result"),
    path("<slug:slug>/", views.tool_detail, name="detail"),
]
