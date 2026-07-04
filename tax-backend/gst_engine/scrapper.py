import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

CHROME_SERVICE = Service(ChromeDriverManager().install())
def create_driver():

    chrome_options = Options()

    # Faster page loading
    chrome_options.page_load_strategy = "eager"

    # Run Chrome in background
    chrome_options.add_argument("--headless=new")

    # Browser settings
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Faster execution
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--mute-audio")

    # Avoid Selenium detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )
    chrome_options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    # Disable loading unnecessary resources
    prefs = {

        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.notifications": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2

    }

    chrome_options.add_experimental_option("prefs", prefs)

    # Realistic browser identity
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=CHROME_SERVICE,options=chrome_options)

    # Hide webdriver property
    driver.execute_script("""

        Object.defineProperty(navigator, 'webdriver', {

            get: () => undefined

        });

    """)

    # Faster timeouts
    driver.set_page_load_timeout(12)
    driver.implicitly_wait(2)

    return driver

def validate_gstin(gstin):

    if gstin is None:
        return False

    gstin = gstin.strip().upper()

    pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$"

    return re.match(pattern, gstin) is not None

def empty_result():

    return {

        "source": None,

        "gstin": None,

        "legal_name": None,

        "trade_name": None,

        "business_name": None,

        "gst_status": None,

        "registration_date": None,

        "last_updated": None,

        "constitution": None,

        "taxpayer_type": None,

        "principal_place": None,

        "nature_of_business": None,

        "state": None,

        "district": None,

        "center_jurisdiction": None,

        "state_jurisdiction": None,

        "websites_checked": []

    }

def get_text(driver, by, value):

    try:

        element = driver.find_element(by, value)

        text = element.text.strip()

        if text == "":
            return None

        return text

    except:

        return None
def get_value_by_label(driver, label):

    try:

        xpath = f"//*[contains(text(),'{label}')]/following::*[1]"

        value = driver.find_element(By.XPATH, xpath)

        return value.text.strip()

    except:

        return None
    
def wait_element(driver, by, value, timeout=15):

    return WebDriverWait(driver, timeout).until(

        EC.visibility_of_element_located((by, value))

    )
def website_limit(driver):

    page = driver.page_source.lower()

    keywords = [

        "too many requests",

        "rate limit exceeded",

        "429",

        "daily search limit",

        "captcha",

        "access denied"

    ]

    return any(keyword in page for keyword in keywords)
def has_sufficient_data(data):

    important_fields = [

        "business_name",

        "legal_name",

        "gst_status",

        "registration_date",

        "principal_place"

    ]

    filled = 0

    for field in important_fields:

        if data.get(field):

            filled += 1

    return filled >= 4

