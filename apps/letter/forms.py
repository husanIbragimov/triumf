from django import forms


class UpdateCourierStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('process', 'Process'),
        ('cancel', 'Cancel'),
        ('finish', 'Finish'),
        ('new', 'New'),
        ('archived', 'Archived'),
    ]

    courier_id = forms.IntegerField()
    status = forms.ChoiceField(choices=STATUS_CHOICES)
