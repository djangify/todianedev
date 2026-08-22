"""Add a "Claude connector" section to the admin sidebar (superusers only).

Rather than hard-coding theme HTML, we inject two links into the ``app_list``
the admin builds for every page, so the active theme (Adminita) renders them in
its own style — exactly like the built-in app sections. Safe to call once at
startup; calling it again is a no-op.
"""

from django.contrib import admin
from django.urls import NoReverseMatch, reverse


def install_sidebar_link():
    site = admin.site
    if getattr(site, "_mcp_sidebar_patched", False):
        return
    site._mcp_sidebar_patched = True

    original_get_app_list = site.get_app_list

    def get_app_list(request, app_label=None):
        app_list = list(original_get_app_list(request, app_label))

        # Fold the standalone "MCP Connector" app section (the MCP call log) into
        # a single owner-facing "Claude connector" section, so there is one place
        # for everything Claude-related instead of two.
        app_list = [a for a in app_list if a.get("app_label") != "mcp_server"]

        # Only the site owner (superuser) needs the connector controls, and only
        # on the full sidebar (app_label is None), not per-app pages.
        try:
            if app_label is None and getattr(request, "user", None) and request.user.is_superuser:
                models = []
                try:
                    models.append(
                        {
                            "name": "Connect to Claude",
                            "object_name": "connect_claude",
                            "admin_url": reverse("admin_connect_claude"),
                            "view_only": True,
                        }
                    )
                    models.append(
                        {
                            "name": "Claude connections",
                            "object_name": "claude_connections",
                            "admin_url": reverse("admin_claude_connections"),
                            "view_only": True,
                        }
                    )
                except NoReverseMatch:
                    models = []
                # The MCP call log lives under Claude connector too (was its own
                # "MCP Connector" section). Guarded so a missing model can't break
                # the sidebar.
                try:
                    models.append(
                        {
                            "name": "MCP call logs",
                            "object_name": "mcpcalllog",
                            "admin_url": reverse("admin:mcp_server_mcpcalllog_changelist"),
                            "view_only": True,
                        }
                    )
                except NoReverseMatch:
                    pass
                if models:
                    app_list.append(
                        {
                            "name": "Claude connector",
                            "app_label": "mcp_connector",
                            "app_url": reverse("admin_connect_claude"),
                            "has_module_perms": True,
                            "models": models,
                        }
                    )
        except Exception:
            # The sidebar link is cosmetic — never let it break the admin.
            pass

        # allauth's account app is also titled "Accounts", which collides with
        # this project's own "Accounts" app. Rename the allauth one (it only
        # holds Email addresses) so there is a single, unambiguous Accounts
        # section plus a clearly-labelled email one.
        try:
            for app in app_list:
                if app.get("app_label") == "account":
                    app["name"] = "Email verification"
        except Exception:
            pass

        # Alphabetise the whole sidebar: apps by name, and the models within each
        # app by name.
        try:
            for app in app_list:
                app.get("models", []).sort(key=lambda m: str(m.get("name", "")).lower())
            app_list.sort(key=lambda a: str(a.get("name", "")).lower())
        except Exception:
            pass

        return app_list

    site.get_app_list = get_app_list
