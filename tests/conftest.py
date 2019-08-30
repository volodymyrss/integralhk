import pytest

import integralhk.app as app_module

@pytest.fixture
def app():
    app = app_module.app
    return app
