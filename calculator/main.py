import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('iPhone Style Calculator')
        self.setGeometry(300, 300, 350, 450)
        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1E; /* Background color similar to iPhone calculator */
            }
            QLineEdit {
                background-color: #000000; /* Dark background for the display */
                color: white;
                border: none;
                padding: 20px;
                font-size: 36px;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #2C2C2E; /* Button color */
                color: white;
                border: none;
                border-radius: 30px; /* Rounded buttons */
                padding: 20px;
                font-size: 24px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #3A3A3C; /* Slightly lighter button color on hover */
            }
            QPushButton:pressed {
                background-color: #4A4A4C; /* Even lighter color when pressed */
            }
            QPushButton.operator {
                background-color: #FF9500; /* Distinct color for operators */
                color: white;
            }
            QPushButton.operator:hover {
                background-color: #FFB84D; /* Lighter color for operators on hover */
            }
            QPushButton.operator:pressed {
                background-color: #FF9F00; /* Even lighter color when pressed */
            }
            QPushButton.memory {
                background-color: #3A3A3C; /* Memory buttons have different color */
                color: white;
            }
            QPushButton.memory:hover {
                background-color: #4A4A4C;
            }
            QPushButton.memory:pressed {
                background-color: #5A5A5C;
            }
        """)

        layout = QVBoxLayout()

        # Display
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        # Buttons
        buttons = [
            ['C', '(', ')', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', 'M+'],
            ['M-', 'MR', 'MRC']
        ]

        for row in buttons:
            h_layout = QHBoxLayout()
            for button_text in row:
                button = QPushButton(button_text)
                if button_text in ['/', '*', '-', '+']:
                    button.setProperty('class', 'operator')
                elif button_text in ['M+', 'M-', 'MR', 'MRC']:
                    button.setProperty('class', 'memory')
                button.clicked.connect(self.on_click)
                h_layout.addWidget(button)
            layout.addLayout(h_layout)

        self.setLayout(layout)
        self.memory = 0

    def on_click(self):
        button = self.sender()
        current_text = self.display.text()

        if button.text() == '=':
            try:
                result = self.evaluate_expression(current_text)
                self.display.setText(str(result))
            except Exception as e:
                self.display.setText('Error')
        elif button.text() == 'C':
            self.clear_display()
        elif button.text() == 'M+':
            try:
                self.memory += float(current_text)
                self.display.clear()
            except:
                self.display.setText('Error')
        elif button.text() == 'M-':
            try:
                self.memory -= float(current_text)
                self.display.clear()
            except:
                self.display.setText('Error')
        elif button.text() == 'MR':
            self.display.setText(str(self.memory))
        elif button.text() == 'MRC':
            self.memory = 0
            self.display.clear()
        elif button.text() in ['sqrt', '^', '(', ')']:
            if button.text() == '^':
                self.display.setText(current_text + '**')
            elif button.text() == 'sqrt':
                self.display.setText('math.sqrt(' + current_text + ')')
            else:
                self.display.setText(current_text + button.text())
        else:
            self.display.setText(current_text + button.text())

    def clear_display(self):
        self.display.clear()

    def evaluate_expression(self, expr):
        try:
            # Replace the sqrt keyword with math.sqrt
            expr = expr.replace('sqrt', 'math.sqrt')
            # Evaluate the expression safely
            return eval(expr, {"__builtins__": None}, {"math": math})
        except:
            return 'Error'

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
