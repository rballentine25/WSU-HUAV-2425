import sys
from PyQt6.QtWidgets import QApplication, QWidget
from pyqt_test import Ui_Form  # Import the generated UI class

class PyQtTestGUI(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Load the UI from motor_ui.py

# Run the application
app = QApplication(sys.argv)
window = PyQtTestGUI()
window.show()
sys.exit(app.exec())
