from dash import html, dcc, Input, Output, callback
import pandas as pd
import os
import plotly.express as px
import dash_bootstrap_components as dbc

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)
CSV_FILE = os.path.join(current_directory, '..', 'data', 'doc_clinicians_SC_enhanced.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Define the layout for Page 1
layout = html.Div([
    html.H1('Provider Map and Details'),

    # Filters
    html.Div([
        dcc.Dropdown(
            id='state-filter',
            options=[{'label': state, 'value': state} for state in df['State'].unique()],
            placeholder='Select a State',
            style={'width': '200px'}
        ),
        dcc.Dropdown(
            id='city-filter',
            options=[{'label': city, 'value': city} for city in df['City/Town'].unique()],
            placeholder='Select a City',
            style={'width': '200px'}
        ),
        dcc.Input(id='npi-search', type='text', placeholder='Search NPI'),
        dcc.Input(id='last-name-search', type='text', placeholder='Provider Last Name')
    ], style={'display': 'flex', 'gap': '10px', 'margin-bottom': '20px'}),

    # Map
    dcc.Graph(id='map'),

    # Table
    html.Div(id='table-container')
])

# Callback to update the map based on filters
@callback(
    Output('map', 'figure'),
    [Input('city-filter', 'value'),
     Input('state-filter', 'value'),
     Input('npi-search', 'value'),
     Input('last-name-search', 'value')]
)
def update_map(city, state, npi, last_name):
    filtered_df = df.copy()

    if city:
        filtered_df = filtered_df[filtered_df['City/Town'] == city]
    if state:
        filtered_df = filtered_df[filtered_df['State'] == state]

    if npi:
        filtered_df = filtered_df[filtered_df['NPI'].astype(str).str.contains(npi)]
    if last_name:
        filtered_df = filtered_df[filtered_df['Provider Last Name'].str.contains(last_name, case=False)]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="NPI",
        hover_data=["Provider Last Name"],
        zoom=10,
        mapbox_style="carto-positron"
    )

    return fig

# Callback to update the table based on the map click
@callback(
    Output('table-container', 'children'),
    [Input('map', 'clickData'),
     Input('city-filter', 'value'),
     Input('state-filter', 'value'),
     Input('npi-search', 'value'),
     Input('last-name-search', 'value')]
)
def update_table(click_data, city, state, npi, last_name):
    filtered_df = df.copy()

    if city:
        filtered_df = filtered_df[filtered_df['City/Town'] == city]
    if state:
        filtered_df = filtered_df[filtered_df['State'] == state]
    if npi:
        filtered_df = filtered_df[filtered_df['NPI'].astype(str).str.contains(npi)]
    if last_name:
        filtered_df = filtered_df[filtered_df['Provider Last Name'].str.contains(last_name, case=False)]

    if click_data:
        npi_clicked = click_data['points'][0]['hovertext']
        filtered_df = filtered_df[filtered_df['NPI'] == npi_clicked]

    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in ['NPI', 'Provider First Name', 'Provider Last Name', 'gndr', 'Cred', 'Med_sch', 'pri_spec']])),
        html.Tbody([
            html.Tr([
                html.Td(filtered_df.iloc[i][col]) for col in ['NPI', 'Provider First Name', 'Provider Last Name', 'gndr', 'Cred', 'Med_sch', 'pri_spec']
            ]) for i in range(len(filtered_df))
        ])
    ]) if not filtered_df.empty else html.P("No data available")

    return table
