# Import the dependencies.
import numpy as np

from pathlib import Path
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
db_path = Path("Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{db_path}")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    """List all available api routes."""
    return (
        f"Available Routes:<br/><br/>"
        f"* /api/v1.0/precipitation<br/>"
        f"* /api/v1.0/stations<br/>"
        f"* /api/v1.0/tobs<br/>"
        f"* /api/v1.0/start<br/>"
        f"* /api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Query measurement to get date and prcp
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of precipitaion dict
    precipitaion = []
    for date, prcp in results:
        precipitaion_dict = {}
        precipitaion_dict["date"] = date
        precipitaion_dict["prcp"] = prcp
        precipitaion.append(precipitaion_dict)
    
    return jsonify(precipitaion)

@app.route("/api/v1.0/stations")
def stations():

    # Query station to get stations
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Create a dictionary from the row data and append to a list of station dict
    stations = []
    for station, name, lat, lng, elev in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = lat
        station_dict["longitude"] = lng
        station_dict["elevation"] = elev
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperatures():
    
    # calculate date a year ago from most recent date in database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    most_recent_date_str = most_recent_date[0]
    recent_date = dt.date(2017, 8, 23)
    one_year_ago = recent_date - dt.timedelta(days=365)
    
    # Determine the most active station
    most_active_station = most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active_station_id = most_active_station[0]

    # Query the data for the most active station for the previous year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_ago).all()

    # Extract the results
    temperatures = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temperatures.append(temp_dict)

    return jsonify(temperatures)

@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):

    # Query the data for the min, max and avg temperature from the given start date
    results = session.query(func.min(Measurement.tobs).label('TMIN'), func.max(Measurement.tobs).label('TMAX'), func.avg(Measurement.tobs).label('TAVG')).filter(Measurement.date >= start).all()
    
   # Extract the results
    tmin = results[0].TMIN
    tavg = results[0].TAVG
    tmax = results[0].TMAX
    
    # Return the results as JSON
    return jsonify({
        'TMIN': tmin,
        'TAVG': tavg,
        'TMAX': tmax
    })

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):

    # Query the data for the min, max and avg temperature from the given start date and end date
    results = session.query(func.min(Measurement.tobs).label('TMIN'), func.max(Measurement.tobs).label('TMAX'), func.avg(Measurement.tobs).label('TAVG')).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
   # Extract the results
    tmin = results[0].TMIN
    tavg = results[0].TAVG
    tmax = results[0].TMAX
    
    # Return the results as JSON
    return jsonify({
        'TMIN': tmin,
        'TAVG': tavg,
        'TMAX': tmax
    })

# close a session
session.close()

if __name__ == '__main__':
    app.run(debug=True)