import os
import logging
import pandas as pd
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from datetime import datetime
from multiprocessing import Pool
from django.contrib import admin
from PyPDF4.merger import PdfFileMerger, PdfFileReader
from django.db.models import Count
from django.contrib import messages
from apps.letter.models import Letter
from apps.account.models import User
from django.core.files.base import ContentFile
from apps.organization.models import (
    Organization, Courier, AlertDebtor,
    InComeOrganization, InComeCourier, 
    UpLoadLetterExcel, Adele, Partner, UploadLetterPDF
    )
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from pypdf import PdfMerger
from reportlab.lib.pagesizes import letter
from django.core.files import File
from django.urls import path
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

admin.site.register(AlertDebtor)


def get_export_every_month_letter_counts(self, request, queryset):
    current_month = datetime.now().month
    current_year = datetime.now().year
    # Get the current month and year
    months = {
        1: 'yanvar',
        2: 'fevral',
        3: 'mart',
        4: 'aprel',
        5: 'may',
        6: 'iyun',
        7: 'iyul',
        8: 'avqust',
        9: 'sentyabr',
        10: 'oktyabr',
        11: 'noyabr',
        12: 'dekabr'
    }

    # Get all organizations
    orgs = queryset

    letter_data = []

    
    for month in months:
        if month <= current_month:
            for org in orgs:
                # Get the total letter count for the current month
                letters = Letter.objects.filter(upload_zip_file__organization=org, created_at__month=month, created_at__year=current_year)

                data = {
                    'Tashkilot': org.name,
                    'INN': org.inn,
                    'Oy': months[month],
                    '1 dona xatning narxi': org.price,
                    'Jami xatlar': letters.count(),
                    'Jami summa': letters.count() * org.price if letters.count() > 0 else 0
                }
                letter_data.append(data)

    df = pd.DataFrame(letter_data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    letter_data.clear()
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{datetime.now().strftime("%Y-%m-%d")}_{datetime.now().time()}.xlsx"'
    return response


def connect_user_to_organization(self, request, queryset):
    for org in queryset:
        if not org.user.exists():
            user = org.inn
            try:
                user = User.objects.get(username=user)
                print(user)
                org.user.set([user])  # Pass a list containing the user
            except User.DoesNotExist:
                messages.error(request, f"User with username {user} does not exist.")
        messages.success(request, "Users connected to organizations successfully")


class OrganizationAdmin(admin.ModelAdmin):
    actions = [get_export_every_month_letter_counts, connect_user_to_organization]
    filter_horizontal = ('user',)
    list_display = ('id', 'name', 'inn', 'price', 'is_active')
    list_display_links = ('id', 'name')
    list_filter = ('created_at', 'is_active')
    exclude = ('adeles',)
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('adeles', 'user')


class UpLoadLetterExcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'count', 'get_excel', 'get_pdf', 'organization', 'get_created_at', 'id')
    list_filter = ('status', 'created_at', 'organization')
    list_per_page = 30
    readonly_fields = ("name", "count", "get_excel", "get_pdf", "organization", "created_at", "updated_at")
    exclude = ('pdf_file', 'excel_file', 'response')



from urllib.parse import unquote
from PyPDF4.utils import PdfReadError


# def merge_pdfs(self, request, queryset):
#     try:
#         for upload_pdf in queryset:
#             merger = PdfFileMerger()

#             if upload_pdf.zip_letters.all().count() == 1:
#                 upload_file = upload_pdf.zip_letters.first().pdf_file
#                 upload_pdf.pdf_file = upload_file
#                 upload_pdf.save()
#                 messages.success(request, f"PDFs merged successfully. ID: {upload_pdf.id}")

#             elif upload_pdf.zip_letters.all().count() > 1:
    
#                 for letter in upload_pdf.zip_letters.all():

#                     if letter.pdf_file.path:

#                         logging.info(f"Processing PDF file: {letter.pdf_file.path}. ID: {upload_pdf.id}")
#                         messages.info(request, f"Processing PDF file: {letter.pdf_file.path}. ID: {upload_pdf.id}")
                        
#                         merger.append(letter.pdf_file.path)
#                     else:
#                         logging.error(f"PDF file not found for letter ID {letter.id}. ID: {upload_pdf.id}", level=messages.ERROR)
                            
                        
#                 output_pdf_path = os.path.join('UploadLetterPDF', f'{datetime.now().date()}_{upload_pdf.id}.pdf')
#                 full_output_path = os.path.join(settings.MEDIA_ROOT, output_pdf_path)
#                 try:
#                     merger.write(full_output_path)
#                 except PdfReadError as e:
#                     logging.error(f"Error writing merged PDF to {full_output_path}: {e}. ID: {upload_pdf.id}")
#                     self.message_user(request, f"Could not write the merged PDF to {full_output_path} due to a PdfReadError. ID: {upload_pdf.id}", level=messages.ERROR)
#                 finally:
#                     merger.close()
                

