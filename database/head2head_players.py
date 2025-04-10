from .base import get_conn
import pandas as pd


def get_player_stats_in_period(player_name, start_date, end_date):
    conn = get_conn()
    query = """
        SELECT COUNT(*) as games,
               ROUND(100.0 * AVG(result), 2) as winrate,
               ROUND(AVG(kills), 2) as avg_kills,
               ROUND(AVG(deaths), 2) as avg_deaths,
               ROUND(AVG(assists), 2) as avg_assists,
               ROUND(AVG(kda), 2) as avg_kda,
               ROUND(AVG(totalgold), 2) as avg_gold
        FROM matches
        WHERE playername = ?
          AND date BETWEEN ? AND ?
          AND position != 'team'
    """
    return pd.read_sql_query(query, conn, params=(player_name, start_date, end_date))


def get_head2head_stats(player1, player2, start_date, end_date):
    conn = get_conn()

    query = """
        WITH games_between AS (
            SELECT gameid, MAX(date) AS date
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND playername IN (?, ?)
            GROUP BY gameid
            HAVING COUNT(DISTINCT playername) = 2
        )
        SELECT
            m.playername,
            COUNT(*) as games,
            SUM(m.result) as wins,
            ROUND(AVG(m.kills), 2) as avg_kills,
            ROUND(AVG(m.deaths), 2) as avg_deaths,
            ROUND(AVG(m.assists), 2) as avg_assists,
            ROUND(AVG(m.kda), 2) as avg_kda,
            ROUND(AVG(m.totalgold), 2) as avg_gold
        FROM matches m
        JOIN games_between gb ON m.gameid = gb.gameid
        WHERE m.playername IN (?, ?)
          AND m.position != 'team'
        GROUP BY m.playername
    """

    params = [start_date, end_date, player1, player2, player1, player2]
    return pd.read_sql_query(query, conn, params=params)


def get_head2head_match_history(player1, player2, start_date, end_date):
    conn = get_conn()
    query = """
        WITH both_players_games AS (
            SELECT gameid, MAX(date) AS date
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND playername IN (?, ?)
              AND position != 'team'
            GROUP BY gameid
            HAVING COUNT(DISTINCT playername) = 2
        )
        SELECT m.gameid, m.date, m.playername, m.champion,
               m.kills, m.deaths, m.assists, m.kda, m.result
        FROM matches m
        JOIN both_players_games g ON m.gameid = g.gameid
        WHERE m.playername IN (?, ?)
        ORDER BY m.date DESC
    """
    params = [start_date, end_date, player1, player2, player1, player2]
    return pd.read_sql_query(query, conn, params=params)
