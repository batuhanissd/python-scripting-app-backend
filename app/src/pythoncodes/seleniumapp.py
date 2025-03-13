import io 
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# stdout'u UTF-8 olarak ayarlıyoruz
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Komut satırından JSON formatında IP listesi al ve listeye çevir
try:
    ipAddressArg = sys.argv[1]  # Komut satırından argümanı al
    bios_ip_list = json.loads(ipAddressArg)  # JSON verisini listeye çevir

    # Eğer gelen veri bir liste değilse, hata fırlat
    if not isinstance(bios_ip_list, list):
        raise ValueError("Gelen JSON bir liste değil!")

    # Her elemanın bir sözlük (dict) olup olmadığını kontrol et
    if not all(isinstance(item, dict) and "ipAddress" in item for item in bios_ip_list):
        raise ValueError("Her eleman bir sözlük olmalı ve 'ipAddress' anahtarı içermelidir!")

except (IndexError, json.JSONDecodeError, ValueError) as e:
    print(f"Hatalı giriş verisi! Lütfen geçerli bir JSON formatı girin. Hata: {e}")
    sys.exit(1)

# Firefox için başsız seçenekler
firefox_options = Options()
firefox_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırır

# Firefox binary yolunu belirtmek için raw string kullan
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'  # Raw string ile doğru bir yol belirt

# GeckoDriver yolu (Kendi sistemine göre güncelle)
driver_path = r"D:\ProgramFiles\GeckoDriver\geckodriver.exe"  # raw string kullanımı

# Her IP adresi için işlemi gerçekleştir
for item in bios_ip_list:
    ip_address = item["ipAddress"]  # IP adresini al
    
    print(f"\nBağlanıyor: {ip_address}")

    # Selenium WebDriver başlat
    driver = webdriver.Firefox(service=Service(driver_path), options=firefox_options)
    
    try:
        driver.get(f"http://{ip_address}/")  # IP'yi parametrik hale getirdik
        
        wait = WebDriverWait(driver, 20)  # Maksimum 20 saniye bekler
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))

        # Kullanıcı adı ve şifreyi gir
        username_field.send_keys("user2")
        password_field.send_keys("user2user2")

        # Giriş butonuna tıkla
        login_button.click()

        # Sayfanın yönlendirilmesi için kısa bekleme
        time.sleep(3)

        # localStorage'dan accessToken'i al
        access_token = driver.execute_script("return localStorage.getItem('accessToken');")

        if access_token:
            print(f"✅ {ip_address} için Access Token: {access_token}")
        else:
            print(f"❌ {ip_address} için Access Token bulunamadı!")

    except Exception as e:
        print(f"❌ {ip_address} için hata oluştu: {str(e)}")

    finally:
        driver.quit()  # Tarayıcıyı her durumda kapat
