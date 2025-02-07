"""config URL Configuration

The `urlpatterns` list routes URLs to api. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function api
    1. Add an import:  from my_app import api
    2. Add a URL to urlpatterns:  path('', api.home, name='home')
Class-based api
    1. Add an import:  from other_app.api import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.static import serve
from .schema import swagger_urlpatterns
from django.conf.urls import handler404, handler400, handler403, handler500

schema_view = get_schema_view(
    openapi.Info(
        title="TRIUMF API",
        default_version='v1',
        description="TRIUMF official site documentations",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="ibragimovxusanofficial@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # files
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

    path('heyswagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # admin
    path('admin/', admin.site.urls),

    path('api/v1/', include('api.dashboard.urls.v1')),
    path('api/v1/', include('api.mobile.urls.v1')),

    path('api/v1/', include('apps.organization.api.web.urls')),

    path('', include('apps.letter.urls')),

    path('auth/', include('apps.account.urls')),

    # path('task/', add("files/MOCK_DATA.xlsx")),
] + swagger_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.STAGE == 'dev':
#     urlpatterns += [
#         path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#         path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
#     ]

handler404 = "config.errors.page_not_found_view"

# handler403 = "config.error_page.page_forbidden_view"
#
# handler500 = "config.error_page.page_server_error_view"
