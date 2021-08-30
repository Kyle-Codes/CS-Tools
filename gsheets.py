import os
import json

def get_service(api_name, api_version, scopes, key_file_location):
    from apiclient.discovery import build
    from oauth2client.service_account import ServiceAccountCredentials
    """Get a service that communicates to a Google API.
    Args:
        api_name: The name of the api to connect to.
        api_version: The api version to connect to.
        scopes: A list auth scopes to authorize for the application.
        key_file_location: The path to a valid service account JSON key file.
    Returns:
        A service that is connected to the specified API.
    """
    # load credentials from the parent key
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file_location, scopes=scopes)
    # Build the service object.
    try:
        service = build(api_name, api_version, credentials=credentials)
        print(api_name, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def create_gsheet(service, sheet_name: str, request_type: str, directory_json: str):
    """
    Creates either a blank Google Drive sheet or copies an existing template based on whether the directory_json contains a template for the specified request type
    Args:
        service: The Google API service object used to connect. Must have Google Drive API enabled. 
        sheet_name: The title to be used for the new sheet being created
        request_type: The subcategory describing the sheet to be created. This field is used to specify the source fileId and the new file's parent folder within Google Drive. 
        directory_json: A JSON file containing specific source file ids and destination folder ids, organized by keys corresponding to the request_type field.
    Returns: 
        A dict containing "kind", "id", "name" and "mimeType" information for the Google Sheet 
    """
    with open(directory_json) as directory:
        drive_urls = json.load(directory)
    # Use directory json to determine whether to copy an existing report template or create a new blank Google Sheet
    if request_type in drive_urls.get("templates").keys():
        try:            
            return service.files().copy(fileId=drive_urls.get("templates")[request_type], 
            #rename folder_test to appropriate key in JSON file
                                body={"name": sheet_name, "parents": [drive_urls.get("folder_test")[request_type]]}).execute()
        except Exception as e:
            print('Error copying template.')
            print(e)
            return None
    else:
        try: 
            return service.files().create(body={
                "name": sheet_name, 
                "mimeType": "application/vnd.google-apps.spreadsheet", 
                #rename folder_test to appropriate key in JSON file
                "parents": [drive_urls.get("folder_test")[request_type]]}).execute() #[directory_json["folder_test"][request_type]]}).execute()
        except Exception as e: 
            print('Error creating file.')
            print(e)
            return None