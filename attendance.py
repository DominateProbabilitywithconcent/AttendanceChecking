# attendance.py

# === STANDARD LIB IMPORTS ===
from datetime import datetime

# === LOCAL IMPORTS ===
import config

# === Attendance Tracking ===
attendance_log = {}  # { class_name: { student_name: status } }
# Status can be: "Present" or "Absent"

def add(class_name, student_name):  # Mark a student as present
    if class_name not in attendance_log:
        attendance_log[class_name] = {}
    
    if student_name not in attendance_log[class_name] or attendance_log[class_name][student_name] != "Present":
        attendance_log[class_name][student_name] = "Present"
        if config.DEBUG: print(f"[+] Marked {student_name} ({class_name}) as present")
        return True
    return False

def toggle_attendance(class_name, student_name):  # Toggle between Present and Absent
    if class_name not in attendance_log:
        attendance_log[class_name] = {}
    
    current_status = attendance_log[class_name].get(student_name, "Absent")
    new_status = "Present" if current_status == "Absent" else "Absent"
    attendance_log[class_name][student_name] = new_status
    
    if config.DEBUG: print(f"[*] Toggled {student_name} ({class_name}) to {new_status}")

def get_class_attendance(class_name):  # Get attendance status for all students in a class
    if class_name not in attendance_log:
        return []
    
    return [(name, status) for name, status in attendance_log[class_name].items()]

def get_all_attendance():  # Get attendance status for all classes
    return attendance_log

def remove(class_name, student_name):   # Remove a specific student's attendance record
    if class_name in attendance_log and student_name in attendance_log[class_name]:
        del attendance_log[class_name][student_name]
        if config.DEBUG: print(f"[x] Removed {student_name} ({class_name}) from attendance log")

def clear_class(class_name):    # Clear attendance for a specific class
    if class_name in attendance_log:
        attendance_log[class_name].clear()
        if config.DEBUG: print(f"[x] Cleared attendance log for {class_name}")

def clear():    # Clear the entire attendance log
    attendance_log.clear()
    if config.DEBUG: print("[x] Cleared all attendance logs")
