"""
pytest integration tests for power API
"""
from http import HTTPStatus

import pytest

from flask import url_for, json

from api.models import Power, Users, Sensors

class TestPowerApi:
    # TODO: Write test cases
    def test_get_energy_data(self, db, load_test_db, test_client):
        response = test_client.get('/energy/026')
