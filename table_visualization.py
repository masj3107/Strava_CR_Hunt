"""
Interactive table visualization module for Strava Course Records.
"""

import json
import logging
import dash
from dash import html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

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

def create_table_app(json_file):
    """
    Create a Dash application with an interactive table.
    
    Args:
        json_file: Path to the JSON file containing the data
        
    Returns:
        dash.Dash: Dash application instance
    """
    # Load data
    df = load_data(json_file)
    if df.empty:
        logger.error("No data loaded, cannot create table")
        return None
    
    # Create Dash app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Define the layout
    app.layout = dbc.Container([
        html.H1("Strava Course Records", className="my-4"),
        
        # Filters
        html.Div([
            html.H4("Filters", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Segment Type:"),
                    dcc.Dropdown(
                        id='type-filter',
                        options=[{'label': t, 'value': t} for t in df['type'].unique()],
                        multi=True,
                        placeholder="Select segment types..."
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Distance Range (km):"),
                    dcc.RangeSlider(
                        id='distance-filter',
                        min=df['distance_km'].min() if not df['distance_km'].isna().all() else 0,
                        max=df['distance_km'].max() if not df['distance_km'].isna().all() else 100,
                        step=0.1,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], width=4),
                
                dbc.Col([
                    html.Label("Date Range:"),
                    dcc.DatePickerRange(
                        id='date-filter',
                        start_date=pd.to_datetime(df['date'].min()).date() if not df['date'].isna().all() else None,
                        end_date=pd.to_datetime(df['date'].max()).date() if not df['date'].isna().all() else None,
                        display_format='YYYY-MM-DD'
                    )
                ], width=4)
            ])
        ], className="mb-4"),
        
        # Interactive Table
        html.Div([
            html.H4("Course Records", className="mb-3"),
            dash_table.DataTable(
                id='cr-table',
                columns=[
                    {'name': 'Type', 'id': 'type', 'type': 'text'},
                    {'name': 'Segment Name', 'id': 'name', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Distance (km)', 'id': 'distance_km', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                    {'name': 'Elevation (m)', 'id': 'elevation_m', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                    {'name': 'Time', 'id': 'time', 'type': 'text', 'presentation': 'markdown'},
                    {'name': 'Date', 'id': 'date', 'type': 'datetime'},
                    {'name': 'Efforts', 'id': 'effort_count', 'type': 'numeric'},
                    {'name': 'Athletes', 'id': 'athlete_count', 'type': 'numeric'}
                ],
                data=df.to_dict('records'),
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                page_size=15,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                markdown_options={'link_target': '_blank'}
            )
        ])
    ], fluid=True)
    
    # Define callbacks
    @app.callback(
        Output('cr-table', 'data'),
        [
            Input('type-filter', 'value'),
            Input('distance-filter', 'value'),
            Input('date-filter', 'start_date'),
            Input('date-filter', 'end_date')
        ]
    )
    def update_table(selected_types, distance_range, start_date, end_date):
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
        
        # Filter by date range
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        # Format markdown links for segment names and times
        filtered_df['name'] = filtered_df.apply(
            lambda row: f"[{row['name']}]({row['link']})" if pd.notna(row['link']) else row['name'], 
            axis=1
        )
        
        filtered_df['time'] = filtered_df.apply(
            lambda row: f"[{row['time']}]({row['time_link']})" if pd.notna(row['time_link']) else row['time'], 
            axis=1
        )
        
        return filtered_df.to_dict('records')
    
    return app

def run_table_app(json_file, port=8050):
    """
    Run the interactive table visualization app.
    
    Args:
        json_file: Path to the JSON file containing the data
        port: Port to run the app on
        
    Returns:
        None
    """
    app = create_table_app(json_file)
    if app:
        logger.info(f"Starting interactive table visualization app on port {port}")
        app.run_server(debug=True, host='0.0.0.0', port=port)
    else:
        logger.error("Failed to create table visualization app")
