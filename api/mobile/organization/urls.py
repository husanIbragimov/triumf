from django.urls import path
from rest_framework.routers import DefaultRouter

from api.mobile.account.views import update_picture
from api.mobile.organization.views import start_login, finish_login

router = DefaultRouter()
# router.register('curiers', UserViewSet, basename='users')


urlpatterns = router.urls + [
    path('start-login/', start_login),
    path('finish-login/', finish_login),
]
