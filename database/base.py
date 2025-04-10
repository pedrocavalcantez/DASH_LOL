import sqlite3
import pandas as pd
import os


class Database:
    def __init__(self, db_name="lol_data.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def initialize_database(self, data_dir="data"):
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
        )
        if self.cursor.fetchone():
            print("Database already initialized")
            return

        all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        dfs = [pd.read_csv(os.path.join(data_dir, f)) for f in all_files]
        combined_df = pd.concat(dfs, ignore_index=True)

        combined_df["kda"] = (
            combined_df["kills"] + combined_df["assists"]
        ) / combined_df["deaths"].replace(0, 1)

        combined_df.to_sql("matches", self.conn, if_exists="replace", index=False)

        self.cursor.execute("CREATE INDEX idx_playername ON matches(playername)")
        self.cursor.execute("CREATE INDEX idx_champion ON matches(champion)")
        self.cursor.execute("CREATE INDEX idx_teamname ON matches(teamname)")
        self.cursor.execute(
            "CREATE INDEX idx_champion_date ON matches (champion, date)"
        )
        self.cursor.execute(
            "CREATE INDEX idx_gameid_teamname ON matches (gameid, teamname)"
        )
        self.cursor.execute("CREATE INDEX idx_league ON matches (league)")
        self.cursor.execute(
            "CREATE INDEX idx_champion_position ON matches (champion,position)"
        )

        self.conn.commit()
        print("Database initialized successfully")


# Singleton
_db_instance = Database()


def get_conn():
    return _db_instance.conn
