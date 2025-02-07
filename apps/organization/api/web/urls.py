from django.urls import path
from .views import OrganizationFileUpload, OrganizationUploadFileInfo, LetterInfo, OrganizationForStatistic, \
    PartnerListCreateView, PartnerRetrieveUpdateDestroyView

urlpatterns = [
    path('file/upload', OrganizationFileUpload.as_view(), name='file_upload'),
    path('dashboard/upload/file/data/list/<int:id>', OrganizationUploadFileInfo.as_view(), name='file_data'),
    path('letter/info/<int:id>', LetterInfo.as_view(), name='letter_info'),
    # path('statistica', OrganizationForStatistic.as_view(), name='letter_info'),
    path('dashboard/partners', PartnerListCreateView.as_view(), name='partners'),
    path('dashboard/partners/<int:pk>/', PartnerRetrieveUpdateDestroyView.as_view(), name='partners'),
]
