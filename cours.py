from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QDateEdit, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QDialog, QMessageBox
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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

        self.setWindowTitle("Создать")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Животное:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Цена:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit()
        layout.addWidget(self.price_input)

        self.create_button = QPushButton("Создать")
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
                    QMessageBox.information(self, "Success", "Новое животное.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error creating the animal: {e}")
            finally:
                connection.close()

class EditAnimalDialog(QDialog):
    def __init__(self, parent=None, ID_animals=None, animal_name=None, animal_price=None):
        super().__init__(parent)

        self.ID_animals = ID_animals

        self.setWindowTitle("Животное")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.name_label = QLabel("Животное:")
        layout.addWidget(self.name_label)

        self.name_input = QLineEdit(animal_name)
        layout.addWidget(self.name_input)

        self.price_label = QLabel("Цена:")
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit(animal_price)
        layout.addWidget(self.price_input)

        self.save_button = QPushButton("Сохранить")
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

        
class EmployeesWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Employees")
        self.setFixedSize(800, 400)

        layout = QVBoxLayout()

        self.employees_table = QTableWidget()
        layout.addWidget(self.employees_table)

        button_layout = QHBoxLayout()
        self.create_employee_button = QPushButton("Создать сотрудника")
        self.create_employee_button.clicked.connect(self.open_create_employee_dialog)
        button_layout.addWidget(self.create_employee_button)

        self.delete_employee_button = QPushButton("Удалить сотрудника")
        self.delete_employee_button.clicked.connect(self.delete_employee)
        button_layout.addWidget(self.delete_employee_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.employees_table.cellDoubleClicked.connect(self.edit_employee)

        self.load_employees()

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

    def load_employees(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM employers"
                    cursor.execute(sql)
                    employees = cursor.fetchall()

                    self.employees_table.setRowCount(len(employees))
                    self.employees_table.setColumnCount(8)
                    self.employees_table.setHorizontalHeaderLabels([
                        'ID_employer', 'Login', 'Password', 'First Name', 
                        'Middle Name', 'Last Name', 'Phone Number', 'E-mail'
                    ])

                    for row_index, employee in enumerate(employees):
                        for col_index, data in enumerate(employee):
                            self.employees_table.setItem(row_index, col_index, QTableWidgetItem(str(data)))

                    self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except pymysql.MySQLError as e:
                print(f"Error querying the database: {e}")
            finally:
                connection.close()

    def open_create_employee_dialog(self):
        dialog = CreateEmployeeDialog(self)
        dialog.exec()
        self.load_employees()

    def delete_employee(self):
        selected_row = self.employees_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an employee to delete.")
            return

        employee_id = self.employees_table.item(selected_row, 0).text()

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "DELETE FROM employers WHERE ID_employer = %s"
                    cursor.execute(sql, (employee_id,))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Employee deleted successfully.")
            except pymysql.MySQLError as e:
                print(f"Error deleting the employee: {e}")
            finally:
                connection.close()

        self.load_employees()

    def edit_employee(self, row, column):
        employee_data = [self.employees_table.item(row, col).text() for col in range(self.employees_table.columnCount())]
        dialog = EditEmployeeDialog(self, *employee_data)
        dialog.exec()
        self.load_employees()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class CreateEmployeeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Создать сотрудника")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        self.fields = {}
        labels = ['Login', 'Password', 'First Name', 'Middle Name', 'Last Name', 'Phone Number', 'E-mail']
        for label in labels:
            lbl = QLabel(f"{label}:")
            layout.addWidget(lbl)
            line_edit = QLineEdit()
            layout.addWidget(line_edit)
            self.fields[label] = line_edit

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_employee)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_employee(self):
        data = {label: field.text() for label, field in self.fields.items()}

        # Check only required fields
        required_fields = ['First Name', 'Last Name', 'Phone Number', 'E-mail']
        if any(not data[field] for field in required_fields):
            QMessageBox.warning(self, "Warning", "Please fill in all required fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO employers (login, password, first_name, middle_name, last_name, phone_number, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        data['Login'] or None,
                        data['Password'] or None,
                        data['First Name'],
                        data['Middle Name'] or None,
                        data['Last Name'],
                        data['Phone Number'],
                        data['E-mail']
                    ))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Employee created successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error creating the employee: {e}")
            finally:
                connection.close()

class EditEmployeeDialog(QDialog):
    def __init__(self, parent=None, ID_employer=None, login=None, password=None, first_name=None, middle_name=None, last_name=None, phone_number=None, email=None):
        super().__init__(parent)

        self.ID_employer = ID_employer

        self.setWindowTitle("Edit Employee")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        self.fields = {}
        labels = ['Login', 'Password', 'First Name', 'Middle Name', 'Last Name', 'Phone Number', 'E-mail']
        values = [login, password, first_name, middle_name, last_name, phone_number, email]
        for label, value in zip(labels, values):
            lbl = QLabel(f"{label}:")
            layout.addWidget(lbl)
            line_edit = QLineEdit(value)
            layout.addWidget(line_edit)
            self.fields[label] = line_edit

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_employee)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_employee(self):
        data = {label: field.text() for label, field in self.fields.items()}

        if any(not value for value in data.values()):
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = "UPDATE employers SET login = %s, password = %s, first_name = %s, middle_name = %s, last_name = %s, phone_number = %s, email = %s WHERE ID_employer = %s"
                    cursor.execute(sql, (*data.values(), self.ID_employer))
                    connection.commit()
                    QMessageBox.information(self, "Success", "Employee updated successfully.")
                    self.accept()
            except pymysql.MySQLError as e:
                print(f"Error updating the employee: {e}")
            finally:
                connection.close()
                
class RecordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Создать запись")
        self.setFixedSize(700, 700)

        layout = QVBoxLayout()

        # Input fields with labels
        self.fields = {}
        labels = ['First Name', 'Middle Name', 'Last Name', 'Phone Number', 'Date Record']
        for label in labels:
            lbl = QLabel(f"{label}:")
            layout.addWidget(lbl)
            if label == 'Date Record':
                line_edit = QDateEdit()
                line_edit.setCalendarPopup(True)
            else:
                line_edit = QLineEdit()
            layout.addWidget(line_edit)
            self.fields[label] = line_edit

        # Dropdowns
        self.animals_dropdown = QComboBox()
        layout.addWidget(QLabel("Animal:"))
        layout.addWidget(self.animals_dropdown)

        self.services_dropdown = QComboBox()
        layout.addWidget(QLabel("Service:"))
        layout.addWidget(self.services_dropdown)

        self.employers_dropdown = QComboBox()
        layout.addWidget(QLabel("Employer:"))
        layout.addWidget(self.employers_dropdown)

        # Price field
        self.price_label = QLabel("Price: 0")
        layout.addWidget(self.price_label)

        # Buttons
        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.create_record)
        layout.addWidget(self.create_button)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.load_dropdowns()
        self.services_dropdown.currentIndexChanged.connect(self.update_price)
        self.animals_dropdown.currentIndexChanged.connect(self.update_price)

        # Apply consistent stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QDateEdit, QComboBox {
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

    def load_dropdowns(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Load animals
                    cursor.execute("SELECT ID_animals, name, price FROM animals")
                    animals = cursor.fetchall()
                    for animal in animals:
                        self.animals_dropdown.addItem(f"{animal[1]} ({animal[2]})", (animal[0], animal[2]))

                    # Load services
                    cursor.execute("SELECT ID_service, name, price FROM service")
                    services = cursor.fetchall()
                    for service in services:
                        self.services_dropdown.addItem(f"{service[1]} ({service[2]})", (service[0], service[2]))

                    # Load employers
                    cursor.execute("SELECT ID_employer, first_name, last_name FROM employers")
                    employers = cursor.fetchall()
                    for employer in employers:
                        self.employers_dropdown.addItem(f"{employer[1]} {employer[2]}", employer[0])
            except pymysql.MySQLError as e:
                print(f"Error loading dropdowns: {e}")
            finally:
                connection.close()

    def update_price(self):
        animal_price = self.animals_dropdown.currentData()[1] if self.animals_dropdown.currentData() else 0
        service_price = self.services_dropdown.currentData()[1] if self.services_dropdown.currentData() else 0
        total_price = animal_price + service_price
        self.price_label.setText(f"Price: {total_price}")

    def create_record(self):
        first_name = self.fields['First Name'].text()
        middle_name = self.fields['Middle Name'].text()
        last_name = self.fields['Last Name'].text()
        date_record = self.fields['Date Record'].date().toString("yyyy-MM-dd")
        phone_number = self.fields['Phone Number'].text()
        ID_animals = self.animals_dropdown.currentData()[0]
        ID_service = self.services_dropdown.currentData()[0]
        ID_employer = self.employers_dropdown.currentData()
        animal_price = self.animals_dropdown.currentData()[1]
        service_price = self.services_dropdown.currentData()[1]
        total_price = animal_price + service_price

        if not first_name or not last_name or not phone_number:
            QMessageBox.warning(self, "Warning", "Please fill in all required fields.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Insert price into the price table
                    cursor.execute("INSERT INTO price (price) VALUES (%s)", (total_price,))
                    connection.commit()
                    price_id = cursor.lastrowid

                    # Insert record into the record table
                    sql = """
                    INSERT INTO record (first_name, middle_name, last_name, date_record, phone_number, ID_animals, ID_service, ID_employer, price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (first_name, middle_name, last_name, date_record, phone_number, ID_animals, ID_service, ID_employer, price_id))
                    connection.commit()

                    QMessageBox.information(self, "Success", "Record created successfully.")
                    self.go_back()
            except pymysql.MySQLError as e:
                print(f"Error creating the record: {e}")
            finally:
                connection.close()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

class ScheduleWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Расписание")
        self.setFixedSize(990, 700)

        layout = QVBoxLayout()

        self.orders_table = QTableWidget()
        layout.addWidget(self.orders_table)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.load_orders()

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


    def load_orders(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    sql = """
                    SELECT r.last_name, r.first_name, r.middle_name, r.date_record, r.phone_number,
                           a.name AS animal_name, s.name AS service_name, e.first_name AS employer_first_name,
                           e.last_name AS employer_last_name, p.price
                    FROM record r
                    JOIN animals a ON r.ID_animals = a.ID_animals
                    JOIN service s ON r.ID_service = s.ID_service
                    JOIN employers e ON r.ID_employer = e.ID_employer
                    JOIN price p ON r.price = p.ID_price
                    """
                    cursor.execute(sql)
                    orders = cursor.fetchall()

                    self.orders_table.setRowCount(len(orders))
                    self.orders_table.setColumnCount(10)
                    self.orders_table.setHorizontalHeaderLabels([
                        'Last_name', 'First_name', 'Middle_name', 'Date', 'Phone Number',
                        'Animal', 'Service', 'Employer First Name', 'Employer Last Name', 'Price'
                    ])

                    for row_index, order in enumerate(orders):
                        for col_index, data in enumerate(order):
                            self.orders_table.setItem(row_index, col_index, QTableWidgetItem(str(data)))

                    self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except pymysql.MySQLError as e:
                print(f"Error querying the database: {e}")
            finally:
                connection.close()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
        
class ReportWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Отчёт")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()

        # Year selection
        self.year_label = QLabel("Выберите год:")
        layout.addWidget(self.year_label)

        self.year_dropdown = QComboBox()
        self.load_years()
        layout.addWidget(self.year_dropdown)

        # Chart area
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Visitors count
        self.visitors_label = QLabel("Количество посетителей: 0")
        layout.addWidget(self.visitors_label)

        # Back button
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Connect year selection change to update chart
        self.year_dropdown.currentIndexChanged.connect(self.update_chart)

        # Initial chart load
        self.update_chart()

        # Apply consistent stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QComboBox {
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

    def load_years(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT YEAR(date_record) FROM record")
                    years = cursor.fetchall()
                    for year in years:
                        self.year_dropdown.addItem(str(year[0]))
            except pymysql.MySQLError as e:
                print(f"Error loading years: {e}")
            finally:
                connection.close()

    def update_chart(self):
        selected_year = self.year_dropdown.currentText()
        if not selected_year:
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Query for monthly revenue
                    sql = """
                    SELECT MONTH(date_record) AS month, SUM(p.price) AS revenue
                    FROM record r
                    JOIN price p ON r.price = p.ID_price
                    WHERE YEAR(date_record) = %s
                    GROUP BY month
                    """
                    cursor.execute(sql, (selected_year,))
                    data = cursor.fetchall()

                    # Prepare data for plotting
                    months = [month for month, _ in data]
                    revenue = [rev for _, rev in data]

                    # Plotting
                    self.figure.clear()
                    ax = self.figure.add_subplot(111)
                    ax.bar(months, revenue, color='blue')
                    ax.set_title(f"Выручка за {selected_year}")
                    ax.set_xlabel("Месяц")
                    ax.set_ylabel("Выручка")
                    ax.set_xticks(range(1, 13))
                    ax.set_xticklabels(['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'])
                    self.canvas.draw()

                    # Query for visitors count
                    cursor.execute("SELECT COUNT(*) FROM record WHERE YEAR(date_record) = %s", (selected_year,))
                    visitors_count = cursor.fetchone()[0]
                    self.visitors_label.setText(f"Количество посетителей: {visitors_count}")

            except pymysql.MySQLError as e:
                print(f"Error updating chart: {e}")
            finally:
                connection.close()

    def go_back(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

# Update the MainWindow to open the EmployeesWindow
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setFixedSize(500, 400)

        self.record_button = QPushButton("Запись", self)
        self.record_button.setGeometry(50, 50, 100, 40)
        self.record_button.clicked.connect(self.open_record_window)

        self.report_button = QPushButton("Отчёт", self)
        self.report_button.setGeometry(200, 50, 100, 40)
        self.report_button.clicked.connect(self.open_report_window)

        self.employees_button = QPushButton("Сотрудники", self)
        self.employees_button.setGeometry(350, 50, 100, 40)
        self.employees_button.clicked.connect(self.open_employees_window)

        self.schedule_button = QPushButton("Расписание", self)
        self.schedule_button.setGeometry(50, 150, 100, 40)
        self.schedule_button.clicked.connect(self.open_schedule_window)

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

    def open_employees_window(self):
        self.employees_window = EmployeesWindow()
        self.employees_window.show()
        self.close()

    def open_animals_window(self):
        self.animals_window = AnimalsWindow()
        self.animals_window.show()
        self.close()

    def open_services_window(self):
        self.services_window = ServicesWindow()
        self.services_window.show()
        self.close()
        
    def open_record_window(self):
        self.record_window = RecordWindow()
        self.record_window.show()
        self.close()

    def open_schedule_window(self):
        self.schedule_window = ScheduleWindow()
        self.schedule_window.show()
        self.close()
        
    def open_report_window(self):
        self.report_window = ReportWindow()
        self.report_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
    
