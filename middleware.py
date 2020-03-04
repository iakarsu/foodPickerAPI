from urllib.request import Request, urlopen, URLError
from bs4 import BeautifulSoup
from collections import namedtuple
from operator import attrgetter
import os, csv, json

def linker(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        web_byte = urlopen(req).read() 
        webpage = web_byte.decode('utf-8')
        soup = BeautifulSoup(webpage, 'html.parser')
    except URLError as e:
        print(e)

    return soup

def csv_writer(file_path, file_name, file_type, file_content):
    with open(file_path + file_name + '.csv', 'a', newline='', encoding='utf8') as f:
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

    print(district)
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
    else:
        return []

def get_current_restaurant_information(city, district):
    restaurants = []
    lokanta = namedtuple('lokanta', ['link', 'name', 'formalAverage']) 

    district = district_purifier(district)
    url = 'https://www.yemeksepeti.com/' + city + '/' + district 
    soup = linker(url)

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

def get_districts_tr(city):
    districts_tr = []

    soup = linker('https://www.yemeksepeti.com/' + city)
    district = soup.find("optgroup", label = "Diğer Semtler")
    
    for i in district.stripped_strings:
        districts_tr.append(i)

    return districts_tr


