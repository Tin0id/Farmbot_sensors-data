# Farmbot project 2023, Sensors & UI, Vincente Galdini
# main_raspberry.py

# Main python code implemented on the raspberry pi. This code make the raspberry totaly independant.
# By choosing the sampling time on the arduino script and the back up time on this script, an infinite loop will run this code non-stop.

# The purpose of this code is to recover data from five differents sensors such as: 
#   Temperature, Pressure, Humidity, Altitude, IR, Visible light, UV,O2 and CO2 concentrations, and an indicator of rain.

# The raspberry pi is used as a master that run the main script and recover the data from the arduino via an USB port.
# The Arduino script will execute only under order of the raspberry pi. 

# Recover data
    # 1) Find the right USB port of the raspberry.
    # 2) Recover the data of the arduino serial.
    # 3) Reshape the data in the adequate type, shape
    # 4) Save those data in a dictionnary.
# Save file     
    # 5) Save the dictionnary in a .txt and .csv files. 
    # Thus the raspberry has a local backup storage.
    # 6) Authorization and authentification to google drive
    # 7) Find the .csv and .txt files and upload them on the drive API on the account farmbotsensors@gmail.com



# ----------------------------
# Import libraries :

# Time, date 
import time 
from time import strftime 
from datetime import datetime

# Serial communication
import serial
import serial.tools.list_ports 

# CSV files 
import csv

# OS
import os
import os.path

# Numpy
import numpy as np

# Google drive libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


##---------------------------------------------------
# User's desktop path

desk_dir = os.path.expanduser("~")
desk_path =  os.path.join(desk_dir,"Desktop")
# ----------------------------
# This function gives the actual date time in the right format in order to have a different name for every files.
# That way it is easier to find the right file later on.

def give_file_name_now ():
    time_now = datetime.now()
    file_name_now = time_now.strftime("%Y_%m_%d_%H_%M_%S")
    return file_name_now

# ----------------------------
# Find the right port through the list of the raspberry ports.
# Return the name of the USB port.

def recup_port_USB() :
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'USB' in p.description :
            port_com = p[0]
            return port_com

# ----------------------------
# Send a command to the arduin0. This will start the arduino script (actually the script runs but wait for an input)

def send_command(serial_command):
    start_command =  ' '
    serial_command.write(start_command.encode())

# ----------------------------
# Decode and split the serial output.
# Split the name of the measurement and the value by finding the 'space' between them.
# If the value is missing it is replace by a None value.

def recover_arduino_data(serial_command):
    response_arduino = serial_command.readline()
    print("Response Arduino : ", response_arduino)
    
    if response_arduino.decode('latin-1') is not None:
        
        response = response_arduino.decode('latin-1')
        #check_arduino_data(response)
        
        if response.count(' ') != None and response.count(' ') == 1 and len(response) > 4:
            indice = response.find(' ')
            response_list = [response[:indice], response[indice:]]
            if response_list[1] == ' \r\n':
                response_list[1] = None
            return response_list
            
    else : 
        print("Error")
        response_arduino.decode()
        response_list = [Error ,0] 
        return response_list
    


# ----------------------------
# Verification of Arduino's response
# Used for debbuging purpose, not used in the final script.

def check_arduino_data(response_arduino):
    premiere_partie = ''
    autre_partie = ''
    index_espace = response_arduino.find(' ')
    if index_espace != -1:
        premiere_partie = response_arduino[:index_espace]
        autre_partie = response_arduino[index_espace+1:]
    else:
        premiere_partie = response_arduino
        autre_partie = ""

    print("Première partie :", premiere_partie)
    print("Autre partie :", autre_partie)
    
    

    #if not premiere_partie.isalpha():
    #    print("erreur première partie ", premiere_partie)
    #    premiere_partie = ''
    #if not autre_partie.isdigit():
    #    print("erreur autre partie ", autre_partie)
    #    autre_partie = ''


# ----------------------------
# Store the cleared serial output in a dictionnary.

def data_to_dict(data, data_base):
    key = data[0]
    if key in data_base:
        try:
            integer = float(data[1])
            data_base[data[0]].append(integer)
                
        except ValueError:
            if data[1] is None:
                none_type = data[1]
                data_base[data[0]].append(none_type)
        
                
                



# ----------------------------
# Return an indicator if the arduino has begun the script.


def find_start(donnee):
    if donnee == None :
        donnee = ['seting' , 0]
    if donnee[0] == 'Start':
        return 1

# ----------------------------
# Compute the real time and the measurement time of the sample.

def time_(liste_temps_mesure):
    tempsmes = time.time()
    liste_temps_mesure.append(tempsmes) # temps mesuré "brut" stocké dans une liste
    tempsreel = tempsmes - liste_temps_mesure[0]
    return tempsmes, tempsreel

