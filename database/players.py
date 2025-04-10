import pandas as pd
from .base import get_conn


def get_player_stats(player_name=None, start_date=None, end_date=None):
    conn = get_conn()
    if player_name:
        query = """
            SELECT playername, AVG(kills) as kills, AVG(deaths) as deaths,
                AVG(assists) as assists, AVG(kda) as kda, AVG(totalgold) as totalgold
        FROM matches
        WHERE playername = ? AND date BETWEEN ? AND ?
        GROUP BY playername
    """
        return pd.read_sql_query(
            query, conn, params=(player_name, start_date, end_date)
        )
    else:
        query = """
            SELECT distinct(playername)
            FROM matches
        """
        return pd.read_sql_query(query, conn)


def get_player_match_history(player_name=None, start_date=None, end_date=None):
    conn = get_conn()
    query = """
        SELECT gameid, date, position, playername, champion, kills, deaths,
               assists, totalgold, result
        FROM matches
        WHERE playername = ? AND date BETWEEN ? AND ?
        ORDER BY date DESC
    """
    df = pd.read_sql_query(query, conn, params=(player_name, start_date, end_date))
    if df.empty:
        return df

    placeholders = ",".join(["?"] * len(df))
    query_opponent = f"""
        SELECT gameid, date, position, playername, champion
        FROM matches
        WHERE playername != ?
          AND date BETWEEN ? AND ?
          AND gameid IN ({placeholders})
    """
    params = [player_name, start_date, end_date, *df["gameid"].tolist()]
    df_opponent = pd.read_sql_query(query_opponent, conn, params=params)

    df_merged = pd.merge(
        df,
        df_opponent.rename(
            columns={"playername": "opponent", "champion": "opponent_champion"}
        ),
        on=["date", "gameid", "position"],
    )
    return df_merged


def get_most_picked_champions(player_name=None, start_date=None, end_date=None):
    conn = get_conn()
    query = """
    SELECT 
        champion,
        COUNT(*) as num_games,
        ROUND(100*CAST(SUM(result) AS FLOAT) / COUNT(*), 2) as winrate,
        ROUND(CAST(SUM(kills) AS FLOAT) / COUNT(*), 2) as avg_kills,
        ROUND(CAST(SUM(deaths) AS FLOAT) / COUNT(*), 2) as avg_deaths,
        ROUND(CAST(SUM(assists) AS FLOAT) / COUNT(*), 2) as avg_assists,
        ROUND(CAST((sum(kills)+sum(assists)) AS FLOAT) / sum(deaths), 2) as kda
    FROM matches
    WHERE playername = ?
        AND position != 'team'
        AND date BETWEEN ? AND ?
    GROUP BY champion 
    ORDER BY num_games DESC
    """
    return pd.read_sql_query(query, conn, params=(player_name, start_date, end_date))
