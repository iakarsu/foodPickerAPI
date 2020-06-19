from urllib.request import Request, urlopen, URLError, HTTPError
from bs4 import BeautifulSoup
from collections import namedtuple
from operator import attrgetter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
import os, csv, json, time, httplib2
from models import session, City, District, Restaurant, Comment, Pending_Restaurants
import db_functions as db

def jsonWriter(list):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(list, f, ensure_ascii=False, indent=4, sort_keys=True)

def linker(url):
    print(url)
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        web_byte = urlopen(req).read() 
        webpage = web_byte.decode('utf-8')
        soup = BeautifulSoup(webpage, 'html.parser')
    except HTTPError as e:
        print('HTTPError = ' + str(e.code))
    except URLError as e:
        print('URLError = ' + str(e.reason))
    except Exception:
        import traceback
        print('generic exception: ' + traceback.format_exc())
    
    return soup

def selenium_linker(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)   
    delay = 5 # seconds
    i = 0

    while i<1000:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #restaurant = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'ys-result-items')))
        i += 1  

    restaurant = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'ys-result-items')))
    restaurant_html = restaurant.get_attribute("outerHTML")
    soup = BeautifulSoup(restaurant_html, features="html.parser")
    print('done!')
    driver.close()
    return soup

def csv_writer(file_path, file_name, file_type, file_content):
    with open(file_path + '-' + file_name + '.csv', 'a', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(file_type._fields)
        writer.writerows(file_content)

def list_sorter(list_, index_):
    list_ = sorted(list_, key = attrgetter(index_))
    return list_

def district_purifier(district):
    list = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'İ': 'i', 'i̇': 'i', 'ş': 's', 'ö': 'o', 'ü': 'u', ' ': '-', '(': '', ')': '', '.': '', '–': '', '--': '-'}
    district = district.lower()
    dash = '--'

    for i in list:
        if(district[-1:] == ' '):
            district = district[:-1]

        district = district.replace(i, list[i])

    for i in district:
            district = district.replace(dash, '-')

    return district

def user_admin_cleaner(comments, admin_comments):
    
    for i in admin_comments:
        if i in comments:
            comments.remove(i)

    return comments

def comment_cleaner(comments, keyword):
    comment_found =  []

    for i in comments:
        if keyword in i.text: 
            comment_found.append(i)

    return comment_found
    
def average_calculator(comments):
    averageSpeed = 0
    averageService = 0
    averageTaste = 0
    length = len(comments)

    for i in comments:
        #check if restaurant has valet service
        if(i.speed != 0):
            speed = int(i.speed[5:])
            averageSpeed += speed / length
        else:
            averageSpeed += 0

        service = int(i.service[8:])
        taste = int(i.taste[8:])
        averageService += service / length
        averageTaste += taste / length

    return {'averageSpeed': averageSpeed, 'averageService': averageService, 'averageTaste': averageTaste}

def checkRestaurants(restaurants, district_id):
    proper_list = []
    unproper_list = []

    #eğer aranan restoranlar db de yoksa onları db ye ekle sonra restoranları çek
    for restaurant in restaurants:
        #restoran db de mi?
        rest = session.query(Restaurant).filter(Restaurant.link == restaurant.link).first()
        if (rest):
            proper_list.append(rest)
        else:
            #restoran zaten unproperlere eklenmiş mi?
            unp = session.query(Pending_Restaurants).filter(Pending_Restaurants.link == restaurant.link).first()
            if(unp):
                print(restaurant.name + " restaurant already in pending list")
            else:
                print(restaurant)
                unproper_list.append(restaurant)

    #restoranları pending tablosuna ekle
    db.import_to_pending_restaurants(district_id, unproper_list)

    return proper_list
   
def get_current_restaurant_information(district):
    restaurants = []
    lokanta = namedtuple('lokanta', ['link', 'name', 'formalAverage']) 

    district = district_purifier(district)
    url = 'https://www.yemeksepeti.com' + district 
    soup = linker(url)

    if(soup is not None):

        restaurant = soup.find('div', class_ = 'ys-reslist')

        restaurant_links = restaurant.findAll('a', href=True, class_='restaurantName')
        restaurant_names = restaurant.findAll('span', class_ = None)
        restaurant_points = restaurant.findAll('span', class_ = 'point')
        
        for i in range(len(restaurant_links)):
            r_Link = 'https://www.yemeksepeti.com' + restaurant_links[i]['href']
            r_Name = restaurant_names[i].text
            r_Point = restaurant_points[i].text
            restaurants.append(lokanta(r_Link, r_Name, r_Point))    

        return restaurants
    else:
        return []

def get_restaurant_informations_for_keyword(city, aid, keyword):
    restaurants = []
    lokanta = namedtuple('lokanta', ['link', 'name', 'formalAverage']) 

    url = 'https://www.yemeksepeti.com/' + city + '/arama#ors:true|st:' + keyword + '|aid:' + aid 
    soup = selenium_linker(url)

    restaurant = soup.find('div', class_ = 'ys-result-items')
    restaurant_info = restaurant.findAll('a', href=True, class_='restaurantName')
    restaurant_points = restaurant.findAll('span', class_ = 'point')
  
    print(len(restaurant_info))
    if len(restaurant_info) > 0:
        for i in range(len(restaurant)):
            r_Link = 'https://www.yemeksepeti.com' + restaurant_info[i]['href']
            r_Name = restaurant_info[i].text
            r_Point = restaurant_points[i].text
            restaurants.append(lokanta(r_Link, r_Name, r_Point))    
        return restaurants
    else: 
        return []

def evaulate_restaurants(city, aid, district, keyword):
    #get restaurants for desired keyword from desired district
    current_restaurants = get_restaurant_informations_for_keyword(city, aid, keyword)

    #restaurant is ordinary restaurant
    Restaurant = namedtuple('restaurant', ['link', 'name', 'formalAverage'])

    #new restaurant is restaurant included new points calculated by our program
    New_Restaurant = namedtuple('n_restaurant', ['name', 'formalAverage', 'calculatedAverage', 'averageSpeed', 'averageService', 'averageTaste', 'total_comments', 'clean_comments'])

    restaurants = []
    restaurants_new = []
    j = 0

    for i in current_restaurants:
        if(i):
            restaurants.append(Restaurant(i.link, i.name, i.formalAverage))
            comments = get_comments(i.link)
            clean_comments = comment_cleaner(comments, keyword)

            if len(clean_comments) > 2:
                new_points = average_calculator(clean_comments)
                if(new_points['averageSpeed'] != 0):
                    calculatedAverage = (new_points['averageSpeed'] + new_points['averageService'] + new_points['averageTaste']) / 3
                else:
                    calculatedAverage = (new_points['averageService'] + new_points['averageTaste']) / 2

                restaurants_new.append(New_Restaurant(restaurants[j].name, restaurants[j].formalAverage, calculatedAverage,
                                        new_points['averageSpeed'], new_points['averageService'], new_points['averageTaste'], len(comments), len(clean_comments)))
            
            # else:
            #     restaurants_new.append(New_Restaurant(restaurants[j].name, restaurants[j].formalAverage, 0,
            #                             0, 0, 0, len(comments), 0))
        
            print(i.link)
            print(j)
            print("----------------------------")
        else:
            restaurants.append("")

        j+=1

    restaurants_new = list_sorter(restaurants_new, 'calculatedAverage')
    file_path = os.path.abspath(os.getcwd())
    file_name = city + district + ':' + keyword
    file_type = New_Restaurant
    file_content = restaurants_new

    return restaurants_new
