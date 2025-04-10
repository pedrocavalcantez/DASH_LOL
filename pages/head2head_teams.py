from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
from data_processor import DataProcessor

data_processor = DataProcessor()

teams = data_processor.get_team_stats()["teamname"].unique()
teams = [t for t in teams if pd.notna(t) and t.strip()]

all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Head-to-Head: Team vs Team", className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Team A"),
                                dcc.Dropdown(
                                    id="team1-dropdown",
                                    options=[{"label": t, "value": t} for t in teams],
                                    placeholder="Select Team A",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Team B"),
                                dcc.Dropdown(
                                    id="team2-dropdown",
                                    options=[{"label": t, "value": t} for t in teams],
                                    placeholder="Select Team B",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Date Range"),
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
                            width=4,
                        ),
                    ],
                    className="mb-4",
                ),
                html.Div(
                    id="head2head-teams-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Stats: Team A"),
                                        html.Div(id="team1-stats"),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H4("Stats: Team B"),
                                        html.Div(id="team2-stats"),
                                    ],
                                    width=6,
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Direct Confrontations"),
                                        html.Div(id="head2head-teams-stats"),
                                    ]
                                )
                            ],
                            className="mb-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Match History"),
                                        html.Div(id="head2head-teams-history"),
                                    ]
                                )
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
        Output("team1-stats", "children"),
        Output("team2-stats", "children"),
        Output("head2head-teams-stats", "children"),
        Output("head2head-teams-history", "children"),
    ],
    [
        Input("team1-dropdown", "value"),
        Input("team2-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_head2head_teams(team1, team2, date_index_range):
    if not team1 or not team2 or team1 == team2:
        msg = html.Div("Select two different teams.")
        return msg, msg, html.Div(), html.Div()

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    stats1 = data_processor.get_team_stats_in_period(team1, start_date, end_date)
    stats2 = data_processor.get_team_stats_in_period(team2, start_date, end_date)
    h2h_stats = data_processor.get_head2head_stats_teams(
        team1, team2, start_date, end_date
    )
    h2h_history = data_processor.get_head2head_match_history_teams(
        team1, team2, start_date, end_date
    )

    def build_team_stats(df, name):
        if df.empty:
            return html.Div(f"No data for {name}")
        row = df.iloc[0]
        return dbc.Table(
            [
                html.Tbody(
                    [
                        html.Tr([html.Td("Games"), html.Td(row["games"])]),
                        html.Tr(
                            [html.Td("Winrate"), html.Td(f"{row['winrate']:.2f}%")]
                        ),
                        html.Tr([html.Td("Kills"), html.Td(row["avg_kills"])]),
                        html.Tr([html.Td("Deaths"), html.Td(row["avg_deaths"])]),
                        html.Tr([html.Td("Assists"), html.Td(row["avg_assists"])]),
                        html.Tr([html.Td("Gold"), html.Td(row["avg_gold"])]),
                    ]
                )
            ],
            bordered=True,
            hover=True,
            size="sm",
        )

    def build_h2h_table(df):
        if df.empty or len(df) < 2:
            return html.Div("No head-to-head games found.")
        row1 = df[df["teamname"] == team1].iloc[0]
        row2 = df[df["teamname"] == team2].iloc[0]

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Team"),
                            html.Th("Games"),
                            html.Th("Wins"),
                            html.Th("Kills"),
                            html.Th("Assists"),
                            html.Th("Gold"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(team1),
                                html.Td(row1["games"]),
                                html.Td(row1["wins"]),
                                html.Td(row1["avg_kills"]),
                                html.Td(row1["avg_assists"]),
                                html.Td(row1["avg_gold"]),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(team2),
                                html.Td(row2["games"]),
                                html.Td(row2["wins"]),
                                html.Td(row2["avg_kills"]),
                                html.Td(row2["avg_assists"]),
                                html.Td(row2["avg_gold"]),
                            ]
                        ),
                    ]
                ),
            ],
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
        )

    def build_match_history_table(df):
        if df.empty:
            return html.Div("No matches found.")
        pivoted = df.pivot(
            index="date",
            columns="teamname",
            values=["kills", "assists", "totalgold", "result"],
        )
        pivoted = pivoted.sort_index(ascending=False)

        rows = []
        for date, row in pivoted.iterrows():
            team1_win = row[("result", team1)] == 1
            row_class = "table-success" if team1_win else "table-danger"

            row_cells = [
                html.Td(str(date)),
                html.Td(row[("kills", team1)]),
                html.Td(row[("assists", team1)]),
                html.Td(row[("totalgold", team1)]),
                html.Td(row[("kills", team2)]),
                html.Td(row[("assists", team2)]),
                html.Td(row[("totalgold", team2)]),
            ]

            rows.append(html.Tr(row_cells, className=row_class))

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date"),
                            html.Th(f"{team1} Kills"),
                            html.Th("Assists"),
                            html.Th("Gold"),
                            html.Th(f"{team2} Kills"),
                            html.Th("Assists"),
                            html.Th("Gold"),
                        ]
                    )
                ),
                html.Tbody(rows),
            ],
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
        )

    return (
        build_team_stats(stats1, team1),
        build_team_stats(stats2, team2),
        build_h2h_table(h2h_stats),
        build_match_history_table(h2h_history),
    )
