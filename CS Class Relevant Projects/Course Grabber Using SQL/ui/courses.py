### CS122, Winter 2017: Course search engine: search
###
### Steven Wei

from math import radians, cos, sin, asin, sqrt
import sqlite3
import json
import re
import os


DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day is array with variable number of elements  
           -> ["'MWF'", "'TR'", etc.]
      - time_start is an integer in the range 0-2359
      - time_end is an integer an integer in the range 0-2359
      - enroll is an integer
      - walking_time is an integer
      - building ia string
      - terms is a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''
    
    order_dictionary = {1: 'dept', 2: 'course_num', 3: 'section_num', 4: 'day',  \
    5: 'time_start', 6: 'time_end', 7: 'building', 8: 'walking_time', 9: 'enrollment', \
    10: 'title'}

    parameter_list = []

    connection = sqlite3.connect(DATABASE_FILENAME)
    c = connection.cursor()
    connection.create_function("time_between", 4, compute_time_between)

    d = args_from_ui
    main_inclusion_list = []
    for key in d:
      inclusion_list = get_attributes(key)
      for attribute in inclusion_list:
        if attribute not in main_inclusion_list:
          main_inclusion_list.append(attribute)

    main_inclusion_list.sort()
    for i, number in enumerate(main_inclusion_list):
      main_inclusion_list[i] = order_dictionary[number]

    select_string = "SELECT "

    main_join_string1 = "FROM courses JOIN sections JOIN meeting_patterns JOIN \
    catalog_index JOIN gps "
                    

    main_join_string2 = "ON courses.course_id = sections.course_id AND \
                    sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id \
                    AND courses.course_id = catalog_index.course_id \
                    AND sections.building_code = gps.building_code "

    where_string = "WHERE "

    for i, attribute in enumerate(main_inclusion_list):
      if attribute == 'course_num' or attribute == 'dept' or attribute == 'title':
        table = 'courses'
      if attribute == 'day' or attribute == 'time_start' or attribute == 'time_end':
        table = 'meeting_patterns'
      if attribute == 'section_num':
        table = 'sections'
      if attribute == 'enrollment':
        table = 'sections'
      if attribute == 'building':
        table = 'sections'
        attribute = 'building_code'
      if attribute is not 'walking_time':
        if attribute is not 'building_code':
          join_string = table + '.' + attribute
          select_string = select_string + join_string + ','
      if attribute == 'time_start':
        where_string = where_string + join_string + ">=" + '?'
        if i < len(main_inclusion_list) - 1:
          where_string = where_string + ' AND '
        parameter_list.append(d[attribute])
      if attribute == 'time_end':
        where_string = where_string + join_string + "<=" + '?'
        if i < len(main_inclusion_list) - 1:
          where_string = where_string + ' AND '
        parameter_list.append(d[attribute])
      if attribute == 'day':
        day_len = len(d['day'])
        for i, day in enumerate(d['day']):
          or_string = ' OR '
          if i < day_len - 1:
            where_string = where_string + join_string + '=' + ' ? ' + or_string
            parameter_list.append(day)
          else:
            where_string = where_string + join_string + '=' + ' ? ' + " AND "
            parameter_list.append(day)

      if attribute == 'walking_time':

        walk_select_string = " gps.building_code, \
        time_between(gps.lon, gps.lat, b.lon, b.lat) AS walking_time, "
        join_select_string = " JOIN (SELECT lon, lat, building_code FROM gps \
          WHERE building_code = " + ' ? ' + ") AS b "
        parameter_list.insert(0, d['building'])  
        main_join_string1 = main_join_string1 + join_select_string
        select_string = select_string + walk_select_string
        walk_where_string = " walking_time <= " + '?' + " AND "
        parameter_list.append(d['walking_time'])
        where_string = where_string + walk_where_string

      if attribute == 'enrollment':
        if 'enroll_upper' in d and 'enroll_lower' in d:
          where_string = where_string + join_string + "<=" + '?' + ' AND '
          where_string = where_string + join_string + ">=" + '?'
          parameter_list.append(d['enroll_upper'])
          parameter_list.append(d['enroll_lower'])
        if 'enroll_upper' in d and 'enroll_lower' not in d:
          where_string = where_string + join_string + "<=" + '?'
          parameter_list.append(d['enroll_upper'])
        if 'enroll_upper' not in d and 'enroll_lower' in d:
          where_string = where_string + join_string + ">=" + '?' 
          parameter_list.append(d['enroll_lower'])
        if i < len(main_inclusion_list) - 1:
          where_string = where_string + ' AND '

    if 'terms' in d:
      word_list = d['terms'].split()
      terms_len = len(word_list)
      for i, word in enumerate(word_list):
        select_substring = "SELECT course_id FROM catalog_index WHERE word = "
        intersect_str = " INTERSECT "
        join_term_str = select_substring + "'" + word + "'"
        if terms_len == 1:
          where_string = where_string + "word = " + "'" + word + "'"
        else:  
          if i == 0:
            where_string = where_string + " courses.course_id IN (" + join_term_str \
            + intersect_str
          elif i < terms_len - 1:
            where_string = where_string + join_term_str + intersect_str
          else:
            where_string = where_string + join_term_str + ')'

    select_string = select_string[:-1] + ' '
    main_join_string = main_join_string1 + main_join_string2
    query_string = select_string + main_join_string + where_string + ';'

    c.execute(query_string, parameter_list)
    classes = c.fetchall()
    connection.close()
    header = main_inclusion_list
    finished_tuple = (header, classes)

    return finished_tuple



def get_attributes(key):
    """
    This function takes a key in the given dictionary and gives the necessary
    attributes that need to be obtained, denoted by a number indicating order.

    Input:

      key: (str) key in given dictionary

    Returns:

      inclusion_list: (list) list of attributes needed for that specific key
    """

    inclusion_list = []
    if key == 'terms' or key == 'dept':
      inclusion_list.extend([1, 2, 10])
    if key == 'day' or key == 'time_start' or key == 'time_end':
      inclusion_list.extend([1, 2, 3, 4, 5, 6])
    if key == 'walking_time' or key == 'building':
      inclusion_list.extend([1, 2, 3, 4, 5, 6, 7, 8])
    if key == 'enroll_lower' or key == 'enroll_upper':
      inclusion_list.extend([1, 2, 3, 4, 5, 6, 9])

    return inclusion_list
    


########### auxiliary functions #################
########### do not change this code #############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    #adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1 
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points 
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m 



def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i in range(len(s)):
        if s[i] == ".":
            s = s[i+1:]
            break

    return s



########### some sample inputs #################

example_0 = {"time_start":930,
             "time_end":1500,
             "day":["MWF"]}

example_1 = {"building":"RY",
             "walking_time": 10,
             "dept":"CMSC",
             "day":["MWF", "TR"],
             "time_start":1030,
             "time_end":1500,
             "enroll_lower":20,
             "terms":"computer science"}

