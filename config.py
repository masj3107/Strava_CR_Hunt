"""
Configuration file for the Strava Course Records application.
"""

# Strava website URLs
STRAVA_LOGIN_URL = "https://www.strava.com/login"
STRAVA_CR_URL_TEMPLATE = "https://www.strava.com/athletes/{user_id}/segments/leader"

# API endpoints
STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
STRAVA_SEGMENT_ENDPOINT = "/segments/{segment_id}"

# File paths
RAW_DATA_PATH = "data/challenge_results_raw.json"
ENRICHED_DATA_PATH = "data/challenge_results_complemented.json"

# Selenium configuration
SELENIUM_IMPLICIT_WAIT = 10  # seconds
SELENIUM_PAGE_LOAD_TIMEOUT = 30  # seconds

# API rate limiting
API_RATE_LIMIT_PAUSE = 2  # seconds between API calls
