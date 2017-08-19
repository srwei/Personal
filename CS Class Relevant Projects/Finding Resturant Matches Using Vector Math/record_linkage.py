# CS122: Linking restaurant records in Zagat and Fodor's list
#Connor Turkatte and Steven Wei



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import jellyfish   
import util

import re
import json
import sys
import csv

def find_matches(mu, lambda_, outfile='./matches.csv', block_on=None):
    '''
    This function takes a maximum false positive rate, maximum false negative rate,
    name of csv file, and optional blocking key and makes a histogram of estimates,
    a csv file with all the matches, and returns a tuple that contains
    (matches, possible matches, unmatches)

    Inputs:
        mu: (int) maximum false positive rate
        lambda_: (int) maximum false negative rate
        outile: (str) name of output csv file
        block_on: (str) either None, 'city', 'name', or 'address'

    Returns:
        matches_data_tuple: (tuple) that contains integers of number of 
                            matches, possible matches, and unmatches
    '''
    
    zagat_file = './zagat.txt'
    fodor_file = './fodors.txt'
    pairs_file = './known_pairs.txt'

    zagat = create_df(zagat_file)
    fodors = create_df(fodor_file)
    matches = create_df(pairs_file)
    unmatches = unmatches_df(zagat, fodors)

    make_histograms(matches, unmatches)
    make_vectors(matches, 'matches')
    make_vectors(unmatches, 'unmatches')
    
    m = get_estimates(matches)
    u = get_estimates(unmatches)
    d = combine_estimates(m, u)

    possible_vectors = []
    match_vectors = []
    unmatch_vectors = []

    for vector in d:
        if d[vector][0] == 0 and d[vector][1] == 0:
            possible_vectors.append(vector)
    
    for k, v in list(d.items()):
        if v[0] == 0 and v[1] == 0:
            del d[k]

    ordered_list = []
    holder_list = []
    for vector in d:
        if d[vector][1] != 0:
            holder_list.append((vector, d[vector][0], d[vector][1], d[vector][0]/d[vector][1]))
        else:
            ordered_list.append((vector, d[vector][0], d[vector][1]))

    holder_list = sorted(holder_list, reverse=True, key=lambda tup: tup[3])
    
    for (a, b, c, d) in holder_list:
        ordered_list.append((a, b, c))

    sum_of_u = 0
    sum_of_m = 0

    ordered_list1 = ordered_list[:]

    for vector in ordered_list:
        if vector[2] + sum_of_u <= mu:
            match_vectors.append(vector[0])
            sum_of_u += vector[2]
            ordered_list1.remove(vector)

    ordered_list2 = ordered_list1[:]

    for vector in list(reversed(ordered_list1)):
        if vector [1] + sum_of_m <= lambda_:
            unmatch_vectors.append(vector[0])
            sum_of_m += vector[1]
            if vector in ordered_list2:
                ordered_list2.remove(vector)

    for i, vector in enumerate(ordered_list2):
        ordered_list2[i] = vector[0]

    possible_vectors.extend(ordered_list2)

    all_pairs_df = create_all_pairs_df(zagat, fodors)

    all_pairs_df['Names from all_pairs score'] = np.vectorize(jellyfish.jaro_winkler)\
    (all_pairs_df['zagat restaurant name'],all_pairs_df['fodors restaurant name'])

    all_pairs_df['Cities from all_pairs score'] = np.vectorize(jellyfish.jaro_winkler)\
    (all_pairs_df['zagat city name'],all_pairs_df['fodors city name'])

    all_pairs_df['Addresses from all_pairs score'] = np.vectorize(jellyfish.jaro_winkler)\
    (all_pairs_df['zagat address'],all_pairs_df['fodors address'])

    if block_on == 'city':
        all_pairs_df = all_pairs_df.ix[(all_pairs_df['zagat city name'] == all_pairs_df['fodors city name'])]
        all_pairs_df = all_pairs_df.reset_index(drop=True)

    if block_on == 'address':
        all_pairs_df = all_pairs_df.ix[(all_pairs_df['zagat address'] == all_pairs_df['fodors address'])]
        all_pairs_df = all_pairs_df.reset_index(drop=True)

    if block_on == 'name':
        all_pairs_df = all_pairs_df.ix[(all_pairs_df['zagat restaurant name'] == all_pairs_df['fodors restaurant name'])]
        all_pairs_df = all_pairs_df.reset_index(drop=True)  

    make_vectors(all_pairs_df, 'all_pairs_df')

    all_pairs_df['Match'] = 's'

    for i in range(0,all_pairs_df.shape[0]):
        all_pairs_df.set_value(i, 'Match', \
            is_match(all_pairs_df.iloc[i]['vector'],match_vectors, unmatch_vectors, possible_vectors)
        )

    matches_pairs_df = all_pairs_df.ix[(all_pairs_df['Match'] == 'Match')]
    matches_csv_list = []
    for row in matches_pairs_df.itertuples():
        matches_csv_list.append((row[1], row[5]))

    writer = csv.writer(open(outfile, 'w', newline = ''), delimiter = "|")
    writer.writerow(['zagat original string', 'fodors original string'])
    for match in matches_csv_list:
        writer.writerow(match)
    
    matches_data = all_pairs_df['Match'].value_counts()

    if 'Match' not in matches_data:
        matches_data['Match'] = 0
    if 'Unmatch' not in matches_data:
        matches_data['Unmatch'] = 0
    if 'Possible Match' not in matches_data:
        matches_data['Possible Match'] = 0

    matches_data_tuple = (matches_data['Match'], matches_data['Possible Match'], matches_data['Unmatch'])

    return matches_data_tuple


