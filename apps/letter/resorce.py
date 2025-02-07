from import_export import resources
from import_export.fields import Field
from apps.letter.models import Letter

class LetterRecoreces(resources.ModelResource):
    address = Field(attribute='address', column_name='Address')
    name = Field(attribute='name', column_name='Name')
    updated_at = Field(attribute='updated_at__date', column_name='Date')
    status = Field(attribute='status', column_name='Status')
    reason__name = Field(attribute='reason__name', column_name='Reason')
    courier__full_name = Field(attribute='courier__full_name', column_name='Courier')
    id = Field(attribute='personal_id', column_name='ID')

    class Meta:
        model = Letter
        fields = ('address', 'name', 'updated_at', 'status', 'reason__name', 'courier__full_name', 'id')
