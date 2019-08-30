import pytest
import time
from flask import url_for


def test_genlc(client):
    t0=time.time()
    r=client.get(url_for('genlc', target="ACS", t0='2019-06-10T11:27:45', dt="30"))
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
    
