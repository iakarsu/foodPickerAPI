from models import session, City, District, Restaurant, Comment, Pending_Restaurants, Pending_Comments
import parser as p
import time, re, json

def get_cities():
    # cities = []
    city = session.query(City).all()
    # for c in city:
    #     cy = {"name": c.name, "link": c.link, "population": c.population}
    #     cities.append(cy)
    # json.dumps(cities, indent=4, sort_keys=True, default=str)
    return city

def get_districts(city_id):
    if city_id == 0:
        districts = session.query(District).all()
    else:    
        districts = session.query(District).filter(District.city_id == city_id).all()
    return districts  

def get_district_by_id(district_id):
    print(district_id)
    district = session.query(District).filter(District.id == district_id).first()
    return district

def get_restaurants(district_id = 0):
    if district_id == 0:
        restaurants = session.query(Restaurant).all()
        return restaurants
    else:
        restaurant = session.query(Restaurant).filter(Restaurant.district_id == district_id).all() 
        return restaurant

def get_pending_restaurants():
    return session.query(Pending_Restaurants).all()

def get_restaurant_comments(restaurant_link):
    restaurant = session.query(Restaurant).filter(Restaurant.link.ilike("%"+ restaurant_link +"%")).first()
    comments = session.query(Comment).filter(Comment.restaurant_id == restaurant.id).all()
    return comments

def import_to_pending_restaurants(district_id, restaurants):
    objects = []
    
    for restaurant in restaurants:
        link = restaurant['link'][28:]
        status = session.query(Pending_Restaurants).filter(Pending_Restaurants.link.ilike("%"+ link +"%")).first()
        if(status is None):
            avg = float(re.split(r'[\"]?([0-9\.]*)[\"]?', restaurant['formalAverage'])[1])
            new_restaurant = Pending_Restaurants(name = restaurant['name'], link = restaurant['link'], speed =0,
                                    service = 0, taste = 0, average = avg, district_id = district_id, status = 1)
            objects.append(new_restaurant)
        else:
            pass    
    session.add_all(objects)
    session.commit()
    
def import_to_pending_comments(restaurants):
    objects = []
    for restaurant in restaurants:
        restaurant = session.query(Restaurant).filter(Restaurant.link == restaurant.link).first()
        pending_comment = Pending_Comments(restaurant_id = restaurant.id)
        objects.append(pending_comment)
    session.add_all(objects)
    session.commit()
