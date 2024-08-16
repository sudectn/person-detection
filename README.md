# Person Detection and Counting System

This project is designed to detect and count people from a live RTSP camera feed. It saves captured frames periodically, processes them to count the number of people detected, and generates reports and visualizations based on the detected data.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Running the System](#running-the-system)
  - [Understanding the Output](#understanding-the-output)
- [Files and Directories](#files-and-directories)
- [Notes](#notes)

## Features

- **Frame Extraction**: Periodically captures frames from an RTSP camera feed.
- **Person Detection**: Processes captured frames to detect the number of people present.
- **Real-time Monitoring**: Displays the current number of people detected in a live JSON file.
- **Daily Reporting**: Generates a daily report and graph based on the detections between 08:10 AM and 05:05 PM.
- **Threaded Operation**: Frame capture and detection run concurrently using Python threads.

## Setup

### Requirements

The project requires Python 3.10.14 and the following Python libraries:

- `opencv-python==4.8.0.76`
- `supervision==0.22.0`
- `inference==0.16.0`
- `python-dotenv==0.21.0`
- `matplotlib==3.7.1`
- `numpy==1.24.3`

For the `extraction` module:

- `flask`
- `flask-cors`
- `opencv-python-headless`
- `python-dotenv`
- `requests`

### Installation

1. Clone the repository:

   `git clone https://github.com/yourusername/person-detection-system.git`
   `cd person-detection-system`

2. Install the required Python packages:

    `pip install -r requirements.txt`

  If using the extraction module, install additional dependencies:

    `pip install -r extraction/requirements.txt`
 
## Environment Configuration

Create a .env file in the root and the extraction directories with the following content:

  `CAMERA_USERNAME=your_username`\n
  `CAMERA_PASSWORD=your_password`\n
  `CAMERA_IP=your_camera_ip`\n
  `CAMERA_PORT=554  # Default RTSP port`\n
  `CAMERA_PATH=your_camera_path`\n
  `ROBOFLOW_API_KEY=your_roboflow_api_key`

The ROBOFLOW_API_KEY is required to access the detection model.

## Usage

### Running the System

The system is divided into two main components: `extract_frames.py` and `detect.py`. These can be run separately in different terminals.

1. Running Frame Extraction:

 In one terminal, run:

  `python extract_frames.py`

 This will start capturing frames from the camera and save them to the `image_frames` directory.

2. Running Person Detection:

 In another terminal, run:

  `python detect.py`

 This will process the captured frames, detect the number of people, and update the live JSON files and daily reports.

### Understanding the Output

- **Live Count**: The current number of people detected is saved in output/current_human_count.json.
- **Daily Report**: A JSON file (output/daily_human_count_report.json) containing the average number of people detected per day.
- **Generated Graphs**: Graphs showing the average human count per hour are saved in the output directory.

## Files and Directories

- **`extract_frames.py`**: Captures frames from the RTSP stream.
- **`detect.py`**: Processes captured frames and detects the number of people.
- **`output/`**: Contains all output files, including JSON reports and graphs.
- **`.env`**: Configuration file for camera credentials and settings, including the RoboFlow API key.
- **`requirements.txt`**: Lists the Python dependencies.
- **`extraction/requirements.txt`**: Lists additional dependencies for the extraction module.
  
## Notes

- Ensure the RTSP camera is properly configured and accessible.
- Run `extract_frames.py` and `detect.py` in separate terminals.
- The detection runs between 08:10 AM and 05:05 PM, and the report is generated at the end of the day.
- If you encounter issues with thread synchronization or camera feed access, check the logs for detailed error messages.
