from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
from data_processor import DataProcessor

data_processor = DataProcessor()

# Carrega opções
champions = data_processor.get_champion_stats()["champion"].unique()
champions = [str(c).strip() for c in champions if pd.notna(c) and str(c).strip()]

leagues = data_processor.get_all_leagues()
leagues = [str(l).strip() for l in leagues if pd.notna(l) and str(l).strip()]

all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}


layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Champion Synergies & Counters", className="mb-4"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Champion(s):"),
                                dcc.Dropdown(
                                    id="champion-dropdown",
                                    options=[
                                        {"label": c, "value": c} for c in champions
                                    ],
                                    value=[],
                                    multi=True,
                                    placeholder="Select champion(s)",
                                ),
                            ],
                            width=4,
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
                            width=4,
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
                            width=4,
                        ),
                    ],
                    className="mb-4",
                ),
                html.Div(
                    id="synergy-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H4("🔗 Best Allies"),
                                        html.Div(id="best-allies-table"),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H4("✅ Best Against"),
                                        html.Div(id="best-against-table"),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H4("❌ Worst Against"),
                                        html.Div(id="worst-against-table"),
                                    ],
                                    width=4,
                                ),
                            ]
                        )
                    ],
                ),
            ]
        )
    ]
)


@callback(
    [
        Output("best-allies-table", "children"),
        Output("best-against-table", "children"),
        Output("worst-against-table", "children"),
    ],
    [
        Input("champion-dropdown", "value"),
        Input("league-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_synergies_and_counters(
    selected_champions, selected_leagues, date_index_range
):
    if not selected_champions:
        return html.Div("Select at least one champion."), html.Div(), html.Div()

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    df_allies = data_processor.get_best_allies(
        selected_champions, start_date, end_date, selected_leagues
    )
    df_best = data_processor.get_best_against(
        selected_champions, start_date, end_date, selected_leagues
    )
    df_worst = data_processor.get_worst_against(
        selected_champions, start_date, end_date, selected_leagues
    )

    def build_table(df):
        if df.empty:
            return html.Div("No data available.")
        return dbc.Table(
            [
                html.Thead(
                    html.Tr(
                        [html.Th("Champion"), html.Th("Games"), html.Th("Winrate (%)")]
                    )
                ),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(row["champion"]),
                                html.Td(row["games"]),
                                html.Td(f"{row['winrate']:.2f}%"),
                            ]
                        )
                        for _, row in df.iterrows()
                    ]
                ),
            ],
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
        )

    return build_table(df_allies), build_table(df_best), build_table(df_worst)
