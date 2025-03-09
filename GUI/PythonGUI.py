import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import serial
import serial.tools.list_ports
import logging
import os
import csv
from PyQt5.QtGui import QKeyEvent, QIcon, QPixmap, QColor, QFont
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph import PlotWidget
from datetime import datetime
import scipy
import numpy as np 
import pandas as pd
import subprocess
from scipy.signal import butter, filtfilt, find_peaks

home_directory = os.path.expanduser('~')


# Globals
CONN_STATUS = False
BIT_RESOLUTION = 12
CONVERSION = 0.001
G_RESOLUTION = 2
g = 9.81

# Logging config
logging.basicConfig(format="%(message)s", level=logging.INFO)


class TableWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TableWindow, self).__init__(parent)
        self.setWindowTitle('CSV Data')
        self.setGeometry(100, 100, 600, 400)  # Adjust size and position as needed
        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setGeometry(10, 10, 580, 380)  # Adjust size and position as needed
        self.table_widget.show()
        



class SerialWorkerSignals(QtCore.QObject):
    status = QtCore.pyqtSignal(bool)
    new_data = QtCore.pyqtSignal(float)
    connection_notification = QtCore.pyqtSignal(str)


class SerialWorker(QtCore.QThread):
    def __init__(self, serial_port_name):
        super().__init__()
        self.port_name = serial_port_name
        self.signals = SerialWorkerSignals()
        self.port = None
        

    def run(self):
        global CONN_STATUS
        try:
            self.port = serial.Serial(port=self.port_name, baudrate=9600, timeout=2)
            if self.port.is_open:
                CONN_STATUS = True
                self.signals.status.emit(True)
                logging.info(f"Connected to {self.port_name}.")
                self.read_data()
            else:
                CONN_STATUS = False
                self.signals.status.emit(False)
                logging.info(f"Failed to connect to {self.port_name}.")
        except serial.SerialException as e:
            CONN_STATUS = False
            self.signals.status.emit(False)
            logging.error(f"Error connecting to {self.port_name}: {e}")

    def read_data(self):
        while self.port.is_open:
            try:
                tail = self.port.read(1)
                if tail == b'\xC0':
                    data = self.port.read(3)
                    if len(data) < 3:
                        continue  # Handle partial data
                    if(data[0]==0xA0):
                        z_unsigned_int = ((data[2] << 8) | data[1])>>4
                        z_signed = z_unsigned_int - 2 ** BIT_RESOLUTION if z_unsigned_int >= 2 ** (BIT_RESOLUTION - 1) else z_unsigned_int
                        z_conv = round(z_signed * CONVERSION * g,4)
                        self.signals.new_data.emit(z_conv)
                continue
            except Exception as e:
                logging.error(f"Error reading data: {e}")
                break

    def disconnect(self):
        if self.port and self.port.is_open:
            self.port.close()
            logging.info(f"Disconnected from {self.port_name}.")

    def send(self, char):
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.flushOutput()  # Clear the sent characters from the buffer
            self.port.write(char.encode('utf-8') + b'\r\n') 
            logging.info("Written {} on port {}.".format(char, self.port_name))
        except:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))


class ConnectDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connecting...")
        self.setFixedSize(300, 200)
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Attempting to connect...")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 11pt;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

class ConnectionSuccessDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle("Connection Successful")
        self.setText("Connection established successfully.\r\nPress 's' on keyword or File-->Start_Acquisition to retrieve data")
        self.addButton(QtWidgets.QMessageBox.Ok)

    def show_message(self, message):
        self.label.setText(message)

class StreamingMovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []
        self.sum = 0

    def process(self, value):
        self.values.append(value)
        self.sum += value
        if len(self.values) > self.window_size:
            self.sum -= self.values.pop(0)
        return float(self.sum) / len(self.values)

