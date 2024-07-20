import serial
import time
from datetime import datetime
import os

# Function to get the current time
def timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')

# Serial port and saving csv file in desire destination
ser = serial.Serial('COM4', 9600)
filename = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 2 - Working with Sensors in Arduino\2.1P\temp_humid_record', 'dht22.csv')

try:
    while True:
        # Check if data is waiting in serial buffer
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip() # read data from serial port and decode it
            formatted_data = f"{timestamp()}, {data}"
            
            # Add data to csv file
            with open(filename, 'a') as file:
                file.write(formatted_data + '\n')
                
            print(f"{formatted_data}")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("Forced stop by user.")
    
finally:
    ser.close()
    print("Serial port closed.")