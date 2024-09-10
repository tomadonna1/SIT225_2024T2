import threading
import pandas as pd
import numpy as np
from dash import Dash, dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Optional
import csv
import time
import os 
import cv2

class live_monitor:
    def __init__(
        self,
        data_function: Callable[[], Dict[str, float]],
        data_columns: List[str],
        update_interval: int = 5000,
        plot_title: str = "Live Data Monitoring",
        yaxis_title: str = "Data Value",
        csv_file: Optional[str] = None,
        camera_url: Optional[str] = None,
        image_save_dir: Optional[str] = None
    ) -> None:
        
        """Init a live_monitor object

        Args:
            data_function (Callable[[], Dict[str, float]]): Function that returns a dictionary of continuous data with keys of corresponding columns
            data_columns (List[str]): List of keys expected in the data dictionary from the 'data_function'
            update_interval (int, optional): interval in milliseconds to update the plot. Defaults to 5000.
            plot_title (str, optional): title of the plot. Defaults to "Live Data Monitoring".
            yaxis_title (str, optional): y-axis title for the plot. Defaults to "Data Value".
            csv_file (Optional[str], optional): Optional file path to save continuous data to csv. Defaults to None.
            camera_url (Optional[str], optional): IP camera URL for capturing images. Defaults to None.
            image_save_dir (Optional[str], optional): Directory to save image. Defaults to None.
        """
        self.data_function = data_function
        self.data_columns = data_columns
        self.update_interval = update_interval
        self.plot_title = plot_title
        self.yaxis_title = yaxis_title
        self.csv_file = csv_file
        self.plot_data: List[Dict[str, float]] = []
        self.csv_file_handle = None
        self.writer = None
        self.camera_url = camera_url
        self.camera_cap = None
        self.image_save_dir = image_save_dir
        self.latest_image_path = None
        
        # Initialize camera capture of camera_url is provided
        if self.camera_url:
            self.init_camera()
        
        # If a CSV file is loaded, open and write
        if self.csv_file:
            try:
                self.csv_file_handle = open(csv_file, mode='a', newline='')
                self.writer = csv.writer(self.csv_file_handle)
            
                # Load existing CSV data into self.plot_data
                self.load_csv_data()
            except FileNotFoundError:
                print(f"CSV file {self.csv_file} not found. Starting with empty data.")
                
        else:
            print("No CSV file provided. Running without CSV logging.")
    
    
    def init_camera(self) -> None:
        """Initialize the camera capture from the IP camera URL"""
        self.camera_cap = cv2.VideoCapture(self.camera_url)
        if not self.camera_cap.isOpened():
            print(f"Failed to open camera at {self.camera_url}")
            
    def capture_image(self, sequence_number: int, timestamp: str) -> None:
        """Capture image from the camera, save with the sequence number and timestamp"""
        try:
            if self.camera_cap and self.camera_cap.isOpened():
                ret, frame = self.camera_cap.read()
                if ret:
                    # Rotate and resize the image 
                    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    resized_frame = cv2.resize(rotated_frame, (720, 1280))
                    
                    # Ensure the image save directory exists
                    if not os.path.exists(self.image_save_dir):
                        os.makedirs(self.image_save_dir)
                    
                    # Construct the file path with a proper file name and extension (.jpg)
                    image_filename = os.path.join(
                        self.image_save_dir, f"{sequence_number}_{timestamp.replace(':', '')}.jpg"
                    )
                    
                    # Save the image and check if the operation is successful
                    if cv2.imwrite(image_filename, resized_frame):
                        print(f"Image saved successfully: {image_filename}")
                        self.latest_image_path = image_filename  # Update the latest image path
                    else:
                        print(f"Failed to save image: {image_filename}")
                else:
                    print("Failed to capture image from the camera.")
            else:
                print("Camera is not initialized or not opened.")
        except Exception as e:
            print(f"Exception during image capture: {e}")
    
    def save_data_to_csv(self, row: Dict[str, float]) -> None:
        """Save a row of data to the CSV if provided"""
        if self.csv_file and self.writer:
            # Check if the file is empty and write headers if needed
            if os.path.getsize(self.csv_file) == 0:
                # Write the header row
                headers = ['Timestamp'] + self.data_columns
                self.writer.writerow(headers) 
        
            # Ensure the timestamp is the first item in the row
            timestamp = row.pop('Timestamp')  # Remove the timestamp from the dictionary
            row_data = [timestamp] + [row[col] for col in self.data_columns]  # Put timestamp first
            self.writer.writerow(row_data)
            self.csv_file_handle.flush()
            
            
    def load_csv_data(self) -> None:
        """Load data from CSV into self.plot_data"""
        if self.csv_file:
            try:
                # Check if the file is empty
                if os.path.getsize(self.csv_file) == 0:
                    print(f"CSV file {self.csv_file} is empty. Starting with empty data.")
                    return
                
                df = pd.read_csv(self.csv_file)
                
                # Convert 'Timestamp' column to datetime, if present
                if 'Timestamp' in df.columns:
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                
                # Convert column listed in data_column to numeric
                for col in self.data_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Update self.plot_data by appending loaded data
                if not df.empty:
                    self.plot_data = df.to_dict(orient='records')
                
            except FileNotFoundError:
                print(f"CSV file {self.csv_file} not found. Starting with empty data.")
            except pd.errors.EmptyDataError:
                print(f"CSV file {self.csv_file} is empty. Starting with empty data.")
            
    def create_dash_app(self) -> Dash:
        """Create the Dash app for live monitoring"""
        app = Dash(__name__)
        
        app.layout = html.Div([
            dcc.Graph(id='live-graph'),
            dcc.Interval(id='graph-update', interval=self.update_interval),
            html.Img(id='live-image', src='', style={'width': '25%', 'display': 'block', 'margin': 'auto'}),
        ])
        
        @app.callback(Output('live-graph', 'figure'), [Input('graph-update', 'n_intervals')])
        def update_graph(n: int) -> go.Figure:
            """Updates the graph with new data and applies smoothing."""
            if len(self.plot_data) > 0:
                
                df = pd.DataFrame(self.plot_data)
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

                # Filter data for the past hour
                current_time = datetime.now()
                df = df[df['Timestamp'] >= (current_time - timedelta(hours=1))]

                # Calculate the magnitude of the chosen data column for monitoring
                df['Data'] = np.sqrt(sum(np.square(df[col]) for col in self.data_columns))

                # Create a plot for combined data
                fig = make_subplots(rows=1, cols=1, subplot_titles=["Data magnitude"])
                fig.add_trace(go.Scatter(
                    x=df['Timestamp'], 
                    y=df['Data'], 
                    mode='lines', 
                    name='Data magnitude',
                    line=dict(shape='spline')), row=1, col=1)

                fig.update_layout(
                    height=450,
                    title=self.plot_title,
                    xaxis_title="Timestamp",
                    yaxis_title=self.yaxis_title,
                    xaxis=dict(tickformat="%H:%M:%S"),
                    transition={
                        'duration': 1000,  # Duration of the transition in milliseconds
                        'easing': 'cubic-in-out'  # Smooth easing function
                    }
                )

                return fig
            else:
                print("Plot data is empty")
                return go.Figure()
            
        # Update the image displayed on the dashboard
        @app.callback(
            Output('live-image', 'src'),
            Input('graph-update', 'n_intervals')
        )
        def update_image(n):
            if self.latest_image_path:
                encoded_image = self.encode_image_to_base64(self.latest_image_path)
                return f"data:image/jpeg;base64,{encoded_image}"
            return ''

        return app
    
    def encode_image_to_base64(self, image_path):
        """Encode the saved image to base64 for display on the dashboard."""
        import base64
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
            
    def start_dash(self) -> None:
        """Start the Dash server"""
        print("Starting Dash server...") 
        app = self.create_dash_app()
        app.run_server(debug=False) 
        
    def main(self) -> None:
        """Main loop to fetch data from the 'data_function' and store it"""
        sequence_number = 1
        while True:
            
            # Add sleep interval between data updates
            time.sleep(self.update_interval / 1000)  # Convert ms to seconds

            # Get the new data
            new_data = self.data_function()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            new_data['Timestamp'] = timestamp
            
            # Append the new data to the plot data
            self.plot_data.append(new_data)
            
            # Add data to the CSV
            self.save_data_to_csv(new_data)
            
            # Capture image
            self.capture_image(sequence_number, timestamp)
            
            # print(self.plot_data[-1])
            # print(f"Loaded {len(self.plot_data)} records from CSV.")
            
            # Load the data
            self.load_csv_data()
            
            sequence_number += 1
            
    
    def start(self) -> None:
        """Start the data monitoring process"""
        dash_thread = threading.Thread(target=self.start_dash)
        dash_thread.start()

        # Start main loop in the current thread
        self.main()
        
    def __del__(self):
        """Ensure that the CSV file and camera are properly closed when the object is closed"""
        if self.csv_file_handle:
            self.csv_file_handle.close()
        if self.camera_cap:
            self.camera_cap.release()