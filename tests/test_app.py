import pytest
import time
from datetime import datetime
from flask import url_for
from astropy.time import Time


def test_ipnlc(client):
    t0=time.time()
    r=client.get(url_for('ipnlc', t0='2019-06-10T11:27:45', dt="30"))
    print(r)
    assert r.status_code == 200

def test_genlc(client):
    t0=time.time()
    r=client.get(url_for('genlc', target="ACS", t0='2019-06-10T11:27:45', dt="30"))
    print(r)
    assert r.status_code == 200
    
def test_rtlc(client):
    t0 = Time(Time.now().unix - 100, format='unix')
    r = client.get(url_for('rtlc', t0=t0.isot, dt="10"))
    print(r.data[:1000])
    print(r)
    assert r.status_code == 200


def test_rtlc_future(client):
    t0 = Time(Time.now().unix + 1000, format='unix')
    r = client.get(url_for('rtlc', t0=t0.isot, dt="10"))
    print(r.data[:1000])
    print(r)
    assert r.status_code == 200



def test_att(client):
    r=client.get(url_for('att', t0='2019-06-10T11:27:45'))
    print(r)
    assert r.status_code == 200

def test_ephs(client):
    r=client.get(url_for('ephs', t0='2019-06-10T11:27:45'))
    print(r)
    assert r.status_code == 200
    
def test_future(client):
    r=client.get(url_for('ephs', t0='3019-06-10T11:27:45'))
    print(r)
    assert r.status_code == 400


def test_timerange(client):
    r=client.get(url_for('timerange', t1='2019-06-10T11:27:45', t2='2019-06-10T12:28:45'))
    print(r.json["attitude"].keys())
    print(r.json["attitude"]["RA_SCX"])


    print(r.json["orbit"]["XPOS"])
    print(r.json["orbit"]["RDIST"])


    for f in 'orbit', 'attitude':
        for k,v in r.json[f].items():
            print(k,":", v[:10])

    assert r.status_code == 200

def test_timerange_small(client):
    r=client.get(url_for('timerange', t1='2019-06-10T11:27:45', t2='2019-06-10T11:28:45'), query_string={'only-columns': 'XPOS,RA_SCX,RDIST'})
    print(r.json["attitude"].keys())
    print(r.json["attitude"]["RA_SCX"])


    print(r.json["orbit"]["XPOS"])
    print(r.json["orbit"]["RDIST"])


    for f in 'orbit', 'attitude':
        for k,v in r.json[f].items():
            print(k,":", v[:10])

    assert r.status_code == 200
