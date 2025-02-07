from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import mixins, viewsets, filters, generics, status
from django.contrib.auth.password_validation import validate_password
from api.dashboard.account.serializers import AdminCreateSerializer
from rest_framework.parsers import FormParser, MultiPartParser
from django_filters.rest_framework import DjangoFilterBackend
from apps.letter.tasks import createpdf, generate_pdf_items
from .signals import make_letter_status_response_excel
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from apps.account.models import Admin
from apps.letter.models import Letter
from django.http import HttpResponse
from django.db.models import Q
from io import BytesIO
import pandas as pd

from api.dashboard.organization.serializers import OrganizationListSerializer, OrganizationCreateSerializer, \
    CourierListSerializer, CourierCreateSerializer, InComeOrganizationListSerializer, \
    InComeOrganizationCreateSerializer, InComeCourierListSerializer, InComeCourierCreateSerializer, \
    UpLoadLetterExcelListSerializer, AdeleSerializer, OrganizationPatchSerializer, UploadLetterPDFListSerializer, \
    RegisterSerializer, PersonalUserSerializer
from apps.organization.models import Organization, Courier, InComeOrganization, InComeCourier, UpLoadLetterExcel, Adele, \
    UploadLetterPDF, User
from datetime import datetime


class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = PersonalUserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    search_fields = ['username', 'first_name', 'last_name']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def create(self, request, *args, **kwargs):
        password = request.data.get('password')
        password2 = request.data.get('password2')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if password != password2:
            raise Response({'password': 'Password must match.'}, status=status.HTTP_400_BAD_REQUEST)

        validate_password(password)
        password = make_password(password)

        user = User.objects.create(username=username, first_name=first_name, last_name=last_name, password=password,
                                   role='Person')
        return Response({'msg': 'User created'}, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            return User.objects.filter(
                Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
        return User.objects.all()

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        user = User.objects.filter(id=user.id).first()
        password = request.data.get('password')
        password2 = request.data.get('password2')
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if password != password2:
            raise Response({'password': 'Password must match.'}, status=status.HTTP_400_BAD_REQUEST)

        if password:
            validate_password(password)
            password = make_password(password)
            user.password = password

        if username:
            user.username = username

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        user.save()
        return Response({'msg': 'User updated'}, status=status.HTTP_200_OK)


class AdeleListCreateView(generics.ListCreateAPIView):
    queryset = Adele.objects.all()
    serializer_class = AdeleSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization']


class AdeleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Adele.objects.all()
    serializer_class = AdeleSerializer
    parser_classes = (MultiPartParser, FormParser)


class OrganizationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                          mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = OrganizationListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'inn', 'incomes']
    search_fields = ['name']
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Organization.objects.all().select_related('user').order_by('-id')

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return OrganizationCreateSerializer
        if self.action == 'partial_update':
            return OrganizationPatchSerializer
        return OrganizationListSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class InComeOrganizationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                                mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = InComeOrganizationListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'is_paid', 'organization', 'created_at']
    search_fields = ['name', 'created_at__year']

    def get_queryset(self):
        return InComeOrganization.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return InComeOrganizationCreateSerializer
        return InComeOrganizationListSerializer


class CourierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = CourierListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id']
    search_fields = ['phone']

    def get_queryset(self):
        return Courier.objects.filter(is_active=True).order_by('full_name')

    def get_serializer_class(self):
        if self.action == 'list':
            return CourierListSerializer
        return CourierCreateSerializer


class InComeCourierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = InComeCourierListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id']
    search_fields = ['name']

    def get_queryset(self):
        return InComeCourier.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return InComeCourierCreateSerializer
        return InComeCourierListSerializer


class UpLoadLetterExcelViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    serializer_class = UpLoadLetterExcelListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'organization']
    search_fields = ['name']

    def get_permissions(self):
        if self.action == 'generate_excel':
            return [AllowAny(), ]
        else:
            return [IsAuthenticated(), ]

    def create(self, request, *args, **kwargs):
        excel_file = request.FILES.get('excel_file')
        organization_id = request.data.get('organization')
        district_id = request.data.get('district_id')
        letter = UpLoadLetterExcel.objects.create(excel_file=excel_file, name='procceesing',
                                                  organization_id=organization_id)
        header = ['Address', 'StreetNumber', 'FullName', 'ID', 'Own', 'Date', 'Inspector',
                  'OfficePhone', 'MobilPhone']
        try:
            df = pd.read_excel(excel_file)

        except Exception as errors:
            letter.status = 'failed'
            letter.save()
            return Response("{'msg':'Excel faylni ochib bo'lmadi iltimos faylni tekshirib ko'ring!'}",
                            status=status.HTTP_404_NOT_FOUND)
        if df.columns.to_list() == header:
            path_site = 'https://api.triumf-express.uz/'
            url_excel = letter.excel_file.url
            count = UpLoadLetterExcel.objects.filter(created_at__date=letter.created_at,
                                                     organization__id=organization_id).select_related("organization").count()
            name = letter.created_at.strftime("%d-%m-%Y") + ' (' + str(count) + ')'
            letter.name = name
            letter.save()
            createpdf.delay(letter.id, url_excel[1:], organization_id, path_site, district_id, header)
            return Response("{'msg':'Excel qabul qilindi!'}", status=status.HTTP_201_CREATED)
        else:
            letter.status = 'failed'
            letter.save()
            return Response("{'msg':'Excel shablon bir xil emas!'}", status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        make_letter_status_response_excel(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @permission_classes([AllowAny, ])
    @action(detail=True, methods=['get'])
    def generate_excel(self, request, pk=None):
        instance = self.get_object()
        letters = Letter.objects.filter(upload_file=instance).select_related("upload_file", "courier", "reason")
        letters_data = []
        for letter in letters:
            letter_data = {
                "Address": f"{letter.address}",
                "Name": f"{letter.name}",
                "Date": f"{letter.updated_at.date()}",
                "Status": f"{letter.status}",
                "ID": letter.personal_id if letter.personal_id else '',
                "Courier": f"{letter.courier.full_name}" if letter.courier else None,
                "Reason": f"{letter.reason.name}" if letter.reason else None,

            }
            letters_data.append(letter_data)
        df = pd.DataFrame(letters_data)
        output = BytesIO()
        df.to_excel(output, sheet_name='Sheet1', index=False)
        output.seek(0)  # Move the cursor to the beginning of the BytesIO object
        response = HttpResponse(output.read(),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={instance.name}_{datetime.now()}.xlsx'
        return response

    def get_queryset(self):

        return UpLoadLetterExcel.objects.filter(status="finished").order_by('-id')

    # def get_serializer_class(self):
    #     if self.action == 'create':
    #         return InComeCourierCreateSerializer
    #     return InComeCourierListSerializer


class UploadLetterPDFViewSet(viewsets.ModelViewSet):
    serializer_class = UpLoadLetterExcelListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id', 'organization']
    search_fields = ['name']

    def get_queryset(self):
        return UploadLetterPDF.objects.all().select_related("organization").order_by('-id')

    def create(self, request, *args, **kwargs):
        try:
            zip_file = request.FILES.get('zip_file')
            organization_id = request.data.get('organization')
            district_id = request.data.get('district_id')
            upload_zip = UploadLetterPDF.objects.create(zip_file=zip_file, name='processing',
                                                        organization_id=organization_id)
            path_site = 'https://api.triumf-express.uz'
            url_zip = upload_zip.zip_file.url
            count = UploadLetterPDF.objects.filter(created_at__date=upload_zip.created_at,
                                                   organization__id=organization_id).count()
            name = upload_zip.created_at.strftime("%d-%m-%Y") + ' (' + str(count) + ')'
            upload_zip.name = name
            upload_zip.save()
            print("sent to celery")
            generate_pdf_items(url_zip[1:], upload_zip.id, organization_id, path_site, district_id)
            return Response({'msg': 'Zip qabul qilindi!', 'zip': url_zip}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'msg': 'Zip qabul qilinmadi!', 'error_log': str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request, *args, **kwargs):
    user = request.user

    if user.role == 'Organization':
        org = Organization.objects.filter(inn=user.username).first()
        org_data = OrganizationCreateSerializer(org).data
        return Response(
            {
                'user': org_data,
                'role': 'Organization'
            }
        )
    if user.role == 'Admin':
        admin = Admin.objects.filter(phone=user.username).first()
        admin_data = AdminCreateSerializer(admin).data
        return Response(
            {
                'user': admin_data,
                'role': 'Admin'
            }
        )
    if user.role == 'Person':
        person = User.objects.filter(username=user.username).first()
        person_data = PersonalUserSerializer(user).data
        return Response(
            {
                'user': person_data,
                'role': 'Person'
            }
        )
    return Response(
        {
            'status': False,
            'msg': 'not fount permission user, user neither admin, organization'
        }
    )
