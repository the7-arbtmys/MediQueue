"""
MediQueue: Smart Hospital Queue System
=======================================
MediQueue is a beginner-friendly Python desktop application built
using Tkinter. It replaces traditional paper-based hospital queues
with a digital system that prioritizes patients based on the severity
of their condition: Emergency → Urgent → General.

The system provides real-time queue updates, estimated waiting times,
and persistent data storage using JSON.


Course   : CC 102 - Advanced Computer Programming
Section  : CS 1205
Student  : Babao, Althea Clarine L.
SR-Code  : 25-03188

"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json, os


# ─── GLOBAL DATA ─────────────────────────────────────────────────────────────

# List that holds all patient records (each patient is a dictionary)
patients = []

# Counter so each patient gets a unique queue number
patient_number = 1

# Staff username and password pairs
staff_accounts = {
    "admin":  "admin123",
    "nurse":  "nurse123",
    "doctor": "doc123",
}

# File where patient records are saved between sessions
DATA_FILE = "patients.json"

# The main tkinter window (set once at the bottom of this file)
root = None

# Shared widget references (clock label, listboxes, etc.)
widgets = {}


# ─── JSON SAVE / LOAD ─────────────────────────────────────────────────────────

def save_patients():
    """
    Save the current patients list to patients.json.

    Because "time" is stored as a datetime object (needed for countdown
    math), we convert it to an ISO-format string before writing so that
    JSON can handle it.  Example: datetime(2026,3,8,14,35,7) becomes
    the string "2026-03-08T14:35:07.123456".

    The file is rewritten from scratch every time a patient checks in
    or is marked as served, so it always reflects the current queue.
    """
    serialisable = []
    for p in patients:
        record = {
            "number":   p["number"],
            "name":     p["name"],
            "id":       p["id"],
            "contact":  p["contact"],
            "severity": p["severity"],
            # Convert datetime object to ISO string for JSON
            "time":     p["time"].isoformat(),
        }
        serialisable.append(record)

    with open(DATA_FILE, "w") as f:
        json.dump(serialisable, f, indent=4)


def load_patients():
    """
    Load patient records from patients.json on startup.

    If the file does not exist yet (first run) or is corrupted,
    the function silently does nothing — patients stays empty.

    The ISO-format time string is converted back into a datetime
    object so format_countdown() can do arithmetic with it.
    """
    global patients, patient_number

    if not os.path.exists(DATA_FILE):
        return

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        loaded = []
        for record in data:
            # Convert the ISO string back into a datetime object
            record["time"] = datetime.fromisoformat(record["time"])
            loaded.append(record)

        patients = loaded

        # Set counter above the highest saved number to avoid duplicates
        if patients:
            patient_number = max(p["number"] for p in patients) + 1

    except (json.JSONDecodeError, KeyError, ValueError):
        # File is damaged — start fresh rather than crashing
        patients = []
        patient_number = 1


# ─── CLOCK ───────────────────────────────────────────────────────────────────

def tick_clock():
    """
    Update the clock label on the current screen every second.
    Uses root.after(1000) so the window never freezes between ticks.
    """
    now = datetime.now().strftime("%I:%M:%S %p")

    if "clock_label" in widgets and widgets["clock_label"].winfo_exists():
        widgets["clock_label"].config(text=now)

    root.after(1000, tick_clock)


# ─── ESTIMATED WAIT TIME (COUNTDOWN) ────────────────────────────────────────

def get_estimated_wait_seconds(patient, patient_list):
    """
    Calculate how many seconds this patient must wait before being seen.

    Adds up the expected service time for every patient ahead in queue:
        Emergency  ->  5 minutes  (300 s)
        Urgent     -> 10 minutes  (600 s)
        General    -> 15 minutes  (900 s)

    Parameters:
        patient      (dict): The patient we are calculating for.
        patient_list (list): The full list of current patients.

    Returns:
        int: Total estimated wait time in seconds.
    """
    sorted_list = sort_by_severity(patient_list)

    time_map = {
        "Emergency":  5 * 60,
        "Urgent":    10 * 60,
        "General":   15 * 60,
    }

    total_seconds = 0
    for p in sorted_list:
        if p == patient:
            break
        total_seconds += time_map[p["severity"]]

    return total_seconds


def format_countdown(start_time, total_seconds):
    """
    Return a "MM:SS" string showing how much wait time is still left.

    Parameters:
        start_time    (datetime): When the patient checked in.
        total_seconds (int)     : Their full estimated wait in seconds.

    Returns:
        str: Remaining time as "MM:SS". Returns "00:00" once elapsed.
    """
    elapsed   = (datetime.now() - start_time).seconds
    remaining = max(total_seconds - elapsed, 0)

    minutes = remaining // 60
    seconds = remaining % 60
    return f"{minutes:02d}:{seconds:02d}"


# ─── AUTO REFRESH ─────────────────────────────────────────────────────────────

def auto_refresh():
    """
    Redraw whichever list is on screen every second so countdowns tick.
    Checks the widgets dictionary for active list references.
    """
    if "patient_listbox" in widgets and widgets["patient_listbox"].winfo_exists():
        refresh_patient_list(widgets["patient_listbox"])

    if "dash_listbox" in widgets and widgets["dash_listbox"].winfo_exists():
        refresh_dashboard_list(
            widgets["dash_listbox"],
            widgets["count_label"]
        )

    root.after(1000, auto_refresh)


# ─── HELPER ──────────────────────────────────────────────────────────────────

def clear_screen():
    """Destroy every widget on the window to prepare for a new screen."""
    for widget in root.winfo_children():
        widget.destroy()
    widgets.clear()


def sort_by_severity(patient_list):
    """
    Return a new list sorted Emergency -> Urgent -> General.
    Python's sorted() is stable so equal-severity patients keep arrival order.
    """
    rank = {"Emergency": 0, "Urgent": 1, "General": 2}
    return sorted(patient_list, key=lambda p: rank[p["severity"]])


# ─── SCREEN 1: ROLE SELECTION ─────────────────────────────────────────────────

def show_role_selection():
    """Opening screen — asks whether the user is a Patient or Staff Member."""
    clear_screen()

    tk.Label(root, text="MediQueue",
             font=("Arial", 22, "bold")).pack(pady=(30, 4))
    tk.Label(root, text="Smart Hospital Queue System",
             font=("Arial", 10)).pack()

    clock = tk.Label(root, font=("Arial", 10), fg="gray")
    clock.pack()
    widgets["clock_label"] = clock

    tk.Frame(root, height=2, bg="gray").pack(fill="x", padx=40, pady=20)

    tk.Label(root, text="Who are you?",
             font=("Arial", 13, "bold")).pack(pady=(0, 16))

    tk.Button(
        root, text="I am a Patient",
        font=("Arial", 11), width=20, height=2,
        bg="green", fg="white", cursor="hand2",
        command=show_patient_screen
    ).pack(pady=6)

    tk.Button(
        root, text="I am a Staff Member",
        font=("Arial", 11), width=20, height=2,
        bg="blue", fg="white", cursor="hand2",
        command=show_staff_login
    ).pack(pady=6)


# ─── SCREEN 2: PATIENT CHECK-IN ───────────────────────────────────────────────

def show_patient_screen():
    """
    Patient check-in form.
    Fields: Name, Patient ID, Contact Number, Severity.
    Shows the live queue with countdown timers below the form.
    """
    clear_screen()

    # Top bar
    top = tk.Frame(root, bg="#2e7d32")
    top.pack(fill="x")

    tk.Label(top, text="Patient Check-in",
             font=("Arial", 13, "bold"),
             bg="#2e7d32", fg="white").pack(side="left", padx=12, pady=8)

    tk.Button(top, text="<- Back",
              command=show_role_selection,
              bg="#2e7d32", fg="white",
              relief="flat", cursor="hand2").pack(side="right", padx=12)

    clock = tk.Label(top, font=("Arial", 10), bg="#2e7d32", fg="white")
    clock.pack(side="right", padx=12)
    widgets["clock_label"] = clock

    # Form
    form = tk.LabelFrame(root, text="Your Information", padx=10, pady=8)
    form.pack(fill="x", padx=12, pady=8)

    tk.Label(form, text="Name:").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(form, width=30)
    name_entry.grid(row=0, column=1, padx=8, pady=3)

    tk.Label(form, text="Patient ID:").grid(row=1, column=0, sticky="w")
    id_entry = tk.Entry(form, width=30)
    id_entry.grid(row=1, column=1, padx=8, pady=3)

    # Contact Number — NEW field
    tk.Label(form, text="Contact No.:").grid(row=2, column=0, sticky="w")
    contact_entry = tk.Entry(form, width=30)
    contact_entry.grid(row=2, column=1, padx=8, pady=3)

    # Severity radio buttons
    tk.Label(form, text="Severity:").grid(row=3, column=0, sticky="nw", pady=4)
    severity_var = tk.StringVar(value="General")

    radio_frame = tk.Frame(form)
    radio_frame.grid(row=3, column=1, sticky="w")

    for level in ["General", "Urgent", "Emergency"]:
        tk.Radiobutton(radio_frame, text=level,
            variable=severity_var, value=level).pack(anchor="w")

    # Check In button
    tk.Button(
        root, text="Check In",
        font=("Arial", 11, "bold"),
        bg="green", fg="white",
        width=20, cursor="hand2",
        command=lambda: do_checkin(
            name_entry, id_entry, contact_entry, severity_var, patient_listbox)
    ).pack(pady=4)

    # Queue list
    tk.Label(root, text="Current Queue:",
             font=("Arial", 10, "bold")).pack()
    patient_listbox = tk.Listbox(root, width=65, height=6)
    patient_listbox.pack(padx=12, pady=4)

    widgets["patient_listbox"] = patient_listbox
    refresh_patient_list(patient_listbox)


def do_checkin(name_entry, id_entry, contact_entry, severity_var, patient_listbox):
    """
    Handle the Check In button click.

    Validates the form, creates a patient record (with contact number),
    appends it to patients, saves to JSON, then refreshes the queue.

    Parameters:
        name_entry     (tk.Entry)    : Name input field.
        id_entry       (tk.Entry)    : Patient ID input field.
        contact_entry  (tk.Entry)    : Contact number input field.
        severity_var   (tk.StringVar): Selected severity level.
        patient_listbox(tk.Listbox)  : List widget to refresh after.
    """
    global patient_number

    name     = name_entry.get().strip()
    pid      = id_entry.get().strip()
    contact  = contact_entry.get().strip()
    severity = severity_var.get()

    # Validation
    if name == "":
        messagebox.showerror("Missing Info", "Please enter your Name.")
        return
    if pid == "":
        messagebox.showerror("Missing Info", "Please enter your Patient ID.")
        return
    if contact == "":
        messagebox.showerror("Missing Info", "Please enter your Contact Number.")
        return
    allowed = set("0123456789 +-")
    if not all(c in allowed for c in contact):
        messagebox.showerror("Invalid Contact",
                             "Contact number should contain digits only.")
        return

    # Build patient record
    # "time" is a full datetime object so format_countdown can do math on it
    new_patient = {
        "number":   patient_number,
        "name":     name,
        "id":       pid,
        "contact":  contact,
        "severity": severity,
        "time":     datetime.now(),
    }

    patients.append(new_patient)
    patient_number += 1

    # Save to JSON immediately
    save_patients()

    queue_num = str(new_patient["number"]).zfill(3)
    messagebox.showinfo(
        "Check-In Successful",
        f"You are now in the queue!\nYour queue number is: #{queue_num}"
    )

    # Clear form for next patient
    name_entry.delete(0, tk.END)
    id_entry.delete(0, tk.END)
    contact_entry.delete(0, tk.END)
    severity_var.set("General")

    refresh_patient_list(patient_listbox)


def refresh_patient_list(patient_listbox):
    """
    Clear and redraw the patient-side queue listbox.
    Shows: queue number, name, severity, live countdown timer.
    Sorted by severity (Emergency first).

    Parameters:
        patient_listbox (tk.Listbox): The listbox widget to update.
    """
    patient_listbox.delete(0, tk.END)

    if not patients:
        patient_listbox.insert(tk.END, "  No patients in queue yet.")
        return

    for p in sort_by_severity(patients):
        total     = get_estimated_wait_seconds(p, patients)
        countdown = format_countdown(p["time"], total)

        line = (
            "  #" + str(p["number"]).zfill(3) +
            "  |  " + p["name"] +
            "  |  " + p["severity"] +
            "  |  Wait: " + countdown
        )
        patient_listbox.insert(tk.END, line)


# ─── SCREEN 3: STAFF LOGIN ────────────────────────────────────────────────────

def show_staff_login():
    """Staff login screen with Username and Password fields."""
    clear_screen()

    top = tk.Frame(root, bg="#1a5f96")
    top.pack(fill="x")

    tk.Label(top, text="Staff Login",
             font=("Arial", 13, "bold"),
             bg="#1a5f96", fg="white").pack(side="left", padx=12, pady=8)

    tk.Button(top, text="<- Back",
              command=show_role_selection,
              bg="#1a5f96", fg="white",
              relief="flat", cursor="hand2").pack(side="right", padx=12)

    clock = tk.Label(top, font=("Arial", 10), bg="#1a5f96", fg="white")
    clock.pack(side="right", padx=12)
    widgets["clock_label"] = clock

    form = tk.LabelFrame(root, text="Enter Your Credentials",
                         padx=20, pady=12)
    form.pack(padx=40, pady=30, fill="x")

    tk.Label(form, text="Username:").grid(row=0, column=0, sticky="w", pady=6)
    username_entry = tk.Entry(form, width=25)
    username_entry.grid(row=0, column=1, padx=10)

    tk.Label(form, text="Password:").grid(row=1, column=0, sticky="w", pady=6)
    password_entry = tk.Entry(form, width=25, show="*")
    password_entry.grid(row=1, column=1, padx=10)

    tk.Button(
        root, text="Login",
        font=("Arial", 11, "bold"),
        bg="blue", fg="white",
        width=16, cursor="hand2",
        command=lambda: do_login(username_entry, password_entry)
    ).pack(pady=10)

    tk.Label(
        root,
        text="Hint: admin / admin123  |  nurse / nurse123  |  doctor / doc123",
        font=("Arial", 8), fg="gray"
    ).pack(pady=4)

    root.bind("<Return>", lambda event: do_login(username_entry, password_entry))


def do_login(username_entry, password_entry):
    """
    Check credentials and go to the staff dashboard if correct.

    Parameters:
        username_entry (tk.Entry): Username field.
        password_entry (tk.Entry): Password field.
    """
    root.unbind("<Return>")

    username = username_entry.get()
    password = password_entry.get()

    if username in staff_accounts and staff_accounts[username] == password:
        messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
        show_staff_dashboard(username)
    else:
        messagebox.showerror("Login Failed",
                             "Wrong username or password. Try again.")


# ─── SCREEN 4: STAFF DASHBOARD ────────────────────────────────────────────────

def show_staff_dashboard(username):
    """
    Staff queue management dashboard.

    Buttons: Call Next Patient | Mark as Served | Refresh
    Columns: #  Name  ID  Contact  Severity  Wait
    The list auto-refreshes every second via auto_refresh().

    Parameters:
        username (str): The logged-in staff member's username.
    """
    clear_screen()

    # Top bar
    top = tk.Frame(root, bg="#1a3a5c")
    top.pack(fill="x")

    tk.Label(
        top,
        text="Staff Dashboard  —  Logged in as: " + username,
        font=("Arial", 11, "bold"),
        bg="#1a3a5c", fg="white"
    ).pack(side="left", padx=12, pady=8)

    tk.Button(top, text="Logout",
              command=show_role_selection,
              bg="#1a3a5c", fg="white",
              relief="flat", cursor="hand2").pack(side="right", padx=12)

    clock = tk.Label(top, font=("Arial", 10), bg="#1a3a5c", fg="white")
    clock.pack(side="right", padx=12)
    widgets["clock_label"] = clock

    # Action buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    dash_listbox_holder = [None]
    count_label_holder  = [None]

    tk.Button(
        btn_frame, text="Call Next Patient",
        font=("Arial", 10, "bold"),
        bg="blue", fg="white",
        width=18, cursor="hand2",
        command=lambda: call_next_patient()
    ).grid(row=0, column=0, padx=8)

    tk.Button(
        btn_frame, text="Mark as Served",
        font=("Arial", 10, "bold"),
        bg="green", fg="white",
        width=18, cursor="hand2",
        command=lambda: serve_next_patient(
            dash_listbox_holder[0], count_label_holder[0])
    ).grid(row=0, column=1, padx=8)

    tk.Button(
        btn_frame, text="Refresh",
        font=("Arial", 10),
        width=10, cursor="hand2",
        command=lambda: refresh_dashboard_list(
            dash_listbox_holder[0], count_label_holder[0])
    ).grid(row=0, column=2, padx=8)

    # Patient count label
    count_label = tk.Label(root, font=("Arial", 9), fg="gray")
    count_label.pack()
    count_label_holder[0] = count_label

    # Column headers — Contact column added
    header = tk.Frame(root, bg="#1a3a5c")
    header.pack(fill="x", padx=12)

    for col_text, col_width in [
        ("#", 5), ("Name", 16), ("ID", 10),
        ("Contact", 13), ("Severity", 10), ("Wait", 7)
    ]:
        tk.Label(
            header,
            text=col_text,
            font=("Arial", 9, "bold"),
            bg="#1a3a5c", fg="white",
            width=col_width, anchor="w"
        ).pack(side="left", padx=2, pady=4)

    # Scrollable patient list
    dash_listbox = tk.Listbox(root, width=76, height=9, font=("Courier", 9))
    dash_listbox.pack(padx=12, pady=4)
    dash_listbox_holder[0] = dash_listbox

    # Store so auto_refresh() updates every second
    widgets["dash_listbox"] = dash_listbox
    widgets["count_label"]  = count_label

    refresh_dashboard_list(dash_listbox, count_label)


def refresh_dashboard_list(dash_listbox, count_label):
    """
    Redraw the staff dashboard listbox.
    Columns: # | Name | ID | Contact | Severity | Wait countdown.
    Sorted by severity (Emergency first), stable for ties.

    Parameters:
        dash_listbox (tk.Listbox): Listbox to update.
        count_label  (tk.Label)  : Label showing patient count.
    """
    dash_listbox.delete(0, tk.END)

    count = len(patients)
    count_label.config(
        text="1 patient in queue" if count == 1
        else f"{count} patients in queue"
    )

    if count == 0:
        dash_listbox.insert(tk.END, "  Queue is empty.")
        return

    for p in sort_by_severity(patients):
        total     = get_estimated_wait_seconds(p, patients)
        countdown = format_countdown(p["time"], total)

        num_col     = "#" + str(p["number"]).zfill(3)
        name_col    = p["name"][:14].ljust(16)
        id_col      = p["id"][:8].ljust(10)
        contact_col = p["contact"][:11].ljust(13)
        sev_col     = p["severity"].ljust(10)
        wait_col    = countdown

        line = ("  " + num_col + "  " + name_col + "  " + id_col +
                "  " + contact_col + "  " + sev_col + "  " + wait_col)
        dash_listbox.insert(tk.END, line)


def call_next_patient():
    """
    Announce the next patient (highest priority) without removing them.
    Pop-up shows: queue number, name, contact number, and severity.
    """
    if not patients:
        messagebox.showinfo("Queue Empty", "There are no patients in the queue.")
        return

    p = sort_by_severity(patients)[0]

    messagebox.showinfo(
        "Now Calling",
        f"Now calling:\n\n"
        f"  #{str(p['number']).zfill(3)}  {p['name']}\n"
        f"  Contact : {p['contact']}\n"
        f"  Severity: {p['severity']}"
    )


def serve_next_patient(dash_listbox, count_label):
    """
    Remove the highest-priority patient from the queue and save to JSON.

    Parameters:
        dash_listbox (tk.Listbox): Listbox to refresh after removal.
        count_label  (tk.Label)  : Count label to refresh after removal.
    """
    if not patients:
        messagebox.showinfo("Queue Empty", "There are no patients in the queue.")
        return

    p = sort_by_severity(patients)[0]
    patients.remove(p)

    # Persist the updated queue immediately
    save_patients()

    queue_num = str(p["number"]).zfill(3)
    messagebox.showinfo(
        "Patient Served",
        f"#{queue_num}  {p['name']} has been served."
    )

    refresh_dashboard_list(dash_listbox, count_label)


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.title("MediQueue - Hospital Queue System")
    root.geometry("520x460")
    root.resizable(False, False)

    # Load any patients saved from a previous session
    load_patients()

    # Start the live clock (runs forever via root.after)
    tick_clock()

    # Start the countdown auto-refresh (runs forever via root.after)
    auto_refresh()

    # Show the opening screen
    show_role_selection()

    root.mainloop()
