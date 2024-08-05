"""
# BlackBox:
"""

# Importing the GUI libraries
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QFileDialog,
    QMessageBox,
    QFrame,
)

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure

# Importing the decoding libraries
from blackbox_decoder.log import FlightRecord, Summary

from datetime import timedelta
from typing import List

# Importing plotting libraries

import matplotlib

matplotlib.use("Qt5Agg")


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)


class FlightRecordCanvas(FigureCanvas):
    """
    The FlighRecordCanvas class is a class that plots the flight record data
    The Figure consists of 8 subplots:
    - Group 1: Rollup Plots
        - Voltage Plot
        - Current Plot
        - Tether Flags
        - Battery Flags
    - Group 2: Detail Plots
        - Voltage Plot
        - Current Plot
        - Tether Flags
        - Battery Flags
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = self.fig.add_subplot(241)
        self.ax2 = self.fig.add_subplot(242)

        # Adding Titles and Labels

        self.ax1.set_title("Voltage Plot")
        self.ax1.set_xlabel("Milliseconds")
        self.ax1.set_ylabel("Voltage (V)")

        self.ax2.set_title("Current Plot")
        self.ax2.set_xlabel("Milliseconds")
        self.ax2.set_ylabel("Current (A)")

        self.fig.tight_layout()
        super(FlightRecordCanvas, self).__init__(self.fig)
        self.setParent(parent)


class PlotWindow(QMainWindow):
    """
    The PlotWindow class is a class that displays the important data of the flight record.

    The PlotWindow class consists of:
    -   Voltage Plot
    -   Current Plot
    -   Tether and Battery Summary

    The Summary of the Battery and Tether Flags display:
    """

    def __init__(self, flight_record: FlightRecord, flight_number: int = 1):
        super().__init__()
        self.setWindowTitle(f"Flight Record {flight_number}")
        self.setAutoFillBackground(True)

        # Setting size to the entire screen
        # Get the screen resolution
        screen = QGuiApplication.primaryScreen()
        screen_rect = (
            screen.availableGeometry()
        )  # I have zero idea why this attribute is not known by pyright.
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())

        df_list = flight_record.to_dataframe(flight_number - 1)
        summary: Summary = flight_record.summary(df_list)
        df = df_list[0]

        # Creating the layout
        layout = QVBoxLayout()

        summary_layout = QGridLayout()
        summary_layout.addWidget(
            QLabel(f"Tether Activity: {summary.tether_activity}"), 0, 0
        )
        summary_layout.addWidget(
            QLabel(f"Battery Activity: {summary.battery_activity}"), 1, 0
        )
        summary_layout.addWidget(QLabel(f"Flight Time: {summary.flight_time}"), 2, 0)
        summary_layout.addWidget(QLabel(f"Switch Count: {summary.switch_count}"), 0, 1)
        summary_layout.addWidget(QLabel(f"Rollup Count: {summary.rollup_count}"), 1, 1)
        summary_layout.addWidget(QLabel(f"Detail Count: {summary.detail_count}"), 2, 1)

        layout.addLayout(summary_layout)

        # Adding the Flight Record Canvas
        self.rollup = FlightRecordCanvas()

        # Adding the Navigation Toolbar
        toolbar = NavigationToolbar(self.rollup, self)

        # Adding the widgets to the layout
        layout.addWidget(toolbar)
        layout.addWidget(self.rollup)

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
            df.plot(x=x, y=v, ax=self.rollup.ax1, label=v)

        current: List[str] = ["tethCurrentX10Avg", "tethCurrentX10Peak"]
        for c in current:
            df.plot(x=x, y=c, ax=self.rollup.ax2, label=c)

        # Detail Plots
        if len(df_list) > 1:
            self.detail = FlightRecordCanvas()
            detail_toolbar = NavigationToolbar(self.detail, self)
            layout.addWidget(detail_toolbar)
            layout.addWidget(self.detail)

            df = df_list[1]
            x = "recNumb"

            voltage: List[str] = [
                "tethVoltX10",
                "battVoltX10",
                "outVoltX10",
            ]
            for v in voltage:
                df.plot(x=x, y=v, ax=self.detail.ax1, label=v)

            current: List[str] = ["tethCurrentX10"]
            for c in current:
                df.plot(x=x, y=c, ax=self.detail.ax2, label=c)

        # Setting the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


class MainWindow(QMainWindow):
    """
    The MainWindow class is the main window of the BlackBox application.
    1. A title
    At the bottom of the window, there are two buttons:
    1. Browse Button:
        1.1 Opens a file dialog to select the log file.
        1.2 When the selected, and the file is initially decoded, the button will display the file name.
        1.3 If the file does not decode correctly, the button will display an error message.
    2. Decode Button:
        2.1 Decodes the log file and displays the summary of the flight record.
        2.2 If the file is not selected, the button will display an err message.
    If the file is decoded properly, the widgets above will allow for the user to decode the log file in a more advanced manner. allowing for a greater number of options. That can help the user to better understand the data.
    These options and displays include:
    - The number of recorded flights in the log file
    - A checkbox of single or multiple flight decoding
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("BlackBox")
        self.setAutoFillBackground(True)

        # Setting size to a large window
        self.setGeometry(100, 100, 400, 300)

        # Main Layout is a vertical layout
        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        summary_layout = QGridLayout()

        # Setting up the settings widgets
        """
        The settings around decoding the log file are as follows:
        - Choose the number of flights to decode (default is the latest flight)
        - A checkbox for single or multiple flight decoding
        """
        settings_layout = QGridLayout()

        # Adding the Plot Window
        self.plot_windows: List[PlotWindow] = []

        # Internal Variables
        self.flight_record: FlightRecord
        self.file_name = None

        self.flight_count: int = 0
        self.num_flights: int = 1

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
            self.plot_windows = [
                PlotWindow(self.flight_record, i + 1)
                for i in range(self.num_flights_selector.value())
            ]
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
