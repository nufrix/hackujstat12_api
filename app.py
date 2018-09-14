#! /usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.exceptions import HTTPException

__author__ = 'nufrix'

from flask import Flask, g, jsonify, request
import sqlite3

HLIDACSTATU_API_TOKEN = '7f7297e6fe4842ffac1820e250a909d0'


app = Flask(__name__)


DATABASE = 'data/api_data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/find-candidates', methods=['GET'], strict_slashes=False)
def find_candidates():
    """
    Try to find candidates by given query.

    E.g.:

        /find-candidates?query=Jiří Nová
    """
    print(request.args)
    query = request.args.get('query').encode('utf-8')
    if query is None:
        raise ValueError('Missing request argument \"query\"')

    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM candidate WHERE FULLNAME LIKE "%{}%"'.format(query))
        result = cursor.fetchall()

        return jsonify(candidates=[{'fullname': item[-1], 'age': item[10], 'work': item[11], 'home': item[12]} for item in result])

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


if __name__ == '__main__':
    app.run(debug=True)
