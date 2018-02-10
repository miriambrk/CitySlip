# Dependencies
import requests as req
import json
import zipcodes
import pandas as pd
import numpy as np
import http.client
from datetime import datetime
import time as time
import os
from RE_functions import get_real_estate_data

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Float, Text


###------------------------------------------###
### START GET MARKET HEALTH
def get_market_health_and_extremes(zip, Market_Health, Home_sales, Rentals, session):
    market_dict = {}
    results = session.query( Market_Health.market_health_index).filter(Market_Health.zip_code == zip).all()
    if len(results) > 0:
        for mhi in results:
            market_health_index = mhi.market_health_index
        market_dict['market_health_index'] = market_health_index
    else:
        #no market health data for input zip code; store 0 as a N/A value
        market_dict["market_health_index"] = 0
    print("Market Health: %s" % market_dict['market_health_index'])

    results = session.query(Home_sales.s2017_12).all()
    all_homes = pd.DataFrame(results, columns=['2017_12'])

    results = session.query(Rentals.r2017_12).all()
    all_rentals = pd.DataFrame(results, columns=['2017_12'])

    #get median home values and rental prices
    median_home_value = all_homes['2017_12'].median()
    median_rental_price = all_rentals['2017_12'].median()

    market_dict["median_home_value"] = median_home_value
    market_dict["median_rental_price"] = median_rental_price
    return market_dict
### END GET GET MARKET HEALTH
###------------------------------------------###

###------------------------------------------###
### START GET CENSUS DATA
# takes in a zip which is converted to lat/long for census block query to return a County
# census popuations are pulled by country from 2010 through 2016
# each year holds a result along with a column for the proceeding year's difference
def census_data(zip,zip_latlon, census, session):

    sel = [zip_latlon.zip_code, zip_latlon.lat, zip_latlon.lon]
    results = session.query(*sel).\
        filter(zip_latlon.zip_code ==zip)
    zip_data = {}
    for result in results:
        zip_data['ZIP_CODE'] = result[0]
        zip_data['LAT'] = result[1]
        zip_data['LON'] = result[2]
    lat = zip_data['LAT']
    lng = zip_data['LON']

    cen_block_url = ('http://data.fcc.gov/api/block/find?format=json&latitude=%s&longitude=%s&showall=true' % (lat, lng))
    lat_lon_county = req.get(cen_block_url).json()
    state_name = lat_lon_county['State']['name']
    if state_name != 'District of Columbia':
        county_name = lat_lon_county['County']['name']+ ' County'
    else:
        county_name = lat_lon_county['County']['name']


    print(state_name)
    sel = [census.state, census.county, census.pop_2010,census.pop_2011,census.pop_2012,
    census.pop_2013, census.pop_2014, census.pop_2015,census.pop_2016]
    county_census_pop = session.query(*sel).\
        filter(census.county == county_name)

    # Match County and State name to retrieve population information from 2010 through 2016
    pop_data = {}
    def diff (col1, col2):
        d = col2 - col1
        e = round(((d/col1) * 100), 2)
        return e
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
    pop_data['diff_2010_2011'] = diff(pop_data['POPULATION_2010'], pop_data['POPULATION_2011'])
    pop_data['diff_2011_2012'] = diff(pop_data['POPULATION_2011'], pop_data['POPULATION_2012'])
    pop_data['diff_2012_2013'] = diff(pop_data['POPULATION_2012'], pop_data['POPULATION_2013'])
    pop_data['diff_2013_2014'] = diff(pop_data['POPULATION_2013'], pop_data['POPULATION_2014'])
    pop_data['diff_2014_2015'] = diff(pop_data['POPULATION_2014'], pop_data['POPULATION_2015'])
    pop_data['diff_2015_2016'] = diff(pop_data['POPULATION_2015'], pop_data['POPULATION_2016'])
    pop_data['diff_2010_2016'] = diff(pop_data['POPULATION_2010'], pop_data['POPULATION_2016'])
    return pop_data

### END GET CENSUS DATA
###------------------------------------------###

