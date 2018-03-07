# File: conf.py 
# Author: Jayanth M (jayanth6@gatech.edu)
# Created: 3/6/2018 6:12 PM 
# Project: gtpower
# Description:

import os

class DevConf(object):
    SWAGGER_Title = "Power API - Development Version"
    SWAGGER_Description = "**DEVELOPMENT VERSION ** This API will allow you to access the energy readings and power consumption of various guildings on campus, provided by GT Facilities. This API currently has data only from 2016."
    SWAGGER_Host = "dockertest.rnoc.gatech.edu:5001"
    CAS_Server = "https://login.gatech.edu/cas"
    CAS_ValRoute = "/serviceValidate"
    CAS_Secret = "6d4e24b1bbaec5f6f7ac35878920b8ebdfdf71bc53521f31bc4ec47885de610d"  # session secret, does not matter - just a random key.
    SQLA_ConnString = os.environ["DB_CONN"]
    SQLA_DbName = "CORE_gtfacilities"
    SQLA_Echo = True
    FLASK_Host = "0.0.0.0"
    FLASK_Port = 5000
    FLASK_Debug = True
    TEST_SrcDb = "CORE_gtfacilities"
    TEST_Tables = ['buildings', 'power', 'sensors']
    TEST_Url = "http://dockertest.rnoc.gatech.edu:5001"

class ProdConf(object):
    SWAGGER_Title = "Power API"
    SWAGGER_Description = "This API will allow you to access the energy readings and power consumption of various guildings on campus, provided by GT Facilities. This API currently has data only from 2016."
    SWAGGER_Host = "dockertest.rnoc.gatech.edu:5001"
    CAS_Server = "https://login.gatech.edu/cas"
    CAS_ValRoute = "/serviceValidate"
    CAS_Secret = "6d4e24b1bbaec5f6f7ac35878920b8ebdfdf71bc53521f31bc4ec47885de610d"  # session secret, does not matter - just a random key.
    SQLA_ConnString = os.environ["DB_CONN"]
    SQLA_DbName = "CORE_gtfacilities"
    SQLA_Echo = False
    FLASK_Host = "0.0.0.0"
    FLASK_Port = 5000
    FLASK_Debug = False

def get_conf(env="dev"):
    if env == "dev":
        return vars(DevConf)
    elif env == "prod":
        return vars(ProdConf)
    else:
        raise ValueError('Invalid environment name')