def is_match(vector, match_vectors, unmatch_vectors, possible_vectors):
    '''
    This function takes a vector(in a tuple format), match_vectors set, unmatch_vectors
    set,and possible_vectors set, and finds which set the vector is in, then returning
    whether it was a match, possible match, or unmatch.

    Inputs:
        vector: (tuple) of integers
        match_vectors: (list) of tuples that are match vectors
        unmatch_vectors: (list) of tuples that are unmatch make vectors
        possible_vectors: (list) of tuples that are possible match vectors

    Returns:
        A string that states whether it is a Match, Possible Match, or Unmatch
    '''
    if vector in match_vectors:
        return "Match"
    if vector in unmatch_vectors:
        return "Unmatch"
    if vector in possible_vectors:
        return "Possible Match"

def general_organizer(rest_string):
    '''
    This function primarily addresses the case where the address is "normal",
    i.e. it has a period and also contains numbers, and this returns a tuple that
    consists of the attributes for each restaurant string 

    Input: (str)restaurant string 

    Output: tuple with attributes as elements
    '''
    one_word_cities = ['Atlanta', 'Hollywood', 'Brooklyn', 'Malibu', 
                        'Roswell', 'Duluth', 'Decatur', 'Marietta', 'Queens', 
                        'Smyrna', 'Glendale', 'Pasadena', 'LA', 'Westwood',
                        'Venice', 'Northridge', 'Encino', 'Brentwood', 'Burbank']

    line = rest_string.strip()
    index_track1 = 0
    rest_name = ''
    city_name = ''
    result = ()
    bad_list1 = []
    bad_list2 = []

    rest_words = re.findall(r'^([^\d]*)(\d.*)$', line)
    rest_words2 = line.split()

    if len(rest_words) != 0:
        rest_words = rest_words[0]

        if rest_words[0] == '':
            for i, word in enumerate(rest_words2[1:]):
                if word.isdigit():
                    index_track1 = i + 1 
                    break
                elif word[0].isdigit() == True:
                    index_track1 = i + 1 
                    break

            for word in rest_words2[0:index_track1]:
                if word == rest_words2[index_track1 - 1]:
                    rest_name += word
                else:
                    rest_name += word + ' '
            bad_list2.append(rest_name) 

        else: 
            rest_name = rest_words[0].strip()

    if '.' in line:
        city_words = line.split('.')

        x = city_words[-2:][0]
        x = x.strip()

        if len(x) <= 2:
            city_name += x + '.' + city_words[-1:][0]
        else:
            city_name += city_words[-1:][0].strip()

        address = line.replace(rest_name, '')
        address = address.replace(city_name, '')
        address = address.strip()
        result = (line, rest_name, city_name, address)

    return result

