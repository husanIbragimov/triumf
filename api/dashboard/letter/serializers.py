from rest_framework import serializers

from api.dashboard.organization.serializers import CourierListSerializer, UpLoadLetterExcelListSerializer
from apps.letter.models import Letter
from apps.organization.models import UpLoadLetterExcel


class LetterListSerializer(serializers.ModelSerializer):
    courier = serializers.CharField(source="courier.full_name", read_only=True)
    organization = serializers.SerializerMethodField()
    reason = serializers.CharField(source='reason.name', read_only=True)

    def get_organization(self, obj):
        org = None
        if obj.upload_file:
            # Agar upload_file mavjud bo'lsa, upload_zip_file-ni upload_file dan olish
            org = obj.upload_file.organization.name
        elif obj.upload_zip_file:
            org = obj.upload_zip_file.organization.name
        else:
            org = 1
        return org
            
            

    class Meta:
        model = Letter
        fields = (
            "id", "name", "receiver_name", "address", "image", "pdf_file", "description", "status", "created_at",
            "updated_at", "parent", "courier", "upload_file", 'organization', 'upload_zip_file', "reason", "is_delivered",
        )


class LetterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = '__all__'  # ['id', 'full_name', 'avatar', 'phone']


class DistrictListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Letter
        fields = ('id', 'name')  # ['id', 'full_name', 'avatar', 'phone']


class LetterGetSerializer(serializers.ModelSerializer):
    courier = serializers.CharField(source='courier.full_name', read_only=True)
    reason = serializers.CharField(source="reason.name", read_only=True)
    upload_file = serializers.SerializerMethodField()

    def get_upload_file(self, obj):
        if obj.upload_file:
            return obj.upload_file
        return obj.upload_zip_file

    class Meta:
        model = Letter
        fields = (
            "id", "name", "receiver_name", "address", "image", "pdf_file", "description", "status", "created_at",
            "updated_at", "parent", "courier", "upload_file", 'upload_zip_file', "reason", "is_delivered",
        )


class LetterRootSerializer(serializers.ModelSerializer):
    children = LetterGetSerializer(many=True)

    class Meta:
        model = Letter
        fields = (
            'id',
            'name',
            'address',
            'status',
            'children'
        )

class BotSentArchivedLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = (
            "id", "name", "address", "image", "pdf_file", "status", "created_at",
            "updated_at", "courier", "upload_file", 'upload_zip_file', "reason", "is_delivered", 'personal_id')


class CreateChildrenLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = (
            'id',
            'name',
            'address',
            'pdf_file',
            'parent',
        )


class CreateLetterSerializer(serializers.ModelSerializer):
    children = CreateChildrenLetterSerializer(many=True)

    class Meta:
        model = Letter
        fields = ('id', 'children',)
