"""
SMART CAMPUS HOSTEL MESS MANAGEMENT SYSTEM
CS3103 - LAB 1

DATA DESIGN
-----------
Student:
    roll_number, name, mailid, hostel

Attendance Record:
    roll_number, date, meal_type, status

Complaint:
    complaint_id, roll_number, date, complaint_text, status

Bill:
    Student monthly bill calculated as:
    BASE_CHARGE + (meals_consumed * PER_MEAL_RATE)

CSV FILES
---------
students.csv:
    roll_number, name, mailid, hostel

attendance.csv:
    roll_number, date, meal_type, status

complaints.csv:
    complaint_id, roll_number, date, complaint_text, status

SMTP SETUP
----------
The program requests SMTP email and Gmail App Password at startup.
Use a Gmail App Password, not your normal Gmail password.
Email failure never prevents CSV data from being saved.
"""

import csv
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from getpass import getpass
from pathlib import Path



# CONSTANTS


BASE_CHARGE = 2500
PER_MEAL_RATE = 65

# Gmail SMTP with STARTTLS is generally more reliable on Colab/networked systems.
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USE_SSL = False

STUDENT_FIELDS = ["roll_number", "name", "mailid", "hostel"]
ATTENDANCE_FIELDS = ["roll_number", "date", "meal_type", "status"]
COMPLAINT_FIELDS = [
    "complaint_id",
    "roll_number",
    "date",
    "complaint_text",
    "status",
]

# Works in VS Code, terminal, Colab and Jupyter.
# For permanent Google Drive storage in Colab, set:
# os.environ["MESS_DATA_DIR"] = "/content/drive/MyDrive/CS3103_Lab1"
try:
    DEFAULT_DATA_FOLDER = Path(__file__).resolve().parent
except NameError:
    DEFAULT_DATA_FOLDER = Path.cwd()

DATA_FOLDER = Path(
    os.getenv("MESS_DATA_DIR", str(DEFAULT_DATA_FOLDER))
)
DATA_FOLDER.mkdir(parents=True, exist_ok=True)

STUDENTS_FILE = DATA_FOLDER / "students.csv"
ATTENDANCE_FILE = DATA_FOLDER / "attendance.csv"
COMPLAINTS_FILE = DATA_FOLDER / "complaints.csv"

WEEKLY_MENU = {
    "Monday": {
        "Breakfast": "Idli, sambar and chutney",
        "Lunch": "Dal fry, rice and vegetable",
        "Dinner": "Paneer masala, roti and salad",
    },
    "Tuesday": {
        "Breakfast": "Poha, banana and tea",
        "Lunch": "Rajma chawal, salad and curd",
        "Dinner": "Mixed vegetable curry, roti and kheer",
    },
    "Wednesday": {
        "Breakfast": "Aloo paratha, curd and pickle",
        "Lunch": "Chole, jeera rice and salad",
        "Dinner": "Dal tadka, roti and vegetable pulao",
    },
    "Thursday": {
        "Breakfast": "Upma, chutney and tea",
        "Lunch": "Kadhi chawal and aloo beans",
        "Dinner": "Soyabean curry, roti and salad",
    },
    "Friday": {
        "Breakfast": "Bread omelette or vegetable sandwich",
        "Lunch": "Sambar rice, papad and salad",
        "Dinner": "Shahi paneer, roti and gulab jamun",
    },
    "Saturday": {
        "Breakfast": "Chole bhature and lassi",
        "Lunch": "Vegetable biryani and raita",
        "Dinner": "Dal makhani, roti and salad",
    },
    "Sunday": {
        "Breakfast": "Dosa, sambar and chutney",
        "Lunch": "Special thali with dessert",
        "Dinner": "Khichdi, curd and papad",
    },
}



# CLASSES


class DuplicateAttendanceError(Exception):
    """Raised when attendance already exists for the same meal session."""


@dataclass
class Student:
    roll_number: str
    name: str
    mailid: str
    hostel: str


@dataclass
class Bill:
    roll_number: str
    name: str
    month: str
    meals_consumed: int

    @property
    def variable_charge(self):
        return self.meals_consumed * PER_MEAL_RATE

    @property
    def total(self):
        return BASE_CHARGE + self.variable_charge

    def as_text(self):
        return (
            "\nSMART CAMPUS HOSTEL MESS - MONTHLY BILL\n"
            "----------------------------------------\n"
            f"Student Name   : {self.name}\n"
            f"Roll Number    : {self.roll_number}\n"
            f"Billing Month  : {self.month}\n"
            f"Meals Consumed : {self.meals_consumed}\n"
            f"Base Charge    : Rs. {BASE_CHARGE}\n"
            f"Meal Charge    : Rs. {self.variable_charge}\n"
            f"Total Payable  : Rs. {self.total}\n"
            "----------------------------------------\n"
        )



