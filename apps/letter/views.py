import pandas as pd
from io import BytesIO
from django.http import HttpResponse

from django.db.models import Q
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from apps.letter.models import Letter
from apps.organization.models import Organization, UploadLetterPDF, AlertDebtor

from django.views.generic import ListView, TemplateView

class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

    def get_organization(self):
        return Organization.objects.filter(user__in=[self.request.user.id]).values('id', 'name', 'inn', 'icon').select_related('user').first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('search')
        
        organization = self.get_organization()
        districts = Letter.objects.filter(parent__isnull=True)
        letters = Letter.objects.filter(
            Q(parent__isnull=False) & Q(upload_zip_file__organization_id=organization.id)
            ).select_related(
                'reason', 'courier', 'upload_zip_file'
            ).exclude(status='archived').order_by('-id')

        if search:
            letters = letters.filter(Q(name__icontains=search) | Q(address__icontains=search) & Q(
                upload_zip_file__organization_id=organization.id))
        last_debtor = AlertDebtor.objects.filter(organization=organization, is_active=True).last()

        context = {
            'organization': organization,
            'districts': districts,
            'letters': letters,
            'last_debtor': last_debtor
        }
        return context


def root(request):
    if not request.user.is_authenticated:
        return redirect("login")

    search = request.GET.get('search')
    organization = get_object_or_404(Organization, user=request.user.id)
    districts = Letter.objects.filter(parent__isnull=True)
    letters = Letter.objects.filter(
        Q(parent__isnull=False) & Q(upload_zip_file__organization_id=organization.id)
        ).select_related(
            'reason', 'courier', 'upload_zip_file'
        ).exclude(status='archived').order_by('-id')

    if search:
        letters = letters.filter(Q(name__icontains=search) | Q(address__icontains=search) & Q(
            upload_zip_file__organization_id=organization.id))
    last_debtor = AlertDebtor.objects.filter(organization=organization, is_active=True).last()

    context = {
        'organization': organization,
        'districts': districts,
        'letters': letters,
	'last_debtor': last_debtor
    }

    return render(request, 'dashboard/index.html', context)


def archive(request):
    search = request.GET.get('search')
    organization = get_object_or_404(Organization, user=request.user.id)
    archives = Letter.objects.filter(
        Q(parent__isnull=False) & Q(upload_zip_file__organization_id=organization.id) &
        Q(status='archived')).select_related('reason', 'courier', 'upload_zip_file').order_by('-id')

    if search:
        archives = archives.filter(Q(name__icontains=search) | Q(address__icontains=search))

    context = {
        'organization': organization,
        'letters': archives
    }

    return render(request, 'dashboard/archive.html', context)


def add_letter(request):
    districts = Letter.objects.filter(parent__isnull=True)
    organization = get_object_or_404(Organization, user=request.user.id, is_active=True)
    if request.method == 'POST':
        name_list = request.POST.getlist('name')
        parent_list = request.POST.getlist('parent')
        address_list = request.POST.getlist('address')
        pdf_file_list = request.FILES.getlist('pdf_file')
        # phone_number_list = request.POST.getlist('phone_number')
        # receiver_name_list = request.POST.getlist('receiver_name')

        upload_pdf_letter = UploadLetterPDF.objects.filter(organization=organization,
                                                           name__exact=f"{datetime.now().date()}").first()
        if not upload_pdf_letter:
            upload_pdf_letter = UploadLetterPDF.objects.create(organization=organization, status='finished',
                                                               name=f"{datetime.now().date()}", )
        else:
            upload_pdf_letter = UploadLetterPDF.objects.filter(organization=organization,
                                                               name__exact=f"{datetime.now().date()}").first()

        for name, parent_id, address, pdf_file in zip(
                name_list, parent_list, address_list, pdf_file_list
        ):
            # Retrieve the parent Letter instance
            parent_instance = get_object_or_404(Letter, id=parent_id)

            # Create the new Letter instance
            Letter.objects.create(
                author=request.user,
                name=name,
                parent=parent_instance,
                address=address,
                pdf_file=pdf_file,
                upload_zip_file=upload_pdf_letter
            )

    return render(request, 'dashboard/detail.html',
                  {'districts': districts, 'organization': organization})


def generate_report_month(request):
    month = request.GET.get('month')
    organization = Organization.objects.get(user=request.user.id)
    letters = Letter.objects.filter(
        upload_zip_file__organization_id=organization.id, 
        created_at__month=month, status__in=['finish', 'cancel'], 
        created_at__year=datetime.now().year).select_related('reason', 'courier', 'upload_zip_file').order_by('-id')
    letter_report = []
    if not letters.exists():
        return HttpResponse('No data found for this month.', status=404)
    for letter in letters:
        created_at_naive = letter.created_at.replace(tzinfo=None) if letter.created_at.tzinfo is not None else letter.created_at
        
        # Convert updated_at to timezone-naive if it's not None
        updated_at_naive = letter.updated_at.replace(tzinfo=None) if letter.updated_at and letter.updated_at.tzinfo is not None else letter.updated_at
        
        letter_report.append({
            'Tashkilot': letter.upload_zip_file.organization.name,
            'INN': letter.upload_zip_file.organization.inn,
            'F.I.SH': letter.name,
            'Manzil': letter.address,
            'status': letter.status,
            'Yuklangan sana': created_at_naive,
            'Kuriyer': letter.courier if letter.courier else 'Not assigned',
            'Sabab': letter.reason.name if letter.reason else 'Not specified',
            'Yetkazilgan sana': updated_at_naive,
            'ID': letter.id,
        })
    file_name = f'TRIUMF_hisobot_{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().time()}'
    df = pd.DataFrame(letter_report)
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name='Hisobot')
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
    return response


def daily_report(request):
    date = datetime.now().date()
    organization = Organization.objects.get(user=request.user.id)
    letters = Letter.objects.filter(upload_zip_file__organization_id=organization.id, created_at__date=date).select_related('reason', 'courier', 'upload_zip_file').order_by('-id')
    letter_report = []
    if letters.count() == 0:
        return redirect('page-404.html')
    for letter in letters:
        created_at_naive = letter.created_at.replace(tzinfo=None) if letter.created_at.tzinfo is not None else letter.created_at
        
        # Convert updated_at to timezone-naive if it's not None
        updated_at_naive = letter.updated_at.replace(tzinfo=None) if letter.updated_at and letter.updated_at.tzinfo is not None else letter.updated_at
        
        letter_report.append({
            'Tashkilot': letter.upload_zip_file.organization.name,
            'INN': letter.upload_zip_file.organization.inn,
            'F.I.SH': letter.name,
            'Manzil': letter.address,
            'status': letter.status,
            'Yuklangan sana': created_at_naive,
            'Kuriyer': letter.courier if letter.courier else 'Not assigned',
            'Sabab': letter.reason.name if letter.reason else 'Not specified',
            'Yetkazilgan sana': updated_at_naive,
            'ID': letter.id,
        })
    file_name = f'TRIUMF_kunlik_restr_{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().time()}'
    df = pd.DataFrame(letter_report)
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name='Hisobot')
    output.seek(0)
    letter_report.clear()
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
    return response
