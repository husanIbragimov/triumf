import sys
import os
import shutil
import zipfile
import subprocess
import pandas as pd
from subprocess import Popen
from barcode.ean import EAN13
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
from PIL import Image
from celery import shared_task
from PyPDF4 import PdfFileMerger
from docxtpl import DocxTemplate
from apps.letter.models import Letter, Counter
from apps.organization.signals import make_in_come_org
from apps.organization.models import UpLoadLetterExcel
from apps.organization.signals import make_in_come_organization
from django.shortcuts import get_object_or_404
from apps.organization.models import UploadLetterPDF

# import barcode
# barcode.PROVIDED_BARCODES

sys.setrecursionlimit(50000)


def delete_folders(id):
    """
    Joriy katalogdagi outputdocx va qrcodes katalogini o'chiradi.
    """
    try:
        shutil.rmtree(f"docx{id}")
        shutil.rmtree(f"png{id}")
        os.remove(f"png{id}")

    except:
        pass


def create_folder(id):
    """
    Joriy katalogda outputdocx va qrcodes katalogini yaratadi.
    """
    try:
        os.makedirs(f"docx{id}", exist_ok=True)
        os.makedirs(f"png{id}", exist_ok=True)
    except FileExistsError:
        print("Kataloglar allaqachon mavjud.")


# Create qr code .png
def make_png(df, name, path_site, id, letter_excel):
    # Berilgan dataframe bo'yicha

    walker = Counter.objects.all().last()
    number = walker.letter_counter

    df = df.sort_values('ID', ascending=True)

    for index, row in df.iterrows():
        number += 1
        letter_count = Counter.objects.create(letter_counter=number)
        bar_id = f"{letter_count.letter_counter}".zfill(12)  # Ensure bar_id has 12 digits

        id = row['ID']

        # Generate EAN-13 barcode
        my_code = EAN13(bar_id)

        code = f'png{name}/{id}'

        # Our barcode is ready. Let's save it.
        my_code.save(code)


def prepare_letter(template, context, qrcode, output):
    tpl = DocxTemplate(template)
    # tpl.replace_pic('qr_code.png', qrcode)
    tpl.render(context)
    tpl.replace_pic('Image1', qrcode)
    tpl.save(output)


def make_docx(df, template, name, header):
    # Create docx
    print("Docx tuzilmoqda...\n")
    print(header)
    for _, row in df.iterrows():
        st = row['ID']
        context = {
            'address': row['Address'],  # Иссиқлик тарқатиш” {{address}} тумани tuman
            'address_home': row['StreetNumber'],  # {{address_home}} уй
            'full_name': row['FullName'],
            'hisob_raqam': row['ID'],
            'tashkilot': row['Own'],
            'date': row['Date'].date(),
            'office_phone': row['OfficePhone'],  # Маълумот учун телефон рақами
            'mob_phone': row['MobilPhone']  # Телефон рақами
        }
        # png generate
        qrcode2 = f'png{name}/{st}.svg'
        output = f"docx{name}/{st}.docx"
        prepare_letter(template, context, qrcode2, output)


# Generate pdf
def generate_pdf(df, name, district_id, letter_excel):
    parent = Letter.objects.filter(id__exact=district_id).first()
    count = 0

    for index, row in df.iterrows():
        st = row['ID']
        docx_file_path = f"docx{name}/{st}.docx"
        pdf_file_path = f"pdfs/{name}/{st}.pdf"  # Changed pdf_file_path to include the specific filename

        try:
            # Database add
            Letter.objects.create(parent=parent, address=f"{row['Address']} {row['StreetNumber']}",
                                  name=row['FullName'], personal_id=row["ID"], pdf_file=pdf_file_path,
                                  upload_file=letter_excel)
            print(f"Databasega yozildi: {pdf_file_path}")
            count += 1
        except Exception as errors:
            letter_excel.status = 'failed'
            letter_excel.save()
            print(f"Xato: {errors}")

    subprocess.call(['sudo', './genpdf.sh', str(name)])
    print("Conversion completed.")
    return count


def combine_pdfs(input_folder, output_file):
    pdf_merger = PdfFileMerger()

    files = os.listdir(input_folder)
    files.sort()
    for file in files:
        if file.endswith(".pdf"):
            file_path = os.path.join(input_folder, file)
            with open(file_path, "rb") as f:
                pdf_merger.append(f)


    with open(output_file, "wb") as output:
        pdf_merger.write(output)


def make_one_pdfs(id, letter_excel, district_id, count):
    district = get_object_or_404(Letter, id=district_id)
    input_folder = f"media/pdfs/{id}"
    output_file = f"media/pdfs/{id}.{district.address}({count}).pdf"

    combine_pdfs(input_folder, output_file)
    letter_excel.pdf_file = f'pdfs/{id}.{district.address}({count}).pdf'
    return 'success pdfs files\n'


@shared_task
def generate_pdf_items(zip_path, upload_instance_id, organization_id, path_site, district_id):
    try:
        pdf_merger = PdfFileMerger()
        upload_instance = get_object_or_404(UploadLetterPDF, id=upload_instance_id)
        print('generating pdf items')
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Extract the contents to a temporary directory
            print('extracting files')
            print(zip_path)
            temp_dir = f'zip/zip_temp{upload_instance_id}'
            zip_file.extractall(temp_dir)

            # Loop through the extracted files and create new LetterPDF instances
            pdf_files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
            letter_pdfs = []
            letter_counter = 0
            for pdf_file in pdf_files:
                letter_pdf = Letter.objects.create(
                    name=pdf_file,
                    pdf_file=os.path.join(temp_dir, pdf_file),
                    upload_zip_file=upload_instance,
                    parent_id=district_id,
                    status='new'
                )
                letter_pdfs.append(letter_pdf)
                letter_counter += 1
            print('created letter pdf')
            upload_instance.status = 'finished'
            upload_instance.count = letter_counter
            # upload_instance.pdf_file = 'zip/pdfs' + str(upload_instance_id) + '.pdf'
            upload_instance.save()
            return 'success'
    except Exception as e:
        print('Error in task:', str(e))


@shared_task
def createpdf(id, url, organization_id, path_site, district_id, header):
    df = pd.read_excel(url)  # DataFrame yaratib olindi
    letter_excel = get_object_or_404(UpLoadLetterExcel, id=id)  # Excel faylga ishlov berish uchun chaqirildi
    create_folder(id)  # Bir nechta excel yuklanganda farqlay olish uchun alohida papka yaratildi
    template = "files/shablon2.docx"  # Word faylidagi shablon ko'rsatildi
    make_png(df, id, path_site, id, letter_excel)  # Xat uchun QR code rasmi tuzildi har bir shaxs uchun
    make_docx(df, template, id, header)  # Xatni docx formatda tuzib chiqildi
    count = generate_pdf(df, id, district_id, letter_excel)  # Docx to PDF convert

    make_one_pdfs(id, letter_excel, district_id, count)
    delete_folders(id)
    letter_excel.count = count
    letter_excel.status = 'finished'
    letter_excel.save()
    # make_in_come_organization(letter_excel)
    # make_in_come_org(letter_excel)

    return "Success!"
