# main.py

# === STANDARD LIB IMPORTS ===
import threading
import time
import argparse
import sys
import os

# === GUI & IMAGE HANDLING IMPORTS ===
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import csv
from datetime import datetime

# === LOCAL IMPORTS ===
import config
import face_detect
import attendance

# === COMMAND LINE ARGUMENTS ===
parser = argparse.ArgumentParser(description="Face Recognition Attendance System")
parser.add_argument("--debug", action="store_true", help="Enable debug print statements")
args = parser.parse_args()

config.DEBUG = args.debug
if config.DEBUG:
    print("[!] DEBUG flag is ON")

# === DETERMINE INITIAL DIRECTORY FOR FILE DIALOGS ===
if getattr(sys, 'frozen', False):
    initial_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    initial_dir = os.path.dirname(os.path.abspath(__file__))

# === GUI SETUP ===
root = tk.Tk()
root.title("Face Recognition Attendance System")

frame_banner = ttk.Frame(root)
frame_banner.pack(side="top", fill="x", pady=10)

label_app_name = tk.Label(
    frame_banner,
    text="Face Recognition Attendance System",
    font=("Arial", 16, "bold"),
    fg="white",
    bg="#1e3d59",
    anchor="w",  # Align left
    padx=20,
    pady=10
)
label_app_name.pack(side="left", fill="x", expand=True)

label_group = tk.Label(
    frame_banner,
    text="Group 5: Kiên, Luân, Nhân",
    font=("Arial", 12),
    fg="white",
    bg="#1e3d59",
    anchor="e",  # Align right
    padx=20,
    pady=13
)
label_group.pack(side="right", fill="x", expand=True)

# Main content frame
frame_content = ttk.Frame(root)
frame_content.pack(fill="both", expand=True, padx=10, pady=10)

# Left side - Video and Class selection
frame_left = ttk.Frame(frame_content)
frame_left.pack(side="left", fill="both", expand=True)

frame_video = ttk.Frame(frame_left)   # Live video frame
frame_video.pack(fill="both", expand=True, pady=10)

# Create a frame for the video and its controls
frame_video_controls = ttk.Frame(frame_video)
frame_video_controls.pack(fill="x", side="bottom", pady=5)

# Add webcam toggle button
btn_toggle_cam = ttk.Button(frame_video_controls, text="Start Camera", command=lambda: toggle_camera(btn_toggle_cam))
btn_toggle_cam.pack(pady=5)

label_video = tk.Label(frame_video)
label_video.pack(fill="both", expand=True)

frame_class = ttk.Frame(frame_left)   # Class selection frame
frame_class.pack(fill="x", pady=10)

label_class = tk.Label(frame_class, text="Select Class:", font=("Arial", 12))
label_class.pack(side="left", padx=5)

class_var = tk.StringVar()
combo_class = ttk.Combobox(frame_class, textvariable=class_var, state="readonly")
combo_class.pack(side="left", fill="x", expand=True, padx=5)

# Right side - Attendance list
frame_right = ttk.Frame(frame_content)
frame_right.pack(side="right", fill="both", expand=True, padx=10)

label_list = tk.Label(frame_right, text="Attendance Status:", font=("Arial", 14))
label_list.pack(pady=10)

# Create a frame for the Treeview and its scrollbar
frame_tree = ttk.Frame(frame_right)
frame_tree.pack(fill="both", expand=True)

# Create Treeview for attendance list
columns = ("Name", "Status")
tree_attendance = ttk.Treeview(frame_tree, columns=columns, show="headings", height=20)
tree_attendance.heading("Name", text="Name")
tree_attendance.heading("Status", text="Status")
tree_attendance.column("Name", width=150)
tree_attendance.column("Status", width=100)
tree_attendance.pack(side="left", fill="both", expand=True)

# Scrollbar for Treeview
scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_attendance.yview)
scrollbar.pack(side="right", fill="y")
tree_attendance.configure(yscrollcommand=scrollbar.set)

# === FUNCTIONS ===
def update_class_list():
    classes = face_detect.get_available_classes()
    combo_class['values'] = classes
    if classes:
        combo_class.set(classes[0])
        on_class_change()

def on_class_change(*args):
    selected_class = class_var.get()
    if selected_class:
        face_detect.set_current_class(selected_class)
        update_attendance_list()

