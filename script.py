from requests import get, post
import re
import json
import os
import bs4 
import datetime
import os
from lxml import html
from urllib.request import urlopen


"""
This section of the code is used to connect to Moodle API

"""


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


"""
This function takes the folder name and string "wk" as inputs and returns any number that comes after the string in a folder name.
This means that a folder called "wk10" will return the value "10".

"""
def find_week_number(text, c):
    return re.findall(r'%s(\d+)' % c, text)


"""
This section of the code is for getting the video info

"""

#Get info about google drive videos
video_page = get("https://drive.google.com/drive/folders/1pFHUrmpLv9gEJsvJYKxMdISuQuQsd_qX")
video_page.text
soup = bs4.BeautifulSoup(video_page.text, "lxml")
get_all_video_info = soup.find_all('div',class_ = 'Q5txwe') 

#create empty lists to store the timestamp, id, links, week numbers for videos 
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

# Generates a link to the slides using the same link root and shoot, adding the week number
    video_link_root = str('https://drive.google.com/file/d/')
    video_link_shoot = str('/view')
    link_to_this_video = str(video_link_root + video_id + video_link_shoot)
    video_link_list.append(link_to_this_video)

#create html root and shoot 
    html_video_root = str("<a href=")
    html_video_shoot = str(">"+ "Video Link for lecture: "+ str(video_date) + "</a><br>")
    video_html_link = str(html_video_root + '"'+ link_to_this_video + '"' + html_video_shoot)
    video_html_list.append(video_html_link)

# find the semester week number. Semester started on september 28th, which was week number 40 in the year - so we can calculate from here dates for the year
# If the week number is bigger than 40, then we are after september 28th, so subtract 39 to make this count from week 1. 
# If it is smaller than 40, then we must be in 2021 and so we add 14 as the first week in 2021 is the 14th week in the semester. 
    video_calender_week_num = video_date.strftime("%V")
    video_semester_week_num = ()
    if int(video_calender_week_num) >= 40:
        video_semester_week_num = int(video_calender_week_num) - 39
    else:
        video_semester_week_num = int(video_calender_week_num) + 15

    video_week_num_list.append(video_semester_week_num)

#zip the id and dates together so they can be stored together as a dict for easy access later, with the keys and values corresponding to id and time for each video. 
zip_iterator = zip(video_html_list, video_week_num_list)
video_dict = dict(zip_iterator)

"""
This section of the code is for getting the slide info

"""



#create empty lists for our week number and slide links
slide_week_list = []
slide_link_list = []

# Walks through current directory in folders containing "wk"
for folder , sub_folders , files in os.walk(os.getcwd()):
    if (("wk" in folder) or ("Wk" in folder)) and ("index.html" in files):   

# Finds the week number from the folder name and assigns to variable week - returns a list which must be converted to str or int to be used later
        week = find_week_number(folder, 'wk')
# convert week number to int - it only contains one element in the list, so the first element is all we need
        week_int = int(week[0])
# Converting into string 
        week_string = str(week[0])
# add to list of weeks
        slide_week_list.append(week_string)
  
# Generates a link to the slides using the same link root and shoot and adding the week number
        slides_link_root = str('https://mikhail-cct.github.io/ca3-test/wk')
        link_to_this_slide = str(slides_link_root + week_string)

# get the lecture titles
        url = link_to_this_slide
        html = urlopen(url).read()
        soup = bs4.BeautifulSoup(html, features="html.parser")
# kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    
# get text
        title = soup.get_text()
# break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in title.splitlines())
# break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
        title = '\n'.join(chunk for chunk in chunks if chunk)

#create html root and shoot 
        html_slide_root = str("<a href=")
        html_slide_shoot = str(">"+ "Lecture Slides for Week "+ week_string + " (" + title + ")" + "</a><br>")
        slide_link = str(html_slide_root + '"'+ link_to_this_slide + '"' + html_slide_shoot)
        

#create pdf link and concat to list containing index.html links created already
        pdf_link_shoot = str("/wk" + week_string + ".pdf" + '"' + ">"+ "PDF for Week "+ week_string + "</a><br>")
        pdf_link_this_slide = str(html_slide_root + '"' + link_to_this_slide + pdf_link_shoot)
        slide_and_pdf_concat = str(slide_link) + str(pdf_link_this_slide)
        slide_link_list.append(slide_and_pdf_concat)
        pdf_link_no_html = str( slides_link_root + week_string + "/wk" + week_string + ".pdf")
            
#create a dict to store the link and corresponding week number, zipped together so they are stored with corresponding info
zip_iterator = zip(slide_link_list, slide_week_list)
slide_dict = dict(zip_iterator)

"""
This section of the code is for updating the moodle with the matching slide and video links

"""

# work out how many moodle sections need to be updated - this may be different depending on if there are more videos or slides.  
max_summary = ()
if len(video_dict) >= len(slide_dict):
    max_summary = len(video_dict)
else:
    max_summary = len(slide_dict)

# update moodle for the range of sections we have files for 
for i in range(max_summary):

#first check for the slides - create a summary if there is an entry for the week number matching the section we are updating.
#create the summary for the slides
    slide_summary = ()
    for key, value in slide_dict.items():
        if i == int(value):
            slide_summary = key

#check if there is a video that corresponds to this week
# create summary for the videos
    video_summary = ()
#seperate keys and values - the section we are updating will add a video link if a value in video dict matches the section number 
    key_list = list(video_dict.keys())
    value_list = list(video_dict.values())
    position = ()
    video_summary = ()
    if i in value_list:
        video_summary = key_list[i-1]

# Add summaries together. If slide summary is blank, only use video summary, and vice versa. Otherwise add concat summary so both summaries are added. 
    both_summary = str(slide_summary) + str(video_summary)
    
    if str(both_summary) == "()()":
        summary = str("")
    elif str(slide_summary) == "()":
        summary = str(video_summary)
    elif str(video_summary) == "()":
        summary = str(slide_summary)
    else:
        summary = both_summary

    # Assign the correct summary
    data[0]['summary'] = summary

    # Set the correct section number
    data[0]['section'] = i

    # Write the data back to Moodle
    sec_write = LocalUpdateSections(courseid, data)

    sec = LocalGetSections(courseid)

print("Master, I have completed my assignment.")

        