import mw as mw, json
from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "FoodPicker DB"}

@app.get("/cities")
def get_cities():
    cities = mw.get_cities()
    if(cities):
        return cities
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the cities"},
        )

@app.get("/districts/{city_id}")
async def get_districts(city_id):
    districts = mw.get_districts(city_id)
    if(districts):
        return districts
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the districts"},
        )

@app.get("/districts/get_district/{district_id}")
async def get_district_by_id(district_id):
    district = mw.get_district_by_id(district_id)
    if(district):
        return district
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the district"},
        )

@app.get("/districts/get_district_restaurants/{district_id}")
async def get_district_by_id(district_id):
    restaurants = mw.get_restaurants(district_id)
    if(restaurants):
        return restaurants
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the restaurants"},
        )

@app.get("/get_restaurants/")
async def get_restaurants():
    restaurants = mw.get_restaurants()
    if(restaurants):
        return restaurants
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the restaurants"},
        )

@app.get("/get_restaurants_names/")
async def get_restaurants():
    names = []
    restaurants = mw.get_restaurants()
    for restaurant in restaurants:
        names.append(restaurant.name)

    if(restaurants):
        return names
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the restaurants"},
        )

@app.get("/get_pending_restaurants")
async def get_pending_restaurants():
    pending_restaurants = mw.get_pending_restaurants()
    if(pending_restaurants):
        return pending_restaurants
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the restaurants"},
        )

@app.get("/get_pending_restaurants_names")
async def get_pending_restaurants():
    names = []
    pending_restaurants = mw.get_pending_restaurants()

    for pending in pending_restaurants:
        names.append(pending.name)

    if(pending_restaurants):
        return names
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the restaurants"},
        )

@app.get("/get_restaurant_comments/{link}")
async def get_restaurant_comments(link):
    comments = mw.get_restaurant_comments(link)
    if(comments):
        return comments
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"Couldn't find the comments"},
        )
    
@app.post("/import_to_pending_restaurants/{district_id}")
async def import_to_pending_restaurants(district_id, request: Request):
    body = await request.json()
    restaurants = json.loads(body)
    mw.import_to_pending_restaurants(district_id, restaurants)
    return {"Success"}

@app.post("/import_to_pending_commentss/{restaurants}")
def import_to_pending_comments(restaurants):
    mw.import_to_pending_comments(restaurants)
    return {"Success"}        