###------------------------------------------###
### START GET WALKABILITY DATA
def get_walk(zip, zip_latlon,session):
    sel = [zip_latlon.zip_code, zip_latlon.lat, zip_latlon.lon]
    results = session.query(*sel).\
        filter(zip_latlon.zip_code ==zip)
    zip_data = {}
    for result in results:
        zip_data['ZIP_CODE'] = result[0]
        zip_data['LAT'] = result[1]
        zip_data['LON'] = result[2]

    lat = zip_data['LAT']
    lng = zip_data['LON']

    ##### When need to execute this, put back the api key #####
    walk_api_key = ""

    walk_url = "http://api.walkscore.com/score?format=json&"
    # Build query URL
    query_url = walk_url  + "&lat=" + str(lat) + "&lon=" + str(lng) + "&transit=1&bike=1" + "&wsapikey=" + walk_api_key
    walk_response = req.get(query_url).json()

    # Get the neighborhood data from the response
    walk_score = walk_response['walkscore']
    walk_description =walk_response['description']
    try:
        bike_score = walk_response['bike']['score']
        bike_description = walk_response['bike']['description']
    except:
        bike_score = 0
        bike_description = ""
    walk_dict = {
        "walk_score": walk_score,
        "walk_description": walk_description,
        "bike_score": bike_score,
        "bike_description": bike_description
    }
    return walk_dict


### END GET WALK DATA
###------------------------------------------###

###------------------------------------------###
### START GET SCHOOLS FUNCTION
### CALLS ONBOARD API FOR RADIUS OF 5 MILES TO GATHER SCHOOLS IN THE AREA

def get_schools(zip, zip_latlon, session):

    sel = [zip_latlon.zip_code, zip_latlon.lat, zip_latlon.lon]
    results = session.query(*sel).\
        filter(zip_latlon.zip_code ==zip)
    zip_data = {}
    for result in results:
        zip_data['ZIP_CODE'] = result[0]
        zip_data['LAT'] = result[1]
        zip_data['LON'] = result[2]
    lat = zip_data['LAT']
    lng = zip_data['LON']

    private = 0
    public = 0
    cath = 0
    other = 0

    page_size = 50
    #Onboard API Key

    #when need to execute, add the API key
    onboard_api_key = ""


    conn = http.client.HTTPSConnection("search.onboard-apis.com")
    school_url = "/propertyapi/v1.0.0/school/snapshot?"
    headers = {
        'accept': "application/json",
        'apikey': onboard_api_key,
        }
        #RADIUS SET TO DEFAULT OF 5 MILES
    point = "latitude=" + str(lat) + "&longitude=" + str(lng) + "&radius=5"
    query_url = school_url + point + "&pageSize=" + str(page_size)

    #request the first page of school data
    conn.request("GET", query_url, headers=headers)
    res = conn.getresponse()
    resp = json.loads(res.read())
    #counts for types of schools
    private = 0
    public = 0
    cath = 0
    other = 0

    #loop through and count up private and public schools
    total_schools = resp['status']['total']
    more_schools = True
    schools_to_get = total_schools
    page = 1
    #print("total schools: % s" % total_schools)
    while more_schools:
        #determine how many results to process
        if schools_to_get - page_size >= 0:
            max_s = page_size
            schools_to_get = schools_to_get - page_size
        else:
            max_s = schools_to_get
        for i in range(0, max_s):
            #track number of types of schools
            sch_type = resp['school'][i]['School']['Filetypetext']
            if sch_type == "PRIVATE":
                private = private + 1
            elif sch_type == "PUBLIC":
                public = public + 1
            elif sch_type == "CATHOLIC":
                cath = cath + 1
            else:
                other = other + 1
        if total_schools - (private+public+cath+other) > 0:
            #get the next page of data
            page = page + 1
            query_url = school_url + point + "&pageSize=" + str(page_size) + "&page="+ str(page)
            conn.request("GET", query_url, headers=headers)
            res = conn.getresponse()
            resp = json.loads(res.read())
            resp
        else:
            more_schools = False
    #DICT USED IN THE FLASK APP TO JSONIFY
    school_dict = {
        "private_school": private,
        "public_school": public,
        "catholic_school": cath,
        "other_school": other
    }
    return school_dict
