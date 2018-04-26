"""
Places API route / endpoint implementations

Uses Flask Blueprints as explained here:
http://flask.pocoo.org/docs/0.12/blueprints/#blueprints
"""
from http import HTTPStatus

import flask
from flask import request, Blueprint
from flask_cas import login_required

from api.errors import NotFoundException, BadRequestException
from api.extensions import cas, db
from api.models import Power, Users, Sensors
from api.schema import power_energy_schema, sensor_schema, sensor_metadata_schema
from api.helpers import res_to_json, sensortype_mapper, units_mapper

api = Blueprint('gtpower', __name__)

# @api.route("/checkuser",methods=['GET'])
# @login_required
# def index():
#     """
#     Check if user is logged in, or ask user to log in
#     Simply test to see if the user is authenticated, and return their login name
#     ---
#     tags:
#         - user
#     produces:
# 	- application/json
#     responses:
#         200:
# 	    description: User is logged in
#             schema:
#                 type: object
#                 properties:
#                     username:
#                          type: string
#                          description: username of the user currently logged in
#                          required: true
#         403:
#             description: Unable to authenticate
#             schema:
#                 type: object
#                 properties:
#                     error:
#                         type: string
#                         description: unable to authenticate
#                         required: true
#     """
#     try:
#         return flask.jsonify({"username":cas.username}), 200
#     except:
#         return flask.jsonify({"error":"Unable to authenticate"}), 403


@api.route("/facilities/energy/<b_id>/", methods=['GET'])
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
    start = request.form['start']
    stop = request.form['stop']
    if not start or not stop:
        raise BadRequestException(message="start and stop parameters required, you cannot query the whole database")
    power = Power.query.filter(Power.source_name.like('%B' + b_id.zfill(3) + '%'), Power.timestamp >= start, Power.timestamp <= stop).filter_by(type='Active Energy Delivered').order_by(Power.timestamp.desc())
    if power:
        power_energy_schema.jsonify(power)
    else:
        raise NotFoundException()

@api.route("/facilities/power/<b_id>/", methods=['GET'])
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
    start = request.form['start']
    stop = request.form['stop']
    if not start or not stop:
        raise BadRequestException(message="start and stop parameters required, you cannot query the whole database")
    power = Power.query.filter(Power.source_name.like('%B' + b_id.zfill(3) + '%'), Power.timestamp >= start, Power.timestamp <= stop).filter_by(type='Active Power').order_by(Power.timestamp.desc())
    if power:
        power_energy_schema.jsonify(power)
    else:
        raise NotFoundException()

@api.route("/facilities/sensor/<sensor_id>/", methods=['GET'])
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
    start = request.form['start']
    stop = request.form['stop']
    if not start or not stop:
        raise BadRequestException(message="start and stop parameters required, you cannot query the whole database")
    sensor = Power.query.filter(Power.timestamp >= start, Power.timestamp <= stop).filter_by(source_name=(sensor_id + '\r')).order_by(Power.timestamp.asc())
    if sensor:
        sensor_schema.jsonify(sensor)
    else:
        raise NotFoundException()

    # @login_required
    @api.route("/facilities/sensor_metadata/<sensor_id>/", methods=['GET'])
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
        metadata = Sensors.query.filter_by(sensor_id=sensor_id).first()
        if not metadata:
            raise NotFoundException()
        return sensor_metadata_schema.jsonify(metadata)
