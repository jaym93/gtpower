import json
import re
import pymysql
import flask
from flasgger import Swagger
import logging
from flask import request
from flask_cas import CAS, login_required
import os

app = flask.Flask(__name__)
cas = CAS(app)
swag = Swagger(app)
app.config['CAS_SERVER'] = 'https://login.gatech.edu/cas'
app.config['CAS_VALIDATE_ROUTE'] = '/serviceValidate'
app.config['SECRET_KEY'] = '6d4e24b1bbaec5f6f7ac35878920b8ebdfdf71bc53521f31bc4ec47885de610d' #set a random key, otherwise the authentication will throw errors
app.config['SESSION_TYPE'] = 'filesystem'
app.config['CAS_AFTER_LOGIN'] =''
app.config['SWAGGER'] = {
    'title': 'Places API',
    'description': 'This API will allow you to access the information of the places at Georgia Tech. It can be used to find out information about the offices and the buildings such as their names, addresses, phone numbers, images, categories and GPS coordinates.',
    'version': '2.0.0',
    'schemes':['http','https']
}
conn = pymysql.connect(host='db0.rnoc.gatech.edu', port=3306, user=os.environ['DB_USERNAME'], passwd=os.environ['DB_PASSWORD'], db='CORE_gtfacilities')
cur = conn.cursor()

def get_building(b_id):
    query = "select name from `CORE_gtplaces.buildings` where b_id ='"+b_id+"'"
    execute_query(query)
    name = cur.fetchone()
    return name

def execute_query(query):
    try:
        cur.execute(query)
    except pymysql.MySQLError as e:
        return flask.jsonify({"status":500,"message":"Something went wrong, this has been logged. You may report errors to rnoc-lab-staff@lists.gatech.edu."})

def units_mapper(meas_type):
    # Add more units here as more unique 'type's in the database are added
    units = {"Active Energy Delivered": "kWh",
             "Active Power": "kW"}
    try:
        return (units[meas_type])
    except KeyError:
        return ""
    
def sensortype_mapper(source):
    stype = re.search('B\d\d\d(.*)',source).group(1)[:-1] # removing the Bxxx part, and the trailing \r that seems to be in the database
    stype = ''.join(filter(str.isalpha, stype)) # keep only the characters, drop all numbers - this gives a unique 3 letter code (for now) for all different meters
    sensortypes = {
        "EMH":"Electrical mains meter, high voltage (480V)",
        "EML":"Electrical mains meter, low voltage (208V)",
        "EUH":"Electrical sub-meter, high voltage (480V)",
        "EUL":"Electrical sub-meter, low voltage (208V)"
        }
    try:
        return (sensortypes[stype])
    except KeyError:
        return "unknown"


def res_to_json(row):
        output = {
            "source_name": row[3][:-1],    # remove the trailing \r that seems to be in the database
            "source_type": sensortype_mapper(row[3]),
            "timestamp": row[0],           # get data in UNIX format, with GMT times, client can use JavaScript to convert timezones.
            "value_read": row[2],
            "units": units_mapper(row[1])
            }
        return(output)

@app.route("/",methods=['GET'])
@login_required
def index():
    username = cas.username
    return "Logged in as: " + username

@app.route("/facilities/energy/<b_id>", methods=['GET'])
def getEnergyData(b_id):
    start = request.args.get('start')
    stop = request.args.get('stop')
    query = "SELECT * FROM `power` WHERE type='Active Energy Delivered' and source_name like '%B"+b_id.zfill(3)+"%' and timestamp BETWEEN '"+start+"' AND '"+stop+"' order by timestamp asc" #zfill is required to map building numbers to 3 digits, ex: 26 -> 026
    cur.execute(query)
    results = cur.fetchall()
    response = []
    for result in results:
        response.append(res_to_json(result).append({'b_id':b_id, 'name':get_building(b_id)}))
    return flask.jsonify(response)

@app.route("/facilities/power/<b_id>", methods=['GET'])
def getPowerData(b_id):
    start = request.args.get('start')
    stop = request.args.get('stop')
    query = "SELECT * FROM `power` WHERE type='Active Power' and source_name like '%B"+b_id.zfill(3)+"%' and timestamp BETWEEN '"+start+"' AND '"+stop+"' order by timestamp asc"
    cur.execute(query)
    results = cur.fetchall()
    response = []
    for result in results:
        response.append(res_to_json(result).append({'b_id':b_id, 'name':get_building(b_id)})) # attaching building ID where the sensor is located
    return flask.jsonify(response)

@app.route("/facilities/sensor/<sensor_id>", methods=['GET'])
def getSensorData(sensor_id):
    start = request.args.get('start')
    stop = request.args.get('stop')
    query = "SELECT * FROM `power` WHERE source_name = '"+sensor_id+"\r' and timestamp BETWEEN '"+start+"' AND '"+stop+"' order by timestamp asc"
    cur.execute(query)
    results = cur.fetchall()
    response = []
    for result in results:
        response.append(res_to_json(result))
    return flask.jsonify(response)

@login_required
@app.route("/facilities/sensor_metadata/<sensor_id>", methods=['GET'])
def getSensorMetadata(sensor_id):
    query = "SELECT * FROM `sensors` WHERE sensor_id = '"+sensor_id+"'"
    cur.execute(query)
    results = cur.fetchall()
    response = []
    for result in results:
        output = {
        "sensor_id": result[0],    # remove the trailing \r that seems to be in the database
        "sensor_type": result[1],
        "site": result[2],           # get data in UNIX format, with GMT times, client can use JavaScript to convert timezones.
        "protocol": result[3],
        "description": result[4],
        "cluster_id": result[5],
        }
        response.append(output)
    return flask.jsonify(response)


app.run(debug=True, host="0.0.0.0", port=5000)    

