from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportModelAdmin
from apps.letter.models import Letter, Reason, Counter
from apps.organization.models import Courier, Organization
from .resorce import LetterRecoreces
from django.contrib import admin
from django.db.models import Q
from django.urls import path
from django.shortcuts import render


class ParentNullListFilter(admin.SimpleListFilter):
    title = 'Tumanlar'
    parameter_name = 'parent__isnull'

    def lookups(self, request, model_admin):
        districts = tuple((f'{i.address}', f'{i.address}') for i in Letter.objects.filter(parent__isnull=True))
        return districts


    def queryset(self, request, queryset):
        for letter in Letter.objects.filter(parent__isnull=True):
            if self.value() == f'{letter.address}':
                return queryset.filter(parent_id=letter.id)
    
        return queryset.filter(parent__isnull=False)


class OranizationFilter(admin.SimpleListFilter):
    title = "Tashkilotlar"
    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        return tuple((f'{i.inn}', f'{i.inn} - {i.name}') for i in Organization.objects.all())
    
    def queryset(self, request, queryset):
        for org in Organization.objects.all():
            if self.value() == f'{org.inn}':
                return queryset.filter(Q(upload_file__organization_id=org.id) | Q(upload_zip_file__organization_id=org.id))



def attach_letter(modeladmin, request, queryset):
    # courier_id = request.POST.get('courier_dropdown')

    for letter in queryset:
        letter.status = 'process'
        letter.courier = Courier.objects.get(id=37)
        letter.save()


attach_letter.short_description = 'Attach selected letters to courier'


def archived_cancel_letters(modeladmin, request, queryset):
    for letter in queryset:
        letter.status = 'archived'
        letter.save()


archived_cancel_letters.short_description = 'Archived selected cancel letters'


def archived_finish_letters(modeladmin, request, queryset):
    for letter in queryset:
        letter.status = 'archived'
        letter.is_delivered = True
        letter.save()


archived_finish_letters.short_description = 'Archived selected finish letters'


def return_new_letters(modeladmin, request, queryset):
    for letter in queryset:
        letter.courier = None
        letter.status = 'new'
        letter.save()

return_new_letters.short_description = 'Return selected new letters'


def return_finish_letters(modeladmin, request, queryset):
    for letter in queryset:
        letter.status = 'finish'
        letter.reason = None
        letter.save()


return_finish_letters.short_description = 'Return selected finish letters'


def return_cencel_letters(modeladmin, request, queryset):
    for letter in queryset:
        letter.status = 'cancel'
        letter.save()


return_cencel_letters.short_description = 'Return selected cancel letters'


class LetterAdmin(DraggableMPTTAdmin, ImportExportModelAdmin, admin.ModelAdmin):
    actions = [archived_finish_letters, archived_cancel_letters, attach_letter, return_new_letters,
               return_cencel_letters, return_finish_letters]
    ordering = ('-id',)
    resource_classes = [LetterRecoreces]
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'courier', 'address', 'status', 'reason', 'id')
    list_filter = ('status', ParentNullListFilter, OranizationFilter, 'is_delivered', 'created_at')
    search_fields = ('personal_id', 'name', 'receiver_name', 'address', 'id', 'courier__full_name', 'reason__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('author', 'name', 'address', 'upload_file', 'parent', 'created_at', 'updated_at', 'personal_id', 'description', 'pdf_file', 'upload_zip_file', 'receiver_name')
    list_editable = ('status', 'courier', 'reason')  # Allow editing status directly from the list view
    list_select_related = ('courier', 'reason', 'parent', 'upload_file', 'upload_zip_file')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'courier':
            kwargs['queryset'] = Courier.objects.all()  # Replace 'Courier' with your actual Courier model name
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ReasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')


admin.site.register(Letter, LetterAdmin)
admin.site.register(Reason, ReasonAdmin)