# SMTP FUNCTIONS


def configure_smtp():
    """Securely asks for SMTP details once at program startup."""
    print("\n" + "=" * 58)
    print("SMTP EMAIL CONFIGURATION")
    print("=" * 58)
    print("Use a Gmail App Password, not your normal Gmail password.")
    print("Press Enter twice to run the program without email.\n")

    try:
        email = input("Enter Gmail address: ").strip()
        password = getpass("Enter Gmail App Password: ").strip()

        if email and password:
            os.environ["SMTP_EMAIL"] = email
            os.environ["SMTP_APP_PASSWORD"] = password
            print("\nSMTP configured. Email notifications are enabled.")
        else:
            os.environ.pop("SMTP_EMAIL", None)
            os.environ.pop("SMTP_APP_PASSWORD", None)
            print("\nSMTP skipped. CSV functions will work normally.")

    except (EOFError, KeyboardInterrupt):
        os.environ.pop("SMTP_EMAIL", None)
        os.environ.pop("SMTP_APP_PASSWORD", None)
        print("\nSMTP skipped. Continuing without email.")


def send_email(to_address, subject, body):
    """Sends email safely. Failure does not stop CSV operations."""
    sender = os.getenv("SMTP_EMAIL", "").strip()
    password = os.getenv("SMTP_APP_PASSWORD", "").strip()

    if not sender or not password:
        print("Email warning: SMTP details are unavailable; email was not sent.")
        return False

    if not to_address:
        print("Email warning: Student email ID is missing.")
        return False

    try:
        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = to_address

        if USE_SSL:
            with smtplib.SMTP_SSL(
                SMTP_SERVER,
                SMTP_PORT,
                timeout=20
            ) as server:
                server.login(sender, password)
                server.sendmail(sender, [to_address], message.as_string())
        else:
            with smtplib.SMTP(
                SMTP_SERVER,
                SMTP_PORT,
                timeout=20
            ) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender, password)
                server.sendmail(sender, [to_address], message.as_string())

        print(f"Email sent successfully to {to_address}.")
        return True

    except (smtplib.SMTPException, OSError, ValueError) as error:
        print(f"Email warning: Could not send email: {error}")
        print("CSV data was saved successfully; only the email could not be sent.")
        return False



# CSV HELPER FUNCTIONS


def ensure_csv(file_path, fields):
    """Creates a CSV file with headers when it does not exist."""
    try:
        if not file_path.exists() or file_path.stat().st_size == 0:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                csv.DictWriter(file, fieldnames=fields).writeheader()
    except (OSError, csv.Error) as error:
        print(f"Warning: Could not create {file_path.name}: {error}")


def initialise_files():
    ensure_csv(STUDENTS_FILE, STUDENT_FIELDS)
    ensure_csv(ATTENDANCE_FILE, ATTENDANCE_FIELDS)
    ensure_csv(COMPLAINTS_FILE, COMPLAINT_FIELDS)


def read_csv(file_path, fields):
    """Reads CSV data safely and ignores malformed rows."""
    ensure_csv(file_path, fields)

    try:
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print(f"Warning: Header missing in {file_path.name}.")
                return []

            rows = []

            for row in reader:
                if row and all(field in row for field in fields):
                    rows.append(
                        {
                            field: (row.get(field) or "").strip()
                            for field in fields
                        }
                    )
                else:
                    print(f"Warning: Skipped malformed row in {file_path.name}.")

            return rows

    except (OSError, csv.Error, UnicodeDecodeError) as error:
        print(f"Warning: Could not read {file_path.name}: {error}")
        return []


def append_csv(file_path, fields, row):
    """Appends a row without removing existing data."""
    ensure_csv(file_path, fields)

    try:
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=fields).writerow(row)
        return True

    except (OSError, csv.Error, UnicodeEncodeError) as error:
        print(f"Warning: Could not update {file_path.name}: {error}")
        return False


