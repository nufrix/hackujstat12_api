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


# NEW VERSION OF DATA LOADING

def load_parties_2():
    parties_files = [f for f in os.listdir('.') if f.startswith('kvros')]
    parties = {}
    last_header = None

    for party_file in parties_files:
        with open(party_file, 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            header = next(reader)

            # Sanity check for header
            if header is not None:
                last_header = header
            else:
                assert header == last_header

            for line in reader:
                if line[5] not in parties:
                    if line[9]:
                        parties[line[5]] = '{} ({})'.format(line[7], line[9])
                    else:
                        parties[line[5]] = line[7]

    return parties




def load_candidates_2():
    # Candidates
    candidates_files = [f for f in os.listdir('.') if f.startswith('kvrk')]
    candidates_ids = {}  # Just candidates for inmemory search. fullname: <id>
    candidates = []  # all data related to candidate
    last_generated_id = 0  # 0 is never used
    last_header = None
    parties = load_parties_2()

    for candidate_file in candidates_files:
        year = candidate_file.split('_')[-1].split('.')[0]
        with open(candidate_file, 'r') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            header = next(reader)

            # Sanity check for header
            if header is not None:
                last_header = header
            else:
                assert header == last_header

            header.append('FULLNAME')
            header.append('ID')
            header.append('YEAR')

            for line in reader:
                # For each candidate, create FULLNAME column for search purposes
                #
                # FULLNAME consists of title before, name, surname and title after
                fullname = ('{} {} {} {}'.format(line[8], line[6], line[7], line[9])).strip()
                unique_id = '{} {}'.format(fullname, int(year) - (int(line[10]) if line[10] else 0))  # fullname, year of birth

                # Generate IDs
                if unique_id not in candidates_ids:
                    last_generated_id += 1
                    candidates_ids[unique_id] = last_generated_id
                generated_id = candidates_ids[unique_id]

                line.append(fullname)
                line.append(generated_id)
                line.append(int(year))
                line[4] = parties[line[4]]
                candidates.append(line)

    return last_header, candidates


def process_candidates_2():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    header, data = load_candidates_2()
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
    process_candidates_2()