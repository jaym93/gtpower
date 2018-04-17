"""
Database models

See SQL Alchemy documentation:
http://flask-sqlalchemy.pocoo.org/2.3/
http://docs.sqlalchemy.org/en/latest/
"""
from sqlalchemy import String, Text, Float, Integer, DateTime, text

from api.extensions import db


class Power(db.Model):
    """
    DB model representing a building
    """
    __tablename__ = 'power'

    timestamp = db.Column(DateTime, primary_key=True, nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    type = db.Column(String(100), primary_key=True, nullable=False)
    value_read = db.Column(Float(asdecimal=True), nullable=False)
    source_name = db.Column(String(100), primary_key=True, nullable=False)


class Users(db.Model):
    """
    DB model representing a category associated with a building
    """
    __tablename__ = 'users'

    username = db.Column(String(30), primary_key=True)
    role = db.Column(String(30), nullable=False)


class Sensors(db.Model):
    """
    DB model representing a tag associated with a building
    """
    __tablename__ = 'sensors'

    sensor_id = db.Column(String(50), primary_key=True)
    type = db.Column(String(50), nullable=False)
    site = db.Column(String(100), nullable=False)
    protocol = db.Column(String(20), nullable=False)
    description = db.Column(Text, nullable=False)
    cluster_id = db.Column(String(10), nullable=False)
