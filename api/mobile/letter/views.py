from django.db.models import Q
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import permission_classes, api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.mobile.letter.serializers import LetterSerializer, LetterDistrictSerializer, LetterQuarterSerializer, \
    LetterListSerializer, ReasonSerializer, BoneSerializer
from apps.letter.models import Letter, Reason


class LetterViewSet(viewsets.ModelViewSet):
    serializer_class = LetterDistrictSerializer
    ordering_fields = ['created_at']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['id']
    search_fields = ['phone']

    def get_queryset(self):
        return Letter.objects.all().select_related("upload_file", "reason", "courier").order_by('-id')

    def get_serializer_class(self):
        if self.action == 'create':
            return LetterSerializer
        return LetterDistrictSerializer

    @action(methods=['get'], detail=False)
    def get_districts(self, request):
        courier = request.user.courier
        districts = Letter.objects.filter(parent__isnull=True)
        serializers = LetterDistrictSerializer(districts, many=True, context={'courier': courier})
        return Response(serializers.data)

    @action(methods=['get'], detail=False)
    def get_letters(self, request):
        district_id = request.GET.get('district')
        status = request.GET.get('status')
        date = request.GET.get('date', None)
        courier = request.user.courier
        letters = Letter.objects.filter(parent_id=district_id, courier=courier, status=status).select_related("courier", "reason", "upload_file").order_by('-updated_at')

        if date is not None:
            letters = Letter.objects.filter(parent_id=district_id, courier=courier, status=status, created_at__lte=date).select_related("courier", "reason", "upload_file")

        letters_count = Letter.objects.filter(~Q(status='process'), parent_id=district_id, courier=courier).select_related("courier").count()
        process_letters_count = Letter.objects.filter(Q(status=status), parent_id=district_id,
                                                      courier=courier).select_related("courier").count()
        finished_letters_count = Letter.objects.filter(Q(status=status), parent_id=district_id,
                                                       courier=courier).select_related("courier").count()
        serializers = LetterListSerializer(letters, many=True, context={'courier': courier})

        real_data = dict(
            card=None,
            letters=None
        )
        real_data['letters'] = serializers.data.copy()

        try:
            if letters.exists():
                real_data['card'] = {
                    "count": letters_count,
                    "process_letters_count": process_letters_count,
                    "summa": finished_letters_count * courier.price,
                    "date": letters.last().updated_at,
                }
            return Response(real_data)

        except Exception as e:
            return Response({"msg": "Something went wrong", "error": f"{e}"}, status=500)

    @action(methods=['get'], detail=False)
    def get_history(self, request):
        status = request.GET.get('status')
        date = request.GET.get('date', None)
        courier = request.user.courier
        month = now().month
        letters = Letter.objects.filter(courier=courier, status=status, created_at__month=month).select_related("courier")
        if date is not None:
            letters = Letter.objects.filter(courier=courier, status=status, created_at__date=date).select_related("courier")
        letters_count = Letter.objects.filter(~Q(status='archived'), courier=courier).select_related("courier").count()
        process_letters_count = Letter.objects.filter(Q(status='process'),
                                                      courier=courier).select_related("courier").count()
        finished_letters_count = Letter.objects.filter(Q(status='finish'),
                                                       courier=courier).select_related("courier").count()
        serializers = LetterListSerializer(letters, many=True, context={'courier': courier})
        real_data = dict(
            card=None,
            letters=None
        )
        real_data['letters'] = serializers.data.copy()
        try:
            if letters.exists():
                real_data['card'] = {
                    "count": letters_count,
                    "process_letters_count": process_letters_count,
                    "summa": finished_letters_count * courier.price,
                    "date": letters.last().updated_at,
                }
            return Response(real_data)

        except Exception as e:
            return Response({"msg": "Something went wrong", "error": f"{e}"}, status=500)

    @action(methods=['get'], detail=False)
    def get_details(self, request):
        letter_id = request.GET.get('id')
        letter = Letter.objects.get(id=letter_id)
        serializers = LetterListSerializer(letter)
        return Response(serializers.data, status=200)

    @action(methods=['post'], detail=False)
    def change_status_letter_list(self, request):
        letters_id = request.data.getlist('letters')
        status = request.data.get('status')
        reason = request.data.get('reason')
        letters = Letter.objects.filter(id__in=letters_id)
        image = request.FILES.get('image')

        for letter in letters:
            if reason != 'null':
                letter.reason_id = reason
            letter.image = image
            letter.status = status

            letter.save()

        return Response({
            "msg": "Success"
        }, status=200)

    @action(methods=['post'], detail=False)
    def update_letter(self, request):
        letter_id = request.data.get('id')
        reason = request.data.get('reason', None)
        letter = Letter.objects.filter(id=letter_id).first()
        image = request.FILES.get('image', None)

        if image is not None:
            letter.image = image
            letter.save()
        if reason is not None:
            letter.reason_id = reason
            letter.save()
        if image is None:
            return Response({
                "msg": "Image is None"
            }, status=400)
        return Response({
            "msg": "Success"
        }, status=200)


class ReasonViewSet(viewsets.ModelViewSet):
    serializer_class = ReasonSerializer
    queryset = Reason.objects.all().order_by('name')


@api_view(['POST'])
@permission_classes([AllowAny])
def create_querter(request, *args, **kwargs):
    name = request.data.get('name')
    serializer = LetterSerializer(data=name, many=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)
