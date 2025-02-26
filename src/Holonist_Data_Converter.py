import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Measurement groups with descriptions for tooltips
measurement_groups = {
    "Acceleration": {
        "data": ["/holonist/acc/x", "/holonist/acc/y", "/holonist/acc/z", "/holonist/acc/activity/x", "/holonist/acc/activity/y", "/holonist/acc/activity/z", "/holonist/acc/activity"],
        "description": "XYZ Acceleration, XYZ Acceleration Activity"
    },
    "User Acceleration": {
        "data": ["/holonist/userAcc/x", "/holonist/userAcc/y", "/holonist/userAcc/z", "/holonist/userAcc/activity/x", "/holonist/userAcc/activity/y", "/holonist/userAcc/activity/z", "/holonist/userAcc/activity"],
        "description": "XYZ User Acceleration, XYZ User Acceleration Activity"
    },
    "Gyroscope": {
        "data": ["/holonist/gyro/x", "/holonist/gyro/y", "/holonist/gyro/z", "/holonist/gyro/activity/x", "/holonist/gyro/activity/y", "/holonist/gyro/activity/z", "/holonist/gyro/activity"],
        "description": "XYZ Gyroscope, XYZ Gyroscope Activity"
    },
    "Rotation": {
        "data": ["/holonist/rotation/x", "/holonist/rotation/y", "/holonist/rotation/z", "/holonist/rotation/activity/x", "/holonist/rotation/activity/y", "/holonist/rotation/activity/z", "/holonist/rotation/activity"],
        "description": "XYZ Rotation, XYZ Rotation Activity"
    },
    "Gravity": {
        "data": ["/holonist/gravity/x", "/holonist/gravity/y", "/holonist/gravity/z"],
        "description": "XYZ Gravity"
    },
    "Attitude": {
        "data": ["/holonist/attitude/x", "/holonist/attitude/y", "/holonist/attitude/z"],
        "description": "XYZ Attitude"
    },
    "Magnetometer": {
        "data": ["/holonist/magn/x", "/holonist/magn/y", "/holonist/magn/z", "/holonist/magn/heading"],
        "description": "XYZ Magnetometer, Magnetometer Heading"
    },
    "Weather": {
        "data": ["/weather/wind/speed", "/weather/wind/speed/min", "/weather/wind/speed/max", "/weather/wind/direction",
                 "/weather/cloud", "/weather/cloud/min", "/weather/cloud/max", "/weather/humidity", "/weather/humidity/min",
                 "/weather/humidity/max", "/weather/pressure", "/weather/pressure/min", "/weather/pressure/max",
                 "/weather/temperature", "/weather/temperature/min", "/weather/temperature/max",
                 "/weather/visibility", "/weather/sunrise", "/weather/sunset", "/weather/night", "/weather/day",
                 "/weather/observationAgeInMinutes", "/weather/sunIsUp"],
        "description": "Temperature, Humidity, Pressure, Wind Speed, Cloud Coverage"
    },
    "Seasons": {
        "data": ["/seasons/spring", "/seasons/summer", "/seasons/autumn", "/seasons/winter"],
        "description": "Spring, Summer, Autumn, Winter"
    },
    "Time": {
        "data": ["/time/countdown_9am", "/time/10minutes", "/time/hour", "/time/30sec", "/time/countdown_5pm", "/time/localtime",
                 "/time/month", "/time/15minutes", "/time/unixtime", "/time/year", "/time/5minutes", "/time/night",
                 "/time/6hours", "/time/countdown_midnight", "/time/week", "/time/minute", "/time/day",
                 "/time/formattedtime", "/time/30minutes", "/time/countdown_noon"],
        "description": "Local Time, Countdown Timers, Formatted Time"
    },
    "Sun": {
        "data": ["/holonist/sun/aim", "/holonist/sun/aimToHeading", "/holonist/sun/aimToElevation", "/holonist/sun/azimuthToHeading", "/holonist/sun/azimuthToElevation"],
        "description": "Sun Aiming, Sun Azimuth to Heading & Elevation"
    },
    "Moon": {
        "data": ["/holonist/moon/aim", "/holonist/moon/aimToHeading", "/holonist/moon/aimToElevation", "/holonist/moon/azimuthToHeading", "/holonist/moon/azimuthToElevation"],
        "description": "Moon Aiming, Moon Azimuth to Heading & Elevation"
    }
}

class CSVFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Movement Filter - Tooltips + Auto-Detection + Output")

        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar(value="filtered_movement.csv")

        # Which groups are displayed (auto-detected). Key = group_name, Value = BooleanVar
        self.measurement_vars = {}
        # All found measurement strings from the file
        self.found_measurements = set()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Input File:").grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.input_file, width=50).grid(
            row=0, column=1, padx=10, pady=5
        )
        tk.Button(self.root, text="Browse", command=self.browse_input_file).grid(
            row=0, column=2, padx=10, pady=5
        )

        tk.Label(self.root, text="Output CSV Filename:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        tk.Entry(self.root, textvariable=self.output_file, width=50).grid(
            row=1, column=1, padx=10, pady=5
        )

        tk.Button(self.root, text="Select All", command=self.select_all).grid(
            row=2, column=0, padx=10, pady=5
        )
        tk.Button(self.root, text="Deselect All", command=self.deselect_all).grid(
            row=2, column=1, padx=10, pady=5
        )

        tk.Label(self.root, text="Select Measurements:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )

        # Frame for the checkboxes (created after auto-detection)
        self.measurement_frame = tk.Frame(self.root)
        self.measurement_frame.grid(
            row=4, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        tk.Button(self.root, text="Convert and Process File", command=self.process_csv).grid(
            row=5, column=1, pady=10
        )

    # ------------------------------------------------------------------------------
    # Auto-detect from the chosen file
    # ------------------------------------------------------------------------------
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Holonist Recording Files", "*.holonistRecording"), ("All Files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            self.detect_available_measurements(filename)
            self.update_checkboxes()

    def detect_available_measurements(self, file_path):
        self.found_measurements.clear()
        try:
            with open(file_path, "r", encoding="utf-8") as infile:
                for line in infile:
                    parts = line.strip().split("\t")
                    if len(parts) == 3:
                        # e.g. "timestamp", "measurement", "value"
                        _, measurement, _ = parts
                        self.found_measurements.add(measurement)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    # ------------------------------------------------------------------------------
    # Create tooltips and checkboxes for auto-detected groups
    # ------------------------------------------------------------------------------
    def update_checkboxes(self):
        # Clear old checkboxes
        for widget in self.measurement_frame.winfo_children():
            widget.destroy()

        self.measurement_vars.clear()

        # Keep only those groups that have at least one measurement found
        valid_groups = {
            g: d for g, d in measurement_groups.items()
            if any(m in self.found_measurements for m in d["data"])
        }

        # Create checkboxes with tooltips
        for i, (group_name, group_info) in enumerate(valid_groups.items()):
            var = tk.BooleanVar(value=True)
            chk = tk.Checkbutton(self.measurement_frame, text=group_name, variable=var)
            chk.grid(row=i // 3, column=i % 3, sticky="w", padx=5, pady=2)

            self.create_tooltip(chk, group_info["description"])
            self.measurement_vars[group_name] = var

    def create_tooltip(self, widget, text):
        """
        Creates a tooltip (hover text) for the given widget.
        """
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()  # Hide initially
        tooltip.overrideredirect(True)
        label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1, padx=5, pady=2)
        label.pack()

        def show_tooltip(event):
            x = event.widget.winfo_rootx() + 20
            y = event.widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def hide_tooltip(_):
            tooltip.withdraw()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    # ------------------------------------------------------------------------------
    # Select All / Deselect All
    # ------------------------------------------------------------------------------
    def select_all(self):
        for var in self.measurement_vars.values():
            var.set(True)

    def deselect_all(self):
        for var in self.measurement_vars.values():
            var.set(False)

    # ------------------------------------------------------------------------------
    # Convert & Process
    # ------------------------------------------------------------------------------
    def process_csv(self):
        input_path = self.input_file.get().strip()
        output_path = self.output_file.get().strip()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid input file.")
            return

        if not output_path.endswith(".csv"):
            output_path += ".csv"

        tmp_csv = self.convert_to_csv(input_path)
        if not tmp_csv:
            return

        self.filter_csv(tmp_csv, output_path)
        messagebox.showinfo("Success", f"Filtered data saved to:\n{output_path}")

    def convert_to_csv(self, input_path):
        """
        Convert the .holonistRecording file to a CSV, storing lines with
        (timestamp, measurement, value). We'll track "Actual Time"
        if we see something like "/time/localtime". Customize as needed.
        """
        csv_path = input_path + ".csv"
        try:
            with open(input_path, "r", encoding="utf-8") as infile, \
                 open(csv_path, "w", newline="", encoding="utf-8") as outfile:

                writer = csv.writer(outfile)
                writer.writerow(["Actual Time", "measurement", "value"])

                actual_time = None
                for line in infile:
                    parts = line.strip().split("\t")
                    if len(parts) == 3:
                        timestamp, measurement, value = parts

                        # If we see a localtime, store it (example logic)
                        if measurement == "/time/localtime":
                            actual_time = value

                        # Only write if we have some actual_time
                        if actual_time is not None:
                            writer.writerow([actual_time, measurement, value])

            return csv_path

        except Exception as e:
            messagebox.showerror("Error", f"Error converting file:\n{str(e)}")
            return None

    def filter_csv(self, input_csv, output_csv):
        """
        Keep only measurements that belong to selected groups.
        Group -> "data" -> actual measurement strings.
        """
        selected_measurements = []
        for group_name, var in self.measurement_vars.items():
            if var.get():
                selected_measurements.extend(measurement_groups[group_name]["data"])

        if not selected_measurements:
            messagebox.showerror("Error", "Please select at least one measurement.")
            return

        data_dict = {}  # { actual_time: { measurement: value, ... } }

        try:
            with open(input_csv, "r", encoding="utf-8") as f_in:
                reader = csv.reader(f_in)
                next(reader)  # skip header

                for row in reader:
                    if len(row) < 3:
                        continue
                    actual_time, measurement, value = row
                    if measurement in selected_measurements:
                        if actual_time not in data_dict:
                            data_dict[actual_time] = {}
                        data_dict[actual_time][measurement] = value

            # Create the header (no rename logic here; we keep measurements as-is)
            header = ["Actual Time"] + selected_measurements

            with open(output_csv, "w", newline="", encoding="utf-8") as f_out:
                writer = csv.writer(f_out)
                writer.writerow(header)

                # Sort by actual_time for consistent order
                for t in sorted(data_dict.keys()):
                    row_measurements = data_dict[t]
                    row = [t] + [row_measurements.get(m, "") for m in selected_measurements]
                    writer.writerow(row)

        except Exception as e:
            messagebox.showerror("Error", f"Error filtering file:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVFilterApp(root)
    root.mainloop()