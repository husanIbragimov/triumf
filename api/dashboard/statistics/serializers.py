from rest_framework import serializers
from apps.organization.models import Organization, InComeCourier, InComeOrganization
from apps.letter.models import Letter, UpLoadLetterExcel
from django.shortcuts import get_object_or_404
from datetime import datetime, date


class InComeOrganizationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InComeOrganization
        fields = '__all__'