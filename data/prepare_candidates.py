#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import sqlite3

DB_NAME = 'api_data.db'


def load_candidates(filename_candidates, filename_parties):
    header = []
    data = []

    parties = load_parties(filename_parties)

    with open(filename_candidates, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='\"')
        header = next(reader)
        header.append('FULLNAME')
        header.append('ID')
        for index, line in enumerate(reader, start=1):
            # For each candidate, create FULLNAME column for search purposes
            #
            # FULLNAME consists of title before, name, surname and title after
            fullname = ('{} {} {} {}'.format(line[8], line[6], line[7], line[9])).strip()
            line.append(fullname)
            line.append(index)
            line[4] = parties[line[4]]
            data.append(line)

    return header, data


def load_parties(filename):
    data = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='\"')
        header = next(reader)

        for line in reader:
            if line[9]:
                data[line[5]] = '{} ({})'.format(line[7], line[9])
            else:
                data[line[5]] = line[7]

        return data


def process_candidates(filename_candidates='kvrk.csv', filename_parties='kvros.csv'):
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    header, data = load_candidates(filename_candidates, filename_parties)
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