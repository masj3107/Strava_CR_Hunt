"""
Interactive map visualization module for Strava Course Records.
"""

import json
import logging
import folium
import polyline
import pandas as pd
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data(json_file):
    """
    Load data from JSON file into a pandas DataFrame.
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        pd.DataFrame: DataFrame containing the data
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        logger.info(f"Successfully loaded {len(df)} records from {json_file}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {json_file}: {str(e)}")
        return pd.DataFrame()

def decode_polyline(encoded_polyline):
    """
    Decode a Google encoded polyline to a list of coordinates.
    
    Args:
        encoded_polyline: Google encoded polyline string
        
    Returns:
        list: List of [latitude, longitude] coordinates
    """
    if not encoded_polyline:
        return []
        
    try:
        return polyline.decode(encoded_polyline)
    except Exception as e:
        logger.error(f"Error decoding polyline: {str(e)}")
        return []

def create_map(df):
    """
    Create a Folium map with segments plotted.
    
    Args:
        df: DataFrame containing segment data with polylines
        
    Returns:
        folium.Map: Folium map object
    """
    try:
        # Filter out records without polylines
        df_with_polylines = df[df['polyline'].notna()]
        
        if df_with_polylines.empty:
            logger.warning("No polyline data available for mapping")
            # Create a default map centered on a reasonable location
            return folium.Map(location=[40.0, -100.0], zoom_start=4)
        
        # Calculate the center of all segments
        all_coords = []
        for poly in df_with_polylines['polyline']:
            coords = decode_polyline(poly)
            if coords:
                all_coords.extend(coords)
        
        if not all_coords:
            logger.warning("No valid coordinates found in polylines")
            return folium.Map(location=[40.0, -100.0], zoom_start=4)
        
        # Calculate center
        center_lat = sum(coord[0] for coord in all_coords) / len(all_coords)
        center_lng = sum(coord[1] for coord in all_coords) / len(all_coords)
        
        # Create map
        m = folium.Map(location=[center_lat, center_lng], zoom_start=10)
        
        # Add segments to map
        for _, row in df_with_polylines.iterrows():
            coords = decode_polyline(row['polyline'])
            if not coords:
                continue
                
            # Create popup content
            popup_html = f"""
            <b>{row['name']}</b><br>
            Type: {row['type']}<br>
            Distance: {row['distance_km']:.2f} km<br>
            Elevation: {row['elevation_m']:.1f} m<br>
            Time: {row['time']}<br>
            Date: {row['date']}<br>
            Efforts: {row['effort_count']}<br>
            Athletes: {row['athlete_count']}<br>
            <a href="{row['link']}" target="_blank">View on Strava</a>
            """
            
            # Add polyline to map
            folium.PolyLine(
                locations=coords,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row['name'],
                color='red',
                weight=3,
                opacity=0.7
            ).add_to(m)
            
            # Add marker at the start of the segment
            folium.Marker(
                location=coords[0],
                popup=folium.Popup(f"Start: {row['name']}", max_width=300),
                tooltip=f"Start: {row['name']}",
                icon=folium.Icon(color='green', icon='play', prefix='fa')
            ).add_to(m)
            
            # Add marker at the end of the segment
            folium.Marker(
                location=coords[-1],
                popup=folium.Popup(f"End: {row['name']}", max_width=300),
                tooltip=f"End: {row['name']}",
                icon=folium.Icon(color='red', icon='stop', prefix='fa')
            ).add_to(m)
        
        return m
    except Exception as e:
        logger.error(f"Error creating map: {str(e)}")
        return folium.Map(location=[40.0, -100.0], zoom_start=4)

def save_map(m, output_file):
    """
    Save the Folium map to an HTML file.
    
    Args:
        m: Folium map object
        output_file: Path to save the HTML file
        
    Returns:
        bool: True if saving was successful, False otherwise
    """
    try:
        m.save(output_file)
        logger.info(f"Map saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving map: {str(e)}")
        return False

def create_map_app(json_file):
    """
    Create a Dash application with an interactive map.
    
    Args:
        json_file: Path to the JSON file containing the data
        
    Returns:
        dash.Dash: Dash application instance
    """
    # Load data
    df = load_data(json_file)
    if df.empty:
        logger.error("No data loaded, cannot create map")
        return None
    
    # Create initial map
    m = create_map(df)
    map_file = "assets/map.html"
    save_map(m, map_file)
    
    # Create Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Define the layout
    app.layout = dbc.Container([
        html.H1("Strava Course Records Map", className="my-4"),
        
        # Filters
        html.Div([
            html.H4("Filters", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Segment Type:"),
                    dcc.Dropdown(
                        id='map-type-filter',
                        options=[{'label': t, 'value': t} for t in df['type'].unique()],
                        multi=True,
                        placeholder="Select segment types..."
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Distance Range (km):"),
                    dcc.RangeSlider(
                        id='map-distance-filter',
                        min=df['distance_km'].min() if not df['distance_km'].isna().all() else 0,
                        max=df['distance_km'].max() if not df['distance_km'].isna().all() else 100,
                        step=0.1,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=4),
                
                dbc.Col([
                    html.Button("Update Map", id="update-map-button", className="btn btn-primary")
                ], width=4)
            ])
        ], className="mb-4"),
        
        # Interactive Map
        html.Div([
            html.H4("Segment Map", className="mb-3"),
            html.Iframe(
                id='map-iframe',
                srcDoc=open(map_file, 'r').read(),
                width='100%',
                height='600px'
            )
        ])
    ], fluid=True)
    
    # Define callbacks
    @app.callback(
        Output('map-iframe', 'srcDoc'),
        [
            Input('update-map-button', 'n_clicks')
        ],
        [
            dash.dependencies.State('map-type-filter', 'value'),
            dash.dependencies.State('map-distance-filter', 'value')
        ]
    )
    def update_map(n_clicks, selected_types, distance_range):
        if n_clicks is None:
            # Initial load, return the default map
            return open(map_file, 'r').read()
        
        filtered_df = df.copy()
        
        # Filter by segment type
        if selected_types and len(selected_types) > 0:
            filtered_df = filtered_df[filtered_df['type'].isin(selected_types)]
        
        # Filter by distance range
        if distance_range and len(distance_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['distance_km'] >= distance_range[0]) & 
                (filtered_df['distance_km'] <= distance_range[1])
            ]
        
        # Create and save the filtered map
        m = create_map(filtered_df)
        save_map(m, map_file)
        
        # Return the updated map
        return open(map_file, 'r').read()
    
    return app

def run_map_app(json_file, port=8051):
    """
    Run the interactive map visualization app.
    
    Args:
        json_file: Path to the JSON file containing the data
        port: Port to run the app on
        
    Returns:
        None
    """
    app = create_map_app(json_file)
    if app:
        logger.info(f"Starting interactive map visualization app on port {port}")
        app.run_server(debug=True, host='0.0.0.0', port=port)
    else:
        logger.error("Failed to create map visualization app")
