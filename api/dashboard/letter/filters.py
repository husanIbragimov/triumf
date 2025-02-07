import datetime

import django_filters
from django.db.models import Q
from django.utils.timezone import now

from apps.letter.models import Letter


def filter_date(queryset, name, value):
    queryset = queryset.filter(created_at__month=value.month)
    return queryset


class LetterFilter(django_filters.FilterSet):
    upload_file__name = django_filters.CharFilter(field_name='upload_file__name', lookup_expr='exact')
    address = django_filters.CharFilter(field_name='address', lookup_expr='icontains')
    upload_file__id = django_filters.CharFilter(field_name='upload_file__id', lookup_expr='exact')
    upload_zip_file__id = django_filters.CharFilter(field_name='upload_zip_file__id', lookup_expr='exact')
    courier__id = django_filters.NumberFilter(field_name='courier__id')
    # choice_status = django_filters.CharFilter(field_name='status')
    status = django_filters.ChoiceFilter(field_name='status', choices=Letter.STATUS)
    organization_id = django_filters.NumberFilter(field_name='upload_file__organization__id')
    org_id = django_filters.NumberFilter(field_name='upload_zip_file__organization__id')
    upload_file = django_filters.NumberFilter(field_name='upload_file')
    date = django_filters.DateFilter(method=filter_date, label='date')
    district_id = django_filters.CharFilter(field_name='parent__id', lookup_expr='exact')


    class Meta:
        model = Letter
        fields = [
            "upload_file__name",
            "address",
            "upload_file__id",
            "upload_zip_file__id",
            "courier__id",
            "status",
            "organization_id",
            "org_id",
            "upload_file",
            "date",
            "district_id"
        ]

# def search_company(queryset, name, value):
#     if value:
#         queryset = queryset.filter(parent__isnull=True)
#     else:
#         queryset = queryset.filter(parent__isnull=False)
#     return queryset
#
#
# class ClientFilter(django_filters.FilterSet):
#     company = django_filters.BooleanFilter(method=search_company, label='client_or_company')
#
#     class Meta:
#         model = Client
#         fields = []
