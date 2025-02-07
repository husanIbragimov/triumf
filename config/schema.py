from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .generator import BothHttpAndHttpsSchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="TRIUMF API",
        default_version="v1",
        description="TRIUMF official site documentations",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="lazy.devsloper@gmail.com"),
      license=openapi.License(name="BSD License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)
swagger_urlpatterns = [
    re_path(
        r"^triumf-swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^triumf-swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^triumf-redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]