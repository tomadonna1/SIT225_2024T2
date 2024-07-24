import sys
import traceback
import random
from arduino_iot_cloud import ArduinoCloudClient
import asyncio
from datetime import datetime
import os

DEVICE_ID = "912ead58-1ded-4c28-ab34-5ae0350d52e2"
SECRET_KEY = "vGkeQIQVVUBZe2wDEj2#U3VFB"

# Direct path to save the csv
filename = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 3 - Arduino IoT cloud\Activity_week_3', 'random_temp.csv')

# Function to get the current time
def timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')

# Callback function on temperature change event.
def on_temperature_changed(client, value):
    # String to save data
    formatted_data = f"{timestamp()}, {value}"
    
    # Add to csv file
    try:
        with open(filename, 'a') as file:
            file.write(formatted_data + '\n')
            file.flush()
        print(f"{formatted_data}") # print to terminal
    except Exception as e:
        print(f"Error in writing to csv: {e}")


def main():
    print("main() function")

    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register with 'temperature' cloud variable
    # and listen on its value changes in 'on_temperature_changed'
    # callback function.
    # 
    client.register(
        "temperature", value=None, 
        on_write=on_temperature_changed)

    # start cloud client
    client.start()


if __name__ == "__main__":
    try:
        main()  # main function which runs in an internal infinite loop
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_type, file=print)