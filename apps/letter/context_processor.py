from django.shortcuts import get_object_or_404

from apps.organization.models import Organization, AlertDebtor


def data(request):
    last_debtor = []
    if Organization.objects.filter(user=request.user).exists():
        organization_id = Organization.objects.get(user=request.user).id
        last_debtor = AlertDebtor.objects.filter(organization_id=organization_id, is_active=True).last()

    return {
        'last_debtor': last_debtor
    }