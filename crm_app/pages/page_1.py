# pages/page_1.py

from dash import html, register_page

# Register the page with the root path to make it the default page
register_page(__name__, path="/")

# Define the layout for Page 1
layout = html.Div([
    html.H1('Page 1'),
    html.P('This is the content of Page 1.')
])
