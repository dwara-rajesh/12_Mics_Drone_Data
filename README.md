# Noise-Based Path Planning For Drones

![GitHub repo size](https://img.shields.io/github/repo-size/dwara-rajesh/12_Mics_Drone_Data)
![GitHub contributors](https://img.shields.io/github/contributors/dwara-rajesh/12_Mics_Drone_Data)
![GitHub forks](https://img.shields.io/github/forks/dwara-rajesh/12_Mics_Drone_Data)
![GitHub stars](https://img.shields.io/github/stars/dwara-rajesh/12_Mics_Drone_Data)
![GitHub issues](https://img.shields.io/github/issues/dwara-rajesh/12_Mics_Drone_Data)
![GitHub license](https://img.shields.io/github/license/dwara-rajesh/12_Mics_Drone_Data)

> **12\_Mics\_Drone\_Data** provides a comprehensive dataset and code framework for collecting and analyzing real-time acoustic and positional data to aid drone path planning with noise and obstacle avoidance.

---

## Table of Contents

* [About the Project](#about-the-project)
* [Framework Overview](#framework-overview)
* [Data Collected](#data-collected)
* [Methodology](#methodology)
* [Folder Structure](#folder-structure)
* [Getting Started](#getting-started)
* [Dependencies](#dependencies)
* [Future Work](#future-work)
* [Contributing](#contributing)
* [License](#license)

---

## About the Project

This repository serves to provide a basic understanding of how to use the data collection framework. It runs on **ROS2 Foxy** and enables testing of noise-sensitive path planning algorithms for drones using real-time acoustic and positional data.

The goal is to enable testing of advanced algorithms like **RRT\*** and **CLF-CBF** that optimize drone trajectories for reduced noise pollution in urban environments.

---

## Framework Overview

The data collection framework incorporates **3 Python scripts** that collect and process different types of data:

* **`mic12_Audio_capture.py`**
  Creates 12 publishers (one per microphone) to publish audio data to topics `db_data1` to `db_data12` every 0.1 seconds. It starts 12 threads and input streams for simultaneous recording. Data is buffered in 15-second chunks saved as temporary `.bin` files. Upon shutdown, these are converted to `.wav` files.

* **`mic12_CSV_logger.py`**
  Subscribes to microphone and Tello positions from VRPN client nodes, and to audio data from the `db_dataX` topics. Computes decibel values for each microphone every 0.1 seconds and logs decibels, positions, and distances to a CSV file.

* **`mic12_Audio_plotter.py`**
  Subscribes to audio data topics and provides live visualization of audio levels from all 12 microphones using matplotlib subplots.

* **`tellocontroller.py`**
  Used to command the drone along predefined paths (e.g., `move_forward(x)`, `rotate_counter_clockwise(90)`).

All scripts are launched simultaneously using a **ROS2 launch file package**.

---

## Data Collected

* **CSV files** containing timestamps, positions, distances, and decibel levels
* **Audio files** (.wav) from each test condition
* **Plots** visualizing amplitude, decibel, and distance over time

👉 [Audio recordings (Google Drive)](https://drive.google.com/drive/folders/1ETiRap-WsGVU20p-wLtL3Vm5_B1fDa9M?usp=sharing)

---

## Methodology

* 12 microphones positioned at various heights and locations
* Motion capture (Motive) for positional tracking
* ROS1-ROS2 bridge for communication
* Python scripts for data collection, logging, and plotting
* Tests under different environmental setups (normal, dampened, various heights, mic caps on/off)

---

## Folder Structure

```
12_Mics_Drone_Data/
├── CSVs/                # CSV data for experiments
├── audio/                # Audio files or external links
├── scripts/              # Python scripts
├── launch/               # ROS2 launch files
└── README.md             # Documentation
```

---

## Getting Started

### Prerequisites

* ROS2 Foxy
* ROS1 Noetic
* Python 3.x

### Running the framework

```bash
ros2 launch launch/mic12_data_collection.launch.py
```

Or run individual scripts:

```bash
python scripts/mic12_Audio_capture.py
python scripts/mic12_CSV_logger.py
python scripts/mic12_Audio_plotter.py
```

---

## Dependencies

* ROS1 / noetic
* ROS2 / foxy
* sounddevice
* rclpy
* std\_msgs
* threading
* scipy.io
* matplotlib
* geometry\_msgs
* csv
* datetime
* time
* djitellopy

---

## Future Work

* Extend testing to outdoor environments
* Integrate machine learning for dynamic noise prediction
* Improve synchronization between data streams
* Upgrade microphone hardware

---

## Contributing

Contributions are welcome! Fork the repo, create issues, or submit pull requests.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
