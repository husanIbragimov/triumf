from apps.letter.models import Letter
from apps.organization.models import Organization, InComeOrganization, UpLoadLetterExcel, Courier, InComeCourier


def create_income_organization():
    organizations = Organization.objects.all()
    month = 0
    for org in organizations:
        income = InComeOrganization.objects.filter(organization=org.id, this_month=True).first()
        letters = Letter.objects.filter(upload_file__organization=org.id, created_at__month=income.created_at.month)
        print(income)
        print(letters)
        total = letters.count()
        delivered_count = letters.filter(is_delivered=True).count()
        income.name = org.name
        income.total_letter = total
        income.delivered = delivered_count
        income.price = delivered_count * org.price
        income.this_month = False

        files = UpLoadLetterExcel.objects.filter(organization=org, created_at__month=income.created_at.month)
        zip = []
        for file in files:
            zip.append(file.excel_file)
            month = file.created_at.month
            print(month)
            # Agar 1 talab qoshilganda pdf fileni zipga qo'shish kerak
        income.save()
        new_income = InComeOrganization.objects.create(organization=org, this_month=True, organization__name=org.name)


def create_income_courier():
    couriers = Courier.objects.all()
    month = 0
    for courier in couriers:
        income = InComeCourier.objects.filter(courier=courier, this_month=True).first()
        letters = Letter.objects.filter(courier=courier, created_at__month=income.created_at.month)
        total = letters.count()
        delivered_count = letters.filter(is_delivered=True).count()
        income.total_letter = total
        income.delivered = delivered_count
        income.price = delivered_count * courier.price
        income.this_month = False

        zip = []
        for file in letters:
            zip.append(file.pdf_file)
            # Agar 1 talab qoshilganda pdf fileni zipga qo'shish kerak
        income.save()
        new_income = InComeCourier.objects.create(courier=courier, this_month=True)
