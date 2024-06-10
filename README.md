

# Laser Control System

This project includes a Python script and a PyQt5-based GUI for controlling and monitoring a laser system using Hardware Abstraction Layer (HAL) and serial communication. The system allows for real-time control and monitoring of various laser parameters, providing a comprehensive solution for laser management.

## Features

- **HAL Integration**: Uses HAL to create and manage pins for laser control and monitoring.
- **Serial Communication**: Communicates with the laser system over a specified serial port.
- **PyQt5 GUI**: Provides a rich graphical interface for user interaction.
- **Real-Time Monitoring**: Displays real-time status and parameters of the laser system.
- **Control Widgets**: Provides widgets for controlling laser parameters such as power, speed, and gas pressures.
- **Logging**: Logs system actions and statuses for debugging and analysis.
- **Error Handling**: Manages communication errors and retries commands as necessary.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages: `PyQt5`, `qtpyvcp`, `pyqtgraph`, `hal`, `pyserial`
- HAL (Hardware Abstraction Layer) setup on your system

### Installation

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/taloot/laser-control-system.git
   cd laser-control-system
   ```

2. **Install Required Packages**:
   Use pip to install the necessary Python packages:
   ```sh
   pip install PyQt5 qtpyvcp pyqtgraph hal pyserial
   ```

3. **Configure HAL**:
   Ensure that the HAL component `lasercomp` is set up and configured correctly on your system.

### Usage

#### Running the Python Script

1. **Configure Serial Port**:
   Update the script to specify the correct serial port for your laser system. Modify the `comPort` variable:
   ```python
   comPort = sys.argv[1]
   ```

2. **Run the Script**:
   Execute the script by providing the serial port as an argument:
   ```sh
   python laser_control.py /dev/ttyUSB0
   ```

3. **Control and Monitor the Laser**:
   - The script will automatically set up HAL pins and start monitoring and controlling the laser.
   - Use the connected system to interact with the HAL pins to control the laser and monitor its parameters.

#### Running the PyQt5 GUI

1. **Run the GUI**:
   Execute the main script to start the GUI:
   ```sh
   python main.py
   ```

2. **Control and Monitor the Laser**:
   - Use the GUI to interact with the laser system.
   - Adjust parameters such as laser power, cut speed, gas pressures, etc.
   - Monitor real-time statuses and ensure the system is operating within desired parameters.

### Code Overview

#### Initialization

- **HAL Component Setup**: Sets up HAL component `lasercomp` and pins for laser control and monitoring.
- **Serial Communication Setup**: Initializes the serial port with specified parameters.
- **PyQt5 GUI Setup**: Initializes and sets up the PyQt5 GUI, including various widgets for control and monitoring.

#### Main Components

- **Python Script**: Handles serial communication and parameter management for the laser system.
- **MyMainWindow Class**: Main window class for the VCP, extends `VCPMainWindow`.
- **Initialization**: Sets up connections between HAL pins and the GUI.

#### HAL Pins

- **Input Pins**: Pins for receiving data from the laser system (e.g., `laserc_velocity_x`, `laserc_velocity_y`).
- **Output Pins**: Pins for sending commands to the laser system (e.g., `laserc_pwm_pwmgen`, `laserc_start_set`).

#### Control and Monitoring

- **Real-Time Updates**: Updates the GUI with real-time data from the laser system.
- **Command Execution**: Sends commands to the laser system based on user input from the GUI.

### Example HAL Pins

- **laserc_arc_on_bit**: Arc on/off status (bit, input).
- **laserc_plasmac_status**: Plasma cutter status (S32, input).
- **laserc_o2_regulator_pwm**: O2 regulator PWM (float, output).
- **laserc_n2_switch_bit**: N2 switch status (bit, output).
- **laserc_cut_speed**: Cut speed (float, output).

### Author

This project is maintained by Taloot.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify this description further to fit your specific needs or preferences. You can copy and paste this directly into your GitHub repository's README file.
