from requests import get, post
import re
import json
import os
import fnmatch
# this function takes the folder name and string "wk" as inputs and returns any number that comes after the string in a folder name.
# This means that a saturday or "s" lecture will still be placed in the correct week number. 
def find_week_number(text, c):
    return re.findall(r'%s(\d+)' % c, text)
                   

# Walks through current directory 
for folder , sub_folders , files in os.walk(os.getcwd()):
    if ("wk" in folder) or ("Wk" in folder):

    # Finds the week number from the folder name and assigns to variable week - returns a list which must be converted to str or int to be used next
        week = find_week_number(folder, 'wk')
        print("Wk num is:", week)
        #print("Type:", type(week))
    
    
    # Converting integers into strings
        str_week = [str(week)] 
        week_string = str("".join(str_week)) # Join the string values into one string
        #print("Wkstr num is:", week_string)
        #print("Type str:", type(week_string))
 

    # Creates a list of the files in the current directory on github    
        git_files = files
        print("Git files are:", git_files)


