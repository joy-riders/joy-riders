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
