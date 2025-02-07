from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from api.dashboard.account.views import AdminViewSet, ContactListCreateView, login

router = DefaultRouter()
router.register('admins', AdminViewSet, basename='admins')

urlpatterns = router.urls + [
    path('login/', obtain_jwt_token),
    path('signin/', login),
    path('contact/', ContactListCreateView.as_view()),
]
