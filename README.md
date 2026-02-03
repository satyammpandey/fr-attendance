# 🎯 AI-Based Face Recognition Attendance System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![AI](https://img.shields.io/badge/AI-Deep%20Learning-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Status](https://img.shields.io/badge/Status-Completed-success)

> An AI-powered real-time attendance management system using facial
> recognition and deep learning.

------------------------------------------------------------------------

## 📌 Overview

This project implements an automated attendance system using Artificial
Intelligence and Computer Vision. It identifies individuals using facial
features and records attendance automatically in real time.

------------------------------------------------------------------------

## 🚀 Features

-   Real-time face detection and recognition\
-   Automatic attendance marking\
-   Duplicate entry prevention\
-   CSV-based storage system\
-   Web dashboard (Streamlit)\
-   Offline functionality

------------------------------------------------------------------------

## 🛠️ Tech Stack

  Category      Technology
  ------------- ------------------------
  Language      Python 3.10
  Vision        OpenCV
  AI            face_recognition, dlib
  Data          Pandas, NumPy
  UI            Streamlit
  Environment   Anaconda

------------------------------------------------------------------------

## 📂 Project Structure

FaceAttendance/ ├── dataset/ ├── attendance/ │ └── attendance.csv ├──
test_camera.py ├── train_model.py ├── recognize.py ├── app.py ├──
model.pkl ├── .gitignore └── README.md

------------------------------------------------------------------------

## ⚙️ Installation & Setup

### Install Anaconda

Download from https://www.anaconda.com

### Create Environment

conda create -n faceai python=3.10\
conda activate faceai

### Install Dependencies

conda install -c conda-forge dlib\
pip install face-recognition opencv-python numpy pandas streamlit

------------------------------------------------------------------------

## ▶️ How to Run

conda activate faceai\
cd FaceAttendance\
streamlit run app.py

------------------------------------------------------------------------

## 📊 Output

-   Live camera feed\
-   Face recognized with name\
-   Attendance recorded in CSV\
-   Records displayed in dashboard

------------------------------------------------------------------------

## ⚠️ Limitations

-   Sensitive to lighting\
-   Similar faces may confuse system\
-   Single camera support

------------------------------------------------------------------------

## 🔮 Future Enhancements

-   Mobile app\
-   Cloud database\
-   Multi-camera support\
-   Admin login

------------------------------------------------------------------------

## 👨‍💻 Developer

Satyam Pandey\
BCA (AI/ML Specialization)

------------------------------------------------------------------------

## 📜 License

For academic and learning purposes.

⭐ If you find this project useful, give it a star!
