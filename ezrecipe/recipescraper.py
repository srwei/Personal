import urllib
import re
import json
import requests
from bs4 import BeautifulSoup
from csv import DictReader, DictWriter
from socket import error as SocketError
from nltk.tokenize import sent_tokenize

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
    req = urllib3.PoolManager()
    res = req.request('GET', url)


#main function
def main():
    recipe_json = open('recipes.json', 'w')
    recipe_json.truncate()

    output_text = open('output.txt', 'w')
    output_text.truncate()

    ingredients_text = open('all_ingredients.txt', 'r')
    all_ingredients = ingredients_text.read().split("\n")
    ingredients_text.close()

    for recipe_id in range(6660, 27000):
        
        soup = None
        try:
            url = "http://allrecipes.com/recipe/{}".format(recipe_id)
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
        except requests.exceptions.HTTPError as e:
            output_text.write("{0}: No recipe".format(recipe_id))
            output_text.write(e)
        except requests.exceptions.ConnectionError as e:
            output_text.write("{0}: CONNECTION ERROR".format(recipe_id))
            output_text.write(e)
        except SocketError as e:
            output_text.write("{0}: SOCKET ERROR".format(recipe_id))
            output_text.write(e)
        
        if soup:
            title_span = soup.find("h1", class_="recipe-summary__h1")
            serving_span = soup.find("span", class_="servings-count")
            calorie_span = soup.find("span", class_="calorie-count")
            direction_span = soup.find_all("span", class_="recipe-directions__list--item")
            ingredients_object = soup.find_all("span", class_="recipe-ingred_txt")
            footnotes_span = soup.find_all("section", class_="recipe-footnotes")

        #get title
        title = title_span.text


        #get ingredients
        num_ingredients = len(ingredients_objects) - 3
        
        for i in range(num_ingredients):
            ingredient = {}
            ingredient_str = ingredient_objects[i].text
            



