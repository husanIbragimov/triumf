from django.urls import path, include
from api.dashboard.organization.views import profile
urlpatterns = [
    path('dashboard/', include(('api.dashboard.account.urls', 'admins'))),
    path('dashboard/', include(('api.dashboard.organization.urls', 'organizations'))),
    path('dashboard/', include(('api.dashboard.letter.urls', 'letter'))),
    path('profile/', profile)


]
