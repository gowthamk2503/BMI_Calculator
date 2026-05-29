# 💙 Premium BMI Analyzer

<div align="center">

<img src="./assets/banner.png" alt="Premium BMI Analyzer Banner"/>

# 🏥 Premium BMI Analyzer

### Modern Health Analytics & BMI Tracking Desktop Application

A professional desktop application built with **Python, CustomTkinter, MongoDB Atlas, and Matplotlib** to help users calculate, monitor, and analyze their Body Mass Index (BMI) through interactive dashboards, personalized health insights, and cloud-based data storage.

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-Modern_UI-blue?style=for-the-badge)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge\&logo=mongodb\&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Analytics-orange?style=for-the-badge)
![Desktop App](https://img.shields.io/badge/Desktop-Python_GUI-success?style=for-the-badge)

### 📊 Track • Analyze • Improve Your Health

</div>

---

# 📖 Overview

Premium BMI Analyzer is a feature-rich health monitoring application designed to provide users with an intuitive way to calculate and track BMI while gaining valuable health insights through visual analytics.

The application offers:

* BMI calculation using Metric and Imperial units
* Historical BMI tracking
* Personalized health recommendations
* Interactive analytics dashboard
* Cloud data storage using MongoDB Atlas
* Data export and import functionality
* Modern light and dark themes

---

# 📸 Application Screenshots

## 🏠 Dashboard

<img width="1146" height="853" alt="image" src="https://github.com/user-attachments/assets/92250496-5086-4ecd-9165-22377b87d62f" />


The dashboard provides:

* Personalized user greeting
* Health summary cards
* Latest BMI insights
* WHO BMI classification guide
* Daily health recommendations

---

## 🧮 BMI Calculator

<img width="1139" height="851" alt="image" src="https://github.com/user-attachments/assets/03a204b1-fd2b-4a9e-aa7b-65ce86520261" />


Features:

* Metric (kg/cm)
* Imperial (lb/in)
* Instant BMI calculation
* Health classification
* Personalized diet suggestions
* Exercise recommendations

---


## 📈 Analytics Dashboard

<img width="1145" height="852" alt="image" src="https://github.com/user-attachments/assets/8e669568-3ff4-49ca-b75b-735b4204d489" />


Analytics includes:

* BMI trend charts
* Average BMI analysis
* Highest BMI tracking
* Lowest BMI tracking
* Progress reports

---

## 👤 User Profile



Manage:

* Full Name
* Age
* Gender
* Personal health profile

---

## 🌙 Dark Mode



Supports:

* Light Theme
* Dark Theme
* Theme switching

---

# ✨ Features

## 🏠 Smart Dashboard

The dashboard provides a complete overview of health statistics including:

* Personalized greeting
* Total BMI records
* Average BMI calculation
* Highest BMI recorded
* Latest BMI entry
* WHO BMI standards guide
* Health recommendations

---

## 🧮 BMI Calculator

Supports:

### Metric System

* Weight (kg)
* Height (cm)

### Imperial System

* Weight (lb)
* Height (in)

Automatically provides:

* BMI Value
* BMI Category
* Diet Recommendation
* Exercise Recommendation

---

## 📋 BMI History Management

Track every BMI calculation with:

* Date & Time
* Weight
* Height
* Unit System
* BMI Score
* Classification

---

## 📈 Health Analytics

Advanced visual analytics include:

* BMI Progress Charts
* Average BMI Monitoring
* Historical Trend Analysis
* Highest BMI Tracking
* Lowest BMI Tracking

Powered by Matplotlib.

---

## 👤 User Profile Management

Store and manage:

* Name
* Age
* Gender

Integrated across all modules.

---

## 💾 Data Management

### Export Data

Export all records into JSON format.

### Import Data

Restore records instantly from backup.

### Cloud Storage

Store data securely using MongoDB Atlas.

### Offline Support

Automatically switches to local memory storage when MongoDB is unavailable.

---

# 🛠 Technology Stack

| Category             | Technology             |
| -------------------- | ---------------------- |
| Programming Language | Python                 |
| GUI Framework        | CustomTkinter          |
| Database             | MongoDB Atlas          |
| Visualization        | Matplotlib             |
| Data Format          | JSON                   |
| Storage              | MongoDB + Local Backup |
| Architecture         | Desktop Application    |

---

# 🏗 System Architecture

```text
User
 │
 ▼
Premium BMI Analyzer
 │
 ├── Dashboard
 ├── BMI Calculator
 ├── BMI History
 ├── Analytics
 ├── User Profile
 │
 ▼
MongoDB Atlas
 │
 ▼
Health Data Storage
 │
 ▼
Charts & Analytics
```

---

# 📊 BMI Classification Guide

| BMI Range   | Classification  |
| ----------- | --------------- |
| Below 18.5  | Underweight     |
| 18.5 – 24.9 | Normal Weight   |
| 25 – 29.9   | Overweight      |
| 30 – 34.9   | Obese           |
| Above 35    | Extreme Obesity |

---

# 📂 Project Structure

```bash
Premium-BMI-Analyzer/
│
├── assets/
│   └── banner.png
│
├── screenshots/
│   ├── dashboard.png
│   ├── calculator.png
│   ├── history.png
│   ├── analytics.png
│   ├── profile.png
│   └── dark-mode.png
│
├── app.py
├── model.py
├── preprocess.py
├── requirements.txt
│
├── data/
│
├── __pycache__/
│
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/gowthamk2503/Premium-BMI-Analyzer.git
```

## Navigate to Project

```bash
cd Premium-BMI-Analyzer
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
python app.py
```

---

# ☁️ MongoDB Configuration

Configure MongoDB Atlas credentials:

```python
username = "your_username"
password = "your_password"
cluster_host = "cluster0.mongodb.net"
db_name = "bmi_app"
```

The application will automatically connect and store BMI records in MongoDB Atlas.

---

# 🔒 Key Highlights

✅ Premium Modern UI

✅ Dashboard Analytics

✅ BMI Classification

✅ Diet Recommendations

✅ Exercise Recommendations

✅ MongoDB Atlas Integration

✅ JSON Export / Import

✅ Light & Dark Theme

✅ Historical Tracking

✅ Offline Support

---

# 📈 Future Enhancements

Planned improvements:

* AI Health Assistant
* Calorie Tracking
* Fitness Goal Monitoring
* PDF Report Generation
* Doctor Consultation Module
* Cloud Synchronization
* Mobile Application
* Smart Notifications
* Health Risk Prediction

---

# 🎓 Learning Outcomes

This project demonstrates:

* Python Desktop Development
* CustomTkinter UI Design
* MongoDB Atlas Integration
* Data Visualization
* Health Analytics
* JSON Data Management
* Dashboard Development
* Modern GUI Architecture

---

# 👨‍💻 Author

## Gowtham K

🎓 B.Tech Information Technology
🏫 Sri Eshwar College of Engineering

📧 [gowtham.k2023it@sece.ac.in](mailto:gowtham.k2023it@sece.ac.in)

### 🌐 Connect With Me

* GitHub
* LinkedIn
* Portfolio

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you found this project useful:

🌟 Star the repository

🍴 Fork the repository

📢 Share with others

---

<div align="center">

## 💙 Healthy Life Begins with Healthy Tracking 💙

### Built with Python, CustomTkinter & MongoDB

</div>
