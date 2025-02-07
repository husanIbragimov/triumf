from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['POST'])
def update_picture(request, *args, **kwargs):
    try:
        courier = request.user.courier
        image = request.FILES.get('image')
        courier.avatar = image
        courier.save()
        return Response({
            "image": courier.avatar.url
        }, status=200)
    except Exception as e:
        return Response({'message': f'{e}'})
