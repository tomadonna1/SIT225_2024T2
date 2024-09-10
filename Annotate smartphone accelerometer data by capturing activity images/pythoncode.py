import os
from monitor import live_monitor
from arduino_iot_cloud import ArduinoCloudClient
import threading
import time

# Configuration
DEVICE_ID = "912ead58-1ded-4c28-ab34-5ae0350d52e2"
SECRET_KEY = "vGkeQIQVVUBZe2wDEj2#U3VFB"
x = y = z = 1.0

# Callback functions on value of change event
def on_X_changed(client, value):
    global x
    x = value
    return x

def on_Y_changed(client, value):
    global y
    y = value
    return y


def on_Z_changed(client, value):
    global z
    z = value
    return z

# Function that returns accelerometer data in dictionary
def get_accelerometer_data() -> dict():
    global x, y, z 
    while x == 1.0 and y == 1.0 and z == 1.0:
        time.sleep(0.1)
    
    # print(f"x: {x}")
    # print(f"y: {y}")
    # print(f"z: {z}")
    
    return {
        "Accelerometer_X": x,
        "Accelerometer_Y": y,
        "Accelerometer_Z": z
    }

# Function to start the monitor
def start_monitor():
    monitor = live_monitor(
        data_function=get_accelerometer_data,
        data_columns=["Accelerometer_X", "Accelerometer_Y", "Accelerometer_Z"],
        update_interval=1000,
        plot_title="Accelerometer Data Monitoring",
        yaxis_title="Accelerometer Linear",
        csv_file=os.path.join(
            r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.3D\test_image\demo', 
            '1.csv'
        ),
        camera_url='http://10.141.10.103:8080/video',
        image_save_dir = r"C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.3D\test_image\demo"
    )
    monitor.start()

# Function to start the Arduino IoT Cloud client
def start_client():
    print("Starting data collection...")

    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Register callbacks
    client.register("accelerometer_X", value=None, on_write=on_X_changed)
    client.register("accelerometer_Y", value=None, on_write=on_Y_changed)
    client.register("accelerometer_Z", value=None, on_write=on_Z_changed)

    # Start the client
    client.start()

if __name__ == "__main__":
    client_thread = threading.Thread(target=start_client)
    monitor_thread = threading.Thread(target=start_monitor)
    
    client_thread.start()
    monitor_thread.start()
    
    client_thread.join()
    monitor_thread.join()