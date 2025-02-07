import os
import zipfile
from celery import shared_task
from apps.letter.models import Letter

@shared_task
def generate_pdf_items(zip_path, upload_instance):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        # Extract the contents to a temporary directory
        print('extracting files')
        print(zip_path)
        temp_dir = 'temp'
        zip_file.extractall(temp_dir)

        # Loop through the extracted files and create new LetterPDF instances
        pdf_files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
        letter_pdfs = []
        for pdf_file in pdf_files:
            letter_pdf = Letter.objects.create(pdf_file=os.path.join(temp_dir, pdf_file), zip_file=upload_instance)
            letter_pdfs.append(letter_pdf)

        # Set the UploadLetterPDF instance's items attribute to the new LetterPDF instances
        upload_instance.pdf_file = letter_pdfs
        upload_instance.save()
        print('success')
