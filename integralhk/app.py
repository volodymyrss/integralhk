#!flask/bin/python
from flask import Flask, url_for, jsonify, send_file, request

import requests

import os
import sys
import glob
import time

import re
import logging
import socket

import time 

import numpy as np

pi=np.pi

app = Flask(__name__)

import diskcache

from integralhk import data
from integralhk.exception import GeneratorException

@app.errorhandler(GeneratorException)
def handle_generator_exception(e):
    return e.message, 400

@app.route('/api/v1.0/ipnlc/<string:t0>/<string:dt>', methods=['GET'])
def ipnlc(t0, dt):

    d=data.getipn(t0, dt)

    return d[0]

@app.route('/api/v1.0/genlc/<string:target>/<string:t0>/<string:dt>', methods=['GET'])
def genlc(target, t0, dt):

    d=data.getgenlc(target, t0, dt)

    return d[0]

@app.route('/api/v1.0/ephs/<string:t0>', methods=['GET'])
def ephs(t0):
    d=data.getephs(t0)

    return d[0]

@app.route('/api/v1.0/att/<string:t0>', methods=['GET'])
def att(t0):
    d = data.getatt(t0)

    return d[0]



@app.route('/api/v1.0/sc/<string:t1>/<string:t2>', methods=['GET'])
def timerange(t1, t2):
    only_columns = request.args.get('only-columns', None)
    if only_columns is not None:
        only_columns = only_columns.split(",")

    j = data.get_timerange(t1, t2, only_columns=only_columns)
    return jsonify(j)



@app.route('/', methods=['GET'])
@app.route('/poke', methods=['GET'])
def poke():
    return "all is ok"


if __name__ == '__main__':
        
    ##
    app.run(debug=False,port=port,host=host)
