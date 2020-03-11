import middleware as mw
from collections import namedtuple

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "FoodPicker"}

@app.get("/cities")
def get_cities():
    return mw.get_cities()

@app.get("/districts/{city}")
def get_districts(city):
    return mw.get_districts(city)

@app.get("/average_restaurants/{city}/{district}/{keyword}")
def evaulate_restaurants(keyword, city, district):
    return mw.evaluate_restaurants(keyword, city, district)

@app.get("/districts_tr/{city}")
def get_districts_tr(city):
    return mw.get_districts_tr(city)
