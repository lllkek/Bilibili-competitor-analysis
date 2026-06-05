import pymysql


class MySqlHelper:
    def __init__(self, host, port, user, password, database, charset="utf8mb4"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset

    def get_connection(self):
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset
        )
        return conn

    def execute(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(sql, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def executemany(self, sql, data_list):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.executemany(sql, data_list)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def query(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()
            conn.close()

    def query_one(self, sql, params=None):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
        finally:
            cursor.close()
            conn.close()