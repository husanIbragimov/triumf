from django.urls import path
from rest_framework.routers import DefaultRouter

from api.dashboard.organization.views import OrganizationViewSet, InComeOrganizationViewSet, CourierViewSet, \
    InComeCourierViewSet, UpLoadLetterExcelViewSet, AdeleListCreateView, AdeleRetrieveUpdateDestroyAPIView, UploadLetterPDFViewSet, \
    RegisterViewSet, UserViewSet
from apps.organization.api.web.views import OrganizationFileUpload, OrganizationUploadFileInfo, LetterInfo, \
    OrganizationForStatistic

router = DefaultRouter()
router.register('register', RegisterViewSet, basename='register')
router.register('user', UserViewSet, basename='user')
router.register('organizations', OrganizationViewSet, basename='organizations')
router.register('income-organizations', InComeOrganizationViewSet, basename='income-organizations')
router.register('couriers', CourierViewSet, basename='couriers')
router.register('income-couriers', InComeCourierViewSet, basename='income-couriers')
router.register('upload-letter-excel', UpLoadLetterExcelViewSet, basename='upload-letter-excel')
router.register('upload-letter-pdf', UploadLetterPDFViewSet, basename='upload-letter-pdf')

urlpatterns = router.urls + [
    path('adele/', AdeleListCreateView.as_view()),
    path('adele/<int:pk>/', AdeleRetrieveUpdateDestroyAPIView.as_view()),

    path('file/upload', OrganizationFileUpload.as_view(), name='file_upload'),
    path('upload/file/data/list/<int:id>', OrganizationUploadFileInfo.as_view(), name='file_data'),
    path('letter/info/<int:id>', LetterInfo.as_view(), name='letter_info'),
    path('statistica', OrganizationForStatistic.as_view(), name='letter_info'),
]
