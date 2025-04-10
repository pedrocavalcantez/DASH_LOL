# database/patch.py

from .base import get_conn
import pandas as pd


def get_patch_champion_stats(patches, start_date, end_date, leagues=None):
    conn = get_conn()

    query = """
        SELECT champion,
              position,
               COUNT(*) as games,
               ROUND(100.0 * SUM(result) / COUNT(*), 2) as winrate
        FROM matches
        WHERE patch IN ({patches_placeholder})
          AND date BETWEEN ? AND ?
    """

    params = []
    patches_placeholder = ",".join(["?"] * len(patches))
    params.extend(patches)
    params += [start_date, end_date]

    if leagues:
        league_placeholder = ",".join(["?"] * len(leagues))
        query += f" AND league IN ({league_placeholder})"
        params.extend(leagues)

    query += " GROUP BY champion ORDER BY games DESC"

    full_query = query.format(patches_placeholder=patches_placeholder)

    return pd.read_sql_query(full_query, conn, params=params)
