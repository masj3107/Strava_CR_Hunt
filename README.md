# Strava Course Records Application - Installation and Usage Guide

## Overview

The Strava Course Records (CR) Application is a tool that automatically logs in to Strava, extracts Course Record data for segments from a target user's account, enriches that data via the Strava API, and presents the information interactively through both a sortable table and an interactive map.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
   - [Basic Usage](#basic-usage)
   - [Command Line Arguments](#command-line-arguments)
   - [Visualization Only Mode](#visualization-only-mode)
5. [Features](#features)
   - [Interactive Table](#interactive-table)
   - [Interactive Map](#interactive-map)
6. [Troubleshooting](#troubleshooting)
7. [API Token Guide](#api-token-guide)

## Prerequisites

Before installing the application, ensure you have the following:

- Python 3.6 or higher
- Google Chrome browser (for Selenium WebDriver)
- A Strava account with login credentials
- A Strava API OAuth token (see [API Token Guide](#api-token-guide))
- The Strava user ID of the target account to extract CRs from

## Installation

1. Clone the repository or download the source code:

```bash
git clone [https://github.com/yourusername/strava-cr-app.git](https://github.com/masj3107/Strava_CR_Hunt)
cd Strava_CR_Hunt
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file, you can install the dependencies directly:

```bash
pip install selenium requests folium pandas dash dash-bootstrap-components webdriver-manager
```

3. Ensure the Chrome WebDriver is installed (this should happen automatically with webdriver-manager).

## Configuration

The application uses a configuration file located at `src/config.py`. You can modify this file to change default settings such as:

- File paths for data storage
- API endpoints
- Selenium configuration
- API rate limiting

The default configuration should work for most users, but you may want to adjust these settings based on your specific needs.

## Usage

### Basic Usage

To run the application with all features (data extraction, enrichment, and visualization):

```bash
python app.py
```

You will be prompted to enter:
- Your Strava username/email
- Your Strava password
- The target Strava user ID to extract CRs from
- Your Strava API OAuth token

### Command Line Arguments

The application supports the following command line arguments:

- `--user_id`: Specify the Strava user ID to fetch CR data from
- `--token`: Provide your Strava API OAuth token
- `--visualize_only`: Skip data processing and only run visualization

Example:

```bash
python app.py --user_id 12345678 --token your_api_token_here
```

### Visualization Only Mode

If you've already processed the data and just want to view the visualizations:

```bash
python app.py --visualize_only
```

This will skip the data processing steps and directly load the previously saved data for visualization.

## Features

### Interactive Table

The interactive table provides the following features:

- Display of all Course Record data in a tabular format
- Sorting by any column (click on column headers)
- Filtering by segment type, distance range, and date range
- Clickable links to view segments and efforts on Strava
- Pagination for easy navigation through large datasets

The table is accessible at http://localhost:8050 when the application is running.

### Interactive Map

The interactive map provides the following features:

- Visual representation of all segments on a map
- Filtering by segment type and distance range
- Interactive markers for start and end points of each segment
- Popups with detailed segment information when clicking on segments
- Standard map controls (zoom, pan, etc.)

The map is accessible at http://localhost:8051 when the application is running.

## Troubleshooting

### Common Issues

1. **Login Failure**
   - Ensure your Strava credentials are correct
   - Check if Strava has implemented CAPTCHA or other security measures
   - Try logging in manually first, then run the application

2. **API Token Issues**
   - Ensure your API token is valid and has not expired
   - Check that you have the necessary permissions (read access)
   - See [API Token Guide](#api-token-guide) for obtaining a new token

3. **WebDriver Issues**
   - Ensure Chrome is installed on your system
   - Try updating the Chrome browser
   - The application should automatically download the correct WebDriver version

4. **Visualization Not Loading**
   - Check that ports 8050 and 8051 are available on your system
   - Ensure the data files exist in the expected location
   - Check the console output for any error messages

### Logging

The application uses Python's logging module to provide detailed information about its operation. By default, logs are output to the console. You can check these logs for information about any issues that occur.

## API Token Guide

To use the Strava API, you need an OAuth token. Here's how to obtain one:

1. Log in to your Strava account
2. Go to [Strava API Settings](https://www.strava.com/settings/api)
3. Create a new application with the following details:
   - Application Name: Strava CR App
   - Website: http://localhost
   - Authorization Callback Domain: localhost
4. After creating the application, you'll see your Client ID and Client Secret
5. Use these credentials to obtain an access token through the OAuth flow
6. For testing purposes, you can use the [Strava API Playground](https://developers.strava.com/playground/) to generate a token

Note: Strava API tokens expire after a certain period. If you encounter API authentication errors, you may need to generate a new token.

---

## Development

If you want to contribute to the development of this application:

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Run the tests to ensure everything works:

```bash
python -m unittest tests.py
```

5. Submit a pull request with your changes

---

For any questions or issues not covered in this documentation, please open an issue on the project repository.
