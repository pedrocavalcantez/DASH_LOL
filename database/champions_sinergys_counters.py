from .base import get_conn
import pandas as pd


def _format_placeholders(lst):
    return ",".join(["?"] * len(lst))


def get_best_allies(champions, start_date, end_date, leagues=None):
    conn = get_conn()

    champ_placeholders = _format_placeholders(champions)
    league_filter = ""
    league_params = []

    if leagues:
        league_placeholders = _format_placeholders(leagues)
        league_filter = f" AND league IN ({league_placeholders})"
        league_params = leagues

    query = f"""
        WITH relevant_games AS (
            SELECT gameid, teamname
            FROM matches
            WHERE champion IN ({champ_placeholders})
              AND date BETWEEN ? AND ?
              AND position != 'team'
              {league_filter}
            GROUP BY gameid, teamname
            HAVING COUNT(DISTINCT champion) = {len(champions)}
        )
        SELECT m2.champion,
               COUNT(*) AS games,
               ROUND(100.0 * SUM(m1.result) / COUNT(*), 2) AS winrate
        FROM matches m1
        JOIN matches m2
          ON m1.gameid = m2.gameid AND m1.teamname = m2.teamname
        JOIN relevant_games rg
          ON m1.gameid = rg.gameid AND m1.teamname = rg.teamname
        WHERE m1.champion IN ({champ_placeholders})
          AND m2.champion NOT IN ({champ_placeholders})
          AND m2.position != 'team'
        GROUP BY m2.champion
        HAVING games >= 5
        ORDER BY winrate DESC
        LIMIT 10
    """

    params = champions + [start_date, end_date] + league_params + champions + champions
    return pd.read_sql_query(query, conn, params=params)


def get_best_against(champions, start_date, end_date, leagues=None):
    conn = get_conn()

    champ_placeholders = _format_placeholders(champions)
    league_filter = ""
    league_params = []

    if leagues:
        league_placeholders = _format_placeholders(leagues)
        league_filter = f" AND league IN ({league_placeholders})"
        league_params = leagues

    query = f"""
        WITH relevant_games AS (
            SELECT gameid, teamname
            FROM matches
            WHERE champion IN ({champ_placeholders})
              AND date BETWEEN ? AND ?
              AND position != 'team'
              {league_filter}
            GROUP BY gameid, teamname
            HAVING COUNT(DISTINCT champion) = {len(champions)}
        )
        SELECT m2.champion,
               COUNT(*) AS games,
               ROUND(100.0 * SUM(m1.result) / COUNT(*), 2) AS winrate
        FROM matches m1
        JOIN matches m2
          ON m1.gameid = m2.gameid AND m1.teamname != m2.teamname
        JOIN relevant_games rg
          ON m1.gameid = rg.gameid AND m1.teamname = rg.teamname
        WHERE m1.champion IN ({champ_placeholders})
          AND m2.champion NOT IN ({champ_placeholders})
          AND m2.position != 'team'
        GROUP BY m2.champion
        HAVING games >= 5
        ORDER BY winrate DESC
        LIMIT 10
    """

    params = champions + [start_date, end_date] + league_params + champions + champions
    return pd.read_sql_query(query, conn, params=params)


def get_worst_against(champions, start_date, end_date, leagues=None):
    conn = get_conn()

    champ_placeholders = _format_placeholders(champions)
    league_filter = ""
    league_params = []

    if leagues:
        league_placeholders = _format_placeholders(leagues)
        league_filter = f" AND league IN ({league_placeholders})"
        league_params = leagues

    query = f"""
        WITH relevant_games AS (
            SELECT gameid, teamname
            FROM matches
            WHERE champion IN ({champ_placeholders})
              AND date BETWEEN ? AND ?
              AND position != 'team'
              {league_filter}
            GROUP BY gameid, teamname
            HAVING COUNT(DISTINCT champion) = {len(champions)}
        )
        SELECT m2.champion,
               COUNT(*) AS games,
               ROUND(100.0 * SUM(m1.result) / COUNT(*), 2) AS winrate
        FROM matches m1
        JOIN matches m2
          ON m1.gameid = m2.gameid AND m1.teamname != m2.teamname
        JOIN relevant_games rg
          ON m1.gameid = rg.gameid AND m1.teamname = rg.teamname
        WHERE m1.champion IN ({champ_placeholders})
          AND m2.champion NOT IN ({champ_placeholders})
          AND m2.position != 'team'
        GROUP BY m2.champion
        HAVING games >= 5
        ORDER BY winrate ASC
        LIMIT 10
    """

    params = champions + [start_date, end_date] + league_params + champions + champions
    return pd.read_sql_query(query, conn, params=params)
