from .base import get_conn
import pandas as pd


def get_team_stats_in_period(team_name, start_date, end_date):
    conn = get_conn()
    query = """
        SELECT COUNT(*) as games,
               ROUND(100.0 * AVG(result), 2) as winrate,
               ROUND(AVG(kills), 2) as avg_kills,
               ROUND(AVG(deaths), 2) as avg_deaths,
               ROUND(AVG(assists), 2) as avg_assists,
               ROUND(AVG(totalgold), 2) as avg_gold
        FROM matches
        WHERE teamname = ?
          AND date BETWEEN ? AND ?
          AND position = 'team'
    """
    return pd.read_sql_query(query, conn, params=(team_name, start_date, end_date))


def get_head2head_stats_teams(team1, team2, start_date, end_date):
    conn = get_conn()

    query = """
        WITH games_between AS (
            SELECT gameid
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND teamname IN (?, ?)
              AND position = 'team'
            GROUP BY gameid
            HAVING COUNT(DISTINCT teamname) = 2
        )
        SELECT teamname,
               COUNT(*) as games,
               SUM(result) as wins,
               ROUND(AVG(kills), 2) as avg_kills,
               ROUND(AVG(assists), 2) as avg_assists,
               ROUND(AVG(totalgold), 2) as avg_gold
        FROM matches
        WHERE position = 'team'
          AND teamname IN (?, ?)
          AND gameid IN (SELECT gameid FROM games_between)
        GROUP BY teamname
    """
    params = [start_date, end_date, team1, team2, team1, team2]
    return pd.read_sql_query(query, conn, params=params)


def get_head2head_match_history_teams(team1, team2, start_date, end_date):
    conn = get_conn()

    query = """
        WITH games_between AS (
            SELECT gameid, MAX(date) as date
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND teamname IN (?, ?)
              AND position = 'team'
            GROUP BY gameid
            HAVING COUNT(DISTINCT teamname) = 2
        )
        SELECT m.gameid, g.date, m.teamname, m.kills, m.assists, m.totalgold, m.result
        FROM matches m
        JOIN games_between g ON m.gameid = g.gameid
        WHERE m.teamname IN (?, ?)
          AND m.position = 'team'
        ORDER BY g.date DESC
    """
    params = [start_date, end_date, team1, team2, team1, team2]
    return pd.read_sql_query(query, conn, params=params)
