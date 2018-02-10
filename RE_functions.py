# Dependencies
import requests as req
import json
import zipcodes
import pandas as pd

import numpy as np
import http.client
from datetime import datetime
import time as time
import csv
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Integer, String, Float, Text

#PROJ2: Get the home sales and rentals from the sqlite database
# note: zip_str is a string, not an integer
def get_real_estate_data(zip_str, Home_sales, Rentals,session):
    rentals = [[]]
    home_values = [[]]
    county = ""
    found = 3


    print("get real estate data zip: " + zip_str)
    #need zip_code to be an int for the database queries
    zip_code = int(zip_str)

    zip_data = zipcodes.matching(zip_str)
    city = zip_data[0]['city']
    state = zip_data[0]['state']

    #next get county from home sales
    county_res = session.query (Home_sales.county).filter(Home_sales.zip_code == zip_code).all()
    if len(county_res) > 0:
        county = county_res[0][0]
        print("county: "+ county)
        #get the home sales data
        results = session.query( Home_sales.s2014_03, Home_sales.s2014_06, Home_sales.s2014_09, Home_sales.s2014_12,\
                Home_sales.s2015_03, Home_sales.s2015_06, Home_sales.s2015_09, Home_sales.s2015_12, \
                Home_sales.s2016_03, Home_sales.s2016_06, Home_sales.s2016_09, Home_sales.s2016_12, \
                Home_sales.s2017_03, Home_sales.s2017_06, Home_sales.s2017_09,Home_sales.s2017_12).filter(Home_sales.zip_code == zip_code).all()
        all_homes = pd.DataFrame(results, columns=['2014_03', '2014_06', '2014_09','2014_12', '2015_03','2015_06', '2015_09','2015_12',\
                '2016_03','2016_06', '2016_09','2016_12','2017_03','2017_06', '2017_09','2017_12'])
        home_values = all_homes.values.tolist()
        print(home_values)
        periods = all_homes.columns.tolist()
        print(periods)
    else:
        print("PROBLEM; looking for other zips")


        #find nearby zip codes
        z = find_near_zips(zip_str, city, state)
        print(z)
        p = {}
        for q in z:
            q = int(q)

            results = session.query( Home_sales.s2014_03, Home_sales.s2014_06, Home_sales.s2014_09, Home_sales.s2014_12,\
                             Home_sales.s2015_03, Home_sales.s2015_06, Home_sales.s2015_09, Home_sales.s2015_12, \
                             Home_sales.s2016_03, Home_sales.s2016_06, Home_sales.s2016_09, Home_sales.s2016_12, \
                             Home_sales.s2017_03, Home_sales.s2017_06, Home_sales.s2017_09,Home_sales.s2017_12).filter(Home_sales.zip_code == q).all()
            if len(results) > 0:
                county_res = session.query (Home_sales.county).filter(Home_sales.zip_code == q).all()
                county = county_res[0][0]
                print("found home data for another zip")
                print("county: "+ county)
                all_homes = pd.DataFrame(results, columns=['2014_03', '2014_06', '2014_09','2014_12', '2015_03','2015_06', '2015_09','2015_12',\
                            '2016_03','2016_06', '2016_09','2016_12','2017_03','2017_06', '2017_09','2017_12'])
                home_values = all_homes.values.tolist()
                print(home_values)
                periods = all_homes.columns.tolist()
                print(periods)
                break
            else:
                next

    #now get the rental data; rental data may exist even if there is no home data for the zip
    results = session.query( Rentals.r2014_03, Rentals.r2014_06, Rentals.r2014_09, Rentals.r2014_12,\
             Rentals.r2015_03, Rentals.r2015_06, Rentals.r2015_09, Rentals.r2015_12, \
             Rentals.r2016_03, Rentals.r2016_06, Rentals.r2016_09, Rentals.r2016_12, \
             Rentals.r2017_03, Rentals.r2017_06, Rentals.r2017_09,Rentals.r2017_12).filter(Rentals.zip_code == zip_code).all()
    if len(results) > 0:
        all_rentals = pd.DataFrame(results, columns=['2014_03', '2014_06', '2014_09','2014_12', '2015_03','2015_06', '2015_09','2015_12',\
                    '2016_03','2016_06', '2016_09','2016_12','2017_03','2017_06', '2017_09','2017_12'])
        rentals = all_rentals.values.tolist()
        print(rentals)
    else:

        print(" no rentals found; looking for other zips")
        z = find_near_zips(str(zip_str), city.upper(), state)
        p = {}
        for q in z:
            q = int(q)
            results = session.query( Rentals.r2014_03, Rentals.r2014_06, Rentals.r2014_09, Rentals.r2014_12,\
                     Rentals.r2015_03, Rentals.r2015_06, Rentals.r2015_09, Rentals.r2015_12, \
                     Rentals.r2016_03, Rentals.r2016_06, Rentals.r2016_09, Rentals.r2016_12, \
                     Rentals.r2017_03, Rentals.r2017_06, Rentals.r2017_09,Rentals.r2017_12).filter(Rentals.zip_code == q).all()
            if len(results) > 0:
                print("found rental data for another zip")

                all_rentals = pd.DataFrame(results, columns=['2014_03', '2014_06', '2014_09','2014_12', '2015_03','2015_06', '2015_09','2015_12',\
                        '2016_03','2016_06', '2016_09','2016_12','2017_03','2017_06', '2017_09','2017_12'])
                rentals = all_rentals.values.tolist()
                print(rentals)
                #get county if no home data
                if county == "":
                    county_res = session.query (Home_sales.county).filter(Home_sales.zip_code == q).all()
                    county = county_res[0][0]
                break
            else:
                next

    recent_rent = 0
    recent_home_value = 0

    #if no data was found, store 0s
    if len(home_values[0]) == 0 & len(rentals[0]) == 0:
        periods.append(0)
        rentals[0].append(0)
        home_values.append(0)
        print("No Home or Rental Data Found")
        found = 0
    elif len(rentals[0]) == 0:
        print("No Rent Data Found")
        found = 1
        print(len(periods))
        for i in range(0, len(periods)):
            rentals[0].append(0)
        recent_home_value = all_homes.iloc[-1]['2017_12']
    elif len(home_values[0]) == 0:
        print("No Home Value Data Found")
        found = 2
        for j in range(0, len(periods)):
            home_values[0].append(0)
        recent_rent = all_rentals.iloc[-1]['2017_12']
    else:
        #store the most recent home value and rent for use in score
        recent_home_value = all_homes.iloc[-1]['2017_12']
        recent_rent = all_rentals.iloc[-1]['2017_12']

    #once all data has been gotten, store it in REdata
    REdata = []
    for i in range(len(periods)):
        row = {}
        row["period"] = periods[i]
        print(home_values[0][i])
        row["home_value"] = home_values[0][i]
        row["rental"] = rentals[0][i]
        REdata.append(row)

    #create dict/list for the rest of the data
    re_dict = []
    row = {}
    #need to store the zip as a string to include leading 0 (set above)
    row["zip"] = zip_str
    row["city"] = city
    row["state"] = state
    row["county"] = county
    row["home_value"] = home_values[0][i]
    row["rental"] = rentals[0][i]
    re_dict.append(row)

    print(REdata)
    print(re_dict)
    return (REdata, re_dict)

