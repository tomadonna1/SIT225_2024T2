from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataTable, TableColumn, Select, TextInput, Button, CheckboxGroup
from bokeh.plotting import figure
import pandas as pd
import numpy as np
from typing import List, Dict, Union

# Read data
def get_data() -> pd.DataFrame:
    data = pd.read_csv(r'C:\Users\tomde\OneDrive\Documents\Deakin\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 6 - Visualisation - Plotly data dashboard\6.2HD\data_gathering\data.csv', 
                       header=None, names=['Timestamp', 'x', 'y', 'z'])
    return data

# Initial data setup
df = get_data()
N = 100  # Number of samples to display
current_start = max(0, len(df) - N)
last_navigated = False  # Track if user navigated

# Axis options
axis_options = ['x', 'y', 'z']
axis_selection = CheckboxGroup(labels=axis_options, active=[0, 1, 2]) 
selected_axes = [axis_options[i] for i in axis_selection.active]
axis_colors = {'x': 'blue', 'y': 'green', 'z': 'red'}

source = ColumnDataSource(df.iloc[current_start:current_start + N][['Timestamp'] + selected_axes])

# Define table columns for the DataTable
def get_table_columns(selected_axes):
    columns = [TableColumn(field="Timestamp", title="Timestamp")]
    for axis in selected_axes:
        columns.append(TableColumn(field=axis, title=axis))
    return columns

columns = get_table_columns(selected_axes)

# Cubic easing function for smooth transition
def cubic_ease_out(t: float, b: Union[float, np.array], c: Union[float, np.array], d: float) -> Union[float, np.array]:
    """Cubic easing function for smooth transition between data updates

    Args:
        t (float): current time
        b (Union[float, np.array]): starting value
        c (Union[float, np.array]): change in value
        d (float): total duration of the transition

    Returns:
        Union[float, np.array]: the eased value at time `t`
    """
    t = t / d - 1
    return c * (t ** 3 + 1) + b

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
    interpolated = [] # empty list to store interpolated data dictionaries
    for i in range(steps): 
        progress = i / steps # normalized progress of the interpolation at the current step
        interpolated_step = {} # empty dictionary to hold interpolated values for each axis
        for axis in current.keys():
            interpolated_step[axis] = cubic_ease_out(progress, current[axis], new[axis] - current[axis], 1)
        interpolated.append(interpolated_step) # append the interpolated values to the list
    return interpolated


# Create the DataTable
data_table = DataTable(source=source, columns=columns, width=700, height=280)

# Create figure
p = figure(x_axis_type="datetime", title="Accelerometer Data", height=400, width=700)

# Create Select widget for graph type
graph_type = Select(title="Select graph type", value="Line", options=["Line", "Scatter", "Distribution"])

# TextInput to select the number of samples to display
sample_input = TextInput(title="Number of samples to display", value=str(N))

# Navigation buttons for previous and next
prev_button = Button(label="Previous", button_type="success")
next_button = Button(label="Next", button_type="success")

# Function to update the plot based on the graph type selection
def update_graph_type():
    p.renderers = [] # Clears existing glyphs from the plot
    if graph_type.value == "Line": # Adds line glyphs to the plot
        for axis in selected_axes:
            p.line(x='Timestamp', y=axis, source=source, line_width=2, color=axis_colors[axis], legend_label=f"{axis}-axis")
        
    elif graph_type.value == "Scatter": # Adds scatter glyphs to the plot
        for axis in selected_axes:
            p.scatter(x='Timestamp', y=axis, source=source, size=7, color=axis_colors[axis], legend_label=f"{axis}-axis")            
        
    elif graph_type.value == "Distribution": # Create histograms for each axis and adds quad glyphs as distributions to the plot
        for axis in selected_axes:
            hist, edges = np.histogram(df[axis].iloc[current_start:current_start + N], bins=30)
            p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color=axis_colors[axis], line_color=axis_colors[axis], alpha=0.5, legend_label=f"{axis}-axis")
    
    p.legend.location = 'bottom_left'

