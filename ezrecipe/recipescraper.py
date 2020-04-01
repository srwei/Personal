import urllib
import re
import requests
import csv
from bs4 import BeautifulSoup
from csv import DictReader, DictWriter
from socket import error as SocketError
from nltk.tokenize import sent_tokenize


descriptions = ['baked', 'beaten', 'blanched', 'boiled', 'boiling', 'boned', 'breaded', 'brewed', 'broken', 'chilled',
		'chopped', 'cleaned', 'coarse', 'cold', 'cooked', 'cool', 'cooled', 'cored', 'creamed', 'crisp', 'crumbled',
		'crushed', 'cubed', 'cut', 'deboned', 'deseeded', 'diced', 'dissolved', 'divided', 'drained', 'dried', 'dry',
		'fine', 'firm', 'fluid', 'fresh', 'frozen', 'grated', 'grilled', 'ground', 'halved', 'hard', 'hardened',
		'heated', 'heavy', 'juiced', 'julienned', 'jumbo', 'large', 'lean', 'light', 'lukewarm', 'marinated',
		'mashed', 'medium', 'melted', 'minced', 'near', 'opened', 'optional', 'packed', 'peeled', 'pitted', 'popped',
		'pounded', 'prepared', 'pressed', 'pureed', 'quartered', 'refrigerated', 'rinsed', 'ripe', 'roasted',
		'roasted', 'rolled', 'rough', 'scalded', 'scrubbed', 'seasoned', 'seeded', 'segmented', 'separated',
		'shredded', 'sifted', 'skinless', 'sliced', 'slight', 'slivered', 'small', 'soaked', 'soft', 'softened',
		'split', 'squeezed', 'stemmed', 'stewed', 'stiff', 'strained', 'strong', 'thawed', 'thick', 'thin', 'tied',
		'toasted', 'torn', 'trimmed', 'wrapped', 'vained', 'warm', 'washed', 'weak', 'zested', 'wedged',
		'skinned', 'gutted', 'browned', 'patted', 'raw', 'flaked', 'deveined', 'shelled', 'shucked', 'crumbs',
		'halves', 'squares', 'zest', 'peel', 'uncooked', 'butterflied', 'unwrapped', 'unbaked', 'warmed']

prepositions = ['as', 'such', 'for', 'with', 'without',
    'if', 'about', 'e.g.', 'in', 'into', 'at', 'until']

measurement_units = ['teaspoons', 'tablespoons', 'cups', 'containers', 'packets', 'bags', 'quarts', 'pounds', 'cans', 'bottles',
		'pints', 'packages', 'ounces', 'jars', 'heads', 'gallons', 'drops', 'envelopes', 'bars', 'boxes', 'pinches',
		'dashes', 'bunches', 'recipes', 'layers', 'slices', 'links', 'bulbs', 'stalks', 'squares', 'sprigs',
		'fillets', 'pieces', 'legs', 'thighs', 'cubes', 'granules', 'strips', 'trays', 'leaves', 'loaves', 'halves']

unnecessary_words = ['chunks', 'pieces', 'rings', 'spears', 'up', 'purpose']

preceding_words = ['well', 'very', 'super']

succeeding_words = ['diagonally', 'lengthwise', 'overnight']

description_preds = ['removed', 'discarded', 'reserved',
    'included', 'inch', 'inches', 'old', 'temperature', 'up']

hyphen_prefixes = ['non', 'reduced', 'semi', 'low']

hyphen_suffixes = ['coated', 'free', 'flavored']


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
        if check_plurals_helper(string, plural_string[1]):
            return plural_string
        if check_plurals_helper(string, plural_string):
            return plural_string

    return None

# main function