#PROJ2: get all market health index from sqlite; also get median home sales and rental price
# This index indicates the current health of a given region’s housing market relative to other markets nationwide.
# It is calculated on a scale of 0 to 10, with 0 = the least healthy markets and 10 = the healthiest markets.
def get_market_health_and_extremes(zip_code, Market_Health, Home_sales, Rentals, session):
    market_dict = {}
    results = session.query( Market_Health.market_health_index).filter(Market_Health.zip_code == zip_code).all()
    try:
        for mhi in results:
            market_health_index = mhi.market_health_index
        market_dict['market_health_index'] = market_health_index
    except:
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


#---------------------------------------------------------------#
# Find the nearest zipcode to a zipcode missing data
def find_near_zips(zipc, city, state):
    x = zipcodes.similar_to(zipc[0],
                    zips=zipcodes.filter_by(zipcodes.list_all(), active=True, city= city, state = state))
    zipps = []
    for zips in x:
        zipps.append(zips['zip_code'])
    return zipps


#---------------------------------------------------------------#
# UPDATED FOR PROJ2 (2/3/18)
#function to calculate the city score/zip slip!  Calculate 0-100 score
# note: zip_factors aka community_dict
def compute_score(zip_factors, poi_data, census_dict, REdata, re_dict):

    #prepare to write the computed score and meta data to the sql database
    Base = declarative_base()
    engine = create_engine("sqlite:///city_slip.sqlite")
    session = Session(engine)

    class City_Slip(Base):
        __tablename__ = "city_slip"
        id = Column(Integer, primary_key=True)
        zip_code = Column(Integer)
        city = Column(Text)
        state = Column(Text)
        county = Column(Text)
        score_date = Column(Text)
        avg_home_value = Column(Float)
        avg_rent = Column(Float)
        re_market_health = Column(Float)
        avg_winter_temp = Column(Float)
        avg_summer_temp = Column(Float)
        total_schools = Column(Integer)
        total_pois = Column(Integer)
        pop_growth = Column(Float)
        sales_tax_rate = Column(Float)
        walkability = Column(Float)
        crime_risk = Column(Float)
        score = Column(Float)


    # compute ratios; closest to 1 is best
    # home and rent each have a max of 0.05
    #if no recent home value or rent data, set the scores to a median value but notify user
    if re_dict[0]['home_value'] == 0:
        RE_home = 0.025
        print("There is no Home Value Data.")
    else:
        home_value_ratio = re_dict[0]['home_value'] / zip_factors['median_home_value']

        #RE_value (home: 0.05; rent: 0.05)
        if home_value_ratio < 1.3:
            RE_home = 0.05
        elif home_value_ratio <= 1.8:
            RE_home = 0.03
        else:
            RE_home = 0.01

    if re_dict[0]['rental'] == 0:
        RE_rent = 0.025
        print("There is no Monthly Rental Data.")
    else:
        rent_ratio = re_dict[0]['rental'] / zip_factors['median_rental_price']
        if rent_ratio < 1.3:
            RE_rent= 0.05
        elif rent_ratio <= 1.8:
            RE_rent = 0.03
        else:
            RE_rent = 0.01

    #market health is 0.05
    MH = (zip_factors['market_health_index']/10) * .05


    # walkability is a percent -- worth 0.05
    WK = (zip_factors['walk_score']/100) * 0.05

    tax_rate = float(zip_factors['sales_tax'])
    #tax - worth 0.05
    if tax_rate == 0:
        TX = 0.05
    elif tax_rate <= 3:
        TX = 0.04
    elif tax_rate <= 5:
        TX = 0.03
    elif tax_rate <= 6:
        TX = 0.02
    elif tax_rate <= 7:
        TX = 0.01
    else:
        TX = 0

    #crime risk (100 is median); worth 0.15
    crime = float(zip_factors['crime'])
    if crime < 100:
        CM = .15
    elif crime <= 150:
        CM = .1
    elif crime <= 200:
        CM = 0.05
    else:
        CM = 0

    #weather; worth .1 total
    avg_jan = float(zip_factors['avg_jan'])
    if avg_jan < 20:
        WW = 0
    elif avg_jan < 30:
        WW = 0.01
    elif avg_jan < 40:
        WW = 0.03
    elif avg_jan < 50:
        WW = 0.04
    else:
        WW = 0.05

    avg_jul = float(zip_factors['avg_jul'])
    if avg_jul > 100:
        WS = 0
    elif avg_jul > 90:
        WS = 0.01
    elif avg_jul >80:
        WS = 0.03
    elif avg_jul >70:
        WS = 0.05
    else:
        WS = 0.04


    #population growth: 0.10 total
    pop_growth = float(census_dict['diff_2010_2016'])
    #temporary; delete when the real thing is available
    if pop_growth < 0:
        PG = 0
    elif pop_growth >= 0.07:
        PG = 0.05
    else:
        PG = 0.1

    #POIs: total worth: .3 broken down as follows:

    points_of_interest = poi_data['Groceryorsupermarket'] + poi_data['Gym'] + poi_data['Liquorstore'] + \
        poi_data['Movietheater'] + poi_data['Park'] + poi_data['Shoppingmall']
    if points_of_interest < 400:
    	POI = .1
    elif points_of_interest < 800:
    	POI = .2
    else:
    	POI = .3

    #use ratio of private to public schools; 0.1 total
    if zip_factors['public_school'] == 0:
        SCH = 0
    else:
        sum_schools = zip_factors['private_school'] + zip_factors['catholic_school'] + zip_factors['public_school']
        SCH = ((zip_factors['private_school'] + zip_factors['catholic_school']) / zip_factors['public_school']) * 0.1
        #if ratio of private to public is over 1, then cap the SCH score
        if SCH > 0.1:
            SCH = 0.1


    #add up all the values to get the score:
    score = RE_home + RE_rent + MH + WK + TX + CM + WW + WS + PG + POI + SCH
    date = datetime.now().strftime("%m/%d/%y")
    city = re_dict[0]['city']
    zip_code = re_dict[0]['zip']
    state = re_dict[0]['state']
    county = re_dict[0]['county']

    # print the breakdown of total score
    print("Breakdown of Total Score for %s" % zip_code)
    print()
    print("Average Home Value: %s/5 | Average Rent: %s/5 | Real Estate Market Health: %s/5" % (round(RE_home*100, 2), round(RE_rent*100,2), round(MH*100,2)))
    print("Average Winter Temp (F): %s/5 | Average Summer Temp (F): %s/5" % (round(WW*100,2), round(WS*100,2)))
    print("Total Schools: %s/10 | Total Points of Interest: %s/30" % (round(SCH*100,2), round(POI*100,2)))
    print("Population Growth: %s/10" % round(PG*100, 2))
    print("Sales Tax Rate: %s/5" % round(TX*100,2))
    print("Walkability: %s/5" % round(WK*100,2))
    print("Crime Risk: %s/15" % round(CM*100,2))
    print()
    print("CitySlip Score (0-100): %s" % round(score * 100,2))

    #write the metadata to the City_Slip database
    score_data = City_Slip(
        zip_code = zip_code,
        city = city,
        state = state,
        county = county,
        score_date = date,
        avg_home_value = re_dict[0]['home_value'],
        avg_rent = re_dict[0]['rental'],
        re_market_health = zip_factors['market_health_index'],
        avg_winter_temp = zip_factors['avg_jan'],
        avg_summer_temp = zip_factors['avg_jul'],
        total_schools = sum_schools,
        total_pois = points_of_interest,
        pop_growth = pop_growth,
        sales_tax_rate = float(zip_factors['sales_tax']),
        walkability = zip_factors['walk_score'],
        crime_risk = zip_factors['crime'],
        score = score)

    def check_score(city_check, score):
        zip_check = []
        for city in city_check:
            if city[17] == score:
                zip_check.append('True')
            else:
                zip_check.append('False')
        return zip_check
    #format SQL select statement with zip_code
    city_sql = "SELECT * FROM city_slip WHERE zip_code == %s" % zip_code
    city_check = engine.execute(city_sql).fetchall()
    if len(city_check) == 0:
        #if the zipcode has not been logged then insert in to database
        print("New zipcode data, record inserted in database")
        session.add(score_data)
        session.commit()
    elif 'True' in check_score(city_check, score):
        #check to see if the zipcode exists in the DB, if it does verify whether score is the same.
        print("Record exists in database, bypassing import")
    else:
        #if the zipcode exists in the DB, but not with same score, then insert record
        print("New data acquired on zipcode in database, inserting record")
        session.add(score_data)
        session.commit()

    return score
