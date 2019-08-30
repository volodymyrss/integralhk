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

@app.route('/api/v1.0/genlc/<string:target>/<string:t0>/<string:dt>', methods=['GET'])
def genlc(target, t0, dt):
    data.getgenlc(target, t0, dt)

    return "all is ok"

@app.route('/api/v1.0/ephs/<string:t0>', methods=['GET'])
def ephs(t0):
    data.getephs(t0)

    return "all is ok"

@app.route('/api/v1.0/att/<string:t0>', methods=['GET'])
def att(t0):
    data.getatt(t0)

    return "all is ok"

@app.route('/', methods=['GET'])
@app.route('/poke', methods=['GET'])
def poke():
    return "all is ok"


if __name__ == '__main__':
        
    ##
    app.run(debug=False,port=port,host=host)
