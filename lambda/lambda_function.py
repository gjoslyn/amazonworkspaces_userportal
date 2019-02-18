import json
import boto3
import sys
import os

client = boto3.client('workspaces', region_name='us-east-1')
ds_client = boto3.client('ds', region_name='us-east-1')

#In this function, we return the PCM URL tag for a Directory (given its ID)
def get_pcm_url_for_directory(directoryID):

    tag_name = os.environ['PCM_URL_TAG_NAME']    
    
    tags = ds_client.list_tags_for_resource(
        ResourceId=directoryID
    )
    
    if(len(tags["Tags"])<1):
        return "";
    
    # Get first key, value pair which matches our Key value
    pcm_tag = next((tag for tag in tags["Tags"] if tag.get('Key') == tag_name), None)
    
    print("URL is "+pcm_tag["Value"])
    
    return pcm_tag["Value"]
    
    
def get_dir_id_and_regcode_for_user(username, list_of_directories):

# In this function, we return the first directory ID/reg code that has a workspace for the user

    for directory in list_of_directories:
        try:
            print("Checking directory "+directory[0])
            response = client.describe_workspaces(
                DirectoryId=directory[0],
                UserName=username
            )
            #print(response)
            #print(len(response["Workspaces"]))
            if(len(response["Workspaces"]) > 0):
                print("Found a workspace!")
                return [directory[0], directory[1]]
            else:
                print("No WorkSpaces for user "+username+" in directory " + directory[0])
        except:
            print("There was an error when calling directory " + directory[0])
            print("Unexpected error:", sys.exc_info()[0])

    return []

def get_list_of_workspace_directories():

    # Get a list of all workspaces in the directory
    response = client.describe_workspace_directories()
    directories = []

    for directory in response["Directories"]:
        directoryID = directory["DirectoryId"]
        regCode = directory["RegistrationCode"]

        #Appends a tuple to the directories list. Each tuple contains the directory ID and reg code.
        directories.append([directoryID,regCode])

    #print ("Directories found: "+str(len(directories)))
    return directories


def lambda_handler(event, context):
    # TODO implement
    
    username = event["username"]

    list_of_directories = get_list_of_workspace_directories()
    
    if(len(list_of_directories) < 1):
        return {
            "statusCode": 500,
            "errorMessage" : "No registered Directories found in your account."
        } 
    
    users_directory = get_dir_id_and_regcode_for_user(username,list_of_directories)

    if(len(users_directory) < 1):
        return {
            "statusCode": 500,
            "errorMessage" : "No WorkSpaces Found for user "+username
        } 
    
    users_directory = get_dir_id_and_regcode_for_user(username,list_of_directories)
    directoryID = users_directory[0];
    regCode = users_directory[1];
    
    print("Directory for user "+username+" is " + directoryID)
    print("Reg Code for user "+username+" is " + regCode)
    
    pcm_url = get_pcm_url_for_directory(directoryID)
    
    if(pcm_url == ""):
        return {
            "statusCode": 500,
            "errorMessage" : "PCM tag not set for directory "+directoryID+". Please inform WorkSpaces administrator."
        } 
    
    return {
        "statusCode": 200,
        "pcm_url": pcm_url
    }