def data_organizer(filename):
    '''
    This function essentially parses the data to a useable format.
    This includes the base cases that are not covered in the general data organizer,
    so in this case, that means this function will properly parse strings that do not 
    contain numbers and also strings that are just too random to write a code for so we
    did it by hand.The function returns a list of tuples that consist of the different 
    attributes for each restaurant string.

    Input: (str) text file name 

    Output: (list) of tuples  
    '''
    data1 = open(filename)
    data1 = data1.readlines()
    #return data1
    holder_list = []
    bad_list3 = []

    for line in data1:
        line = line.strip()
        rest_name = ''
        city_name = ''

        if '.' in line:
            result = general_organizer(line)
            if result[0] == '' or result[1] == '' or result[2] == '' or result[3] == '':
                bad_list3.append(result)
            else: 
                holder_list.append(result)

        else: 
            if filename == './fodors.txt':
                words = line.split()
                if 'San Francisco' in line:
                    if words[0] in ['Helmand', 'Splendido', 'Stars']:
                        rest_name = words[0]
                        city_name = 'San Francisco'

                    elif words[0] == 'South':
                        rest_name = 'South Park Cafe'
                        city_name = 'San Francisco'

                    else:
                        rest_name = words[0] + ' ' + words[1]
                        city_name = 'San Francisco'

                    address = line.replace(rest_name, '')
                    address = address.replace(city_name, '')
                    address = address.strip() 
                    result = (line, rest_name, city_name, address)
                    holder_list.append(result) 

                if 'Atlanta' in line:
                    if 'Dante' not in words[0]:
                        if 'Bone' in words[0]:
                            rest_name = words[0]
                            city_name = 'Atlanta' 
                        else:
                            rest_name = words[0] + ' ' + words[1]
                            city_name = 'Atlanta'

                        address = line.replace(rest_name, '')
                        address = address.replace(city_name, '')
                        address = address.strip() 
                        result = (line, rest_name, city_name, address)
                        holder_list.append(result)

                if 'New York' in line:

                    if words[0] == 'Hudson':
                        rest_name = 'Hudson River Club'
                        city_name = 'New York'

                    else:
                        rest_name = words[0] + ' ' + words[1]
                        city_name = 'New York'

                    address = line.replace(rest_name, '')
                    address = address.replace(city_name, '') 
                    address = address.strip()
                    result = (line, rest_name, city_name, address)
                    holder_list.append(result)

                if 'Los Angeles' in line:
                    if words[0] == 'Grill':
                        rest_name = 'Grill on the Alley'
                        city_name = 'Los Angeles'
                    else:
                        rest_name = "Adriano's Ristorante"
                        city_name = 'Los Angeles'

                    address = line.replace(rest_name, '')
                    address = address.replace(city_name, '')
                    address = address.strip() 
                    result = (line, rest_name, city_name, address)
                    holder_list.append(result)


    zagat_hard_code = [('Brighton Coffee Shop 9600 Brighton Way Beverly Hills',
            'Brighton Coffee Shop', 'Beverly Hills', '9600 Brighton Way'),
             ('Chez Melange 1716 PCH Redondo Beach',
                'Chez Melange', 'Redondo Beach', '1716 PCH'),
             ('The Grill On The Alley 9560 Dayton Way Beverly Hills',
                'The Grill On The Alley', 'Beverly Hills', '9560 Dayton Way'),
             ("Jody Maroni's Sausage Kingdom 2011 Ocean Front Walk Venice",
                "Jody Maroni's Sausage Kingdom", 'Venice', '2011 Ocean Front Walk'),
             ('La Salsa (LA) 22800 PCH Malibu',
                'La Salsa (LA)', 'Malibu', '22800 PCH'),
             ('Pho Hoa 642 Broadway Chinatown',
                'Pho Hoa', 'Chinatown', '642 Broadway'),
             ("Russell's Burgers 1198 PCH Seal Beach",
                "Russell's Burgers", 'Seal Beach', '1198 PCH'),
             ("Carmine's 2450 Broadway New York City",
                "Carmine's", 'New York City', '2450 Broadway'),
             ("Gray's Papaya 2090 Broadway New York City",
                "Gray's Papaya", 'New York City', '2090 Broadway'),
             ('La Caridad 2199 Broadway New York City',
                'La Caridad', 'New York City', '2199 Broadway'),
             ('Oyster Bar lower level New York City',
                'Oyster Bar', 'New York City', '89 E. 42nd St.'),
             ('Peter Luger Steak House 178 Broadway Brooklyn',
                'Peter Luger Steak House', 'Brooklyn', '178 Broadway'),
             ('Rainbow Room 30 Rockefeller Plaza New York City',
                'Rainbow Room', 'New York City', '30 Rockefeller Plaza'),
             ('Tavern on the Green Central Park West New York City',
                'Tavern on the Green', 'New York City', 'Central Park'),
             ('Veggieland 220 Sandy Springs Circle Atlanta',
                'Veggieland', 'Atlanta', '220 Sandy Springs Circle')]

    fodors_hard_code = [

        ('La Grotta at Ravinia Dunwoody Rd.  Holiday Inn/Crowne Plaza at Ravinia  Dunwoody Atlanta',
          'La Grotta','Atlanta', 'Dunwoody Rd.  Holiday Inn/Crowne Plaza at Ravinia  Dunwoody'),
         ('Little Szechuan C Buford Hwy.  Northwoods Plaza  Doraville Atlanta',
          'Little Szechuan','Atlanta','C Buford Hwy.  Northwoods Plaza  Doraville'),
         ('Mi Spia Dunwoody Rd.  Park Place  across from Perimeter Mall  Dunwoody Atlanta',
          'Mi Spia','Atlanta','Dunwoody Rd.  Park Place  across from Perimeter Mall  Dunwoody'),
         ('Toulouse B Peachtree Rd. Atlanta',
          'Toulouse','Atlanta','B Peachtree Rd.'),
         ('Garden Court Market and New Montgomery Sts. San Francisco',
          'Garden Court Market','San Francisco','New Montgomery Sts.'),
         ("Gaylord's Ghirardelli Sq. San Francisco",
          "Gaylord's",'San Francisco',"Ghiradelli Sq."),
         ('Greens Bldg. A Fort Mason San Francisco',
          'Greens','San Francisco','Landmark Bldg. A Fort Mason'),
         ("McCormick & Kuleto's Ghirardelli Sq. San Francisco",
          "McCormick & Kuleto's",'San Francisco',"Ghirardelli Sq.")]


    if filename == './zagat.txt':
        holder_list.extend(zagat_hard_code)

    if filename == './fodors.txt':
        holder_list.extend(fodors_hard_code)

    return holder_list


