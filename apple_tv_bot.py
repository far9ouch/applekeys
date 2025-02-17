from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time
import re
import os
import sys
from datetime import datetime
import platform
import subprocess
import traceback

def get_chrome_version():
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        else:
            version = subprocess.check_output(['google-chrome', '--version']).decode().strip().split()[-1]
            return version
    except Exception as e:
        print(f"Error getting Chrome version: {str(e)}")
        return None

def setup_driver():
    try:
        print("Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--incognito")
        
        # Additional options for stability
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Set up Chrome binary location for Render
        if os.getenv("RENDER"):
            chrome_options.binary_location = "/usr/bin/google-chrome-stable"
            chromedriver_path = "/usr/local/bin/chromedriver"
            chrome_options.add_argument(f"--user-data-dir={os.getenv('CHROME_USER_DATA_DIR', '/tmp/.chrome')}")
        else:
            chromedriver_path = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
        
        print(f"ChromeDriver path: {chromedriver_path}")
        print(f"Chrome version: {get_chrome_version()}")
        
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        print("Chrome driver setup successful!")
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {str(e)}")
        print("Environment:", os.environ.get("RENDER", "Not Render"))
        print("Platform:", platform.system())
        print("Chrome binary:", chrome_options.binary_location if 'chrome_options' in locals() else "Not set")
        print("ChromeDriver path:", chromedriver_path if 'chromedriver_path' in locals() else "Not set")
        print("System PATH:", os.environ.get("PATH", ""))
        print("Traceback:", traceback.format_exc())
        
        # Try to get ChromeDriver version
        try:
            chromedriver_version = subprocess.check_output([chromedriver_path, '--version']).decode()
            print("ChromeDriver version:", chromedriver_version)
        except:
            print("Could not get ChromeDriver version")
        
        raise

def extract_code(url):
    code_match = re.search(r'code=([A-Z0-9]+)', url)
    if code_match:
        return code_match.group(1)
    return None

def save_key_to_file(key):
    try:
        filename = "apple_tv_keys.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a") as f:
            f.write(f"[{timestamp}] APPLE TV+ 1 Month key: {key}\n")
    except Exception as e:
        print(f"Warning: Could not save key to file: {str(e)}")

def get_apple_tv_key(driver):
    initial_url = "https://redeem.services.apple/uberappletv?itscg=MC_30000&itsct=atvp_brand_omd&mttn3pid=uber&mttnagencyid=a5e&mttncc=US&mttnsiteid=143238&mttnsubad=04621974"
    
    try:
        print("Navigating to initial URL...")
        driver.get(initial_url)
        
        print("Waiting for button...")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div/div/section/div/div/div[4]/div/button"))
        )
        print("Clicking button...")
        button.click()
        
        print("Waiting for redirect...")
        time.sleep(2)  # Increased wait time
        final_url = driver.current_url
        print(f"Final URL: {final_url}")
        
        code = extract_code(final_url)
        if code:
            try:
                save_key_to_file(code)
            except:
                pass
            print(f"Successfully generated key: {code}")
            return code
        print("No code found in URL")
        return None
            
    except WebDriverException as e:
        print(f"WebDriver error: {str(e)}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Error generating key: {str(e)}")
        print(traceback.format_exc())
        return None
    finally:
        try:
            print("Page source:", driver.page_source)
        except:
            pass

if __name__ == "__main__":
    driver = None
    try:
        driver = setup_driver()
        get_apple_tv_key(driver)
    except Exception as e:
        print(f"Main error: {str(e)}")
        print(traceback.format_exc())
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass 