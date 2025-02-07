from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from api.mobile.account.views import update_picture
from api.mobile.letter.views import create_querter, LetterViewSet, ReasonViewSet

router = DefaultRouter()
# router.register('account', LetterViewSet, basename='account')


urlpatterns = router.urls + [
    path('update-picture/', update_picture)
]
