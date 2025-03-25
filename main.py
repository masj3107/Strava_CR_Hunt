"""
Main application module for Strava Course Records.
"""

import os
import logging
import json
import argparse
from getpass import getpass

from src.webdriver_config import setup_driver
from src.strava_login import login_to_strava
from src.data_extraction import navigate_to_cr_page, extract_cr_data
from src.json_conversion import convert_to_json
from src.strava_api import StravaAPI
from config import RAW_DATA_PATH, ENRICHED_DATA_PATH

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the Strava Course Records application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Strava Course Records Data Processor')
    parser.add_argument('--user_id', type=str, help='Strava user ID to fetch CR data from')
    parser.add_argument('--token', type=str, help='Strava API OAuth token')
    args = parser.parse_args()
    
    # Get Strava credentials
    username = input("Enter your Strava username/email: ")
    password = getpass("Enter your Strava password: ")
    
    # Get target user ID if not provided
    user_id = args.user_id
    if not user_id:
        user_id = input("Enter the target Strava user ID: ")
    
    # Get Strava API token if not provided
    token = args.token
    if not token:
        token = input("Enter your Strava API OAuth token: ")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    
    # Set up the web driver
    driver = setup_driver()
    
    try:
        # Step 1: Login to Strava
        logger.info("Logging in to Strava...")
        if not login_to_strava(driver, username, password):
            logger.error("Failed to log in to Strava. Exiting.")
            return
        
        # Step 2: Navigate to CR page and extract data
        logger.info(f"Navigating to CR page for user {user_id}...")
        if not navigate_to_cr_page(driver, user_id):
            logger.error("Failed to navigate to CR page. Exiting.")
            return
        
        cr_data = extract_cr_data(driver)
        if not cr_data:
            logger.error("Failed to extract CR data. Exiting.")
            return
        
        # Step 3: Convert data to JSON
        logger.info("Converting data to JSON format...")
        if not convert_to_json(cr_data, RAW_DATA_PATH):
            logger.error("Failed to convert data to JSON. Exiting.")
            return
        
        # Step 4: Enrich data with API information
        logger.info("Enriching data with API information...")
        strava_api = StravaAPI(token)
        
        # Load the raw JSON data
        with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if not strava_api.enrich_cr_data(raw_data, ENRICHED_DATA_PATH):
            logger.error("Failed to enrich data with API information. Exiting.")
            return
        
        logger.info("Data processing completed successfully!")
        logger.info(f"Raw data saved to: {RAW_DATA_PATH}")
        logger.info(f"Enriched data saved to: {ENRICHED_DATA_PATH}")
        
    finally:
        # Close the web driver
        driver.quit()

if __name__ == "__main__":
    main()
