"""
Schema for JSON exposed by the API.

See Marshmallow documentation:
https://flask-marshmallow.readthedocs.io/en/latest/
http://marshmallow.readthedocs.io/en/latest/
"""
from api.extensions import ma


class PowerOrAndEnergySchema(ma.Schema):
    """
    JSON schema for the 'power' table in CORE_gtfacilities
    """
    class Meta:
        # JSON fields - type will be inferred
        fields = ('b_id', 'source_name', 'source_type', 'timestamp', 'units', 'value_read')


class SensorReadingSchema(ma.Schema):
    """
    JSON schema for a building category
    """
    class Meta:
        # JSON fields - type will be inferred
        fields = ('source_name', 'source_type', 'timestamp', 'units', 'value_read')


class SensorMetadataSchema(ma.Schema):
    """
    JSON schema for a building
    """
    class Meta:
        # JSON fields - type will be inferred
        fields = ('cluster_id', 'description', 'protocol', 'sensor_id', 'sensor_type', 'site')


power_energy_schema = PowerOrAndEnergySchema(many=True)
sensor_schema = SensorReadingSchema(many=True)
sensor_metadata_schema = SensorMetadataSchema()
