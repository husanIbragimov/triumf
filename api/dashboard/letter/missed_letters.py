import requests
from selenium import webdriver

list_ = [8000269586, 8000269735, 8000271530, 8000284208, 8000284279, 8000295334, 8000269609, 8000269638]
list_.sort()

driver = webdriver.Chrome()

for i in list_:
    response = requests.get(f"https://api.triumf-express.uz/media/pdfs/235/{i}.pdf")
    file_name = f'{i}.pdf'
    with open(file_name, 'wb') as f:
        f.write(response.content)
