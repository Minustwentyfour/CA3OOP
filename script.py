from requests import get, post
import re
import json
import os
import bs4 
import lxml
import datetime

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
# define the data 
data = [{'type': 'num', 'section': 1, 'summary': '',
 'summaryformat': 1, 'visible': 1 , 'highlight': 0, 
 'sectionformatoptions': [{'name': 'level', 'value': '1'}]}]



# this function takes the folder name and string "wk" as inputs and returns any number that comes after the string in a folder name.
# This means that a folder called "wk10" will return "10"
def find_week_number(text, c):
    return re.findall(r'%s(\d+)' % c, text)


#Generate link to google videos
video_page = get("https://drive.google.com/drive/folders/1pFHUrmpLv9gEJsvJYKxMdISuQuQsd_qX")
#type(video_page)
video_page.text
soup = bs4.BeautifulSoup(video_page.text, "lxml")
#print(soup)
get_all_video_info = soup.find_all('div',class_ = 'Q5txwe') 
#print("Video info: ", get_all_video_info)

#create empty lists to store the timestamp, id, links for videos 
video_date_list = []
video_id_list = []
video_link_list = []
video_html_list = []
video_week_num_list = []

#loop through the videos 
for video in get_all_video_info:

#find the id for each video and add to video id list 
    video_id = video.parent.parent.parent.parent.attrs['data-id']
    video_id_list.append(video_id)

#find the date pattern and add to list 
    date_pattern = re.search('\d{4}-\d{2}-\d{2}', str(video))
    video_date = datetime.datetime.strptime(date_pattern.group(), '%Y-%m-%d').date()
    video_date_list.append(video_date)
    print("time", video_date)

    # Generates a link to the slides using the same link root and adding the week number
    video_link_root = str('https://drive.google.com/file/d/')
    video_link_shoot = str('/view')
    link_to_this_video = str(video_link_root + video_id + video_link_shoot)
    video_link_list.append(link_to_this_video)
    print("Link to video: ", link_to_this_video)

#create html root and shoot (?! shoot is the opposite end to the root, right?! - That's what I mean anyway)
    html_root = str("<a href=")
    html_video_shoot = str(">"+ "Video Link for lecture: "+ str(video_date) + "</a><br>")
    video_html_link = str(html_root + '"'+ link_to_this_video + '"' + html_video_shoot)
    video_html_list.append(video_html_link)
    print("html Link to video: ", video_html_link)

# find the week number. Semester started on september 28th, which was week number 40 in the year - so we can calculate from here dates for the year
# If the week number is bigger than 40, then we are after september 28th, so subtract 39 to make this count from week 1. 
# If it is smaller than 40, then we must be in 2021 and so we add 14 as the first week in 2021 is the 14th week in the semester. 
    video_calender_week_num = video_date.strftime("%V")
    video_semester_week_num = ()
    if int(video_calender_week_num) >= 40:
        video_semester_week_num = int(video_calender_week_num) - 39
    else:
        video_semester_week_num = int(video_calender_week_num) + 14

    video_week_num_list.append(video_semester_week_num)
    print("Vid wk num", video_semester_week_num)
   




#zip the id and dates together so they can be stored together as a dict for easy access later, with the keys and values corresponding to id and time for each video. 
zip_iterator = zip(video_html_list, video_week_num_list)
video_dict = dict(zip_iterator)
print("Dict", video_dict)


# Walks through current directory in folders containing "wk"
for folder , sub_folders , files in os.walk(os.getcwd()):
    if (("wk" in folder) or ("Wk" in folder)) and ("index.html" in files):
    
    
    # Finds the week number from the folder name and assigns to variable week - returns a list which must be converted to str or int to be used later
        week = find_week_number(folder, 'wk')
        # convert week number to int - it only contains one element in the list, so the first element is all we need
        week_int = int(week[0])
        # Converting into string 
        week_string = str(week[0])

        print("Wk num is:", week_string)    
        # Generates a link to the slides using the same link root and adding the week number
        slides_link_root = str('https://mikhail-cct.github.io/ca3-test/wk')
        link_to_this_slide = str(slides_link_root + week_string)
        #print("Link to slide: ", link_to_this_slide)

        #create html root and shoot (?! shoot is the opposite end to the root, right?! - That's what I mean anyway)
        html_root = str("<a href=")
        html_link_shoot = str(">"+ "Lecture Slides for Week Number "+ week_string + "</a><br>")
        slide_link = str(html_root + '"'+ link_to_this_slide + '"' + html_link_shoot)

        #check if there is a video that corresponds to this week
        link_to_this_video = ()
        for i in video_dict:
            if video_dict[i] == week_int:
                link_to_this_video = i
                print("Corresponding video link is: ", i)
  

        
        # create the summary
        summary = (str(slide_link) + str(link_to_this_video))
                       
        print("Summary: ", summary)

        # Assign the correct summary
        data[0]['summary'] = summary

        # Set the correct section number
        data[0]['section'] = week_int

        # Write the data back to Moodle
        sec_write = LocalUpdateSections(courseid, data)

        sec = LocalGetSections(courseid)