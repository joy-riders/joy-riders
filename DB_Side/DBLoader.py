import os
import mysql.connector
from dotenv import load_dotenv

class DBLoader:
    def __init__(self):
        load_dotenv()
        self.config = {
            "host":"localhost",
            "port":3306,
            "user": os.getenv('DB_USER'),
            "password": os.getenv('DB_PASSWORD'),
            "database":"tco_system"
        }

    def sendquery(self, query:str) -> list:
        try:
            with mysql.connector.connect(**self.config) as conn:
                with conn.cursor() as curs:
                    curs.execute(query)
                    rows = curs.fetchall()
                    return rows
        except mysql.connector.Error as err:
            print(err)
            return []

dbloader = DBLoader()
