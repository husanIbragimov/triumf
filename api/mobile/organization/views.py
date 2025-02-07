from django.contrib.auth import authenticate
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from api.mobile.organization.serializers import CourierLoginSerializer
from apps.account.models import User

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


@api_view(['POST'])
@permission_classes([AllowAny])
def start_login(request, *args, **kwargs):
    try:
        username = request.data['phone']
        if username:
            user = User.objects.filter(username=username).exists()

            if user:
                return Response({
                    "msg": "success",
                    'username': username,
                }, status=200)
            else:
                return Response({
                    'msg': 'Not found user'
                }, status=404)
        return Response({
            'msg': "Empty username field"
        }, status=404)
    except Exception as e:
        return Response({'error': f'{e}'})


@api_view(['POST'])
@permission_classes([AllowAny])
def finish_login(request, *args, **kwargs):
    try:

        username = request.data['username']
        password = request.data['password']

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)

                return Response({
                    'token': token,
                    'user': CourierLoginSerializer(user.courier, many=False).data,
                }, status=200)
            else:
                return Response({
                    'msg': 'Not found user'
                }, status=401)

        return Response({
            'msg': "Empty username or password fields"
        }, status=404)
    except Exception as e:
        return Response({'error': f'{e}'}, status=401)
