## 📊 College Attendance Optimization System

### Description

A data-driven simulation and analysis system built using **Python & Pandas** to study student attendance behavior across subjects, time, and behavioral profiles.
The project generates synthetic attendance data, identifies risk patterns, and produces actionable insights for academic optimization.

### Features

* Realistic attendance data simulation (weekday-based academic calendar)
* Student behavior modeling (disciplined, borderline, chronic)
* Subject-wise & month-wise attendance analysis
* Identification of low-attendance students and weak subjects
* Automated CSV report generation
* Single consolidated **PDF report** containing all visualizations

### Tech Stack

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn

### Reports Generated

**CSV Files**

* `attendance.csv`
* `low_attendance_students.csv`
* `subject_attendance_summary.csv`
* `overall_monthly_trends.csv`
* `subject_wise_monthly_trends.csv`
* `perfect_attendance_students.csv`
* `chronic_absentee_students.csv`
* `attendance_summary_dashboard.csv`

**Visualization**

* `attendance_report.pdf` (all plots combined)

### How to Run

```bash
python data_generation.py
```

### Project Structure

```
College Attendance Optimization System/
│
├── data_generation.py
├── attendance.csv
├── attendance_report.pdf
├── *.csv
└── README.md
```

### AI Assistance Disclosure

AI assistance was **used only for plotting logic and PDF visualization consolidation**.
All data modeling, simulation logic, analysis, and reporting design were implemented manually.

### Author

Dhwanit

### Future Scope

* Predictive attendance risk scoring
* Early-warning alerts for chronic absenteeism
* Instructor & timetable optimization insights
* Dashboard integration (Streamlit / Power BI)

---