def csv_writer(result_organizer):
    '''
    This function takes a list generated (fodors or zagat) in the organizer and 
    creates a csv of that list with headers.
    '''
    holder_list = result_organizer
    writer = csv.writer(open('restaurant_data.csv', 'w', newline = ''), delimiter = "|")
    writer.writerow(['original string', 'restaurant name', 'city name', 'address'])
    for restaurant in holder_list:
        writer.writerow([restaurant[0].strip(), restaurant[1].strip(), restaurant[2].strip(), restaurant[3].strip()])

def csv_writer_pairs(result_organizer):
    '''
    This function takes a list generated from the fixing_known_pairs_file function
    and creates a csv of that list with headers.
    '''

    holder_list = result_organizer
    writer = csv.writer(open('known_pairs_data.csv', 'w', newline = ''), delimiter = "|")
    writer.writerow(['zagat original string', 'zagat restaurant name', 'zagat city name',
                    'zagat address', 'fodors original string', 'fodors restaurant name',
                    'fodors city name', 'fodors address'])
    for restaurant in holder_list:
        writer.writerow(restaurant)

def fixing_known_pairs_file(known_pairs_file):
    '''
    This function takes the known file txt, and first, re-organizes it in order to  
    just get the restaurant strings. It then removes the hashtag elements and fixes
    the rows that are different from the original fodor/zagat file. Finally, it parses 
    this data using the general organizer.

    Input: txt file 
    Output: (list) of tuples with attributes from both txt files 
    '''
    data2  = open(known_pairs_file)
    data2 = data2.readlines()

    holder_list1 = []
    holder_list2 = []
    index_list = []
    data2 = data2[8:]
    for line in data2: 
        if line != '\n':
           holder_list1.append(line)

    holder_string = ''
    for line in holder_list1:
        if '#' in line:
            line = '*'
        holder_string += line + ' '
    
    holder_list2 = holder_string.split('*')[:-1]

    restaurants_list = []
    for line in holder_list2:
        holder_list3 = []
        if '3434 Peachtree' in line:
            a = 'Ritz-Carlton Cafe (Buckhead) 3434 Peachtree Rd. NE Atlanta'
            b = 'Caf&eacute; Ritz-Carlton Buckhead,3434 Peachtree Rd. Atlanta'
            holder_list3 = [a,b]

        elif 'CDaniel' in line:
            a = 'Daniel 20 E. 76th St. New York City '
            b = 'Daniel 20 E. 76th St. New York '
            holder_list3 = [a,b]
        else:
            new_lines = line.split('\n')[:-1]
            for index, value in enumerate(new_lines):
                value = value.strip()
                x = len(value.split())
                if x <= 4 and index >= 1:
                    new_lines[index - 1] += value
                    new_lines[index] = ''
            for element in new_lines:
                if element != '':
                    holder_list3.append(element)

        restaurants_list.append(holder_list3)
    result_list = []

    for rest_pair in restaurants_list:
        rest_tuple = ()

        for item in rest_pair:
            if '.' in item:
                holder_tuple = general_organizer(item)
                rest_tuple += holder_tuple

            else:
                item = item.strip()
                if 'New York City' in item:
                    rest_tuple +=('Rainbow Room 30 Rockefeller Plaza New York City',
                                'Rainbow Room', 'New York City', '30 Rockefeller Plaza')

                elif 'New York' in item:
                    rest_tuple +=('Rainbow Room 30 Rockefeller Plaza New York',
                                'Rainbow Room', 'New York', '30 Rockefeller Plaza')
                else:
                    if 'Atlanta' in item:
                        words = item.split()

                        if 'Bone' in words[0]:
                            rest_name = words[0]
                            city_name = 'Atlanta' 
                        else:
                            rest_name = words[0] + ' ' + words[1]
                            city_name = 'Atlanta'

                        address = item.replace(rest_name, '')
                        address = address.replace(city_name, '')
                        address = address.strip() 
                        result = (item, rest_name, city_name, address)
                        rest_tuple += result
                    
        result_list.append(rest_tuple)

    return result_list 
    #first four a attributes are from Zagat and the next four are from fodors

