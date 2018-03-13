# File: power_test.py
# Author: Jayanth M (jayanth6@gatech.edu)
# Created: 3/6/2018 6:12 PM
# Project: gtpower
# Description:

import unittest
import requests
import conf

# ALWAYS USE DEV CONFIGURATION FOR TESTING
config = conf.get_conf("dev")

# RUN THE TESTS
class TestPlacesApiUsingRequests(unittest.TestCase):
    def test_CheckUser(self):
        response = requests.get(config['TEST_Url']+'/checkuser')
        self.assertEqual(response.status_code, 200)
        response = requests.get(config['TEST_Url']+'/checkuser')  # check for unauthorized here
        self.assertEqual(response.status_code, 403)

    def test_Energy(self):
        response = requests.get(config['TEST_Url']+'/facilities/energy/026?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 200)
        response = requests.get(config['TEST_Url']+'/facilities/energy/026')
        self.assertEqual(response.status_code, 400)
        response = requests.get(config['TEST_Url']+'/facilities/energy/358?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 404)

    def test_Power(self):
        response = requests.get(config['TEST_Url']+'/facilities/power/026?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 200)
        response = requests.get(config['TEST_Url']+'/facilities/power/026')
        self.assertEqual(response.status_code, 400)
        response = requests.get(config['TEST_Url']+'/facilities/power/358?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 404)

    def test_Sensor(self):
        response = requests.get(config['TEST_Url']+'/facilities/sensor/GTECH.B026E_MH1?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 200)
        response = requests.get(config['TEST_Url']+'/facilities/sensor/GTECH.B026E_MH1')
        self.assertEqual(response.status_code, 400)
        response = requests.get(config['TEST_Url']+'/facilities/sensor/B026E_MH1?start=2016-09-01 00:00:00&stop=2016-09-03 23:59:59')
        self.assertEqual(response.status_code, 404)

    def test_SensorMeta(self):
        response = requests.get(config['TEST_Url']+'/facilities/sensor_metadata/B003E_MH1')
        self.assertEqual(response.status_code, 200)
        response = requests.get(config['TEST_Url']+'/facilities/sensor_metadata/B003E_LH1')
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
