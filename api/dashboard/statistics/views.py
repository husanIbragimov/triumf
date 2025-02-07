from apps.organization.models import Organization, InComeOrganization, InComeCourier
from api.dashboard.statistics.serializers import InComeOrganizationSerializer
from rest_framework import views, status, viewsets, generics
from apps.letter.models import Letter, UpLoadLetterExcel
from apps.organization.signals import make_in_come_org
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class StatisticsLetterViewSet(generics.ListAPIView):
    queryset = InComeOrganization.objects.all()
    serializer_class = InComeOrganizationSerializer

    def get_queryset(self):
        make_in_come_org()
        return self.queryset.all()
