# Import dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)

# Flask Setup
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from the most active station<br/>"
        f"<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
    most_recent_date = session.query(func.max(Measurement.date)).first()
    most_recent_date = list(most_recent_date)
    start_date = dt.datetime.strptime(most_recent_date[0], "%Y-%m-%d")- dt.timedelta(days = 366)
    result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > start_date).\
        order_by(Measurement.date).all()

    return jsonify(dict(result))

@app.route("/api/v1.0/stations")
def stations():
    session.query(Station.name).distinct().count()
    station_count = func.count(Measurement.station)
    active_stations = session.query(Measurement.station, station_count).group_by(Measurement.station).order_by(station_count.desc()).all()

    return jsonify(dict(active_stations))

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    latest_date = session.query(func.max(Measurement.date)).first()
    latest_date = list(latest_date)
    last_year = dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days = 366)
    temperature = session.query(Measurement.tobs).filter(Measurement.date >= last_year, Measurement.station == 'USC00519281').order_by(Measurement.tobs).all()
    
    temperature_totals = []
    for y_t in temperature:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        temperature_totals.append(yrtemp)
    
    return jsonify(temperature_totals)

if __name__ == "__main__":
    app.run(debug=True)