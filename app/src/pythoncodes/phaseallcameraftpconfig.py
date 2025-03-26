import io
import sys
import json
import time
import requests
import psycopg2
from psycopg2.extras import DictCursor
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
    ipAddressArg = sys.argv[1]
    bios_ip_list = json.loads(ipAddressArg)

    if not isinstance(bios_ip_list, list) or not all(isinstance(item, dict) and "ipAddress" in item for item in bios_ip_list):
        raise ValueError("Invalid JSON format!")
except (IndexError, json.JSONDecodeError, ValueError) as e:
    print(json.dumps({"error": f"Invalid input data: {str(e)}"}))
    sys.exit(1)

# Firefox options for headless mode
firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
firefox_options.set_preference("intl.accept_languages", "en-US,en")

# GeckoDriver path
driver_path = r"D:\ProgramFiles\GeckoDriver\geckodriver.exe"

# List to store logs
log_results = []

# Process each IP address
for item in bios_ip_list:
    ip_address = item["ipAddress"]
    bios_id = item["biosid"]

    # İlk iki karakteri al ve port numarasını oluştur
    bios_prefix = bios_id[:2]  # İlk iki karakter (örneğin "49" veya "48")
    port_no = f"21{bios_prefix}"

    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    result = {"processType": "ftpconfig", "biosid": bios_id, "ipAddress": ip_address, "startTime": start_time, "connectionStatus": "", "xmlStatus": "", "endTime": None}
    session_tag = None

    try:
        driver = webdriver.Firefox(service=Service(driver_path), options=firefox_options)
        driver.get(f"http://{ip_address}/")
        time.sleep(2)  # Sayfanın yüklenmesini bekle

        # Kullanıcı adı ve şifre giriş alanlarını bul
        #username_field = driver.find_element(By.ID, "username")
        #password_field = driver.find_element(By.ID, "password")
        #login_button = driver.find_element(By.CSS_SELECTOR, "button[ng-click='login()']")
        # bu ust kisim muhammet abinin

        wait = WebDriverWait(driver, 20)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))
        # bu ust kisim da windows icin benim kodum

        # Kullanıcı adı ve şifreyi gir
        username_field.send_keys("user1")  
        password_field.send_keys("user1user1")  
        login_button.click()

        time.sleep(5)  # Giriş işleminin tamamlanmasını bekle

        # SessionTag'i al
        session_tag = driver.execute_script("return sessionStorage.getItem('sessionTag');")

        if session_tag:
            result["connectionStatus"] = "Success"
        else:
            result["connectionStatus"] = "Failed - No sessionTag"

    except Exception as e:
        result["connectionStatus"] = "Error"
        error_message = str(e)

        if "about:neterror" in error_message:
            error_message = "Connection error: Unable to connect to the server or invalid IP address."
        elif "RemoteError" in error_message:
            error_message = "Selenium RemoteError: WebDriver connection problem."
        else:
            error_message = f"Unexpected error: {error_message}"

        result["status"] = "Error"
        result["connectionErrorMessage"] = error_message

    finally:
      if 'driver' in locals():
          try:
              driver.quit()
          except Exception as quit_error:
              result["quitError"] = f"Error quitting driver: {str(quit_error)}"
      result["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
      log_results.append(result)

    # Eğer sessionTag başarıyla alındıysa, XML verisini gönder
    if session_tag:
        xml_data = f"""
<?xml version: "1.0" encoding="UTF-8"?>
<FTPNotificationList
	xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">
	<FTPNotification>
		<id>1</id>
		<enabled>true</enabled>
		<addressingFormatType>ipaddress</addressingFormatType>
		<ipAddress>10.5.0.15</ipAddress>
		<portNo>{port_no}</portNo>
		<userName>ftp_anpr</userName>
		<uploadPath>
			<pathDepth>3</pathDepth>
			<topDirNameRule>time_date</topDirNameRule>
			<topDirName/>
			<subDirNameRule>time_hour</subDirNameRule>
			<subDirName/>
			<threeDirNameRule>customize</threeDirNameRule>
			<threeDirName>{bios_id}</threeDirName>
			<fourDirNameRule>none</fourDirNameRule>
			<fourDirName/>
			<fiveDirNameRule>none</fiveDirNameRule>
			<fiveDirName/>
			<sixDirNameRule>none</sixDirNameRule>
			<sixDirName/>
		</uploadPath>
		<ftpPicNameRuleType>ITC</ftpPicNameRuleType>
		<FTPPicNameRule>
			<ItemList>
				<Item>
					<itemID>1</itemID>
					<itemOrder>plateNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>2</itemID>
					<itemOrder>regionNation</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>3</itemID>
					<itemOrder>custom</itemOrder>
					<itemCustomStr>{bios_id}</itemCustomStr>
				</Item>
				<Item>
					<itemID>4</itemID>
					<itemOrder>time</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>5</itemID>
					<itemOrder>platePosition</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>6</itemID>
					<itemOrder>carType</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>7</itemID>
					<itemOrder>vehicleLogo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>8</itemID>
					<itemOrder>carColor</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>9</itemID>
					<itemOrder>carSpeed</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>10</itemID>
					<itemOrder>laneNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>11</itemID>
					<itemOrder>CarNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>12</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>13</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>14</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>15</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
			</ItemList>
			<delimiter>=</delimiter>
			<customStr>{bios_id}</customStr>
		</FTPPicNameRule>
		<upDataType>0</upDataType>
		<uploadPlateEnable>true</uploadPlateEnable>
		<site/>
		<roadNum/>
		<instrumentNum/>
		<direction/>
		<directionDesc/>
		<monitoringInfo1/>
		<uploadAttachedInfomation>false</uploadAttachedInfomation>
		<pathEncodingMode>utf-8</pathEncodingMode>
		<uploadFaceEnable>false</uploadFaceEnable>
		<uploadTargetEnable>false</uploadTargetEnable>
		<uploadProtocolType>FTP</uploadProtocolType>
		<attachedInfomationTypeList>
			<attachedInfomationType>
				<type/>
			</attachedInfomationType>
		</attachedInfomationTypeList>
		<connectMode>shortConnect</connectMode>
		<password>Jakarta!61</password>
	</FTPNotification>
	<FTPNotification>
		<id>2</id>
		<enabled>false</enabled>
		<addressingFormatType>ipaddress</addressingFormatType>
		<ipAddress>10.5.0.15</ipAddress>
		<portNo>{port_no}</portNo>
		<userName>ftp_anpr</userName>
		<uploadPath>
			<pathDepth>3</pathDepth>
			<topDirNameRule>time_date</topDirNameRule>
			<topDirName/>
			<subDirNameRule>time_hour</subDirNameRule>
			<subDirName/>
			<threeDirNameRule>customize</threeDirNameRule>
			<threeDirName>{bios_id}</threeDirName>
			<fourDirNameRule>none</fourDirNameRule>
			<fourDirName/>
			<fiveDirNameRule>none</fiveDirNameRule>
			<fiveDirName/>
			<sixDirNameRule>none</sixDirNameRule>
			<sixDirName/>
		</uploadPath>
		<ftpPicNameRuleType>ITC</ftpPicNameRuleType>
		<FTPPicNameRule>
			<ItemList>
				<Item>
					<itemID>1</itemID>
					<itemOrder>plateNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>2</itemID>
					<itemOrder>regionNation</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>3</itemID>
					<itemOrder>custom</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>4</itemID>
					<itemOrder>time</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>5</itemID>
					<itemOrder>platePosition</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>6</itemID>
					<itemOrder>carType</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>7</itemID>
					<itemOrder>vehicleLogo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>8</itemID>
					<itemOrder>carColor</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>9</itemID>
					<itemOrder>carSpeed</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>10</itemID>
					<itemOrder>laneNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>11</itemID>
					<itemOrder>CarNo</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>12</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>13</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>14</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
				<Item>
					<itemID>15</itemID>
					<itemOrder>none</itemOrder>
					<itemCustomStr/>
				</Item>
			</ItemList>
			<delimiter>=</delimiter>
			<customStr>{bios_id}</customStr>
		</FTPPicNameRule>
		<upDataType>0</upDataType>
		<uploadPlateEnable>true</uploadPlateEnable>
		<site/>
		<roadNum/>
		<instrumentNum/>
		<direction/>
		<directionDesc/>
		<monitoringInfo1/>
		<uploadAttachedInfomation>false</uploadAttachedInfomation>
		<pathEncodingMode>utf-8</pathEncodingMode>
		<uploadFaceEnable>false</uploadFaceEnable>
		<uploadTargetEnable>false</uploadTargetEnable>
		<uploadProtocolType>FTP</uploadProtocolType>
		<attachedInfomationTypeList/>
		<connectMode>shortConnect</connectMode>
		<password>Jakarta!61</password>
	</FTPNotification>
</FTPNotificationList>
    """  # XML verisini buraya ekleyin

        try:
            url = f"http://{ip_address}/ISAPI/ITC/TriggerMode/postHVT"
            headers = {
                "Content-Type": "application/xml",
                "Sessiontag": session_tag,
            }

            response = requests.put(url, headers=headers, data=xml_data)

            if response.status_code == 200:
              result["xmlStatus"] = "Sent"
            else:
              result["xmlStatus"] = f"Failed ({response.status_code})"
              result["xmlErrorMessage"] = "Failed to sent xmldata"

        except Exception as e:
            result["xmlErrorMessage"] = str(e)

# Output in JSON format
print(json.dumps(log_results, indent=4, ensure_ascii=False))
