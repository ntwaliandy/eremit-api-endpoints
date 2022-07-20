from flask import Flask, redirect, request, url_for, render_template
from flask_mysqldb import MySQL
from config import DB_CONFIG

application = Flask(__name__)

application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = DB_CONFIG['username']
application.config['MYSQL_PASSWORD'] = DB_CONFIG['password']
application.config['MYSQL_DB'] = DB_CONFIG['db']
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(application)