def main():
    recipe_csv = open('recipes.csv', 'w')
    recipe_csv.truncate()
    recipe_csv.close()

    output_text = open('output.txt', 'w')
    output_text.truncate()

    ingredients_csv = open('all_ingredients.csv', 'w')
    ingredients_csv.truncate()
    ingredients_csv.close()

    all_ingredients_csv = open('all_recipe_ingredients.csv', 'w')
    all_ingredients_csv.truncate()
    all_ingredients_csv.close()

    all_ingredients = []
    all_recipes = []
    all_recipe_ingredients = []

    description_regex = re.compile(r"\([^()]*\)")
    ingredientId_increment = 1

    # for recipe_id in range(6660, 27000):
    for recipe_id in range(7000, 20000):
        ingredient_count = 0
        if recipe_id == 7678:
            continue
        print("trying recipe id: {}".format(recipe_id))
        soup = None
        try:
            url = "http://allrecipes.com/recipe/{}".format(recipe_id)
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

        except requests.exceptions.HTTPError as e:
            output_text.write("{0}: No recipe".format(recipe_id))
            # output_text.write(e.response.content)
        except requests.exceptions.ConnectionError as e:
            output_text.write("{0}: CONNECTION ERROR".format(recipe_id))
            # output_text.write(e.response.content)
        except SocketError as e:
            output_text.write("{0}: SOCKET ERROR".format(recipe_id))
            # output_text.write(e.response.content)

        if soup:
            title_span = soup.find("h1", class_="recipe-summary__h1")
            serving_span = soup.find("span", class_="servings-count")
            calorie_span = soup.find("span", class_="calorie-count")
            direction_span = soup.find_all("span", class_="recipe-directions__list--item")
            ingredients_object = soup.find_all("span", class_="recipe-ingred_txt")
            footnotes_span = soup.find_all("section", class_="recipe-footnotes")

        # get title
            if not title_span:
                continue
            title = title_span.text
            #all_recipes.append([recipe_id, title])

            # get ingredients
            num_ingredients = len(ingredients_object) - 3
            for i in range(num_ingredients):
                ingredient = {}
                ingredient_str = ingredients_object[i].text
                # print(ingredient_str)
                while True:
                    description = description_regex.search(ingredient_str)
                    if not description:
                        break
                    description_string = description.group()
                    ingredient_str = ingredient_str.replace(description_string, "")
                ingredient_str = ingredient_str.replace(","," and ")
                ingredient_str = ingredient_str.replace("-"," ")
                parsed_ingredient = ingredient_str.split(" ")
                
                while "" in parsed_ingredient:
                    parsed_ingredient.remove("")	
                # print(parsed_ingredient)
                for i in range(len(parsed_ingredient)):
                    # print(parsed_ingredient)
                    if parsed_ingredient[i] in prepositions:
                        parsed_ingredient = parsed_ingredient[:i]
                        break
                # print(parsed_ingredient)
                non_digits = []
                for i in range(len(parsed_ingredient)):
                    try:
                        int_check = eval(parsed_ingredient[i])
                    except:
                        non_digits.append(i)
                
                parsed_ingredient[:] = [parsed_ingredient[i] for i in range(len(parsed_ingredient)) if i in non_digits]
                        
                    # get first word

                    # if first word is digit or fraction, eval
                    # "x" not multiplier, "%" used as modulo


                for i in range(0, len(parsed_ingredient)):
                    plural_unit = check_plurals(parsed_ingredient[i], measurement_units)
                    if plural_unit:
                        del parsed_ingredient[i]

                        if i < len(parsed_ingredient) and parsed_ingredient[i] == "+":
                            while "+" in parsed_ingredient:
                                index = parsed_ingredient.index("+")
                                del parsed_ingredient[index]
                        break
                # print(parsed_ingredient)
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
                            previous = parsed_ingredient[index - 1]
                            if previous in preceding_words or previous[-2:] == "ly":
                                descriptionString = previous + " " + word
                                parsed_ingredient.remove(previous)

                        # check next_word word
                        elif index + 1 < len(parsed_ingredient):
                            next_word = parsed_ingredient[index + 1]
                            if next_word in succeeding_words or next_word[-2:] == "ly":
                                descriptionString = word + " " + next_word
                                parsed_ingredient.remove(next_word)

                    # word not in descriptions, check if description with predecessor
                    elif word in description_preds and index > 0:
                        descriptionString = parsed_ingredient[index - 1] + " " + word
                        del parsed_ingredient[index - 1]
                    # either add description string to descriptions or check next_word word
                    if descriptionString == "":
                        index+=1
                    else:
                        parsed_ingredient.remove(word)

                while "and" in parsed_ingredient:
                    parsed_ingredient.remove("and")

                if parsed_ingredient[-1] == "or":
                    del parsed_ingredient[-1]

                for word in parsed_ingredient:
                    for suffix in hyphen_suffixes:
                        if suffix in word:
                            word=word.replace(suffix, "-" + suffix)
                        
                    for prefix in hyphen_prefixes:
                        if word.find(prefix) == 0:
                            word=word.replace(prefix, prefix + "-")

                if "powder" in parsed_ingredient and \
                    ("coffee" in parsed_ingredient or \
                        "espresso" in parsed_ingredient or \
                        "tea" in parsed_ingredient):
                    parsed_ingredient.remove("powder")

                ingredient_str = " ".join(parsed_ingredient)

                if "*" in ingredient_str:
                    ingredient_str.replace("*","")
                
                if "," in ingredient_str:
                    ingredient_str.replace(",", "")

                plural = check_plurals(ingredient_str, all_ingredients)
                if plural:
                    all_recipe_ingredients.append([recipe_id, plural[0], title, plural[1]])
                    print("added ingredient {} to recipe {}".format(plural[1].upper(), title.upper()))
                else:
                    all_ingredients.append([ingredientId_increment, ingredient_str])
                    all_recipe_ingredients.append([recipe_id, ingredientId_increment, title, ingredient_str])
                    ingredientId_increment += 1
                    print("added ingredient {} to recipe {}".format(ingredient_str.upper(), title.upper()))
                ingredient_count += 1
    
            print("finished writing recipe {}".format(title))

            all_recipes.append([recipe_id, title, ingredient_count])

    with open("all_ingredients.csv", "w") as f:
        wr = csv.writer(f)
        for i in all_ingredients:
            wr.writerow(i)

    with open("recipes.csv", "w") as f:
        wr = csv.writer(f)
        for r in all_recipes:
            wr.writerow(r)

    with open("all_recipe_ingredients.csv", "w") as f:
        wr = csv.writer(f)
        for r in all_recipe_ingredients:
            wr.writerow(r)

if __name__== "__main__":
    main()

        
