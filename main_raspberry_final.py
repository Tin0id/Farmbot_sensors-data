# Farmbot project 2023, Sensors & UI, Vincente Galdini
# main_raspberry_final.py
# Final version on Raspberry Pi.
# Main code that runs functions_raspberry.py and functions_mean.py

#---------------------------------------------
# Import function file.
import functions_raspberry
import functions_mean


# Serial communication
import serial
import serial.tools.list_ports 

# Time library
import time

#---------------------------------------------
# Define backup parameters:
global backup_time
backup_time = 30

global sample_number
sample_number = 12

global day_now
day_now = 0

# ----------------------------
# Initialisation of constants for the serial communication.

global baud 
baud = 9600
global delay_time_out
delay_time_out = 3

# ----------------------------
# Main

while True:
    start_time = time.time()
    data_base = {

    "Temps_reel" : [],
    "Temps_mesure" : [],
    "Temp_bme" : [],
    "Pressure_bme" : [],
    "Altitude_bme" : [],
    "Humidity" : [],
    "IR" : [],
    "VISIBLE" : [],
    "UV" : [],
    "Water" : [],
    "CO2" : [],
    "Temp_co2" : [],
    "Humidity_co2" : [],
    "O2" : []

    }

    liste_temps_mesure =[] 

    port_com = functions_raspberry.recup_port_USB()
    port_com = '/dev/ttyACM0'
    serial_command = serial.Serial()
    serial_command.port = port_com
    serial_command.baudrate = baud
    serial_command.timeout = delay_time_out
    serial_command.open()

    file_name_now = functions_raspberry.give_file_name_now()
    functions_raspberry.data_five_sensors(serial_command, file_name_now, data_base, sample_number, liste_temps_mesure)
    functions_raspberry.drive_upload(file_name_now)
    serial_command.close()

    check_date = day_now
    print("Day of last script execution : ", day_now)
    day_now, day_yest = functions_mean.give_time_now()
    print("Today : ", day_now)

    if check_date != day_now :
        
        from_date = int(day_yest + '000000')
        to_date = int(day_now + '000000')

        creds = functions_mean.authorization_authentication()
        functions_mean.access_API(creds, from_date, to_date, day_yest)
        functions_mean.txt_to_csv(day_yest)

        time.sleep(2)

        functions_mean.drive_upload(day_yest)

    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time [sec]: " , execution_time)
    print("Backup time [min] : " , backup_time)
    
    if execution_time < backup_time * 60 :
        time.sleep(backup_time * 60 - execution_time)
    