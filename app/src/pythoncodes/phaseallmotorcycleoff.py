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
    biosid = item.get("biosid", "Unknown") #portno icin biosid kullaniliyor ama sadece ftpde kullaniliyor. yine de ekledim silinebilir.
    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    driver = webdriver.Firefox(service=Service(driver_path), options=firefox_options)
    result = {"processType": "motoroff", "biosid": biosid, "ipAddress": ip_address, "startTime": start_time, "connectionStatus": "", "xmlStatus": "", "endTime": None}
    session_tag = None
    
    try:
        driver.get(f"http://{ip_address}/")
        #username_field = driver.find_element(By.ID, "username")
        #password_field = driver.find_element(By.ID, "password")
        #login_button = driver.find_element(By.CSS_SELECTOR, "button[ng-click='login()']")
        # bu ust kisim muhammet abinin

        wait = WebDriverWait(driver, 20)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))
        # bu ust kisim da windows icin benim kodum

        username_field.send_keys("user1")
        password_field.send_keys("user1user1")
        login_button.click()
        
        time.sleep(5)
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
        
        result["connectionErrorMessage"] = error_message
    finally:
        driver.quit()
        result["endTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_results.append(result)
    
    if session_tag:
        xml_data = f"""
<?xml version: "1.0" encoding="UTF-8"?>
<PostHVT
	xmlns="http://www.isapi.org/ver20/XMLSchema" version="2.0">
	<relatedLaneCount>2</relatedLaneCount>
	<backupType>1</backupType>
	<DetectSnapType>
		<intervalType>time</intervalType>
		<IntervalList>
			<Interval>
				<intervalValue>100</intervalValue>
			</Interval>
			<Interval>
				<intervalValue>100</intervalValue>
			</Interval>
		</IntervalList>
		<post>true</post>
		<postCapNo>1</postCapNo>
		<reverse>false</reverse>
		<reverseCapNo>2</reverseCapNo>
		<overSpeed>true</overSpeed>
		<overSpeedCapNo>2</overSpeedCapNo>
		<lowSpeed>false</lowSpeed>
		<lowSpeedCapNo>2</lowSpeedCapNo>
		<driveLine>false</driveLine>
		<driveLineCapNo>2</driveLineCapNo>
		<driveLineSensitivity>30</driveLineSensitivity>
		<banSign>false</banSign>
		<banSignCapNo>2</banSignCapNo>
		<changeLane>false</changeLane>
		<changeLaneCapNo>2</changeLaneCapNo>
		<safeBelt>false</safeBelt>
		<safeBeltCapNo>2</safeBeltCapNo>
		<uphone>false</uphone>
		<uphoneCapNo>2</uphoneCapNo>
		<gasser>
			<enabled>false</enabled>
			<gasserCapNo>3</gasserCapNo>
			<sensitivity>50</sensitivity>
			<congestionThreshold>50</congestionThreshold>
			<capInterval>5000</capInterval>
		</gasser>
		<congestion>
			<enabled>false</enabled>
			<interval>5</interval>
			<sensitivity>50</sensitivity>
			<lastTime>30</lastTime>
			<capNo>1</capNo>
		</congestion>
		<helmet>false</helmet>
		<helmetCapNo>2</helmetCapNo>
		<twoWheelPassenger>false</twoWheelPassenger>
		<twoWheelPassengerCapNo>2</twoWheelPassengerCapNo>
		<nonMotorExist>false</nonMotorExist>
		<nonMotorExistCapNo>2</nonMotorExistCapNo>
		<nonDriveWay>
			<enabled>false</enabled>
			<capNo>2</capNo>
			<lastTime>3</lastTime>
		</nonDriveWay>
		<nonMotorShed>
			<enabled>false</enabled>
			<capNo>2</capNo>
		</nonMotorShed>
		<banNonMotorSign>
			<enabled>false</enabled>
			<capNo>2</capNo>
		</banNonMotorSign>
		<nonmotorUphone>false</nonmotorUphone>
		<nonmotorUphoneCapNo>2</nonmotorUphoneCapNo>
		<copilotWithoutSafeBeltCaptureEnabled>false</copilotWithoutSafeBeltCaptureEnabled>
		<pilotsafebelt>false</pilotsafebelt>
		<vicepilotsafebelt>false</vicepilotsafebelt>
		<Smoking>
			<enabled>false</enabled>
			<capNo>2</capNo>
		</Smoking>
		<BanMotorDet>
			<enabled>false</enabled>
			<capNo>2</capNo>
		</BanMotorDet>
		<BanSignTypeList/>
	</DetectSnapType>
	<sceneMode>urban</sceneMode>
	<snapType>motor</snapType>
	<capMode>videoFrame</capMode>
	<detectMode>video</detectMode>
	<speedDetector>videoSpeed</speedDetector>
	<trigLineEffect>0</trigLineEffect>
	<carHighSpeed>180</carHighSpeed>
	<carLowSpeed>0</carLowSpeed>
	<bigCarHighSpeed>180</bigCarHighSpeed>
	<bigCarLowSpeed>0</bigCarLowSpeed>
	<LaneParamList>
		<LaneParam>
			<laneId>1</laneId>
			<laneNO>1</laneNO>
			<relatedDriveWay>1</relatedDriveWay>
			<laneUsage>carriageWay</laneUsage>
			<laneType>other</laneType>
			<laneDirectionType>0</laneDirectionType>
			<carDriveDirect>up2down</carDriveDirect>
			<signSpeed>70</signSpeed>
			<speedLimit>80</speedLimit>
			<lowSpeedLimit>30</lowSpeedLimit>
			<bigCarSignSpeed>70</bigCarSignSpeed>
			<bigCarSpeedLimit>80</bigCarSpeedLimit>
			<bigCarLowSpeedLimit>20</bigCarLowSpeedLimit>
			<recordEnable>false</recordEnable>
			<recordType>preRecord</recordType>
			<preRecordTime>0</preRecordTime>
			<recordDelayTime>0</recordDelayTime>
			<recordTimeOut>0</recordTimeOut>
			<beginTime>2</beginTime>
			<Radar>
				<radarType>multiLaneSSTK</radarType>
				<enableRadarTestMode>false</enableRadarTestMode>
				<radarSensitivity>0</radarSensitivity>
				<radarAngle>0</radarAngle>
				<validRadarSpeedTime>2000</validRadarSpeedTime>
				<radarLinearCorrection>1.0</radarLinearCorrection>
				<radarConstantCorrection>0</radarConstantCorrection>
				<radarRS485>1</radarRS485>
			</Radar>
			<banTrucksTimeSwitchList>
				<banTrucksTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
			</banTrucksTimeSwitchList>
			<emergencyTimeSwitchList>
				<emergencyTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
			</emergencyTimeSwitchList>
			<IOOutList>
				<IOOut>
					<id>1</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>2</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>3</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>4</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>5</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>6</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>7</id>
					<enabled>true</enabled>
				</IOOut>
			</IOOutList>
			<flashMode>together</flashMode>
			<LaneLine>
				<lineName>laneLine</lineName>
				<lineType>white</lineType>
				<RegionCoordinatesList>
					<RegionCoordinates>
						<positionX>307</positionX>
						<positionY>41</positionY>
					</RegionCoordinates>
					<RegionCoordinates>
						<positionX>22</positionX>
						<positionY>919</positionY>
					</RegionCoordinates>
				</RegionCoordinatesList>
			</LaneLine>
			<busWayTimeSwitchList>
				<busWayTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
			</busWayTimeSwitchList>
		</LaneParam>
		<LaneParam>
			<laneId>2</laneId>
			<laneNO>2</laneNO>
			<relatedDriveWay>2</relatedDriveWay>
			<laneUsage>carriageWay</laneUsage>
			<laneType>other</laneType>
			<laneDirectionType>0</laneDirectionType>
			<carDriveDirect>up2down</carDriveDirect>
			<signSpeed>70</signSpeed>
			<speedLimit>80</speedLimit>
			<lowSpeedLimit>30</lowSpeedLimit>
			<bigCarSignSpeed>70</bigCarSignSpeed>
			<bigCarSpeedLimit>80</bigCarSpeedLimit>
			<bigCarLowSpeedLimit>20</bigCarLowSpeedLimit>
			<recordEnable>false</recordEnable>
			<recordType>preRecord</recordType>
			<preRecordTime>0</preRecordTime>
			<recordDelayTime>0</recordDelayTime>
			<recordTimeOut>0</recordTimeOut>
			<beginTime>2</beginTime>
			<Radar>
				<radarType>multiLaneSSTK</radarType>
				<enableRadarTestMode>false</enableRadarTestMode>
				<radarSensitivity>0</radarSensitivity>
				<radarAngle>0</radarAngle>
				<validRadarSpeedTime>2000</validRadarSpeedTime>
				<radarLinearCorrection>1.0</radarLinearCorrection>
				<radarConstantCorrection>0</radarConstantCorrection>
				<radarRS485>2</radarRS485>
			</Radar>
			<banTrucksTimeSwitchList>
				<banTrucksTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</banTrucksTimeSwitch>
			</banTrucksTimeSwitchList>
			<emergencyTimeSwitchList>
				<emergencyTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</emergencyTimeSwitch>
			</emergencyTimeSwitchList>
			<IOOutList>
				<IOOut>
					<id>1</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>2</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>3</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>4</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>5</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>6</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>7</id>
					<enabled>true</enabled>
				</IOOut>
			</IOOutList>
			<flashMode>together</flashMode>
			<LaneLine>
				<lineName>laneLine</lineName>
				<lineType>white</lineType>
				<RegionCoordinatesList>
					<RegionCoordinates>
						<positionX>510</positionX>
						<positionY>38</positionY>
					</RegionCoordinates>
					<RegionCoordinates>
						<positionX>446</positionX>
						<positionY>954</positionY>
					</RegionCoordinates>
				</RegionCoordinatesList>
			</LaneLine>
			<busWayTimeSwitchList>
				<busWayTimeSwitch>
					<timeId>1</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>2</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>3</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>4</timeId>
					<startHour>00</startHour>
					<startMinute>00</startMinute>
					<endHour>00</endHour>
					<endMinute>00</endMinute>
				</busWayTimeSwitch>
			</busWayTimeSwitchList>
		</LaneParam>
		<LaneParam>
			<laneId>3</laneId>
			<laneNO>3</laneNO>
			<relatedDriveWay>3</relatedDriveWay>
			<laneUsage>carriageWay</laneUsage>
			<laneType>other</laneType>
			<laneDirectionType>0</laneDirectionType>
			<carDriveDirect>up2down</carDriveDirect>
			<signSpeed>70</signSpeed>
			<speedLimit>80</speedLimit>
			<lowSpeedLimit>30</lowSpeedLimit>
			<bigCarSignSpeed>70</bigCarSignSpeed>
			<bigCarSpeedLimit>80</bigCarSpeedLimit>
			<bigCarLowSpeedLimit>20</bigCarLowSpeedLimit>
			<recordEnable>false</recordEnable>
			<recordType>preRecord</recordType>
			<preRecordTime>0</preRecordTime>
			<recordDelayTime>0</recordDelayTime>
			<recordTimeOut>0</recordTimeOut>
			<beginTime>2</beginTime>
			<Radar>
				<radarType>multiLaneSSTK</radarType>
				<enableRadarTestMode>false</enableRadarTestMode>
				<radarSensitivity>0</radarSensitivity>
				<radarAngle>0</radarAngle>
				<validRadarSpeedTime>2000</validRadarSpeedTime>
				<radarLinearCorrection>1.0</radarLinearCorrection>
				<radarConstantCorrection>0</radarConstantCorrection>
				<radarRS485>3</radarRS485>
			</Radar>
			<banTrucksTimeSwitchList>
				<banTrucksTimeSwitch>
					<timeId>1</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>2</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>3</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</banTrucksTimeSwitch>
				<banTrucksTimeSwitch>
					<timeId>4</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</banTrucksTimeSwitch>
			</banTrucksTimeSwitchList>
			<emergencyTimeSwitchList>
				<emergencyTimeSwitch>
					<timeId>1</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>2</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>3</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</emergencyTimeSwitch>
				<emergencyTimeSwitch>
					<timeId>4</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</emergencyTimeSwitch>
			</emergencyTimeSwitchList>
			<IOOutList>
				<IOOut>
					<id>1</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>2</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>3</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>4</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>5</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>6</id>
					<enabled>true</enabled>
				</IOOut>
				<IOOut>
					<id>7</id>
					<enabled>true</enabled>
				</IOOut>
			</IOOutList>
			<flashMode>together</flashMode>
			<LaneLine>
				<lineName>laneLine</lineName>
				<lineType>white</lineType>
				<RegionCoordinatesList>
					<RegionCoordinates>
						<positionX>658</positionX>
						<positionY>500</positionY>
					</RegionCoordinates>
					<RegionCoordinates>
						<positionX>658</positionX>
						<positionY>900</positionY>
					</RegionCoordinates>
				</RegionCoordinatesList>
			</LaneLine>
			<busWayTimeSwitchList>
				<busWayTimeSwitch>
					<timeId>1</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>23</endHour>
					<endMinute>59</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>2</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>3</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</busWayTimeSwitch>
				<busWayTimeSwitch>
					<timeId>4</timeId>
					<startHour>0</startHour>
					<startMinute>0</startMinute>
					<endHour>0</endHour>
					<endMinute>0</endMinute>
				</busWayTimeSwitch>
			</busWayTimeSwitchList>
		</LaneParam>
	</LaneParamList>
	<LaneRightBoundaryLine>
		<lineName>laneRightBoundaryLine</lineName>
		<lineType>unknown</lineType>
		<RegionCoordinatesList>
			<RegionCoordinates>
				<positionX>732</positionX>
				<positionY>39</positionY>
			</RegionCoordinates>
			<RegionCoordinates>
				<positionX>965</positionX>
				<positionY>962</positionY>
			</RegionCoordinates>
		</RegionCoordinatesList>
	</LaneRightBoundaryLine>
	<TriggerLine>
		<lineName>triggerLine</lineName>
		<RegionCoordinatesList>
			<RegionCoordinates>
				<positionX>10</positionX>
				<positionY>796</positionY>
			</RegionCoordinates>
			<RegionCoordinates>
				<positionX>985</positionX>
				<positionY>817</positionY>
			</RegionCoordinates>
		</RegionCoordinatesList>
	</TriggerLine>
	<LeftTriggerLine>
		<lineName>leftTriggerLine</lineName>
		<RegionCoordinatesList>
			<RegionCoordinates>
				<positionX>15</positionX>
				<positionY>250</positionY>
			</RegionCoordinates>
			<RegionCoordinates>
				<positionX>15</positionX>
				<positionY>750</positionY>
			</RegionCoordinates>
		</RegionCoordinatesList>
	</LeftTriggerLine>
	<RightTriggerLine>
		<lineName>rightTriggerLine</lineName>
		<RegionCoordinatesList>
			<RegionCoordinates>
				<positionX>985</positionX>
				<positionY>250</positionY>
			</RegionCoordinates>
			<RegionCoordinates>
				<positionX>985</positionX>
				<positionY>750</positionY>
			</RegionCoordinates>
		</RegionCoordinatesList>
	</RightTriggerLine>
	<ObjectDetectAera>
		<DetectAera>
			<DetectAeraCoordinatesList>
				<AeraCoordinates>
					<positionX>25</positionX>
					<positionY>25</positionY>
				</AeraCoordinates>
				<AeraCoordinates>
					<positionX>975</positionX>
					<positionY>25</positionY>
				</AeraCoordinates>
				<AeraCoordinates>
					<positionX>975</positionX>
					<positionY>975</positionY>
				</AeraCoordinates>
				<AeraCoordinates>
					<positionX>25</positionX>
					<positionY>975</positionY>
				</AeraCoordinates>
			</DetectAeraCoordinatesList>
		</DetectAera>
	</ObjectDetectAera>
	<lossDriving>0</lossDriving>
	<refineMannedIllegalCode>false</refineMannedIllegalCode>
</PostHVT>
        """
        
        try:
            url = f"http://{ip_address}/ISAPI/ITC/TriggerMode/postHVT"
            headers = {"Content-Type": "application/xml", "Sessiontag": session_tag}
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
