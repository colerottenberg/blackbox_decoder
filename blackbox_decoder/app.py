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
    def __init__(self, flight_record: FlightRecord):
        super().__init__()
        self.setWindowTitle("Flight Data")
        self.setAutoFillBackground(True)

        # Setting size to the entire screen
        # Get the screen resolution
        screen = QGuiApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        self.setGeometry(0, 0, screen_rect.width(), screen_rect.height())

        df = flight_record.to_dataframe()

        layout = QVBoxLayout()

        # Adding the Flight Record Canvas
        self.flight_record_canvas = FlightRecordCanvas()

        # Adding the Navigation Toolbar
        toolbar = NavigationToolbar(self.flight_record_canvas, self)

        # Adding the widgets to the layout
        layout.addWidget(toolbar)
        layout.addWidget(self.flight_record_canvas)

        # Plotting the data
        # Voltage Plot
        df.plot(
            x="recNumb",
            y="outVoltX10Avg",
            ax=self.flight_record_canvas.ax1,
            label="outVoltX10Avg",
        )
        df.plot(
            x="recNumb",
            y="outVoltX10Peak",
            ax=self.flight_record_canvas.ax1,
            label="outVoltX10Peak",
        )
        df.plot(
            x="recNumb",
            y="tethVoltX10Avg",
            ax=self.flight_record_canvas.ax1,
            label="tethVoltX10Avg",
        )
        df.plot(
            x="recNumb",
            y="tethVoltX10Peak",
            ax=self.flight_record_canvas.ax1,
            label="tethVoltX10Peak",
        )
        df.plot(
            x="recNumb",
            y="battVoltX10Avg",
            ax=self.flight_record_canvas.ax1,
            label="battVoltX10Avg",
        )
        df.plot(
            x="recNumb",
            y="battVoltX10Peak",
            ax=self.flight_record_canvas.ax1,
            label="battVoltX10Peak",
        )

        # Current Plot
        df.plot(
            x="recNumb",
            y="tethCurrentX10Avg",
            ax=self.flight_record_canvas.ax2,
            label="tethCurrentX10Avg",
        )
        df.plot(
            x="recNumb",
            y="tethCurrentX10Peak",
            ax=self.flight_record_canvas.ax2,
            label="tethCurrentX10Peak",
        )

        # Tether Flags Plot
        # These are discrete values of 0 or 1 and we can treat them as a step plot to show when the flags are on or off
        df.plot(
            x="recNumb",
            y="tethReady",
            ax=self.flight_record_canvas.ax3,
            label="tethReady",
            drawstyle="steps-post",
        )
        df.plot(
            x="recNumb",
            y="tethActive",
            ax=self.flight_record_canvas.ax3,
            label="tethActive",
            drawstyle="steps-post",
        )
        df.plot(
            x="recNumb",
            y="tethGood",
            ax=self.flight_record_canvas.ax3,
            label="tethGood",
            drawstyle="steps-post",
        )
        df.plot(
            x="recNumb",
            y="tethOn",
            ax=self.flight_record_canvas.ax3,
            label="tethOn",
            drawstyle="steps-post",
        )

        # Battery Flags Plot
        # These are discrete values of 0 or 1 and we can treat them as a step plot to show when the flags are on or off
        df.plot(
            x="recNumb",
            y="battOn",
            ax=self.flight_record_canvas.ax4,
            label="battOn",
            drawstyle="steps-post",
        )
        df.plot(
            x="recNumb",
            y="battDrain",
            ax=self.flight_record_canvas.ax4,
            label="battDrain",
            drawstyle="steps-post",
        )
        df.plot(
            x="recNumb",
            y="battKill",
            ax=self.flight_record_canvas.ax4,
            label="battKill",
            drawstyle="steps-post",
        )

        # Setting the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("BlackBox")
        self.setAutoFillBackground(True)

        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Adding the Plot Window
        self.plot_window: PlotWindow = None
        self.flight_record = None
        self.file_name = None

        # Creating the widgets
        self.browse_button = QPushButton("Browse")
        self.decode_button = QPushButton("Decode")
        self.file_path = QLabel("No file selected")

        # Adding the widgets to the layout
        button_layout.addWidget(self.browse_button)
        button_layout.addWidget(self.decode_button)
        pagelayout.addWidget(self.file_path)
        pagelayout.addLayout(button_layout)

        # Describing the actions of the buttons
        # Open File Dialog
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.decode_button.clicked.connect(self.decode_log_file)

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
        if self.plot_window is None:
            self.plot_window = PlotWindow(self.flight_record)
        self.plot_window.show()

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
            self.file_path.setText(file_name)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
