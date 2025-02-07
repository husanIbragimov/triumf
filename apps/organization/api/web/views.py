from .serializers import UpLoadLetterExcelSeriazliers, LetterListSerializer, PartnerSerializer
from rest_framework import response, serializers, status, views, generics, permissions
from apps.organization.models import Organization, UpLoadLetterExcel, Partner
from apps.organization.permissions import OrganizationPermission
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.letter.models import Letter
from django.shortcuts import render
from django.db.models import Q
from datetime import date


# Create your views here.

class OrganizationFileUpload(views.APIView):
    permission_classes = [OrganizationPermission, IsAuthenticated]

    def get(self, request):
        user = Organization.objects.filter(user=request.user).last()
        organization_file_info = UpLoadLetterExcel.objects.filter(organization=user)
        serializers_data = UpLoadLetterExcelSeriazliers(organization_file_info, many=True)
        return response.Response(serializers_data.data, status=status.HTTP_200_OK)

    def post(self, request):
        file_seriazliers = UpLoadLetterExcelSeriazliers(data=request.data)
        if file_seriazliers.is_valid():
            todays_date = date.today()
            file_name = f"{todays_date.day}.{todays_date.month}.{todays_date.year}"
            get_file_name_count = UpLoadLetterExcel.objects.filter(name__contains=file_name).count()
            if get_file_name_count != 0:
                file_name = f"{file_name}({get_file_name_count})"
            user = Organization.objects.filter(user=request.user).last()
            file_seriazliers.save(organization=user, name=file_name)
            return response.Response(file_seriazliers.data, status=status.HTTP_201_CREATED)
        else:
            return response.Response(file_seriazliers.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationUploadFileInfo(views.APIView):
    permission_classes = [OrganizationPermission, IsAuthenticated]

    def get(self, request, id):
        file_data = get_object_or_404(UpLoadLetterExcel, id=id)
        letters = Letter.objects._mptt_filter(upload_file=file_data)
        letters_serializers = LetterListSerializer(letters, many=True)
        return response.Response(letters_serializers.data, status=status.HTTP_200_OK)


class LetterInfo(views.APIView):
    permission_classes = [OrganizationPermission, IsAuthenticated]

    def get(self, request, id):
        letters = Letter.objects._mptt_filter(id=id)
        if letters.count() == 0:
            return response.Response({'message': 'Letter not found'}, status=status.HTTP_404_NOT_FOUND)
        letters_serializers = LetterListSerializer(letters, many=True)
        return response.Response(letters_serializers.data, status=status.HTTP_200_OK)


class OrganizationForStatistic(views.APIView):
    permission_classes = [OrganizationPermission, IsAuthenticated]

    def get(self, request):
        month_dict = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
        }
        statistic_info = {}
        price_letter = get_object_or_404(Organization, user=request.user).price
        for month in range(1, 13):
            info_data = {}
            file_get = UpLoadLetterExcel.objects.filter(created_at__month=month)
            if file_get != 0:
                count_letter = 0
                finished_letter = 0
                for file in file_get:
                    print(file)
                    count_letter = count_letter + file.letters.count()
                    finished_letter += Letter.objects._mptt_filter(status='finish').count()
                info_data['all_letter'] = count_letter
                info_data['finished_letter'] = finished_letter
                info_data['total_price'] = count_letter * price_letter

                statistic_info[month_dict[month]] = info_data
            else:
                info_data['all_letter'] = 0
                info_data['finished+letter'] = 0
                info_data['total_price'] = 0

                statistic_info[month_dict[month]] = info_data
        return response.Response(statistic_info, status=status.HTTP_200_OK)


class PartnerListCreateView(generics.ListCreateAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.AllowAny]


class PartnerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"
