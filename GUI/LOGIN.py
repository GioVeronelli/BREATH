import sys
import sqlite3
import os
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess


class UI_Form(object):
    def openwindow(self):
        from USER import Ui_NewUser  # Importa qui per evitare l'importazione circolare
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_NewUser()
        self.ui.setupUi(self.window)
        self.window.show()

    def setupUi(self, Form):
        Form.setWindowTitle("Login Page")
        Form.setObjectName("Form")
        Form.resize(614, 436)
        Form.setStyleSheet("background-color: #f5f5f5;")

        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setText("Enter your Credentials")
        self.label.setFont(QtGui.QFont("Arial", 18, QtGui.QFont.Bold))
        self.label.setStyleSheet("color: #2c3e50;")

        label_width = 320  # larghezza dell'etichetta
        window_width = Form.width()  # larghezza della finestra
        x_pos = (window_width - label_width) / 2 - 12  # Modifica il valore dell'offset a tuo piacimento

        self.label.setGeometry(QtCore.QRect(int(x_pos), 40, 320, 50))

        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(100, 110, 431, 201))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.l_username = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_username.setObjectName("l_username")
        self.l_username.setText("Username:")
        self.l_username.setFont(QtGui.QFont("Arial", 12))
        self.gridLayout.addWidget(self.l_username, 0, 0, 1, 1)

        self.l_password = QtWidgets.QLabel(self.gridLayoutWidget)
        self.l_password.setObjectName("l_password")
        self.l_password.setText("Password:")
        self.l_password.setFont(QtGui.QFont("Arial", 12))
        self.gridLayout.addWidget(self.l_password, 1, 0, 1, 1)

        self.txt_username = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_username.setObjectName("txt_username")
        self.txt_username.setFont(QtGui.QFont("Arial", 12))
        self.txt_username.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.gridLayout.addWidget(self.txt_username, 0, 1, 1, 1)

        self.txt_password = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.txt_password.setObjectName("txt_password")
        self.txt_password.setFont(QtGui.QFont("Arial", 12))
        self.txt_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_password.setStyleSheet("border: 1px solid #2c3e50; border-radius: 5px; padding: 5px;")
        self.gridLayout.addWidget(self.txt_password, 1, 1, 1, 1)

        self.btn_submit = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_submit.setObjectName("btn_submit")
        self.btn_submit.setText("Submit")
        self.btn_submit.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.gridLayout.addWidget(self.btn_submit, 2, 1, 1, 1)

        self.btn_newuser = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.btn_newuser.setObjectName("btn_newuser")
        self.btn_newuser.setText("New User")
        self.btn_newuser.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        self.btn_newuser.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.gridLayout.addWidget(self.btn_newuser, 3, 1, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(Form)

        self.btn_newuser.clicked.connect(lambda: self.btn_newuser_handler(Form))
        self.btn_submit.clicked.connect(lambda: self.btn_login_handler(Form))

    def pop_window(self, text, title="Error"):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()
       
    def btn_newuser_handler(self, window):
        self.openwindow()
        window.close()

    def btn_login_handler(self, Form):
        username = self.txt_username.text()
        password = self.txt_password.text()

        if(username== "" or password== ""): 
            self.pop_window('Fill all the fields!')
            return
        
        if len(password) < 10:
            self.pop_window('Password should be at least 10 characters long!')
            return


        conn = sqlite3.connect('user.db')
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM credentials")
            val = cursor.fetchall()
            login_success = False
            for user_pass in val:
                if username == user_pass[0] and password == user_pass[1]:
                    login_success = True
                    break
            if login_success:
                self.open_protocol_window(Form, username)
            else:
                self.pop_window('Invalid username or password!')
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            conn.close()

    def open_protocol_window(self, Form, username):
        current_path = os.path.dirname(os.path.realpath(__file__))
        protocol_gui_path = os.path.join(current_path, 'Protocol.py')
        subprocess.Popen(['python', protocol_gui_path, username])
        Form.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = UI_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