def create_df(filename):
    '''
    This function takes a fileame and returns the associated pandas dataframe
    associated with it. It uses fixing_known_pairs_file and data_organizer
    to generate the lists first, then uses csv_writer and csv_writer_pairs
    to turn it into the dataframe. 

    Input: (str) name of txt file
    Returns: (pd.DataFrame) dataframe of txt file
    '''

    if filename == './known_pairs.txt':
        file_list = fixing_known_pairs_file(filename)
        csv_writer_pairs(file_list)
        df = pd.read_csv('known_pairs_data.csv', delimiter = '|')     
        return df

    else:
        file_list = data_organizer(filename)
        csv_writer(file_list)
        df = pd.read_csv('restaurant_data.csv', delimiter = '|')
        return df

def unmatches_df(zagat, fodors):
    '''
    This function takes the zagat and fodors dataframes and returns a new 
    dataframe that consists of 1000 random pairs from those two dataframes.

    Inputs:
        zagat: (pandas DataFrame)
        fodors: (pandas DataFrame)

    Returns:
        unmatches: (pandas DataFrame)
    '''

    zagat_random = zagat.sample(1000, replace = True)
    fodors_random = fodors.sample(1000, replace = True)
    zagat_random.columns = ['zagat original string', 'zagat restaurant name', 
                            'zagat city name', 'zagat address']
    fodors_random.columns = ['fodors original string', 'fodors restaurant name',
                            'fodors city name', 'fodors address']
    zagat_random = zagat_random.reset_index()
    fodors_random = fodors_random.reset_index()
    unmatches = pd.concat([zagat_random[['zagat original string', 'zagat restaurant name', 
                    'zagat city name', 'zagat address']],fodors_random[['fodors original string', 
                    'fodors restaurant name','fodors city name', 'fodors address']]], axis=1)

    return unmatches

