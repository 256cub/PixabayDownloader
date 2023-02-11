import datetime
import math
import os
import re
import time
from datetime import datetime, timedelta

import mysql.connector

import config


class MySQL:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            passwd=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            auth_plugin="mysql_native_password"
        )

    def select(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchall()
        self.connection.close()
        return sql_result

    def update(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        sql_cursor.close()
        return sql_cursor

    def get_last_record(self):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute('SELECT * FROM activity ORDER BY id DESC LIMIT 1')
        sql_result = sql_cursor.fetchone()
        self.connection.close()
        return sql_result

    def close(self):
        self.connection.close()
