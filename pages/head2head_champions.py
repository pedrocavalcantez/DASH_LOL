from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
from data_processor import DataProcessor

data_processor = DataProcessor()

champions = data_processor.get_champion_stats()["champion"].unique()
champions = [c for c in champions if pd.notna(c) and c.strip()]

leagues = data_processor.get_all_leagues()
leagues = [str(l).strip() for l in leagues if pd.notna(l) and str(l).strip()]

all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Head-to-Head: Champion vs Champion", className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Champion A"),
                                dcc.Dropdown(
                                    id="champ1-dropdown",
                                    options=[
                                        {"label": c, "value": c} for c in champions
                                    ],
                                    placeholder="Select Champion A",
                                ),
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Champion B"),
                                dcc.Dropdown(
                                    id="champ2-dropdown",
                                    options=[
                                        {"label": c, "value": c} for c in champions
                                    ],
                                    placeholder="Select Champion B",
                                ),
                            ],
                            width=3,
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
                            width=3,
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
                            width=3,
                        ),
                    ],
                    className="mb-4",
                ),
                html.Div(
                    id="head2head-champions-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("Stats: Champion A"),
                                        html.Div(id="champ1-stats"),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H4("Stats: Champion B"),
                                        html.Div(id="champ2-stats"),
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
                                        html.Div(id="head2head-champions-stats"),
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
                                        html.Div(id="head2head-champions-history"),
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
        Output("champ1-stats", "children"),
        Output("champ2-stats", "children"),
        Output("head2head-champions-stats", "children"),
        Output("head2head-champions-history", "children"),
    ],
    [
        Input("champ1-dropdown", "value"),
        Input("champ2-dropdown", "value"),
        Input("league-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_head2head_champions(champ1, champ2, selected_leagues, date_index_range):
    if not champ1 or not champ2 or champ1 == champ2:
        msg = html.Div("Select two different champions.")
        return msg, msg, html.Div(), html.Div()

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    stats1 = data_processor.get_champion_stats_in_period(
        champ1, start_date, end_date, selected_leagues
    )
    stats2 = data_processor.get_champion_stats_in_period(
        champ2, start_date, end_date, selected_leagues
    )
    h2h_stats = data_processor.get_head2head_stats_champions(
        champ1, champ2, start_date, end_date, selected_leagues
    )
    h2h_history = data_processor.get_head2head_match_history_champions(
        champ1, champ2, start_date, end_date, selected_leagues
    )

    def build_stat_table(df, label):
        if df.empty:
            return html.Div(f"No data for {label}")
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
        row1 = df[df["champion"] == champ1].iloc[0]
        row2 = df[df["champion"] == champ2].iloc[0]

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Champion"),
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
                                html.Td(champ1),
                                html.Td(row1["games"]),
                                html.Td(row1["wins"]),
                                html.Td(row1["avg_kills"]),
                                html.Td(row1["avg_assists"]),
                                html.Td(row1["avg_gold"]),
                            ]
                        ),
                        html.Tr(
                            [
                                html.Td(champ2),
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
            columns="champion",
            values=["playername", "kills", "deaths", "assists", "kda", "result"],
        )
        pivoted = pivoted.sort_index(ascending=False)

        rows = []
        for date, row in pivoted.iterrows():
            champ1_win = row[("result", champ1)] == 1
            row_class = "table-success" if champ1_win else "table-danger"

            row_cells = [
                html.Td(str(date)),
                html.Td(str(row[("playername", champ1)])),
                html.Td(
                    f"{int(row[('kills', champ1)])}/{int(row[('deaths', champ1)])}/{int(row[('assists', champ1)])}"
                ),
                html.Td(f"{row[('kda', champ1)]:.2f}"),
                html.Td(str(row[("playername", champ2)])),
                html.Td(
                    f"{int(row[('kills', champ2)])}/{int(row[('deaths', champ2)])}/{int(row[('assists', champ2)])}"
                ),
                html.Td(f"{row[('kda', champ2)]:.2f}"),
            ]
            rows.append(html.Tr(row_cells, className=row_class))

        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date"),
                            html.Th(f"{champ1} Player"),
                            html.Th("K/D/A"),
                            html.Th("KDA"),
                            html.Th(f"{champ2} Player"),
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
        build_stat_table(stats1, champ1),
        build_stat_table(stats2, champ2),
        build_h2h_table(h2h_stats),
        build_match_history_table(h2h_history),
    )
