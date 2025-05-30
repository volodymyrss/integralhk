#!flask/bin/python
from flask import Flask, url_for, jsonify, send_file, request

import logging

import os
import sys
import glob
import time

import re
import logging
import socket

import time
from datetime import datetime, timezone

import numpy as np

pi=np.pi

app = Flask(__name__)

logger = logging.getLogger(__name__)

import diskcache

from integralhk import data, prophet
from integralhk.exception import GeneratorException

@app.errorhandler(GeneratorException)
def handle_generator_exception(e):
    return e.message, 400


@app.route('/api/v1.0/rthealth', methods=['GET'])
def rthealth():
    dt = float(request.args.get('dt', 10))

    t0_recently = datetime.fromtimestamp(time.time() - dt - 50, timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

    t0 = request.args.get('t0', t0_recently)
    
    prophecy = prophet.predict(time=t0)

    try:
        lcdata = data.getrealtime(t0, dt, json=True)[0].to_dict('tight')['data']
    except Exception as e:
        logger.info('no realtime data accessible: %s', e)
        lcdata = []

    have_data = len(lcdata) > 1
    
    if prophecy[1]['expected_data_status'] == 'ONLINE':
        logger.info('prophecy says data will be online')    
        if not have_data:
            logger.info('but we have no data')
            return jsonify({'status': 'NOK',
                            'reason': f'no data (lcdata={lcdata}) while we expect some: {prophecy}'}), 400
        else:
            logger.info('and we have data')
    else:
        logger.info('prophecy says data will not be online')        
        
    return jsonify({'status': 'OK', 'prophecy': prophecy, 'lcdata_len': len(lcdata)}), 200

    


@app.route('/api/v1.0/ipnlc/<string:t0>/<string:dt>', methods=['GET'])
def ipnlc(t0, dt):

    d=data.getipn(t0, dt)

    return d[0]

@app.route('/api/v1.0/genlc/<string:target>/<string:t0>/<string:dt>', methods=['GET'])
def genlc(target, t0, dt):
    d=data.getgenlc(target, t0, dt)
    return d[0]


@app.route('/api/v1.0/rtlc/<string:t0>/<string:dt>', methods=['GET'])
def rtlc(t0, dt):
    return_json = 'json' in request.args
    logger.info('requested rtlc with t0=%s dt=%s return_json=%s', t0, dt, return_json)

    if return_json:        
        try:
            d = data.getrealtime(t0, dt, json=True)[0].to_dict('tight')
        except Exception as e:
            logger.info('no realtime data accessible: %s', e)
            d = {'data': []}

        if 'prophecy' in request.args:
            logger.info('requested prophecy')
            d = {
                'lc': d,
                'prophecy': prophet.predict(time=t0)
            }
    else:
        d = data.getrealtime(t0, dt)[0]
    
    return d


@app.route('/api/v1.0/ephs/<string:t0>', methods=['GET'])
def ephs(t0):
    d = data.getephs(t0)
    #prediction = prophet.predict(time=t0)
    # TODO: check
    #return "ok", 200
    return d[0]


@app.route('/api/v1.0/status/<string:t0>', methods=['GET'])
def status(t0):
    d = data.getrealtime(t0, 1, json=True)[0].to_dict('tight')

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

    source = request.args.get('source', 'cons')

    j = data.get_timerange(t1, t2, only_columns=only_columns, source=source)
    return jsonify(j)



@app.route('/', methods=['GET'])
@app.route('/poke', methods=['GET'])
def poke():
    return "all is ok"


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    r = {}

    t = time.time()
    r['nrev_cons'] = len(glob.glob(os.path.join(
        os.environ.get("REP_BASE_PROD_ARC"), "scw/*")))
    r['tspent_cons'] = time.time() - t

    t = time.time()
    r['nrev_idx_cons'] = len(glob.glob(os.path.join(
        os.environ.get("REP_BASE_PROD_ARC"), "idx/scw/*")))
    r['tspent_idx_cons'] = time.time() - t

    if r['nrev_idx_cons'] > 0  and r['nrev_cons'] > 0:
        #if r['nrev_idx_cons'] > 0 and r['nrev_idx_nrt'] > 0 and r['nrev_cons'] > 0 and r['nrev_nrt'] > 0:
        return jsonify({'status': 'OK', **r}), 200
    else:
        return jsonify({'status': 'NOK', **r}), 400

if __name__ == '__main__':
        
    ##
    app.run(debug=False,port=port,host=host)
