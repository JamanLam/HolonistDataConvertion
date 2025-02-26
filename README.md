# Holonist Data Converter

A simple Tkinter GUI tool for filtering .holonistRecording sensor data and outputting a cleaned-up CSV. Automatically detects measurement categories (like acceleration, gyroscope, weather, etc.) in the selected log file, lets you choose which categories to keep, and then saves the result to a CSV.

## Features
- Automatic Detection of available measurements in .holonistRecording files.
- Group Selection for easy toggling of measurement sets (acceleration, weather, etc.).
- Tooltip Descriptions to clarify each measurement group.
- CSV Conversion with optional filtering, generating a final CSV containing only chosen columns.

## How to Install & Run
### 🖥️ Windows
1. **Download** `Holonist_Data_Converter.exe`
2. **Double-click** to run (No installation needed)

### 🍏 macOS
1. **Download** `Holonist_Data_Converter.app`
2. **Run** the app (May need permission: *Right-click → Open*)


### 🛠️ Running the Python Script
If you have Python installed:
```bash
python Holonist_Data_Converter.py
