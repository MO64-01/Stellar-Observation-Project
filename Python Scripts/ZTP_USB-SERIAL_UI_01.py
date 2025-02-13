import serial
import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel

# Initialize serial ports for both stepper motors
ser1 = serial.Serial('COM9', 9600)  # Replace 'COM9' with your port name
ser2 = serial.Serial('COM10', 9600)  # Replace 'COM10' with your second port name

step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

def read_micro_switch(serial_port):
    # Read the state of the DSR (Data Set Ready) control line
    return serial_port.getDSR()

def move_motor(serial_port, steps, direction=1):
    sequence = step_sequence if direction == 1 else step_sequence[::-1]
    for _ in range(steps):
        for step in sequence:
            if read_micro_switch(serial_port):
                print("Micro switch triggered, stopping motor")
                return
            command = ''.join(str(bit) for bit in step) + '\n'
            serial_port.write(command.encode())
            time.sleep(0.002)  # Adjust speed here

class StepperControl(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Input for step size
        self.step_input = QLineEdit("10")
        layout.addWidget(QLabel("Step Increment (degrees):"))
        layout.addWidget(self.step_input)
        
        # RA Controls
        ra_layout = QHBoxLayout()
        ra_minus = QPushButton("RA -")
        ra_plus = QPushButton("RA +")
        ra_minus.clicked.connect(lambda: self.move_ra(-1))
        ra_plus.clicked.connect(lambda: self.move_ra(1))
        ra_layout.addWidget(ra_minus)
        ra_layout.addWidget(ra_plus)
        layout.addLayout(ra_layout)
        
        # DEC Controls
        dec_layout = QHBoxLayout()
        dec_minus = QPushButton("DEC -")
        dec_plus = QPushButton("DEC +")
        dec_minus.clicked.connect(lambda: self.move_dec(-1))
        dec_plus.clicked.connect(lambda: self.move_dec(1))
        dec_layout.addWidget(dec_minus)
        dec_layout.addWidget(dec_plus)
        layout.addLayout(dec_layout)
        
        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Stepper Motor Control")
        
    def move_ra(self, direction):
        steps = self.get_steps()
        t1 = threading.Thread(target=move_motor, args=(ser1, steps, direction))
        t1.start()
        
    def move_dec(self, direction):
        steps = self.get_steps()
        t2 = threading.Thread(target=move_motor, args=(ser2, steps, direction))
        t2.start()
    
    def get_steps(self):
        try:
            return int(self.step_input.text())
        except ValueError:
            return 10  # Default step size

# Create the application
app = QApplication(sys.argv)
window = StepperControl()
window.show()
sys.exit(app.exec())

# Close the serial ports when the application exits
ser1.close()
ser2.close()