def write_csv(file_path, fields, rows):
    """Safely rewrites a complete CSV file."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return True

    except (OSError, csv.Error, UnicodeEncodeError) as error:
        print(f"Warning: Could not save {file_path.name}: {error}")
        return False



# STUDENT FUNCTIONS


def get_students():
    students = []

    for row in read_csv(STUDENTS_FILE, STUDENT_FIELDS):
        try:
            students.append(Student(**row))
        except TypeError:
            print("Warning: Skipped invalid student record.")

    return students


def find_student(roll_number):
    roll_number = roll_number.strip().upper()

    for student in get_students():
        if student.roll_number.upper() == roll_number:
            return student

    return None


def add_student():
    """Adds a student after checking duplicate roll numbers."""
    try:
        roll = input("Roll Number: ").strip().upper()
        name = input("Student Name: ").strip()
        mailid = input("Email ID: ").strip()
        hostel = input("Hostel Name: ").strip()

        if not all([roll, name, mailid, hostel]):
            print("All student fields are required.")
            return

        if find_student(roll):
            print("Duplicate roll number found. Student was not added.")
            return

        saved = append_csv(
            STUDENTS_FILE,
            STUDENT_FIELDS,
            {
                "roll_number": roll,
                "name": name,
                "mailid": mailid,
                "hostel": hostel,
            },
        )

        if saved:
            print("Student added successfully.")

    except (EOFError, KeyboardInterrupt):
        print("\nStudent entry cancelled.")


def view_students():
    students = get_students()

    if not students:
        print("No student records found.")
        return

    print("\nSTUDENT RECORDS")
    print("-" * 90)
    print(f"{'ROLL NUMBER':<15}{'NAME':<25}{'EMAIL':<32}{'HOSTEL'}")
    print("-" * 90)

    for student in students:
        print(
            f"{student.roll_number:<15}"
            f"{student.name:<25}"
            f"{student.mailid:<32}"
            f"{student.hostel}"
        )



# WEEKLY MENU FUNCTIONS


def display_menu(day=None):
    """Displays the whole weekly menu or one selected day."""
    if day is None:
        print("\nWEEKLY MESS MENU")
        print("=" * 52)

        for menu_day, meals in WEEKLY_MENU.items():
            print(f"\n{menu_day}")

            for meal_type, item in meals.items():
                print(f"  {meal_type:<10}: {item}")

        return

    actual_day = next(
        (
            menu_day for menu_day in WEEKLY_MENU
            if menu_day.lower() == day.lower()
        ),
        None,
    )

    if actual_day is None:
        print("Invalid day. Use Monday to Sunday.")
        return

    print(f"\n{actual_day.upper()} MENU")
    print("-" * 45)

    for meal_type, item in WEEKLY_MENU[actual_day].items():
        print(f"{meal_type:<10}: {item}")


def update_menu(day, meal_type, new_item):
    """Updates an item in the nested weekly menu dictionary."""
    actual_day = next(
        (
            menu_day for menu_day in WEEKLY_MENU
            if menu_day.lower() == day.strip().lower()
        ),
        None,
    )

    if actual_day is None:
        print("Invalid day.")
        return False

    actual_meal = next(
        (
            meal for meal in WEEKLY_MENU[actual_day]
            if meal.lower() == meal_type.strip().lower()
        ),
        None,
    )

    if actual_meal is None or not new_item.strip():
        print("Invalid meal type or empty menu item.")
        return False

    WEEKLY_MENU[actual_day][actual_meal] = new_item.strip()
    print(f"{actual_day} {actual_meal} menu updated successfully.")
    return True



# ATTENDANCE FUNCTIONS


def attendance_exists(date, meal_type):
    return any(
        row["date"] == date
        and row["meal_type"].lower() == meal_type.lower()
        for row in read_csv(ATTENDANCE_FILE, ATTENDANCE_FIELDS)
    )


def remove_attendance_session(date, meal_type):
    """Removes one saved session after overwrite approval."""
    rows = read_csv(ATTENDANCE_FILE, ATTENDANCE_FIELDS)

    remaining = [
        row for row in rows
        if not (
            row["date"] == date
            and row["meal_type"].lower() == meal_type.lower()
        )
    ]

    return write_csv(ATTENDANCE_FILE, ATTENDANCE_FIELDS, remaining)


def mark_absentees(date, meal_type):
    """Marks all unrecorded students absent for the selected meal."""
    saved_rows = read_csv(ATTENDANCE_FILE, ATTENDANCE_FIELDS)

    recorded_rolls = {
        row["roll_number"].upper()
        for row in saved_rows
        if row["date"] == date
        and row["meal_type"].lower() == meal_type.lower()
    }

    absent_count = 0

    for student in get_students():
        if student.roll_number.upper() not in recorded_rolls:
            if append_csv(
                ATTENDANCE_FILE,
                ATTENDANCE_FIELDS,
                {
                    "roll_number": student.roll_number,
                    "date": date,
                    "meal_type": meal_type.title(),
                    "status": "absent",
                },
            ):
                absent_count += 1

    return absent_count


def record_attendance(date, meal_type, present_roll_numbers):
    """
    Saves present attendance and automatically marks absent students.
    Raises DuplicateAttendanceError if the session already exists.
    """
    date = date.strip()
    meal_type = meal_type.strip().title()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError(
            "Date must be written in YYYY-MM-DD format."
        ) from error

    if meal_type not in ["Breakfast", "Lunch", "Dinner"]:
        raise ValueError(
            "Meal type must be Breakfast, Lunch or Dinner."
        )

    if attendance_exists(date, meal_type):
        raise DuplicateAttendanceError(
            f"Attendance already exists for {date} - {meal_type}."
        )

    valid_rolls = {
        student.roll_number.upper()
        for student in get_students()
    }

    present_set = {
        roll.strip().upper()
        for roll in present_roll_numbers
        if roll.strip()
    }

    invalid_rolls = present_set - valid_rolls

    if invalid_rolls:
        raise ValueError(
            "Unknown roll number(s): "
            + ", ".join(sorted(invalid_rolls))
        )

    for roll in sorted(present_set):
        append_csv(
            ATTENDANCE_FILE,
            ATTENDANCE_FIELDS,
            {
                "roll_number": roll,
                "date": date,
                "meal_type": meal_type,
                "status": "present",
            },
        )

    absent_count = mark_absentees(date, meal_type)

    print(
        f"Attendance saved successfully: "
        f"{len(present_set)} present, {absent_count} absent."
    )


def take_attendance():
    """Interactive attendance entry with overwrite choice."""
    try:
        date = input("Date (YYYY-MM-DD): ").strip()
        meal_type = input(
            "Meal Type (Breakfast/Lunch/Dinner): "
        ).strip()

        print("Enter present roll numbers separated by commas.")
        present_rolls = input("Present Roll Numbers: ").split(",")

        try:
            record_attendance(date, meal_type, present_rolls)

        except DuplicateAttendanceError as error:
            print(error)

            choice = input(
                "Overwrite existing attendance? (yes/no): "
            ).strip().lower()

            if choice in ["yes", "y"]:
                if remove_attendance_session(date, meal_type):
                    record_attendance(date, meal_type, present_rolls)
            else:
                print("Existing attendance was kept.")

        except ValueError as error:
            print(f"Attendance not saved: {error}")

    except (EOFError, KeyboardInterrupt):
        print("\nAttendance entry cancelled.")



# COMPLAINT FUNCTIONS


def next_complaint_id():
    highest = 0

    for row in read_csv(COMPLAINTS_FILE, COMPLAINT_FIELDS):
        try:
            number = int(
                row["complaint_id"]
                .upper()
                .replace("CP-", "")
            )
            highest = max(highest, number)
        except ValueError:
            continue

    return f"CP-{highest + 1:04d}"


def log_complaint(roll_number, date, complaint_text):
    """Logs an open complaint and sends confirmation email."""
    student = find_student(roll_number)

    if student is None:
        print("Student roll number not found.")
        return

    if not complaint_text.strip():
        print("Complaint text cannot be empty.")
        return

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Date must be written in YYYY-MM-DD format.")
        return

    complaint_id = next_complaint_id()

    saved = append_csv(
        COMPLAINTS_FILE,
        COMPLAINT_FIELDS,
        {
            "complaint_id": complaint_id,
            "roll_number": student.roll_number,
            "date": date,
            "complaint_text": complaint_text.strip(),
            "status": "Open",
        },
    )

    if saved:
        print(f"Complaint {complaint_id} logged successfully.")

        send_email(
            student.mailid,
            "Mess Complaint Registered",
            (
                f"Hello {student.name},\n\n"
                f"Your complaint ID {complaint_id} was registered on {date}.\n"
                "The hostel mess team will review it shortly.\n\n"
                "Regards,\nHostel Mess Team"
            ),
        )


def resolve_complaint(complaint_id, resolution_message):
    """Changes a complaint status to Resolved and emails the student."""
    rows = read_csv(COMPLAINTS_FILE, COMPLAINT_FIELDS)
    selected = None

    for row in rows:
        if row["complaint_id"].upper() == complaint_id.strip().upper():
            row["status"] = "Resolved"
            selected = row
            break

    if selected is None:
        print("Complaint ID not found.")
        return

    if write_csv(COMPLAINTS_FILE, COMPLAINT_FIELDS, rows):
        print("Complaint marked as resolved.")

        student = find_student(selected["roll_number"])

        if student:
            send_email(
                student.mailid,
                "Mess Complaint Resolved",
                (
                    f"Hello {student.name},\n\n"
                    f"Your complaint {selected['complaint_id']} has been resolved.\n"
                    f"Resolution: {resolution_message.strip()}\n\n"
                    "Regards,\nHostel Mess Team"
                ),
            )


def show_open_complaints():
    """Displays all Open complaints sorted by date."""
    complaints = [
        row for row in read_csv(COMPLAINTS_FILE, COMPLAINT_FIELDS)
        if row["status"].lower() == "open"
    ]

    complaints.sort(key=lambda row: row["date"])

    if not complaints:
        print("No open complaints found.")
        return

    print("\nOPEN COMPLAINTS")
    print("=" * 70)

    for row in complaints:
        print(
            f"{row['complaint_id']} | {row['date']} | "
            f"{row['roll_number']}"
        )
        print(f"  {row['complaint_text']}")



# BILL FUNCTIONS


def generate_bill(roll_number, month):
    """
    Generates one student bill.
    Missing attendance safely creates a bill with zero variable charge.
    """
    student = find_student(roll_number)

    if student is None:
        print("Student roll number not found.")
        return None

    meals_consumed = 0

    try:
        attendance_rows = read_csv(
            ATTENDANCE_FILE,
            ATTENDANCE_FIELDS
        )

        present_rows = [
            row for row in attendance_rows
            if row["roll_number"].upper() == student.roll_number.upper()
            and row["date"].startswith(month)
            and row["status"].lower() == "present"
        ]

        if not present_rows:
            raise LookupError("No attendance data for selected month.")

        meals_consumed = len(present_rows)

    except LookupError:
        print(
            "No attendance found for this month. "
            "Generating bill with zero meal charges."
        )

    except (OSError, csv.Error, ValueError) as error:
        print(
            f"Attendance warning: {error}. "
            "Generating bill with zero meal charges."
        )

    # BUGFIX:
    # A student with no attendance rows previously could cause bill generation
    # to fail. The program now produces a valid base-charge bill safely.

    return Bill(
        student.roll_number,
        student.name,
        month.strip(),
        meals_consumed,
    )


def send_bill_email(roll_number, bill_text):
    student = find_student(roll_number)

    if student is None:
        print("Bill email not sent: Student roll number not found.")
        return False

    return send_email(
        student.mailid,
        "Hostel Mess Monthly Bill",
        bill_text,
    )


def safe_filename(text):
    return "".join(
        character if character.isalnum() or character in "-_"
        else "_"
        for character in text
    )


def generate_hostel_bills(hostel, month):
    """Creates bill output for every student in a given hostel."""
    selected_students = [
        student for student in get_students()
        if student.hostel.lower() == hostel.strip().lower()
    ]

    if not selected_students:
        print("No students found in this hostel.")
        return

    output_file = DATA_FOLDER / (
        f"hostel_bills_{safe_filename(month)}.csv"
    )

    bill_fields = [
        "roll_number",
        "name",
        "month",
        "meals_consumed",
        "base_charge",
        "variable_charge",
        "total",
    ]

    bill_rows = []

    for student in selected_students:
        bill = generate_bill(student.roll_number, month)

        if bill:
            bill_rows.append(
                {
                    "roll_number": bill.roll_number,
                    "name": bill.name,
                    "month": bill.month,
                    "meals_consumed": bill.meals_consumed,
                    "base_charge": BASE_CHARGE,
                    "variable_charge": bill.variable_charge,
                    "total": bill.total,
                }
            )

            send_bill_email(
                student.roll_number,
                bill.as_text(),
            )

    if write_csv(output_file, bill_fields, bill_rows):
        print(
            f"Hostel bill output generated successfully: "
            f"{output_file.name}"
        )



# MENU FUNCTIONS


def manage_students():
    while True:
        print("\nSTUDENT MANAGEMENT")
        print("1. Add Student")
        print("2. View Students")
        print("3. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            return
        else:
            print("Please enter a valid option.")


def manage_menu():
    while True:
        print("\nMENU MANAGEMENT")
        print("1. Display Weekly Menu")
        print("2. Display Menu for One Day")
        print("3. Update Menu")
        print("4. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            display_menu()

        elif choice == "2":
            display_menu(input("Enter day: ").strip())

        elif choice == "3":
            day = input("Enter day: ").strip()
            meal = input("Enter meal type: ").strip()
            item = input("Enter new menu item: ").strip()

            update_menu(day, meal, item)

        elif choice == "4":
            return

        else:
            print("Please enter a valid option.")


def manage_complaints():
    while True:
        print("\nCOMPLAINT MANAGEMENT")
        print("1. Log Complaint")
        print("2. Show Open Complaints")
        print("3. Resolve Complaint")
        print("4. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            log_complaint(
                input("Roll Number: ").strip(),
                input("Date (YYYY-MM-DD): ").strip(),
                input("Complaint: ").strip(),
            )

        elif choice == "2":
            show_open_complaints()

        elif choice == "3":
            resolve_complaint(
                input("Complaint ID: ").strip(),
                input("Resolution Message: ").strip(),
            )

        elif choice == "4":
            return

        else:
            print("Please enter a valid option.")


def manage_bills():
    while True:
        print("\nBILL MANAGEMENT")
        print("1. Generate Bill for One Student")
        print("2. Generate Bills for One Hostel")
        print("3. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            bill = generate_bill(
                input("Roll Number: ").strip(),
                input("Month (YYYY-MM): ").strip(),
            )

            if bill:
                print(bill.as_text())

                send_choice = input(
                    "Send bill email? (yes/no): "
                ).strip().lower()

                if send_choice in ["yes", "y"]:
                    send_bill_email(
                        bill.roll_number,
                        bill.as_text(),
                    )

        elif choice == "2":
            generate_hostel_bills(
                input("Hostel Name: ").strip(),
                input("Month (YYYY-MM): ").strip(),
            )

        elif choice == "3":
            return

        else:
            print("Please enter a valid option.")



# MAIN PROGRAM


def main():
    configure_smtp()
    initialise_files()

    print("\nSMART CAMPUS HOSTEL MESS MANAGEMENT SYSTEM")

    while True:
        print("\nMAIN MENU")
        print("1. Manage Students")
        print("2. Manage Menu")
        print("3. Record Attendance")
        print("4. Complaints")
        print("5. Generate Bills")
        print("6. Exit")

        try:
            choice = input("Enter choice: ").strip()

            if choice == "1":
                manage_students()
            elif choice == "2":
                manage_menu()
            elif choice == "3":
                take_attendance()
            elif choice == "4":
                manage_complaints()
            elif choice == "5":
                manage_bills()
            elif choice == "6":
                print("Thank you for using the system.")
                break
            else:
                print("Please enter a number from 1 to 6.")

        except (EOFError, KeyboardInterrupt):
            print("\nProgram closed safely.")
            break



# OPTIONAL SAMPLE DATA FOR TESTING
"""
initialise_files()

