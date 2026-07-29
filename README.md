# 🏠 Smart Campus Hostel Mess Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CSV](https://img.shields.io/badge/Storage-CSV-2E8B57?style=for-the-badge)
![SMTP](https://img.shields.io/badge/Email-Gmail_SMTP-EA4335?style=for-the-badge&logo=gmail&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20Google%20Colab-blue?style=for-the-badge)

### A Python-based command-line application for efficient hostel mess management with CSV storage and Gmail SMTP notifications.

</div>

---

## 📖 Overview

The **Smart Campus Hostel Mess Management System** is a lightweight command-line application developed in **Python** to automate day-to-day hostel mess operations. It helps administrators manage student records, maintain the weekly menu, record meal attendance, handle complaints, and generate monthly bills through a simple menu-driven interface.

The application stores all information in CSV files, making it easy to use without requiring any external database. Optional Gmail SMTP integration allows automatic email notifications for complaints and billing.

---

## ✨ Features

- 👨‍🎓 Student Registration and Management
- 🍽 Weekly Mess Menu Management
- ✅ Meal Attendance Recording
- 🚫 Automatic Absent Marking
- 🔄 Duplicate Attendance Detection
- 📢 Complaint Registration and Resolution
- 📧 Automated Gmail Email Notifications
- 💰 Monthly Bill Generation
- 📄 Hostel-wise Bill Export
- 🛡 Robust Error and Exception Handling

---

## 🚀 Application Workflow

```mermaid
flowchart TD

A([Start])
--> B[Configure Gmail SMTP]

B --> C[Initialize CSV Files]

C --> D{Main Menu}

D --> E[Manage Students]

D --> F[Manage Menu]

D --> G[Record Attendance]

D --> H[Manage Complaints]

D --> I[Generate Bills]

D --> J([Exit])

E --> D
F --> D
G --> D
H --> D
I --> D
```

---

## 🏗 System Architecture

```mermaid
flowchart LR

User --> CLI

CLI --> StudentModule
CLI --> MenuModule
CLI --> AttendanceModule
CLI --> ComplaintModule
CLI --> BillingModule

StudentModule --> CSV[(students.csv)]

AttendanceModule --> CSV2[(attendance.csv)]

ComplaintModule --> CSV3[(complaints.csv)]

BillingModule --> CSV4[(hostel_bills.csv)]

ComplaintModule --> SMTP

BillingModule --> SMTP

SMTP --> Gmail
```

---

## 👨‍🎓 Student Management

```mermaid
flowchart TD

A[Enter Student Details]

A --> B{Duplicate Roll Number?}

B -- Yes --> C[Reject Entry]

B -- No --> D[Save Student]

D --> E[Student Added Successfully]
```

---

## 🍽 Attendance Management

```mermaid
flowchart TD

A[Enter Date]

A --> B[Choose Meal]

B --> C[Enter Present Roll Numbers]

C --> D{Attendance Already Exists?}

D -- Yes --> E[Ask for Overwrite]

E -- Yes --> F[Delete Previous Attendance]

F --> G

D -- No --> G[Validate Roll Numbers]

G --> H[Save Present Students]

H --> I[Automatically Mark Remaining Students Absent]

I --> J[Attendance Recorded]
```

---

## 📢 Complaint Management

```mermaid
flowchart TD

A[Student Submits Complaint]

A --> B[Validate Roll Number]

B --> C[Generate Complaint ID]

C --> D[Save Complaint]

D --> E[Send Confirmation Email]

E --> F[Complaint Open]

F --> G[Resolve Complaint]

G --> H[Update Status]

H --> I[Send Resolution Email]
```

---

## 💰 Bill Generation

```mermaid
flowchart TD

A[Select Student]

A --> B[Read Attendance]

B --> C[Count Meals]

C --> D[Calculate Charges]

D --> E[Generate Bill]

E --> F[Send Email]

E --> G[Export Hostel Bill CSV]
```

---

## 📂 Project Structure

```text
Smart-Campus-Hostel-Mess-Management/
│
├── 2401CS09_CS3103_Lab1.py
├── students.csv
├── attendance.csv
├── complaints.csv
├── hostel_bills_YYYY-MM.csv
├── README.md
└── Rahul_Kumar_Sahoo_2401CS09_lab_1_28_07_2026.pdf
```

---

## 🛠 Technologies Used

- Python 3
- CSV Module
- Dataclasses
- Pathlib
- Datetime
- Gmail SMTP
- MIMEText
- Getpass
- Object-Oriented Programming
- Exception Handling

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/Smart-Campus-Hostel-Mess-Management.git
```

Navigate to the project directory

```bash
cd Smart-Campus-Hostel-Mess-Management
```

Run the application

```bash
python 2401CS09_CS3103_Lab1.py
```

---

## 📧 Gmail SMTP Configuration

At startup, the application optionally asks for:

- Gmail Address
- Gmail App Password

If you do not wish to enable email notifications, simply press **Enter** twice to continue.

---

## 📊 Billing Formula

```text
Total Bill = Base Charge + (Meals Consumed × Per Meal Rate)
```

Example

```text
Base Charge      : ₹2500
Meals Consumed   : 12
Per Meal Charge  : ₹65

Total Bill = ₹2500 + (12 × ₹65)
           = ₹3280
```

---

## 🔒 Error Handling

The application safely handles:

- Duplicate Roll Numbers
- Duplicate Attendance Records
- Invalid Dates
- Invalid Meal Types
- Unknown Student IDs
- Missing Attendance Records
- CSV Read/Write Errors
- SMTP Failures
- Keyboard Interrupts

---

## 🚀 Future Improvements

- SQLite/MySQL Database Support
- User Authentication
- Web-Based Dashboard
- QR Code Attendance
- Mobile Application
- Online Payment Gateway
- Analytics Dashboard
- Hostel Inventory Management
- Multi-Hostel Support

---

## 👨‍💻 Author

**Rahul Kumar Sahoo**

B.Tech in Computer Science and Engineering

Indian Institute of Technology Patna

---

<div align="center">

## 🌸 ଜୟ ଜଗନ୍ନାଥ 🌸

**May Lord Jagannath bless everyone with wisdom, happiness, and success.**

If you found this project useful, consider giving it a ⭐ on GitHub.

**Made with ❤️ and Python 🐍**

</div>
