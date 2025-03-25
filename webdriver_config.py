"""
Web driver configuration for Selenium.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import SELENIUM_IMPLICIT_WAIT, SELENIUM_PAGE_LOAD_TIMEOUT

def setup_driver():
    """
    Set up and configure the Chrome web driver for Selenium.
    
    Returns:
        webdriver.Chrome: Configured Chrome web driver instance.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Configure timeouts
    driver.implicitly_wait(SELENIUM_IMPLICIT_WAIT)
    driver.set_page_load_timeout(SELENIUM_PAGE_LOAD_TIMEOUT)
    
    return driver

def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present on the page.
    
    Args:
        driver (webdriver.Chrome): Chrome web driver instance.
        by (By): Method to locate the element.
        value (str): Value to search for.
        timeout (int): Maximum time to wait in seconds.
        
    Returns:
        WebElement: The found element.
        
    Raises:
        TimeoutException: If the element is not found within the timeout period.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))

def wait_for_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable on the page.
    
    Args:
        driver (webdriver.Chrome): Chrome web driver instance.
        by (By): Method to locate the element.
        value (str): Value to search for.
        timeout (int): Maximum time to wait in seconds.
        
    Returns:
        WebElement: The found element.
        
    Raises:
        TimeoutException: If the element is not found or not clickable within the timeout period.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((by, value)))
