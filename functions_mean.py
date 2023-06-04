# Farmbot project 2023, Sensors & UI, Vincente Galdini
# main_user.py
# Python code run by the user via GUI.
# This code takes a range of time caracterized by two inputs, from_date and to_date.

# 1) Authorization and authentication (same structure as the one implemented on the raspberry).
# 2) Access the API.
# 3) Look through files in the drive. If the date of the file is in the wished range of time, it stores the name in a list.
# 4) Read the wished files and store the data in one txt file.
# 5) Create a csv file based on the txt file.


##---------------------------------------------------
# Import libraries

import os
import os.path

import csv

# Time, date 
import time 
from time import strftime 
from datetime import datetime, timedelta

import numpy as np

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

##---------------------------------------------------
# User's desktop path

desk_dir = os.path.expanduser("~")
desk_path =  os.path.join(desk_dir,"Desktop")

# ----------------------------
# This function gives the actual date time in the right format in order to have a different name for every files.
# That way it is easier to find the right file later on.

def give_time_now ():
    time_now = datetime.now()
    day_now = time_now.strftime("%Y_%m_%d")
    day_yest = time_now - timedelta(hours = 24)
    day_yest = day_yest.strftime("%Y_%m_%d")
    return day_now, day_yest

##---------------------------------------------------
# Authorization and authentication

def authorization_authentication():
    
    # Authorization and authentication

    
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)


    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:  
            creds.refresh(Request())

        else:  
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

        with open('token.json','w') as token:
            token.write(creds.to_json())
    return creds


##---------------------------------------------------
# Access API.
# Recover right folder ID and credentials.

def access_API(creds, from_date, to_date, day_yest):
    # We try to access the drive API with our authorization
    try:
        service = build("drive", "v3", credentials = creds)

        # Check if there is the Farmbot_sensor_data folder.
        response = service.files().list(
            q = "name='Farmbot_sensor_data' and mimeType='application/vnd.google-apps.folder' ", # We verify that is a google folder and note a file
            spaces='drive'
        ).execute() # Gives us the informations of the folder in our drive.
       
        # If there is no files.
        if not response['files']: 
            print("The file Farmbot_sensor_data doesn't exist on the drive.")
            
        # If the folder exist:
        else:
            # Recover the id of the file.
            folder_id = response['files'][0]['id']

            recover_wished_file_name(folder_id, service, from_date, to_date, day_yest)

    # In case we have error, we print them.
    except HttpError as e:
        print("Error: " + str(e))



##---------------------------------------------------
# Select the files that are in the right range of time based on their name.
# Check the date of each file.

def select_files(from_date, to_date, items):
    list_wished_files_name = []
    list_files = []
    count = 0
    
    for item in items:
        
        item_clear = str('{0}'.format(item['name']))
        item_date = int(item_clear[13:-4])
        item_type = item_clear[-4:]
       
        list_files.append(item_clear)

        if from_date != None and to_date != None:
            if item_date >= from_date and item_date <= to_date and item_type == '.csv':
                count = count +1
                list_wished_files_name.append(item_clear)
                
        

    if from_date == None and to_date == None:
        max_index_date = np.argmax(list_files)  
        latest_file = items[max_index_date]
        latest_file_clear= str('{0}'.format(latest_file['name'])) 
        latest_reducted = latest_file_clear[:-4]
        list_wished_files_name = latest_reducted + '.csv'
    

    return list_wished_files_name
            
##---------------------------------------------------
# Recover google drive file names.
# Clear the previous txt and csv files in the OS.

def recover_wished_file_name(folder_id, service, from_date, to_date, day_yest):

    # Define the query to retrieve the files in the specified folder
    query = "parents in '{}' and trashed = false".format(folder_id)

    try:
    # Execute the query to retrieve the list of files.
        results = service.files().list(q=query, fields="nextPageToken, files(name)").execute()
        items = results.get('files', [])
        

    # Print the name of each file in the list
        if not items:
            print('No files found.')
        else:
            
            # Recover the file list:
            list_wished_files_name = select_files(from_date, to_date, items)
            
            print("Charging content of wished files on the file data_of_the_day.txt :")
            
            # Clear the previous txt and csv files.
            file_path_txt = desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.txt"

            with open(file_path_txt, 'wb') as f:
                f.write(b'')

            file_path_csv = desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.csv"

            with open(file_path_csv, "w", newline='') as f_dest:
                f_dest.truncate(0)

            # Write in the cleared txt and csv files.
            if type(list_wished_files_name) == list:
                for item_wished in list_wished_files_name:
                    print(item_wished)
                    write_file_in_OS(service, item_wished, day_yest)
            if type(list_wished_files_name) == str:
                print(list_wished_files_name)
                write_file_in_OS(service, list_wished_files_name, day_yest)


    except HttpError as error:
        print(f'An error occurred: {error}')


