

---

# Laser Control System via HAL and Serial Communication

This Python script is designed to control and monitor a laser system using Hardware Abstraction Layer (HAL) and serial communication. It sets up various pins to control the laser and read its parameters, enabling control via a connected system. The script reads and sets parameters such as laser power, control mode, and temperature sensors, and communicates with the laser hardware over a serial port.

## Features

- **HAL Integration**: Uses HAL to create and manage pins for laser control and monitoring.
- **Serial Communication**: Communicates with the laser system over a specified serial port.
- **Laser Control**: Sets laser power, control mode, and on/off state.
- **Parameter Monitoring**: Reads various parameters from the laser, including temperature sensors, electrical part conditions, and machine time.
- **Error Handling**: Manages communication errors and retries commands as necessary.
- **Logging**: Logs communication data to a file for debugging.

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages: `pyserial`, `hal`
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
   pip install pyserial hal
   ```

3. **Configure Serial Port**:
   Update the script to specify the correct serial port for your laser system. Modify the `comPort` variable:
   ```python
   comPort = sys.argv[1]
   ```

### Usage

1. **Run the Script**:
   Execute the script by providing the serial port as an argument:
   ```sh
   python laser_control.py /dev/ttyUSB0
   ```

2. **Control and Monitor the Laser**:
   - The script will automatically set up HAL pins and start monitoring and controlling the laser.
   - Use the connected system to interact with the HAL pins to control the laser and monitor its parameters.

### Code Overview

#### Initialization

- **HAL Component Setup**: Sets up HAL component and pins for laser control and monitoring.
- **Serial Communication Setup**: Initializes the serial port with specified parameters.

#### Main Loop

- **Enable/Disable Laser**: Monitors the enable pin and controls the laser accordingly.
- **Read Parameters**: Periodically reads various parameters from the laser system.
- **Set Parameters**: Updates laser settings based on the current state of HAL pins.

#### Functions

- **cmd_set(ordercode, databits)**: Sends a command to set a parameter on the laser.
- **cmd_read(ordercode)**: Sends a command to read a parameter from the laser.
- **alarm(alarmbits)**: Updates the alarm status based on received alarm bits.
- **get_parameters()**: Reads and updates all monitored parameters from the laser system.

### Example HAL Pins

- **laser_power_set**: Set the laser power (float, input).
- **laser_control_mode_set**: Set the laser control mode (float, input).
- **laser_onoff_set**: Set the laser on/off state (bit, input).
- **temperature_sensor1**: Temperature sensor 1 (S32, output).
- **temperature_sensor2**: Temperature sensor 2 (S32, output).
- **laser_power_read**: Read the current laser power (S32, output).

### Error Handling

- The script includes basic error handling for serial communication issues.
- Logs communication data to a file for debugging purposes.

### Author

This project is maintained by Taloot.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Feel free to modify this description further to fit your specific needs or preferences. You can copy and paste this directly into your GitHub repository's README file.
