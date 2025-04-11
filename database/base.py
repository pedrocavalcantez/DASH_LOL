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
        conn = get_conn()
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
        )
        if self.cursor.fetchone():
            print("Database already initialized")
            return
        # data_dir="Z:/Repositorios Pessoais/DASH_LOL/data"
        all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        dfs = [pd.read_csv(os.path.join(data_dir, f)) for f in all_files]
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df = combined_df.query("datacompleteness=='complete'").drop(
            columns=[
                "datacompleteness",
                "url",
                "pick1",
                "pick2",
                "pick3",
                "pick4",
                "pick5",
                "playerid",
                "ban1",
                "ban2",
                "ban3",
                "ban4",
                "ban5",
                "teamid",
            ]
        )
        combined_df = combined_df.drop(
            columns=[
                col
                for col in combined_df.columns
                if col.endswith("25")
                or col.endswith("20")
                or col.endswith("15")
                or col.endswith("10")
            ]
        )
        for col in [
            "league",
            "split",
            "side",
            "position",
            "playername",
            "teamname",
            "champion",
        ]:
            combined_df[col] = combined_df[col].astype("category")

        gameids = combined_df["gameid"].astype("category").cat.codes
        combined_df["gameid"] = pd.to_numeric(gameids, downcast="unsigned")

        combined_df["date"] = pd.to_datetime(combined_df["date"]).astype("string")
        for col in combined_df.select_dtypes(include=["float"]):
            if (
                combined_df[col].dropna().apply(float.is_integer).all()
            ):  # VE SE TODOS OS VALORES CONSEGUEM SER COLOCADO PRA INTEGER
                combined_df[col] = combined_df[col].astype(
                    "Int64"
                )  # Int64 aceita valores nulos também

        for col in combined_df.select_dtypes(include=["float"]):
            if not combined_df[col].dropna().apply(float.is_integer).all():
                combined_df[col] = pd.to_numeric(combined_df[col], downcast="float")
        for col in combined_df.select_dtypes(include="category").columns:
            combined_df[col] = combined_df[col].cat.remove_unused_categories()

        # Remover colunas com valor único
        for col in combined_df.columns:
            if combined_df[col].nunique(dropna=False) == 1:
                combined_df.drop(columns=col, inplace=True)
        # pd.DataFrame(combined_df.dtypes).to_clipboard()
        # SELECT JUST SOME COLUMNS
        # combined_df.info(memory_usage="deep")
        # combined_df.memory_usage(deep=True).sort_values(ascending=False)
        # combined_df.dtypes
        # combined_df.nunique().sort_values()
        combined_df["kda"] = (
            combined_df["kills"] + combined_df["assists"]
        ) / combined_df["deaths"].replace(0, 1)

        combined_df = combined_df.query("date>='2023-01-01'")
        combined_df.to_sql("matches", self.conn, if_exists="replace", index=False)
        self.cursor.execute("VACUUM")
        self.cursor.execute("CREATE INDEX idx_playername ON matches(playername)")
        self.cursor.execute("CREATE INDEX idx_champion ON matches(champion)")
        self.cursor.execute("CREATE INDEX idx_teamname ON matches(teamname)")
        self.cursor.execute(
            "CREATE INDEX idx_champion_date ON matches (champion, date)"
        )
        # self.cursor.execute(
        #     "CREATE INDEX idx_gameid_teamname ON matches (gameid, teamname)"
        # )
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


def analyze_memory_usage(df):
    print("🔍 DataFrame Memory Usage Overview:\n")
    total_memory = df.memory_usage(deep=True).sum()
    print(f"Total memory usage: {total_memory / 1024**2:.2f} MB\n")

    mem_by_col = df.memory_usage(deep=True).sort_values(ascending=False)
    mem_percent = (mem_by_col / total_memory * 100).round(2)

    result = pd.DataFrame(
        {
            "Type": df.dtypes,
            "Memory_MB": (mem_by_col / 1024**2).round(2),
            "Memory_%": mem_percent,
            "Num_Unique": df.nunique(),
            "Example_Values": df.apply(
                lambda x: x.unique()[:3] if x.nunique() < 10 else "..."
            ),
        }
    )

    print(result)

    print("\n📌 Suggested Optimizations:\n")
    for col in df.columns:
        col_type = df[col].dtype
        nunique = df[col].nunique()
        if col_type == "object":
            if nunique / len(df) < 0.5:
                print(
                    f"- '{col}' → Convert to 'category' (object with few unique values)"
                )
        elif "int" in str(col_type):
            if df[col].min() >= 0:
                print(f"- '{col}' → Consider downcasting to 'unsigned' integer")
            else:
                print(f"- '{col}' → Consider downcasting to 'int32' or 'int16'")
        elif "float" in str(col_type):
            print(f"- '{col}' → Consider downcasting to 'float32'")
    return result


def analyze_sqlite_database(db_path="Z:/Repositorios Pessoais/DASH_LOL/lol_data.db"):
    print("🔍 SQLite Database Diagnostic\n")

    # 1. Tamanho do arquivo
    size_mb = os.path.getsize(db_path) / 1024**2
    print(f"📦 File size: {size_mb:.2f} MB\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Tabelas e número de linhas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    if not tables:
        print("⚠️ Nenhuma tabela encontrada.")
        conn.close()
        return

    print("📊 Tabelas e quantidade de linhas:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"- {table}: {count:,} linhas")
    print()

    # 3. Schema e tipos
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"🧱 Schema da tabela '{table}':")
        for col in columns:
            if col[2] == "REAL":
                print(f"  - {col[1]} ({col[2]})")  # col[1]: nome, col[2]: tipo
        print()

    # 4. Índices
    for table in tables:
        cursor.execute(f"PRAGMA index_list({table})")
        indexes = cursor.fetchall()
        if indexes:
            print(f"⚙️ Índices em '{table}':")
            for idx in indexes:
                print(f"  - {idx[1]}")
            print()

    conn.close()
    print("✅ Análise finalizada.")


# analyze_sqlite_database()
