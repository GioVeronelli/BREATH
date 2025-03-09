from PyQt5 import QtCore, QtGui, QtWidgets
from LOGIN import *
import sqlite3
import sys

class Ui_NewUser(object):

    def openwindow(self):
        self.window = QtWidgets.QMainWindow()  # Store reference to the window
        self.ui = UI_Form()
        self.ui.setupUi(self.window)
        self.window.show()

    def btn_exit_handler(self, window):
        self.openwindow()
        window.close()

    def setupUi(self, Newuser):
        self.Newuser = Newuser  # Store reference to the window
        Newuser.setWindowTitle("Registration")
        Newuser.setObjectName("Newuser")
        Newuser.resize(750, 500)
        Newuser.setStyleSheet("background-color: #f5f5f5;")

        self.gridLayoutWidget = QtWidgets.QWidget(Newuser)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(50, 80, 650, 250))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(40, 40, 40, 40)
        self.gridLayout.setObjectName("gridLayout")

        # Labels and Text Fields
        self.l_firstname = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_firstname.setObjectName("l_firstname")
        self.l_firstname.setText("First Name")
        self.l_firstname.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_firstname, 1, 1)

        self.txt_firstname = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_firstname.setObjectName("txt_firstname")
        self.txt_firstname.setFont(QtGui.QFont("Arial", 12))
        self.txt_firstname.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_firstname.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_firstname.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_firstname, 2, 1)

        self.l_phone = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_phone.setObjectName("l_phone")
        self.l_phone.setText("Phone Number")
        self.l_phone.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_phone, 4, 1)

        self.txt_phone = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_phone.setObjectName("txt_phone")
        self.txt_phone.setFont(QtGui.QFont("Arial", 11))
        self.txt_phone.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_phone.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_phone.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_phone, 5, 1)

        self.l_email = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_email.setObjectName("l_email")
        self.l_email.setText("Email Address")
        self.l_email.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_email, 4, 3)

        self.txt_email = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_email.setObjectName("txt_email")
        self.txt_email.setFont(QtGui.QFont("Arial", 11))
        self.txt_email.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_email.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_email.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_email, 5, 3)

        self.l_lastname = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_lastname.setObjectName("l_lastname")
        self.l_lastname.setText("Last Name")
        self.l_lastname.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_lastname, 1, 3)

        self.txt_lastname = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_lastname.setObjectName("txt_lastname")
        self.txt_lastname.setFont(QtGui.QFont("Arial", 12))
        self.txt_lastname.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_lastname.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_lastname.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_lastname, 2, 3)

        self.l_password = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_password.setObjectName("l_password")
        self.l_password.setText("Password*")
        self.l_password.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_password, 6, 3)

        self.txt_password = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_password.setObjectName("txt_password")
        self.txt_password.setFont(QtGui.QFont("Arial", 11))
        self.txt_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_password.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_password.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_password.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_password, 7, 3)

        self.l_username = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_username.setObjectName("l_username")
        self.l_username.setText("Username*")
        self.l_username.setFont(QtGui.QFont("Arial", 11))
        self.gridLayout.addWidget(self.l_username, 6, 1)

        self.txt_username = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_username.setObjectName("txt_username")
        self.txt_username.setFont(QtGui.QFont("Arial", 12))
        self.txt_username.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.txt_username.setMinimumSize(QtCore.QSize(250, 30))
        self.txt_username.setMaximumSize(QtCore.QSize(250, 30))
        self.gridLayout.addWidget(self.txt_username, 7, 1)

        # Label indicating mandatory fields
        self.label_mandatory = QtWidgets.QLabel(Newuser)
        self.label_mandatory.setGeometry(QtCore.QRect(110, 320, 300, 40))
        self.label_mandatory.setObjectName("label_mandatory")
        self.label_mandatory.setText("* indicates mandatory fields")
        self.label_mandatory.setFont(QtGui.QFont("Arial", 12))  
        self.label_mandatory.setStyleSheet("color: #e74c3c;")

        # Label
        self.label = QtWidgets.QLabel(Newuser)
        self.label.setGeometry(QtCore.QRect(0, 30, 750, 40))
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setText("New User Registration")
        self.label.setFont(QtGui.QFont("Arial", 20, QtGui.QFont.Bold))  
        self.label.setStyleSheet("color: #2c3e50;")

        # Layout for buttons
        self.verticalLayoutWidget = QtWidgets.QWidget(Newuser)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(200, 370, 350, 100))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        # Buttons
        self.btn_submit = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.btn_submit.setObjectName("btn_submit")
        self.btn_submit.setText("Submit")
        self.btn_submit.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        self.btn_submit.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                padding: 50px 100px;
            }
            QPushButton:enabled {
                background-color: #27ae60;
                color: white;
            }
            QPushButton:disabled {
                background-color: #bdc3c7; /* Gray color */
                color: #7f8c8d; /* Text color for disabled */
            }
            QPushButton:hover:enabled {
                background-color: #2ecc71;
            }
        """)
        self.btn_submit.setEnabled(False)  # Initially disabled
        self.verticalLayout.addWidget(self.btn_submit)

        self.btn_exit = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.btn_exit.setObjectName("btn_exit")
        self.btn_exit.setText("Exit")
        self.btn_exit.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border-radius: 5px;
                padding: 50px 100px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        self.verticalLayout.addWidget(self.btn_exit)

        QtCore.QMetaObject.connectSlotsByName(Newuser)

        # Button Click Events
        self.btn_exit.clicked.connect(lambda: self.btn_exit_handler(Newuser))
        self.btn_submit.clicked.connect(self.database)

        # Text Field Change Events
        self.txt_username.textChanged.connect(self.toggle_submit_button)
        self.txt_password.textChanged.connect(self.toggle_submit_button)

    def toggle_submit_button(self):
        # Enable submit button only if both username and password fields are not empty
        if self.txt_username.text() and self.txt_password.text():
            self.btn_submit.setEnabled(True)
        else:
            self.btn_submit.setEnabled(False)

    def pop_message(self, text, callback=None):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        if callback:
            msg.buttonClicked.connect(callback)
        msg.exec_()

    def switch_to_login(self):
        self.openwindow()
        self.Newuser.close()
        
    def pop_window(self, text, title="Error"):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def database(self):
        try:
            txt_firstname_v = self.txt_firstname.text()
            txt_lastname_v = self.txt_lastname.text()
            txt_phone_v = self.txt_phone.text()
            txt_email_v = self.txt_email.text()
            txt_username_v = self.txt_username.text()
            txt_password_v = self.txt_password.text()


            if len(txt_password_v)<10:
                self.pop_window('Password should be at least 10 characters long!')
                return

            conn = sqlite3.connect('user.db')
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials 
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                fname TEXT, 
                lname TEXT, 
                Phone TEXT, 
                email TEXT,
                username TEXT, 
                password TEXT)
            """)

            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM credentials WHERE username = ?", (txt_username_v,))
            if cursor.fetchone()[0] > 0:
                self.pop_message("User already present in the database")
            else:
                cursor.execute(""" 
                    INSERT INTO credentials 
                    (fname, lname, Phone, email, username, password)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (txt_firstname_v, txt_lastname_v, txt_phone_v, txt_email_v, txt_username_v, txt_password_v))
                conn.commit()
                cursor.close()
                conn.close()
                self.pop_message("Added to Database", self.switch_to_login)

        except Exception as e:
            self.pop_message(f"Cannot add to Database: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Newuser = QtWidgets.QWidget()
    ui = Ui_NewUser()
    ui.setupUi(Newuser)
    Newuser.show()
    sys.exit(app.exec_())

