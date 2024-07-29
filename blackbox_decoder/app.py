"""
# BlackBox:
BlackBoX is a flight log decoder for the Blue Vigil Powerboard. It is a tool that allows you to decode the flight log files and keep tracking of previous flight data.
The tool is designed to take in a .log file and: 1. output a CSV for each respective field, 2. output individual flight log graphs, 3. output a summary of the flight data.
The tool uses the the bitstring library to decode the binary data and the matplotlib library to plot the data. the
"""

# Importing the GUI libraries
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QWidget

# Importing plotting libraries
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

# Importing the decoding libraries
from blackbox_decoder.log import *

import datetime
from datetime import timedelta


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)


class FlightRecordCanvas(FigureCanvas):
    """
    The FlighRecordCanvas class is a class that plots the flight record data
    The Figure consists of 4 subplots:
    1. Voltage Plot of: outVoltX10Avg, outVoltX10Peak, tethVoltX10Avg, tethVoltX10Peak, battVoltX10Avg, battVoltX10Peak
    2. Current Plot of: tethCurrentX10Avg, tethCurrentX10Peak
    3. Tether Flags Broken Plot of: tethReady, tethActive, tethGood, tethOn
    4. Battery Flags Broken Plot of: battOn, battDrain, battKill
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)

        # Adding Titles and Labels
        self.ax1.set_title("Voltage Plot")
        self.ax1.set_xlabel("Record Number")
        self.ax1.set_ylabel("Voltage (V)")

        self.ax2.set_title("Current Plot")
        self.ax2.set_xlabel("Record Number")
        self.ax2.set_ylabel("Current (A)")

        self.ax3.set_title("Tether Flags")
        self.ax3.set_xlabel("Record Number")
        self.ax3.set_ylabel("Flag")

        self.ax4.set_title("Battery Flags")
        self.ax4.set_xlabel("Record Number")
        self.ax4.set_ylabel("Flag")

        self.fig.tight_layout()
        super(FlightRecordCanvas, self).__init__(self.fig)
        self.setParent(parent)


class PlotWindow(QMainWindow):
    def __init__(self, flight_record: FlightRecord, flight_number: int = 1):
        super().__init__()
        self.setWindowTitle(f"Flight Record {flight_number}")
        self.setAutoFillBackground(True)

        # Setting size to the entire screen
        # Get the screen resolution
        screen = QGuiApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())

        # TODO: Add a functionality to handle multiple flight records
        df = flight_record.to_dataframe(flight_number-1)

        layout = QVBoxLayout()

        # Adding the Flight Record Canvas
        self.flight_record_canvas = FlightRecordCanvas()

        # Adding the Navigation Toolbar
        toolbar = NavigationToolbar(self.flight_record_canvas, self)

        # Adding the widgets to the layout
        layout.addWidget(toolbar)
        layout.addWidget(self.flight_record_canvas)

        # Plotting the data

        x: str = "entryTimeMsecs"
        voltage: List[str] = [
                "outVoltX10Avg",
                "outVoltX10Peak",
                "tethVoltX10Avg",
                "tethVoltX10Peak",
                "battVoltX10Avg",
                "battVoltX10Peak",
        ]
        for v in voltage:
            df.plot(x=x, y=v, ax=self.flight_record_canvas.ax1, label=v)

        current: List[str] = ["tethCurrentX10Avg", "tethCurrentX10Peak"]
        for c in current:
            df.plot(x=x, y=c, ax=self.flight_record_canvas.ax2, label=c)

        tether_flags: List[str] = ["tethReady", "tethActive", "tethGood", "tethOn"]
        for t in tether_flags:
            df.plot(x=x, y=t, ax=self.flight_record_canvas.ax3, label=t, drawstyle="steps-post")

        battery_flags: List[str] = ["battOn", "battDrain", "battKill"]
        for b in battery_flags:
            df.plot(x=x, y=b, ax=self.flight_record_canvas.ax4, label=b, drawstyle="steps-post")

        # Setting the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


class MainWindow(QMainWindow):
    """
    The MainWindow is the... main window of the application and contains the following design:
    1. A title
    At the bottom of the window, there are two buttons:
    1. Browse Button: Opens a file dialog to select the log file. When the file is selected, and the file is initially decoded, the button will display the file name. If the file does not decode correctly, the button will display an error message.
    If the file is decoded properly, the widgets above will allow for the user to decode the log file in a more advanced manner. allowing for a greater number of options. That can help the user to better understand the data.
    These options and displays include:
    - The number of recorded flights in the log file
    - A checkbox that allows the user to view the data either in separate windows or concatenated into one window.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("BlackBox")
        self.setAutoFillBackground(True)

        # Setting size to a large window
        self.setGeometry(100, 100, 400, 300)

        # Main Layout is a vertical layout
        pagelayout = QVBoxLayout()

        # The button layout is a horizontal layout that sits at the bottom of the window
        button_layout = QHBoxLayout()

        # The summary layout is a vertical layout that sits at the top of the window
        summary_layout = QGridLayout()

        # Setting up the settings widgets
        """
        The settings around decoding the log file are as follows:
        - Choose the number of flights to decode (default is the latest flight)
        - A checkbox to choose whether to decode the log file in a single window or multiple windows
        """
        settings_layout = QGridLayout()

        # Adding the Plot Window
        self.plot_windows: List[PlotWindow] = []

        # Internal Variables
        self.flight_record = None
        self.file_name = None

        self.flight_count: int = 0
        self.num_flights: int = 1;

        # Creating the widgets
        # The browsing and decoding buttons
        self.browse_button = QPushButton("Browse")
        self.decode_button = QPushButton("Decode")

        # The settings widgets
        self.drone_name_label = QLabel("Drone Name:")
        self.drone_name_plc = QLabel("No flight data")

        self.flight_count_label = QLabel("Number of Flights:")
        # Dropdown menu for the number of flights
        self.flight_count_plc = QLabel("No flight data")
        # Adding Flight Times and Labels
        self.flight_times_label = QLabel("Flight Time:")
        self.flight_time: timedelta = timedelta()
        self.flight_time_placeholder = QLabel("No flight data")

        # Settings widgets
        self.checkbox = QCheckBox("Decode Multiple Flights")
        self.num_flights_selector = QSpinBox()
        self.num_flights_selector.setMinimum(1)
        self.num_flights_selector.setMaximum(10)
         


        # Adding the widgets to the layout
        button_layout.addWidget(self.browse_button)
        button_layout.addWidget(self.decode_button)

        # Adding the settings widgets
        summary_layout.addWidget(self.drone_name_label, 0, 0)
        summary_layout.addWidget(self.drone_name_plc, 0, 1)
        summary_layout.addWidget(self.flight_count_label, 1, 0)
        summary_layout.addWidget(self.flight_count_plc, 1, 1)
        summary_layout.addWidget(self.flight_times_label, 2, 0)
        summary_layout.addWidget(self.flight_time_placeholder, 2, 1)

        seperator = QFrame()
        seperator.setFrameShape(QFrame.Shape.HLine)
        seperator.setFrameShadow(QFrame.Shadow.Sunken)
        seperator.setStyleSheet("background-color: black; height: 2px;")

        settings_layout.addWidget(self.checkbox, 0, 0)
        settings_layout.addWidget(self.num_flights_selector, 0, 1)

        pagelayout.addLayout(summary_layout)
        pagelayout.addWidget(seperator)
        pagelayout.addLayout(settings_layout)
        pagelayout.addLayout(button_layout)

        # Describing the actions of the buttons
        # Open File Dialog
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.decode_button.clicked.connect(self.show_plot_window)

        # Setting the layout
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def decode_log_file(self):
        """
        Decodes the lof file and outputs the data into a pandas dataframe
        """
        if not self.file_name:
            QMessageBox.warning(self, "Error", "Please select a log file to decode")
            return
        # Decoding the log file
        self.flight_record = FlightRecord(self.file_name)

        if not self.flight_record:
            QMessageBox.warning(self, "Error", "Error decoding the log file")
            self.browse_button.setText("Browse")
            return
        # Recording the settings and stats of the flight record
        self.flight_count = len(self.flight_record)
        self.flight_time = self.flight_record.get_flight_time()
        self.drone_name: str = self.flight_record.get_drone_name()
        self.show_summary()

    def show_summary(self):
        """
        Shows the summary of the flight record
        """
        if self.flight_record is None:
            QMessageBox.warning(self, "Error", "No flight record to display")
            return

        # Set the flight count and flight time placeholders
        self.drone_name_plc.setText(self.drone_name)
        self.flight_count_plc.setText(str(self.flight_count))
        self.flight_time_placeholder.setText(str(self.flight_time))
    
    def show_plot_window(self):
        """
        Shows the plot windows of however many flights are selected
        """
        if self.flight_record is None:
            QMessageBox.warning(self, "Error", "No flight record to display")
            return
        
        if len(self.plot_windows) > 0:
            for window in self.plot_windows:
                window.close()
            # Clear the plot windows
            self.plot_windows = []

        if self.checkbox.isChecked():
            self.plot_windows = [PlotWindow(self.flight_record, i+1) for i in range(self.num_flights_selector.value())]
        else:
            window = PlotWindow(self.flight_record, self.num_flights_selector.value())
            self.plot_windows = [window]
        for window in self.plot_windows:
            window.show()


    def open_file_dialog(self):
        """
        Opens a file dialog to select the log file
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log)"
        )
        self.file_name = file_name
        # Removing the file path and keeping only the file name
        file_name = file_name.split("/")[-1]
        if file_name:
            self.browse_button.setText(file_name)
        
        # Decoding the log file
        self.decode_log_file()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