### END GET SCHOOLS FUNCTION
###------------------------------------------###
#---------------------------------------------------------------#
#Query Community API and return the results as JSON object 'resp'

#API URL: https://developer.onboard-apis.com/docs
#---------------------------------------------------------------#

###------------------------------------------###
### START GET POIs
def barfinder(zip, zip_latlon, session):
    sel = [zip_latlon.zip_code, zip_latlon.lat, zip_latlon.lon]
    results = session.query(*sel).\
        filter(zip_latlon.zip_code ==zip)
    zip_data = {}
    for result in results:
        zip_data['ZIP_CODE'] = result[0]
        zip_data['LAT'] = result[1]
        zip_data['LON'] = result[2]
    lat = zip_data['LAT']
    lng = zip_data['LON']

    # Google API Key
    #when need to run this again, add the API key
    gkey = ""

    # types of points of interest we care about
    target_types = ["liquor_store", "gym", "park", "shopping_mall", "grocery_or_supermarket", "movie_theater"]

    #create a blank dictionary to store results
    poi_results = {}

    # loop through each target type and gather the number of each nearby
    for target in target_types:

        # set default values
        count = 0
        x = True

        # while loop that uses google radar to gather our numbers
        while x == True:

            # take in latitude and longitude, set the search radius to 5 miles (8k meters)
            target_area = {"lat": lat, "lng": lng}
            target_radius = 8000

            # create the target urls and use requests to gather the necessary data
            target_url = "https://maps.googleapis.com/maps/api/place/radarsearch/json" \
                "?types=%s&location=%s,%s&radius=%s&key=%s" % (
                    target, target_area["lat"], target_area["lng"], target_radius,
                    gkey)

            places_data = req.get(target_url).json()

            # use the len function to find the count of results
            numbers = len(places_data["results"])

            # use a series of if statments to check if we returned results. Run a second time if no results showed up as a check
            if numbers > 0:
                poi_results[target.replace("_", "").title()] = numbers
                x = False
            elif count == 1:
                x = False
            else:
                count += 1

    # return the results
    if "Liquorstore" not in poi_results:
        poi_results["Liquorstore"] = 0
    if "Gym" not in poi_results:
        poi_reuslts["Gym"] = 0
    if "Park" not in poi_results:
        poi_results["Park"] = 0
    if "Shoppingmall" not in poi_results:
        poi_results["Shoppingmall"] = 0
    if "Groceryorsupermarket" not in poi_results:
        poi_results["Groceryorsupermarket"] = 0
    if "Movietheater" not in poi_results:
        poi_results["Movietheater"] = 0
    print(poi_results)
    return poi_results

### END GET POIs
###------------------------------------------###

