from dash import html, dcc, register_page
import pandas as pd
import os
import plotly.express as px
import dash


dash.register_page(__name__,
                   path='/last',
                   name='Finder',
                   title='Last',  # title that appears on browser's tab
                   description='Lasttt'
                   )

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)
CSV_FILE = os.path.join(current_directory, '..', 'data', 'combo_cleaned_df.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Example function to plot locations on a map
def plot_locations_on_map():
    df_subset = df.copy()  # Selecting the first 10 rows in Charleston

    # Plot locations on map using Plotly Express
    fig = px.scatter_mapbox(
        df_subset,
        lat="Latitude",
        lon="Longitude",
        hover_name="name_full",
        zoom=5,
        color="data_source"  # Add this line to color by the 'data_source' column
    )

    fig.update_layout(mapbox_style="open-street-map")

    # Create a table displaying address info
    table_rows = []
    for _, row in df_subset.iterrows():
        table_rows.append(html.Tr([
            html.Td(row['data_source']),
            html.Td(row['name_full']),
            html.Td(row['Cleaned Address']),
        ]))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th("data_source"),
            html.Th("name_full"),
            html.Th("Cleaned Address"),
        ])),
        html.Tbody(table_rows)
    ], style={'width': '100%'})

    # Return layout with map and table
    return html.Div([
        html.H1('Page 3'),
        html.H2('Lead Overview'),
        dcc.Graph(figure=fig),
        html.H2('Address Information'),
        table
    ])


# Layout for Page 3
layout = plot_locations_on_map()
