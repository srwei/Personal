import urllib3
import re
from bs4 import BeautifulSoup
from csv import DictReader, DictWriter

def get_ingredients():
    url = f'https://www.simplyrecipes.com/recipes/cranberry_sauce/'
    req = urllib3.PoolManager()
    res = req.request('GET', url)
    soup = BeautifulSoup(res.data, 'html.parser')
    title_content = soup.find_all('title')
    #return title_content
    recipe = re.search(r'>  (.*?) Recipe',str(title_content)).groups(1)[0]
    contents = soup.find_all(class_= 'ingredient')
    #return contents
    ingredients = re.findall(r'>([0-9].*?)</li>', str(contents))
    return recipe, ingredients

def get_links():
    url = f'https://www.simplyrecipes.com/'