from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
from data_processor import DataProcessor

data_processor = DataProcessor()

players = data_processor.get_player_stats()["playername"].unique()
players = [p for p in players if pd.notna(p) and p.strip()]

all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Head-to-Head: Player vs Player", className="mb-4"),
                # Filtros
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Player A"),
                                dcc.Dropdown(
                                    id="player1-dropdown",
                                    options=[{"label": p, "value": p} for p in players],
                                    placeholder="Select Player A",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Player B"),
                                dcc.Dropdown(
                                    id="player2-dropdown",
                                    options=[{"label": p, "value": p} for p in players],
                                    placeholder="Select Player B",
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
                # Resultado
                html.Div(
                    id="head2head-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Stats: Player A"),
                                        html.Div(id="player1-stats"),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H4("Stats: Player B"),
                                        html.Div(id="player2-stats"),
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
                                        html.Div(id="head2head-stats"),
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
                                        html.Div(id="head2head-history"),
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
        Output("player1-stats", "children"),
        Output("player2-stats", "children"),
        Output("head2head-stats", "children"),
        Output("head2head-history", "children"),
    ],
    [
        Input("player1-dropdown", "value"),
        Input("player2-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_head2head(player1, player2, date_index_range):
    if not player1 or not player2 or player1 == player2:
        msg = html.Div("Select two different players.")
        return msg, msg, html.Div(), html.Div()

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    stats1 = data_processor.get_player_stats_in_period(player1, start_date, end_date)
    stats2 = data_processor.get_player_stats_in_period(player2, start_date, end_date)
    h2h_df = data_processor.get_head2head_stats(player1, player2, start_date, end_date)
    h2h_history = data_processor.get_head2head_match_history(
        player1, player2, start_date, end_date
    )

    def build_stats_card(df, name):
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
                        html.Tr([html.Td("KDA"), html.Td(row["avg_kda"])]),
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
        p1_row = df[df["playername"] == player1].iloc[0]
        p2_row = df[df["playername"] == player2].iloc[0]

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Player"),
                            html.Th("Games"),
                            html.Th("Wins"),
                            html.Th("Kills"),
                            html.Th("Deaths"),
                            html.Th("Assists"),
                            html.Th("KDA"),
                            html.Th("Gold"),
                        ]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(player1),
                                html.Td(p1_row["games"]),
                                html.Td(p1_row["wins"]),
                                html.Td(p1_row["avg_kills"]),
                                html.Td(p1_row["avg_deaths"]),
                                html.Td(p1_row["avg_assists"]),
                                html.Td(p1_row["avg_kda"]),
                                html.Td(p1_row["avg_gold"]),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(player2),
                                html.Td(p2_row["games"]),
                                html.Td(p2_row["wins"]),
                                html.Td(p2_row["avg_kills"]),
                                html.Td(p2_row["avg_deaths"]),
                                html.Td(p2_row["avg_assists"]),
                                html.Td(p2_row["avg_kda"]),
                                html.Td(p2_row["avg_gold"]),
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
            columns="playername",
            values=["champion", "kills", "deaths", "assists", "kda", "result"],
        )
        pivoted = pivoted.sort_index(ascending=False)

        rows = []
        for date, row in pivoted.iterrows():
            # Verifica vitória de Player A
            player_a_win = row[("result", player1)] == 1
            row_class = "table-success" if player_a_win else "table-danger"

            row_cells = [
                html.Td(str(date)),
                html.Td(str(row[("champion", player1)])),
                html.Td(
                    f"{int(row[('kills', player1)])}/{int(row[('deaths', player1)])}/{int(row[('assists', player1)])}"
                ),
                html.Td(f"{row[('kda', player1)]:.2f}"),
                html.Td(str(row[("champion", player2)])),
                html.Td(
                    f"{int(row[('kills', player2)])}/{int(row[('deaths', player2)])}/{int(row[('assists', player2)])}"
                ),
                html.Td(f"{row[('kda', player2)]:.2f}"),
            ]

            rows.append(html.Tr(row_cells, className=row_class))

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date"),
                            html.Th(f"{player1} Champ"),
                            html.Th("K/D/A"),
                            html.Th("KDA"),
                            html.Th(f"{player2} Champ"),
                            html.Th("K/D/A"),
                            html.Th("KDA"),
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
        build_stats_card(stats1, player1),
        build_stats_card(stats2, player2),
        build_h2h_table(h2h_df),
        build_match_history_table(h2h_history),
    )
