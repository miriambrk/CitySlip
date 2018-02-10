from flask import Flask, render_template, jsonify, redirect, request
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import requests as req
import json
from census_funcs import get_community_data, cityslip_history, barfinder
from RE_functions import get_real_estate_data, compute_score

app = Flask(__name__)


engine = create_engine("sqlite:///city_input.sqlite")
Base = automap_base()
# reflect an existing database into a new model
Base.prepare(engine, reflect=True)
# Base.classes.keys()

# Create session (link) from Python to the DB
session = Session(engine)
Home_sales = Base.classes.home_sales
Rentals = Base.classes.rentals
zip_latlon = Base.classes.zip_to_lat
Market_Health = Base.classes.market_health
census = Base.classes.census_pop

# display dashboard homepage
@app.route("/")
def index():
    return render_template("index.html")


#return all real estate data and market health index
@app.route("/REdata/<zip>")
def REdata(zip):

    REdata, re_dict = get_real_estate_data(zip, Home_sales, Rentals, session)

    return(jsonify(REdata, re_dict))


# EXAMPLE URL:  /POIdata?lat=38.83&lng=-76.52
#return all POIs for a specific lat/long
@app.route("/POIdata", methods=['get'])
def poi():
    lat = request.args.get("lat", None)
    lng = request.args.get("lng", None)
    return poidata(lat,lng)
def poidata(lat, lng):
    print(lat)
    print(lng)
    poi_json = barfinder(lat,lng)
    return(jsonify(poi_json))



# returns the zipcode with associated lattitude and longitude
@app.route("/zip_latlng/<zip>")
def zip_loc(zip):
    sel = [zip_latlon.zip_code, zip_latlon.lat, zip_latlon.lon]
    results = session.query(*sel).\
        filter(zip_latlon.zip_code ==zip)
    zip_data = {}
    for result in results:
        zip_data['ZIP_CODE'] = result[0]
        zip_data['LAT'] = result[1]
        zip_data['LON'] = result[2]
    return jsonify(zip_data)


# pull census population data
# EXAMPLE URL:  /census?lat=38.83&lng=-76.52
@app.route("/census",methods=['get'])
def cen():
    lat = request.args.get("lat", None)
    lng = request.args.get("lng", None)
    return census_data(lat,lng)
def census_data(lat, lng, census, session):

    cen_block_url = ('http://data.fcc.gov/api/block/find?format=json&latitude=%s&longitude=%s&showall=true' % (lat, lng))
    lat_lon_county = req.get(cen_block_url).json()
    county_name = lat_lon_county['County']['name']+ ' County'
    state_name = lat_lon_county['State']['name']
    print(state_name)
    sel = [census.state, census.county, census.pop_2010,census.pop_2011,census.pop_2012,
    census.pop_2013, census.pop_2014, census.pop_2015,census.pop_2016]
    county_census_pop = session.query(*sel).\
        filter(census.county == county_name)

    # Match County and State name to retrieve population information from 2010 through 2016
    pop_data = {}
    for row in county_census_pop:
        pop_data['STATE'] = row[0]
        pop_data['COUNTY'] = row[1]
        pop_data['POPULATION_2010'] = row[2]
        pop_data['POPULATION_2011'] = row[3]
        pop_data['POPULATION_2012'] = row[4]
        pop_data['POPULATION_2013'] = row[5]
        pop_data['POPULATION_2014'] = row[6]
        pop_data['POPULATION_2015'] = row[7]
        pop_data['POPULATION_2016'] = row[8]
    return(jsonify(pop_data))

#Query onboard's community API for age demographics / avg Jan and Jun temps / crime rate / sales tax / schools
#EXAMPLE URL:  /community/20764
@app.route("/community/<zip>")
def community(zip):
    return(jsonify(get_community_data(zip, census, zip_latlon, Market_Health, Home_sales, Rentals, session)))


#get all the data for the zip and compute the score
@app.route("/alldata/<zip>")
def get_alldata(zip):

    print("ALLDATA: " + str(zip))

    #get all the community and real estate data used to compute the score
    community_dict, poi_data, census_dict, REdata, re_dict = get_community_data(zip, census, zip_latlon, Market_Health, Home_sales, Rentals, session)

    #compute the score and store in dictionary
    community_dict["score"] = compute_score(community_dict, poi_data, census_dict, REdata, re_dict)

    return(jsonify(community_dict, poi_data, census_dict, REdata, re_dict))

#get the historical data from the cityslip database
@app.route("/history")
def get_history():
    return (jsonify(cityslip_history()))


if __name__ == "__main__":
    app.run(debug=True)
