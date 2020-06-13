import middleware as mw
from collections import namedtuple

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "FoodPicker"}

@app.get("/cities")
async def get_cities():
    return mw.get_cities()

@app.get("/districts/{city}")
async def get_districts(city):
    districts = mw.get_districts('ankara')
    return mw.get_districts(city)

#Return average points of restaurants from desired city
#desired district on related keyword
@app.get("/average_of_restaurants/{city}/{aid}/{district}/{keyword}")
async def evaulate_restaurants(city, aid, district, keyword):
    return mw.evaluate_restaurants(city, aid, district, keyword)



