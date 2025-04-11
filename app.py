import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import os

# Initialize the Dash app
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.VAPOR],
    suppress_callback_exceptions=True,
)

# Custom CSS
dash_app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background-color: #1a1a2e;
                color: #e6e6e6;
            }
            .navbar {
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .nav-link {
                transition: all 0.3s ease;
            }
            .nav-link:hover {
                transform: translateY(-2px);
            }
            .card {
                background-color: #16213e;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .card-header {
                background-color: #0f3460;
                border-bottom: none;
                border-radius: 10px 10px 0 0;
            }
            .table {
                background-color: #16213e;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the layout
dash_app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Navbar(
            [
                dbc.Container(
                    [
                        html.A(
                            dbc.Row(
                                [
                                    dbc.Col(html.I(className="fas fa-gamepad me-2")),
                                    dbc.Col(dbc.NavbarBrand("LoL Dashboard", className="ms-2")),
                                ],
                                align="center",
                                className="g-0",
                            ),
                            href="/",
                            style={"textDecoration": "none"},
                        ),
                        dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                [
                                    dbc.NavItem(dbc.NavLink("Players", href="/players", className="px-3")),
                                    dbc.NavItem(dbc.NavLink("Champions", href="/champions", className="px-3")),
                                    dbc.NavItem(dbc.NavLink("Teams", href="/teams", className="px-3")),
                                    dbc.NavItem(dbc.NavLink("Patch", href="/patch", className="px-3")),
                                    dbc.NavItem(dbc.NavLink("Best Matches", href="/best-matches", className="px-3")),
                                    dbc.DropdownMenu(
                                        [
                                            dbc.DropdownMenuItem("Players", href="/head2head-players"),
                                            dbc.DropdownMenuItem("Teams", href="/head2head-teams"),
                                            dbc.DropdownMenuItem("Champions", href="/head2head-champions"),
                                        ],
                                        nav=True,
                                        label="Head2Head",
                                        className="px-3",
                                    ),
                                ],
                                className="ms-auto",
                                navbar=True,
                            ),
                            id="navbar-collapse",
                            navbar=True,
                        ),
                    ]
                ),
            ],
            color="dark",
            dark=True,
            className="mb-4",
            sticky="top",
        ),
        html.Div(id="page-content"),
    ]
)

# Import page layouts
from pages.players import layout as players_layout
from pages.champions import layout as champions_layout
from pages.teams import layout as teams_layout
from pages.patch import layout as patch_layout
from pages.champions_sinergys_counters import (
    layout as champions_sinergys_counters_layout,
)
from pages.head2head_players import layout as head2head_players_layout
from pages.head2head_teams import layout as head2head_teams_layout
from pages.head2head_champions import layout as head2head_champions_layout


# Callback to switch between pages
@dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/players":
        return players_layout
    elif pathname == "/champions":
        return champions_layout
    elif pathname == "/teams":
        return teams_layout
    elif pathname == "/patch":
        return patch_layout
    elif pathname == "/best-matches":
        return champions_sinergys_counters_layout
    elif pathname == "/head2head-players":
        return head2head_players_layout
    elif pathname == "/head2head-teams":
        return head2head_teams_layout
    elif pathname == "/head2head-champions":
        return head2head_champions_layout
    else:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("Welcome to LoL Dashboard", 
                               className="display-4 text-center mb-4"),
                        html.P("Explore professional League of Legends statistics and analysis",
                               className="lead text-center mb-5"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Players", className="card-title"),
                                        html.P("View player statistics and performance metrics"),
                                        dbc.Button("Explore Players", href="/players", color="primary"),
                                    ])
                                ])
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Champions", className="card-title"),
                                        html.P("Analyze champion win rates and meta trends"),
                                        dbc.Button("View Champions", href="/champions", color="primary"),
                                    ])
                                ])
                            ], width=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H4("Teams", className="card-title"),
                                        html.P("Compare team performances and statistics"),
                                        dbc.Button("See Teams", href="/teams", color="primary"),
                                    ])
                                ])
                            ], width=4),
                        ], className="mb-4"),
                    ], className="py-5")
                ])
            ])
        ])


# Create the Flask app for Gunicorn
app = dash_app.server

if __name__ == "__main__":
    dash_app.run_server(debug=True)
