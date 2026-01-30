# Timetable Engine

Automated Timetable Engine built using **Python** and **Streamlit**.  
This project generates **faculty-availability based, clash-free timetables** for college departments, including theory and lab sessions.

---

## 📝 Features

- Dynamic timetable generation based on **faculty availability**
- Supports **multiple sections** and **labs**
- Ensures **no time-slot clashes**
- Export timetable to **PDF / CSV**
- Web-based interface via **Streamlit**, mobile-friendly
- Fully **college-inspection ready** with sample data

---

## 💻 Technologies Used

| Technology        | Version / Notes                |
|------------------|-------------------------------|
| Python           | 3.10+                         |
| Streamlit        | 1.27+                         |
| Pandas           | 2.0+                          |
| ReportLab        | 3.6+ (for PDF export)         |
| VS Code          | IDE                            |
| Git / GitHub     | Version control & hosting      |

---

## 📂 Project Structure

timetable-engine/
│── app.py # Main Streamlit app
│── requirements.txt # Python dependencies
│── data/ # Sample data for timetable
│ ├── faculty.csv
│ ├── timetable.csv
│── README.md # Project documentation
│── .gitignore # Ignored files (venv, pycache)

## 🚀 How to Run Locally

1. **Clone the repository**
```bash
git clone https://github.com/<your-username>/timetable-engine.git
cd timetable-engine

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py