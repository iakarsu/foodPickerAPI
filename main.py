import middleware as mw
from collections import namedtuple

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "FoodPicker"}

@app.get("/cities")
def get_cities():
    cities = []

    soup = mw.linker('https://www.yemeksepeti.com/sehir-secim')
    city = soup.findAll('a', href=True, class_='cityLink col-md-1')

    for i in city:
        cities.append(i['href'][1:])
    
    print(cities)

    return cities

@app.get("/districts/{city}")
def get_districts(city):
    districts = []

    soup = mw.linker('https://www.yemeksepeti.com/' + city)
    district = soup.find("optgroup", label = "Diğer Semtler")
    
    for i in district.stripped_strings:
        districts.append(i)

    for i in range(len(districts)):
        districts[i] = mw.district_purifier(districts[i])

    return districts

@app.get("/average_restaurants/{city}/{district}/{keyword}")
def evaulate_restaurants(keyword, city, district):
    current_restaurants = mw.get_current_restaurant_information(city, district)

    Restaurant = namedtuple('restaurant', ['link', 'name', 'formalAverage'])
    New_Restaurant = namedtuple('n_restaurant', ['name', 'formalAverage', 'averageSpeed', 'averageService', 'averageTaste'])
    restaurants = []
    restaurants_new = []
    j = 0

    for i in current_restaurants:
        restaurants.append(Restaurant(i.link, i.name, i.formalAverage))
        comments = mw.get_comments(i.link)
        clean_comments = mw.comment_cleaner(comments, keyword)

        if len(clean_comments) > 2:
            new_points = mw.average_calculator(clean_comments)
            restaurants_new.append(New_Restaurant(restaurants[j].name, restaurants[j].formalAverage, new_points['averageSpeed'], new_points['averageService'], new_points['averageTaste']))
       
        print(i.link)
        print("----------------------------")

        j+=1


    return restaurants_new