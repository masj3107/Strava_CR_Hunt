"""
Unified application for Strava Course Records.
This module integrates all components into a single application.
"""

import os
import logging
import argparse
import threading
import webbrowser
import time
from getpass import getpass

from src.webdriver_config import setup_driver
from src.strava_login import login_to_strava
from src.data_extraction import navigate_to_cr_page, extract_cr_data
from src.json_conversion import convert_to_json
from src.strava_api import StravaAPI
from src.table_visualization import run_table_app
from src.map_visualization import run_map_app
from src.config import RAW_DATA_PATH, ENRICHED_DATA_PATH

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_data(username, password, user_id, token):
    """
    Process Strava Course Records data.
    
    Args:
        username: Strava username/email
        password: Strava password
        user_id: Target Strava user ID
        token: Strava API OAuth token
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    
    # Set up the web driver
    driver = setup_driver()
    
    try:
        # Step 1: Login to Strava
        logger.info("Logging in to Strava...")
        if not login_to_strava(driver, username, password):
            logger.error("Failed to log in to Strava. Exiting.")
            return False
        
        # Step 2: Navigate to CR page and extract data
        logger.info(f"Navigating to CR page for user {user_id}...")
        if not navigate_to_cr_page(driver, user_id):
            logger.error("Failed to navigate to CR page. Exiting.")
            return False
        
        cr_data = extract_cr_data(driver)
        if not cr_data:
            logger.error("Failed to extract CR data. Exiting.")
            return False
        
        # Step 3: Convert data to JSON
        logger.info("Converting data to JSON format...")
        if not convert_to_json(cr_data, RAW_DATA_PATH):
            logger.error("Failed to convert data to JSON. Exiting.")
            return False
        
        # Step 4: Enrich data with API information
        logger.info("Enriching data with API information...")
        strava_api = StravaAPI(token)
        
        # Load the raw JSON data
        with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
            import json
            raw_data = json.load(f)
        
        if not strava_api.enrich_cr_data(raw_data, ENRICHED_DATA_PATH):
            logger.error("Failed to enrich data with API information. Exiting.")
            return False
        
        logger.info("Data processing completed successfully!")
        logger.info(f"Raw data saved to: {RAW_DATA_PATH}")
        logger.info(f"Enriched data saved to: {ENRICHED_DATA_PATH}")
        return True
        
    finally:
        # Close the web driver
        driver.quit()

def run_visualization_apps(json_file):
    """
    Run the table and map visualization apps in separate threads.
    
    Args:
        json_file: Path to the JSON file containing the data
        
    Returns:
        None
    """
    # Create assets directory for map
    os.makedirs("assets", exist_ok=True)
    
    # Start the table app in a separate thread
    table_thread = threading.Thread(
        target=run_table_app,
        args=(json_file, 8050),
        daemon=True
    )
    table_thread.start()
    
    # Start the map app in a separate thread
    map_thread = threading.Thread(
        target=run_map_app,
        args=(json_file, 8051),
        daemon=True
    )
    map_thread.start()
    
    # Wait a moment for the apps to start
    time.sleep(2)
    
    # Open the apps in the browser
    webbrowser.open("http://localhost:8050")
    webbrowser.open("http://localhost:8051")
    
    logger.info("Visualization apps started.")
    logger.info("Table visualization available at: http://localhost:8050")
    logger.info("Map visualization available at: http://localhost:8051")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down visualization apps...")

def main():
    """
    Main function to run the Strava Course Records application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Strava Course Records Application')
    parser.add_argument('--user_id', type=str, help='Strava user ID to fetch CR data from')
    parser.add_argument('--token', type=str, help='Strava API OAuth token')
    parser.add_argument('--visualize_only', action='store_true', help='Skip data processing and only run visualization')
    args = parser.parse_args()
    
    if args.visualize_only:
        # Check if enriched data file exists
        if not os.path.exists(ENRICHED_DATA_PATH):
            logger.error(f"Enriched data file not found: {ENRICHED_DATA_PATH}")
            logger.error("Please run data processing first or provide the correct file path.")
            return
            
        # Run visualization apps
        run_visualization_apps(ENRICHED_DATA_PATH)
        return
    
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
    
    # Process data
    if process_data(username, password, user_id, token):
        # Run visualization apps
        run_visualization_apps(ENRICHED_DATA_PATH)
    else:
        logger.error("Data processing failed. Visualization apps will not be started.")

if __name__ == "__main__":
    main()