##---------------------------------------------------
## Read wished files content and writes it in the OS txt file

def write_file_in_OS(service, target_file, day_yest):
    response_file = service.files().list(
                        q="name='" + target_file + "' and trashed=false", fields="nextPageToken, files(id, name)").execute()
                    
    target_file_id = response_file['files'][0]['id']
    
    file_download = service.files().get_media(fileId= target_file_id)
    response_wished = file_download.execute()
    
    file_path_txt = desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.txt"
    
    with open(file_path_txt, 'ab') as f:
        f.write(response_wished)


##---------------------------------------------------
# Create a csv file with the right shape based on the txt file.

def txt_to_csv(day_yest):

    path_txt = desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.txt"

    with open(path_txt, "r") as file:
        lines = file.readlines()
    
    path_csv = desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.csv"
    
    with open(path_csv, mode = 'w', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        first_line_list = ['Temps_reel', 'Temps_mesure', 'Temp_bme', 'Pressure_bme', 'Altitude_bme', 'Humidity', 'IR', 'VISIBLE', 'UV', 'Water', 'CO2', 'Temp_co2', 'Humidity_co2','O2']
        writer.writerow(first_line_list)
        
        for line in lines:
            
            if len(line) != 117 :
                
                donnees = []
                index_comma = [-1]
                
                for caracter in range(len(line)):
                    if line[caracter] == ',':
                        index_comma.append(caracter)
                        donnees.append(line[index_comma[-2]+1:index_comma[-1]])
                donnees.append(line[index_comma[-1]+1:])
                
                writer.writerow(donnees)       

            
    print("CSV file created.")


# ----------------------------
# Authorization and authentication to google drive
# Create a folder in google drive if it is not already done.
# Find the files in the OS that have the right name.
# Upload them in the right folder in google drive.
# Note: The main structure of the function 'drive_upload' is highly inspired by NeuralNine (https://www.youtube.com/watch?v=fkWM7A-MxR0) 

def drive_upload(day_yest):

    ## Authorization and authentication

    # We use google drive API.
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    creds = None

    # Check if we have a token.json in the OS. If it is we use it as a credentials.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)


    # If the credentials are inexistant or not valid. If credentials are existant but expired we refresh them:
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:  
            creds.refresh(Request())

        else:  
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)


        with open('token.json','w') as token:
            token.write(creds.to_json())


    ## Files backing up

    # We try to access the drive API with our authorization
    try:
        service = build("drive", "v3", credentials = creds)

        # Check if there is the Farmbot_daily_data folder in google drive.
        response = service.files().list(
            q = "name='Farmbot_daily_data' and mimeType='application/vnd.google-apps.folder' ", # We verify that is a google folder and not a file.
            spaces='drive'
        ).execute() # Gives us the informations of the folder in our drive.

        
        # If there is no files.
        if not response['files']: 
            file_metadata = {  # We create a dictionnary with the name and the type of Farmbot_daily_data.
                "name": "Farmbot_daily_data",
                "mimeType": "application/vnd.google-apps.folder"
            }

            # We create this folder:
            file = service.files().create(body=file_metadata, fields="id").execute()

            # We want to create AND write in this folder so we recover the id:
            folder_id = file.get('id')
            

        # If the folder exist:
        else:
            # Recover the id of the file. We find the key 'files' of the dictionnary 'response' and recover the id of the file.
            folder_id = response['files'][0]['id']
            
        
        # We look at the files we have in our OS folder. 
        
        for file in os.listdir(desk_path):
            
            
            # Upload the txt file.
            if file == 'data_of_the_day_' + day_yest + '_00_00_00.txt':
                
                file_metadata = {
                    "name": file,
                    "parents": [folder_id]  # We give the dictionnary the folder id OF THE DRIVE FOLDER.

                }
                
                
                # We create a mediafile.
                media = MediaFileUpload(f""+ desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.txt")
                

                # We create the file in the drive based on the OS file.
                upload_file = service.files().create(body=file_metadata, media_body = media, fields = "id").execute()

                
            # Upload the csv file.
            if file == 'data_of_the_day_' + day_yest + '_00_00_00.csv':
                
                file_metadata = {
                    "name": file,
                    "parents": [folder_id]  # We give the dictionnary the folder id OF THE DRIVE FOLDER.

                }

                # We create a mediafile.
                media = MediaFileUpload(f""+ desk_path + "/data_of_the_day_" + day_yest + "_00_00_00.csv")
                

                # We create the file in the drive based on the OS file.
                upload_file = service.files().create(body=file_metadata, media_body = media, fields = "id").execute()

        print("Backed up files")

    # In case we have error, we print them.
    except HttpError as e:
        print("Error: " + str(e))

