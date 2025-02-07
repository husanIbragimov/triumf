import os
import subprocess
from django.db import models
from io import BytesIO
# from PyPDF4 import 
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from apps.account.models import BaseAbstractDate
from apps.organization.models import UpLoadLetterExcel, Courier, Organization, UploadLetterPDF
from PIL import Image
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import logging

logger = logging.getLogger(__name__)


def compress(file):
    file = Image.open(file)
    file_io = BytesIO()

    if file.mode in ("RGBA", "P"):
        file.load()
        background = Image.new("RGB", file.size, (255, 255, 255))
        background.paste(file, mask=file.split()[3])
        background.save(file_io, "JPEG", quality=60)
    else:
        file.save(file_io, "JPEG", quality=60)

    new_file = File(file_io, name=file.name)

    return new_file

def compress_pdf(file):
    input_pdf = file.path
    output_dir = os.path.join(os.path.dirname(input_pdf), 'Letter')
    os.makedirs(output_dir, exist_ok=True)
    output_pdf = os.path.join(output_dir, f"compressed_{os.path.basename(input_pdf)}")

    # Command to compress the PDF using Ghostscript
    gs_command = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", 
        "-dPDFSETTINGS=/screen", "-dNOPAUSE", "-dBATCH", 
        "-sOutputFile=" + output_pdf, input_pdf
    ]

    try:
        # Run the command
        subprocess.run(gs_command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Ghostscript command failed with error: {e}")
        raise

    # Read compressed file and return as File object
    with open(output_pdf, 'rb') as f:
        return File(f, name=os.path.basename(output_pdf))


class Letter(MPTTModel):
    STATUS = (
        ('process', 'Process'),
        ('cancel', 'Cancel'),
        ('finish', 'Finish'),
        ('new', 'New'),
        ('archived', 'Archived')
    )
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    receiver_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    personal_id = models.BigIntegerField(default=0)
    image = models.FileField(upload_to='LetterResponses', null=True, blank=True)
    pdf_file = models.FileField(upload_to='Letter', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, default='new', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    author = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        related_name='letters',
        null=True, blank=True
    )

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='children',
        db_index=True
    )
    courier = models.ForeignKey(
        Courier,
        on_delete=models.CASCADE,
        related_name='attached',
        null=True, blank=True
    )
    upload_file = models.ForeignKey(
        UpLoadLetterExcel,
        on_delete=models.CASCADE,
        related_name='letters',
        null=True, blank=True
    )
    upload_zip_file = models.ForeignKey(
        UploadLetterPDF,
        on_delete=models.CASCADE,
        related_name='zip_letters',
        null=True, blank=True
    )
    reason = models.ForeignKey(
        'Reason',
        on_delete=models.CASCADE,
        related_name='letters',
        null=True, blank=True
    )
    is_delivered = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # if self.image:
        #     self.image = compress(self.image)
        # if self.pdf_file:
        #     file_size = self.pdf_file.size
        #     file_size_mb = file_size / (1024 * 1024)
        #     if file_size_mb > 8:
        #         self.pdf_file = compress_pdf(self.pdf_file)
        super(Letter, self).save(*args, **kwargs)


    def __str__(self):
        if self.name:
            return self.name
        return "Letter"

    class MPTTMeta:
        order_insertion_by = ['name']

class Reason(BaseAbstractDate):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Counter(BaseAbstractDate):
    letter_counter = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.letter_counter}"
