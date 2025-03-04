import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel

class MockSerial:
    def __init__(self, port, baudrate, output_widget=None):
        self.port = port
        self.baudrate = baudrate
        self.dsr = False
        self.output_widget = output_widget

    def write(self, data):
        message = f"Mock write to {self.port}: {data}"
        print(message)
        if self.output_widget:
            self.output_widget.setText(message)

    def getDSR(self):
        return self.dsr

    def close(self):
        message = f"Mock close {self.port}"
        print(message)
        if self.output_widget:
            self.output_widget.setText(message)

    def set_dsr(self, state):
        self.dsr = state

# Use the mock serial class if running in a test environment
if 'test' in sys.argv:
    Serial = MockSerial
else:
    import serial
    Serial = serial.Serial

# Initialize serial ports for both stepper motors
ser1 = Serial('COM9', 9600)  # Replace 'COM9' with your port name
ser2 = Serial('COM10', 9600)  # Replace 'COM10' with your second port name

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
    for step_index in range(steps):
        for step in sequence:
            if read_micro_switch(serial_port):
                print("Micro switch triggered, stopping motor")
                return
            command = ''.join(str(bit) for bit in step) + '\n'
            serial_port.write(command.encode())
            time.sleep(0.002)  # Adjust speed here
            # Update the output display with the current step
            if serial_port.output_widget:
                serial_port.output_widget.setText(f"Step {step_index + 1}/{steps}")

class StepperControl(QWidget):
    def __init__(self):
        super().__init__()
        self.ra_position = 0
        self.dec_position = 0
        self.ra_reference = 0
        self.dec_reference = 0
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Input for RA step size
        self.ra_step_input = QLineEdit("10")
        layout.addWidget(QLabel("RA Step Increment (degrees):"))
        layout.addWidget(self.ra_step_input)
        
        # RA Controls
        ra_layout = QHBoxLayout()
        ra_minus_fine = QPushButton("RA - Fine")
        ra_plus_fine = QPushButton("RA + Fine")
        ra_minus_coarse = QPushButton("RA - Coarse")
        ra_plus_coarse = QPushButton("RA + Coarse")
        ra_minus_fine.clicked.connect(lambda: self.move_ra(-1, fine=True))
        ra_plus_fine.clicked.connect(lambda: self.move_ra(1, fine=True))
        ra_minus_coarse.clicked.connect(lambda: self.move_ra(-1, fine=False))
        ra_plus_coarse.clicked.connect(lambda: self.move_ra(1, fine=False))
        ra_layout.addWidget(ra_minus_fine)
        ra_layout.addWidget(ra_plus_fine)
        ra_layout.addWidget(ra_minus_coarse)
        ra_layout.addWidget(ra_plus_coarse)
        layout.addLayout(ra_layout)
        
        # RA Output display
        self.ra_output_display = QLabel("RA Position: 0")
        layout.addWidget(self.ra_output_display)
        
        # Input for DEC step size
        self.dec_step_input = QLineEdit("10")
        layout.addWidget(QLabel("DEC Step Increment (degrees):"))
        layout.addWidget(self.dec_step_input)
        
        # DEC Controls
        dec_layout = QHBoxLayout()
        dec_minus_fine = QPushButton("DEC - Fine")
        dec_plus_fine = QPushButton("DEC + Fine")
        dec_minus_coarse = QPushButton("DEC - Coarse")
        dec_plus_coarse = QPushButton("DEC + Coarse")
        dec_minus_fine.clicked.connect(lambda: self.move_dec(-1, fine=True))
        dec_plus_fine.clicked.connect(lambda: self.move_dec(1, fine=True))
        dec_minus_coarse.clicked.connect(lambda: self.move_dec(-1, fine=False))
        dec_plus_coarse.clicked.connect(lambda: self.move_dec(1, fine=False))
        dec_layout.addWidget(dec_minus_fine)
        dec_layout.addWidget(dec_plus_fine)
        dec_layout.addWidget(dec_minus_coarse)
        dec_layout.addWidget(dec_plus_coarse)
        layout.addLayout(dec_layout)
        
        # DEC Output display
        self.dec_output_display = QLabel("DEC Position: 0")
        layout.addWidget(self.dec_output_display)
        
        # Datum Set button
        datum_button = QPushButton("Set Datum")
        datum_button.clicked.connect(self.set_datum)
        layout.addWidget(datum_button)
        
        # Set layout
        self.setLayout(layout)
        self.setWindowTitle("Stepper Motor Control")
        
        # Initialize serial ports with output display
        global ser1, ser2
        ser1 = Serial('COM9', 9600, self.ra_output_display)  # Replace 'COM9' with your port name
        ser2 = Serial('COM10', 9600, self.dec_output_display)  # Replace 'COM10' with your second port name
        
    def move_ra(self, direction, fine=True):
        steps = self.get_steps(self.ra_step_input, fine)
        self.ra_position += direction * steps
        t1 = threading.Thread(target=move_motor, args=(ser1, steps, direction))
        t1.start()
        self.update_position_display()
        
    def move_dec(self, direction, fine=True):
        steps = self.get_steps(self.dec_step_input, fine)
        self.dec_position += direction * steps
        t2 = threading.Thread(target=move_motor, args=(ser2, steps, direction))
        t2.start()
        self.update_position_display()
    
    def get_steps(self, step_input, fine):
        try:
            step_size = int(step_input.text())
            return step_size if fine else step_size * 10  # Coarse adjustment is 10 times the fine adjustment
        except ValueError:
            return 10  # Default step size
    
    def set_datum(self):
        self.ra_reference = self.ra_position
        self.dec_reference = self.dec_position
        self.update_position_display()
    
    def update_position_display(self):
        ra_absolute = self.ra_position - self.ra_reference
        dec_absolute = self.dec_position - self.dec_reference
        self.ra_output_display.setText(f"RA Position: {ra_absolute} degrees")
        self.dec_output_display.setText(f"DEC Position: {dec_absolute} degrees")
        
# Create the application
app = QApplication(sys.argv)
window = StepperControl()
window.show()
sys.exit(app.exec())

# Close the serial ports when the application exits
ser1.close()
ser2.close()