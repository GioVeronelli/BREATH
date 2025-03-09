import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QDesktopWidget, QRadioButton, QGridLayout
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Select Acquisition Protocol')
        self.setGeometry(0, 0, 800, 600)
        self.setStyleSheet("background-color: #ffffff;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 60, 60, 60)  # Aggiunge margini a tutto il layout principale
        
        # Ottenere l'username dalla linea di comando
        if len(sys.argv) > 1:
            self.username = sys.argv[1]
        else:
            self.username = "Guest"

        # Etichetta di benvenuto
        welcome_label = QLabel(f"Welcome, {self.username}!", self)
        welcome_label.setFont(QFont('Arial', 16, QFont.Bold))
        welcome_label.setStyleSheet("color: #000080; margin-bottom: 20px;")
        welcome_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(welcome_label)

        title = QLabel("Select Acquisition Protocol", self)
        title.setFont(QFont('Arial', 13, QFont.Bold))  # Aggiunto QFont.Bold per il titolo
        title.setStyleSheet("color: #333; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        

        # Lista dei testi per i radio button
        radio_texts = [
            "Option 1 - Subject is standing and device is put on the subject's stomach",
            "Option 2 - Subject is standing and device is put on the subject's abdomen",
            "Option 3 - Subject is sitting and device is put on the subject's abdomen",
            "Option 4 - Subject is sitting and device is put on the subject's stomach"
        ]

        button_radio_layout = QGridLayout()  # Utilizzo di QGridLayout per allineare i radio button

        # Costruisci il percorso delle immagini
        current_directory = os.path.dirname(__file__)
        image_paths = [
            os.path.join(current_directory, '..', 'Images', 'BandStanding.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandStanding1.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandSitting.jpg'),
            os.path.join(current_directory, '..', 'Images', 'BandSitting1.jpg')
        ]

        # Verifica e crea i pulsanti per le immagini e i radio button
        self.image_buttons = []
        self.radio_buttons = []

        for idx, (image_path, radio_text) in enumerate(zip(image_paths, radio_texts), start=1):
            if not os.path.isfile(image_path):    
                continue
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                continue

            icon = QIcon(pixmap)

            # Creazione del pulsante con l'icona
            button = QPushButton(self)
            button.setObjectName(f"button_{idx}")  # Nome univoco per identificare il pulsante
            button.setFixedSize(200, 150)
            button.setIcon(icon)
            button.setIconSize(QSize(270, 270))
            button.setFlat(True)  # Rimuove il bordo attorno al pulsante

            # Aggiunta dei widget al QGridLayout
            button_radio_layout.addWidget(button, idx, 0, alignment=Qt.AlignCenter)

            # Creazione del radio button con il testo personalizzato
            radio_button = QRadioButton(radio_text, self)
            radio_button.setFont(QFont('Arial', 12))
            radio_button.setStyleSheet(
                "QRadioButton::indicator { width: 20px; height: 20px; }"
                "QRadioButton { padding-left: 10px; }"
            )
            radio_button.toggled.connect(self.update_button_style)  # Connessione per aggiornare lo stile

            # Aggiunta dei radio button alla lista
            self.radio_buttons.append(radio_button)

            button_radio_layout.addWidget(radio_button, idx, 1, alignment=Qt.AlignLeft)  # Allineamento a sinistra

            # Aggiungi il pulsante delle immagini alla lista
            self.image_buttons.append(button)

        main_layout.addLayout(button_radio_layout)
        main_layout.addSpacing(30)

        # Layout per i pulsanti "Enter" e "Exit"
        button_layout_bottom = QHBoxLayout()
        button_layout_bottom.addStretch()

        self.button_enter = QPushButton('Enter', self)
        self.button_enter.setFont(QFont('Arial', 15, QFont.Bold))
        self.button_enter.setFixedSize(150, 50)
        self.button_enter.setStyleSheet(
            'QPushButton { background-color: #ccc; color: white; padding: 15px; border-radius: 10px; }'
            'QPushButton:hover { background-color: #45a049; }'
        )
        self.button_enter.setEnabled(False)
        self.button_enter.clicked.connect(self.enter_application)
        button_layout_bottom.addWidget(self.button_enter)

        self.button_exit = QPushButton('Exit', self)
        self.button_exit.setFont(QFont('Arial', 15, QFont.Bold))
        self.button_exit.setFixedSize(150, 50)
        self.button_exit.setStyleSheet(
            'QPushButton { background-color: #f44336; color: white; padding: 15px; border-radius: 10px; }'
            'QPushButton:hover { background-color: #d32f2f; }'
        )
        self.button_exit.clicked.connect(self.exit_application)
        button_layout_bottom.addWidget(self.button_exit)

        button_layout_bottom.addStretch()
        main_layout.addLayout(button_layout_bottom)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.center()
        self.protocol_process = None

    def center(self, offset_y=220):
        desktop_geometry = QDesktopWidget().screenGeometry()
        window_geometry = self.frameGeometry()
        center_point = desktop_geometry.center()
        center_point.setY(center_point.y() - offset_y)
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

        if len(sys.argv) > 1:
            username = sys.argv[1]
            print(f"Username received: {username}")
        else:
            print("No username provided.")

    def enter_application(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        python_gui_path = os.path.join(current_path, 'PythonGUI.py')
        if len(sys.argv) > 1:
            username = sys.argv[1]
        else:
            username = "Guest"
        # Trova il radio button selezionato
        selected_radio_button = next((rb for rb in self.radio_buttons if rb.isChecked()), None)

        if selected_radio_button:
            # Ottieni l'indice del radio button selezionato
            idx = self.radio_buttons.index(selected_radio_button)

            # Passa il parametro in base all'opzione selezionata
            parameter = None
            if idx == 0:    # Option 1
                parameter = "Option1"
            elif idx == 1:  # Option 2
                parameter = "Option2"
            elif idx == 2:  # Option 3
                parameter = "Option3"
            elif idx == 3:  # Option 4
                parameter = "Option4"

            # Avvia PythonGUI.py con il parametro
            subprocess.Popen(['python', python_gui_path, parameter, username])

        self.close()

    def exit_application(self):
        if self.protocol_process and self.protocol_process.poll() is None:
            self.protocol_process.terminate()
            self.protocol_process.wait()
        self.close()

        current_path = os.path.dirname(os.path.realpath(__file__))
        login_script_path = os.path.join(current_path, 'LOGIN.py')
        subprocess.Popen(['python', login_script_path])

    def update_button_style(self):
        selected_radio_button = next((rb for rb in self.radio_buttons if rb.isChecked()), None)
    
        if not selected_radio_button:
            self.button_enter.setEnabled(False)
            self.button_enter.setStyleSheet(
                'QPushButton { background-color: #ccc; color: white; padding: 15px; border-radius: 10px; }'
                'QPushButton:hover { background-color: #ccc; }'
            )
            for button in self.image_buttons:
                button.setIconSize(QSize(300, 300))
        else:
            self.button_enter.setEnabled(True)
            self.button_enter.setStyleSheet(
                'QPushButton { background-color: #4CAF50; color: white; padding: 15px; border-radius: 10px; }'
                'QPushButton:hover { background-color: #45a049; }'
            )
            # Ingrandisci l'immagine associata al radio button selezionato
            for idx, rb in enumerate(self.radio_buttons):
                if rb.isChecked():
                    self.image_buttons[idx].setIconSize(QSize(270, 270))
                else:
                    self.image_buttons[idx].setIconSize(QSize(190, 190))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
