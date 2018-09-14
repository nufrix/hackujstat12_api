#! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'nufrix'

from flask import Flask

HLIDACSTATU_API_TOKEN = '7f7297e6fe4842ffac1820e250a909d0'


app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run(debug=True)
