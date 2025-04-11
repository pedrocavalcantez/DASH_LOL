import sys
import os

# Caminho absoluto até a raiz do seu projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # diretório do script
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR))  # ou '..' se estiver em /scripts

# Adiciona a raiz do projeto ao path de import
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import pandas as pd
from database.base import get_conn
from database.players import get_player_stats, get_player_match_history
from database.teams import get_team_stats, get_team_match_history
from database.champions import get_champion_stats
from database.shared import get_all_dates

conn = get_conn()


# # CRIAR A DATABASE
# from database.base import Database

# # Initialize the database
# db = Database()
# # Initialize the database with your data
# db.initialize_database()


# # ▶️ Testes básicos:

# print("📅 Datas disponíveis:")
# print(get_all_dates().tail())

# print("\n👤 Estatísticas do player Robo:")
# print(get_player_stats("Robo", "2024-01-01", "2026-01-01"))

# print("\n📄 Partidas recentes do Robo:")
# df_robo = get_player_match_history("Robo", "2024-01-01", "2026-01-01")
# print(df_robo.head())

# print("\n🛡 Estatísticas do time LOUD:")
# print(get_team_stats("LOUD", "2024-01-01", "2026-01-01"))

# print("\n📄 Partidas recentes da LOUD:")
# df_team = get_team_match_history("LOUD", "2024-01-01", "2026-01-01")
# print(df_team.head())

# print("\n🏆 Estatísticas do campeão Jayce:")
# print(get_champion_stats("Jayce", "2024-01-01", "2026-01-01"))

# # Você também pode rodar queries manuais:
# print("\n🔎 5 primeiras linhas da tabela 'matches':")
# print(pd.read_sql_query("SELECT * FROM matches LIMIT 5", conn))


# def get_most_picked_champions(
#     player="", start_date="2024-01-01", end_date="2026-01-01"
# ):
#     query = """
#     SELECT
#         champion,
#         COUNT(*) as num_games,
#         ROUND(100*CAST(SUM(result) AS FLOAT) / COUNT(*), 2) as winrate,
#         ROUND(CAST(SUM(kills) AS FLOAT) / COUNT(*), 2) as avg_kills,
#         ROUND(CAST(SUM(deaths) AS FLOAT) / COUNT(*), 2) as avg_deaths,
#         ROUND(CAST(SUM(assists) AS FLOAT) / COUNT(*), 2) as avg_assists,
#         ROUND(CAST((sum(kills)+sum(assists)) AS FLOAT) / sum(deaths), 2) as kda
#     FROM matches
#     WHERE playername = ?
#         AND position != 'team'
#         AND date BETWEEN ? AND ?
#     GROUP BY champion
#     ORDER BY num_games DESC
#     """
#     return pd.read_sql_query(query, conn, params=(player, start_date, end_date))


# get_most_picked_champions("TitaN", "2024-01-01", "2026-01-01")

# pd.read_sql_query("SELECT * FROM matches LIMIT 5", conn).columns.tolist()
# pd.read_sql_query("SELECT teamname FROM matches LIMIT 5", conn)


# pd.read_sql_query("SELECT * FROM matches", conn).league.unique()
