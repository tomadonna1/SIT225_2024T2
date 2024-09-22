import time  
import numpy as np 
import pandas as pd  
import plotly.express as px 
import streamlit as st   
from typing import List, Dict, Union

class AccelerometerAPI:
    def __init__(self, csv_path: str, update_interval: int = 5):
        """Initialize the API with the CSV file path and update interval"""
        self.csv_path = csv_path
        self.update_interval = update_interval
        self.N = 200 # Default number of samples to display
        self.data = pd.DataFrame()  # Empty DataFrame to start
    
    def get_data(self) -> pd.DataFrame:
        """Read accelerometer data from CSV file and handle live updates."""
        data = pd.read_csv(self.csv_path, header=None, names=['Timestamp', 'x', 'y', 'z'])
        data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y%m%d%H%M%S')
        return data
    
    def update_dashboard(self):
        """Function to continuously update the dashboard with live data"""
        
        # Set up Streamlit page config
        st.set_page_config(
            page_title="Accelerometer Dashboard",
            page_icon="✅",
            layout="wide",
        )

        st.title("Accelerometer Dashboard")
        
        # Chart and axis selection
        chart_type = st.selectbox("Select chart type", ["Line Chart", "Scatter Plot", "Distribution Plot"])
        axes_options = st.multiselect("Select axis to plot", options=["x", "y", "z"], default=["x", "y", "z"])
        N = st.number_input("Enter number of samples to display", min_value=1, max_value=1000, value=self.N)
        
        # Placeholder for chart and table
        place_holder = st.empty()
        
        while True:
            self.data = self.get_data()  # get live update from CSV
            
            # Determine the subset of data to display
            start_index = max(0, len(self.data) - N)
            df_subset = self.data.iloc[start_index:]

            # Container that organizes the chart and table
            with place_holder.container():
                # Chart update
                col_chart, col_data = st.columns(2)
                if axes_options: # generate chart based on what user selected
                    with col_chart:
                        if chart_type == "Line Chart":
                            fig = px.line(df_subset, x='Timestamp', y=axes_options, title="Accelerometer Data - Line Chart")
                        elif chart_type == "Scatter Plot":
                            fig = px.scatter(df_subset, x='Timestamp', y=axes_options, title="Accelerometer Data - Scatter Plot")
                        elif chart_type == "Distribution Plot":
                            fig = px.histogram(df_subset.melt(id_vars="Timestamp", value_vars=axes_options),
                                               x='value', color='variable', barmode='overlay', 
                                               title="Accelerometer Data - Distribution Plot")
                        st.write(fig)
                        
                    # Data table update
                    with col_data:
                        st.markdown(f"Latest data from rows {start_index} to {len(self.data)}")
                        st.dataframe(df_subset[['Timestamp'] + axes_options])
                else:
                    st.write("Please select at least one axis to display the chart.")
                
        
                time.sleep(self.update_interval)
                st.rerun()  # This forces the Streamlit app to refresh the data

# Usage
if __name__ == "__main__":
    api = AccelerometerAPI(csv_path=r'C:\Users\tomde\OneDrive\Documents\Deakin uni\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 6 - Visualisation - Plotly data dashboard\6.2HD\data_gathering\data.csv')
    api.update_dashboard()
