import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask import Flask

# External stylesheets
FONT_AWESOME = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]

# Server
server = Flask(__name__)
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=external_stylesheets,
           server=server,
           suppress_callback_exceptions=True)

# Import the page modules
import pages.page_1
import pages.page_2

# Sidebar
sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [
                html.Div(page["name"], className="ms-2"),
            ],
            href=page["path"],
            active="exact",
        )
        for page in dash.page_registry.values()
    ],
    vertical=True,
    pills=True,
    className="bg-light",
)

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Img(src='/assets/images/plotador_logo_1.png', alt='Plotador Logo',
                     style={'width': '80%', 'margin': '10px'}),
            width=2
        ),
        dbc.Col(
            html.Div(
                html.H1("Plotador CRM", style={'textAlign': 'center', 'font-size': '48px'}),
                style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'height': '100%'}
            ),
            width=8
        ),
        dbc.Col([
            html.A(
                [
                    html.Img(src='/assets/images/support_icon.png', alt='Support Icon', style={'width': '20px', 'margin-right': '10px'}),
                    "Contact Support"
                ],
                href='mailto:robert@plotador.com', style={'display': 'flex', 'alignItems': 'center', 'margin-bottom': '10px'}
            ),
            html.A("Plotador.com", href='https://www.plotador.com/', target="_blank")
        ], width=2),
    ], style={'height': '100px'}),
    html.Hr(),
    dbc.Row([
        dbc.Col(sidebar, width=2),
        dbc.Col(dash.page_container, width=10)
    ])
])

if __name__ == "__main__":
    app.run(debug=False)
