# 🎯 AI Face Recognition Attendance System

An AI-powered desktop application for automatic attendance management using real-time face recognition and a modern GUI interface.

---

## 🌟 Features

### 🎯 Core Functionality
- **Real-time Face Recognition** using webcam
- **Automatic Attendance Marking**
- **High Accuracy Matching** with trained face encodings
- **Live Camera Preview**
- **Unknown Face Detection**
- **Session-based Attendance Tracking**

### 👥 Student Management
- **Student Registration System**
- **Store Student Information** (ID, Name, Department, Batch)
- **Face Capture Support**
- **SQLite Database Integration**
- **Student Search & Filter**
- **Edit / Delete Students**

### 🖥️ User Interface
- **Modern Tkinter GUI**
- **Dark-Themed Professional Design**
- **Dashboard Overview**
- **Live Status Indicator**
- **Activity Logs**
- **Quick Navigation Panel**

### 📊 Analytics & Reports
- **Daily / Weekly / Monthly Attendance Stats**
- **Graph Visualization**
- **CSV / Excel / JSON Export**
- **Attendance Reports Panel**
- **Session History Tracking**

---

## 🛠️ Tech Stack

- **Python 3.10+** - Core language
- **OpenCV (cv2)** - Camera & vision processing
- **face_recognition (dlib)** - Face matching
- **Tkinter** - GUI framework
- **SQLite3** - Database
- **Pandas** - Data processing
- **Matplotlib** - Analytics charts
- **Git & GitHub** - Version control

---

## 📋 Prerequisites

- Python 3.10 or higher
- Webcam / Camera device
- Windows OS (Recommended)
- CMake (for dlib installation)

---

## 🚀 Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/satyammpandey/fr-attendance.git
cd fr-attendance
```

### 2️⃣ Create Virtual Environment (Optional)

```bash
python -m venv faceai
faceai\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🎮 Usage

### 1️⃣ Start GUI Application

```bash
python gui.py
```

### 2️⃣ Register Students
- Open **Students Tab**
- Add student details
- Capture face images
- Save student record

### 3️⃣ Train Model

```bash
python train_model.py
```

### 4️⃣ Start Attendance
- Click **START** button
- Camera opens
- Face is detected
- Attendance marked automatically

### 5️⃣ View Records
- Open **Attendance Tab**
- Filter by date
- Export reports

---

## 📁 Project Structure

```
FaceAttendance/
│
├── gui.py                 # Main GUI application
├── recognize.py           # Face recognition engine
├── train_model.py         # Model training script
├── model.pkl              # Trained face model
├── attendance_system.db   # SQLite database
├── requirements.txt       # Dependencies
├── logs/                  # Log files
├── backups/               # Auto backups
├── exports/               # Exported reports
└── README.md
```

---

## ⚙️ Configuration

Settings are stored in:

```
config.json
```

You can configure:

- Camera index
- Recognition threshold
- Working hours
- Backup interval
- Export format
- Notifications

Through the **Settings Panel** in GUI.

---

## 🗄️ Database

Database file:

```
attendance_system.db
```

### Tables:

- students
- attendance
- sessions
- activity_logs
- settings

---

## 🔑 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Attendance | F5 |
| Stop Attendance | ESC |
| Exit App | Ctrl + Q |
| Save Settings | Ctrl + S |

---

## 🧹 Clear Attendance Data

### Delete All Records

```sql
DELETE FROM attendance;
```

### Reset Database (Optional)

Delete file:

```
attendance_system.db
```

And restart application.

---

## 🧠 How Recognition Works

1. Face images collected
2. Encodings generated
3. Saved in model.pkl
4. Live camera compares faces
5. Best match selected
6. Attendance recorded in DB

---

## 🤝 Contributing

Contributions are welcome!

You may:
- Improve UI
- Add features
- Fix bugs
- Optimize performance

Fork → Modify → Pull Request

---

## 👨‍💻 Author

**Satyam Pandey**  


GitHub: https://github.com/satyammpandey

---

## 📜 License

This project is developed for educational and academic use.

Free to modify and extend.

---

## 🔮 Future Enhancements

- [ ] Mobile App Integration
- [ ] Cloud Backup
- [ ] Face Mask Detection
- [ ] Multi-Camera Support
- [ ] Voice Notifications
- [ ] Web Dashboard
- [ ] Online Database Sync

---

⭐ If you like this project, give it a star on GitHub!