#                 # Update the pdf_file field with the relative path from the media directory
#                 upload_pdf.pdf_file = output_pdf_path
#                 upload_pdf.save()
#             messages.success(request, f"PDFs merged successfully. ID: {upload_pdf.id}")
#     except Exception as e:
#         logging.error(f"Error merging PDFs: {e}")
#         messages.error(request, f"Error merging PDFs: {e}", level=messages.ERROR)

# merge_pdfs.short_description = "Merge selected PDFs"


def create_title_page(file_name, output):
    c = canvas.Canvas(output, pagesize=letter)
    c.drawString(100, 750, f"File: {file_name}")
    c.showPage()
    c.save()


def combine_pdfs_with_titles(pdf_files, upload_file_name):
    merger = PdfMerger()
    for pdf_file in pdf_files:
        file_name = os.path.basename(pdf_file)
        title_pdf_path = f"title_{file_name}.pdf"
        
        with open(title_pdf_path, 'wb') as output:
            create_title_page(file_name, output)
        
        merger.append(title_pdf_path)
        merger.append(pdf_file)
        os.remove(title_pdf_path)  # Clean up the temporary title page file
    
    combined_pdf_path = f"combined_{upload_file_name}.pdf"
    with open(combined_pdf_path, 'wb') as output_pdf:
        merger.write(output_pdf)
    
    merger.close()
    return combined_pdf_path

@admin.action(description='Tanlangan PDF-fayllarni birlashtirish')
def combine_pdfs_for_selected_organizations(modeladmin, request, queryset):
    for obj in queryset:
        pdf_files = [letter.pdf_file.path for letter in obj.zip_letters.all()]
        combined_pdf_path = combine_pdfs_with_titles(pdf_files, obj.name)

        with open(combined_pdf_path, 'rb') as pdf_file:
            django_file = File(pdf_file)
            obj.status = 'finished'
            obj.pdf_file.save(f"combined_{obj.name}.pdf", django_file, save=True)
        
        os.remove(combined_pdf_path)  # Clean up the combined PDF file


def combine_pdfs(self, request, queryset):
    try:
        for upload_pdf in queryset:
                merger = PdfFileMerger()
                zip_letters_count = upload_pdf.zip_letters.count()
                if zip_letters_count == 1:
                    upload_file = upload_pdf.zip_letters.first().pdf_file
                    upload_pdf.pdf_file = upload_file
                    upload_pdf.save()
                    messages.success(request, f"PDFs merged successfully. ID: {upload_pdf.id}")
                elif zip_letters_count > 1:
                    pdf_files = []
                    for letter in upload_pdf.zip_letters.all():
                        if letter.pdf_file.path:
                            logging.info(f"Processing PDF file: {letter.pdf_file.path}. ID: {upload_pdf.id}")
                            messages.info(request, f"Processing PDF file: {letter.pdf_file.path}. ID: {upload_pdf.id}")
                            pdf_files.append(letter.pdf_file.path)
                        else:
                            logging.error(f"PDF file not found for letter ID {letter.id}. ID: {upload_pdf.id}", level=messages.ERROR)
                    for file_path in pdf_files:
                        try:
                            merger.append(file_path)
                        except PdfReadError:
                            logging.error(f"Error reading PDF file: {file_path}. ID: {upload_pdf.id}")
                            messages.error(request, f"Error reading PDF file: {file_path}. ID: {upload_pdf.id}")
                    output_pdf_path = os.path.join('UploadLetterPDF', f'{datetime.now().date()}_{upload_pdf.id}.pdf')
                    full_output_path = os.path.join(settings.MEDIA_ROOT, output_pdf_path)
                    try:
                        merger.write(full_output_path)
                    except PdfReadError as e:
                        logging.error(f"Error writing merged PDF to {full_output_path}: {e}. ID: {upload_pdf.id}")
                        self.message_user(request, f"Could not write the merged PDF to {full_output_path} due to a PdfReadError. ID: {upload_pdf.id}", level=messages.ERROR)
                    finally:
                        merger.close()

                    # excel generation
                    df = pd.DataFrame({
                        'F.I.SH': upload_pdf.zip_letters.values_list('name', flat=True),
                        'Manzil': upload_pdf.zip_letters.values_list('address', flat=True),
                        'Status': upload_pdf.zip_letters.values_list('status', flat=True),
                    })

                    # Update the pdf_file field with the relative path from the media directory
                    upload_pdf.pdf_file = output_pdf_path
                    upload_pdf.zip_file = df.to_excel(os.path.join(settings.MEDIA_ROOT, 'UploadLetterPDFResponse', f'{upload_pdf.organization.name}_{datetime.now().date()}.xlsx'))
                    upload_pdf.save()
                    messages.success(request, f"PDFs merged successfully. ID: {upload_pdf.id}")
    except Exception as e:
        logging.error(f"Error merging PDFs: {e}")
        messages.error(request, f"Error Combine selected PDFs: {e}", level=messages.ERROR)


