# Import the dependencies.


import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta


app = Flask(__name__)
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement= Base.classes.measurement
station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)






#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/temp/start<br/>"
        "/api/v1.0/temp/start/end"
    )

# Precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date 1 year ago from the last data point
    last_date = session.query(func.max(measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Stations route
@app.route('/api/v1.0/stations')
def stations():
    # Query list of stations
    results = session.query(station.station).all()

    # Convert the query results to a list
    station_list = list(np.ravel(results))

    return jsonify({'Stations': station_list})

#Temperature Observations route
@app.route("/api/v1.0/tobs")

def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.tobs).\
      filter(measurement.station == 'USC00519281').\
      filter(measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify({'temps': temps})


# Temperature Statistics route
@app.route("/api/v1.0/temp/<start>")
 # go back one year from start date and go to end of data for Min/Avg/Max temp   
def temperature_stats_start(start):
    # Convert the input start date string to a datetime object
    #breakpoint()
    
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')


    # Query temperature statistics for all dates greater than or equal to the start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    # Convert the query results to a dictionary
    temperature_stats_data = {
        'Min Temperature': results[0][0],
        'Average Temperature': results[0][1],
        'Max Temperature': results[0][2]
    }

    return jsonify(temperature_stats_data)

@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        # When no end date is provided, calculate stats from the start date to the latest date
        results = session.query(*sel).filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify({'temps': temps})
    
    # When both start and end dates are provided, calculate stats for the specified date range
    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temps = list(np.ravel(results))
    
    # Convert the query results to a dictionary
    temperature_stats_data = {
        'Min Temperature': results[0][0],
        'Average Temperature': results[0][1],
        'Max Temperature': results[0][2]
    }

    return jsonify(temperature_stats_data) 

if __name__ == "__main__":
    app.run(debug=True)
    