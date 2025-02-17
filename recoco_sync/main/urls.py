from __future__ import annotations

from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from ninja import NinjaAPI

from .views import router

api = NinjaAPI(
    title="Recoco-Sync API",
    version="1.0.0",
    description="Recoco-Sync API",
    openapi_url="/openapi.json",
    docs_url="/docs",
    urls_namespace="api",
)

api.add_router("", router)

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    path("api/", api.urls),
]
