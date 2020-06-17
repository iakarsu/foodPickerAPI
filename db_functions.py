from models import session, City, District, Restaurant, Comment, Pending_Restaurants, Pending_Comments
import parser as p
import time, re

def get_cities():
    return session.query(City).all()

def get_districts(city_id):
    if city_id == 0:
        districts = session.query(District).all()
    else:    
        districts = session.query(District).filter(District.city_id == city_id).all()
    return districts  

def get_restaurants(district_id = 0):
    if district_id == 0:
        restaurants = session.query(Restaurant).all()
        return restaurants
    else:
        restaurant = session.query(Restaurant).filter(Restaurant.district_id == district_id).all() 
        return restaurant

def get_restaurant_comments(restaurant_id=0):
    if restaurant_id == 0:
        comments = session.query(Comment).all()
        return comments
    else:
        comments = session.query(Comment).filter(Comment.restaurant_id == restaurant_id).all() 
        return comments

def import_to_pending_restaurants(district_id, restaurants):
    objects = []
    #status True ise restoran listesine eklenmemiştir
    if restaurants is not None:
        for restaurant in restaurants:
            avg = float(re.split(r'[\"]?([0-9\.]*)[\"]?', restaurant.formalAverage)[1])
            new_restaurant = Pending_Restaurants(name = restaurant.name, link = restaurant.link, speed =0,
                                    service = 0, taste = 0, average = avg, district_id = district_id, status = 1)
            objects.append(new_restaurant)
            
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

