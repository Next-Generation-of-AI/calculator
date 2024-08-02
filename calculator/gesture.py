import sys
import math
import cv2
import mediapipe as mp
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initGestureRecognition()

    def initUI(self):
        self.setWindowTitle('iPhone Style Calculator')
        self.setGeometry(300, 300, 350, 450)
        self.setStyleSheet("""
            QWidget {
                background-color: #1C1C1E;
            }
            QLineEdit {
                background-color: #000000;
                color: white;
                border: none;
                padding: 20px;
                font-size: 36px;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #2C2C2E;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 20px;
                font-size: 24px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #3A3A3C;
            }
            QPushButton:pressed {
                background-color: #4A4A4C;
            }
            QPushButton.operator {
                background-color: #FF9500;
                color: white;
            }
            QPushButton.operator:hover {
                background-color: #FFB84D;
            }
            QPushButton.operator:pressed {
                background-color: #FF9F00;
            }
            QPushButton.memory {
                background-color: #3A3A3C;
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

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(True)
        layout.addWidget(self.display)

        self.buttons = {}
        button_labels = [
            ['C', '(', ')', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', 'M+'],
            ['M-', 'MR', 'MRC']
        ]

        for row in button_labels:
            h_layout = QHBoxLayout()
            for button_text in row:
                button = QPushButton(button_text)
                self.buttons[button_text] = button
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

        if current_text == 'Error':
            current_text = ''

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
            expr = expr.replace('sqrt', 'math.sqrt')
            return eval(expr, {"__builtins__": None}, {"math": math})
        except:
            return 'Error'

    def initGestureRecognition(self):
        self.capture = cv2.VideoCapture(0)
        self.hands = mp.solutions.hands.Hands()
        self.drawing_utils = mp.solutions.drawing_utils
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                self.detect_gesture(hand_landmarks, frame.shape[1], frame.shape[0])

        cv2.imshow('Hand Gesture Recognition', frame)
        cv2.waitKey(1)

    def detect_gesture(self, hand_landmarks, frame_width, frame_height):
        finger_tips = [4, 8, 12, 16, 20]
        fingers = []

        for tip in finger_tips:
            finger_tip_y = hand_landmarks.landmark[tip].y
            finger_bottom_y = hand_landmarks.landmark[tip - 2].y
            fingers.append(finger_tip_y < finger_bottom_y)

        index_finger_tip = hand_landmarks.landmark[8]
        x = int(index_finger_tip.x * frame_width)
        y = int(index_finger_tip.y * frame_height)

        if fingers[1] and not fingers[2]:
            print("Second finger is up, controlling mouse")
            screen_x, screen_y = pyautogui.size()
            screen_x = int(index_finger_tip.x * screen_x)
            screen_y = int(index_finger_tip.y * screen_y)
            pyautogui.moveTo(screen_x, screen_y)

        if fingers[1] and fingers[2]:
            print("Second and third fingers are up, pressing button")
            screen_x, screen_y = pyautogui.size()
            screen_x = int(index_finger_tip.x * screen_x)
            screen_y = int(index_finger_tip.y * screen_y)
            pyautogui.click(screen_x, screen_y)
            self.simulate_button_press('=')  # This ensures that the button press logic is still handled

    def simulate_button_press(self, button_text):
        if button_text in self.buttons:
            button = self.buttons[button_text]
            button.click()

    def closeEvent(self, event):
        self.timer.stop()
        self.capture.release()
        cv2.destroyAllWindows()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())

