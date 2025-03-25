"""
Strava API integration module for data enrichment.
"""

import time
import logging
import requests
import json
from src.config import STRAVA_API_BASE_URL, STRAVA_SEGMENT_ENDPOINT, API_RATE_LIMIT_PAUSE

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StravaAPI:
    """
    Class to handle Strava API interactions.
    """
    
    def __init__(self, access_token):
        """
        Initialize the Strava API client.
        
        Args:
            access_token: OAuth access token for Strava API
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
    def get_segment_details(self, segment_id):
        """
        Get detailed information about a segment from the Strava API.
        
        Args:
            segment_id: Strava segment ID
            
        Returns:
            dict: Segment details or None if request fails
        """
        if not segment_id:
            logger.warning("No segment ID provided")
            return None
            
        try:
            endpoint = STRAVA_SEGMENT_ENDPOINT.format(segment_id=segment_id)
            url = f"{STRAVA_API_BASE_URL}{endpoint}"
            
            logger.info(f"Fetching segment details for segment ID: {segment_id}")
            response = requests.get(url, headers=self.headers)
            
            # Implement rate limiting
            time.sleep(API_RATE_LIMIT_PAUSE)
            
            # Check if request was successful
            if response.status_code == 200:
                segment_data = response.json()
                logger.info(f"Successfully fetched details for segment: {segment_data.get('name', 'Unknown')}")
                return segment_data
            else:
                logger.error(f"Failed to fetch segment details. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"An error occurred while fetching segment details: {str(e)}")
            return None
            
    def enrich_cr_data(self, cr_data, output_file):
        """
        Enrich Course Record data with additional information from the Strava API.
        
        Args:
            cr_data: List of CR data dictionaries
            output_file: Path to save the enriched JSON file
            
        Returns:
            bool: True if enrichment was successful, False otherwise
        """
        try:
            logger.info("Enriching CR data with Strava API information...")
            
            enriched_data = []
            
            for record in cr_data:
                segment_id = record.get('segment_id')
                
                if not segment_id:
                    logger.warning(f"No segment ID for record: {record.get('name', 'Unknown')}")
                    enriched_data.append(record)
                    continue
                    
                # Get segment details from API
                segment_details = self.get_segment_details(segment_id)
                
                if segment_details:
                    # Extract relevant fields
                    polyline = segment_details.get('map', {}).get('polyline')
                    effort_count = segment_details.get('effort_count')
                    athlete_count = segment_details.get('athlete_count')
                    
                    # Update record with API data
                    record['polyline'] = polyline
                    record['effort_count'] = effort_count
                    record['athlete_count'] = athlete_count
                    
                enriched_data.append(record)
                
            # Save enriched data to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enriched_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Successfully saved {len(enriched_data)} enriched records to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"An error occurred during data enrichment: {str(e)}")
            return False
