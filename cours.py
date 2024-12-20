from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QDialog, QMessageBox
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

        layout = QVBoxLayout()

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

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
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
                margin-top: 10px;
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
        self.services_button.clicked.connect(self.open_services_window)
        
        self.exit_button = QPushButton("Выход", self)
        self.exit_button.setGeometry(200, 300, 100, 40)
        self.exit_button.clicked.connect(self.close)

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

    def open_services_window(self):
        self.services_window = ServicesWindow()
        self.services_window.show()
        self.close()

class ServicesWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Services")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.services_table = QTableWidget()
        layout.addWidget(self.services_table)

        button_layout = QHBoxLayout()
        self.create_service_button = QPushButton("Создать услугу")
        self.create_service_button.clicked.connect(self.open_create_service_dialog)
        button_layout.addWidget(self.create_service_button)

        self.delete_service_button = QPushButton("Удалить услугу")
        self.delete_service_button.clicked.connect(self.delete_service)
        button_layout.addWidget(self.delete_service_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.services_table.cellDoubleClicked.connect(self.edit_service)

        self.load_services()

        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def load_services(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM service"
                    cursor.execute(sql)
                    services = cursor.fetchall()

                    self.services_table.setRowCount(len(services))
                    self.services_table.setColumnCount(3)  # Adjust based on your table structure
                    self.services_table.setHorizontalHeaderLabels(['ID_service', 'Name', 'Price'])  # Adjust headers

                    for row_index, service in enumerate(services):
                        for col_index, data in enumerate(service):
                            self.services_table.setItem(row_index, col_index, QTableWidgetItem(str(data)))

                    self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except pymysql.MySQLError as e:
                print(f"Error querying the database: {e}")
            finally:
                connection.close()

    def open_create_service_dialog(self):
        dialog = CreateServiceDialog(self)
        dialog.exec()
        self.load_services()

    def delete_service(self):
        selected_row = self.services_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a service to delete.")
            return

        service_id = self.services_table.item(selected_row, 0).text()

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM service WHERE ID_service = %s"
                    cursor.execute(sql, (service_id,))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Service deleted successfully.")
            except pymysql.MySQLError as e:
                print(f"Error deleting the service: {e}")
            finally:
                connection.close()

        self.load_services()

    def edit_service(self, row, column):
        service_id = self.services_table.item(row, 0).text()
        service_name = self.services_table.item(row, 1).text()
        service_price = self.services_table.item(row, 2).text()

        dialog = EditServiceDialog(self, service_id, service_name, service_price)
        dialog.exec()
        self.load_services()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class CreateServiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Service")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Service Name:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Service Price:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit()
        layout.addWidget(self.price_input)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_service)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_service(self):
        name = self.name_input.text()
        price = self.price_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO service (name, price) VALUES (%s, %s)"
                    cursor.execute(sql, (name, price))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Service created successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error creating the service: {e}")
            finally:
                connection.close()

class EditServiceDialog(QDialog):
    def __init__(self, parent=None, ID_service=None, service_name=None, service_price=None):
        super().__init__(parent)

        self.ID_service = ID_service

        self.setWindowTitle("Edit Service")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Service Name:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit(service_name)
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Service Price:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit(service_price)
        layout.addWidget(self.price_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_service)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_service(self):
        name = self.name_input.text()
        price = self.price_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "UPDATE service SET name = %s, price = %s WHERE ID_service = %s"
                    cursor.execute(sql, (name, price, self.ID_service))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Service updated successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error updating the service: {e}")
            finally:
                connection.close()
                
class AnimalsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Animals")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        self.animals_table = QTableWidget()
        layout.addWidget(self.animals_table)

        button_layout = QHBoxLayout()
        self.create_animal_button = QPushButton("Создать животное")
        self.create_animal_button.clicked.connect(self.open_create_animal_dialog)
        button_layout.addWidget(self.create_animal_button)

        self.delete_animal_button = QPushButton("Удалить животное")
        self.delete_animal_button.clicked.connect(self.delete_animal)
        button_layout.addWidget(self.delete_animal_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.animals_table.cellDoubleClicked.connect(self.edit_animal)

        self.load_animals()

        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def load_animals(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM animals"
                    cursor.execute(sql)
                    animals = cursor.fetchall()

                    self.animals_table.setRowCount(len(animals))
                    self.animals_table.setColumnCount(3)
                    self.animals_table.setHorizontalHeaderLabels(['ID_animals', 'Name', 'Price'])

                    for row_index, animal in enumerate(animals):
                        for col_index, data in enumerate(animal):
                            self.animals_table.setItem(row_index, col_index, QTableWidgetItem(str(data)))

                    self.animals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except pymysql.MySQLError as e:
                print(f"Error querying the database: {e}")
            finally:
                connection.close()

    def open_create_animal_dialog(self):
        dialog = CreateAnimalDialog(self)
        dialog.exec()
        self.load_animals()

    def delete_animal(self):
        selected_row = self.animals_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an animal to delete.")
            return

        animal_id = self.animals_table.item(selected_row, 0).text()

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM animals WHERE ID_animals = %s"
                    cursor.execute(sql, (animal_id,))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Animal deleted successfully.")
            except pymysql.MySQLError as e:
                print(f"Error deleting the animal: {e}")
            finally:
                connection.close()

        self.load_animals()

    def edit_animal(self, row, column):
        animal_id = self.animals_table.item(row, 0).text()
        animal_name = self.animals_table.item(row, 1).text()
        animal_price = self.animals_table.item(row, 2).text()

        dialog = EditAnimalDialog(self, animal_id, animal_name, animal_price)
        dialog.exec()
        self.load_animals()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class CreateAnimalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Animal")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Animal Name:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Animal Price:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit()
        layout.addWidget(self.price_input)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_animal)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_animal(self):
        name = self.name_input.text()
        price = self.price_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO animals (name, price) VALUES (%s, %s)"
                    cursor.execute(sql, (name, price))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Animal created successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error creating the animal: {e}")
            finally:
                connection.close()

class EditAnimalDialog(QDialog):
    def __init__(self, parent=None, ID_animals=None, animal_name=None, animal_price=None):
        super().__init__(parent)

        self.ID_animals = ID_animals

        self.setWindowTitle("Edit Animal")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Animal Name:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit(animal_name)
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Animal Price:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit(animal_price)
        layout.addWidget(self.price_input)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_animal)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_animal(self):
        name = self.name_input.text()
        price = self.price_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "UPDATE animals SET name = %s, price = %s WHERE ID_animals = %s"
                    cursor.execute(sql, (name, price, self.ID_animals))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Animal updated successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error updating the animal: {e}")
            finally:
                connection.close()

# Update the MainWindow to open the AnimalsWindow
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setFixedSize(500, 400)

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
        self.animals_button.clicked.connect(self.open_animals_window)

        self.services_button = QPushButton("Услуги", self)
        self.services_button.setGeometry(350, 150, 100, 40)
        self.services_button.clicked.connect(self.open_services_window)

        self.exit_button = QPushButton("Выход", self)
        self.exit_button.setGeometry(200, 300, 100, 40)
        self.exit_button.clicked.connect(self.close)

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

    def open_animals_window(self):
        self.animals_window = AnimalsWindow()
        self.animals_window.show()
        self.close()

    def open_services_window(self):
        self.services_window = ServicesWindow()
        self.services_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
    
