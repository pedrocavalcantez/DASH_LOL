import pandas as pd
from .base import get_conn


def get_all_dates():
    query = "SELECT DISTINCT date FROM matches ORDER BY date"
    return pd.read_sql_query(query, get_conn())["date"]


def get_all_columns():
    query = "SELECT * FROM matches LIMIT 0"
    df = pd.read_sql_query(query, get_conn())
    return {col: str(df[col].dtype) for col in df.columns}


def get_all_leagues():
    conn = get_conn()
    query = "SELECT DISTINCT league FROM matches ORDER BY league"
    return pd.read_sql_query(query, conn)["league"].tolist()


def get_all_patches():
    conn = get_conn()
    query = "SELECT DISTINCT patch FROM matches ORDER BY patch"
    return pd.read_sql_query(query, conn)["patch"].tolist()


def get_all_players(league=None):
    conn = get_conn()
    base_query = """
        SELECT DISTINCT playername
        FROM matches
        WHERE position != 'team'
    """

    params = []
    if league:
        base_query += " AND league = ?"
        params.append(league)

    base_query += " ORDER BY playername"

    return (
        pd.read_sql_query(base_query, conn, params=params)["playername"]
        .dropna()
        .str.strip()
        .tolist()
    )


def get_all_teams(league=None):
    conn = get_conn()
    base_query = """
        SELECT DISTINCT teamname
        FROM matches
        WHERE position != 'team'
    """

    params = []
    if league:
        base_query += " AND league = ?"
        params.append(league)

    base_query += " ORDER BY teamname"

    return (
        pd.read_sql_query(base_query, conn, params=params)["teamname"]
        .dropna()
        .str.strip()
        .tolist()
    )
