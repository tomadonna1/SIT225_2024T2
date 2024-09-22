from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource, DataTable, TableColumn, Select, TextInput,
    Button, CheckboxGroup
)
from bokeh.plotting import figure
import pandas as pd
import numpy as np
from typing import List, Dict, Union

class AccelerometerDataApp:
    def __init__(self, data_path: str):
        """Initiate the application with a csv file path

        Args:
            data_path (str): path to csv for the accelerometer data
        """
        self.data_path = data_path
        self.N = 100  # Initial number of samples to display
        self.df = self.get_data()
        self.current_start = max(0, len(self.df) - self.N)
        self.last_navigated = False  # Track if user navigated

        self.axis_options = ['x', 'y', 'z']
        self.axis_colors = {'x': 'blue', 'y': 'green', 'z': 'red'}
        self.selected_axes = ['x', 'y', 'z']  # Default axes selected

        # Initialize ColumnDataSource
        self.source = ColumnDataSource(
            self.df.iloc[self.current_start:self.current_start + self.N][['Timestamp'] + self.selected_axes]
        )

        # Initialize DataTable
        self.columns = self.get_table_columns(self.selected_axes)
        self.data_table = DataTable(source=self.source, columns=self.columns, width=700, height=280)

        # Initialize Figure
        self.p = figure(x_axis_type="datetime", title="Accelerometer Data", height=400, width=700)

        # Initialize Widgets
        self.graph_type = Select(
            title="Select graph type",
            value="Line",
            options=["Line", "Scatter", "Distribution"]
        )
        self.sample_input = TextInput(title="Number of samples to display", value=str(self.N))
        self.prev_button = Button(label="Previous", button_type="success")
        self.next_button = Button(label="Next", button_type="success")
        self.axis_selection = CheckboxGroup(labels=self.axis_options, active=[0, 1, 2])

        # Create Layout
        self.layout = self.create_layout()

        # Attach Callbacks
        self.graph_type.on_change('value', self.on_graph_type_change)
        self.sample_input.on_change('value', self.on_sample_input_change)
        self.prev_button.on_click(self.on_prev_button_click)
        self.next_button.on_click(self.on_next_button_click)
        self.axis_selection.on_change('active', self.on_axis_selection_change)

        # Initial Graph Rendering
        self.update_graph_type()

        # Add Layout to Document
        curdoc().add_root(self.layout)

        # Periodic Callback to update data every 2 seconds (update continuously for 2s) 
        curdoc().add_periodic_callback(self.periodic_update, 2000)

    def get_data(self) -> pd.DataFrame:
        """Read data from csv

        Returns:
            pd.DataFrame: dataframe containing accelerometer data
        """
        data = pd.read_csv(
            self.data_path,
            header=None,
            names=['Timestamp', 'x', 'y', 'z'],
            parse_dates=['Timestamp']
        )
        return data

    def get_table_columns(self, selected_axes) -> List[TableColumn]:
        """Generate table columns for the DataTable based on the selected axes

        Args:
            selected_axes (_type_): list of current selected axes

        Returns:
            List[TableColumn]: list of TableColumn objects for the DataTable
        """
        columns = [TableColumn(field="Timestamp", title="Timestamp")]
        for axis in selected_axes:
            columns.append(TableColumn(field=axis, title=axis.upper()))
        return columns

    def cubic_ease_out(self, t: float, b: Union[float, np.array], c: Union[float, np.array], d: float) -> Union[float, np.array]:
        """Cubic easing for smooth transactions between data updates

        Args:
            t (float): current time step
            b (Union[float, np.array]): starting value
            c (Union[float, np.array]): change in value
            d (float): duration of the transition

        Returns:
            Union[float, np.array]: the eased value at time t
        """
        t = t / d - 1
        return c * (t ** 3 + 1) + b

    def interpolate_data(self, current: Dict[str, np.ndarray], new: Dict[str, np.ndarray], steps: int = 10) -> List[Dict[str, np.ndarray]]:
        """Interpolate data points between current and new data via cubic easing

        Args:
            current (Dict[str, np.ndarray]): current data (x,y,z)
            new (Dict[str, np.ndarray]): new data (x,y,z)
            steps (int, optional): number of interpolation steps. Defaults to 10.

        Returns:
            List[Dict[str, np.ndarray]]: list of interpolated data dictionaries at each step
        """
        interpolated = []
        for i in range(steps):
            progress = i / steps
            interpolated_step = {}
            for axis in current.keys():
                interpolated_step[axis] = self.cubic_ease_out(
                    progress,
                    current[axis],
                    new[axis] - current[axis],
                    1
                )
            interpolated.append(interpolated_step)
        return interpolated

    def create_layout(self):
        """Create layout for the app with widgets, plots, and tables

        Returns:
            _type_: the layout with its components
        """
        return column(
            row(self.graph_type, self.sample_input),
            self.axis_selection,
            self.p,
            row(self.prev_button, self.next_button),
            self.data_table
        )

    def update_graph_type(self):
        """Update plot based on selected graph type (line, scatter, distribution)
        """
        self.p.renderers = []  # Clear existing glyphs

        if self.graph_type.value == "Line":
            for axis in self.selected_axes:
                self.p.line(
                    x='Timestamp',
                    y=axis,
                    source=self.source,
                    line_width=2,
                    color=self.axis_colors[axis],
                    legend_label=f"{axis.upper()}-axis"
                )
        elif self.graph_type.value == "Scatter":
            for axis in self.selected_axes:
                self.p.scatter(
                    x='Timestamp',
                    y=axis,
                    source=self.source,
                    size=7,
                    color=self.axis_colors[axis],
                    legend_label=f"{axis.upper()}-axis"
                )
        elif self.graph_type.value == "Distribution":
            for axis in self.selected_axes:
                hist, edges = np.histogram(
                    self.df[axis].iloc[self.current_start:self.current_start + self.N],
                    bins=30
                )
                self.p.quad(
                    top=hist,
                    bottom=0,
                    left=edges[:-1],
                    right=edges[1:],
                    fill_color=self.axis_colors[axis],
                    line_color=self.axis_colors[axis],
                    alpha=0.5,
                    legend_label=f"{axis.upper()}-axis"
                )

        self.p.legend.location = 'bottom_left'
        self.p.legend.click_policy = "hide"

    def update_data(self):
        """Update the data source and apply interpolation when data is updated
        """
        self.df = self.get_data()

        if not self.last_navigated:
            self.current_start = max(0, len(self.df) - self.N)

        new_data_slice = self.df.iloc[self.current_start:self.current_start + self.N]
        timestamps = new_data_slice['Timestamp'].values

        if not self.selected_axes:
            # If no axes are selected, update only the Timestamp
            self.source.data = {'Timestamp': timestamps}
            self.data_table.columns = self.get_table_columns(self.selected_axes)
            self.update_graph_type()
            self.last_navigated = False  # Reset navigation flag
            return

        # Get the current and new data slices
        current_data = {axis: np.array(self.source.data[axis]) for axis in self.selected_axes}
        new_data = {axis: np.array(new_data_slice[axis]) for axis in self.selected_axes}

        # Determine the minimum length
        min_length = min(len(current_data[self.selected_axes[0]]), len(new_data[self.selected_axes[0]]))

        # Trim data to the minimum length
        for axis in self.selected_axes:
            current_data[axis] = current_data[axis][:min_length]
            new_data[axis] = new_data[axis][:min_length]
        timestamps = timestamps[:min_length]

        # Interpolate data over 10 steps
        interpolated_steps = self.interpolate_data(current_data, new_data, steps=10)

        # Apply the interpolation over time
        def apply_interpolation(step=0):
            if step < len(interpolated_steps):
                data = {'Timestamp': timestamps}
                for axis in self.selected_axes:
                    data[axis] = interpolated_steps[step][axis]
                self.source.data = data
                curdoc().add_timeout_callback(lambda: apply_interpolation(step + 1), 100)  # 100ms delay
            else:
                # Ensure the final data is set correctly
                data = {'Timestamp': timestamps}
                for axis in self.selected_axes:
                    data[axis] = new_data[axis]
                self.source.data = data

        apply_interpolation()

        # Update the table columns
        self.data_table.columns = self.get_table_columns(self.selected_axes)

        # Update the plot
        self.update_graph_type()

        self.last_navigated = False  # Reset navigation flag

    def on_graph_type_change(self, attr, old, new):
        """Callback for when is graph type is changed

        Args:
            attr (_type_): the attribute that changed
            old (_type_): the old value of the attribute
            new (_type_): the new value of the attribute
        """
        self.update_graph_type()

    def on_sample_input_change(self, attr, old, new):
        """Callbacks for when the number of samples to display changed

        Args:
            attr (_type_): the attribute that changed
            old (_type_): the old value of the attribute
            new (_type_): the new value of the attribute
        """
        try:
            new_N = int(new)
            if new_N <= 0:
                raise ValueError
            self.N = new_N
        except ValueError:
            self.N = 100  # Reset to default if invalid
            self.sample_input.value = str(self.N)
            return  # Exit early to avoid unnecessary updates

        self.current_start = max(0, len(self.df) - self.N)  # Adjust starting point
        self.last_navigated = True  # Indicate user interaction
        self.update_data()  # Refresh data

    def on_prev_button_click(self):
        """Callback for when previous button is clicked
        """
        self.last_navigated = True  # Mark navigation
        self.current_start = max(0, self.current_start - self.N)
        self.update_data()

    def on_next_button_click(self):
        """Callback for when next button is clicked
        """
        self.last_navigated = True  # Mark navigation
        self.current_start = min(len(self.df) - self.N, self.current_start + self.N)
        self.update_data()

    def on_axis_selection_change(self, attr, old, new):
        """Callback when the axes selection changes

        Args:
            attr (_type_): the attribute that changed
            old (_type_): the old value of the attribute
            new (_type_): the new value of the attribute
        """
        self.selected_axes = [self.axis_options[i] for i in self.axis_selection.active]
        if self.selected_axes:
            self.source.data = self.df.iloc[self.current_start:self.current_start + self.N][['Timestamp'] + self.selected_axes].to_dict('list')
        else:
            self.source.data = {'Timestamp': self.df.iloc[self.current_start:self.current_start + self.N]['Timestamp'].values}
        self.data_table.columns = self.get_table_columns(self.selected_axes)
        self.update_graph_type()
        self.last_navigated = True  # Indicate user interaction
        self.update_data()

    def periodic_update(self):
        """Periodic callback to update data every 2 seconds. Continuous data update
        """
        if not self.last_navigated:
            self.update_data()

# Usage
app = AccelerometerDataApp(r'C:\Users\tomde\OneDrive\Documents\Deakin uni\Deakin-Data-Science\T1Y2\SIT225 - Data Capture Technologies\Week 6 - Visualisation - Plotly data dashboard\6.2HD\data_gathering\data.csv')
