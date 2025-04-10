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