def gst_search(gstin):

    gstin = gstin.strip().upper()

    if not validate_gstin(gstin):

        return {

            "status": "failed",

            "message": "Invalid GST Number"

        }

    websites = [

        ("ClearTax", search_cleartax),

        ("MastersIndia", search_mastersindia),

        ("Cashfree", search_cashfree),

        ("Razorpay", search_razorpay),

        ("Tally", search_tally)

    ]

    final_data = empty_result()

    final_data["gstin"] = gstin

    website_status = {}

    driver = None

    try:

        driver = create_driver()

        for website_name, website_function in websites:

            print(f"\nChecking {website_name}")

            try:

                result = website_function(driver, gstin)

                if result is None:

                    print(f"{website_name} returned no data.")

                    website_status[website_name] = "Failed"

                    continue

                print(f"{website_name} Success")

                website_status[website_name] = "Success"

                final_data["websites_checked"].append(website_name)

                # Merge Data
                for key, value in result.items():

                    if value in [None, ""]:

                        continue

                    current = final_data.get(key)

                    # Fill empty field
                    if current in [None, ""]:

                        final_data[key] = value

                    # Prefer longer address
                    elif key == "principal_place":

                        if len(str(value)) > len(str(current)):

                            final_data[key] = value

                    # Prefer detailed business activity
                    elif key == "nature_of_business":

                        if len(str(value)) > len(str(current)):

                            final_data[key] = value

                    # Prefer longer legal name
                    elif key == "legal_name":

                        if len(str(value)) > len(str(current)):

                            final_data[key] = value

                    # Keep first business name
                    elif key == "business_name":

                        pass

                    # Generic fallback
                    elif len(str(value)) > len(str(current)):

                        final_data[key] = value

                # Intelligent Fallback
                if has_sufficient_data(final_data):

                    print("\nEnough GST information collected.")

                    break

            except Exception as e:

                print(f"{website_name} Error : {e}")

                website_status[website_name] = "Error"

                continue

        driver.quit()

        # Source Information
        if len(final_data["websites_checked"]) > 1:

            final_data["source"] = "Multiple Sources"

        elif len(final_data["websites_checked"]) == 1:

            final_data["source"] = final_data["websites_checked"][0]

        else:

            final_data["source"] = "No Source"

        final_data["website_status"] = website_status

        final_data["total_websites_checked"] = len(
            final_data["websites_checked"]
        )

        final_data["successful_sources"] = ", ".join(
            final_data["websites_checked"]
        )

        useful_fields = [

            key

            for key, value in final_data.items()

            if key not in [

                "source",

                "websites_checked",

                "website_status",

                "successful_sources",

                "total_websites_checked"

            ]

            and value not in [None, ""]

        ]

        if len(useful_fields) <= 1:

            return {

                "status": "failed",

                "message": "No GST information found."

            }

        return {

            "status": "success",

            "data": final_data

        }

    except Exception as e:

        if driver:

            try:

                driver.quit()

            except:

                pass

        return {

            "status": "failed",

            "message": str(e)

        }
def get_table_value(driver, heading):

    try:

        xpath = f"//th[contains(text(),'{heading}')]/following-sibling::td"

        return driver.find_element(

            By.XPATH,

            xpath

        ).text.strip()

    except:

        return None
def get_razorpay_value(driver, label):

    try:

        xpath = f"//p[contains(text(),'{label}')]/following-sibling::h5"

        return driver.find_element(
            By.XPATH,
            xpath
        ).text.strip()

    except:

        return None
def get_cashfree_value(driver, label):

    try:

        xpath = f"//div[contains(text(),'{label}')]/following-sibling::div"

        return driver.find_element(
            By.XPATH,
            xpath
        ).text.strip()

    except:

        return None
def get_info_cell(driver, label):

    try:

        cells = driver.find_elements(By.CLASS_NAME, "info-cell")

        for cell in cells:

            lbl = cell.find_element(By.CLASS_NAME, "info-lbl").text.strip()

            if lbl.lower() == label.lower():

                return cell.find_element(
                    By.CLASS_NAME,
                    "info-val"
                ).text.strip()

    except:
        pass

    return None
def get_value_by_anchor(driver, anchor):

    try:

        xpath = f"//span[@id='{anchor}']/following-sibling::h4/following-sibling::small"

        element = driver.find_element(
            By.XPATH,
            xpath
        )

        return element.text.strip()

    except:

        return None
