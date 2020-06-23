import parser as p
from fastapi import FastAPI, HTTPException
import os, requests, uvicorn
from dotenv import load_dotenv

load_dotenv(verbose=True)
api_url = os.getenv("DB_URL")

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "FoodPicker"}

@app.get("/cities")
def get_cities():
    cities = requests.get(api_url + '/cities')
    if(cities.status_code == 200):
        return cities.json()
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"City-id": "City id is not correct"},
        )

@app.get("/districts/{city_id}")
async def get_districts(city_id):
    districts = requests.get(api_url + '/districts/' + city_id)
    if(districts):
        return districts.json()
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"City-id": "City id is not correct"},
        )

#Return average points of restaurants from desired city
#desired district on related keyword
@app.get("/average_of_restaurants/{city}/{district_id}/{keyword}")
async def evaulate_restaurants(city, district_id, keyword):
    restaurants = p.get_restaurants(city, district_id, keyword)
    restaurants.sort(key=lambda x: x.get('calculatedAverage'))
    if(restaurants):
        return restaurants
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Restaurants": "Restaurants have not found"},
        )
    