#! /usr/bin/env python
# -*- coding: utf-8 -*-
from werkzeug.exceptions import HTTPException

__author__ = 'nufrix'

from flask import Flask, g, jsonify, request
import sqlite3

HLIDACSTATU_API_TOKEN = '7f7297e6fe4842ffac1820e250a909d0'
DATABASE = 'data/api_data.db'

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

    with app.app_context():
        cursor = get_db().cursor()
        search_query = 'SELECT * FROM candidate WHERE FULLNAME LIKE "%{}%"'.format(query)

        if party:
            search_query = '{} AND {}'.format(search_query, 'OSTRANA="{}"'.format(party.encode('utf-8')))

        search_query = '{} ORDER BY POCHLASU {}'.format(search_query, sort)

        cursor.execute(search_query)
        result = cursor.fetchall()

        return jsonify(candidates=[{'id': item[-1], 'fullname': item[-2], 'age': item[10]} for item in result], count=len(result))

@app.route('/candidate/<int:candidate_id>', methods=['GET'])
def candidate(candidate_id):
    """Get details for given candidate."""
    with app.app_context():
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM candidate WHERE ID={}'.format(candidate_id))
        result = cursor.fetchone()

        return jsonify(fullname=result[-2], age=result[10], work=result[11], home=result[12], region=result[0],
                       party=result[4], council=result[1], vote_region=result[2], mandate=True if result[19]=="1" else False, votes=result[16],
                       votes_percent=result[18])


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
    app.run(debug=True, host='0.0.0.0')
