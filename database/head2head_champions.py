from .base import get_conn
import pandas as pd


def get_champion_stats_in_period(champion_name, start_date, end_date, leagues=None):
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
        WHERE champion = ?
          AND date BETWEEN ? AND ?
          AND position != 'team'
    """
    params = [champion_name, start_date, end_date]

    if leagues:
        placeholders = ",".join(["?"] * len(leagues))
        query += f" AND league IN ({placeholders})"
        params += leagues

    return pd.read_sql_query(query, conn, params=params)


def get_head2head_stats_champions(champ1, champ2, start_date, end_date, leagues=None):
    conn = get_conn()
    league_filter = ""
    league_params = []

    if leagues:
        placeholders = ",".join(["?"] * len(leagues))
        league_filter = f" AND league IN ({placeholders})"
        league_params = leagues

    query = f"""
        WITH games_between AS (
            SELECT gameid
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND champion IN (?, ?)
              AND position != 'team'
              {league_filter}
            GROUP BY gameid
            HAVING COUNT(DISTINCT champion) = 2
        )
        SELECT champion,
               COUNT(*) as games,
               SUM(result) as wins,
               ROUND(AVG(kills), 2) as avg_kills,
               ROUND(AVG(deaths), 2) as avg_deaths,
               ROUND(AVG(assists), 2) as avg_assists,
               ROUND(AVG(kda), 2) as avg_kda,
               ROUND(AVG(totalgold), 2) as avg_gold
        FROM matches
        WHERE champion IN (?, ?)
          AND position != 'team'
          AND gameid IN (SELECT gameid FROM games_between)
    """
    params = [start_date, end_date, champ1, champ2] + league_params + [champ1, champ2]
    return pd.read_sql_query(query, conn, params=params)


def get_head2head_match_history_champions(
    champ1, champ2, start_date, end_date, leagues=None
):
    conn = get_conn()
    league_filter = ""
    league_params = []

    if leagues:
        placeholders = ",".join(["?"] * len(leagues))
        league_filter = f" AND league IN ({placeholders})"
        league_params = leagues

    query = f"""
        WITH games_between AS (
            SELECT gameid, MAX(date) as date
            FROM matches
            WHERE date BETWEEN ? AND ?
              AND champion IN (?, ?)
              AND position != 'team'
              {league_filter}
            GROUP BY gameid
            HAVING COUNT(DISTINCT champion) = 2
        )
        SELECT m.gameid, g.date, m.champion, m.playername,
               m.kills, m.deaths, m.assists, m.kda, m.result
        FROM matches m
        JOIN games_between g ON m.gameid = g.gameid
        WHERE m.champion IN (?, ?)
          AND m.position != 'team'
        ORDER BY g.date DESC
    """
    params = [start_date, end_date, champ1, champ2] + league_params + [champ1, champ2]
    return pd.read_sql_query(query, conn, params=params)
