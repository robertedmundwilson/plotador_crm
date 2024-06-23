from dash import html, register_page
import pandas as pd
import os

# Register the page with its specific path
register_page(__name__, path="/page-2")

# Determine the path to the CSV file
current_directory = os.path.dirname(__file__)
CSV_FILE = os.path.join(current_directory, '..', 'data', 'doc_clinicians_SC.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(CSV_FILE)

# Calculate count of distinct values for each column
distinct_counts = df.nunique()

# Create a table displaying the distinct counts
table_rows = []
for col, count in distinct_counts.items():
    table_rows.append(html.Tr([html.Td(col), html.Td(str(count))]))

table = html.Table(
    [html.Thead(html.Tr([html.Th('Column Name'), html.Th('Distinct Count')])),
     html.Tbody(table_rows)]
)

# Create the layout for Page 2
layout = html.Div([
    html.H1('Page 2'),
    html.H2('Distinct Value Counts for Columns in space-mission-data.csv'),
    table
])
