from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_title = "Recoco-sync administration"
admin.site.site_header = f"Recoco-sync administration ({settings.ENVIRONMENT})"
admin.site.index_title = "Recoco-sync administration"


urlpatterns = [
    path("", include("recoco_sync.main.urls")),
    path("admin/", admin.site.urls),
]

if settings.ENVIRONMENT == "dev":
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
