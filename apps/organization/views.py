from datetime import datetime

from rest_framework import response, status, views

from .models import Organization, InComeOrganization, UpLoadLetterExcel, Courier, InComeCourier
from .permissions import OrganizationPermission


class OrganizationFileUpload(views.APIView):
    permission_classes = OrganizationPermission

    def get(self, request):
        return response.Response(status=status.HTTP_200_OK)

    def post(self, request):
        pass


def in_come_organization_create_list():
    month = datetime.now().month
    month_name = datetime.now().strftime('%B')
    organizations = Organization.objects.all()

    for organization in organizations:
        income = InComeOrganization.objects.filter(this_month=True, organization=organization).last()
        uploads = UpLoadLetterExcel.objects.filter(created_at__month=month, organization=organization)

        for upload in uploads:
            income.total_letter += upload.count
            income.price = organization.price * income.total_letter

        income.this_month = False
        income.save()

        new_income = InComeOrganization.objects.create(name=month_name, this_month=True, organization=organization)


def in_come_courier_create_list():
    month = datetime.now().month
    month_name = datetime.now().strftime('%B')
    couriers = Courier.objects.all()

    for courier in couriers:
        income = InComeCourier.objects.filter(this_month=True, courier=courier)
        uploads = UpLoadLetterExcel.objects.filter(created_at__month=month, incomescourier=income)

        for upload in uploads:
            income.total_letter += upload.count
            income.price = courier.price * income.total_letter

        income.this_month = False
        income.save()

        new_income = InComeCourier.objects.create(name=month_name, this_month=True, courier=courier)