def search_cleartax(driver, gstin):

    print("\n-------------------------------")
    print("Searching in ClearTax")
    print("-------------------------------")

    try:

        data = empty_result()

        data["source"] = "ClearTax"

        data["gstin"] = gstin

        driver.get("https://cleartax.in/gst-number-search/")

        # Wait for search box
        search_box = WebDriverWait(driver,8).until(

            EC.presence_of_element_located(
                (By.ID,"input")
            )

        )

        search_box.clear()

        search_box.send_keys(gstin)

        # Click SEARCH button

        search_button = WebDriverWait(driver,8).until(

            EC.element_to_be_clickable(

                (By.XPATH,"//button[contains(text(),'SEARCH')]")

            )

        )

        search_button.click()

        print("GST Submitted")

        # Wait until Business Name appears

        WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (
                    By.XPATH,
                    "//span[@id='Business Name']"
                )

            )

        )

        print("Result Loaded")

        # Extract Data

        data["business_name"] = get_value_by_anchor(

            driver,

            "Business Name"

        )

        data["principal_place"] = get_value_by_anchor(

            driver,

            "Address"

        )

        data["constitution"] = get_value_by_anchor(

            driver,

            "Entity Type"

        )

        data["nature_of_business"] = get_value_by_anchor(

            driver,

            "Nature of business"

        )

        data["registration_date"] = get_value_by_anchor(

            driver,

            "Registration Date"

        )

        data["taxpayer_type"] = get_value_by_anchor(

            driver,

            "Registration Type"

        )

        data["center_jurisdiction"] = get_value_by_anchor(

            driver,

            "Department Code"

        )

        data["state"] = get_value_by_anchor(

            driver,

            "Address"

        )

        print("ClearTax Success")

        return data

    except TimeoutException:

        print("ClearTax : Result not found")

        return None

    except Exception as e:

        print("ClearTax Error :",e)

        return None
    
def search_gstverify(driver, gstin):

    print("\n-------------------------------")
    print("Searching in GSTVerify")
    print("-------------------------------")

    try:

        data = empty_result()

        data["source"] = "GSTVerify"

        data["gstin"] = gstin

        driver.get("https://gstverify.co.in/")

        search_box = WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (By.NAME,"gstin")

            )

        )

        search_box.clear()

        search_box.send_keys(gstin)

        driver.find_element(

            By.XPATH,

            "//button[contains(text(),'Search')]"

        ).click()

        WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (By.CLASS_NAME,"info-grid")

            )

        )

        # Top section

        data["legal_name"] = get_text(

            driver,

            By.TAG_NAME,

            "h2"

        )

        data["business_name"] = get_text(

            driver,

            By.CSS_SELECTOR,

            "div[style*='font-size:.9rem']"

        )

        # Information Grid

        data["constitution"] = get_info_cell(driver,"Constitution")

        data["taxpayer_type"] = get_info_cell(driver,"Taxpayer Type")

        data["registration_date"] = get_info_cell(driver,"Registration Date")

        data["last_updated"] = get_info_cell(driver,"Last Updated")

        data["state"] = get_info_cell(driver,"State")

        data["district"] = get_info_cell(driver,"District")

        data["principal_place"] = get_info_cell(driver,"Principal Place of Business")

        data["nature_of_business"] = get_info_cell(driver,"Nature of Business")

        print("GSTVerify Success")

        return data

    except Exception as e:

        print("GSTVerify Error :",e)

        return None
def search_cashfree(driver, gstin):

    print("\n-------------------------------")
    print("Searching in Cashfree")
    print("-------------------------------")

    try:

        data = empty_result()

        data["source"] = "Cashfree"

        data["gstin"] = gstin

        driver.get(
            "https://www.cashfree.com/gst-verification/"
        )

        # Wait for input box
        search_box = WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (
                    By.NAME,
                    "gstNumber"
                )

            )

        )

        search_box.clear()

        search_box.send_keys(gstin)

        # Click Verify button
        verify_button = driver.find_element(

            By.XPATH,

            "//button[@type='submit']"

        )

        verify_button.click()

        print("GST Submitted")

        # Wait until Legal Name appears
        WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (

                    By.XPATH,

                    "//div[contains(text(),'Legal Name of Business')]"

                )

            )

        )

        print("Result Loaded")

        data["legal_name"] = get_cashfree_value(
            driver,
            "Legal Name of Business:"
        )

        data["gst_status"] = get_cashfree_value(
            driver,
            "GST in Status :"
        )

        data["registration_date"] = get_cashfree_value(
            driver,
            "Date of Registration :"
        )

        data["last_updated"] = get_cashfree_value(
            driver,
            "Last Update Date :"
        )

        data["nature_of_business"] = get_cashfree_value(
            driver,
            "Nature of Business Activities :"
        )

        data["constitution"] = get_cashfree_value(
            driver,
            "Constitution of Business:"
        )

        data["taxpayer_type"] = get_cashfree_value(
            driver,
            "Tax Payer:"
        )

        data["center_jurisdiction"] = get_cashfree_value(
            driver,
            "Center Jurisdiction:"
        )

        data["state_jurisdiction"] = get_cashfree_value(
            driver,
            "State Jurisdiction:"
        )

        data["principal_place"] = get_cashfree_value(
            driver,
            "Principal Place Address:"
        )

        print("Cashfree Success")

        return data

    except TimeoutException:

        print("Cashfree Result Not Found")

        return None

    except Exception as e:

        print("Cashfree Error :", e)

        return None

