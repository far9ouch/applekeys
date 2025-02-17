from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
import sys
from datetime import datetime

def setup_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.binary_location = os.getenv("CHROME_BIN", "")
        
        # Use ChromeDriver from PATH in production, local file in development
        if os.getenv("CHROME_BIN"):
            service = Service()
        else:
            service = Service("chromedriver.exe")
            
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {str(e)}")
        print("Please make sure Chrome browser is installed and up to date")
        sys.exit(1)

def extract_code(url):
    code_match = re.search(r'code=([A-Z0-9]+)', url)
    if code_match:
        return code_match.group(1)
    return None

def save_key_to_file(key):
    filename = "apple_tv_keys.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a") as f:
        f.write(f"[{timestamp}] APPLE TV+ 1 Month key: {key}\n")

def get_apple_tv_key(driver):
    initial_url = "https://redeem.services.apple/uberappletv?itscg=MC_30000&itsct=atvp_brand_omd&mttn3pid=uber&mttnagencyid=a5e&mttncc=US&mttnsiteid=143238&mttnsubad=04621974"
    
    try:
        driver.get(initial_url)
        
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/div/section/div/div/div[4]/div/button"))
        )
        button.click()
        
        time.sleep(1.5)  # Reduced wait time
        final_url = driver.current_url
        
        code = extract_code(final_url)
        if code:
            save_key_to_file(code)
            print(f"Generated key: {code}")
            return code
        return None
            
    except Exception as e:
        print(f"Error generating key: {str(e)}")
        return None

if __name__ == "__main__":
    driver = setup_driver()
    try:
        get_apple_tv_key(driver)
    finally:
        driver.quit() 