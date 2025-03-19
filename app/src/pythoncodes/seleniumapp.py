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

# stdout'u UTF-8 olarak ayarla
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Komut satırından JSON formatında IP listesi al
try:
    ipAddressArg = sys.argv[1]  # Komut satırından argümanı al
    bios_ip_list = json.loads(ipAddressArg)  # JSON verisini listeye çevir

    # Gelen veriyi doğrula
    if not isinstance(bios_ip_list, list) or not all(isinstance(item, dict) and "ipAddress" in item for item in bios_ip_list):
        raise ValueError("Geçersiz JSON formatı!")

except (IndexError, json.JSONDecodeError, ValueError) as e:
    print(json.dumps({"error": f"Hatalı giriş verisi: {str(e)}"}))
    sys.exit(1)

# Firefox için başsız seçenekler
firefox_options = Options()
firefox_options.add_argument("--headless")  # Arka planda çalıştır
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# GeckoDriver yolu
driver_path = r"D:\ProgramFiles\GeckoDriver\geckodriver.exe"

# Logları saklamak için liste
log_results = []

# Her IP adresi için işlemi gerçekleştir
for item in bios_ip_list:
    ip_address = item["ipAddress"]
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    driver = webdriver.Firefox(service=Service(driver_path), options=firefox_options)
    result = {"ipAddress": ip_address, "startTime": start_time, "status": "", "accessToken": None, "endTime": None}
    
    try:
        driver.get(f"http://{ip_address}/")
        wait = WebDriverWait(driver, 20)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))
        
        username_field.send_keys("user2")
        password_field.send_keys("user2user2")
        login_button.click()
        
        time.sleep(3)
        access_token = driver.execute_script("return localStorage.getItem('accessToken');")
        
        result["status"] = "Success" if access_token else "Failed"
        result["accessToken"] = access_token
    except Exception as e:
        result["status"] = "Error"
        result["errorMessage"] = str(e)
    finally:
        result["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_results.append(result)
        driver.quit()

# JSON formatında çıktı ver
print(json.dumps(log_results, indent=4, ensure_ascii=False))

# python D:/staj/PythonScriptingApp/app/src/pythoncodes/seleniumapp.py "[{\"ipAddress\":\"127.0.0.1:3006\"}]"