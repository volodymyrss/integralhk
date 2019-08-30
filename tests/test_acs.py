def test_future():
    import integralhk.data as d

    lc = d.getgenlc("ACS", "30000", "30")

    print(lc[0])

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
