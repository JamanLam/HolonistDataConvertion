import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Mapping original measurement names to friendly names
measurement_renames = {
    "/holonist/acc/x": "X Acceleration",
    "/holonist/acc/y": "Y Acceleration",
    "/holonist/acc/z": "Z Acceleration",
    "/holonist/acc/activity": "Acceleration Activity",
    "/holonist/acc/activity/x": "X Acceleration Activity",
    "/holonist/acc/activity/y": "Y Acceleration Activity",
    "/holonist/acc/activity/z": "Z Acceleration Activity",
    
    "/holonist/attitude/x": "X Attitude",
    "/holonist/attitude/y": "Y Attitude",
    "/holonist/attitude/z": "Z Attitude",
    
    "/holonist/rotation/x": "X Rotation",
    "/holonist/rotation/y": "Y Rotation",
    "/holonist/rotation/z": "Z Rotation",
    "/holonist/rotation/activity": "Rotation Activity",
    "/holonist/rotation/activity/x": "X Rotation Activity",
    "/holonist/rotation/activity/y": "Y Rotation Activity",
    "/holonist/rotation/activity/z": "Z Rotation Activity",
    
    "/holonist/userAcc/x": "X User Acceleration",
    "/holonist/userAcc/y": "Y User Acceleration",
    "/holonist/userAcc/z": "Z User Acceleration",
    "/holonist/userAcc/activity": "User Acceleration Activity",
    "/holonist/userAcc/activity/x": "X User Acceleration Activity",
    "/holonist/userAcc/activity/y": "Y User Acceleration Activity",
    "/holonist/userAcc/activity/z": "Z User Acceleration Activity",
    
    "/holonist/gyro/x": "X Gyroscope",
    "/holonist/gyro/y": "Y Gyroscope",
    "/holonist/gyro/z": "Z Gyroscope",
    "/holonist/gyro/activity": "Gyroscope Activity",
    "/holonist/gyro/activity/x": "X Gyroscope Activity",
    "/holonist/gyro/activity/y": "Y Gyroscope Activity",
    "/holonist/gyro/activity/z": "Z Gyroscope Activity",
    
    "/holonist/barometerVerticalSpeed": "Barometer Vertical Speed",
    "/holonist/relativeAltitude": "Relative Altitude",
    "/holonist/atmosphericPressure": "Atmospheric Pressure",
    
    "/postures/Down/match": "Posture Down Match",
    "/postures/Up/match": "Posture Up Match",
    "/postures/Up": "Posture Up"
}

# GUI for File Processing
class CSVFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Holonist Data Converter")

        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar(value="filtered_measurements.csv")

        # UI Components
        self.create_widgets()

    def create_widgets(self):
        # Input File Selection
        tk.Label(self.root, text="Select Input CSV File:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=10, pady=5)

        # Output File Name
        tk.Label(self.root, text="Output CSV Filename:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.output_file, width=50).grid(row=1, column=1, padx=10, pady=5)

        # Measurement Selection
        tk.Label(self.root, text="Select Measurements to Include:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.measurement_vars = {}  # Dictionary to store checkbox variables

        self.measurement_frame = tk.Frame(self.root)
        self.measurement_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        for i, (orig_name, friendly_name) in enumerate(measurement_renames.items()):
            var = tk.BooleanVar(value=True)  # Default all selected
            chk = tk.Checkbutton(self.measurement_frame, text=friendly_name, variable=var)
            chk.grid(row=i // 4, column=i % 4, sticky="w")  # Organize in columns
            self.measurement_vars[orig_name] = var

        # Process Button
        tk.Button(self.root, text="Process CSV", command=self.process_csv).grid(row=4, column=1, pady=10)

    def browse_input_file(self):
        """Opens a file dialog to select the input CSV file."""
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.input_file.set(filename)

    def process_csv(self):
        """Processes the CSV file based on user selections."""
        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid input CSV file.")
            return

        if not output_path.endswith(".csv"):
            output_path += ".csv"

        selected_measurements = [m for m, var in self.measurement_vars.items() if var.get()]

        if not selected_measurements:
            messagebox.showerror("Error", "Please select at least one measurement.")
            return

        # Dictionary to store readings using /time/localtime as the timestamp
        data_dict = {}

        try:
            with open(input_path, mode="r", encoding="utf-8") as file:
                reader = csv.reader(file)
                header = next(reader)  # Read the first row (assuming it contains column names)

                actual_time = None  # Initialize actual_time

                for row in reader:
                    if len(row) < 3:
                        continue  # Skip incomplete rows

                    timestamp, measurement, value = row[0], row[1], row[2]

                    # Capture the actual recording time
                    if measurement == "/time/localtime":
                        actual_time = value  # Update the actual time

                    # Store measurement values only if actual_time has been set
                    if measurement in selected_measurements and actual_time is not None:
                        if actual_time not in data_dict:
                            data_dict[actual_time] = {}

                        data_dict[actual_time][measurement] = value

            # Write the output CSV file with renamed columns
            renamed_columns = ["Actual Time"] + [measurement_renames[m] for m in selected_measurements]
            with open(output_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Write header row
                writer.writerow(renamed_columns)

                # Write data rows
                for actual_time, measurements in sorted(data_dict.items()):  # Sort by time
                    row = [actual_time] + [measurements.get(m, "") for m in selected_measurements]
                    writer.writerow(row)

            messagebox.showinfo("Success", f"Filtered data saved to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVFilterApp(root)
    root.mainloop()