class DataSummaryWindow(QtWidgets.QDialog):
    def __init__(self, data, parent=None):
        super(DataSummaryWindow, self).__init__(parent)
        self.setWindowTitle('Data Summary')
        self.setGeometry(200, 200, 800, 400)
        self.table_widget = QtWidgets.QTableWidget(self)
        self.table_widget.setGeometry(50, 30, 800, 400)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(['Cycle', 'RR (breaths/min)', 'Inspiration Time (s)', 'Expiration Time (s)', 'I/E Ratio'])
        self.load_data(data)
        self.table_widget.show()

    def load_data(self, data):
        self.table_widget.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                self.table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,  username="Guest"):  # Add username as a parameter
        super(MainWindow, self).__init__()
        if len(sys.argv) >= 2:
            self.username = sys.argv[2]
        else:
            self.username = "Guest"

        if len(sys.argv) >= 2:
            self.option = sys.argv[1]
        else:
            self.option = "No Option" 
        self.fs = 200
        self.max_RR_thresh = 20  # Imposta la tua soglia massima desiderata
        self.serial_worker = None
        self.icon = None
        self.data_buffer = []
        self.data_BW_filtered = []
        self.data_MA_filtered =[]
        self.peak_indices = []
        self.min_indices = []
        self.peak_scatter = None
        self.min_scatter = None
        self.last_min_count = 0
        self.last_min_count_insp = 0
        self.last_peak_count = 0
        self.last_min_count_exp = 0
        self.last_ie_count = 0
        self.instant_rrs = []
        self.inspiratory_times = []
        self.expiratory_times = []
        self.ie_ratios = []
        self.threshold_exceeded = False
        self.data_uploaded = False
        self.data_filtered_offline = None
        self.start = time.time()
        self.acquisition_running = False  # Track the state of data acquisition
        self.connection = False
        self.initUI()
        self.serialscan()
        self.threadpool = QtCore.QThreadPool()
        self.connected = CONN_STATUS

         # Initialize the moving average filter with a window size of 10 (try wto change while acquiring data)
        self.moving_average_filter = StreamingMovingAverage(window_size=10)
       
    def initUI(self):
        self.setObjectName("MainWindow")
        self.setFixedSize(1480, 930)
        self.setWindowTitle("B(R)EAT(H)")

        self.plot_mode = 'raw'  # Can be 'filtered' or 'raw'

        button_style_top = """
    QPushButton {{
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: {color};
        min-width: 80px;
        max-width: 200px;
        min-height: 40px;
        max-height: 40px;
        font-weight: bold;
        font-size: 15px;
    }}
    QPushButton:pressed {{
        background-color: {pressed_color};
    }}
    QPushButton:disabled {{
        background-color: #e0e0e0;
        border-color: #a1a1a1;
    }}"""
        
        # Define box_style as an instance variable
        self.box_style = """
QFrame {{
    border: 2px solid #8f8f91;
    border-radius: 6px;
    background-color: #ffffff;
    min-width: 150px;
    min-height: 50px;
}}
QLabel {{
    font-size: 14px;
    color: #000000;
}}
"""
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1480, 26))  # Adjust the width to match the window size
        self.menubar.setObjectName("menubar")

        # adding the file tab
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setTitle("File")

        # actions for file tab
    
        self.actionStart_acquisition = QtWidgets.QAction(self)
        self.actionStart_acquisition.setObjectName("actionStart_acquisition")
        self.actionStart_acquisition.setText("Start Data Acquisition")
        self.actionStart_acquisition.triggered.connect(self.start_acquisition)
        
        self.actionStop_acquisition = QtWidgets.QAction(self)
        self.actionStop_acquisition.setObjectName("actionStop_acquisition")
        self.actionStop_acquisition.setText("Stop Data Acquisition")
        self.actionStop_acquisition.triggered.connect(self.stop_acquisition)
        
        self.actionSave_data = QtWidgets.QAction(self)
        self.actionSave_data.setObjectName("actionSave_data")
        self.actionSave_data.setText("Save Data")
        self.actionSave_data.triggered.connect(self.save_file)

        self.load = QtWidgets.QAction(self)
        self.load.setObjectName("load")
        self.load.setText("Load Data")
        self.load.triggered.connect(self.load_csv_to_table)

        #user label
        self.label_username = QtWidgets.QLabel(self)
        self.label_username.setText(f'Logged in as: {self.username}')
        self.label_username.setFont(QtGui.QFont('Arial', 10))
        self.label_username.setStyleSheet("QLabel { color : black; }")
        self.label_username.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        # Calculate the position for the top right corner
        label_width = self.label_username.sizeHint().width()
        window_width = self.width()
        padding = 8  # Adjust padding as needed
        x_pos = window_width - label_width - padding

        self.label_username.setGeometry(x_pos, padding, label_width, self.label_username.sizeHint().height())
        self.label_username.show()

        # adding the actions to menu bar

        self.menuInfo = QtWidgets.QMenu(self.menubar)
        self.menuInfo.setTitle("?")
        self.actionShow_info = QtWidgets.QAction(self)
        self.actionShow_info.setObjectName("actionShow_info")
        self.actionShow_info.setText("Show Info")
        self.actionShow_info.triggered.connect(self.show_info)

        self.menuInfo.addAction(self.actionShow_info)
        
        self.menuFile.addAction(self.actionStart_acquisition)
        self.menuFile.addAction(self.actionStop_acquisition)
        self.menuFile.addAction(self.actionSave_data)
        self.menuFile.addAction(self.load)
        
        
        # Add the tabs to the menu bar
        self.menubar.addMenu(self.menuFile)
        self.menubar.addMenu(self.menuInfo)

        # Set the menu bar
        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
       

        screen = QtWidgets.QApplication.desktop().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) -250 // 2)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        color = QtGui.QColor(185, 243, 243)
        self.centralwidget.setStyleSheet(f"background-color: {color.name()};")
        self.setCentralWidget(self.centralwidget)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSpacing(10)

        self.horizontalLayout_title = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout_title)

        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily(".SF Arabic Rounded")
        font.setPointSize(20)  # Riduci la dimensione del carattere del titolo
        font.setBold(True)
        font.setWeight(75)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet("color: #00008B; padding: 5px;")
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setText("B(R)EAT(H)")
        self.horizontalLayout_title.addWidget(self.label_title)

        # Reset Button
        self.pushButton_reset = QtWidgets.QPushButton()
        self.pushButton_reset.setText("Reset")
        self.pushButton_reset.clicked.connect(self.reset_graph)
        self.pushButton_reset.setStyleSheet(button_style_top.format(color="#008CBA", pressed_color="#005f6b"))
        self.horizontalLayout_title.addWidget(self.pushButton_reset)

        # Add the button to switch between raw and filtered data
        self.pushButton_switch_plot = QtWidgets.QPushButton()
        self.pushButton_switch_plot.setText("Switch to Filtered Data")
        self.pushButton_switch_plot.clicked.connect(self.switch_plot_mode)
        self.pushButton_switch_plot.setStyleSheet(button_style_top.format(color="#008CBA", pressed_color="#005f6b"))
        self.horizontalLayout_title.addWidget(self.pushButton_switch_plot)



