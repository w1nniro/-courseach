from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
import sys
import pymysql

def create_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            db='salon'
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
    return connection

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setFixedSize(300, 200)

        # Create layout
        layout = QVBoxLayout()

        # Create and add widgets to the layout
        self.username_label = QLabel("Login:")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Set the layout for the window
        self.setLayout(layout)

        # Apply styles
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def handle_login(self):
        login = self.username_input.text()
        password = self.password_input.text()

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Use 'employers' table for authentication
                    sql = "SELECT * FROM employers WHERE login=%s AND password=%s"
                    cursor.execute(sql, (login, password))
                    result = cursor.fetchone()

                    if result:
                        print("Login successful")
                        self.open_main_window()
                    else:
                        print("Login failed: Invalid credentials")
            except pymysql.MySQLError as e:
                print(f"Error querying the database: {e}")
            finally:
                connection.close()

    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setFixedSize(500, 400)

        # Create buttons and position them using coordinates
        self.record_button = QPushButton("Запись", self)
        self.record_button.setGeometry(50, 50, 100, 40)

        self.report_button = QPushButton("Отчёт", self)
        self.report_button.setGeometry(200, 50, 100, 40)

        self.employees_button = QPushButton("Сотрудники", self)
        self.employees_button.setGeometry(350, 50, 100, 40)

        self.schedule_button = QPushButton("Расписание", self)
        self.schedule_button.setGeometry(50, 150, 100, 40)

        self.animals_button = QPushButton("Животные", self)
        self.animals_button.setGeometry(200, 150, 100, 40)

        self.services_button = QPushButton("Услуги", self)
        self.services_button.setGeometry(350, 150, 100, 40)
        
        # Add Exit button
        self.exit_button = QPushButton("Выход", self)
        self.exit_button.setGeometry(200, 300, 100, 40)
        self.exit_button.clicked.connect(self.close)

        # Apply styles
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())