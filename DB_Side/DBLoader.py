import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
config = {
    "host": "localhost",
    "port": 3306,
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": "tco_system"
}

def sendquery(query: str) -> list:
    global config
    try:
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as curs:
                curs.execute(query)
                rows = curs.fetchall()
                return rows
    except mysql.connector.Error as err:
        print(err)
        return []

def sendquerys_with_commit(querys:list[str]) -> list:
    global config
    try:
        with mysql.connector.connect(**config) as conn:
            with conn.cursor() as curs:
                rows = []
                for q in querys:
                    curs.execute(q)
                    for r in curs.fetchall():
                        rows.append(r)

                curs.execute("COMMIT")
                return rows
    except mysql.connector.Error as err:
        print(err)
        return []