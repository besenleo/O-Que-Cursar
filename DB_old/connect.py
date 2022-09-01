import psycopg2
from psycopg2.extras import DictCursor
from config import config
from flask import g

def db_connector():
    # Lê parametros de conexão
    params = config()
    # Conecta ao PostgreSQL server
    print('Conectando ao database PostgreSQL...')
    conn = psycopg2.connect(**params, cursor_factory=DictCursor)
    # Cria o cursor
    sql = conn.cursor()
    # Retorna o conexao e cursor
    return conn, sql

def get_db():
    db = db_connector()

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]

    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = db[1]

    return g.postgres_db_cur

def init_db():
    db = db_connector()

    db[1].execute(open('db_schema.sql', 'r').read())
    db[1].close()

    db[0].close()

# @app_teardown_appcontext
# def close_db(error):
#     if hasattr(g, 'postgres_db_cur'):
#         g.postgres_db_cur.close()

#     if hasattr(g, 'postgres_db_conn'):
#         g.postgres_db_conn.close()
