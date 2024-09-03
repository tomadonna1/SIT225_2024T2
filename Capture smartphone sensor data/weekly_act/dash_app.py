import sys
import traceback
from arduino_iot_cloud import ArduinoCloudClient
from datetime import datetime
import os
import csv
import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import threading

# Configuration
DEVICE_ID = "912ead58-1ded-4c28-ab34-5ae0350d52e2"
SECRET_KEY = "vGkeQIQVVUBZe2wDEj2#U3VFB"
N = 510  # Number of samples before plotting

filename = os.path.join(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 8 - Using smartphone to capture sensor data\8.1P\weekly_act', '8_2_data.csv')
current_row = {"Timestamp": None, "accelerometer_X": None, "accelerometer_Y": None, "accelerometer_Z": None}

# Buffer for data
incoming_data = []
plot_data = []

# Open the CSV file once and keep it open for writing
csv_file = open(filename, mode='a', newline='')
writer = csv.writer(csv_file)

# Load existing data from csv into `incoming_data` list
def load_existing_data():
    global incoming_data, plot_data
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        incoming_data = df.to_dict('records')
        plot_data = incoming_data.copy()  # Copy existing data to plot_data
        print(f"Loaded {len(incoming_data)} records from {filename}")

# Callback functions on value of change event
def on_X_changed(client, value):
    print(f"py_x: {value}")
    current_row["accelerometer_X"] = value
    current_row["Timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data_to_csv()

def on_Y_changed(client, value):
    print(f"py_y: {value}")
    current_row["accelerometer_Y"] = value
    save_data_to_csv()

def on_Z_changed(client, value):
    print(f"py_z: {value}")
    current_row["accelerometer_Z"] = value
    save_data_to_csv()

# Save to CSV
def save_data_to_csv():
    global current_row, writer, incoming_data, csv_file
    
    if None not in (current_row["accelerometer_X"], current_row["accelerometer_Y"], current_row["accelerometer_Z"]):
        writer.writerow([current_row["Timestamp"], current_row["accelerometer_X"], current_row["accelerometer_Y"], current_row["accelerometer_Z"]])
        csv_file.flush()
        incoming_data.append(current_row.copy())  # Add the current row to the buffer
        plot_data.append(current_row.copy())  # Add the row to plot_data for live updates
        
        # Reset current_row for the next set of values
        current_row["accelerometer_X"] = current_row["accelerometer_Y"] = current_row["accelerometer_Z"] = None

# Dash app
def create_app():
    app = Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id='live-graph'),
        dcc.Interval(
            id='graph-update',
            interval=30000,  # Update every 30s
            n_intervals=0
        )
    ])

    @app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals')])
    def update_graph(n):
        global plot_data
        print(f"Updating graph, plot_data size: {len(plot_data)}")
        if len(plot_data) > 0:
            # Convert plot_data to DataFrame
            df = pd.DataFrame(plot_data)
            
            # Convert 'Timestamp' column to datetime dtype
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['accelerometer_X'], mode='lines', name='X'))
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['accelerometer_Y'], mode='lines', name='Y'))
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['accelerometer_Z'], mode='lines', name='Z'))

            # Customize the layout
            fig.update_layout(
                title="Accelerometer Data Over Time",
                xaxis_title="Timestamp",
                yaxis_title="Acceleration data",
                legend_title="Axis",
                xaxis=dict(
                    tickformat="%H:%M:%S"
                )
            )

            return fig
        else:
            print("Plot data is empty")
            return go.Figure()

    return app

def start_dash():
    app = create_app()
    app.run_server(debug=False)

def main():
    print("Starting data collection...")
    
    # Load existing data from CSV
    load_existing_data()
    
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
        dash_thread = threading.Thread(target=start_dash)
        dash_thread.start()
        main()
        dash_thread.join()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    finally:
        csv_file.close()