def search_razorpay(driver, gstin):

    print("\n-------------------------------")
    print("Searching in Razorpay")
    print("-------------------------------")

    try:

        data = empty_result()

        data["source"] = "Razorpay"
        data["gstin"] = gstin

        driver.get("https://razorpay.com/gst-number-search/")

        search_box = WebDriverWait(driver,8).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder]")
            )
        )

        search_box.clear()
        search_box.send_keys(gstin)

        driver.find_element(
            By.XPATH,
            "//button[@type='submit']"
        ).click()

        WebDriverWait(driver,8).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//h3[contains(text(),'Business Details')]"
                )
            )
        )

        data["legal_name"] = get_razorpay_value(
            driver,
            "Legal Name of Business"
        )

        data["gst_status"] = get_razorpay_value(
            driver,
            "GSTIN Status"
        )

        data["constitution"] = get_razorpay_value(
            driver,
            "Constitution of Business"
        )

        data["taxpayer_type"] = get_razorpay_value(
            driver,
            "Taxpayer Type"
        )

        print("Razorpay Success")

        return data

    except Exception as e:

        print("Razorpay Error :", e)

        return None

def search_mastersindia(driver, gstin):

    print("\n-------------------------------")
    print("Searching in MastersIndia")
    print("-------------------------------")

    try:

        data = empty_result()

        data["source"] = "MastersIndia"

        data["gstin"] = gstin

        driver.get(
            "https://www.mastersindia.co/gst-number-search-and-gstin-verification/"
        )

        # Wait for search box
        search_box = WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (By.XPATH,"//input[@placeholder='XXXAAAYYYYZ01Z5']")

            )

        )

        search_box.clear()

        search_box.send_keys(gstin)

        # Click Search
        search_button = driver.find_element(

            By.XPATH,

            "//button//span[text()='Search']"

        )

        search_button.click()

        print("GST Submitted")

        # Wait for result table

        WebDriverWait(driver,8).until(

            EC.presence_of_element_located(

                (

                    By.XPATH,

                    "//table"

                )

            )

        )

        print("Result Loaded")

        data["legal_name"] = get_table_value(

            driver,

            "Legal Name of Business"

        )

        data["principal_place"] = get_table_value(

            driver,

            "Principal Place of Business"

        )

        data["state_jurisdiction"] = get_table_value(

            driver,

            "State Jurisdiction"

        )

        data["center_jurisdiction"] = get_table_value(

            driver,

            "Centre Jurisdiction"

        )

        data["registration_date"] = get_table_value(

            driver,

            "Date of Registration"

        )

        data["constitution"] = get_table_value(

            driver,

            "Constitution of Business"

        )

        data["taxpayer_type"] = get_table_value(

            driver,

            "Taxpayer Type"

        )

        data["gst_status"] = get_table_value(

            driver,

            "GSTIN Status"

        )

        print("MastersIndia Success")

        return data

    except TimeoutException:

        print("MastersIndia Result Not Found")

        return None

    except Exception as e:

        print("MastersIndia Error :",e)

        return None

