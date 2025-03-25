"""
Code structure documentation for the Strava Course Records application.
"""

# Application Structure

The Strava Course Records application is organized into the following components:

## 1. Main Application Files

- `app.py`: The main entry point for the application that integrates all components
- `README.md`: Comprehensive documentation for installation and usage
- `requirements.txt`: List of Python dependencies
- `tests.py`: Unit tests for various application components

## 2. Source Modules

### Configuration
- `src/config.py`: Configuration settings for URLs, file paths, and other parameters

### Data Acquisition
- `src/webdriver_config.py`: Selenium WebDriver configuration and utility functions
- `src/strava_login.py`: Functionality for authenticating with Strava
- `src/data_extraction.py`: Extraction of Course Record data from Strava web pages

### Data Processing
- `src/json_conversion.py`: Conversion of extracted data to structured JSON format
- `src/strava_api.py`: Integration with Strava API for data enrichment

### Visualization
- `src/table_visualization.py`: Interactive table visualization using Dash
- `src/map_visualization.py`: Interactive map visualization using Folium and Dash

## 3. Data Storage

- `data/`: Directory for storing JSON data files
  - `challenge_results_raw.json`: Raw extracted CR data
  - `challenge_results_complemented.json`: Enriched CR data with API information

## 4. Component Relationships

1. The user interacts with `app.py`, which orchestrates the entire workflow
2. Authentication is handled by `strava_login.py` using the WebDriver from `webdriver_config.py`
3. Data extraction is performed by `data_extraction.py`
4. The extracted data is converted to JSON by `json_conversion.py`
5. The data is enriched with API information by `strava_api.py`
6. The enriched data is visualized through `table_visualization.py` and `map_visualization.py`

## 5. Data Flow

```
User Input → Authentication → Data Extraction → JSON Conversion → API Enrichment → Visualization
```

## 6. Module Dependencies

- `app.py` depends on all other modules
- `webdriver_config.py` depends on `config.py`
- `strava_login.py` depends on `config.py`
- `data_extraction.py` depends on `config.py`
- `strava_api.py` depends on `config.py`
- `table_visualization.py` and `map_visualization.py` are independent visualization modules

This modular structure allows for easy maintenance and extension of the application.
