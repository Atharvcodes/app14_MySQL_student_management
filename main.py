import sys
from PyQt6.QtWidgets import QApplication, \
    QLabel, QWidget, QGridLayout, QLineEdit, \
    QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sqlite3
import mysql.connector


class DatabaseConnection:
    def __init__(self, host="localhost", user="root", password="Atharv.Database", database="school" ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        # Run QMainWindow class
        super().__init__()
        # Set Title of application
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(600)
        self.setFixedHeight(600)
        # Create menu and their actions
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        # Create action
        add_student_action = QAction(QIcon("icons/add.png"), "Add student", self)
        add_student_action.triggered.connect(self.insert)

        search_student_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_student_action.triggered.connect(self.search)
        # Attach the action to its menu
        file_menu_item.addAction(add_student_action)
        edit_menu_item.addAction(search_student_action)
        # Create action
        about_action = QAction("About", self)
        # Attach the action to its menu
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)
        # Table structure
        self.table = QTableWidget()
        # Set number of columns
        self.table.setColumnCount(4)
        # Set labels
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        # Specify the table as central widget
        self.setCentralWidget(self.table)

        # Create and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student_action)

        # Create and add status bar elements
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.addWidget(self.status_bar)

        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

        # 4.1 Detect a cell click and item change
        self.table.cellClicked.connect(self.status_bar.show)
        self.table.itemChanged.connect(self.status_bar.hide)

    def load_data(self):
        # Connect to the DB
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM school.students")
        result = cursor.fetchall()
        # Let's start the count each time from 0 in order to avoid to
        # add existing data to our table
        self.table.setRowCount(0)
        # List of tuples, the first row represents the first student
        # Populate the table
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, column_data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(column_data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Courses widget
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile Phone")
        layout.addWidget(self.mobile)

        # Submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s,%s,%s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search1)
        layout.addWidget(button)

        self.setLayout(layout)

    def search1(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        row = list(result)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)
        self.close()
        cursor.close()
        connection.close()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        index = main_window.table.currentRow()
        # Get Student name from selected row
        student_name = main_window.table.item(index, 1).text()
        self.student_id = main_window.table.item(index, 0).text()
        # Student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Courses widget
        cousre_name =  main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(cousre_name)
        layout.addWidget(self.course_name)

        # Mobile widget
        mobile_num = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile_num)
        self.mobile.setPlaceholderText("Mobile Phone")
        layout.addWidget(self.mobile)

        # Edit button
        button = QPushButton("Edit")
        button.clicked.connect(self.edit_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def edit_student(self):
        edited_name = self.student_name.text()
        edited_course = self.course_name.itemText(self.course_name.currentIndex())
        edited_number = self.mobile.text()
        student_id = self.student_id
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (edited_name, edited_course, edited_number, student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()

        delete_lable = QLabel("Do you really want to delete this student?")
        layout.addWidget(delete_lable, 0, 0, 1, 2)
        yes_button = QPushButton("Yes")
        no_button = QPushButton("No")
        if no_button.clicked:
            no_button.clicked.connect(self.not_delete_student)
        if yes_button.clicked:
            yes_button.clicked.connect(self.delete_student)

        layout.addWidget(yes_button, 1, 0)
        layout.addWidget(no_button, 1, 1)
        self.setLayout(layout)

    def delete_student(self):
        # Get id from selected row
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record was deleted")
        confirmation_widget.exec()

    def not_delete_student(self):
        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("Record was not deleted")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        A Student Management System is a comprehensive software solution designed to streamline the administrative processes of 
        educational institutions. 
        It encompasses features such as student information management, enrollment, and registration, class scheduling, 
        attendance tracking, grading, and transcript generation.
        Additionally, it facilitates communication between students, teachers, and parents, manages financial transactions, 
        oversees library resources, handles examinations, and provides role-based access control. The system aims to enhance efficiency, 
        communication, and data-driven decision-making within educational institutions, contributing to a more organized and effective learning environment.
        """
        self.setText(content)


# In order to execute our app we need to instantiate QApplication
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
