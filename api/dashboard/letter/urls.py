from django.urls import path
from rest_framework.routers import DefaultRouter

from api.dashboard.letter.views import LetterViewSet, CreateLetterView

router = DefaultRouter()
router.register('letters', LetterViewSet, basename='letters')

urlpatterns = router.urls + [
    # path('create-letter/', CreateLetterView.as_view())
]
