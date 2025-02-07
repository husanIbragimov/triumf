from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins, viewsets, filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from api.dashboard.account.serializers import AdminCreateSerializer, AdminListSerializer, ContactSerializer
from apps.account.models import User, Admin, Contact

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class AdminViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = AdminListSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id']
    search_fields = ['phone']

    def get_queryset(self):
        return Admin.objects.all()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return AdminCreateSerializer
        return AdminListSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request, *args, **kwargs):
    username = request.data['phone']
    password = request.data['password']

    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'token': token,
                'user_role': user.role
                # 'user': UserListSerializer(user, many=False).data,
            }, status=200)
        else:
            return Response({
                'msg': 'Not found user'
            }, status=404)

    return Response({
        'msg': "Empty username or password fields"
    }, status=400)


class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
