import mysql.connector

class DBLoader:
    def __init__(self):
        self.config = {
            "host":"localhost",
            "port":3306,
            "user":"skn26",
            "password":"skn26",
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
