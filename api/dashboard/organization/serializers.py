from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.account.models import User
from apps.organization.models import Organization, Courier, InComeOrganization, InComeCourier, UpLoadLetterExcel, Adele, UploadLetterPDF


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=16, write_only=True)
    password2 = serializers.CharField(max_length=16, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',  'password', 'password2']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        password2 = validated_data.pop('password2', None)
        username = validated_data.pop('username', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)

        if password != password2:
            raise serializers.ValidationError({'password': 'Password must match.'})

        validate_password(password)
        password = make_password(password)

        user = User.objects.create(username=username, first_name=first_name, last_name=last_name, password=password, role='Person')
        return user
    

class PersonalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class AdeleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adele
        fields = '__all__'


class InComeOrganizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InComeOrganization
        fields = '__all__'  # ['id', 'full_name', 'avatar', 'phone']


class InComeOrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InComeOrganization
        fields = '__all__'  # ['id', 'full_name', 'avatar', 'phone']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # ['id', 'full_name', 'avatar', 'phone']


class OrganizationListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = '__all__'  # ['id', 'full_name', 'avatar', 'phone']


class OrganizationPatchSerializer(serializers.ModelSerializer):
    inn = serializers.CharField(required=False)
    adeles = AdeleSerializer(many=True)

    class Meta:
        model = Organization
        fields = ['adeles', 'inn']

    def update(self, instance, validated_data):
        adeles = validated_data.pop('adeles')
        for adele in adeles:
            name = adele.pop('name')
            excel_file = adele.pop('excel_file', None)
            pdf_file = adele.pop('pdf_file', None)
            adeles = Adele.objects.create(name=name, excel_file=excel_file, pdf_file=pdf_file)
            instance.adeles.add(adeles.id)

        instance.save()
        return instance


class OrganizationCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    icon = serializers.FileField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    inn = serializers.CharField(required=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'icon', 'inn', 'district', 'password', 'price', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        inn = validated_data['inn']

        # validate_password(password)
        password = make_password(password)

        user = User.objects.filter(username=inn)
        if user:
            raise serializers.ValidationError({'Organization': 'Already exist'})
        else:
            organization = Organization.objects.create(**validated_data)
            u = User.objects.create(username=inn, password=password, role='Organization')
            if u:
                organization.user = u
                organization.save()
                return organization
            else:
                organization.delete()
                raise serializers.ValidationError({'Organization': 'Do not created'})

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        inn = validated_data['inn']
        is_active = validated_data['is_active']

        # user = User.objects.filter(username=instance.inn).first()

        if password:
            # validate_password(password)
            password = make_password(password)
            instance.user.password = password
            # user.password = password

        if instance.inn != inn:
            instance.user.username = inn
            # user.inn = inn

        if instance.is_active != is_active:
            instance.user.is_active = is_active
            # user.is_active = is_active
        instance.user.save()
        return super().update(instance=instance, validated_data=validated_data)


class CourierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['id', 'full_name', 'avatar', 'phone']


class CourierCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    avatar = serializers.FileField(required=False)
    password = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(required=True)

    class Meta:
        model = Courier
        fields = ['id', 'full_name', 'avatar', 'phone', 'password', 'jshr', 'language', 'auto_type', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        phone = validated_data['phone']

        # validate_password(password)
        password = make_password(password)

        user = User.objects.filter(username=phone)
        if user:
            raise serializers.ValidationError({'Courier': 'Already exist'})
        else:
            courier = Courier.objects.create(**validated_data)
            u = User.objects.create(username=phone, password=password, role='Courier')
            if u:
                courier.user = u
                courier.save()
                return courier
            else:
                courier.delete()
                raise serializers.ValidationError({'Courier': 'Do not created'})

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
        instance.user.save()
        return super().update(instance=instance, validated_data=validated_data)


class InComeCourierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InComeCourier
        fields = ['id', 'name', 'price', 'total_letter', 'delivered']


class InComeCourierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InComeCourier
        fields = '__all__'


class UpLoadLetterExcelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpLoadLetterExcel
        fields = '__all__'



class UploadLetterPDFListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadLetterPDF
        fields = '__all__'
        