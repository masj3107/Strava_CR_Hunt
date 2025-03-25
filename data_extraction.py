"""
Data extraction module for Strava Course Records.
"""

import time
import logging
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config import STRAVA_CR_URL_TEMPLATE

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def navigate_to_cr_page(driver, user_id):
    """
    Navigate to the Course Records page for the specified user.
    
    Args:
        driver: Selenium WebDriver instance
        user_id: Strava user ID to fetch CR data from
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    try:
        cr_url = STRAVA_CR_URL_TEMPLATE.format(user_id=user_id)
        logger.info(f"Navigating to Course Records page for user {user_id}...")
        driver.get(cr_url)
        
        # Wait for the page to load
        time.sleep(3)
        
        # Check if the page loaded successfully by looking for the CR table
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "segments-table"))
            )
            logger.info("Course Records page loaded successfully!")
            return True
        except TimeoutException:
            logger.error("Timed out waiting for Course Records table to load")
            return False
            
    except Exception as e:
        logger.error(f"An error occurred while navigating to CR page: {str(e)}")
        return False

def extract_segment_id_from_url(url):
    """
    Extract the segment ID from a Strava segment URL.
    
    Args:
        url: Strava segment URL
        
    Returns:
        str: Segment ID or None if not found
    """
    if not url:
        return None
        
    # Pattern to match segment ID in URLs like https://www.strava.com/segments/12345
    pattern = r'strava\.com/segments/(\d+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    return None

def extract_cr_data(driver):
    """
    Extract Course Record data from the current page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of dictionaries containing CR data
    """
    try:
        logger.info("Extracting Course Record data...")
        
        # Find the CR table
        table = driver.find_element(By.CLASS_NAME, "segments-table")
        
        # Find all rows in the table (excluding header)
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
        
        cr_data = []
        
        for row in rows:
            try:
                # Extract cells from the row
                cells = row.find_elements(By.TAG_NAME, "td")
                
                # Skip if not enough cells
                if len(cells) < 6:
                    continue
                
                # Extract data from cells
                segment_type = cells[0].text.strip()
                
                # Extract segment name and link
                name_cell = cells[1]
                segment_name = name_cell.text.strip()
                segment_link = None
                
                # Try to find the link in the name cell
                try:
                    link_element = name_cell.find_element(By.TAG_NAME, "a")
                    segment_link = link_element.get_attribute("href")
                except NoSuchElementException:
                    pass
                
                # Extract distance, elevation, time, and date
                distance_km = cells[2].text.strip()
                elevation_m = cells[3].text.strip()
                
                # Extract time and time link
                time_cell = cells[4]
                time_value = time_cell.text.strip()
                time_link = None
                
                # Try to find the link in the time cell
                try:
                    link_element = time_cell.find_element(By.TAG_NAME, "a")
                    time_link = link_element.get_attribute("href")
                except NoSuchElementException:
                    pass
                
                date = cells[5].text.strip()
                
                # Extract segment ID from segment link
                segment_id = extract_segment_id_from_url(segment_link)
                
                # Create a record
                record = {
                    "type": segment_type,
                    "name": segment_name,
                    "link": segment_link,
                    "segment_id": segment_id,
                    "distance_km": distance_km,
                    "elevation_m": elevation_m,
                    "time": time_value,
                    "time_link": time_link,
                    "date": date,
                    "polyline": None,  # To be filled later via API
                    "effort_count": None,  # To be filled later via API
                    "athlete_count": None  # To be filled later via API
                }
                
                cr_data.append(record)
                
            except Exception as e:
                logger.warning(f"Error extracting data from row: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(cr_data)} Course Records")
        return cr_data
        
    except Exception as e:
        logger.error(f"An error occurred while extracting CR data: {str(e)}")
        return []
