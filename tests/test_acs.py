import pytest

def test_future():
    import integralhk.data as d    

    with pytest.raises(d.GeneratorException) as e:
        lc = d.getgenlc("ACS", "30000", "30")
        print(lc[0])
        assert e

    
def test_acs():
    import integralhk.data as d

    lc = d.getgenlc("ACS", "3000", "30")

    print(lc[0])

def test_ephs():
    import integralhk.data as d

    lc = d.getephs("3000")

    print(lc[0])

def test_att():
    import integralhk.data as d

    lc = d.getatt("3000")

    print(lc[0])

def test_realtime():
    import integralhk.data as d
    from integralhk.realtime import get_realtime_data
    import time

    lc = d.getrealtime(time.strftime("%Y-%m-%dT%H:%M:%S"), 50)

    print(lc[0])

