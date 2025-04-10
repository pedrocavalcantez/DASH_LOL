from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from data_processor import DataProcessor
import pandas as pd

data_processor = DataProcessor()

# Dropdown options
teams = data_processor.get_team_stats()["teamname"].unique()
teams = [team for team in teams if pd.notna(team) and team.strip()]
# print(teams[0:3])
# Date slider options
all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Team Statistics", className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Team:"),
                                dcc.Dropdown(
                                    id="team-dropdown",
                                    options=[
                                        {"label": team, "value": team} for team in teams
                                    ],
                                    value=None,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Select Date Range:"),
                                dcc.RangeSlider(
                                    id="date-slider",
                                    min=0,
                                    max=len(all_dates) - 1,
                                    value=[0, len(all_dates) - 1],
                                    marks={
                                        i: date_marks[i]
                                        for i in range(
                                            0,
                                            len(all_dates),
                                            max(1, len(all_dates) // 6),
                                        )
                                    },
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                    allowCross=False,
                                ),
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                # Conteúdo condicional
                html.Div(
                    id="team-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col([dcc.Graph(id="team-winrate-graph")], width=6),
                                dbc.Col(
                                    [dcc.Graph(id="team-performance-graph")], width=6
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Team Overview", className="mt-4"),
                                        html.Div(id="team-stats-table"),
                                    ]
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Recent Matches", className="mt-4"),
                                        html.Div(id="team-match-history"),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.H3(
                                            "Most Picked Champions", className="mt-4"
                                        ),
                                        html.Div(id="team-most-picked-champions"),
                                    ]
                                ),
                            ]
                        ),
                    ],
                ),
            ]
        )
    ]
)


@callback(
    [
        Output("team-winrate-graph", "figure"),
        Output("team-performance-graph", "figure"),
        Output("team-stats-table", "children"),
        Output("team-match-history", "children"),
        Output("team-most-picked-champions", "children"),
        Output("team-content", "style"),  # controla visibilidade
    ],
    [Input("team-dropdown", "value"), Input("date-slider", "value")],
)
def update_team_stats(selected_team, date_index_range):
    if not selected_team:
        hidden = {"display": "none"}
        return {}, {}, html.Div(), html.Div(), html.Div(), hidden

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    team_data = data_processor.get_team_stats(selected_team, start_date, end_date)
    match_history = data_processor.get_team_match_history(
        selected_team, start_date, end_date
    )

    # Win Rate Graph
    winrate_fig = px.pie(
        team_data,
        names="result",
        title=f"Win Rate for {selected_team}",
        labels={"result": "Win Rate"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    # Performance Graph
    performance_fig = px.bar(
        team_data,
        x=["kills", "deaths", "assists", "totalgold"],
        title=f"Team Performance for {selected_team}",
        labels={"value": "Average", "variable": "Stat"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    # Stats Table
    stats_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Stat"), html.Th("Value")])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td("Win Rate"),
                            html.Td(f"{team_data['result'].mean() * 100:.2f}%"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Kills"),
                            html.Td(f"{team_data['kills'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Deaths"),
                            html.Td(f"{team_data['deaths'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Assists"),
                            html.Td(f"{team_data['assists'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Gold"),
                            html.Td(f"{team_data['totalgold'].mean():.2f}"),
                        ]
                    ),
                ]
            ),
        ],
        bordered=True,
        hover=True,
    )

    # Recent Matches Table
    history_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Date"),
                        html.Th("Opponent"),
                        html.Th("Result"),
                        html.Th("Kills"),
                        html.Th("Deaths"),
                        html.Th("Assists"),
                        html.Th("Gold"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["date"]),
                            html.Td(row["opponent"]),
                            html.Td("Win" if row["result"] == 1 else "Loss"),
                            html.Td(row["kills"]),
                            html.Td(row["deaths"]),
                            html.Td(row["assists"]),
                            html.Td(row["totalgold"]),
                        ],
                        className="table-success"
                        if row["result"] == 1
                        else "table-danger",
                    )
                    for _, row in match_history.head(10).iterrows()
                ]
            ),
        ],
        bordered=True,
        hover=True,
        striped=True,
        size="sm",
    )
    most_picked = data_processor.get_team_most_picked_champions(
        selected_team, start_date, end_date
    )
    champions_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Champion"),
                        html.Th("Times Picked"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["champion"]),
                            html.Td(row["num_ocurrences"]),
                        ]
                    )
                    for _, row in most_picked.iterrows()
                ]
            ),
        ],
        bordered=True,
        hover=True,
        striped=True,
        size="sm",
    )

    return winrate_fig, performance_fig, stats_table, history_table, champions_table, {}
