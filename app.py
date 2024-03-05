# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save references to each table
Station = Base.classes.station
measurement= Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app= Flask (__name__)

@app.route('/')
def Whome():
    return (
        f"Welcome!<br/>"
        f"Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )



# Routes
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all daily precipitation totals for the last year"""
    # Query and summarize daily precipitation across all stations for the last year of available data
    
    start_date = '2016-08-23'
    sel = [measurement.date, 
        func.sum(measurement.prcp)]
    precipitation = session.query(*sel).\
            filter(measurement.date >= start_date).\
            group_by(measurement.date).\
            order_by(measurement.date).all()
   
    session.close()

    # Return a dictionary with the date as key and the daily precipitation total as value
    precipitation_dates = []
    precipitation_totals = []

    for date, dailytotal in precipitation:
        precipitation_dates.append(date)
        precipitation_totals.append(dailytotal)
    
    precipitation_dict = dict(zip(precipitation_dates, precipitation_totals))

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    station_data = session.query(Station.station, Station.name).all()

    # Convert the results to a list of dictionaries
    stations_list = [{'station': station, 'name': name} for station, name in station_data]

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for the most active station
    start_date = '2016-08-23'
    sel = [measurement.date, 
        measurement.tobs]
    station_temps = session.query(*sel).\
            filter(measurement.date >= start_date, measurement.station == 'USC00519281').\
            group_by(measurement.date).\
            order_by(measurement.date).all()

    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route('/api/v1.0/<start>')
def temperature_start_date(start):
    # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    temperature_stats = session.query(
        func.min(measurement.tobs).label('min_temperature'),
        func.avg(measurement.tobs).label('avg_temperature'),
        func.max(measurement.tobs).label('max_temperature')
    ).filter(measurement.date >= start).all()

    temperature_stats_dict = {
        'start_date': start,
        'min_temperature': temperature_stats[0].min_temperature,
        'avg_temperature': temperature_stats[0].avg_temperature,
        'max_temperature': temperature_stats[0].max_temperature
    }

    return jsonify(temperature_stats_dict)

@app.route('/api/v1.0/<start>/<end>')
def temperature_start_end_date(start, end):
    # Calculate TMIN, TAVG, and TMAX for the specified date range
    temperature_stats = session.query(
        func.min(measurement.tobs).label('min_temperature'),
        func.avg(measurement.tobs).label('avg_temperature'),
        func.max(measurement.tobs).label('max_temperature')
    ).filter(measurement.date >= start).filter(measurement.date <= end).all()

    # Convert the results to a dictionary
    temperature_stats_dict = {
        'start_date': start,
        'end_date': end,
        'min_temperature': temperature_stats[0].min_temperature,
        'avg_temperature': temperature_stats[0].avg_temperature,
        'max_temperature': temperature_stats[0].max_temperature
    }

    return jsonify(temperature_stats_dict)

if __name__ == '__main__':
    app.run(debug=True)