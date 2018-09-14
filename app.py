#! /usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.exceptions import HTTPException

__author__ = 'nufrix'

from flask import Flask, g, jsonify, request
import sqlite3
import zipfile

HLIDACSTATU_API_TOKEN = '7f7297e6fe4842ffac1820e250a909d0'
DATABASE = 'data/api_data.db'
DATABASE_ZIP = 'data/api_data.zip'

app = Flask(__name__)


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

        /find-candidates?query=Jiří%20Nová&party=komunistická&sort=desc
    """
    query = request.args.get('query').encode('utf-8')
    if query is None:
        raise ValueError('Missing request argument \"query\"')

    party = request.args.get('party')
    sort = request.args.get('sort', default='ASC').upper()
    year = request.args.get('year', default=2006, type=int)

    with app.app_context():
        cursor = get_db().cursor()
        search_query = 'SELECT * FROM candidate WHERE FULLNAME LIKE "%{}%" AND YEAR={}'.format(query, year)

        if party:
            search_query = '{} AND {}'.format(search_query, 'OSTRANA="{}"'.format(party.encode('utf-8')))

        search_query = '{} ORDER BY POCHLASU {}'.format(search_query, sort)

        cursor.execute(search_query)
        result = cursor.fetchall()

        return jsonify(candidates=[{'id': item[-2], 'fullname': item[-3], 'age': item[10]} for item in result], count=len(result))

@app.route('/candidate/<int:candidate_id>', methods=['GET'])
def candidate(candidate_id):
    """Get details for given candidate."""
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM candidate WHERE ID={}'.format(candidate_id))
        result = cursor.fetchall()

        return jsonify([{'fullname': item[-3], 'age': item[10], 'work': item[11], 'home': item[12], 'region': item[0],
                         'party': item[4], 'council': item[1], 'vote_region': item[2], 'mandate': True if item[19] == "1" else False,
                         'votes': item[16], 'votes_percent': item[18], 'year': item[-1]} for item in result])


@app.route('/parties', methods=['GET'])
def list_parties():
    """
    List all parties.

    E.g.:
        /parties?query=ksčm
    """
    query = request.args.get('query', default='')

    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT OSTRANA FROM candidate WHERE OSTRANA LIKE "%{}%" GROUP BY OSTRANA'.format(query.encode('utf-8')))
        result = cursor.fetchall()

        return jsonify(parties=[item[0] for item in result], count=len(result))


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    app.logger.exception('Unhandled exception.')
    return jsonify(error=str(e)), code


if __name__ == '__main__':
    zip_ref = zipfile.ZipFile(DATABASE_ZIP, 'r')
    zip_ref.extractall('data/')
    zip_ref.close()

    app.run(debug=True, host='0.0.0.0', port=8080)
