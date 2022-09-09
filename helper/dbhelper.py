# from flask import request, jsonify
# from config import DB_CONFIG as conf
# from application import mysql

# class Database:
#     def __init__(self):
#         self.conn = mysql.connection.cursor()

    
#     def select(self, query):
#         self.conn.execute(query)
#         rows = self.conn.fetchall()
#         return rows

    
#     def delete(self, query):
#         self.conn.execute(query)
#         mysql.connection.commit()
#         self.conn.close()
#         return True

    
#     def insert(self, table_name, **data):
#         keys = ', '.join(['%s'] * len(data))
#         columns = ', '.join(data.keys())
#         values = tuple(data.values())
#         sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, keys)
#         self.conn.execute(sql, values)
#         mysql.connection.commit()
#         self.conn.close()
#         last_id = self.conn.lastrowid
#         return last_id

    
#     def Update(self, table, where, **d):
#         sql = 'UPDATE ' + table + ' SET {}'.format(', '.join('{}=%s'.format(k) for k in d))
#         sql = sql + ' WHERE ' + where
#         write_to_file(sql)
#         values = tuple(d.values())
#         self.conn.execute(sql, values)
#         mysql.connection.commit()
#         self.conn.close()
#         last_id = self.conn.lastrowid
#         return last_id


# def write_to_file(data):
#     f = open("output.txt", "w")
#     f.write(data)
#     f.close()



#                         ******************************PYMYSQL VERSION *********************************

from flask import request
import pymysql
from config import DB_CONFIG as conf

DB = pymysql.connect(host=conf['host'], port=conf['port'], user=conf['username'], passwd=conf['password'],
                     db=conf['db'], autocommit=True, cursorclass=pymysql.cursors.DictCursor)
conn = DB.cursor()


class Database:
    def __init__(self):
        self.conn = conn

    @staticmethod
    def insert(table, **data):
        keys = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        values = tuple(data.values())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table, columns, keys)
        conn.execute(sql, values)
        last_id = conn.lastrowid
        return last_id


    @staticmethod
    def select(query):
        conn.execute(query)
        rows = conn.fetchall()
        return rows

    @staticmethod
    def Update(table, where, **d):
        sql = 'UPDATE ' + table + ' SET {}'.format(', '.join('{}=%s'.format(k) for k in d))
        sql = sql + ' WHERE ' + where
        write_to_file(sql)
        values = tuple(d.values())
        conn.execute(sql, values)
        last_id = conn.lastrowid
        return last_id



def write_to_file(data):
    f = open("output.txt", "w")
    f.write(data)
    f.close()