sample_students = [
    (
        "2401CS03",
        "Aditya Kumar",
        "aditya_2401cs03@iitp.ac.in",
        "Kalam",
    ),
    (
        "2401CS05",
        "Aman Sharma",
        "aman_2401cs05@iitp.ac.in",
        "Kalam",
    ),
    (
        "2401CS07",
        "Prashant Singh",
        "prashant_2401cs07@iitp.ac.in",
        "Kalam",
    ),
    (
        "2401CS08",
        "Ayush Raj",
        "ayush_2401cs08@iitp.ac.in",
        "Kalam",
    ),
    (
        "2401CS09",
        "Rahul Kumar Sahoo",
        "rahul_2401cs09@iitp.ac.in",
        "Kalam",
    ),
]

for roll, name, email, hostel in sample_students:
    if not find_student(roll):
        append_csv(
            STUDENTS_FILE,
            STUDENT_FIELDS,
            {
                "roll_number": roll,
                "name": name,
                "mailid": email,
                "hostel": hostel,
            },
        )

record_attendance(
    "2026-07-26",
    "Breakfast",
    ["2401CS03", "2401CS05", "2401CS07"],
)

record_attendance(
    "2026-07-27",
    "Lunch",
    ["2401CS03", "2401CS07", "2401CS08", "2401CS09"],
)

record_attendance(
    "2026-07-28",
    "Dinner",
    ["2401CS05", "2401CS07", "2401CS09"],
)
"""

if __name__ == "__main__":
    main()