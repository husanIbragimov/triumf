import datetime
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from api.dashboard.letter.serializers import BotSentArchivedLetterSerializer, LetterListSerializer, LetterCreateSerializer, DistrictListSerializer, \
    CreateLetterSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets, filters, generics, permissions as per
from rest_framework.pagination import PageNumberPagination

from api.dashboard.organization.serializers import UpLoadLetterExcelListSerializer
from apps.organization.models import UpLoadLetterExcel
from api.dashboard.letter.filters import LetterFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.letter.models import Letter
import pandas as pd


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LetterViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = LetterListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['id', 'upload_file__name', 'courier__id', 'status',
    #                     'upload_file__organization__id', 'upload_file']
    search_fields = ['name']
    filterset_class = LetterFilter
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return Letter.objects.all().select_related('courier', 'upload_file', 'reason').exclude(status='archived').order_by('-id')

    def get_serializer_class(self):
        if self.action == 'create':
            return LetterCreateSerializer
        if self.action == 'get_districts':
            return DistrictListSerializer
        # if self.action == 'get_letters':
        #     return LetterRootSerializer
        return LetterListSerializer

    def create(self, request, *args, **kwargs):
        org_id = request.data.get('organization')
        district_id = request.data.get('district_id')
        file = request.FILE.get('file')
        if org_id and district_id and file:
            upload_file = UpLoadLetterExcel.objects.create(organization=org_id, pdf_file=file, status="finished")
            letter = Letter.objects.create(upload_file=upload_file, status="new", parent=district_id)
        return Response({'message': "Success"}, status=status.HTTP_201_CREATED, )
    
    

    @action(detail=False, methods=['post'])
    def set_letters_courier(self, request):
        courier_id = request.data.get('courier_id')
        letter_ids = request.data.get('letter_ids')
        letters = Letter.objects.filter(id__in=letter_ids).select_related('courier')
        if letters:
            for letter in letters:
                letter.courier_id = int(courier_id)
                letter.status = "process"
                letter.save()

        return Response({'message': "Success"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def get_districts(self, request):
        districts = Letter.objects.filter(parent__isnull=True)
        serializer = self.get_serializer(districts, many=True)
        return Response(serializer.data, status=200)



class BotSentArchivedLettersView(generics.ListAPIView):
    queryset = Letter.objects.filter(status='archived').select_related('courier', 'upload_file', 'reason').order_by('-id')
    serializer_class = BotSentArchivedLetterSerializer
    permission_classes = [per.AllowAny]
    pagination_class = None


class CreateLetterView(generics.CreateAPIView):
    queryset = Letter.objects.all()
    serializer_class = CreateLetterSerializer
    # parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        data = request.data
        
        letter = get_object_or_404(Letter, id=data['id'])
        for child in data['children']:
            Letter.objects.create(name=child['name'], address=child['address'], pdf_file=child['pdf_file'],
                                  parent=letter, status='new')
        return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)
