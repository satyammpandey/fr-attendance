
# 🎯 AI Face Recognition Attendance System

An intelligent attendance management system using Face Recognition, Python, OpenCV, Tkinter, and SQLite.  
Automatically marks attendance when a registered face is detected.

---

## 📌 Features

- ✅ Real-time face detection & recognition  
- ✅ Automatic attendance marking  
- ✅ Secure SQLite database storage  
- ✅ Interactive Tkinter GUI  
- ✅ Student registration & management  
- ✅ Analytics dashboard  
- ✅ Report generation  
- ✅ Export to CSV / Excel / JSON  
- ✅ Camera auto-reconnect system  
- ✅ Activity logging  

---

## 🛠️ Tech Stack

- Python 3.10+
- OpenCV
- face_recognition (dlib)
- Tkinter
- SQLite
- Pandas
- Pillow
- Matplotlib

---

## 📂 Project Structure

FaceAttendance/
│
├── gui.py # Main GUI application
├── recognize.py # Face recognition engine
├── train_model.py # Model training script
├── model.pkl # Trained face model
├── attendance_system.db # SQLite database
├── config.json # App configuration
├── logs/ # Log files
├── backups/ # Backup files
├── exports/ # Exported reports
└── README.md # Documentation


---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/satyammpandey/fr-attendance.git
cd fr-attendance
2️⃣ Install Dependencies
pip install opencv-python face-recognition pandas pillow matplotlib
If dlib fails:

Install CMake

Install Visual Studio Build Tools

Re-run the command

🚀 Usage
Step 1: Train the Model (First Time Only)
python train_model.py
Step 2: Launch Application
python gui.py
Step 3: Start Attendance
Click ▶ START

Camera opens

Face is detected

Attendance saved automatically

Press Q to stop recognition.

💾 Database System
All records are stored in:

attendance_system.db
Main Tables
students

attendance

sessions

activity_logs

🗑️ Clear Attendance Records
To remove old records:

DELETE FROM attendance;
(Use DB Browser for SQLite)

🧠 System Workflow
Capture face using camera

Generate face encoding

Compare with trained data

Identify person

Store attendance

Update GUI dashboard

❗ Troubleshooting
Camera Not Working
Close other apps using camera

Restart system

Check camera index

Face Not Recognized
Re-train model

Improve lighting

Add more images

Attendance Not Showing
Check database file

Verify recognize.py output

Check table structure

📈 Future Enhancements
Cloud backup system

Mobile application

Face mask detection

Multi-camera support

Role-based login system

Cloud dashboard

👨‍💻 Author
Satyam Pandey
BCA (AI/ML) Student

GitHub: https://github.com/satyammpandey

⭐ Support
If you found this project useful, give it a ⭐ on GitHub.