def search_tally(driver,gstin):

    try:

        print("Opening Tally...")

        driver.get("https://tallysolutions.com/business-tools-templates/gstin-verification-search/")

        WebDriverWait(driver,8).until(
            EC.presence_of_element_located((By.ID,"gstin"))
        )

        driver.find_element(By.ID,"gstin").send_keys(gstin)

        driver.find_element(By.ID,"generateDetailsBtn").click()

        WebDriverWait(driver,5).until(EC.presence_of_element_located((...)))

        with open("tally.html","w",encoding="utf-8") as f:
            f.write(driver.page_source)

        if website_limit(driver):
            return None

        data=empty_result()

        data["source"]="Tally"

        data["legal_name"]=get_text(driver,By.ID,"leagalName")

        data["business_name"]=get_text(driver,By.ID,"tradeName")

        data["registration_date"]=get_text(
            driver,
            By.ID,
            "effectiveDateOfRegistration"
        )

        data["constitution"]=get_text(
            driver,
            By.ID,
            "constitutionOfBusiness"
        )

        data["gst_status"]=get_text(
            driver,
            By.ID,
            "gstinStatus"
        )

        data["taxpayer_type"]=get_text(
            driver,
            By.ID,
            "taxpayerType"
        )

        data["principal_place"]=get_text(
            driver,
            By.ID,
            "principalPlaceOfBusiness"
        )

        data["nature_of_business"]=get_text(
            driver,
            By.ID,
            "natureOfBusinessActivities"
        )

        return data

    except Exception as e:

        print(e)

        return None

def search_company(driver, company_name):

    print("\n-------------------------------")
    print("Searching Company Name")
    print("-------------------------------")

    driver.get("https://cleartax.in/gst-number-search/")

    wait = WebDriverWait(driver, 8)

    try:

        search_box = wait.until(
            EC.presence_of_element_located(
                (By.ID, "input")
            )
        )

        search_box.clear()
        search_box.send_keys(company_name)

        driver.find_element(
            By.XPATH,
            "//button[contains(text(),'SEARCH')]"
        ).click()

        print("Company Search Submitted")

    except Exception as e:

        print("Unable to search company :", e)
        return None

    try:

        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'items-start') and contains(@class,'cursor-pointer')]"
                )
            )
        )

        print("Company List Loaded")

    except:

        print("No companies found.")
        return None

    companies = []

    try:

        rows = driver.find_elements(By.XPATH,"//div[contains(@class,'items-start') and contains(@class,'cursor-pointer')]")

        rows = rows[:5]

        print("Rows Found :", len(rows))

        for row in rows:

            try:

                name = row.find_element(
                    By.XPATH,
                    ".//div[contains(@class,'font-semibold')]"
                ).text.strip()

                state = row.find_element(
                    By.XPATH,
                    ".//div[contains(@class,'text-font-200')]"
                ).text.strip()

                gstin = row.find_element(
                    By.XPATH,
                    ".//div[contains(@class,'w-1/4')]"
                ).text.strip()

                companies.append({

                    "business_name": name,

                    "gstin": gstin,

                    "state": state

                })

                print(name, state, gstin)

            except Exception as e:

                print("Skipping Row :", e)

        print(f"Found {len(companies)} companies")

        return companies

    except Exception as e:

        print("Extraction Error :", e)

        return None
def run_scraper(query):

    query = query.strip()

    # GSTIN Search
    if validate_gstin(query):

        return gst_search(query.upper())

    # Company Name Search
    driver = None

    try:

        driver = create_driver()

        companies = search_company(driver, query)

        driver.quit()

        if not companies:

            return {

                "status": "failed",

                "message": "No companies found."

            }

        return {

            "status": "company_list",

            "companies": companies

        }

    except Exception as e:

        if driver:

            try:

                driver.quit()

            except:

                pass

        return {

            "status": "failed",

            "message": str(e)

        }
    
def main():

    query = input("Enter GSTIN or Company Name: ")

    result = run_scraper(query)

    print(result)


if __name__ == "__main__":
    main()