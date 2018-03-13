import re
import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Index, UniqueConstraint, asc
from sqlalchemy import Integer, Float, String, Text, DateTime, text
from sqlalchemy.sql import select, and_
from sqlalchemy.ext.declarative import declarative_base
from flasgger import Swagger
import flask
from flask_cas import CAS, login_required
import flask_restful
import conf  # all configurations are stored here, change individually for development and release configurations.

# Import the right configuration from conf.py, based on if it is the development environment or release environment
# Run 'python3 power_api.py release' for deployment to release, 'python3 power_api.py dev' or 'python3 power_api.py' will deploy to development environment

if __name__ == '__main__':
    env = sys.argv[1] if len(sys.argv) > 2 else 'dev'  # always fall back to dev environment
    config = conf.get_conf(env)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": config['SWAGGER_Title'],
        "description": config['SWAGGER_Description'],
        "contact": {
            "responsibleOrganization": "GT-RNOC",
            "responsibleDeveloper": "RNOC Lab Staff",
            "email": "rnoc-lab-staff@lists.gatech.edu",
            "url": "http://rnoc.gatech.edu/"
        },
        # "termsOfService": "http://me.com/terms",
        "version": "2.0"
    },
    "host": config['SWAGGER_Host'],  # Places API is hosted here
    "basePath": "/",  # base bash for blueprint registration
    "schemes": ["http", "https"],
}

# Flask stuff
app = flask.Flask(__name__)
cas = CAS(app)
swag = Swagger(app, template=swagger_template)
app.config['CAS_SERVER'] = config['CAS_Server']
app.config['CAS_VALIDATE_ROUTE'] = config['CAS_ValRoute']
app.config['SECRET_KEY'] = config['CAS_Secret']  # set a random key, otherwise the authentication will throw errors
app.config['SESSION_TYPE'] = 'filesystem'
app.config['CAS_AFTER_LOGIN'] = ''

# Flask_restful API, used for testing
api = flask_restful.Api(app)

# SQLAlchemy stuff
db = create_engine(config['SQLA_ConnString'] + config['SQLA_DbName'], echo=config['SQLA_Echo'])
Base = declarative_base()
metadata = MetaData(bind=db)

