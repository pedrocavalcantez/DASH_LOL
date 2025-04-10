from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from data_processor import DataProcessor

data_processor = DataProcessor()

# Carrega filtros
patches = data_processor.get_all_patches()
patches = [str(p).strip() for p in patches if pd.notna(p)]
leagues = data_processor.get_all_leagues()
leagues = [l for l in leagues if pd.notna(l) and l.strip()]

all_dates = data_processor.get_all_dates()
all_dates = sorted(pd.to_datetime(all_dates).dt.date.unique())
date_marks = {i: str(date) for i, date in enumerate(all_dates)}

layout = html.Div(
    [
        dbc.Container(
            [
                html.H1("Patch Analysis", className="mb-4"),
                # Filtros
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select Patch:"),
                                dcc.Dropdown(
                                    id="patch-dropdown",
                                    options=[{"label": p, "value": p} for p in patches],
                                    multi=True,
                                    placeholder="All patches",
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
                # Conteúdo
                html.Div(
                    id="patch-content",
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3(
                                            "Most Picked Champions", className="mt-4"
                                        ),
                                        html.Div(id="patch-most-picked-champions"),
                                    ]
                                )
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
        Output("patch-most-picked-champions", "children"),
        Output("patch-content", "style"),
    ],
    [
        Input("patch-dropdown", "value"),
        Input("league-dropdown", "value"),
        Input("date-slider", "value"),
    ],
)
def update_patch_analysis(selected_patch, selected_leagues, date_index_range):
    selected_patches = selected_patch if selected_patch else patches

    start_date = str(all_dates[int(date_index_range[0])])
    end_date = str(all_dates[int(date_index_range[1])])

    df = data_processor.get_patch_champion_stats(
        selected_patches, start_date, end_date, selected_leagues
    )

    if df.empty:
        return html.Div("No data available."), {"display": "none"}

    # Divide em duas linhas
    row1_positions = ["top", "jng", "mid"]
    row2_positions = ["bot", "sup"]

    row1 = []
    row2 = []

    for pos in row1_positions + row2_positions:
        df_pos = df[df["position"] == pos]
        if df_pos.empty:
            continue

        table = dbc.Table(
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
                        for _, row in df_pos.head(5).iterrows()
                    ]
                ),
            ],
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
        )

        col = dbc.Col(
            [
                html.H5(pos.upper(), className="text-center mb-2"),
                table,
            ],
            width="auto",
            style={"padding": "0 20px"},
        )

        if pos in row1_positions:
            row1.append(col)
        else:
            row2.append(col)

    # Retorna as duas linhas empilhadas
    return html.Div(
        [
            dbc.Row(row1, justify="center", className="gy-4"),
            dbc.Row(row2, justify="center", className="gy-4"),
        ]
    ), {}
