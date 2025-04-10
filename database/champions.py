import pandas as pd
from .base import get_conn


def get_champion_stats(
    champion_name=None, start_date=None, end_date=None, leagues=None
):
    conn = get_conn()
    if champion_name is None:
        return pd.read_sql_query(
            "SELECT DISTINCT(champion) FROM matches",
            conn,
        )

    query = """
        SELECT champion, kills, deaths, assists, kda, result
        FROM matches
        WHERE champion = ?
          AND date BETWEEN ? AND ?
    """

    params = [champion_name, start_date, end_date]

    if leagues:
        placeholders = ",".join(["?"] * len(leagues))
        query += f" AND league IN ({placeholders})"
        params += leagues

    return pd.read_sql_query(query, conn, params=params)


def get_champion_match_history(
    champion_name=None, start_date=None, end_date=None, leagues=None
):
    conn = get_conn()

    query = """
        SELECT league,gameid,teamname,position,result,champion
        FROM matches
        WHERE champion = ?
          AND date BETWEEN ? AND ?
    """

    params = [champion_name, start_date, end_date]

    if leagues:
        placeholders = ",".join(["?"] * len(leagues))
        query += f" AND league IN ({placeholders})"
        params += leagues

    df1_champ = pd.read_sql_query(query, conn, params=params)
    # df1_champ = pd.read_sql_query(
    #     query, conn, params=[champion_name, "2024-01-01", "2026-01-01"]
    # )

    placeholders = ",".join(["?"] * len(df1_champ))
    query_opp = f"""
        SELECT gameid, date,position, teamname, champion 
        FROM matches 
        WHERE gameid IN ({placeholders})
    """
    df_opp = pd.read_sql_query(query_opp, conn, params=df1_champ.gameid.tolist())

    df_merged = pd.merge(
        df1_champ,
        df_opp,
        on=["gameid", "position"],
        how="left",
        suffixes=("_champ", "_opp"),
    ).query("champion_champ != champion_opp")

    return df_merged.sort_values(by="date", ascending=False).head(10)