######### DA INSERIRE  QUI FINO A LINEA 367
        self.horizontalLayout_main = QtWidgets.QHBoxLayout()
        self.horizontalLayout_main.setSpacing(20)
        self.verticalLayout.addLayout(self.horizontalLayout_main)

        self.graphicsView = pg.PlotWidget(self.centralwidget)
        self.graphicsView.setMouseEnabled(x=False, y=False)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setBackground('w')
        self.graphicsView.setMaximumSize(1100, 750)
        label_style = {'font-size': '9pt', 'font-weight': 'bold'}
        self.graphicsView.getPlotItem().setLabel('left', 'Acceleration', units='m/s²', **label_style)
        self.graphicsView.getPlotItem().setLabel('bottom', 'Time', units='s', **label_style)
        self.horizontalLayout_main.addWidget(self.graphicsView)

        # Add grid to the plot
        self.graphicsView.getPlotItem().showGrid(x=True, y=True, alpha=0.3)

        self.verticalLayout_data = QtWidgets.QVBoxLayout()
        self.verticalLayout_data.setSpacing(0)
        self.verticalLayout_data.setContentsMargins(0, 0, 0, 0) 
        self.horizontalLayout_main.addLayout(self.verticalLayout_data)

        self.verticalLayout_data.addStretch(0)
        self.verticalLayout_data.addSpacing(50)

        # Creating and adding data labels
        self.rr_box, self.label_respiratory_rate = self.create_param_box("RR:", self.box_style)
        self.verticalLayout_data.addWidget(self.rr_box, alignment=QtCore.Qt.AlignCenter)  
        self.verticalLayout_data.addStretch(0)
        self.verticalLayout_data.addSpacing(50)

        self.inspiration_time_box, self.label_inspiration_time = self.create_param_box("Inspiration Time:", self.box_style)
        self.verticalLayout_data.addWidget(self.inspiration_time_box, alignment=QtCore.Qt.AlignCenter)  

        self.verticalLayout_data.addStretch(0)
        self.verticalLayout_data.addSpacing(50) 

        self.expiration_time_box, self.label_expiration_time = self.create_param_box("Expiration Time:", self.box_style)
        self.verticalLayout_data.addWidget(self.expiration_time_box, alignment=QtCore.Qt.AlignCenter)  

        self.verticalLayout_data.addStretch(0)
        self.verticalLayout_data.addSpacing(50)

        # Aggiungi il nuovo box per il rapporto I/E
        self.ie_ratio_box, self.label_ie_ratio = self.create_param_box("I/E Ratio:", self.box_style)
        self.verticalLayout_data.addWidget(self.ie_ratio_box, alignment=QtCore.Qt.AlignCenter)

        self.verticalLayout_data.addStretch(0)
        self.verticalLayout_data.addSpacing(45)

        self.change_option_img()

        # Creazione del pulsante con l'icona
        self.pushButton_option = QtWidgets.QPushButton()
        self.pushButton_option.setObjectName(f"button")  # Nome univoco per identificare il pulsante
        self.pushButton_option.setFixedSize(200, 150)
        self.pushButton_option.clicked.connect(self.change_option)
        self.pushButton_option.setIcon(self.icon)
        self.pushButton_option.setIconSize(QtCore.QSize(270, 270))
        self.pushButton_option.setFlat(True)  # Rimuove il bordo attorno al pulsante

        # Ensure the button is added to the layout
        self.verticalLayout_data.addWidget(self.pushButton_option, alignment=QtCore.Qt.AlignCenter)

        self.verticalLayout_data.addStretch(1)
        # self.verticalLayout.addSpacing(20)

        self.horizontalLayout_buttons = QtWidgets.QHBoxLayout()
        self.verticalLayout.addLayout(self.horizontalLayout_buttons)

        # Combo box style
        combo_box_style = """
        QComboBox {{
            border: 2px solid #8f8f91; 
            border-radius: 6px; 
            padding: 1px 18px 1px 3px; 
            max-width: 13.4em;
            font-weight: bold;
            font-size: 16px;
            background-color: {background_color};
        }}
        QComboBox:editable {{
            background-color: #ffffff;
        }}
        QComboBox:!editable, QComboBox::drop-down:editable {{
            background: {background_color};
        }}
        /* QComboBox gets the "on" state when the popup is open */
        QComboBox:!editable:on, QComboBox::drop-down:editable:on {{
            background-color: {drop_down_color};
        }}"""

        self.comboBox_serialport = QtWidgets.QComboBox()
        self.horizontalLayout_buttons.addWidget(self.comboBox_serialport)
        self.comboBox_serialport.setStyleSheet(combo_box_style.format(background_color="#f0f0f0", drop_down_color="#f0f0f0"))

        # Add the scan button
        self.pushButton_scan = QtWidgets.QPushButton()
        self.pushButton_scan.setText("Scan")
        self.pushButton_scan.clicked.connect(self.serialscan)
        self.pushButton_scan.setStyleSheet(self.button_style_bot.format(color="#008CBA", pressed_color="#005f6b"))
        self.horizontalLayout_buttons.addWidget(self.pushButton_scan)

        # Add the connect button
        self.pushButton_connect = QtWidgets.QPushButton()
        self.pushButton_connect.setText("Connect")
        self.pushButton_connect.clicked.connect(self.toggle_connection)
        self.pushButton_connect.setStyleSheet(self.button_style_bot.format(color="#008CBA", pressed_color="#005f6b"))
        self.horizontalLayout_buttons.addWidget(self.pushButton_connect)

        # Add the start acquisition button
        self.pushButton_start_acquisition = QtWidgets.QPushButton()
        self.pushButton_start_acquisition.setText("Start Acquisition")
        self.pushButton_start_acquisition.clicked.connect(self.toggle_acquisition)
        self.pushButton_start_acquisition.setStyleSheet(self.button_style_bot.format(color="#4CAF50", pressed_color="#4CAF50"))
        self.pushButton_start_acquisition.setDisabled(True)
        self.horizontalLayout_buttons.addWidget(self.pushButton_start_acquisition)

        # Add the save button
        self.pushButton_save = QtWidgets.QPushButton()
        self.pushButton_save.setText("Save")
        self.pushButton_save.clicked.connect(self.save_file)
        self.pushButton_save.setStyleSheet(self.button_style_bot.format(color="#008CBA", pressed_color="#89f0ec"))        
        self.pushButton_save.setDisabled(True)
        self.horizontalLayout_buttons.addWidget(self.pushButton_save)

        # Add the show summary button
        self.pushButton_show_summary = QtWidgets.QPushButton()
        self.pushButton_show_summary.setText("Show Summary")
        self.pushButton_show_summary.clicked.connect(self.show_data_summary)
        self.pushButton_show_summary.setStyleSheet(self.button_style_bot.format(color="#008CBA", pressed_color="#89f0ec"))
        self.pushButton_show_summary.setDisabled(True)
        self.horizontalLayout_buttons.addWidget(self.pushButton_show_summary)

        self.label_timer = QtWidgets.QLabel()
        self.horizontalLayout_buttons.addWidget(self.label_timer)

    # Button style
    button_style_bot = """
    QPushButton {{
        border: 2px solid #8f8f91;
        border-radius: 6px;
        background-color: {color};
        min-width: 80px;
        max-width: 150px;
        min-height: 40px;
        max-height: 40px;
        font-weight: bold;
        font-size: 16px;
    }}
    QPushButton:pressed {{
        background-color: {pressed_color};
    }}
    QPushButton:disabled {{
        background-color: #e0e0e0;
        border-color: #a1a1a1;
    }}"""

    def show_info(self):
        QtWidgets.QMessageBox.information(self, "Info", "Welcome to B(R)EAT(H). Start acquisitions by pressing the Start Acquisition Button in the main screen app.")
    
    def toggle_acquisition(self):
        if self.acquisition_running:
            self.stop_acquisition()
            self.pushButton_start_acquisition.setText("Start Acquisition")
            self.pushButton_start_acquisition.setStyleSheet(self.button_style_bot.format(color="#4CAF50", pressed_color="#f44336"))
            self.pushButton_save.setDisabled(False)
        else:
            self.start_acquisition()
            self.pushButton_start_acquisition.setText("Stop Acquisition")
            self.pushButton_start_acquisition.setStyleSheet(self.button_style_bot.format(color="#f44336", pressed_color="#4CAF50"))
            self.pushButton_save.setDisabled(True)
        self.acquisition_running = not self.acquisition_running

    def toggle_connection(self):
        if self.connection:
            self.serial_disconnect()
        else:
            self.serial_connect()
        self.connection = not self.connection
    
    def show_data_summary(self):
        data = []
        for i in range(min(len(self.instant_rrs), len(self.inspiratory_times), len(self.expiratory_times), len(self.ie_ratios))):
            cycle_data = [
                f"{i + 1}th cycle",
                self.instant_rrs[i] if i < len(self.instant_rrs) else "--",
                self.inspiratory_times[i] if i < len(self.inspiratory_times) else "--",
                self.expiratory_times[i] if i < len(self.expiratory_times) else "--",
                self.ie_ratios[i] if i < len(self.ie_ratios) else "--"
            ]
            data.append(cycle_data)

        self.data_summary_window = DataSummaryWindow(data, self)
        self.data_summary_window.exec_()

    def change_option_img(self):
        # Costruisci il percorso delle immagini
        current_directory = os.path.dirname(__file__)
        self.option_idx = None
        image_paths = [
            os.path.join(current_directory, '..', 'Images', 'BandStanding.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandStanding1.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandSitting.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandSitting1.jpg')
        ]
        
        if self.option == "Option1":
            self.icon = QIcon(image_paths[0])
            logging.info(f"Option1: {self.option}")
            self.option_idx == 0
        elif self.option == "Option2":
            self.icon = QIcon(image_paths[1])
            logging.info(f"Option2: {self.option}")
            self.option_idx == 1
        elif self.option == "Option3":
            self.icon = QIcon(image_paths[2])
            logging.info(f"Option3: {self.option}")
            self.option_idx == 2
        elif self.option == "Option4":
            self.icon = QIcon(image_paths[3])
            logging.info(f"Option4: {self.option}")
            self.option_idx == 3
                
    def change_option(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        protocol_gui_path = os.path.join(current_path, 'Protocol.py')
        self.close()
        subprocess.Popen(['python', protocol_gui_path, self.username])
        

    def create_param_box(self, param_name, box_style): 
        frame = QtWidgets.QFrame(self.centralwidget)
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        frame.setStyleSheet(box_style)
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(param_name)
        label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        label.setFont(font)
        value_label = QtWidgets.QLabel("--")
        value_label.setAlignment(QtCore.Qt.AlignCenter)
        value_font = QtGui.QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setStyleSheet("border: 1px solid #8f8f91; border-radius: 6px; background-color: #ffffff; min-height: 50px; min-width: 200px; max-width: 250px;")
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(value_label, alignment=QtCore.Qt.AlignCenter)
        return frame, value_label
    
    # Method to update respiratory rate label
    def update_respiratory_rate_label(self, value):
        self.label_respiratory_rate.setText(f"{value} breaths/min")

    # Method to update inspiration time label
    def update_inspiration_time_label(self, value):
        self.label_inspiration_time.setText(f"{value} s")

    # Method to update expiration time label
    def update_expiration_time_label(self, value):
        self.label_expiration_time.setText(f"{value} s")

    def update_ie_ratio_label(self, value):
        self.label_ie_ratio.setText(f"{value}")
            
    def load_csv_to_table(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", home_directory, "CSV Files (*.csv);;All Files (*)", options=options)
 
        if file_path:
            self.data_uploaded = True
            filename = os.path.basename(file_path)
            parts = filename.split('_')  # Dividi il nome del file in parti basandoti sugli underscore
            
            # Assicurati che il formato del file sia quello atteso
            parts = filename.split('_')  # Split the filename into parts based on underscores

            # Initialize option to None
            self.option = None
            self.option_idx = None
            self.icon = None
            # Iterate through parts to find the one that starts with "Option"
            for part in parts:
                if part.startswith("Option"):
                    self.option = part
                    break  # Exit the loop once the option part is found

            if self.option:
                self.change_option_img()
                self.pushButton_option.setDisabled(True)

            # Load data into a DataFrame
            self.dataframe = pd.read_csv(file_path)
            logging.info("Data loaded into DataFrame.")            
            # Set data_uploaded flag to True
            self.data_uploaded = True            
            # Call a method to update the plot with the loaded data
            self.update_plot_with_loaded_data(file_path)
        else:
            logging.info("No file selected.")

    
    def update_plot_with_loaded_data(self, file_path):
        self.data_buffer = []  # Clear the current data buffer
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip headers
            for row in csv_reader:
                try:
                    value = float(row[0])
                    self.data_buffer.append(value)
                except ValueError:
                    logging.error(f"Could not convert {row[0]} to float.")
        
        # Update the plot with the loaded data
        self.update_plot()

    def serialscan(self):
        self.comboBox_serialport.clear()
        serial_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.comboBox_serialport.addItems(serial_ports)
  


    def serial_connect(self):
        self.dialog = ConnectDialog(self)
        self.dialog.show()
        serial_port = self.comboBox_serialport.currentText()
        self.serial_worker = SerialWorker(serial_port)
        self.serial_worker.signals.status.connect(self.status_monitor)
        self.serial_worker.signals.status.connect(self.connection_success_notification)
        self.serial_worker.start()

    def connection_success_notification(self, status):
        if status:
            success_dialog = ConnectionSuccessDialog(self)
            success_dialog.exec_()
            self.serial_worker.send('t') 

    def show_disconnect_dialog(self):
        self.disconnect_dialog = QtWidgets.QMessageBox(self)
        self.disconnect_dialog.setIcon(QtWidgets.QMessageBox.Warning)
        self.disconnect_dialog.setWindowTitle("Disconnection")
        self.disconnect_dialog.setText("You have pressed the disconnect button. Do you want to proceed?")
        self.disconnect_dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        self.disconnect_dialog.buttonClicked.connect(self.disconnect_response)
        self.disconnect_dialog.show()

    def disconnect_response(self, button):
        if button.text() == "&Yes":
            self.serial_worker.send('o')
            self.serial_disconnect()

    def serial_disconnect(self):
        if self.serial_worker is not None:
            self.serial_worker.send('d')
            self.serial_worker.disconnect()
            self.serial_worker = None
            self.update_disconnect_button()

    def status_monitor(self, status):
        self.dialog.close()
        self.connected = status
        if status:
            logging.info("Connection established.")
            self.pushButton_connect.setText("Disconnect")
            self.pushButton_connect.setStyleSheet(self.button_style_bot.format(color="#f44336", pressed_color="#fa7369"))
            self.pushButton_reset.setDisabled(False)
            self.pushButton_start_acquisition.setDisabled(False)
        else:
            logging.info("Failed to connect.")
            self.update_disconnect_button()

    def update_disconnect_button(self):
        self.pushButton_connect.setText("Connect")
        self.pushButton_connect.setStyleSheet(self.button_style_bot.format(color="#008CBA", pressed_color="#89f0ec"))
        #self.pushButton_reset.setDisabled(True)
        self.pushButton_start_acquisition.setDisabled(True)









    

    def acquire_data(self, z_value):
        if not hasattr(self, 'data_buffer'):
            self.data_buffer = []  # Inizializza il buffer se non esiste

        self.data_buffer.append(z_value)
        # Evita di aggiungere nuovamente i dati al buffer
        if len(self.data_buffer) > 0:
            self.acquire_data_filt(z_value)  # Esegui le operazioni sui dati
            self.update_plot()  # Aggiorna il grafico

    def acquire_data_filt(self, z_value):

        self.apply_moving_average()
        self.apply_butterworth_filter()
        self.apply_find_peaks()
        # Compute and update the labels
        self.compute_rr()
        self.inspiratory_time()
        self.expiratory_time()
        self.compute_ie_ratio()

    def apply_moving_average(self, window_size=200):
        if len(self.data_buffer) >= window_size:
            cumsum = np.cumsum(np.insert(self.data_buffer, 0, 0))
            self.data_MA_filtered = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
        else:
            self.data_MA_filtered = np.array(self.data_buffer)  # Ensure `self.data_MA_filtered` is always a numpy array

    def apply_butterworth_filter(self, cutoff=0.6, fs=200, order=3):
        if len(self.data_MA_filtered) >= 13:  # Ensure there are enough data points
            b, a = butter(order, cutoff / (0.5 * fs), btype='low', analog=False)
            try:
                self.data_BW_filtered = filtfilt(b, a, self.data_MA_filtered, padlen=12)
            except ValueError as e:
                logging.error(f"Filtering error: {e}")
                self.data_BW_filtered = self.data_MA_filtered.copy()  # Fallback to original data if filtering fails
        else:
            self.data_BW_filtered = self.data_MA_filtered.copy()  # Fallback to original data if not enough points

    def apply_find_peaks(self):
        if len(self.data_BW_filtered) > 0:
            self.peak_indices, _ = find_peaks(self.data_BW_filtered,prominence = 0.05,distance=100)
            self.min_indices, _ = find_peaks(-self.data_BW_filtered,prominence = 0.05,distance=100)

            # Rimuovi il primo minimo se è trovato prima del primo massimo
            if len(self.peak_indices) > 0 and (len(self.min_indices) == 0 or self.peak_indices[0] < self.min_indices[0]):
                self.peak_indices = self.peak_indices[1:]  # Rimuove il primo minimo

        else:
            self.peak_indices = []
            self.min_indices = []

    def compute_rr(self):
        """
        Compute the instantenous respiratory rate.
        """

        if len(self.min_indices) > 1 and len(self.min_indices) > self.last_min_count:
            time_diff = self.min_indices[-1] - self.min_indices[-2]
            rr = int(60 / (time_diff / self.fs))
            self.instant_rrs.append(rr)
            self.update_respiratory_rate_label(rr)
            logging.info(f"Respiratory rate for cycle {len(self.instant_rrs)}: {rr}")

            # Check if the respiratory rate exceeds the threshold
            if rr > self.max_RR_thresh and not self.threshold_exceeded:
                self.handle_threshold_exceeded()
            elif rr <= self.max_RR_thresh and self.threshold_exceeded:
                self.handle_threshold_not_exceeded()

            # Update the last processed minima count
            self.last_min_count = len(self.min_indices)
    
    def handle_threshold_exceeded(self):
        logging.info(f"Respiratory rate exceeded threshold: {self.max_RR_thresh}")
        if self.serial_worker is not None:
            self.serial_worker.send('b')  # Invia il carattere desiderato al dispositivo
        self.threshold_exceeded = True
    
    def handle_threshold_not_exceeded(self):
        logging.info(f"Respiratory rate below threshold: {self.max_RR_thresh}")
        if self.serial_worker is not None:
            self.serial_worker.send('o')  # Invia il carattere per spegnere il buzzer
        self.threshold_exceeded = False
    
    def inspiratory_time(self, fs = 200):
        """
        Calculate the inspiratory time from the peak and low indices.

        Parameters:
        peak_indices (array-like): The indices of the peaks in the signal.
        min_indices (array-like): The indices of the lows in the signal.
        fs (float): The sampling frequency of the signal.

        Returns:
        float: The expiratory time in seconds.

        """
        # Calculate the time between peaks and subsequent lows
        # Ensure there are at least two min_indices and one peak_index
        if len(self.min_indices) > 1 and len(self.peak_indices) > 0 and len(self.min_indices) > self.last_min_count_insp:
            # Trova il prossimo minimo dopo ogni picco
            if self.min_indices[-2] < self.peak_indices[-1]:
                inspiratory_time = round(((self.peak_indices[-1] - self.min_indices[-2]) / fs), 2)
                self.inspiratory_times.append(inspiratory_time)
                logging.info(f"Tempo inspiratorio per ciclo {len(self.inspiratory_times)}: {self.inspiratory_times[-1]}")
                # Aggiorna l'ultimo conteggio elaborato
                self.last_min_count_insp = len(self.min_indices)

        if len(self.inspiratory_times) > 0:
            self.update_inspiration_time_label(self.inspiratory_times[-1])
        else:
            self.update_inspiration_time_label("--")


    def expiratory_time(self, fs = 200):
        """
        Calculate the expiratory time from the peak and low indices.

        Parameters:
        peak_indices (array-like): The indices of the peaks in the signal.
        min_indices (array-like): The indices of the lows in the signal.
        fs (float): The sampling frequency of the signal.

        Returns:
        float: The inspiratory time in seconds.

        """
        # Ensure there are at least two min_indices and one peak_index
        if len(self.min_indices) > 1 and len(self.peak_indices) > 0 and len(self.min_indices) > self.last_min_count_exp:
            # Ensure peak comes after the min to calculate a positive expiratory time
            if self.min_indices[-1] > self.peak_indices[-1]:
                expiratory_time = round(((self.min_indices[-1] - self.peak_indices[-1]) / fs), 2)
                self.expiratory_times.append(expiratory_time)
                logging.info(f"Tempo espiratorio per ciclo {len(self.expiratory_times)}: {self.expiratory_times[-1]}")
                # Aggiorna l'ultimo conteggio elaborato
                self.last_min_count_exp = len(self.min_indices)

        if len(self.expiratory_times) > 0:
            self.update_expiration_time_label(self.expiratory_times[-1])
        else:
            self.update_expiration_time_label("--")

    def compute_ie_ratio(self):
        """
        Calculate the inspiratory/expiratory ratio.
        """
        if len(self.inspiratory_times) > 0 and len(self.expiratory_times) > 0 and len(self.ie_ratios) < len(self.inspiratory_times):
            inspiratory_time = self.inspiratory_times[-1]
            expiratory_time = self.expiratory_times[-1]
            if expiratory_time != 0:
                ie_ratio = round((inspiratory_time / expiratory_time), 2)
                self.ie_ratios.append(ie_ratio)
                logging.info(f"Rapporto I/E per ciclo {len(self.ie_ratios)}: {self.ie_ratios[-1]}")
                # Aggiorna l'ultimo conteggio elaborato
                self.last_ie_count = len(self.ie_ratios)
                self.update_ie_ratio_label(self.ie_ratios[-1])
            else:
                self.update_ie_ratio_label("--")

    # Offline analysis
    def remove_dc_offset(self):
        """
        Remove the DC offset from the data in the DataFrame.
        """
        if hasattr(self, 'dataframe'):
            self.data_dc_removed = self.dataframe['Raw Data'] - self.dataframe['Raw Data'].mean()
            logging.info("DC offset removed from the DataFrame.")
        else:
            logging.error("DataFrame not loaded. Cannot remove DC offset.")
    
    def bw_offline(self, low_freq, high_freq, order=3):
        """
        Apply a bandpass filter to the input signal.
        """
        nyq = 0.5 * self.fs
        low = low_freq / nyq
        high = high_freq / nyq
        b, a = butter(order, [low, high], btype='band')
        self.data_filtered_offline = filtfilt(b, a, self.data_dc_removed)
        logging.info("Bandpass filter applied to the DataFrame.")

    def find_peaks_and_lows(self, threshold=0.01):
        """
        Find the peaks and lows in a signal.
        """
        self.peaks, _ = find_peaks(self.data_filtered_offline, height=threshold)
        self.lows, _ = find_peaks(-self.data_filtered_offline, height=threshold)

    def real_peaks(self):
        """
        Find the real peaks in a signal by grouping adjacent peaks.
        """
        final_peaks = []
        processed_peaks = set()

        for i in range(len(self.peaks)):
            if i in processed_peaks:
                continue

            current_group = [self.peaks[i]]
            processed_peaks.add(i)

            while i + 1 < len(self.peaks) and not any((self.lows > self.peaks[i]) & (self.lows < self.peaks[i + 1])):
                current_group.append(self.peaks[i + 1])
                processed_peaks.add(i + 1)
                i += 1

            if len(current_group) > 1:
                midpoint = int(np.round(np.mean(current_group)))
                final_peaks.append(midpoint)
            else:
                final_peaks.append(current_group[0])

        self.peak_indices = np.array(final_peaks)

    def real_lows(self):
        """
        Find the real lows in a signal by grouping adjacent lows.
        """
        final_lows = []
        processed_lows = set()

        for j in range(len(self.lows)):
            if j in processed_lows:
                continue

            current_group = [self.lows[j]]
            processed_lows.add(j)

            while j + 1 < len(self.lows) and not any((self.peaks > self.lows[j]) & (self.peaks < self.lows[j + 1])):
                current_group.append(self.lows[j + 1])
                processed_lows.add(j + 1)
                j += 1

            if len(current_group) > 1:
                midpoint = int(np.round(np.mean(current_group)))
                final_lows.append(midpoint)
            else:
                final_lows.append(current_group[0])

        self.min_indices = np.array(final_lows)

    def compute_respiratory_rate_offline(self):
        """
        Calculate the respiratory rate from the peak indices.
        """
        if len(self.peak_indices) < 2:
            self.update_respiratory_rate_label(0)
            return

        # Calculate the time between peaks
        time_diff = np.diff(self.peak_indices) / self.fs

        # Calculate the average time between peaks
        avg_time_diff = np.mean(time_diff)

        # Calculate the respiratory rate in breaths per minute
        respiratory_rate = 60 / avg_time_diff
        
        self.update_respiratory_rate_label(int(respiratory_rate))

    def compute_inspiratory_expiratory_time_offline(self):
        """
        Calculate the inspiratory and expiratory times from the peak and low indices.
        """
        # Check if there are sufficient peaks and lows to compute the times
        if len(self.peak_indices) < 2 or len(self.min_indices) < 2:
            self.update_inspiration_time_label(0)
            self.update_expiration_time_label(0)
            self.update_ie_ratio_label(0)
            return

        # Ensure the sequence starts with a peak followed by a low
        if self.min_indices[0] < self.peak_indices[0]:
            self.min_indices = self.min_indices[1:]

        # Ensure there are still sufficient peaks and lows
        if len(self.peak_indices) < 2 or len(self.min_indices) < 2:
            self.update_inspiration_time_label(0)
            self.update_expiration_time_label(0)
            self.update_ie_ratio_label(0)
            return

        # Calculate the time between peaks and subsequent lows
        inspiratory_times = []
        expiratory_times = []

        for i in range(min(len(self.peak_indices), len(self.min_indices)) - 1):
            if self.min_indices[i] > self.peak_indices[i]:
                inspiratory_times.append((self.min_indices[i] - self.peak_indices[i]) / self.fs)
                expiratory_times.append((self.peak_indices[i + 1] - self.min_indices[i]) / self.fs)

        # Calculate the average inspiratory and expiratory times
        avg_inspiratory_time = np.mean(inspiratory_times) if inspiratory_times else 0
        avg_expiratory_time = np.mean(expiratory_times) if expiratory_times else 0

        # Calculate the inspiratory to expiratory ratio (IER)
        if avg_expiratory_time != 0:
            ier = avg_inspiratory_time / avg_expiratory_time
        else:
            ier = np.inf

        self.update_inspiration_time_label(round(avg_inspiratory_time, 2))
        self.update_expiration_time_label(round(avg_expiratory_time, 2))
        self.update_ie_ratio_label(round(ier, 2))

    def apply_filt_offline(self):
        self.remove_dc_offset()
        self.bw_offline(0.1, 0.6)
        self.find_peaks_and_lows()
        self.real_peaks()
        self.real_lows()

        # Calculate and update respiratory parameters
        self.compute_respiratory_rate_offline()
        self.compute_inspiratory_expiratory_time_offline()        






    def switch_plot_mode(self):
        if self.plot_mode == 'filtered':
            self.plot_mode = 'raw'
            self.pushButton_switch_plot.setText("Switch to Filtered Data")
        else:
            self.plot_mode = 'filtered'
            self.pushButton_switch_plot.setText("Switch to Raw Data")

            # Apply DC offset removal when switching to filtered mode if data was uploaded
            if self.data_uploaded:
                self.apply_filt_offline()

        self.update_plot()   
    
    def update_plot(self):
        if self.plot_mode == 'filtered':
            if self.data_uploaded and self.data_filtered_offline is not None:
                data_to_plot = self.data_filtered_offline
            else:
                data_to_plot = self.data_BW_filtered
        else:
            data_to_plot = self.data_buffer

        if len(data_to_plot) > 0:
            time_values = np.arange(len(data_to_plot)) / self.fs
        else:
            time_values = []

        if not hasattr(self, 'z_curve'):
            self.z_curve = self.graphicsView.plot(time_values, data_to_plot, pen=pg.mkPen(color='b', width=1))
        else:
            self.z_curve.setData(time_values, data_to_plot)

        if self.peak_scatter is None:
            self.peak_scatter = self.graphicsView.plot([], [], pen=None, symbol='o', symbolBrush='r')
        if self.min_scatter is None:
            self.min_scatter = self.graphicsView.plot([], [], pen=None, symbol='o', symbolBrush='g')

        if self.plot_mode == 'filtered':
            if self.data_uploaded:
                # Plot offline filtered data peaks and lows
                if len(self.peak_indices) > 0:
                    peak_x = np.array(self.peak_indices) / self.fs
                    peak_y = np.array(data_to_plot)[self.peak_indices]
                    self.peak_scatter.setData(peak_x, peak_y)
                else:
                    self.peak_scatter.setData([], [])

                if len(self.min_indices) > 0:
                    min_x = np.array(self.min_indices) / self.fs
                    min_y = np.array(data_to_plot)[self.min_indices]
                    self.min_scatter.setData(min_x, min_y)
                else:
                    self.min_scatter.setData([], [])
            else:
                # Plot real-time filtered data peaks and lows
                if len(self.peak_indices) > 0:
                    peak_x = np.array(self.peak_indices) / self.fs
                    peak_y = np.array(data_to_plot)[self.peak_indices]
                    self.peak_scatter.setData(peak_x, peak_y)
                else:
                    self.peak_scatter.setData([], [])

                if len(self.min_indices) > 0:
                    min_x = np.array(self.min_indices) / self.fs
                    min_y = np.array(data_to_plot)[self.min_indices]
                    self.min_scatter.setData(min_x, min_y)
                else:
                    self.min_scatter.setData([], [])
        else:
            # Clear scatter data for raw plot or when switching to raw mode
            self.peak_scatter.setData([], [])
            self.min_scatter.setData([], [])



















    def keyPressEvent(self, event: QKeyEvent):
        """!
        @brief Handle key press events.
        """
        if event.text().lower() == 's':
            self.serial_worker.send('s') # _from_key

    def save_file(self):
        self.end = time.time()
        
        # Formatta i timestamp di inizio e fine
        start_time_str = datetime.fromtimestamp(self.start).strftime('%H-%M-%S')
        end_time_str = datetime.fromtimestamp(self.end).strftime('%H-%M-%S')
        
        # Apri una finestra di dialogo per selezionare la cartella di destinazione
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", home_directory, options=options)

        if directory:  # Se una cartella è stata selezionata
            # Include the username at the beginning of the filename and save it in the selected directory
            filename = f"{self.username}_{self.option}_{start_time_str}_{end_time_str}.csv"
            filepath = os.path.join(directory, filename)  # Combine the selected directory with the filename

            # Scrivi i dati raw nel file CSV
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Raw Data'])  # Add a header for clarity
                for value in self.data_buffer:
                    writer.writerow([value])
            
            logging.info(f"Data saved to {filepath}")
        else:
            logging.info("No directory selected. Data not saved.")


    def reset_graph(self):
        self.data_buffer = []
        self.data_BW_filtered = []
        self.data_MA_filtered = []
        self.peak_indices = []
        self.min_indices = []
        self.data_filtered_offline = None
        self.data_uploaded = False
        self.pushButton_save.setDisabled(True)
        self.pushButton_show_summary.setDisabled(True)
        self.pushButton_option.setDisabled(False) 
        self.instant_rrs = []
        self.inspiratory_times = []
        self.expiratory_times = []
        self.ie_ratios = []
        self.last_min_count = 0
        self.last_min_count_insp = 0
        self.last_min_count_exp = 0
        self.last_ie_count = 0

        # Reset computed parameters
        self.update_respiratory_rate_label("--")
        self.update_inspiration_time_label("--")
        self.update_expiration_time_label("--")
        self.update_ie_ratio_label("--")

        self.update_plot()

    def start_acquisition(self):
        if self.serial_worker is not None:
            self.serial_worker.signals.new_data.connect(self.acquire_data)
            self.serial_worker.send('s')
            logging.info("Acquisition started.")

    def stop_acquisition(self):
        if self.serial_worker is not None:
            try:
                self.serial_worker.signals.new_data.disconnect(self.acquire_data)
            except TypeError:
                pass  # Ignore if no connection exists
            self.serial_worker.send('v')
            # Flush the input buffer to clear any remaining data
            self.serial_worker.port.reset_input_buffer()
            logging.info("Acquisition stopped.")
            self.pushButton_show_summary.setDisabled(False)

    def save_data(self):
        self.save_file()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())