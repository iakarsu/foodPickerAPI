import mw as mw
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "FoodPicker"}

@app.get("/cities")
async def get_cities():
    return mw.get_cities()

@app.get("/districts/{city_id}")
async def get_districts(city_id):
    districts = mw.get_districts(city_id)
    if(districts):
        return districts
    else:
        return {"404 Not Found"}

#Return average points of restaurants from desired city
#desired district on related keyword
@app.get("/average_of_restaurants/{city}/{district_id}/{keyword}")
async def evaulate_restaurants(city, district_id, keyword):
    restaurants = mw.get_restaurants(city, district_id, keyword)
    if(restaurants):
        return restaurants
    else:
        return {"404 Not Found"}
    

