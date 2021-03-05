from requests import get, post
import re
import json
import os
import fnmatch
from bs4 import BeautifulSoup
import lxml

# Module variables to connect to moodle api:
## Insert token and URL for your site here. 
## Mind that the endpoint can start with "/moodle" depending on your installation.
KEY = "8cc87cf406775101c2df87b07b3a170d" 
URL = "https://034f8a1dcb5c.eu.ngrok.io"
ENDPOINT="/webservice/rest/server.php"

def rest_api_parameters(in_args, prefix='', out_dict=None):
    """Transform dictionary/array structure to a flat dictionary, with key names
    defining the structure.
    Example usage:
    >>> rest_api_parameters({'courses':[{'id':1,'name': 'course1'}]})
    {'courses[0][id]':1,
     'courses[0][name]':'course1'}
    """
    if out_dict==None:
        out_dict = {}
    if not type(in_args) in (list,dict):
        out_dict[prefix] = in_args
        return out_dict
    if prefix == '':
        prefix = prefix + '{0}'
    else:
        prefix = prefix + '[{0}]'
    if type(in_args)==list:
        for idx, item in enumerate(in_args):
            rest_api_parameters(item, prefix.format(idx), out_dict)
    elif type(in_args)==dict:
        for key, item in in_args.items():
            rest_api_parameters(item, prefix.format(key), out_dict)
    return out_dict

def call(fname, **kwargs):
    """Calls moodle API function with function name fname and keyword arguments.
    Example:
    >>> call_mdl_function('core_course_update_courses',
                           courses = [{'id': 1, 'fullname': 'My favorite course'}])
    """
    parameters = rest_api_parameters(kwargs)
    parameters.update({"wstoken": KEY, 'moodlewsrestformat': 'json', "wsfunction": fname})
    #print(parameters)
    response = post(URL+ENDPOINT, data=parameters).json()
    if type(response) == dict and response.get('exception'):
        raise SystemError("Error calling Moodle API\n", response)
    return response

################################################
# Rest-Api classes
################################################

class LocalGetSections(object):
    """Get settings of sections. Requires courseid. Optional you can specify sections via number or id."""
    def __init__(self, cid, secnums = [], secids = []):
        self.getsections = call('local_wsmanagesections_get_sections', courseid = cid, sectionnumbers = secnums, sectionids = secids)

   

class LocalUpdateSections(object):
    """Updates sectionnames. Requires: courseid and an array with sectionnumbers and sectionnames"""
    def __init__(self, cid, sectionsdata):
        self.updatesections = call('local_wsmanagesections_update_sections', courseid = cid, sections = sectionsdata)

################################################
# Example - This section is for getting and updating sections on moodle
################################################

courseid = "24" 
# Get all sections of the course.


# Update sections. 

# you add the other links here - the pdf and video - 26min video 2
#summary = '<a href = "https://mikhail-cct.github.io/ooapp2/wk3/#/16"> Testing </a>'

data = [{'type': 'num', 'section': 1, 'summary': '',
 'summaryformat': 1, 'visible': 1 , 'highlight': 0, 
 'sectionformatoptions': [{'name': 'level', 'value': '1'}]}]

#data[0]['summary'] = summary

#sec_write = LocalUpdateSections(courseid, data)


# this function takes the folder name and string "wk" as inputs and returns any number that comes after the string in a folder name.
# This means that a saturday or "s" lecture will still be placed in the correct week number. 
def find_week_number(text, c):
    return re.findall(r'%s(\d+)' % c, text)


# Walks through current directory 
for folder , sub_folders , files in os.walk(os.getcwd()):
    if ("wk" in folder) or ("Wk" in folder):
    
    # Finds the week number from the folder name and assigns to variable week - returns a list which must be converted to str or int to be used later
        week = find_week_number(folder, 'wk')
        #print("Wk num is:", week)
        #print("Type:", type(week))

        week_int = int(week[0])
        #print("Wkint num is:", week_int)
        #print("Type int:", type(week_int))

        # Converting into string - it only contains one element in the list, so the first element is all we need
        week_string = str(week[0])
        

       
    

        # Creates a list of the files in the current directory on github  
        git_files = files
        #print("Git files are:", git_files)  

        # Generates a link using the same link root and adding the week number
        link_root = str('https://mikhail-cct.github.io/ca3-test/wk')
        link_to_this_slide = str(link_root + week_string)
        #print("Link to slide: ", link_to_this_slide)

        #create html root and shoot (?! oppisite end to the root?!)
        html_root = str("<a href=")
        html_shoot = str(">"+ "Week Number "+ week_string + "</a><br>")
        
        # create the summary
        summary = str(html_root + '"'+ link_to_this_slide + '"' + html_shoot)
        print("Summary: ", summary)




        # Assign the correct summary
        data[0]['summary'] = summary

        # Set the correct section number
        data[0]['section'] = week_int

        # Write the data back to Moodle
        sec_write = LocalUpdateSections(courseid, data)

        sec = LocalGetSections(courseid)
        print(json.dumps(sec.getsections[1]['summary'], indent=4, sort_keys=True))



        # check whether link to the slide exists on the moodle
        # get moodle section summary
        #sec = LocalGetSections(courseid)
        print("Moodle secion summary:", json.dumps(sec.getsections[week_int]['summary'], indent=4, sort_keys=True)) 
       # if link_to_this_slide not in sec:

            
