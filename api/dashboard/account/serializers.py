from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.account.models import Admin, User, Contact


class AdminCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    avatar = serializers.FileField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(required=True)

    class Meta:
        model = Admin
        fields = ['id', 'full_name', 'avatar', 'phone', 'password', 'is_organizations', 'is_courier', 'is_statistic',
                  'is_incomes', 'is_archive', 'is_add_admin', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        phone = validated_data['phone']

        # validate_password(password)
        password = make_password(password)

        user = User.objects.filter(username=phone)
        if user:
            raise serializers.ValidationError({'user': 'Already exist'})
        else:
            admin = Admin.objects.create(**validated_data)
            u = User.objects.create(username=phone, password=password, role='Admin')
            if u:
                admin.user = u
                admin.save()
                return admin
            else:
                admin.delete()
                raise serializers.ValidationError({'user': 'Do not created'})

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        phone = validated_data['phone']
        is_active = validated_data['is_active']

        # user = User.objects.filter(username=instance.phone).first()
        if password:
            # validate_password(password)
            password = make_password(password)
            instance.user.password = password
            # user.password = password

        if instance.phone != phone:
            instance.user.username = phone
            # user.username = phone

        if instance.is_active != is_active:
            instance.user.is_active = is_active
            # user.is_active = is_active
        # user.save()
        instance.user.save()
        return super().update(instance=instance, validated_data=validated_data)


class AdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
