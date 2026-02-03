import streamlit as st
import os
import pandas as pd
import sys


st.set_page_config(page_title="Face Attendance System")

st.title("AI-Based Face Recognition Attendance System")
st.write("Developed by: Satyam (BCA AI/ML)")

st.divider()

file_path = "attendance/attendance.csv"


# Start Button
if st.button("Start Attendance System"):

    python_path = sys.executable
    os.system(f'"{python_path}" recognize.py')


st.divider()

st.subheader("Attendance Records")


if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.dataframe(df)
else:
    st.warning("No attendance recorded yet.")
