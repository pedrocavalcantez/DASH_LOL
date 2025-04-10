from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from data_processor import DataProcessor
import pandas as pd

data_processor = DataProcessor()

# Dropdown options
champions = data_processor.get_champion_stats()["champion"].unique()
champions = [champ for champ in champions if pd.notna(champ) and champ.strip()]
# print(champions[0:3])
leagues = data_processor.get_all_leagues()
leagues = [l for l in leagues if pd.notna(l) and l.strip()]

# Date slider options
all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}
# print("All Dates: ", date_marks)

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Champion Statistics", className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Champion:"),
                                dcc.Dropdown(
                                    id="champion-dropdown",
                                    options=[
                                        {"label": champ, "value": champ}
                                        for champ in champions
                                    ],
                                    value=None,
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Select League(s):"),
                                dcc.Dropdown(
                                    id="league-dropdown",
                                    options=[{"label": l, "value": l} for l in leagues],
                                    multi=True,
                                    placeholder="All leagues",
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
                html.Div(
                    id="champion-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [dcc.Graph(id="champion-winrate-graph")], width=6
                                ),
                                dbc.Col([dcc.Graph(id="champion-kda-graph")], width=6),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Champion Overview", className="mt-4"),
                                        html.Div(id="champion-stats-table"),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Match History", className="mt-4"),
                                        html.Div(id="champion-match-history"),
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
        Output("champion-winrate-graph", "figure"),
        Output("champion-kda-graph", "figure"),
        Output("champion-stats-table", "children"),
        Output("champion-match-history", "children"),
        Output("champion-content", "style"),
    ],
    [
        Input("champion-dropdown", "value"),
        Input("date-slider", "value"),
        Input("league-dropdown", "value"),
    ],
)
def update_champion_stats(selected_champion, date_index_range, selected_leagues):
    if not selected_champion:
        return {}, {}, html.Div(), html.Div(), {"display": "none"}

    print("Selected Champion: ", selected_champion)
    print("Date Index Range: ", date_index_range)
    print("Selected Leagues: ", selected_leagues)

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    champion_data = data_processor.get_champion_stats(
        selected_champion, start_date, end_date, selected_leagues
    )
    df_matches = data_processor.get_champion_match_history(
        selected_champion, start_date, end_date, selected_leagues
    )

    # Win Rate Graph
    winrate_fig = px.pie(
        champion_data,
        names="result",
        title=f"Win Rate for {selected_champion}",
        labels={"result": "Win Rate"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    # KDA Graph
    kda_fig = px.bar(
        champion_data,
        x=["kills", "deaths", "assists"],
        title=f"KDA Stats for {selected_champion}",
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
                            html.Td(f"{champion_data['result'].mean() * 100:.2f}%"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Kills"),
                            html.Td(f"{champion_data['kills'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Deaths"),
                            html.Td(f"{champion_data['deaths'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Assists"),
                            html.Td(f"{champion_data['assists'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average KDA"),
                            html.Td(f"{champion_data['kda'].mean():.2f}"),
                        ]
                    ),
                ]
            ),
        ],
        bordered=True,
        hover=True,
    )

    history_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("League"),
                        html.Th("Date"),
                        html.Th("Team"),
                        html.Th("Result"),
                        html.Th("Opponent Team"),
                        html.Th("Opponent Champion"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["league"]),
                            html.Td(row["date"]),
                            html.Td(row["teamname_champ"]),
                            html.Td("Win" if row["result"] == 1 else "Loss"),
                            html.Td(row["teamname_opp"]),
                            html.Td(row["champion_opp"]),
                        ],
                        className="table-success"
                        if row["result"] == 1
                        else "table-danger",
                    )
                    for _, row in df_matches.iterrows()
                ]
            ),
        ],
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
    )

    return winrate_fig, kda_fig, stats_table, history_table, {}
