"""
JSON conversion module for Strava Course Records data.
"""

import json
import logging
import re
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_date(date_str):
    """
    Normalize date string to ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        str: Normalized date in ISO format or original string if parsing fails
    """
    try:
        # Handle various date formats that might appear in Strava
        # Common formats: "Jan 1, 2023", "January 1, 2023", "01/01/2023", etc.
        
        # Try different date formats
        for fmt in ["%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        # If none of the formats match, return the original string
        logger.warning(f"Could not normalize date: {date_str}")
        return date_str
        
    except Exception as e:
        logger.error(f"Error normalizing date {date_str}: {str(e)}")
        return date_str

def normalize_distance(distance_str):
    """
    Normalize distance string to numeric value in kilometers.
    
    Args:
        distance_str: Distance string (e.g., "5.2 km", "5,200 m")
        
    Returns:
        float: Distance in kilometers or None if parsing fails
    """
    try:
        # Remove commas and convert to lowercase
        distance_str = distance_str.lower().replace(',', '')
        
        # Extract numeric value and unit
        match = re.search(r'([\d.]+)\s*([a-z]+)', distance_str)
        if not match:
            logger.warning(f"Could not parse distance: {distance_str}")
            return None
            
        value, unit = match.groups()
        value = float(value)
        
        # Convert to kilometers based on unit
        if 'km' in unit:
            return value
        elif 'm' in unit:
            return value / 1000
        else:
            logger.warning(f"Unknown distance unit: {unit}")
            return value
            
    except Exception as e:
        logger.error(f"Error normalizing distance {distance_str}: {str(e)}")
        return None

def normalize_elevation(elevation_str):
    """
    Normalize elevation string to numeric value in meters.
    
    Args:
        elevation_str: Elevation string (e.g., "100 m", "328 ft")
        
    Returns:
        float: Elevation in meters or None if parsing fails
    """
    try:
        # Remove commas and convert to lowercase
        elevation_str = elevation_str.lower().replace(',', '')
        
        # Extract numeric value and unit
        match = re.search(r'([\d.]+)\s*([a-z]+)', elevation_str)
        if not match:
            logger.warning(f"Could not parse elevation: {elevation_str}")
            return None
            
        value, unit = match.groups()
        value = float(value)
        
        # Convert to meters based on unit
        if 'm' in unit:
            return value
        elif 'ft' in unit:
            return value * 0.3048  # Convert feet to meters
        else:
            logger.warning(f"Unknown elevation unit: {unit}")
            return value
            
    except Exception as e:
        logger.error(f"Error normalizing elevation {elevation_str}: {str(e)}")
        return None

def convert_to_json(cr_data, output_file):
    """
    Convert extracted CR data to structured JSON format and save to file.
    
    Args:
        cr_data: List of dictionaries containing CR data
        output_file: Path to save the JSON file
        
    Returns:
        bool: True if conversion and saving was successful, False otherwise
    """
    try:
        logger.info("Converting CR data to structured JSON format...")
        
        structured_data = []
        
        for record in cr_data:
            # Normalize date
            normalized_date = normalize_date(record.get('date', ''))
            
            # Normalize distance
            distance_km = normalize_distance(record.get('distance_km', ''))
            
            # Normalize elevation
            elevation_m = normalize_elevation(record.get('elevation_m', ''))
            
            # Create structured record
            structured_record = {
                "type": record.get('type', ''),
                "name": record.get('name', ''),
                "link": record.get('link', ''),
                "distance_km": distance_km,
                "elevation_m": elevation_m,
                "time": record.get('time', ''),
                "time_link": record.get('time_link', ''),
                "date": normalized_date,
                "polyline": None,  # To be filled later via API
                "effort_count": None,  # To be filled later via API
                "athlete_count": None  # To be filled later via API
            }
            
            structured_data.append(structured_record)
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved {len(structured_data)} records to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"An error occurred during JSON conversion: {str(e)}")
        return False