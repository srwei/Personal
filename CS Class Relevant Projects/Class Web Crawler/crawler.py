# CS122: Course Search Engine Part 1
#
#Steven Wei
# Your name(s)
#

import re
import util
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are', 'as',  'at',  'be',
                    'but',  'by',  'course',  'for',  'from',  'how', 'i',
                    'ii',  'iii',  'in',  'include',  'is',  'not',  'of',
                    'on',  'or',  's',  'sequence',  'so',  'social',  'students',
                    'such',  'that',  'the',  'their',  'this',  'through',  'to',
                    'topics',  'units', 'we', 'were', 'which', 'will', 'with', 'yet'])


### YOUR FUNCTIONS HERE

def go(num_pages_to_crawl, course_map_filename, index_filename):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs: 
        CSV file of the index index.
    '''
    starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/ \
                                    new.collegecatalog.uchicago.edu/index.html"
    limiting_domain = "classes.cs.uchicago.edu"

    crawler_list = getting_urls(starting_url, limiting_domain, num_pages_to_crawl)
    index_list = creating_index(crawler_list)

    with open(index_filename, 'w') as output:
        writer = csv.writer(output, delimiter='|')
        for val in index_list:
            writer.writerow([val[0], val[1]])  

def getting_urls(starting_url, limiting_domain, max_pages):
    '''
    Original when we tried to combine both the url crawler and the indexer 
    together, our computers could not handle the load, and so we never actually 
    produced anything. Thus, we decided to split apart the functions and call get_request 
    twice. In this first function, we will crawl through all the urls with the specified 
    starting url and limiting domain, until we find all of the various urls, primarily 
    those associated with courses, or until we have visit the specified number of pages. 

    Input:  

        starting_url = string 
        Limiting_domain = string
        Max_number_pages = int

    Output:
        
        list of strings (urls)
    '''

    q = queue.Queue()
    main_list = []
    index_list = []
    count = 1 

    q.put(starting_url)
    while q.empty() == False:
        current_url = q.get()
        result = util.get_request(current_url)
        text = util.read_request(result)
        soup = bs4.BeautifulSoup(text, "html5lib")
        
        if len(soup.find_all('div', class_ = "courseblock main")) > 0:
            break

        else: 

            urls = soup.find_all('a', href = True)
            urls_string = str(urls)
            link_list = re.findall(r'href="(.*?)"', urls_string)

            for i, link in enumerate(link_list):
                link_list[i] = util.remove_fragment(link)
            
            link_list = list(set(link_list))
            for link in link_list:

                if util.is_absolute_url(link):
                    result1 = util.get_request(link)
                    if result1 is not None:
                        new_link = util.get_request_url(result1)
                        if util.is_url_ok_to_follow(new_link, limiting_domain):
                            if new_link not in main_list:
                                if count == max_pages:
                                    return main_list

                                else:

                                    main_list.append(new_link)
                                    count += 1
                                    q.put(new_link)
                                
                else:

                    new_link = util.convert_if_relative_url(current_url, link)
                    if new_link is not None:
                        result2 = util.get_request(new_link)
                        if result2 is not None:
                            new_link2 = util.get_request_url(result2)
                            if util.is_url_ok_to_follow(new_link2, limiting_domain):
                                if new_link2 not in main_list:
                                    if count == max_pages:
                                        return main_list

                                    else:
                                        main_list.append(new_link2)
                                        count += 1
                                        q.put(new_link2)
                                        
    return main_list

def creating_index(crawler_list):
    '''
    As described previously, we decided to split apart this function from 
    getting_urls. We take the output from getting_urls and we get the course 
    title and description from “courseblock main.” We then match each word 
    in title and description to the course number provided by the course_map.json. 
    We return a list of tuples where the first value is the course index code number 
    and the second value is a word found in the description/title.

    Input:

        list of strings (crawler list) 

    Ouput: 

        List of tuples
    '''
    course_list = []

    with open('course_map.json') as json_data:
        d = json.load(json_data)

    for url in crawler_list:
        result = util.get_request(url)
        text = util.read_request(result)
        soup = bs4.BeautifulSoup(text, "html5lib")
        if len(soup.find_all('div', class_ = "courseblock main")) > 0:
            department_list = soup.find_all('div', class_ = "courseblock main")

            for course in department_list:
                word_list = []
                course_string = str(course)
                course_title = re.findall('<strong>(.*?)\.', course_string)
                course_title = course_title[0].replace('\xa0', ' ')
                title_word = course_title[:4]
                word_list.append(title_word.lower())

                if '-' not in course_title:
                    course_number = d[course_title]
                    class_title = re.findall('\.(.*?)\..*Units', course_string)
                    if len(class_title) > 0:
                        old_title_word_list = re.compile
                                ('[A-Za-z]\w*').findall(class_title[0])
                        title_word_list = []
                        for word in old_title_word_list:
                            word = word.lower()
                            if word not in INDEX_IGNORE:
                                title_word_list.append(word)
                        word_list.extend(title_word_list)
                        course_description = re.findall
                                                ('class="courseblockdesc">\n(.*?)\.<', 
                                                                        course_string)
                        if len(course_description) > 0:
                            old_course_description_list = re.compile
                                        ('[A-Za-z]\w*').findall(course_description[0])
                            course_description_list = []
                            for word in old_course_description_list:
                                word = word.lower()
                                if word not in INDEX_IGNORE:
                                    course_description_list.append(word)
                            word_list.extend(course_description_list)
                            word_list = map(str.lower,word_list)
                            word_list = list(set(word_list))
                            for unique_word in word_list:
                                index = (course_number, unique_word)
                                course_list.append(index)
                        else:

                            for unique_word in word_list:
                                index = (course_number, unique_word)
                                course_list.append(index)
                else:
                    sequence_list = re.findall(r'\d+', course_title)
                    for i, course in enumerate(sequence_list):
                        tag = title_word + " " + course
                        sequence_list[i] = d[tag]
                    class_title = re.findall('\.(.*?)\.</strong>', course_string)
                    if len(class_title) > 0:
                        old_title_word_list = re.compile
                                        ('[A-Za-z]\w*').findall(class_title[0])
                        title_word_list = []
                        for word in old_title_word_list:
                            word = word.lower()
                            if word not in INDEX_IGNORE:
                                title_word_list.append(word)
                        word_list.extend(title_word_list)
                        course_description = re.findall
                                        ('class="courseblockdesc">\n(.*?)\.<', course_string)
                        if len(course_description) > 0:
                            old_course_description_list = re.compile
                                            ('[A-Za-z]\w*').findall(course_description[0])
                            course_description_list = []
                            for word in old_course_description_list:
                                word = word.lower()
                                if word not in INDEX_IGNORE:
                                    course_description_list.append(word)
                            word_list.extend(course_description_list)
                            word_list = map(str.lower,word_list)
                            word_list = list(set(word_list))
                            for number in sequence_list:
                                for unique_word in word_list:
                                    index = (number, unique_word)
                                    course_list.append(index)
                        else:
                            word_list = map(str.lower,word_list)
                            word_list = list(set(word_list))
                            for number in sequence_list:               
                                for unique_word in word_list:
                                    index = (number, unique_word)
                                    course_list.append(index)

        if len(soup.find_all('div', class_ = "courseblock subsequence")) > 0:

            department_list = soup.find_all('div', class_ = "courseblock subsequence")
            for course in department_list:
                word_list = []
                course_string = str(course)
                course_title = re.findall('<strong>(.*?)\.', course_string)
                course_title = course_title[0].replace('\xa0', ' ')
                title_word = course_title[:4]
                word_list.append(title_word.lower())

                if '-' not in course_title:
                    course_number = d[course_title]
                    class_title = re.findall('\.(.*?)\..*Units', course_string)
                    if len(class_title) > 0:

                        old_title_word_list = re.compile
                                        ('[A-Za-z]\w*').findall(class_title[0])
                        title_word_list = []
                        for word in old_title_word_list:
                            word = word.lower()
                            if word not in INDEX_IGNORE:
                                title_word_list.append(word)
                        word_list.extend(title_word_list)
                        course_description = re.findall
                                    ('class="courseblockdesc">\n(.*?)\.<', course_string)
                        if len(course_description) > 0:

                            old_course_description_list = re.compile
                                        ('[A-Za-z]\w*').findall(course_description[0])
                            course_description_list = []
                            for word in old_course_description_list:
                                word = word.lower()
                                if word not in INDEX_IGNORE:
                                    course_description_list.append(word)
                            word_list.extend(course_description_list)

                            word_list = list(set(word_list))
                            for unique_word in word_list:
                                index = (course_number, unique_word)
                                course_list.append(index)
                        else:
                            word_list = list(set(word_list))
                            for unique_word in word_list:
                                index = (course_number, unique_word)
                                course_list.append(index)

    return course_list  

    starting_url = "http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/index.html"
    limiting_domain = "cs.uchicago.edu"

    # YOUR CODE HERE

if __name__ == "__main__":
    usage = "python3 crawl.py <number of pages to crawl>"
    args_len = len(sys.argv)
    course_map_filename = "course_map.json"
    index_filename = "catalog_index.csv"
    if args_len == 1:
        num_pages_to_crawl = 1000
    elif args_len == 2:
        try:
            num_pages_to_crawl = int(sys.argv[1])
        except ValueError:
            print(usage)
            sys.exit(0)
    else:
        print(usage)    
        sys.exit(0)


    go(num_pages_to_crawl, course_map_filename, index_filename)