def make_histograms(matches, unmatches):
    '''
    This function takes the matches and unmatches dataframe and first, generates 
    the jaro winkler value for each attribute(name, city, address) in each dataframe, 
    and then saves a pdf of 6 histograms that maps the frequency of their respective
    jaro winkler value.

    Inputs:
        matches: (pandas DataFrame)
        unmatches: (pandas DataFrame)

    Saves:
        A histogram called 'histograms.pdf' that maps the jaro winkler values
    '''

    unmatches['Names from unmatches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (unmatches['zagat restaurant name'],unmatches['fodors restaurant name'])

    unmatches['Cities from unmatches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (unmatches['zagat city name'],unmatches['fodors city name'])

    unmatches['Addresses from unmatches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (unmatches['zagat address'],unmatches['fodors address'])

    matches['Names from matches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (matches['zagat restaurant name'],matches['fodors restaurant name'])

    matches['Cities from matches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (matches['zagat city name'],matches['fodors city name'])

    matches['Addresses from matches score'] = np.vectorize(jellyfish.jaro_winkler)\
    (matches['zagat address'],matches['fodors address'])   

    fig = plt.figure()
    plt.subplot(3,2,1)
    plt.title('Names from matches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    matches['Names from matches score'].hist(color='b')
    
    plt.subplot(3,2,2)
    plt.title('Names from unmatches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    unmatches['Names from unmatches score'].hist(color='b')
    #grid off
    plt.subplot(3,2,3)
    plt.title('Cities from matches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    matches['Cities from matches score'].hist(color='b')
    #grid off
    plt.subplot(3,2,4)
    plt.title('Cities from unmatches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    unmatches['Cities from unmatches score'].hist(color='b')
    #grid off
    plt.subplot(3,2,5)
    plt.title('Addresses from matches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    matches['Addresses from matches score'].hist(color='b')
    #grid off
    plt.subplot(3,2,6)
    plt.title('Addresses from unmatches')
    plt.xlabel('Jaro_Winkler score')
    plt.ylabel('Frequency')
    plt.grid(b=False)
    unmatches['Addresses from unmatches score'].hist(color='b')

    plt.tight_layout()
    #fig.subplots_adjust(hspace=0.8)
    fig.savefig('histograms.pdf')

def make_vectors(df, df_name):
    '''
    This function takes a pandas DataFrame and the name of the DataFrame
    and adds a column to the dataframe called 'vector' that determines
    the jaro winkler category of that pair.

    Intput:
        df: (pandas DataFrame)
        df_name: (str) name of df
    '''
    if df_name == 'matches':
        df['vector'] = 's'
        for i in range(0,df.shape[0]):
            df.set_value(i, 'vector', \
                (util.get_jw_category(df.iloc[i]['Names from matches score']),\
                util.get_jw_category(df.iloc[i]['Cities from matches score']),\
                util.get_jw_category(df.iloc[i]['Addresses from matches score']))
                )

    if df_name == 'unmatches':
        df['vector'] = 's'
        for i in range(0,df.shape[0]):
            df.set_value(i, 'vector', \
                (util.get_jw_category(df.iloc[i]['Names from unmatches score']),\
                util.get_jw_category(df.iloc[i]['Cities from unmatches score']),\
                util.get_jw_category(df.iloc[i]['Addresses from unmatches score']))
                )

    if df_name =='all_pairs_df':
        df['vector'] = 's'
        for i in range(0,df.shape[0]):
            df.set_value(i, 'vector', \
                (util.get_jw_category(df.iloc[i]['Names from all_pairs score']),\
                util.get_jw_category(df.iloc[i]['Cities from all_pairs score']),\
                util.get_jw_category(df.iloc[i]['Addresses from all_pairs score']))
                )

def get_estimates(df):
    '''
    This function takes a dataframe and returns a dictionary that has 
    each unique vector as its key and its match or unmatch frequency
    estimate as its values.

    Input: df: (pandas DataFrame) 

    Returns: d: (dict) dictionary that contains frequency estimates of all
                        the 27 unique vectors

    '''

    d = {}
    all_vectors = []
    for x in range(3):
        for y in range(3):
            for z in range(3):
                all_vectors.append((x, y, z))

    vl = df['vector'].tolist()
    num_vectors = len(vl)

    for v in vl:
        if v not in d:
            d[v] = 1
        else:
            d[v] += 1
    for vector in all_vectors:
        if vector not in d:
            d[vector] = 0
    for vector in d:
        d[vector] = d[vector] / num_vectors

    return d

def combine_estimates(matches, unmatches):
    '''
    This function takes the matches and unmatches frequency estimates
    dictionaries and combines them into one dictionary that has the
    unique vectors as the keys and the respective matches estimate and 
    unmatches estimate as its values.

    Intputs:
        matches: (dict) of unique vectors and its frequency estimates
        unmatches: (dict) of unique vectors and its frequency estimates

    Returns:
        matches: (dict) combined dictionary of frequency estimates 
    '''

    for vector in matches:
        matches[vector] = (matches[vector], unmatches[vector])
    return matches


def create_all_pairs_df(zagat, fodors):
    '''
    This function takes the zagat and fodors DataFrames and returns a new DataFrame
    that includes all possible pairs of fodors and zagat rows. 

    Inputs:
        zagat: (pandas DataFrame)
        fodors: (pandas DataFrame)

    Returns:
        pairs_df: (pandas DataFrame) all possible zagat and fodors pairs
    '''

    tuples_list = []
    column_names = [', zagat original string', 'zagat restaurant name', 'zagat city name', \
                    'zagat address','fodors original string', 'fodors restaurant name', \
                    'fodors city name', 'fodors address']
    
    for z_row in zagat.itertuples():
        for f_row in fodors.itertuples():
            tuples_list.append((z_row[1], z_row[2], z_row[3], z_row[4], f_row[1], f_row[2], f_row[3], f_row[4]))

    pairs_df = pd.DataFrame.from_records(tuples_list, columns=column_names)

    return pairs_df       

    #
    # ----------------- YOUR CODE HERE ------------------------
    #

    #return (0, 0, 0)
'''  
    
if __name__ == '__main__':

    num_m, num_p, num_u = find_matches(0.005, 0.005, './matches.csv', 
                                       block_on=None)

    print("Found {} matches, {} possible matches, and {} " 
              "unmatches with no blocking.".format(num_m, num_p, num_u))
'''