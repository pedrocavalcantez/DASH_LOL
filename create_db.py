import sys
import os

# Caminho absoluto até a raiz do seu projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # diretório do script
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR))  # ou '..' se estiver em /scripts

# Adiciona a raiz do projeto ao path de import
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from database.base import get_conn

conn = get_conn()
# CRIAR A DATABASE
from database.base import Database

# Initialize the database
db = Database()
# Initialize the database with your data
db.initialize_database()
