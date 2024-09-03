import sys
import traceback
import random
from arduino_iot_cloud import ArduinoCloudClient
import asyncio
from datetime import datetime
import os
import csv

DEVICE_ID = "912ead58-1ded-4c28-ab34-5ae0350d52e2"
SECRET_KEY = "vGkeQIQVVUBZe2wDEj2#U3VFB"

# Direct path to save the csv
filename = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.1P\act8_2', '8_2_data.csv')

# Write headers to csv
if not os.path.exists(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "accelerometer_X", "accelerometer_Y", "accelerometer_Z"])

# Callback function on value change event.
def on_X_changed(client, value):
    print(f"accelerometer_X: {value}")
    save_data_to_csv(value, 'X')
    
def on_Y_changed(client, value):
    print(f"accelerometer_Y: {value}")
    save_data_to_csv(value, 'Y')
    
def on_Z_changed(client, value):
    print(f"accelerometer_Z: {value}")
    save_data_to_csv(value, 'Z')

def save_data_to_csv(value, axis):
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Prepare the data row to append to the CSV
    row = {"X": [timestamp, value, None, None],
           "Y": [timestamp, None, value, None],
           "Z": [timestamp, None, None, value]}
    
    # Append the data row to the CSV file
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row[axis])

def main():
    print("main() function")
    
    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register with values cloud variable
    # and listen on its value changes in 'on_value_changed'
    # callback function.
    # 
    client.register(
        "accelerometer_X", value=None, 
        on_write=on_X_changed)
    
    client.register(
        "accelerometer_Y", value=None, 
        on_write=on_Y_changed)
    
    client.register(
        "accelerometer_Z", value=None, 
        on_write=on_Z_changed)



    # start cloud client
    client.start()


if __name__ == "__main__":
    try:
        main()  # main function which runs in an internal infinite loop
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_type, file=print)