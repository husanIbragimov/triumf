import datetime
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from apps.letter.models import Letter
from apps.organization.models import InComeCourier, UpLoadLetterExcel, InComeOrganization


# @receiver(post_save, sender=UpLoadLetterExcel)
# def make_in_come_org(sender, instance, created, **kwargs):
#     month = datetime.datetime.now().month

#     if created:
#         make_in_come_organization(instance)

def make_in_come_organization(uploadfile):
    date = datetime.datetime.now()
    month = date.month

    if uploadfile.organization:  # and uploadfile.status == 'finished'
        income = get_object_or_404(InComeOrganization, organization_id=uploadfile.organization.id,
                                                   created_at__month=month)
        if not income:
            income = InComeOrganization.objects.create(organization=uploadfile.organization, total_letter=0,
                                                       name=date.strftime('%B'))
        income.total_letter = uploadfile.count

        letters = Letter.objects.filter(upload_file_id=uploadfile.id, created_at__month=month)
        delivered_count = letters.filter(Q(status='finish') | Q(status='archive')).count()
        all_letters = letters.filter(Q(Q(status='finish') | Q(status='cencel')) | Q(status='archive')).count()
        income.delivered = delivered_count
        income.price = uploadfile.organization.price * all_letters
        income.save()


def make_in_come_org(uploadfile):
    date = datetime.datetime.now()
    month = date.month

    if uploadfile.organization:  # and uploadfile.status == 'finished'
        income = get_object_or_404(InComeOrganization, organization_id=uploadfile.organization.id,
                                                   created_at__month=month)
        if not income:
            income = InComeOrganization.objects.create(organization=uploadfile.organization, total_letter=0,
                                                       name=date.strftime('%B'))

        letters = Letter.objects.filter(created_at__month=month, upload_file_id=uploadfile.id)
        income.name = f"{date.strftime('%B')} {date.year} ({uploadfile.name})"
        income.total_letter = letters.count()
        income.delivered = letters.filter(status='finish').count()
        income.price = letters.first().upload_file.organization.price * letters.filter(Q(status='finish') | Q(status='cencel')).count()
        income.upload_file = letters.first().upload_file
        income.organization = letters.first().upload_file.organization
        income.save()


def make_in_come_courier(courier):
    date = datetime.datetime.now()
    month = date.month

    if courier:
        income = InComeCourier.objects.filter(courier=courier, created_at__month=month).first()
        if not income:
            income = InComeCourier.objects.create(organization=courier, total_letter=0, name=date.strftime('%B'))

        letters = courier.attached.filter(created_at__month=month)
        income.total_letter = letters.count
        delivered_count = letters.filter(is_delivered=True).count()
        income.delivered = delivered_count
        income.price = courier.price * delivered_count
        income.save()