def update_attendance_list():
    # Clear current items
    for item in tree_attendance.get_children():
        tree_attendance.delete(item)
    
    # Get current class attendance
    selected_class = class_var.get()
    if not selected_class:
        return
        
    # Get all students in the class
    students = face_detect.get_class_students(selected_class)
    
    # Add each student to the treeview
    for student in students:
        status = attendance.attendance_log.get(selected_class, {}).get(student, "Absent")
        tree_attendance.insert("", "end", values=(student.replace("_", " "), status))

def toggle_selected_attendance():
    selected = tree_attendance.selection()
    if not selected:
        return
        
    selected_class = class_var.get()
    if not selected_class:
        return
        
    for item in selected:
        student_name = tree_attendance.item(item)['values'][0].replace(" ", "_")
        attendance.toggle_attendance(selected_class, student_name)
    
    update_attendance_list()

def clear_attendance():
    selected_class = class_var.get()
    if selected_class:
        attendance.clear_class(selected_class)
        update_attendance_list()

def export_attendance():
    selected_class = class_var.get()
    if not selected_class:
        return
        
    timestamp = datetime.now().strftime("%d-%m-%Y")
    default_filename = f"{selected_class}_{timestamp}_attendance.csv"
    export_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=default_filename,
        initialdir=initial_dir,
        filetypes=[("CSV files", "*.csv")],
        title="Save Attendance CSV"
    )
    if export_path:
        with open(export_path, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Class", "Student", "Status"])
            for student, status in attendance.get_class_attendance(selected_class):
                writer.writerow([selected_class, student, status])

def on_close(): # Close camera, destroy window
    print("[x] Program closing...")
    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()
    root.destroy()

# === ATTENDANCE CONTROLS ===
frame_button = ttk.Frame(frame_right)
frame_button.pack(pady=10)

btn_export = ttk.Button(frame_button, text="Export", command=export_attendance)
btn_export.pack(side="left", padx=5)

btn_toggle = ttk.Button(frame_button, text="Toggle Status", command=toggle_selected_attendance)
btn_toggle.pack(side="left", padx=5)

# Bind class selection change
combo_class.bind('<<ComboboxSelected>>', on_class_change)

# === CAMERA SETUP ===
camera = None
camera_active = False
current_frame = None
processed_faces = []
frame_lock = threading.Lock()   # Lock to avoid threading race conditions

def init_camera():
    global camera
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return camera.isOpened()

def toggle_camera(button):
    global camera_active, current_frame, camera
    camera_active = not camera_active
    if camera_active:
        if init_camera():
            button.configure(text="Stop Camera")
            if config.DEBUG: print("[✓] Camera ON")
        else:
            camera_active = False
            button.configure(text="Start Camera")
            if config.DEBUG: print("[!] Failed to initialize camera")
    else:
        if camera is not None:
            camera.release()
            camera = None
        button.configure(text="Start Camera")
        current_frame = None
        # Clear the video display
        label_video.configure(image='')
        if config.DEBUG: print("[x] Camera OFF")

def capture_frames():   # Continuously capture frames from camera
    global current_frame
    while True:
        if camera_active and camera is not None and camera.isOpened():
            ret, frame = camera.read()
            if not ret:
                continue
            with frame_lock:
                current_frame = frame.copy()
        time.sleep(0.1)  # Reduced sleep time for more responsive toggle

def process_faces():    # Process frames periodically for face detection/recognition
    global processed_faces
    while True:
        with frame_lock:
            frame = current_frame.copy() if current_frame is not None else None
        if frame is not None:
            processed_faces = face_detect.process_frame(frame)
        time.sleep(0.3) # Wait between processing to reduce load

def update_display():   # Update video frame and draw rectangles + labels
    with frame_lock:
        frame = current_frame.copy() if current_frame is not None else None

    if frame is not None:
        # Draw recognized faces and emotion labels
        for (top, right, bottom, left, name, emotion, just_logged) in processed_faces:
            label = f"{name} ({emotion})"
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 165, 255), 2)
            cv2.rectangle(frame, (left, top - 20), (right, top), (0, 165, 255), -1)
            cv2.putText(frame, label, (left + 6, top - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            if just_logged:
                update_attendance_list()

        # Convert frame to RGB and update Tkinter label
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

    root.after(30, update_display)  # Call again after 30ms to keep updating

# === START THREADS ===
threading.Thread(target=capture_frames, daemon=True).start()
threading.Thread(target=process_faces, daemon=True).start()

# === START GUI MAINLOOP ===
print("[!] Program starting...")
root.protocol("WM_DELETE_WINDOW", on_close)
update_class_list()
update_display()
root.mainloop()
