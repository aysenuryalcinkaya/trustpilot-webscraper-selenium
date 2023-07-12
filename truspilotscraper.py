from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import csv
import re
import json

# Selenium WebDriver'ı başlatma

service = Service('path/to/chromedriver.exe')  # ChromeDriver'ın dizinini belirtin
driver = webdriver.Chrome(service=service)

# İstek göndermek istediğiniz URL'yi oluşturun
category = "Air & Water Transport"  # Gerçek kategoriyle değiştirin
country_name = "Denmark"  # Gerçek ülke adıyla değiştirin

# category.csv dosyasını okuyun
with open('categories.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['Category Name'] == category:
            formatted_category = row['Formatted Category']
            break
    else:
        formatted_category = None  # Kategori bulunamadığında durumu yönetin

# countries.csv dosyasını okuyun
with open('countries.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['countryname'] == country_name:
            country_code = row['countrycode']
            break
    else:
        country_code = None  # Ülke bulunamadığında durumu yönetin

# Başlangıçta sayfa numarası 1 olarak ayarlanmış URL'yi oluşturun
page_number = 1
url = f"https://www.trustpilot.com/categories/{formatted_category}?country={country_code}&page={page_number}"

# Sayfayı açın
driver.get(url)

# Sayfalamayı bulun
try:
    pagination = driver.find_element("css selector", "nav.pagination_pagination___F1qS")

    # Son sayfa bağlantısını bulun
    last_page_link = pagination.find_element("css selector", "a[data-pagination-button-last-link='true']")

    # Son sayfa numarasını alın
    page_number = last_page_link.text

    # Filtrelenmiş işletmelerin adını ve e-posta adresini depolamak için bir liste oluşturun
    filtered_businesses = []

    for i in range(1, int(page_number) + 1):
        url = f"https://www.trustpilot.com/categories/{formatted_category}?country={country_code}&page={i}"

        # Sayfayı açın
        driver.get(url)

        # Sayfanın tamamen yüklenmesini bekleyin
        driver.implicitly_wait(10)

        script_element = driver.find_element("css selector", "script#__NEXT_DATA__")
        script_text = script_element.get_attribute("innerHTML")

        # JSON verisini ayrıştırma
        data = json.loads(script_text)

        # JSON verisini kullanarak işletme bilgilerini alın
        businesses = data["props"]["pageProps"]["businessUnits"]["businesses"]

        # İşletme bilgilerini kontrol ederek filtreleyin
        for business in businesses:
            trustScore = business["trustScore"]
            numberOfReviews = business["numberOfReviews"]
            displayName = business["displayName"]
            email = business["contact"]["email"]

            if trustScore < 3.0 and numberOfReviews < 3000 and email:
                filtered_businesses.append((displayName, email))

    # Filtrelenmiş işletmelerin adını ve e-posta adresini yazdırın
    for business in filtered_businesses:
        displayName, email = business
        print("İsim:", displayName)
        print("E-posta:", email)
        print("------------------------")

    # filtered_businesses'ı bir CSV dosyasına yazın
    with open('filtered_businesses.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['İsim', 'E-posta'])
        writer.writerows(filtered_businesses)

except NoSuchElementException:
    print("Bu sayfada hiç şirket bulunamadı.")

driver.quit()

print(len(filtered_businesses))
