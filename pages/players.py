from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from data_processor import DataProcessor
import pandas as pd

data_processor = DataProcessor()

players = data_processor.get_player_stats()["playername"].unique()
players = [player for player in players if pd.notna(player) and player.strip()]
# print(players[0:3])
all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Player Statistics", className="mb-4"),
                # 🎯 Filtros: sempre visíveis
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Player:"),
                                dcc.Dropdown(
                                    id="player-dropdown",
                                    options=[
                                        {"label": player, "value": player}
                                        for player in players
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
                # 📦 Conteúdo condicional: esse será ocultado no callback
                html.Div(
                    id="player-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col([dcc.Graph(id="player-kda-graph")], width=6),
                                dbc.Col([dcc.Graph(id="player-gold-graph")], width=6),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Player Overview", className="mt-4"),
                                        html.Div(id="player-stats-table"),
                                    ]
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Recent Matches", className="mt-4"),
                                        html.Div(id="player-match-history"),
                                    ]
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3(
                                            "Most Picked Champions", className="mt-4"
                                        ),
                                        html.Div(id="player-most-picked-champions"),
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
        Output("player-kda-graph", "figure"),
        Output("player-gold-graph", "figure"),
        Output("player-stats-table", "children"),
        Output("player-match-history", "children"),
        Output("player-most-picked-champions", "children"),
        Output("player-content", "style"),
    ],
    [
        Input("player-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_player_stats(selected_player, date_index_range):
    if not selected_player:
        hidden = {"display": "none"}
        return {}, {}, html.Div(), html.Div(), html.Div(), hidden

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    player_data = data_processor.get_player_stats(selected_player, start_date, end_date)
    match_history = data_processor.get_player_match_history(
        selected_player, start_date, end_date
    )

    if match_history.empty:
        return (
            {},
            {},
            html.Div("No data available in selected range"),
            html.Div(),
            html.Div(),
        )

    kda_fig = px.bar(
        player_data,
        x=["kills", "deaths", "assists"],
        title=f"KDA Stats for {selected_player}",
        labels={"value": "Average", "variable": "Stat"},
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    gold_fig = px.line(
        match_history,
        x="date",
        y="totalgold",
        title=f"Gold Progression for {selected_player}",
        labels={"totalgold": "Gold", "date": "Date"},
    )

    stats_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Stat"), html.Th("Value")])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td("Average Kills"),
                            html.Td(f"{player_data['kills'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Deaths"),
                            html.Td(f"{player_data['deaths'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Assists"),
                            html.Td(f"{player_data['assists'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average KDA"),
                            html.Td(f"{player_data['kda'].mean():.2f}"),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Average Gold"),
                            html.Td(f"{player_data['totalgold'].mean():.2f}"),
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
                        html.Th("Date"),
                        html.Th("Champion"),
                        html.Th("Vs"),
                        html.Th("Enemy Champion"),
                        html.Th("K/D/A"),
                        html.Th("Gold"),
                        html.Th("Result"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["date"]),
                            html.Td(row["champion"]),
                            html.Td(""),
                            html.Td(row["opponent_champion"]),
                            html.Td(f"{row['kills']}/{row['deaths']}/{row['assists']}"),
                            html.Td(f"{row['totalgold']:.0f}"),
                            html.Td("Win" if row["result"] == 1 else "Loss"),
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

    champ_data = data_processor.get_most_picked_champions(
        selected_player, start_date, end_date
    )

    champions_table = dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Champion"),
                        html.Th("Games"),
                        html.Th("Winrate"),
                        html.Th("Kills"),
                        html.Th("Deaths"),
                        html.Th("Assists"),
                        html.Th("KDA"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["champion"]),
                            html.Td(row["num_games"]),
                            html.Td(f"{row['winrate']}%"),
                            html.Td(row["avg_kills"]),
                            html.Td(row["avg_deaths"]),
                            html.Td(row["avg_assists"]),
                            html.Td(row["kda"]),
                        ]
                    )
                    for _, row in champ_data.iterrows()
                ]
            ),
        ],
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
    )
    return kda_fig, gold_fig, stats_table, history_table, champions_table, {}
