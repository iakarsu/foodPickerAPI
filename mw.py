from models import session, City, District, Restaurant, Comment, Pending_Restaurants
import parser as p
import db_functions as db
from collections import namedtuple
import time

def get_cities():
    cities = db.get_cities()
    return cities

def get_districts(city_id):
    districts = db.get_districts(city_id)

    return districts

def get_district_names(city_id):
    district_names = []
    districts = db.get_districts(city_id)
    for district in districts:
        district_names.append(district)

    return district_names

def get_restaurants(city, district_id, keyword):
    new_restaurants = []
    district = session.query(District).filter(District.id == district_id).first()

    #istenen keyword için o bölgedeki restoranlar dinamik olarak taranır, açık olup database de verisi olan restoranlar
    #proper list olarak döndürülür
    restaurants = p.get_restaurant_informations_for_keyword(city, district.district_y_id, keyword)
    proper_list = p.checkRestaurants(restaurants, district.id)

    for restaurant in proper_list:
        comments = db.get_restaurant_comments(restaurant.id)
        clean_comments = p.comment_cleaner(comments, keyword)

        if len(clean_comments) >= 5:
            new_points = p.average_calculator(clean_comments)
            if(new_points['averageSpeed'] != 0):
                calculatedAverage = (new_points['averageSpeed'] + new_points['averageService'] + new_points['averageTaste']) / 3
            else:
                calculatedAverage = (new_points['averageService'] + new_points['averageTaste']) / 2
            print(calculatedAverage)
            new_restaurant = {"name": restaurant.name, "formalAverage": restaurant.average, "calculatedAverage": calculatedAverage,
                                "averageSpeed": new_points['averageSpeed'], "averageService": new_points['averageService'],
                                "averageTaste": new_points['averageTaste'], "totalComments": len(comments), "clean_comments": len(clean_comments)}

            new_restaurants.append(new_restaurant)
    # p.jsonWriter(new_restaurants)
    return new_restaurants