# ----------------------------
# Add the measurment time and the real time to the dictionnary.

def time_to_dict(data, data_base):
    data_base["Temps_mesure"].append(data[0])
    data_base["Temps_reel"].append(data[1])


# ----------------------------
# In case the dictionnary isn't uniform it returns the smalest set of data.

def size_dict_uniform(data_base):
    list_len = []
    
    for keys in data_base.keys():
        len = 0
        array = data_base[keys]
        for i in array:
            len = len + 1
        list_len.append(len)
        
    return int(np.min(list_len))
        
    

# ----------------------------
# Send and recover the serial arduino. If the serial output is 'start' we recover the time of the sample.
# We run the script X times per backup time.
# We graduatly store those data in a dictionnary.
# Once the data fully recover, we create .txt and .csv files and write the data base.


def data_five_sensors(serial_command, file_name_now, data_base, countloop, liste_temps_mesure):

    lines_txt = [] 

    send_command(serial_command)
    donnee = recover_arduino_data(serial_command)
    print(donnee)

    if donnee == None :
        donnee = ['seting' , 0]
    while(donnee[0] != 'Start'):
        send_command(serial_command)
        donnee = recover_arduino_data(serial_command)
        if donnee == None :
            donnee = ['seting' , 0]

    while(countloop >= 0):
        

        send_command(serial_command)
        donnee = recover_arduino_data(serial_command)
        if donnee == None :
            donnee = ['seting' , 0]
        print("Decoded data : ", donnee)
        
        
        if find_start(donnee) == 1:
            countloop -= 1
            tempsreel = time_(liste_temps_mesure)
            time_to_dict(tempsreel, data_base)
            line = str(tempsreel[0]) +'\t'+ str(tempsreel[1]) +'\t'
            lines_txt.append(line)
        else:
        
            data_to_dict(donnee, data_base)
            
            line = str(donnee)+'\n'
            lines_txt.append(line)

    minim = size_dict_uniform(data_base)
    
    print("Data base : " , data_base)
    print("Data base cut to minimum : " , minim)

    # Create and write in the txt file:
    with open(desk_path + "/Farmbot/data_farmbot_" + file_name_now + ".txt", 'w') as f: 
            for key, value in data_base.items(): 
                f.write('%s:%s\n' % (key, value))


    # Create and write in the csv file. Csv file is written in a specific structure to simplify the communication with the pandas library later on.
    with open(desk_path + '/Farmbot/data_farmbot_' + file_name_now + '.csv', mode='w', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(data_base.keys())
        row = []

        for values in range(minim):
            row = [data_base[key][values] for key in data_base.keys()]
            
            writer.writerow(row)
            


# ----------------------------
# Authorization and authentication to google drive
# Create a folder in google drive if it is not already done.
# Find the files in the OS that have the right name.
# Upload them in the right folder in google drive.
# Note: The main structure of the function 'drive_upload' is highly inspired by NeuralNine (https://www.youtube.com/watch?v=fkWM7A-MxR0) 

def drive_upload(file_name_now):

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

        # Check if there is the Farmbot_sensor_data folder in google drive.
        response = service.files().list(
            q = "name='Farmbot_sensor_data' and mimeType='application/vnd.google-apps.folder' ", # We verify that is a google folder and not a file.
            spaces='drive'
        ).execute() # Gives us the informations of the folder in our drive.

        
        # If there is no files.
        if not response['files']: 
            file_metadata = {  # We create a dictionnary with the name and the type of Farmbot_sensor_data.
                "name": "Farmbot_sensor_data",
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
        
        for file in os.listdir(desk_path + '/Farmbot'):
            
            
            # Upload the txt file.
            if file == 'data_farmbot_' + file_name_now + '.txt':
                
                file_metadata = {
                    "name": file,
                    "parents": [folder_id]  # We give the dictionnary the folder id OF THE DRIVE FOLDER.

                }
                

                # We create a mediafile.
                media = MediaFileUpload(f"" + desk_path + "/Farmbot/" + file)
                

                # We create the file in the drive based on the OS file.
                upload_file = service.files().create(body=file_metadata, media_body = media, fields = "id").execute()

                
            # Upload the csv file.
            if file == 'data_farmbot_' + file_name_now + '.csv':
                
                file_metadata = {
                    "name": file,
                    "parents": [folder_id]  # We give the dictionnary the folder id OF THE DRIVE FOLDER.

                }

                # We create a mediafile.
                media = MediaFileUpload(f"" + desk_path + "/Farmbot/" + file)
                

                # We create the file in the drive based on the OS file.
                upload_file = service.files().create(body=file_metadata, media_body = media, fields = "id").execute()

        print("Backed up files")

    # In case we have error, we print them.
    except HttpError as e:
        print("Error: " + str(e))

