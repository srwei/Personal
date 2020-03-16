import urllib
import re
import requests
import csv 
from bs4 import BeautifulSoup
from csv import DictReader, DictWriter
from socket import error as SocketError
from nltk.tokenize import sent_tokenize

prepositions = ['as', 'such', 'for', 'with', 'without', 'if', 'about', 'e.g.', 'in', 'into', 'at', 'until']

measurement_units = ['teaspoons','tablespoons','cups','containers','packets','bags','quarts','pounds','cans','bottles',
		'pints','packages','ounces','jars','heads','gallons','drops','envelopes','bars','boxes','pinches',
		'dashes','bunches','recipes','layers','slices','links','bulbs','stalks','squares','sprigs',
		'fillets','pieces','legs','thighs','cubes','granules','strips','trays','leaves','loaves','halves']

unnecessary_words = ['chunks', 'pieces', 'rings', 'spears']

preceding_words = ['well', 'very', 'super']

succeeding_words = ['diagonally', 'lengthwise', 'overnight']

description_preds = ['removed', 'discarded', 'reserved', 'included', 'inch', 'inches', 'old', 'temperature', 'up']


def check_plurals_helper(string, plural_string):
    
    if string[0] != plural_string[0]:
        return None
    if len(string) > 1 and len(plural_string) > 1 and string[1] != plural_string[1]:
        return None
    if len(string) > 2 and len(plural_string) > 2 and string[2] != plural_string[2]:
        return None

    if string == plural_string or \
            string + 's' == plural_string or \
            string + 'es' == plural_string or \
            string[:-1] + 'ies' == plural_string or \
            string[:-1] + 'ves' == plural_string:
        return plural_string

    return None

def check_plurals(string, plural_list):
    for plural_string in plural_list:
        if check_plurals_helper(string, plural_string):
            return plural_string
        
    return None

#main function
def main():
    recipe_csv = open('recipes.csv', 'w')
    recipe_csv.truncate()

    output_text = open('output.txt', 'w')
    output_text.truncate()

    ingredients_csv = open('all_ingredients.csv', 'r')
    ingredients_csv.truncate()

    description_regex = re.compile(r"\([^()]*\)")

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
        num_ingredients = len(ingredients_object) - 3
        
        for i in range(num_ingredients):
            ingredient = {}
            ingredient_str = ingredients_object[i].text
            while True:
                description = description_regex.search(ingredient_str)
                if not description:
                    break
                description_string = description.group()
                ingredient_str.replace(description_string, "")
            ingredient_str = ingredient_str.replace(","," and ")
            ingredient_str = ingredient_str.replace("-"," ")
            parsed_ingredient = ingredient_str.split(" ")

            for i in range(len(parsed_ingredient)):
                if parsed_ingredient[i] in prepositions:
                    parsed_ingredient = parsed_ingredient[:i]
                    break

        
        for i in range(0, len(parsed_ingredient)):
            plural_unit = check_plurals(parsed_ingredient[i], measurement_units)
            if plural_unit:
                del parsed_ingredient[i]

                if i < len(parsed_ingredient) and parsed_ingredient[i] == "+":
                    while "+" in parsed_ingredient:
                        index = parsed_ingredient.index("+")
                        del parsed_ingredient[index]
                break
        
        for word in parsed_ingredient:
            if word in unnecessary_words:
                parsed_ingredient.remove(word)

        index = 0
        while index < len(parsed_ingredient):
            descriptionString = ""
            word = parsed_ingredient[index]

            # search through descriptions (adjectives)
            if word in descriptions:
                descriptionString = word

                # check previous word
                if index > 0:
                    previousWord = parsed_ingredient[index - 1]
                    if previousWord in preceding_words or previousWord[-2:] == "ly":
                        descriptionString = previousWord + " " + word
                        parsed_ingredient.remove(previousWord)

                # check next word
                elif index + 1 < len(parsed_ingredient):
                    nextWord = parsed_ingredient[index + 1]
                    if nextWord in succeeding_words or nextWord[-2:] == "ly":
                        descriptionString = word + " " + nextWord
                        parsed_ingredient.remove(nextWord)

            # word not in descriptions, check if description with predecessor
            elif word in description_preds and index > 0:
                descriptionString = parsed_ingredient[index - 1] + " " + word
                del parsed_ingredient[index - 1]
            
            # either add description string to descriptions or check next word
            if descriptionString == "":
                index+=1
            else:
                ingredient["descriptions"].append(descriptionString)
                parsed_ingredient.remove(word)

        
        




