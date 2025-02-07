from django.core.files import File
from django.core.files.base import ContentFile
from apps.letter.models import Letter
from datetime import datetime
import os
import pandas as pd
from django.conf import settings
from io import BytesIO

def make_letter_status_response_excel(upload_excel):
    try:
        # Define the target directory path
        target_directory = os.path.join(settings.MEDIA_ROOT, "excel")
        letter_directory = os.path.join(settings.MEDIA_ROOT, "UpLoadLetterExcelResponse")

        # Ensure the directory exists, create it if not
        os.makedirs(target_directory, exist_ok=True)
        os.makedirs(letter_directory, exist_ok=True)

        # Define the Excel file path
        excel_file_path = os.path.join(target_directory, f"{datetime.now().date()}_{upload_excel.name}.xlsx")
        upload_excel_file_path = os.path.join(letter_directory, f"{datetime.now().date()}_{upload_excel.name}.xlsx")

        # Create a list to store letter data
        letters_data = []

        # Fetch letters associated with the upload_excel
        letters = Letter.objects.filter(upload_file=upload_excel)

        if letters:
            for letter in letters:
                letter_data = {
                    "ID": letter.personal_id if letter.personal_id else '',
                    "Name": f"{letter.name}",
                    "Address": f"{letter.address}",
                    "Date": f"{letter.updated_at.date()}",
                    "Status": f"{letter.status}",
                    "Courier": f"{letter.courier.full_name}" if letter.courier else None,
                    "Reason": f"{letter.reason.name}" if letter.reason else None,

                }
                letters_data.append(letter_data)

            # Create a DataFrame from the letter data
            df = pd.DataFrame(letters_data)

            # Save the DataFrame to a BytesIO object
            output = BytesIO()
            df.to_excel(output, sheet_name='Sheet1', index=False)
            output.seek(0)  # Move the cursor to the beginning of the BytesIO object

            # Save the BytesIO object to the response field of upload_excel
            upload_excel.response.save(f"{datetime.now().date()}_{upload_excel.name}.xlsx", ContentFile(output.read()))

            os.remove(target_directory)

            print("Success")
            return upload_excel.response
        else:
            print("No letters found for the provided upload_excel.")
    except Exception as e:
        print(e, 'error')
        print("Failed")
