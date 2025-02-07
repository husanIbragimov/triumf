from apps.organization.models import UpLoadLetterExcel
from rest_framework import serializers
from apps.letter.models import Letter
from apps.organization.models import Partner


class UpLoadLetterExcelSeriazliers(serializers.ModelSerializer):
    class Meta:
        model = UpLoadLetterExcel
        fields = "__all__"


class LetterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = '__all__'


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'
