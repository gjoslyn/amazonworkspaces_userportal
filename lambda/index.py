import json
import boto3
import sys
import os
import time
from decimal import Decimal


client = boto3.client('workspaces', region_name='us-west-2')
ds_client = boto3.client('ds', region_name='us-west-2')
dynamodb_client = boto3.client('dynamodb', region_name='us-west-2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('user_cache')


def print_debug(message_to_print):
    #Uncomment  next line to enable printing (which can be turned on for debugging purposes)
    print(message_to_print)
    return
    
    
def build_error_response(username, message):
    
    result = {
        "statusCode": 500,
        "errorMessage" : message
    }
    
    #json.dumps(result)

    return result;
    
def construct_workspaces_uri(username, directoryID, regCode):
    uri = "workspaces://"+username+"@"+regCode
    #uri = "workspaces://"+username+"@"+regCode

    return uri
    
# In this function, we return the PCM URL tag for a Directory (given its ID)
# This may be useful to include in the response if you've deployed Teradici PCM
# for use with Teradici Zero Clients.
def get_pcm_url_for_directory(directoryID):
    
    # Comment out the next line if you'd like to return a Directory's PCM URL stored in a tag (that is, you are using Teradici clients)
    return ""

    tag_name = os.environ['PCM_URL_TAG']    

    tags = ds_client.list_tags_for_resource(
        ResourceId=directoryID
    )

    if(len(tags["Tags"])<1):
        return "";

    # Get first key, value pair which matches our Key value
    pcm_tag = next((tag for tag in tags["Tags"] if tag.get('Key') == tag_name), None)

    # If the PCM tag has not been set, pcm_tag will be empty. Checking that here.
    if pcm_tag:
        return pcm_tag["Value"]
    else:
        return ""

# In this function, we return the NAME tag for a Directory (given its ID)
# This may be useful to include in the response if there are multiple directories
# which contain a WorkSpace for the user. This will make it easier for the user to 
# understand what each directory is and which WorkSpace to pick.

def get_name_tag_for_directory(directoryID):

    print("Getting name tag for directory " + directoryID)
    tag_name = os.environ['NAME_TAG']
    response = check_cache("directory_cache", "directory_id", directoryID)
    print_debug(response)
    
    # If we found something in the cache, then return that instead of proceeding further.
    if 'Item' in response:
        print_debug("Found value for directory "+ directoryID +" in the cache")
        cachedResponse = response["Item"]["cached_response"]["S"]
        if cachedResponse == "EMPTY_STRING":
            return "";
        else:
            return cachedResponse

    tags = ds_client.list_tags_for_resource(
        ResourceId=directoryID
    )

    if(len(tags["Tags"])<1):
        print_debug("Adding value for directory "+ directoryID +" into the cache")
        add_to_cache("directory_cache", "directory_id", directoryID, "EMPTY_STRING")
        return ""

    # Get first key, value pair which matches our Key value
    name = next((tag for tag in tags["Tags"] if tag.get('Key') == tag_name), None)

    # If the NAME tag has not been set, it will be empty. Checking that here.
    if name:
        print_debug("Adding value for directory "+ directoryID +" into the cache")
        add_to_cache("directory_cache", "directory_id", directoryID, name["Value"])
        return name["Value"]
    else:
        print_debug("Adding value for directory "+ directoryID +" into the cache")
        add_to_cache("directory_cache", "directory_id", directoryID, "EMPTY_STRING")
        return ""


def get_workspaces_info_for_user(username, list_of_directories):

# In this function, we return the Directory ID, Reg Code and PCM URL for each
# Directory that has a workspace for the user

    workspaces_info_for_user = [];

    for directory in list_of_directories:
        directoryID = directory["DirectoryId"]
        try:
            print_debug("Checking directory " + directoryID)
            response = client.describe_workspaces(
                DirectoryId=directoryID,
                UserName=username
            )

            if(len(response["Workspaces"]) > 0):
                print_debug("Found a workspace!")
                regCode = directory["RegistrationCode"]
                pcm_url = get_pcm_url_for_directory(directoryID)
                name_tag = get_name_tag_for_directory(directoryID)
                uri = construct_workspaces_uri(username, directoryID, regCode)
        
                workspaces_info_for_user.append({'directoryID':directoryID,'regCode':regCode, 
                                                'pcm_url':pcm_url, 'name':name_tag, 'uri':uri })
            else:
                print_debug("No WorkSpaces for user "+username+" in directory " + directoryID)
        except:
            print_debug("There was an error when calling directory " + directoryID)
            print_debug("Unexpected error:" + str(sys.exc_info()[0]))

    return workspaces_info_for_user

def check_cache(table_name, key_name, key_value):
    
    try:
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={
                key_name : {
                    'S': key_value
                }
            },
            ProjectionExpression='cached_response'
        )
        print_debug("Checked cache for key " + key_value)
    except:
        print_debug("An Exception occurred while checking the cache.")
        response = {};
    
    return response
    
def add_to_cache(table_name, key_name, key_value, response_to_cache):
    
    try:

        table = boto3.resource('dynamodb').Table(table_name)
        
        # Here we set the expiration time of the cache (1 hour from now, by default)
        # The TTL feature in DynamoDB will automatically remove this item after the expiration time.
        expiration_time = int(time.time() + 3600)
        
        table.update_item(
            Key={
                key_name: key_value
            },
            UpdateExpression='SET expiration_time = :val1, cached_response = :val2',
            ExpressionAttributeValues={
                ':val1': expiration_time,
                ':val2': response_to_cache
            }
        )
    
    except:
        print_debug("Exception occurred when adding to the cache.")
        print_debug("Unexpected error:", sys.exc_info())

    return
    
def lambda_handler(event, context):
    workspaces_info_for_user = [];
    username = event["username"]

    if(username == ""):
        return build_error_response(username, "Provided username is invalid.")
        
    response = check_cache("user_cache", "username", username)
    print_debug(response)
    
    # If we found something in the cache, then return that instead of proceeding further.
    if 'Item' in response:
        print_debug("Found something in the cache")
        cachedResponse = json.loads(response["Item"]["cached_response"]["S"])
        return cachedResponse

    list_of_directories = client.describe_workspace_directories()["Directories"]
    

    if(len(list_of_directories) < 1):
        return build_error_response(username, "No registered Directories found in your account.")

    directories = get_workspaces_info_for_user(username,list_of_directories)

    if(len(directories) < 1):
        result = build_error_response(username, "No WorkSpaces Found for user "+username)
        print_debug("Adding response for user "+ username +" into the cache")
        add_to_cache("user_cache", "username", username, json.dumps(result))
        return result
        
    result = {
        "statusCode": 200,
        "directories": directories
    }
    
    print_debug("Adding response for user "+ username +" into the cache")
    add_to_cache("user_cache", "username", username, json.dumps(result))
    
    return result;
