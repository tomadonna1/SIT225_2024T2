import time  
import numpy as np 
import pandas as pd  
import plotly.express as px 
import plotly.graph_objs as go
import streamlit as st   
from datetime import datetime, timedelta
from typing import List, Dict, Union

# basic dashboard setup
st.set_page_config(
    page_title="Accelerometer dashboard",
    page_icon="✅",
    layout="wide",
)

# Function to read data
def get_data() -> pd.DataFrame:
    data = pd.read_csv(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 6 - Visualisation - Plotly data dashboard\6.2HD\data_gathering\data.csv', header=None, names=['Timestamp', 'x', 'y', 'z'])
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%Y%m%d%H%M%S')
    return data

# Cubic easing function for smooth transition
def cubic_ease_out(t: float, b: Union[float, np.array], c: Union[float, np.array], d: float) -> Union[float, np.array]:
    """Cubic easing function for smooth transition between data updates

    Args:
        t (float): current time
        b (Union[float, np.array]): starting value
        c (Union[float, np.array]): change in value
        d (float): total duration of the transition

    Returns:
        Union[float, np.array]: the eased value at time t
    """
    t = t / d - 1
    return c * (pow(t, 3) + 1) + b

# Function to interpolate data using cubic easing
def interpolate_data(current: Dict[str, np.ndarray], new: Dict[str, np.ndarray], steps: int = 10) -> List[Dict[str, np.ndarray]]:
    """ Interpolate data points between current and new data using cubic easing

    Args:
        current (Dict[str, np.ndarray]): current data array x,y,z
        new (Dict[str, np.ndarray]): new data array x,y,z
        steps (int, optional): number of interpolation steps. Defaults to 10.

    Returns:
        List[Dict[str, np.ndarray]]: list of interpolated data dictionaries at each step
    """
    interpolated = []
    for i in range(steps):
        progress = i / steps
        interpolated.append({
            'x': cubic_ease_out(progress, current['x'], new['x'] - current['x'], 1),
            'y': cubic_ease_out(progress, current['y'], new['y'] - current['y'], 1),
            'z': cubic_ease_out(progress, current['z'], new['z'] - current['z'], 1),
        })
    return interpolated

# dashboard title
st.title("Accelerometer dashboard")

# chart selection
chart_type = st.selectbox("Select chart type", ["Line Chart", "Scatter Plot", "Distribution Plot"])

# axis selection
axes_options = st.multiselect("Select axis to plot", options=["x", "y", "z"], default=["x", "y", "z"])

# text box to display the number of samples to display
N = st.number_input("Enter number of samples to display", min_value=1, max_value=len(get_data()), value=200)

#! auto update
# Placeholder for the graph and table
place_holder = st.empty()

# Initialize variables for navigation
start_index = st.session_state.get('start_index', len(get_data())-N+10)
# Navigation buttons for previous and next
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Previous"):
        start_index = max(0, start_index - N)  # Go backward but don't go negative
        st.session_state['start_index'] = start_index

with col2:
    if st.button("Next"):
        start_index = min(len(get_data()) - N, start_index + N)  # Go forward but don't exceed the dataset length
        st.session_state['start_index'] = start_index
        
# End index for slicing
end_index = start_index + N

while True:
    # Get data
    df = get_data()
    
    # Dataframe for plotting 
    df2 = df.iloc[start_index:end_index] # two columns side-by-side for graph and table

    with place_holder.container():
        # Update chart
        col_chart, col_data = st.columns(2)
        if axes_options:
            with col_chart:
                if chart_type == "Line Chart":                    
                    fig = px.line(df2, x='Timestamp', y=axes_options, title="Accelerometer Data - Line Chart")
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df2, x='Timestamp', y=axes_options, title="Accelerometer Data - Scatter Plot")
                elif chart_type == "Distribution Plot":
                    fig = px.histogram(df.melt(id_vars="Timestamp", value_vars=axes_options),
                                    x='value', color='variable', barmode='overlay', 
                                    title="Accelerometer Data - Distribution Plot")
                
                st.write(fig)
                
        else:
            st.write("Please select at least one axis to display the chart.")
            
        # Update dataframe
        with col_data:
            st.markdown("Latest data based on selected data for rows {} to {}".format(start_index, end_index))
            st.dataframe(df2)
            
        time.sleep(2)