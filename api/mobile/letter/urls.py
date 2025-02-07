from django.urls import path
from rest_framework.routers import DefaultRouter

from api.mobile.letter.views import create_querter, LetterViewSet, ReasonViewSet

router = DefaultRouter()
router.register('letters', LetterViewSet, basename='letters')
router.register('reasons', ReasonViewSet, basename='reasons')

urlpatterns = router.urls + [
    path('create-querter/', create_querter)
]
