import csv
import requests
import bs4
import re
import json

#from bs4 import BeautifulSoup
from pprint import pprint
from typing import Dict, List, Union


def problem_1(name: str) -> List[Dict[str, Union[str, List[str]]]]:
    # TODO Write your code for Problem 1 here.
    main_url = "https://how-i-met-your-mother.fandom.com/"

    name_link = name.replace(" ","_")
    character_url = main_url + "/wiki/" + name_link #to obtain the link for each character
    
    character_result = requests.get(character_url)
    character_soup = bs4.BeautifulSoup(character_result.text, 'lxml')
    
    infobox = character_soup.find("table", {"class": "infobox character"}) #filtering the infobox
    
    infobox_details = []
    attributes = []
    values = []

    tags = infobox.find_all("div")

    for tag in tags:
        infobox_details.append(tag.text.strip().split("<a ")[0]) 
    
    for index in range(len(infobox_details)):
        if index % 2 == 0:
            attributes.append(infobox_details[index]) #assigning attributes
        else:
            values.append(re.sub("[\[].*?[\]]", "", infobox_details[index])) #assigning values

    info_list=[]

    for ind in range(len(attributes)):
        info_list.append(dict(attribute = attributes[ind], value = values[ind])) #assigning key value pairs to list

    return info_list
    


def problem_2_1() -> List[Dict[str, str]]:
    base_url = "https://www.lsf.uni-saarland.de/qisserver/rds?state=wtree&search=1&trex=step&root120221=320944%7C310559%7C318658%7C311255&P.vx=kurz&lang=en&noDBAction=y&init=y&lang=en"

    # TODO Write your code for Problem 2.1 here.

    headers = {"Accept-Language": "en-US,en;q=0.9"} #to use only english version
    base_result = requests.get(base_url, headers)
    
    base_soup = bs4.BeautifulSoup(base_result.text, 'lxml')
    
    content = base_soup.find("div", {"class": "content_max_portal_qis"})
    
    all_links = content.find_all("a", {"class": "ueb"})

    all_courses_url = all_links[5].attrs['href'] #link with all courses
    
    course_result = requests.get(all_courses_url)
    course_soup = bs4.BeautifulSoup(course_result.text, 'lxml')

    each_course_table = course_soup.find_all("table", {"summary": "Übersicht über alle Veranstaltungen"})
    
    #tables 1:5, 2:8, 3:32, 4:32, 5:4, total:81
    links=[]
    courses=[]
    for table in each_course_table:
        tds = table.find_all("a", {"class": "regular"}) #finding links to each course
        for td in tds:
            courses.append(td.text.strip())
            links.append(td.attrs['href'].strip())

    course_list=[]

    for ind in range(len(courses)):
        course_dictionary = {'Name of Course': courses[ind], 'URL': links[ind]} #assigning key value pairs to dictionary
        course_list.append(course_dictionary)
        
    return course_list


def problem_2_2(url: str) -> Dict[str, Union[str, List[str]]]:
    # TODO Write your code for Problem 2.2 here.

    headers = {"Accept-Language": "en-US,en;q=0.9"} #to use only english version
    course_result = requests.get(url, headers)
    
    course_soup = bs4.BeautifulSoup(course_result.text, 'lxml')
    
    info_table_headers = course_soup.find_all("table", {"summary": "Grunddaten zur Veranstaltung"}) #for basic information
    
    instructor_headers = course_soup.find_all("table", {"summary": "Verantwortliche Dozenten"}) #for responsible instructors
    
    attr = []
    vals = []
    add_links = []
    all_instructors = []

    for head in info_table_headers:
        lhs = head.find_all("th", "mod")
        rhs = head.find_all("td", "mod_n_basic")
    
    for right in rhs:
        header_string = ' '.join(map(str, right.get('headers'))) #to remove extra spaces
        if header_string=="basic_12":
            add_links.append(right.text.strip())
        else:
            inter = right.text.replace(u'\xa0',u' ').replace('\t','').replace('\n','').strip()
            inter = re.sub(' +', ' ', right.text.replace(u'\xa0',u' ').replace('\t','').replace('\n','').strip())
            vals.append(inter)
            
    vals.append(add_links)

    for left in lhs:
        attr.append(left.text.strip())
    
    if(len(vals)!=len(attr)):
        for right in rhs:
            header_string = ' '.join(map(str, right.get('headers')))
            if header_string=="basic_14":
                attr.append("application period")
    
    
    for ins in instructor_headers:
        global instructor
        global names
    
        instructor = ins.find("th", "mod").text.strip()
        attr.append(instructor)
        names = ins.find_all("td", {"class": ["mod_n_odd", "mod_n_even"]})

        for name in names:
            prof_name = name.text.replace('\xa0',' ').strip()
            all_instructors.append(prof_name) 
    
    while('' in all_instructors) :
        all_instructors.remove('')
    
    vals.append(all_instructors)

    info_dictionary = {}

    for ind in range(0,len(attr)):
        info_dictionary[attr[ind]] = vals[ind] #assigning key value pairs to dictionary

    return info_dictionary


def problem_2_3() -> None:
    # TODO Write your code for Problem 2.3 here.

    list_of_courses = problem_2_1()
    list_details_dict = []
    url_of_course = [] 
    details_of_courses = {}
    headers = []

    f = open("file.csv", 'w', newline="")
    
    for ind in range(len(list_of_courses)): #obtaining name and url of courses from problem_2_1() and assigning to separate lists
        dict = list_of_courses[ind]
        first_pair = next(iter((dict.items())))
        details_dict = {first_pair[0]:first_pair[1]}
        list_details_dict.append(details_dict)
        fieldnames = list(details_dict.keys())
        url_of_course.append(dict.get('URL'))

    details_of_courses = problem_2_2(url_of_course[0]) #to obtain field names of basic information table
    
    details_dict.update(details_of_courses)
    
    headers = []
    headers = [*details_of_courses] 
    fieldnames.extend(headers) #total 16 fields

    write = csv.writer(f)
    write_dict = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    write_dict.writeheader()

    for ind in range(0,len(url_of_course)):
        details_of_courses = problem_2_2(url_of_course[ind])
        list_details_dict[ind].update(details_of_courses)
        write_dict.writerow(list_details_dict[ind])
        
    f.close()

    return None


def main():
    # You can call your functions here to test their behaviours.
    pprint(problem_1("Lily Aldrin"))
    #pprint(problem_2_1())
    #pprint(problem_2_2("https://www.lsf.uni-saarland.de/qisserver/rds?state=verpublish&status=init&vmfile=no&publishid=136509&moduleCall=webInfo&publishConfFile=webInfo&publishSubDir=veranstaltung&noDBAction=y&init=y"))
    #pprint(problem_2_3())



if __name__ == "__main__":
    main()

#References:
#https://www.crummy.com/software/BeautifulSoup/bs4/doc/
#https://www.youtube.com/watch?v=87Gx3U0BDlo
#https://scribbleghost.net/2020/07/09/scraping-a-webpage-with-browser-based-language/
#https://www.geeksforgeeks.org/python-program-to-convert-a-list-to-string/
#https://thispointer.com/get-first-key-value-pair-from-a-python-dictionary/
#https://docs.python.org/3/library/csv.html
#https://tutorial.eyehunts.com/python/python-remove-extra-spaces-between-words-example-code/
