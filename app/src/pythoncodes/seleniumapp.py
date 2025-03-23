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

# Set stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get IP list in JSON format from command line
try:
    ipAddressArg = sys.argv[1]  # Get argument from command line
    bios_ip_list = json.loads(ipAddressArg)  # Convert JSON to list

    # Validate the incoming data
    if not isinstance(bios_ip_list, list) or not all(isinstance(item, dict) and "ipAddress" in item for item in bios_ip_list):
        raise ValueError("Invalid JSON format!")

except (IndexError, json.JSONDecodeError, ValueError) as e:
    print(json.dumps({"error": f"Invalid input data: {str(e)}"}))
    sys.exit(1)

# Firefox options for headless mode
firefox_options = Options()
firefox_options.add_argument("--headless")  # Run in the background
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
firefox_options.set_preference("intl.accept_languages", "en-US,en")  # English output

# GeckoDriver path
driver_path = r"D:\ProgramFiles\GeckoDriver\geckodriver.exe"

# List to store logs
log_results = []

# Perform the operation for each IP address
for item in bios_ip_list:
    ip_address = item["ipAddress"]
    biosid = item["biosid"]
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    driver = webdriver.Firefox(service=Service(driver_path), options=firefox_options)
    result = {"biosid": biosid, "ipAddress": ip_address, "startTime": start_time, "status": "", "endTime": None}
    
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
    except Exception as e:
        result["status"] = "Error"
        error_message = str(e)
        
        if "about:neterror" in error_message:
            error_message = "Connection error: Unable to connect to the server or invalid IP address."
        elif "RemoteError" in error_message:
            error_message = "Selenium RemoteError: WebDriver connection problem."
        else:
            error_message = f"Unexpected error: {error_message}"
        
        result["errorMessage"] = error_message
    finally:
        result["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_results.append(result)
        driver.quit()

# Output in JSON format
print(json.dumps(log_results, indent=4, ensure_ascii=False))
