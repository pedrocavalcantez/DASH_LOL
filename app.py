import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import os

# Initialize the Dash app
dash_app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

# Define the layout
dash_app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Players", href="/players")),
                dbc.NavItem(dbc.NavLink("Champions", href="/champions")),
                dbc.NavItem(dbc.NavLink("Teams", href="/teams")),
                dbc.NavItem(dbc.NavLink("Patch", href="/patch")),
                dbc.NavItem(dbc.NavLink("Best Matches", href="/best-matches")),
                dbc.NavItem(
                    dbc.NavLink("Head2Head Players", href="/head2head-players")
                ),
                dbc.NavItem(dbc.NavLink("Head2Head Teams", href="/head2head-teams")),
                dbc.NavItem(
                    dbc.NavLink("Head2Head Champions", href="/head2head-champions")
                ),
            ],
            brand="League of Legends Dashboard",
            brand_href="/",
            color="primary",
            dark=True,
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
        return html.Div(
            [
                html.H1("Welcome to Dashboard"),
                html.P(
                    "Select a category from the navigation bar above to explore the data."
                ),
            ]
        )


# Create the Flask app for Gunicorn
app = dash_app.server

if __name__ == "__main__":
    dash_app.run_server(debug=True)
