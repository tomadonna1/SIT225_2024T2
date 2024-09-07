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

class live_monitor:
    def __init__(
        self,
        data_function: Callable[[], Dict[str, float]],
        data_columns: List[str],
        update_interval: int = 5000,
        plot_title: str = "Live Data Monitoring",
        yaxis_title: str = "Data Value",
        csv_file: Optional[str] = None
    ) -> None:
        
        """Init a live_monitor object

        Args:
            data_function (Callable[[], Dict[str, float]]): Function that returns a dictionary of continuous data with keys of corresponding columns
            data_columns (List[str]): List of keys expected in the data dictionary from the 'data_function'
            update_interval (int, optional): interval in milliseconds to update the plot. Defaults to 5000.
            plot_title (str, optional): title of the plot. Defaults to "Live Data Monitoring".
            yaxis_title (str, optional): y-axis title for the plot. Defaults to "Data Value".
            csv_file (Optional[str], optional): Optional file path to save continuous data to csv. Defaults to None.
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
        
        self.incoming_data = []
        
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
                    height=700,
                    title=self.plot_title,
                    xaxis_title="Timestamp",
                    yaxis_title=self.yaxis_title,
                    xaxis=dict(tickformat="%H:%M:%S"),
                    transition={
                        'duration': 2000,  # Duration of the transition in milliseconds
                        'easing': 'cubic-in-out'  # Smooth easing function
                    }
                )

                return fig
            else:
                print("Plot data is empty")
                return go.Figure()

        return app
            
    def start_dash(self) -> None:
        """Start the Dash server"""
        print("Starting Dash server...") 
        app = self.create_dash_app()
        app.run_server(debug=False) 
        
    def main(self) -> None:
        """Main loop to fetch data from the 'data_function' and store it"""
        while True:
            
            # Add sleep interval between data updates
            time.sleep(self.update_interval / 1000)  # Convert ms to seconds

            # Get the new data
            new_data = self.data_function()
            new_data['Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Append the new data to the plot data
            self.plot_data.append(new_data)
            
            # Add data to the CSV
            self.save_data_to_csv(new_data)
            
            print(self.plot_data[-1])
            print(f"Loaded {len(self.plot_data)} records from CSV.")
            
            # Load the data
            self.load_csv_data()
            
    
    def start(self) -> None:
        """Start the data monitoring process"""
        dash_thread = threading.Thread(target=self.start_dash)
        dash_thread.start()

        # Start main loop in the current thread
        self.main()
        
    def __del__(self):
        """Ensure that the CSV file is properly closed when the object is closed"""
        if self.csv_file_handle:
            self.csv_file_handle.close()