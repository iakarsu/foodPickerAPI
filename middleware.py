from urllib.request import Request, urlopen, URLError
from bs4 import BeautifulSoup
from collections import namedtuple
from operator import attrgetter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import os, csv, json

def linker(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    web_byte = urlopen(req).read() 
    webpage = web_byte.decode('utf-8')
    soup = BeautifulSoup(webpage, 'html.parser')

    return soup

def selenium_linker(url):
    driver = webdriver.Firefox(executable_path='/home/iakarsu/geckodriver')
    driver.get(url)   
    delay = 5 # seconds
    i = 0

    while i<1000:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1

    restaurant = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'ys-result-items')))
    restaurant_html = restaurant.get_attribute("outerHTML")
    soup = BeautifulSoup(restaurant_html, features="html.parser")
    driver.close()
    return soup

def csv_writer(file_path, file_name, file_type, file_content):
    with open(file_path + file_name + '.csv', 'a', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(file_type._fields)
        writer.writerows(file_content)

def list_sorter(list_, index_):
    sorted_list = sorted(list_, key = attrgetter(index_))
    return sorted_list

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
    if admin_comments is not None:
        for i in admin_comments:
            if i in comments:
                comments.remove(i)

    return comments

def comment_cleaner(comments, keyword):
    comment_found =  []

    if(comments is not None):
        for i in comments:
            if keyword in i.text: 
                comment_found.append(i)

        return comment_found
    else:
        return []
    
def average_calculator(comments):
    averageSpeed = 0
    averageService = 0
    averageTaste = 0
    length = len(comments)

    for i in comments:
        speed = int(i.speed[5:])
        service = int(i.service[8:])
        taste = int(i.taste[8:])

        averageSpeed += speed / length
        averageService += service / length
        averageTaste += taste / length

    return {'averageSpeed': averageSpeed, 'averageService': averageService, 'averageTaste': averageTaste}

def get_comments(url):
    comment = namedtuple('comment', ['speed', 'service', 'taste', 'text'])

    soup = linker(url)
     
    comments_pages = soup.find('ul', class_= 'ys-commentlist-page pagination')

    if(comments_pages is not None):
        comments_pages_links = comments_pages.findAll('li')

        if(comments_pages_links is not None):
            comments_page_count = len(comments_pages_links)

            i = 0

            comments = []
            clean_user_comments = []
            clean_admin_comments = []
            clean_user_speed = []
            clean_user_service = []
            clean_user_taste = []
            
            while (i <= 7):
                
                if(comments_page_count == 1):
                    sub_url = url
                else:
                    sub_url = url + '?section=comments&page=' + str(i)


                sub = linker(sub_url)
                if(sub is not None):
                    sub_soup = sub

                    comments_all = sub_soup.find('div', class_= 'comments allCommentsArea') 
                    
                    user_comment_speed = comments_all.findAll('div', class_='speed')
                    user_comment_service = comments_all.findAll('div', class_='flavour')
                    user_comment_taste = comments_all.findAll('div', class_='serving')
                    user_comments = comments_all.findAll('div', class_='comment row')
                    admin_comments = comments_all.findAll('div', class_='comments-body comments-restaurant')

                    for j in user_comments:
                        clean_user_comments.append(j.p.text)

                    for j in admin_comments:
                        clean_admin_comments.append(j.p.text)    

                    for j in user_comment_speed:
                        clean_user_speed.append(j.text)

                    for j in user_comment_service:
                        clean_user_service.append(j.text)

                    for j in user_comment_taste:
                        clean_user_taste.append(j.text)    

                    i += 1


            clean_user_comments = user_admin_cleaner(clean_user_comments, clean_admin_comments)    

            for i in range(len(clean_user_comments)):
                comments.append(comment(clean_user_speed[i], clean_user_service[i], clean_user_taste[i], clean_user_comments[i]))

            return comments
    else:
        return []

def get_districts_tr(city):
    districts_tr = []

    soup = linker('https://www.yemeksepeti.com/' + city)
    if(soup is not None):
        district = soup.find("optgroup", label = "Diğer Semtler")
        
        for i in district.stripped_strings:
            districts_tr.append(i)

        return districts_tr
    else:
        return 'Connection Error'

def get_districts(city):
    District = namedtuple('district', ['name', 'aid', 'url'])
    districts = []

    url = 'https://www.yemeksepeti.com/' + city
    soup = linker(url)
    district = soup.find("optgroup", label = "Diğer Semtler")
    options = district.findAll('option')

    for i in options:
        aid = i['value']
        name = i.text
        url = i['data-url']
        districts.append(District(name, aid, url))

    print(type(districts))
    return districts

def get_cities():
    cities = []

    soup = linker('https://www.yemeksepeti.com/sehir-secim')
    city = soup.findAll('a', href=True, class_='cityLink col-md-1')

    for i in city:
        cities.append(i['href'][1:])
    
    return cities

def get_current_restaurant_information(city, district):
    restaurants = []
    lokanta = namedtuple('lokanta', ['link', 'name', 'formalAverage']) 

    district = district_purifier(district)
    url = 'https://www.yemeksepeti.com/' + city + '/' + district 
    soup = linker(url)

    if(soup is not None):

        restaurant = soup.find('div', class_ = 'ys-reslist')

        restaurant_links = restaurant.findAll('a', href=True, class_='restaurantName')
        restaurant_names = restaurant.findAll('span', class_ = None)
        restaurant_points = restaurant.findAll('span', class_ = 'point')
        
        for i in range(len(restaurant_points)):
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

    for i in range(len(restaurant)):
        r_Link = 'https://www.yemeksepeti.com' + restaurant_info[i]['href']
        r_Name = restaurant_info[i].text
        r_Point = restaurant_points[i].text
        restaurants.append(lokanta(r_Link, r_Name, r_Point))    

    return restaurants

def evaluate_restaurants(city, aid, district, keyword):
    current_restaurants = get_restaurant_informations_for_keyword(city, aid, keyword)

    Restaurant = namedtuple('restaurant', ['link', 'name', 'formalAverage'])
    New_Restaurant = namedtuple('n_restaurant', ['name', 'formalAverage', 'averageSpeed', 'averageService', 'averageTaste'])

    restaurants = []
    restaurants_new = []
    j = 0

    print(current_restaurants)

    for i in current_restaurants:
        restaurants.append(Restaurant(i.link, i.name, i.formalAverage))
        comments = get_comments(i.link)
        clean_comments = comment_cleaner(comments, keyword)

        if len(clean_comments) > 2:
            new_points = average_calculator(clean_comments)
            restaurants_new.append(New_Restaurant(restaurants[j].name, restaurants[j].formalAverage, new_points['averageSpeed'], new_points['averageService'], new_points['averageTaste']))
       
        print(i.link)
        print("----------------------------")

        j+=1

    return restaurants_new