###------------------------------------------###
### START GET COMMUNITY DATA FUNCTION
### CALLS ONBOARD API FOR: ge demographics / avg Jan and Jun temps / crime rate / sales tax
def get_community_data(zip, census, zip_latlon, Market_Health, Home_sales, Rentals, session):

   #Onboard API Key

   #when executing this, add the real API key
    onboard_api_key = ""

    conn = http.client.HTTPSConnection("search.onboard-apis.com")
    headers = {
        'accept': "application/json",
        'apikey': onboard_api_key,
        }

    community_url = "/communityapi/v2.0.0/Area/Full/?"
    queries="AreaId=ZI"+zip
    query_url = community_url + queries
    conn.request("GET", query_url, headers=headers)
    res = conn.getresponse()
    resp = json.loads(res.read())
    community_dict = {}
    community_dict['crime'] = resp['response']['result']['package']['item'][0]['crmcytotc']
    community_dict['sales_tax']= resp['response']['result']['package']['item'][0]['salestaxrate']
    community_dict['avg_jan'] = resp['response']['result']['package']['item'][0]['tmpavejan']
    community_dict['avg_jul'] = resp['response']['result']['package']['item'][0]['tmpavejul']
    age_columns = ['age00_04','age05_09','age10_14','age15_19','age20_24','age25_29','age30_34','age35_39','age40_44',
                    'age45_49','age50_54','age55_59','age60_64','age65_69','age70_74','age75_79','age80_84','agegt85']
    labels = []
    age_groups = []
    age_group_values = []
    county_name = resp['response']['result']['package']['item'][0]['countyname']
    for x in age_columns:
        group_name = x
        age_groups.append(x)
        route = resp['response']['result']['package']['item'][0][x]
        age_group_values.append(int(route))
        label = x.replace('age','').replace('_','-').replace('gt85',' >=85') #format labels
        labels.append(label)

    # Create DF with summarized age groups
    age_by_zip = {"Groups": age_groups, "Count": age_group_values}
    age_by_zip_df = pd.DataFrame(age_by_zip)
    community_dict['_0_09'] = age_by_zip_df[0:2]['Count'].sum()
    community_dict['_10_19'] = age_by_zip_df[2:4]['Count'].sum()
    community_dict['_20_29'] = age_by_zip_df[4:6]['Count'].sum()
    community_dict['_30_39'] = age_by_zip_df[6:8]['Count'].sum()
    community_dict['_40_49'] = age_by_zip_df[8:10]['Count'].sum()
    community_dict['_50_59'] = age_by_zip_df[10:12]['Count'].sum()
    community_dict['_60_69'] = age_by_zip_df[12:14]['Count'].sum()
    community_dict['_70_plus'] = age_by_zip_df[14:18]['Count'].sum()
    school = get_schools(zip, zip_latlon, session)
    market = get_market_health_and_extremes(zip, Market_Health, Home_sales, Rentals, session)
    walk = get_walk(zip, zip_latlon, session)
    poi_data = barfinder(zip, zip_latlon, session)

    community_dict['private_school'] = school['private_school']
    community_dict['public_school'] = school['public_school']
    community_dict['catholic_school'] = school['catholic_school']
    community_dict['other_school'] = school['other_school']
    community_dict['median_home_value'] = market['median_home_value']
    community_dict['median_rental_price'] = market['median_rental_price']
    community_dict['market_health_index'] = market['market_health_index']
    community_dict['walk_score'] = walk['walk_score']
    community_dict['walk_description'] = walk['walk_description']
    community_dict['bike_score'] = walk['bike_score']
    community_dict['bike_description'] = walk['bike_description']
    #real_estate = get_real_estate(zip, Home_sales, Rentals, session)

    #note: will need to jsonify REdata and re_dict
    REdata, re_dict = get_real_estate_data(zip, Home_sales, Rentals, session)
    census_dict = census_data(zip,zip_latlon, census, session)
    #Community dict used for FLASK app to jsonify
    return [community_dict, poi_data, census_dict, REdata, re_dict]
### END GET COMMUNITY DATA FUNCTION
###------------------------------------------###
###------------------------------------------###
### START GET CITY SLIP HISTORY DATA FUNCTION
#Mirrors the city_slip sqlite database and presents all records stored
def cityslip_history():
    Base = declarative_base()
    engine = create_engine("sqlite:///city_slip.sqlite")
    session = Session(engine)
    city_query = engine.execute("SELECT * FROM city_slip").fetchall()
    print(city_query)
    citySlip_records = []
    for c in city_query:
        record_dict = {}
        record_dict['00_record'] = c[0]
        record_dict['01_zip_code'] = c[1]
        record_dict['02_city'] = c[2]
        record_dict['03_state'] = c[3]
        record_dict['04_county'] = c[4]
        record_dict['05_score_date'] = c[5]
        record_dict['06_avg_home_value'] = c[6]
        record_dict['07_avg_rent'] = c[7]
        record_dict['08_re_market_health'] = round(c[8])
        record_dict['09_avg_winter_temp'] = c[9]
        record_dict['10_avg_summer_temp'] = c[10]
        record_dict['11_total_schools'] = c[11]
        record_dict['12_total_pois'] = c[12]
        record_dict['13_pop_growth'] = c[13]
        record_dict['14_sales_tax_rate'] = c[14]
        record_dict['15_walkability'] = c[15]
        record_dict['16_crime_risk'] = c[16]
        if c[17] < 1:
            record_dict['17_score'] = round(c[17] * 100)
        else:
            record_dict['17_score'] = round(c[17])
        citySlip_records.append(record_dict)

    return citySlip_records

### END GET CITY SLIP HISTORY DATA FUNCTION
###------------------------------------------###
