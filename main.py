import mw as mw
from fastapi import FastAPI, HTTPException

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
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"City-id": "City id is not correct"},
        )

#Return average points of restaurants from desired city
#desired district on related keyword
@app.get("/average_of_restaurants/{city}/{district_id}/{keyword}")
async def evaulate_restaurants(city, district_id, keyword):
    restaurants = mw.get_restaurants(city, district_id, keyword)
    if(restaurants):
        return restaurants
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Restaurants": "Restaurants have not found"},
        )
    

