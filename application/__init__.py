from flask import Flask, redirect, request, url_for, render_template

from helper.dbhelper import DB as DB_CON

application = Flask(__name__)
