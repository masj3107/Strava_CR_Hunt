"""
Strava login functionality module.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.config import STRAVA_LOGIN_URL

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def login_to_strava(driver, username, password):
    """
    Log in to Strava using the provided credentials.
    
    Args:
        driver: Selenium WebDriver instance
        username: Strava username or email
        password: Strava password
        
    Returns:
        bool: True if login was successful, False otherwise
    """
    try:
        logger.info("Navigating to Strava login page...")
        driver.get(STRAVA_LOGIN_URL)
        
        # Wait for the page to load
        time.sleep(2)
        
        logger.info("Entering login credentials...")
        # Find and fill the email/username field
        email_field = driver.find_element(By.ID, "email")
        email_field.clear()
        email_field.send_keys(username)
        
        # Find and fill the password field
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click the login button
        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful by looking for elements that would be present after login
        # This could be a dashboard element, profile link, etc.
        try:
            profile_element = driver.find_element(By.CLASS_NAME, "user-menu")
            logger.info("Login successful!")
            return True
        except NoSuchElementException:
            # Check for error messages
            try:
                error_message = driver.find_element(By.CLASS_NAME, "alert-message")
                logger.error(f"Login failed: {error_message.text}")
            except NoSuchElementException:
                logger.error("Login failed: Unknown error")
            return False
            
    except Exception as e:
        logger.error(f"An error occurred during login: {str(e)}")
        return False