combine_pdfs.short_description = "Tanlangan PDF-fayllarni birlashtirish 2"
        


def generate_excel(self, request, queryset):
    try:
        for item in queryset:
            df = pd.DataFrame({
                'F.I.SH': item.zip_letters.values_list('name', flat=True),
                'Manzil': item.zip_letters.values_list('address', flat=True),
                'Status': item.zip_letters.values_list('status', flat=True),
                'ID': item.zip_letters.values_list('id', flat=True),
            })
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            item.zip_file = ContentFile(output.getvalue(), f'{item.organization.name}_{item.name}.xlsx')
            item.save()
            output.close()
        messages.success(request, "Excel files generated successfully")
    except Exception as e:
        logging.error(f"Error generating Excel files: {e}")
        messages.error(request, f"Error generating Excel files: {e}", level=messages.ERROR)

generate_excel.short_description = "Excel hisobot yaratish"


class UploadLetterPDFAdmin(admin.ModelAdmin):
    actions = [generate_excel, combine_pdfs, combine_pdfs_for_selected_organizations]
    list_display = ('name', 'status', 'letter_count', 'get_excel', 'get_pdf', 'organization', 'created_at', 'id')
    list_filter = ('status', 'created_at', 'organization')
    readonly_fields = ("organization", "name", "letter_count", "get_excel", "get_pdf", "created_at", "updated_at")
    exclude = ("count", "pdf_file", "zip_file")
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organization')



class InComeOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_letter', 'organization', 'id')
    list_filter = ('created_at',)
    list_per_page = 30


class CourierAdmin(admin.ModelAdmin):
    list_display = ('phone', 'full_name', 'jshr', 'price', 'auto_type', 'is_active', 'id')
    list_filter = ('created_at', 'is_active')
    list_per_page = 30
    change_list_template = 'admin/organization/courier/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("import/", self.attach_letter, name="attach_letter")]

        return my_urls + urls
    
    @staticmethod
    def get_pagination_context(page_obj, paginator):
        index = page_obj.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = paginator.page_range[start_index:end_index]
        return {
            'page_range': page_range,
            'start_page': start_index + 1,
            'end_page': end_index
        }

    def attach_letter(self, request):
        org_id = request.GET.get('organization_id')
        courier_id = request.GET.get('courier_id')
        status = request.GET.get('status')
        region_id = request.GET.get('region_id')

        query_kwargs = Q()

        if org_id:
            query_kwargs &= Q(
                Q(upload_file__organization_id=org_id) | Q(upload_zip_file__organization_id=org_id)
            )
        
        if status:
            query_kwargs &= Q(status=status)
        else:
            query_kwargs &= Q(status__in=['new', 'process'])
        
        if courier_id:
            query_kwargs &= Q(courier_id=courier_id)
        
        if region_id:
            query_kwargs &= Q(parent_id=region_id)
        else:
            query_kwargs &= Q(parent__isnull=False)
        

        letters = Letter.objects.filter(query_kwargs).select_related('upload_file', 'upload_zip_file', 'courier')
        regions = Letter.objects.filter(parent__isnull=True)

        organizations = Organization.objects.all()
        couriers = Courier.objects.all()

        # Pagination logic
        paginator = Paginator(letters, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Custom pagination data
        pagination_context = self.get_pagination_context(page_obj, paginator)

        template_name = 'admin/organization/courier/attach_letter.html'
        context = {
            'organizations': organizations,
            'couriers': couriers,
            'page_obj': page_obj,
            'pagination_context': pagination_context,
            'regions': regions
        }
        return render(request, template_name, context)


class InComeCourierAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_paid', 'price', 'total_letter', 'delivered', 'courier', 'id')
    list_filter = ('created_at',)
    list_per_page = 30

# admin.site.register(Adele)
admin.site.register(InComeOrganization, InComeOrganizationAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Courier, CourierAdmin)
admin.site.register(InComeCourier)
admin.site.register(UpLoadLetterExcel, UpLoadLetterExcelAdmin)
admin.site.register(UploadLetterPDF, UploadLetterPDFAdmin)
# admin.site.register(Partner)