# SQLAlchemy models
power = Table('power', metadata,
              Column('timestamp', DateTime, primary_key=True, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")),
              Column('type', String(100), primary_key=True, nullable=False),
              Column('value_read', Float(asdecimal=True), nullable=False),
              Column('source_name', String(100), primary_key=True, nullable=False)
              )

sensors = Table('sensors', metadata,
                Column('sensor_id', String(50), primary_key=True),
                Column('type', String(50), nullable=False),
                Column('site', String(100), nullable=False),
                Column('protocol', String(20), nullable=False),
                Column('description', Text, nullable=False),
                Column('cluster_id', String(10), nullable=False)
                )

def units_mapper(meas_type):
    """
    Maps units to each kind of meter
    """
    # Add more units here as more unique 'type's in the database are added
    units = {"Active Energy Delivered": "kWh",
             "Active Power": "kW"}
    try:
        return (units[meas_type])
    except KeyError:
        return ""

def sensortype_mapper(source):
    """
    Maps the unique 3-letter code to different types of meters. Should be migrated to a database in a future version.
    """
    stype = re.search('B\d\d\d(.*)',source).group(1)[:-1] # removing the Bxxx part, and the trailing \r that seems to be in the database
    stype = ''.join(filter(str.isalpha, stype)) # keep only the characters, drop all numbers - this gives a unique 3 letter code (for now) for all different meters
    sensortypes = {
        "EMS": "Electrical mains transformer (4160V - 480V)",
        "EMH": "Electrical mains meter, high voltage (480V)",
        "EML": "Electrical mains meter, low voltage (208V)",
        "EUH": "Electrical sub-meter, high voltage (480V)",
        "EUL": "Electrical sub-meter, low voltage (208V)"
    }
    try:
        return (sensortypes[stype])
    except KeyError:
        return "unknown"


def res_to_json(row):
    """
    Encode the result of a power-related SQL query to JSON
    """
    output = {
        "source_name": row[3][:-1],    # remove the trailing \r that seems to be in the database
        "source_type": sensortype_mapper(row[3]),
        "timestamp": row[0],           # get data in UNIX format, with GMT times, client can use JavaScript to convert timezones.
        "value_read": str(row[2]),
        "units": units_mapper(row[1])
    }
    return(output)

class CheckUser(flask_restful.Resource):
    @app.route("/checkuser",methods=['GET'])
    @login_required
    def index():
        """
        Check if user is logged in, or ask user to log in
        Simply test to see if the user is authenticated, and return their login name
        ---
        tags:
            - user
        produces:
        - application/json
        responses:
            200:
                description: User is logged in
                schema:
                    type: object
                    properties:
                        username:
                             type: string
                             description: username of the user currently logged in
                             required: true
            403:
                description: Unable to authenticate
                schema:
                    type: object
                    properties:
                        error:
                            type: string
                            description: unable to authenticate
                            required: true
        """
        try:
            return flask.jsonify({"username": cas.username}), 200
        except:
            return flask.jsonify({"error": "Unable to authenticate"}), 403
api.add_resource(CheckUser, '/checkuser')

class Energy(flask_restful.Resource):
    @app.route("/facilities/energy/<b_id>", methods=['GET'])
    def getEnergyData(b_id):
        """
        Returns list of energy readings for a given building
        With specified start and stop dates, retrieve list of all energy sensor readings at that building, with meter name, meter type, timestamp and value units.
        ---
        tags:
            - electricity
        produces:
            - application/json
        parameters:
            - name: b_id
              in: path
              description: building ID you need data from
              required: true
              default: 26
              type: string
            - name: start
              in: query
              description: start timestamp of the readings
              required: true
              default: "2016-09-01 00:00:00"
              type: string
            - name: stop
              in: query
              description: end timestamp of the readings
              required: true
              default: "2016-09-03 23:59:59"
              type: string
        responses:
            200:
                description: An array of building information
                schema:
                    type: array
                    items:
                        type: object
                        properties:
                          b_id:
                            type: string
                            description: ID of the building
                            required: true
                          source_name:
                            type: string
                            description: Name of the sensor that recorded this value
                            required: true
                          source_type:
                            type: string
                            description: Detailed description of the sensor type
                          timestamp:
                            type: string
                            description: Timestamp of this recording
                          units:
                            type: string
                            description: Units of the reading
                          value_read:
                            type: string
                            description: Value that the sensor reported
            400:
                description: Building ID not valid, or date range not present in the database
        """
        start = flask.request.args.get('start')
        stop = flask.request.args.get('stop')
        if start is None or stop is None:
            return flask.jsonify({"error": "start and stop parameters required, you cannot query the whole database"}), 400
        query = select([power], and_(power.c.type == 'Active Energy Delivered', power.c.source_name.like('%B' + b_id.zfill(3) + '%'), power.c.timestamp >= start, power.c.timestamp <= stop)).order_by(asc(power.c.timestamp))
        results = db.execute(query)
        response = []
        for result in results:
            energy_data = res_to_json(result)
            energy_data["b_id"] = b_id
            response.append(energy_data)
        if len(response) == 0:
            return flask.jsonify({"error": "Building ID not found in the database"}), 404
        return flask.jsonify(response)
api.add_resource(Energy, "/facilities/energy/<b_id>")

class Power(flask_restful.Resource):
    @app.route("/facilities/power/<b_id>", methods=['GET'])
    def getPowerData(b_id):
        """
            Returns list of power readings for a given building
            With specified start and stop dates, retrieve list of all power sensor readings at that building, with meter name, meter type, timestamp and value units.
            ---
            tags:
                - electricity
            produces:
                - application/json
            parameters:
                - name: b_id
                  in: path
                  description: building ID you need data from
                  required: true
                  default: 26
                  type: string
                - name: start
                  in: query
                  description: start timestamp of the readings
                  required: true
                  default: "2016-09-01 00:00:00"
                  type: string
                - name: stop
                  in: query
                  description: end timestamp of the readings
                  required: true
                  default: "2016-09-03 23:59:59"
                  type: string
            responses:
                200:
                    description: An array of building information
                    schema:
                        type: array
                        items:
                            type: object
                            properties:
                              b_id:
                                type: string
                                description: ID of the building
                                required: true
                              source_name:
                                type: string
                                description: Name of the sensor that recorded this value
                                required: true
                              source_type:
                                type: string
                                description: Detailed description of the sensor type
                              timestamp:
                                type: string
                                description: Timestamp of this recording
                              units:
                                type: string
                                description: Units of the reading
                              value_read:
                                type: string
                                description: Value that the sensor reported
                400:
                    description: Start and stop parameters required
                404:
                    description: Building ID not found
            """
        start = flask.request.args.get('start')
        stop = flask.request.args.get('stop')
        if start is None or stop is None:
            return flask.jsonify({"error": "start and stop parameters required, you cannot query the whole database"}), 400
        query = select([power], and_(power.c.type == 'Active Power', power.c.source_name.like('%B' + b_id.zfill(3) + '%'), power.c.timestamp >= start, power.c.timestamp <= stop)).order_by(asc(power.c.timestamp))
        results = db.execute(query)
        response = []
        for result in results:
            power_data = res_to_json(result)
            power_data["b_id"] = b_id
            response.append(power_data)
        if len(response) == 0:
            return flask.jsonify({"error": "Building ID not found in the database"}), 404
        return flask.jsonify(response)
api.add_resource(Power, "/facilities/power/<b_id>")

class Sensor(flask_restful.Resource):
    @app.route("/facilities/sensor/<sensor_id>", methods=['GET'])
    def getSensorData(sensor_id):
        """
            Returns list of all sensor readings, given a particular sensor name
            With specified start and stop dates, retrieve list of readings of the specified sensor, with meter name, meter type, timestamp and value units.
            ---
            tags:
                - raw sensor
            produces:
                - application/json
            parameters:
                - name: sensor_id
                  in: path
                  description: sensor ID you need data from
                  required: true
                  default: "GTECH.B026E_MH1"
                  type: string
                - name: start
                  in: query
                  description: start timestamp of the readings
                  required: true
                  default: "2016-09-01 00:00:00"
                  type: string
                - name: stop
                  in: query
                  description: end timestamp of the readings
                  required: true
                  default: "2016-09-03 23:59:59"
                  type: string
            responses:
                200:
                    description: An array of building information
                    schema:
                        type: array
                        items:
                            type: object
                            properties:
                              source_name:
                                type: string
                                description: Name of the sensor that recorded this value
                                required: true
                              source_type:
                                type: string
                                description: Detailed description of the sensor type
                              timestamp:
                                type: string
                                description: Timestamp of this recording
                              units:
                                type: string
                                description: Units of the reading
                              value_read:
                                type: string
                                description: Value that the sensor reported
                400:
                    description: Start and stop parameters required
                404:
                    description: Sensor ID not found
            """
        start = flask.request.args.get('start')
        stop = flask.request.args.get('stop')
        if start is None or stop is None:
            return flask.jsonify({"error": "start and stop parameters required, you cannot query the whole database"}), 400
        query = select([power], and_(power.c.source_name == (sensor_id + '\r'), power.c.timestamp >= start, power.c.timestamp <= stop)).order_by(asc(power.c.timestamp))
        results = db.execute(query)
        response = []
        for result in results:
            response.append(res_to_json(result))
        if len(response) == 0:
            return flask.jsonify({"error": "Building ID not found in the database"}), 404
        return flask.jsonify(response)
api.add_resource(Sensor, "/facilities/sensor/<sensor_id>")

class SensorMeta(flask_restful.Resource):
    # @login_required
    @app.route("/facilities/sensor_metadata/<sensor_id>", methods=['GET'])
    def getSensorMetadata(sensor_id):
        """
            Returns list of all sensor readings, given a particular sensor name
            With specified start and stop dates, retrieve list of readings of the specified sensor, with meter name, meter type, timestamp and value units.
            ---
            tags:
                - metadata
            produces:
                - application/json
            parameters:
                - name: sensor_id
                  in: path
                  description: building ID you need data from
                  required: true
                  default: "B003E_MH1"
                  type: string
            responses:
                200:
                    description: An array of building information
                    schema:
                        type: array
                        items:
                            type: object
                            properties:
                              sensor_id:
                                type: string
                                description: ID of the sensor
                                required: true
                              sensor_type:
                                type: string
                                description: Type of sensor
                              site:
                                type: string
                                description: Location of the sensor
                              protocol:
                                type: string
                                description: Protocol that the sensor is using
                              description:
                                type: string
                                description: Any additional description of the sensor
                              cluster:
                                type: string
                                description: Cluster that the sensor belongs to, if any
                404:
                    description: Sensor ID not found
            """
        query = select([sensors], sensors.c.sensor_id == sensor_id)
        results = db.execute(query).fetchone()
        if results is None:
            return flask.jsonify({"error": "Sensor ID not found"}), 404
        output = {
            "sensor_id": results[0],
            "sensor_type": results[1],
            "site": results[2],
            "protocol": results[3],
            "description": results[4][:-2],
            "cluster_id": results[5]
        }
        return flask.jsonify(output)
api.add_resource(SensorMeta, "/facilities/sensor_metadata/<sensor_id>")

app.run(host=config['FLASK_Host'], port=config['FLASK_Port'], debug=config['FLASK_Debug'])


