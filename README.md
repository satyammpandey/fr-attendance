# 🎯 AI Face Recognition Attendance System

An AI-based desktop application for automatic attendance using face recognition.

---

## 🚀 Features

- Real-time face detection
- Automatic attendance marking
- Tkinter GUI
- Student registration
- SQLite database
- Attendance reports
- Analytics dashboard
- Export to CSV / Excel / JSON
- Activity logs

---

## 🖥️ Tech Stack

- Python 3.10+
- OpenCV
- face_recognition
- Tkinter
- SQLite
- Pandas
- Matplotlib
- Git

---

## 📂 Project Structure

```
FaceAttendance/
│
├── gui.py
├── recognize.py
├── train_model.py
├── model.pkl
├── attendance_system.db
├── requirements.txt
├── logs/
├── backups/
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/satyammpandey/fr-attendance.git
cd fr-attendance
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

```bash
python gui.py
```

---

## 📸 How It Works

1. Register students
2. Train face model
3. Click START
4. Camera opens
5. Face detected
6. Attendance saved
7. Data appears in GUI

---

## 🗄️ Database

File used:

```
attendance_system.db
```

---

## 📊 Analytics

- Daily attendance
- Weekly reports
- Monthly analysis
- Graph visualization

---

## ⌨️ Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Start  | F5  |
| Stop   | ESC |
| Exit   | Ctrl + Q |

---

## 🧹 Clear Attendance Data

```sql
DELETE FROM attendance;
```

---

## 👨‍💻 Author

**Satyam Pandey**  
BCA (AI & ML)

GitHub: https://github.com/satyammpandey

---

## 📜 License

Educational Use Only

Free to modify
