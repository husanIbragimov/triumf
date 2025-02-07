from rest_framework import serializers

from apps.organization.models import Courier


class CourierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['id', 'full_name', 'avatar', 'phone']


class CourierLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'
