#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import sqlite3

DB_NAME = 'api_data.db'


def load_file(filename):
    header = []
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='\"')
        header = next(reader)
        header.append('FULLNAME')
        for line in reader:
            # For each candidate, create FULLNAME column for search purposes
            #
            # FULLNAME consists of title before, name, surname and title after
            fullname = ('{} {} {} {}'.format(line[8], line[6], line[7], line[9])).strip()
            line.append(fullname)
            data.append(line)

    return header, data

def process_candidates(filename='kvrk.csv'):
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    header, data = load_file(filename)
    if not header or not data:
        raise ValueError('No data: {}, {}'.format(header, data))

    create_query = 'CREATE TABLE candidate({})'.format(', '.join(header))
    insert_query = 'INSERT INTO candidate VALUES ({})'.format(','.join(['?' for _ in header]))

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(create_query)
    cursor.executemany(insert_query, data)
    connection.commit()


if __name__ == '__main__':
    process_candidates()