<div align="center">

# 🏥 MediQueue
### Smart Hospital Queue Management System

A desktop-based hospital queue management system built with **Python** and **Tkinter** that replaces traditional paper queues with a digital, priority-based system.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=for-the-badge)
![JSON](https://img.shields.io/badge/Storage-JSON-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

</div>

---

# 📖 Overview

**MediQueue** is a beginner-friendly hospital queue management system developed for **CC 102 – Advanced Computer Programming**.

The application digitizes patient registration and queue management by automatically prioritizing patients based on the severity of their condition. It also provides live queue updates, estimated waiting times, secure staff access, and persistent JSON storage.

---

# ✨ Features

## 👤 Patient Module

- Register patient information
- Generate automatic queue numbers
- Enter:
  - Patient Name
  - Patient ID
  - Contact Number
  - Severity Level
- View the current queue
- Live countdown for estimated waiting time

---

## 👨‍⚕️ Staff Module

- Secure login system
- View all waiting patients
- Call the next patient
- Mark patients as served
- View complete served patient history
- Automatic queue refresh

---

## 🚑 Priority Queue System

Patients are automatically sorted according to medical urgency.

| Priority | Severity | Estimated Consultation |
|----------|----------|------------------------|
| 1 | 🔴 Emergency | 5 minutes |
| 2 | 🟠 Urgent | 10 minutes |
| 3 | 🟢 General | 15 minutes |

Patients with the same priority maintain their original arrival order.

---

# ⏱ Estimated Waiting Time

The application calculates waiting time automatically based on:

- Current queue position
- Patient priority
- Average consultation duration

A live countdown updates every second.

---

# 💾 Data Persistence

MediQueue stores data using JSON files.

| File | Purpose |
|------|---------|
| `patients.json` | Active patient queue |
| `served_history.json` | Permanent record of served patients |

Patient data is automatically saved after every check-in and every completed consultation.

---

# 🔐 Staff Accounts

Default login credentials:

| Username | Password |
|----------|----------|
| admin | admin123 |
| nurse | nurse123 |
| doctor | doc123 |

---

# 🛠 Technologies Used

- Python 3
- Tkinter
- JSON
- Datetime
- OS Module

---

# 📂 Project Structure

```
MediQueue/
│
├── main.py
├── patients.json
├── served_history.json
└── README.md
```

---

# 🚀 How to Run

### Clone the repository

```bash
git clone https://github.com/yourusername/MediQueue.git
```

### Navigate to the project

```bash
cd MediQueue
```

### Run the application

```bash
python main.py
```

---

# 📸 System Workflow

```text
Patient
    │
    ▼
Patient Check-In
    │
    ▼
Priority Assignment
    │
    ▼
Queue Display
    │
    ▼
Staff Login
    │
    ▼
Call Next Patient
    │
    ▼
Mark as Served
    │
    ▼
Save to History
```

---

# 🎯 Learning Objectives

This project demonstrates:

- GUI Programming with Tkinter
- Event-driven programming
- JSON file handling
- Data persistence
- Queue management
- Priority-based sorting
- Form validation
- Modular programming
- Real-time UI updates

---

# 👩‍💻 Author

**Althea Clarine L. Babao**

- BS Computer Science
- Batangas State University
- CC 102 – Advanced Computer Programming

---

# 📄 License

This project is intended for educational purposes.
