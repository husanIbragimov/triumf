from django.db.models import Count
from rest_framework import serializers

from apps.letter.models import Letter, Reason


class LetterQuarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ['id', 'address', 'name']
        # fields = '__all__'

    def to_representation(self, instance):
        data = super(LetterQuarterSerializer, self).to_representation(instance)
        data['count'] = Letter.objects.filter(parent__id=instance.id,
                                              courier=self.context.get('courier')).count()
        return data


class LetterDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ['id', 'address', 'name']
        # fields = '__all__'

    def to_representation(self, instance):
        data = super(LetterDistrictSerializer, self).to_representation(instance)
        data['count'] = Letter.objects.filter(parent__id=instance.id, status="process",
                                              courier=self.context.get('courier')).count()
        return data


class LetterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        fields = ['id', 'name', 'receiver_name', 'address', 'image', 'description', 'status', 'created_at',
                  'is_delivered', 'reason']
        depth = 1

    def to_representation(self, instance):
        data = super(LetterListSerializer, self).to_representation(instance)
        data['address'] = f"{instance.parent.address}, {instance.address}"
        if instance.upload_file:
            data['organization'] = instance.upload_file.organization.name
        elif instance.upload_zip_file :
            data['organization'] = instance.upload_zip_file.organization.name
        else:
            data['organization'] = None
        return data


class LetterSerializer(serializers.ModelSerializer):
    upload_file = serializers.SerializerMethodField()

    def get_upload_file(self, obj):
        if obj.upload_file:
            return obj.upload_file
        return obj.upload_zip_file

    class Meta:
        model = Letter
        fields = ['id', 'name', 'receiver_name', 'address', 'personal_id', 'image', 'status', 'created_at', 'updated_at',
                  'parent', 'courier', 'upload_file', 'pdf_file', 'is_delivered', 'reason']


class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reason
        fields = ['id', 'name']


class ChildrenBoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letter
        exclude = ['lft', 'rght', ]


class BoneSerializer(serializers.ModelSerializer):
    children = ChildrenBoneSerializer(many=True)

    class Meta:
        model = Letter
        exclude = ['lft','rght',]