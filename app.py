#!flask/bin/python
from flask import Flask, url_for, jsonify, send_file, request

import requests

import os
import sys
import glob
import time

import copy
import re
import logging
import socket
import traceback

import pilton

import time 

from astropy.table import Table
from astropy.io import fits
import astropy.io as pyfits
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy import coordinates as coord
from astropy import time as atime

import subprocess
import tempfile
from retrying import retry
import requests

import numpy as np

pi=np.pi

import healpy

import pylru

from integralclient import converttime
from service_exception import ServiceException

app = Flask(__name__)

import diskcache

@app.route('/', methods=['GET'])
@app.route('/poke', methods=['GET'])
def poke():
    return "all is ok"


if __name__ == '__main__':
        
    ##
    app.run(debug=False,port=port,host=host)
