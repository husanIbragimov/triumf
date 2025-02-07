from django.urls import path
from .views import root, add_letter, archive, generate_report_month, daily_report

urlpatterns = [
    path('dashboard/', root, name="index"),
    path('dashboard/add-letter', add_letter, name="add_letter"),
    path('dashboard/archives/', archive, name='archives'),
    path('dashboard/report/', generate_report_month, name='report'),
    path('dashboard/daily-report', daily_report, name='daily_report'),
]
