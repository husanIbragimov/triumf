from django.urls import path, include

urlpatterns = [
    path('mobile/', include(('api.mobile.organization.urls', 'organization'))),
    path('mobile/', include(('api.mobile.account.urls', 'account'))),
    path('mobile/', include(('api.mobile.letter.urls', 'letter'))),

]
