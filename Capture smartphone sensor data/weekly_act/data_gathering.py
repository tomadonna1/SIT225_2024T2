import sys
import traceback
from arduino_iot_cloud import ArduinoCloudClient
from datetime import datetime
import os
import csv

# Configuration
DEVICE_ID = "912ead58-1ded-4c28-ab34-5ae0350d52e2"
SECRET_KEY = "vGkeQIQVVUBZe2wDEj2#U3VFB"

filename = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.1P\weekly_act', '8_2_data.csv')
current_row = {"Timestamp": None, "X": None, "Y": None, "Z": None}

# Open the CSV file once and keep it open for writing
csv_file = open(filename, mode='a', newline='')
writer = csv.writer(csv_file)

# Write headers if the file is empty
if csv_file.tell() == 0:
    writer.writerow(["Timestamp", "accelerometer_X", "accelerometer_Y", "accelerometer_Z"])

# Callback functions on value change event
def on_X_changed(client, value):
    print(f"py_x: {value}")
    current_row["X"] = value
    current_row["Timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data_to_csv()

def on_Y_changed(client, value):
    print(f"py_y: {value}")
    current_row["Y"] = value
    save_data_to_csv()

def on_Z_changed(client, value):
    print(f"py_z: {value}")
    current_row["Z"] = value
    save_data_to_csv()

# Save to CSV
def save_data_to_csv():
    if None not in (current_row["X"], current_row["Y"], current_row["Z"]):
        writer.writerow([current_row["Timestamp"], current_row["X"], current_row["Y"], current_row["Z"]])
        
        # Reset current_row for the next set of values
        current_row["X"] = current_row["Y"] = current_row["Z"] = None

def main():
    print("Starting data collection...")
    
    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register callbacks
    client.register("py_x", value=None, on_write=on_X_changed)
    client.register("py_y", value=None, on_write=on_Y_changed)
    client.register("py_z", value=None, on_write=on_Z_changed)

    # Start the client
    client.start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    finally:
        csv_file.close()  
