import pandas as pd
from .base import get_conn


def get_team_stats(team_name=None, start_date=None, end_date=None):
    conn = get_conn()
    if team_name:
        query = """
            SELECT teamname, AVG(kills) as kills, AVG(deaths) as deaths,
                   AVG(assists) as assists, AVG(totalgold) as totalgold, AVG(result) as result
            FROM matches
            WHERE teamname = ? AND date BETWEEN ? AND ?
            GROUP BY teamname
        """
        return pd.read_sql_query(query, conn, params=(team_name, start_date, end_date))
    else:
        query = """
            SELECT teamname, AVG(kills) as kills, AVG(deaths) as deaths,
                   AVG(assists) as assists, AVG(totalgold) as totalgold, AVG(result) as result
            FROM matches GROUP BY teamname
        """
        return pd.read_sql_query(query, conn)


def get_team_match_history(team_name, start_date=None, end_date=None):
    conn = get_conn()
    query = """
        SELECT gameid, date, teamname, kills, deaths, assists, totalgold, result
        FROM matches
        WHERE teamname = ? AND position = 'team' AND date BETWEEN ? AND ?
        ORDER BY date DESC
    """
    df = pd.read_sql_query(query, conn, params=(team_name, start_date, end_date))
    if df.empty:
        return df

    placeholders = ",".join(["?"] * len(df))
    query_opponent = f"""
        SELECT gameid, teamname
        FROM matches
        WHERE teamname != ?
          AND position = 'team'
          AND gameid IN ({placeholders})
    """
    params = [team_name, *df["gameid"].tolist()]
    df_opponent = pd.read_sql_query(query_opponent, conn, params=params)

    return pd.merge(
        df,
        df_opponent.rename(columns={"teamname": "opponent"}),
        on="gameid",
        how="left",
    )


def get_team_most_picked_champions(team_name=None, start_date=None, end_date=None):
    conn = get_conn()
    query = """
        WITH total_games AS (
            SELECT COUNT(DISTINCT gameid) as total
            FROM matches
            WHERE teamname = ? AND position != 'team' AND date BETWEEN ? AND ?
        )
        SELECT champion,
        100*COUNT(*)/(SELECT total FROM total_games) as num_ocurrences
        FROM matches
        WHERE teamname = ? AND
        position != 'team' and 
        date BETWEEN ? AND ?
        GROUP BY champion
        ORDER BY num_ocurrences DESC
    """
    print()
    return pd.read_sql_query(
        query,
        conn,
        params=(team_name, start_date, end_date, team_name, start_date, end_date),
    ).head(20)
