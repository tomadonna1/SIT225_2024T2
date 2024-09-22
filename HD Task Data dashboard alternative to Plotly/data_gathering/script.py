import serial
import time
from datetime import datetime
import os
import pandas as pd

# Function to get the current time
def timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')

# Serial port and saving csv, json file in desire destination
ser = serial.Serial('COM4', 9600)
csv_file = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin uni\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 6 - Visualisation - Plotly data dashboard\6.2HD\data_gathering', 'data.csv')

try:
    while True:
        # Check if data is waiting in serial buffer
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip() # read data from serial port and decode it
            formatted_data = f"{timestamp()}, {data}"
            
            # Add data to csv file
            with open(csv_file, 'a') as file:
                file.write(formatted_data + '\n')
            
            print(f"{formatted_data}")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Forced stop by user.")
    
finally:
    ser.close()
    print("Serial port closed.")