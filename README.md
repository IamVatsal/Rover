# Autonomous Rover Project

This repository contains code and modules for building an autonomous rover using a Raspberry Pi. The project integrates a wide range of sensors and actuators to enable autonomous navigation and data collection.

## Features

- **Ultrasonic Sensor**: For distance measurement and obstacle detection
- **IR Sensor**: For line following and proximity sensing
- **IMU (Inertial Measurement Unit)**: For orientation and motion tracking
- **LIDAR Sensor**: For advanced mapping and obstacle avoidance
- **GPS Module**: For global positioning and navigation
- **Camera**: For vision-based tasks and image processing
- **DC Motor Control**: For driving the rover
- **Servo Motor Control**: For steering and sensor actuation
- **Integrated Autonomous System**: Combines all modules for a fully autonomous rover

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/IamVatsal/Rover.git
   cd Rover
   ```
2. **Set up the Python environment**
   - Use the provided `roverEnv` virtual environment or create your own.
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
3. **Connect your hardware**
   - Wire up your sensors and motors according to your Raspberry Pi GPIO pinout.

4. **Run example code**
   - Example for DC motor control: `DC Motor/Control.py`

## Folder Structure

- `DC Motor/` — DC motor control code
- `roverEnv/` — Python virtual environment and dependencies
- `requirements.txt` — Python dependencies

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new sensors, features, or improvements.

## License

This project is licensed under the MIT License.

---

*Created for educational and research purposes.*
