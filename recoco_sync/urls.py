from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_title = "Recoco-sync administration"
admin.site.site_header = f"Recoco-sync administration ({settings.ENVIRONMENT})"
admin.site.index_title = "Recoco-sync administration"


urlpatterns = [
    path("", include("main.urls")),
    path("admin/", admin.site.urls),
]
