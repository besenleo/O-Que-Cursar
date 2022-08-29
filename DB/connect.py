#!/usr/bin/python
from fnmatch import fnmatch
import logging
import psycopg2
from config import config

def db_connector(func):
    """ Conecta ao PostgreSQL database server """
    def with_connection_(*args,**kwargs):
        # Lê parametros de conexão
        params = config()
        # Conecta ao PostgreSQL server
        print('Conectando ao database PostgreSQL...')
        conn = psycopg2.connect(**params)
        try: 
            rv = func(conn, *args, **kwargs)
        except Exception as error:
            conn.rollback()
            logging.error(f"Falha na conexão com Database: {error}")
            raise
        else:
            conn.commit()
        finally:
            conn.close()
        
        return rv
    
    return with_connection_

@db_connector
def get_db_version(conn):
    cur = conn.cursor()

    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    db_version = cur.fetchone()
    print(db_version)
       
    cur.close()

if __name__ == '__main__':
    get_db_version()