# Attach callback to the Select widget
graph_type.on_change('value', lambda attr, old, new: update_graph_type())

# Function to update the displayed data based on current range
def update_data():
    global current_start, N, df, last_navigated, selected_axes

    # Get the new data
    df = get_data()

    if not last_navigated:  # Check if user has not navigated
        current_start = max(0, len(df) - N)  # Update to display the latest data

    new_data_slice = df.iloc[current_start:current_start + N]
    timestamps = new_data_slice['Timestamp'].values

    if not selected_axes:
        # If no axes are selected, update only the Timestamp
        source.data = {'Timestamp': timestamps}
        data_table.columns = get_table_columns(selected_axes)
        update_graph_type()
        last_navigated = False  # Reset navigation flag
        return

    # Get the current and new data slices
    current_data = {axis: np.array(source.data[axis]) for axis in selected_axes}
    new_data = {axis: np.array(new_data_slice[axis]) for axis in selected_axes}

    # Determine the minimum length
    min_length = min(len(current_data[selected_axes[0]]), len(new_data[selected_axes[0]]))

    # Trim data to the minimum length
    for axis in selected_axes:
        current_data[axis] = current_data[axis][:min_length]
        new_data[axis] = new_data[axis][:min_length]
    timestamps = timestamps[:min_length]

    # Interpolate data over 10 steps
    interpolated_steps = interpolate_data(current_data, new_data, steps=10)

    # Apply the interpolation over time
    def apply_interpolation(step=0):
        if step < len(interpolated_steps):
            # Update data for selected axes and Timestamp
            data = {'Timestamp': timestamps}
            for axis in selected_axes:
                data[axis] = interpolated_steps[step][axis]
            source.data = data
            curdoc().add_timeout_callback(lambda: apply_interpolation(step + 1), 100)  # Delay each step by 100ms
        else:
            # Ensure the final data is set correctly
            data = {'Timestamp': timestamps}
            for axis in selected_axes:
                data[axis] = new_data[axis]
            source.data = data

    apply_interpolation()
    # Update the table columns
    data_table.columns = get_table_columns(selected_axes)
    # Update the plot
    update_graph_type()
    last_navigated = False  # Reset navigation flag
    

# Callback for the Previous button
def prev_samples():
    global current_start, N, last_navigated
    last_navigated = True  # Mark navigation occurred
    current_start = max(0, current_start - N)
    update_data()

# Callback for the Next button
def next_samples():
    global current_start, N, last_navigated
    last_navigated = True  # Mark navigation occurred
    current_start = min(len(df) - N, current_start + N)
    update_data()

# Callback to update the number of samples displayed
def update_samples(attr, old, new):
    global N, current_start, last_navigated
    try:
        N = int(sample_input.value)
    except ValueError:
        N = 100
    current_start = max(0, len(df) - N)
    last_navigated = True 
    update_data()

# Callback to update axes when selection changes
def update_axes(attr, old, new):
    global selected_axes, last_navigated
    selected_axes = [axis_options[i] for i in axis_selection.active]
    
    source.data = df.iloc[current_start:current_start + N][['Timestamp'] + selected_axes].to_dict('list')
    
    data_table.columns = get_table_columns(selected_axes)
    
    update_graph_type()
    last_navigated = True
    update_data()

# Attach callback for navigation buttons, input text box and the axis selection
sample_input.on_change('value', update_samples)
prev_button.on_click(prev_samples)
next_button.on_click(next_samples)
axis_selection.on_change('active', update_axes)

# Layout for Bokeh
layout = column(row(graph_type, sample_input), axis_selection, p, row(prev_button, next_button), data_table)
curdoc().add_root(layout)

# Periodic callback for 2s
def periodic_update():
    global last_navigated
    if not last_navigated:  # Only update if no navigation happened
        update_data()

curdoc().add_periodic_callback(periodic_update, 2000)